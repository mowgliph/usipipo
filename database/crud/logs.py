# database/crud/logs.py
from __future__ import annotations
from typing import Optional, List, Any, Dict

from datetime import datetime, timezone
import logging

from sqlalchemy import select, delete, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import models

logger = logging.getLogger("usipipo.crud.logs")


async def create_audit_log(
    session: AsyncSession,
    user_id: Optional[str],
    action: str,
    details: Optional[str] = None,
    *,
    payload: Optional[Dict[str, Any]] = None,
    commit: bool = False,
) -> models.AuditLog:
    """
    Crea un nuevo registro de auditoría y lo añade a la sesión.
    No hace commit por defecto; el caller (service) debe controlar la transacción.
    - user_id: UUID string o None para SYSTEM
    - payload: datos estructurados que se almacenan en la columna JSON `payload`
    - commit: si True hace commit() y refresh() antes de devolver el objeto
    """
    try:
        now = datetime.now(timezone.utc)
        log = models.AuditLog(
            user_id=user_id,
            action=action,
            payload=payload,
            created_at=now,
        )
        # details históricamente usado; si el modelo tiene 'details' se puede mapear en payload
        if details:
            if log.payload:
                log.payload = dict(log.payload)
                log.payload.setdefault("details", details)
            else:
                log.payload = {"details": details}

        session.add(log)

        if commit:
            try:
                await session.commit()
                await session.refresh(log)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al commitear create_audit_log", extra={"user_id": user_id})
                raise

        logger.info("AuditLog creado", extra={"user_id": user_id, "action": action})
        return log
    except SQLAlchemyError:
        logger.exception("Error creando AuditLog", extra={"user_id": user_id})
        raise


async def get_audit_logs(
    session: AsyncSession,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[models.AuditLog]:
    """
    Obtiene registros de auditoría con opciones de filtrado y paginación.
    Devuelve instancias ya cargadas con relación a User via selectinload.
    """
    try:
        stmt = select(models.AuditLog).options(selectinload(models.AuditLog.user)).order_by(models.AuditLog.created_at.desc())

        if user_id is not None:
            stmt = stmt.filter(models.AuditLog.user_id == user_id)
        if action:
            stmt = stmt.filter(models.AuditLog.action == action)

        result = await session.execute(stmt.offset(offset).limit(limit))
        logs = result.scalars().all()
        logger.debug("Fetched audit logs", extra={"user_id": user_id})
        return logs
    except SQLAlchemyError:
        logger.exception("Error obteniendo AuditLogs", extra={"user_id": user_id})
        raise


async def count_audit_logs(
    session: AsyncSession,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
) -> int:
    """
    Cuenta registros de auditoría que coincidan con filtros.
    """
    try:
        stmt = select(func.count(models.AuditLog.id))

        if user_id is not None:
            stmt = stmt.filter(models.AuditLog.user_id == user_id)
        if action:
            stmt = stmt.filter(models.AuditLog.action == action)

        result = await session.execute(stmt)
        count = result.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando AuditLogs", extra={"user_id": user_id})
        raise


async def delete_old_logs(
    session: AsyncSession,
    cutoff: datetime,
    user_id: Optional[str] = None,
    *,
    commit: bool = False,
) -> int:
    """
    Elimina registros de auditoría anteriores a `cutoff`.
    - user_id: si se especifica, solo elimina logs de ese usuario.
    - commit: si True hace commit() al finalizar la operación.
    Devuelve el número de filas afectadas (int).
    """
    try:
        stmt = delete(models.AuditLog).where(models.AuditLog.created_at < cutoff)
        if user_id is not None:
            stmt = stmt.where(models.AuditLog.user_id == user_id)

        result = await session.execute(stmt)
        rowcount = int(result.rowcount or 0)

        if commit:
            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al commitear delete_old_logs", extra={"user_id": user_id})
                raise

        logger.info("Deleted old audit logs", extra={"user_id": user_id, "rows": rowcount})
        return rowcount
    except SQLAlchemyError:
        logger.exception("Error eliminando AuditLogs antiguos", extra={"user_id": user_id})
        raise