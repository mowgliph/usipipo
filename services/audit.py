# services/audit.py

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database import models
from database.db import AsyncSessionLocal as get_session
from database.crud import logs as crud_logs
import logging
import traceback

logger = logging.getLogger("usipipo.services.audit")


async def create_audit_log(
    session: AsyncSession,
    user_id: Optional[str],
    action: str,
    payload: Optional[Dict[str, Any]] = None,
    commit: bool = True,
) -> models.AuditLog:
    """Crea un AuditLog usando el CRUD y maneja commit/rollback.

    - session: AsyncSession (requerido)
    - user_id: id del usuario (o None -> SYSTEM)
    - action: identificador de acción
    - details: texto descriptivo
    - payload: objeto serializable adicional
    - commit: si True hace commit al final
    """
    try:
        log = await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action=action,
            payload=payload,
            commit=False,
        )

        if commit:
            try:
                await session.commit()
                await session.refresh(log)
            except Exception:
                await session.rollback()
                logger.exception("DB error creando audit log", extra={"user_id": user_id})
                raise

        logger.info("Audit log creado", extra={"user_id": user_id, "action": action})
        return log
    except Exception:
        logger.exception("Error en create_audit_log", extra={"user_id": user_id})
        raise


async def get_audit_logs(
    session: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
) -> List[models.AuditLog]:
    try:
        logs = await crud_logs.get_audit_logs(
            session=session,
            user_id=user_id,
            action=action,
            limit=limit,
            offset=offset,
        )
        return logs
    except Exception:
        logger.exception("Error en get_audit_logs", extra={"user_id": user_id})
        raise


async def count_audit_logs(
    session: AsyncSession,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
) -> int:
    try:
        total = await crud_logs.count_audit_logs(session=session, user_id=user_id, action=action)
        return total
    except Exception:
        logger.exception("Error en count_audit_logs", extra={"user_id": user_id})
        raise


async def delete_old_logs(
    session: AsyncSession,
    cutoff: datetime,
    user_id: Optional[str] = None,
    commit: bool = True,
) -> int:
    """Elimina logs anteriores a `cutoff`. Devuelve la cantidad eliminada."""
    try:
        deleted_count = await crud_logs.delete_old_logs(session=session, cutoff=cutoff, user_id=user_id)
        if commit:
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("DB error en delete_old_logs", extra={"user_id": user_id})
                raise
        logger.info("Old logs deleted", extra={"user_id": user_id, "deleted": deleted_count})
        return deleted_count
    except Exception:
        logger.exception("Error en delete_old_logs", extra={"user_id": user_id})
        raise


async def delete_logs_older_than(
    session: AsyncSession,
    days_old: int = 30,
    user_id: Optional[str] = None,
    commit: bool = True,
) -> int:
    from datetime import timezone
    cutoff_date = datetime.now(tz=timezone.utc) - timedelta(days=days_old)
    return await delete_old_logs(session=session, cutoff=cutoff_date, user_id=user_id, commit=commit)


def format_logs(logs_list: List[models.AuditLog]) -> str:
    """Formatea una lista de AuditLog para presentación en mensajes.

    - Devuelve texto con fecha, usuario (o SYSTEM), acción y detalles.
    """
    if not logs_list:
        return "📭 No hay registros disponibles."

    lines: List[str] = []
    for log in logs_list:
        username = (
            f"@{log.user.username}"
            if hasattr(log, 'user') and log.user and hasattr(log.user, 'username') and log.user.username
            else (f"ID:{log.user_id}" if log.user_id else "SYSTEM")
        )
        created_at = log.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(log, 'created_at') else 'N/A'
        action = getattr(log, 'action', 'N/A')
        details = getattr(log, 'details', '') or ''

        lines.append(f"🕒 {created_at} | {username} | {action} | {details}")

    return "\n".join(lines)


# Convenience: if a caller wants a session managed internally
async def log_action_auto_session(
    user_id: Optional[str],
    action: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    async with get_session() as session:
        try:
            log = await create_audit_log(session=session, user_id=user_id, action=action, payload=payload, commit=True)
            return {"ok": True, "data": log}
        except Exception:
            logger.exception("Error en log_action_auto_session", extra={"user_id": user_id})
            await session.rollback()
            return {"ok": False, "data": None}


# Exported instance-style object for compatibility with previous code that used `audit_service`.
class _AuditServiceCompat:
    async def log_action(self, user_id: Optional[str], action: str, payload: Optional[Dict[str, Any]] = None):
        return await log_action_auto_session(user_id=user_id, action=action, payload=payload)

    async def get_logs(self, limit: int = 20, offset: int = 0, user_id: Optional[str] = None, action: Optional[str] = None):
        async with get_session() as session:
            try:
                items = await get_audit_logs(session=session, limit=limit, offset=offset, user_id=user_id, action=action)
                total = await count_audit_logs(session=session, user_id=user_id, action=action)
                return {"ok": True, "data": {"items": items, "total": total, "limit": limit, "offset": offset}}
            except Exception:
                logger.exception("Error en compat.get_logs", extra={"user_id": user_id})
                return {"ok": False, "data": None}


audit_service = _AuditServiceCompat()
