# database/crud/status.py
from __future__ import annotations
from typing import Optional, Dict, Any

from datetime import datetime, timezone
import logging

from sqlalchemy import select, func, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database import models

logger = logging.getLogger("usipipo.crud.status")


async def count_users(session: AsyncSession) -> int:
    """Devuelve el total de usuarios registrados (int)."""
    try:
        stmt = select(func.count(models.User.id))
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando usuarios", extra={"user_id": None})
        raise


async def count_active_users(session: AsyncSession) -> int:
    """Cuenta usuarios activos (is_active=True)."""
    try:
        stmt = select(func.count(models.User.id)).where(models.User.is_active.is_(True))
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando usuarios activos", extra={"user_id": None})
        raise


async def count_admins(session: AsyncSession) -> int:
    """Cuenta usuarios con rol de admin (is_admin=True)."""
    try:
        stmt = select(func.count(models.User.id)).where(models.User.is_admin.is_(True))
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando admins", extra={"user_id": None})
        raise


async def count_superadmins(session: AsyncSession) -> int:
    """Cuenta usuarios con rol de superadmin (is_superadmin=True)."""
    try:
        stmt = select(func.count(models.User.id)).where(models.User.is_superadmin.is_(True))
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando superadmins", extra={"user_id": None})
        raise


async def count_vpn_configs(session: AsyncSession) -> int:
    """Cuenta total de configuraciones VPN."""
    try:
        stmt = select(func.count(models.VPNConfig.id))
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando VPNConfigs", extra={"user_id": None})
        raise


async def count_vpn_configs_by_type(session: AsyncSession, vpn_type: str) -> int:
    """
    Cuenta las VPN según su tipo (ej. 'wireguard' | 'outline' | 'none').
    No filtra por status here; si quieres solo activas añade status == 'active' en caller.
    """
    try:
        stmt = select(func.count(models.VPNConfig.id)).where(models.VPNConfig.vpn_type == vpn_type)
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando VPNConfigs por tipo", extra={"user_id": None, "vpn_type": vpn_type})
        raise


async def count_active_vpn_configs(session: AsyncSession) -> int:
    """Cuenta VPNs activas (status='active')."""
    try:
        stmt = select(func.count(models.VPNConfig.id)).where(models.VPNConfig.status == "active")
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando VPNs activas", extra={"user_id": None})
        raise


async def count_trial_vpn_configs(session: AsyncSession) -> int:
    """Cuenta VPNs de trial (is_trial=True)."""
    try:
        stmt = select(func.count(models.VPNConfig.id)).where(models.VPNConfig.is_trial.is_(True))
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando VPNs de trial", extra={"user_id": None})
        raise


async def count_paid_vpn_configs(session: AsyncSession) -> int:
    """Cuenta VPNs pagas (is_trial=False)."""
    try:
        stmt = select(func.count(models.VPNConfig.id)).where(models.VPNConfig.is_trial.is_(False))
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando VPNs pagas", extra={"user_id": None})
        raise


async def total_bandwidth_gb(session: AsyncSession) -> float:
    """Devuelve el consumo total de ancho de banda en GB (float)."""
    try:
        stmt = select(func.coalesce(func.sum(models.VPNConfig.bandwidth_used_mb), 0))
        res = await session.execute(stmt)
        total_mb = res.scalar_one() or 0
        return float(total_mb) / 1024.0
    except SQLAlchemyError:
        logger.exception("Error calculando ancho de banda total", extra={"user_id": None})
        raise


async def count_payments(session: AsyncSession) -> int:
    """Cuenta total de pagos registrados."""
    try:
        stmt = select(func.count(models.Payment.id))
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando pagos", extra={"user_id": None})
        raise


async def count_pending_payments(session: AsyncSession) -> int:
    """Cuenta pagos pendientes (status='pending')."""
    try:
        stmt = select(func.count(models.Payment.id)).where(models.Payment.status == "pending")
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando pagos pendientes", extra={"user_id": None})
        raise


async def count_successful_payments(session: AsyncSession) -> int:
    """Cuenta pagos exitosos (status='paid')."""
    try:
        stmt = select(func.count(models.Payment.id)).where(models.Payment.status == "paid")
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando pagos exitosos", extra={"user_id": None})
        raise


async def count_ips(session: AsyncSession) -> int:
    """Cuenta total de IPs en el manager."""
    try:
        stmt = select(func.count(models.IPManager.id))
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando IPs", extra={"user_id": None})
        raise


async def count_available_ips(session: AsyncSession) -> int:
    """Cuenta IPs disponibles (is_available=True y is_revoked=False)."""
    try:
        stmt = select(func.count(models.IPManager.id)).where(
            and_(models.IPManager.is_available.is_(True), models.IPManager.is_revoked.is_(False))
        )
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando IPs disponibles", extra={"user_id": None})
        raise


async def count_assigned_ips(session: AsyncSession) -> int:
    """Cuenta IPs asignadas (assigned_to_user_id IS NOT NULL y no revocadas)."""
    try:
        stmt = select(func.count(models.IPManager.id)).where(
            and_(models.IPManager.assigned_to_user_id.isnot(None), models.IPManager.is_revoked.is_(False))
        )
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count or 0)
    except SQLAlchemyError:
        logger.exception("Error contando IPs asignadas", extra={"user_id": None})
        raise


async def get_system_status(session: AsyncSession) -> Dict[str, Any]:
    """
    Devuelve un resumen completo del estado del sistema.
    Útil para dashboards administrativos.
    """
    try:
        # Ejecutar todas las consultas en paralelo para eficiencia
        users_total = await count_users(session)
        users_active = await count_active_users(session)
        admins = await count_admins(session)
        superadmins = await count_superadmins(session)

        vpn_total = await count_vpn_configs(session)
        vpn_active = await count_active_vpn_configs(session)
        vpn_trials = await count_trial_vpn_configs(session)
        vpn_paid = await count_paid_vpn_configs(session)

        bandwidth_gb = await total_bandwidth_gb(session)

        payments_total = await count_payments(session)
        payments_pending = await count_pending_payments(session)
        payments_successful = await count_successful_payments(session)

        ips_total = await count_ips(session)
        ips_available = await count_available_ips(session)
        ips_assigned = await count_assigned_ips(session)

        status = {
            "users": {
                "total": users_total,
                "active": users_active,
                "admins": admins,
                "superadmins": superadmins,
            },
            "vpn": {
                "total": vpn_total,
                "active": vpn_active,
                "trials": vpn_trials,
                "paid": vpn_paid,
            },
            "bandwidth_gb": bandwidth_gb,
            "payments": {
                "total": payments_total,
                "pending": payments_pending,
                "successful": payments_successful,
            },
            "ips": {
                "total": ips_total,
                "available": ips_available,
                "assigned": ips_assigned,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info("Status del sistema obtenido", extra={"user_id": None})
        return status
    except SQLAlchemyError:
        logger.exception("Error obteniendo status del sistema", extra={"user_id": None})
        raise