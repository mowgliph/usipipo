# database/crud/ip_manager.py

from __future__ import annotations
from typing import Optional, List, Dict, Any

from datetime import datetime, timezone
import logging

from sqlalchemy import select, update, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database import models

logger = logging.getLogger("usipipo.crud.ips")


async def get_available_ips_for_type(session: AsyncSession, ip_type: str) -> List[models.IPManager]:
    """Obtiene IPs disponibles de un tipo específico (no revocadas y no asignadas)."""
    try:
        stmt = select(models.IPManager).where(
            models.IPManager.ip_type == ip_type,
            models.IPManager.is_available.is_(True),
            models.IPManager.is_revoked.is_(False)
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo IPs disponibles", extra={"user_id": None})
        raise


async def assign_ip_to_user(
    session: AsyncSession,
    ip_type: str,
    user_id: str,
    commit: bool = False
) -> Optional[models.IPManager]:
    """
    Asigna una IP disponible del tipo especificado al usuario.
    Devuelve la IP asignada o None si no hay disponibles.
    """
    try:
        # Buscar IP disponible del tipo correcto
        # Usamos with_for_update() para evitar condiciones de carrera
        stmt = select(models.IPManager).where(
            models.IPManager.ip_type == ip_type,
            models.IPManager.is_available.is_(True),
            models.IPManager.is_revoked.is_(False)
        ).with_for_update().limit(1)
        result = await session.execute(stmt)
        ip = result.scalars().one_or_none()
        
        if not ip:
            logger.info("No hay IPs disponibles para asignar", extra={"user_id": user_id, "ip_type": ip_type})
            return None
            
        # Asignar IP
        ip.is_available = False
        ip.assigned_to_user_id = user_id
        ip.assigned_at = datetime.now(timezone.utc)
        
        if commit:
            try:
                await session.commit()
                await session.refresh(ip)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error asignando IP", extra={"user_id": user_id})
                raise
                
        logger.info("IP asignada exitosamente", extra={"user_id": user_id, "ip_id": ip.id, "ip_address": ip.ip_address})
        return ip
    except SQLAlchemyError:
        logger.exception("Error en assign_ip_to_user", extra={"user_id": user_id})
        raise


async def revoke_ip(
    session: AsyncSession,
    ip_id: str,
    reason: str = "manual_revocation",
    commit: bool = False
) -> bool:
    """
    Revoca una IP, marcándola como no disponible y registrando el motivo.
    No la libera para reutilización inmediata, eso se hace en cleanup.
    """
    try:
        ip = await session.get(models.IPManager, ip_id)
        if not ip:
            return False
            
        ip.is_revoked = True
        ip.is_available = False
        ip.revoked_at = datetime.now(timezone.utc)
        
        extra = dict(ip.extra_data or {})
        extra["revoked_reason"] = reason
        extra["revoked_by_process"] = "manual" # Puede ser 'manual', 'trial_expired', 'payment_expired'
        ip.extra_data = extra
        
        if commit:
            try:
                await session.commit()
                await session.refresh(ip)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error revocando IP", extra={"user_id": ip.assigned_to_user_id, "ip_id": ip_id})
                raise
                
        logger.info("IP revocada", extra={"user_id": ip.assigned_to_user_id, "ip_id": ip_id, "reason": reason})
        return True
    except SQLAlchemyError:
        logger.exception("Error en revoke_ip", extra={"user_id": None})
        raise


async def release_ip(
    session: AsyncSession,
    ip_id: str,
    commit: bool = False
) -> bool:
    """
    Libera una IP, marcándola como disponible nuevamente.
    Usar esta función solo cuando se *quiere* liberar una IP revocada para su reutilización.
    """
    try:
        ip = await session.get(models.IPManager, ip_id)
        if not ip:
            return False
            
        # Permitir liberar IPs revocadas o no asignadas
        if not ip.is_revoked and ip.assigned_to_user_id is not None:
            logger.warning("Intento de liberar IP no revocada que tiene usuario asignado", extra={"user_id": ip.assigned_to_user_id, "ip_id": ip_id})
            return False # O manejar según lógica de negocio

        ip.is_available = True
        ip.assigned_to_user_id = None
        ip.assigned_at = None
        # No se toca is_revoked, ya que liberar no significa que no haya sido revocada antes
        
        if commit:
            try:
                await session.commit()
                await session.refresh(ip)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error liberando IP", extra={"user_id": ip.assigned_to_user_id, "ip_id": ip_id})
                raise
                
        logger.info("IP liberada para reutilización", extra={"user_id": ip.assigned_to_user_id, "ip_id": ip_id})
        return True
    except SQLAlchemyError:
        logger.exception("Error en release_ip", extra={"user_id": None})
        raise


async def get_assigned_ips_for_user(session: AsyncSession, user_id: str) -> List[models.IPManager]:
    """Obtiene todas las IPs asignadas a un usuario (no revocadas)."""
    try:
        stmt = select(models.IPManager).where(
            models.IPManager.assigned_to_user_id == user_id,
            models.IPManager.is_revoked.is_(False)
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo IPs asignadas al usuario", extra={"user_id": user_id})
        raise


async def get_ip_by_address(session: AsyncSession, ip_address: str) -> Optional[models.IPManager]:
    """Obtiene una IP por su dirección exacta."""
    try:
        stmt = select(models.IPManager).where(models.IPManager.ip_address == ip_address)
        result = await session.execute(stmt)
        return result.scalars().one_or_none()
    except SQLAlchemyError:
        logger.exception("Error obteniendo IP por dirección", extra={"user_id": None})
        raise


async def count_available_ips_for_type(session: AsyncSession, ip_type: str) -> int:
    """Cuenta el número de IPs disponibles para un tipo específico (no revocadas y disponibles)."""
    try:
        stmt = select(func.count()).select_from(models.IPManager).where(
            models.IPManager.ip_type == ip_type,
            models.IPManager.is_available.is_(True),
            models.IPManager.is_revoked.is_(False)
        )
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)
    except SQLAlchemyError:
        logger.exception("Error contando IPs disponibles", extra={"user_id": None})
        raise


async def cleanup_revoked_ips(session: AsyncSession, commit: bool = False) -> int:
    """
    Limpia IPs revocadas que ya no están asignadas a ningún usuario activo,
    marcándolas como disponibles nuevamente para su reutilización.
    Devuelve el número de IPs limpiadas.
    """
    try:
        # Actualizar IPs revocadas para que estén disponibles nuevamente
        # Solo las que no estén actualmente asignadas a un usuario
        stmt = (
            update(models.IPManager)
            .where(
                models.IPManager.is_revoked.is_(True),
                models.IPManager.assigned_to_user_id.is_(None)
            )
            .values(
                is_available=True,
                revoked_at=None, # Opcional: limpiar la fecha de revocación
                # extra_data puede mantenerse si tiene info útil
            )
        )
        result = await session.execute(stmt)
        affected = result.rowcount
        
        if commit:
            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error limpiando IPs revocadas", extra={"user_id": None})
                raise
                
        logger.info("IPs revocadas limpiadas y disponibles", extra={"user_id": None, "count": affected})
        return affected
    except SQLAlchemyError:
        logger.exception("Error en cleanup_revoked_ips", extra={"user_id": None})
        raise


async def create_ip_entry(
    session: AsyncSession,
    ip_address: str,
    ip_type: str,
    extra_data: Optional[Dict[str, Any]] = None,
    commit: bool = False
) -> models.IPManager:
    """
    Crea una nueva entrada de IP en el manager.
    Útil para poblar la base de datos con IPs generadas por los scripts de instalación.
    """
    try:
        # Verificar si ya existe
        existing = await get_ip_by_address(session, ip_address)
        if existing:
            logger.warning(f"IP {ip_address} ya existe en la base de datos.", extra={"user_id": None})
            return existing

        ip = models.IPManager(
            ip_address=ip_address,
            ip_type=ip_type,
            extra_data=extra_data or {},
            is_available=True,
            is_revoked=False
        )
        session.add(ip)
        
        if commit:
            try:
                await session.commit()
                await session.refresh(ip)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error creando entrada de IP", extra={"user_id": None})
                raise
                
        logger.info("IP registrada", extra={"user_id": None, "ip_address": ip_address, "ip_type": ip_type})
        return ip
    except SQLAlchemyError:
        logger.exception("Error en create_ip_entry", extra={"user_id": None})
        raise


async def get_all_ips_for_type(session: AsyncSession, ip_type: str) -> List[models.IPManager]:
    """Obtiene todas las IPs de un tipo específico, sin importar su estado."""
    try:
        stmt = select(models.IPManager).where(models.IPManager.ip_type == ip_type)
        result = await session.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo todas las IPs de un tipo", extra={"user_id": None})
        raise


async def get_revoked_ips(session: AsyncSession) -> List[models.IPManager]:
    """Obtiene todas las IPs que han sido revocadas."""
    try:
        stmt = select(models.IPManager).where(models.IPManager.is_revoked.is_(True))
        result = await session.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo IPs revocadas", extra={"user_id": None})
        raise
async def count_assigned_ips_for_user(session: AsyncSession, user_id: str) -> int:
    """Cuenta el número de IPs asignadas a un usuario (no revocadas)."""
    try:
        stmt = select(func.count()).select_from(models.IPManager).where(
            models.IPManager.assigned_to_user_id == user_id,
            models.IPManager.is_revoked.is_(False)
        )
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)
    except SQLAlchemyError:
        logger.exception("Error contando IPs asignadas al usuario", extra={"user_id": user_id})
        raise


