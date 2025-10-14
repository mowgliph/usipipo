# database/crud/vpn.py

from __future__ import annotations
from typing import Optional, List, Dict, Any

from datetime import datetime, timedelta, timezone
import logging

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database import models

logger = logging.getLogger("usipipo")


async def get_vpn_config(session: AsyncSession, vpn_id: str) -> Optional[models.VPNConfig]:
    """Obtiene una configuración VPN por su ID (UUID string)."""
    try:
        res = await session.execute(select(models.VPNConfig).where(models.VPNConfig.id == vpn_id))
        return res.scalars().one_or_none()
    except SQLAlchemyError:
        logger.exception("Error obteniendo VPNConfig por id", extra={"user_id": None, "vpn_id": vpn_id})
        raise


async def get_vpn_configs_for_user(session: AsyncSession, user_id: str) -> List[models.VPNConfig]:
    """Obtiene todas las configuraciones VPN asociadas a un usuario (user_id es UUID string)."""
    try:
        res = await session.execute(select(models.VPNConfig).where(models.VPNConfig.user_id == user_id))
        return res.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo VPNConfigs por usuario", extra={"user_id": None, "target_user_id": user_id})
        raise


async def get_active_trial_for_user(session: AsyncSession, user_id: str) -> Optional[models.VPNConfig]:
    """
    Devuelve el trial activo del usuario si existe.
    Condiciones: is_trial=True, status='active', expires_at is null or > now (UTC).
    """
    try:
        now = datetime.now(timezone.utc)
        stmt = select(models.VPNConfig).where(
            models.VPNConfig.user_id == user_id,
            models.VPNConfig.is_trial.is_(True),
            models.VPNConfig.status == "active",
            (models.VPNConfig.expires_at.is_(None) | (models.VPNConfig.expires_at > now)),
        ).order_by(models.VPNConfig.created_at.desc()).limit(1)
        res = await session.execute(stmt)
        return res.scalars().one_or_none()
    except SQLAlchemyError:
        logger.exception("Error comprobando trial activo", extra={"user_id": None, "target_user_id": user_id})
        raise


async def create_vpn_config(
    session: AsyncSession,
    user_id: str,
    vpn_type: str,
    config_name: Optional[str],
    config_data: Dict[str, Any] | str,
    *,
    expires_at: Optional[datetime] = None,
    extra_data: Optional[Dict[str, Any]] = None,
    is_trial: bool = False,
    commit: bool = False,
) -> models.VPNConfig:
    """
    Crea un registro VPNConfig en estado active. No realiza validaciones de negocio.
    - user_id: UUID string
    - vpn_type: 'wireguard' | 'outline' | 'none' (validar en services)
    - config_data: dict (se almacenará como JSON) o str
    - commit: por defecto False para que el service coordine la transacción
    """
    try:
        # Normalizar config_data a dict si viene como str (service debería validar)
        cfg = config_data if isinstance(config_data, dict) else {"content": str(config_data)}

        vpn = models.VPNConfig(
            user_id=user_id,
            vpn_type=vpn_type,
            config_name=config_name,
            config_data=cfg,
            expires_at=expires_at,
            extra_data=extra_data or {},
            status="active",
            is_trial=bool(is_trial),
            bandwidth_used_mb=0.0,
            created_at=datetime.now(timezone.utc),
        )
        session.add(vpn)
        if commit:
            try:
                await session.commit()
                await session.refresh(vpn)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error commiteando create_vpn_config", extra={"user_id": user_id})
                raise
        logger.info("VPNConfig creado", extra={"user_id": user_id, "vpn_id": getattr(vpn, "id", None)})
        return vpn
    except SQLAlchemyError:
        logger.exception("Error creando VPNConfig", extra={"user_id": user_id})
        raise


async def create_trial_vpn(
    session: AsyncSession,
    user_id: str,
    vpn_type: str,
    config_name: Optional[str],
    config_data: Dict[str, Any] | str,
    *,
    duration_days: int = 7,
    extra_data: Optional[Dict[str, Any]] = None,
    commit: bool = False,
) -> models.VPNConfig:
    """
    Crea un VPN trial con duración `duration_days`.
    Previene la creación de más de un trial activo por usuario.
    """
    try:
        existing = await get_active_trial_for_user(session, user_id)
        if existing:
            logger.info("Intento de crear trial cuando ya existe uno activo", extra={"user_id": user_id, "vpn_id": existing.id})
            raise ValueError("user_has_active_trial")

        expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)
        vpn = await create_vpn_config(
            session,
            user_id=user_id,
            vpn_type=vpn_type,
            config_name=config_name,
            config_data=config_data,
            expires_at=expires_at,
            extra_data=extra_data,
            is_trial=True,
            commit=commit,
        )
        return vpn
    except ValueError:
        raise
    except SQLAlchemyError:
        logger.exception("Error creando trial VPN", extra={"user_id": user_id})
        raise


