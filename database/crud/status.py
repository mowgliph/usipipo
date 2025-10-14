# database/crud/status.py
from __future__ import annotations
from typing import Optional

from datetime import datetime, timezone
import logging

from sqlalchemy import select, func
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