async def revoke_ips_by_user_and_type(
    session: AsyncSession,
    user_id: str,
    ip_type: str,
    reason: str = "vpn_revoked",
    commit: bool = False
) -> int:
    """
    Revoca todas las IPs asignadas a un usuario de un tipo específico.
    Devuelve el número de IPs revocadas.
    Útil cuando se revoca una VPN y se necesitan revocar las IPs asociadas.
    """
    try:
        # Actualizar IPs asignadas al usuario del tipo especificado
        stmt = (
            update(models.IPManager)
            .where(
                models.IPManager.assigned_to_user_id == user_id,
                models.IPManager.ip_type == ip_type,
                models.IPManager.is_revoked.is_(False)
            )
            .values(
                is_revoked=True,
                is_available=False,
                revoked_at=datetime.now(timezone.utc),
                extra_data=func.json_set(
                    models.IPManager.extra_data,
                    "$.revoked_reason",
                    reason,
                    "$.revoked_by_process",
                    "vpn_revocation"
                )
            )
        )
        result = await session.execute(stmt)
        affected = result.rowcount

        if commit:
            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error revocando IPs por usuario y tipo", extra={"user_id": user_id, "ip_type": ip_type})
                raise

        logger.info("IPs revocadas por usuario y tipo", extra={"user_id": user_id, "ip_type": ip_type, "count": affected, "reason": reason})
        return affected
    except SQLAlchemyError:
        logger.exception("Error en revoke_ips_by_user_and_type", extra={"user_id": user_id, "ip_type": ip_type})
        raise