async def has_trial(session: AsyncSession, user_id: str) -> bool:
    """Verifica si el usuario tiene un trial activo (sin devolver el objeto)."""
    try:
        now = datetime.now(timezone.utc)
        stmt = select(func.count()).select_from(models.VPNConfig).where(
            models.VPNConfig.user_id == user_id,
            models.VPNConfig.is_trial.is_(True),
            models.VPNConfig.status == "active",
            (models.VPNConfig.expires_at.is_(None) | (models.VPNConfig.expires_at > now)),
        )
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count) > 0
    except SQLAlchemyError:
        logger.exception("Error comprobando existencia de trial", extra={"user_id": user_id})
        raise


async def update_vpn_status(session: AsyncSession, vpn_id: str, status: str, *, commit: bool = False) -> Optional[models.VPNConfig]:
    """Actualiza el estado de una configuración VPN (active/revoked/expired)."""
    try:
        vpn = await get_vpn_config(session, vpn_id)
        if not vpn:
            return None
        vpn.status = status
        if commit:
            try:
                await session.commit()
                await session.refresh(vpn)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error guardando status de VPNConfig", extra={"user_id": vpn.user_id, "vpn_id": vpn_id})
                raise
        logger.info("Status VPN actualizado", extra={"user_id": vpn.user_id, "vpn_id": vpn_id, "status": status})
        return vpn
    except SQLAlchemyError:
        logger.exception("Error en update_vpn_status", extra={"user_id": None, "vpn_id": vpn_id})
        raise


async def revoke_vpn(session: AsyncSession, vpn_id: str, reason: str, *, commit: bool = False) -> bool:
    """
    Marca una VPN como 'revoked' y añade un campo 'extra_data.revoked_reason' si procede.
    Devuelve True si la vpn existía y fue modificada.
    """
    try:
        vpn = await get_vpn_config(session, vpn_id)
        if not vpn:
            return False
        vpn.status = "revoked"
        extra = dict(vpn.extra_data or {})
        extra["revoked_reason"] = reason
        extra["revoked_at"] = datetime.now(timezone.utc).isoformat()
        vpn.extra_data = extra
        if commit:
            try:
                await session.commit()
                await session.refresh(vpn)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error revocando VPNConfig", extra={"user_id": vpn.user_id, "vpn_id": vpn_id})
                raise
        logger.info("VPN revocada", extra={"user_id": vpn.user_id, "vpn_id": vpn_id, "reason": reason})
        return True
    except SQLAlchemyError:
        logger.exception("Error en revoke_vpn", extra={"user_id": None, "vpn_id": vpn_id})
        raise


async def delete_vpn_config(session: AsyncSession, vpn_id: str, *, commit: bool = False) -> bool:
    """Elimina una configuración VPN por ID."""
    try:
        vpn = await get_vpn_config(session, vpn_id)
        if not vpn:
            return False
        await session.delete(vpn)
        if commit:
            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error borrando VPNConfig", extra={"user_id": vpn.user_id, "vpn_id": vpn_id})
                raise
        logger.info("VPNConfig eliminada", extra={"user_id": vpn.user_id, "vpn_id": vpn_id})
        return True
    except SQLAlchemyError:
        logger.exception("Error en delete_vpn_config", extra={"user_id": None, "vpn_id": vpn_id})
        raise


async def get_expired_trials(session: AsyncSession) -> List[models.VPNConfig]:
    """
    Devuelve todos los VPN trials vencidos y aún activos.
    Útil para jobs de mantenimiento.
    """
    try:
        now = datetime.now(timezone.utc)
        stmt = select(models.VPNConfig).where(
            models.VPNConfig.is_trial.is_(True),
            models.VPNConfig.status == "active",
            models.VPNConfig.expires_at < now,
        )
        res = await session.execute(stmt)
        return res.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error listando trials vencidos", extra={"user_id": None})
        raise


# =========================
# Métricas / helpers simples
# =========================

async def count_vpn_configs_by_type(session: AsyncSession, vpn_type: str) -> int:
    try:
        stmt = select(func.count()).select_from(models.VPNConfig).where(models.VPNConfig.vpn_type == vpn_type)
        res = await session.execute(stmt)
        return int(res.scalar_one())
    except SQLAlchemyError:
        logger.exception("Error contando VPNs por tipo", extra={"user_id": None})
        raise


async def total_bandwidth_gb(session: AsyncSession) -> float:
    try:
        stmt = select(func.coalesce(func.sum(models.VPNConfig.bandwidth_used_mb), 0))
        res = await session.execute(stmt)
        total_mb = res.scalar_one() or 0
        return float(total_mb) / 1024.0
    except SQLAlchemyError:
        logger.exception("Error calculando ancho de banda total", extra={"user_id": None})
        raise