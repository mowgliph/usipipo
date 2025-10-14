# services/alerts.py

from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from telegram import Bot

from database import models
from database.crud import logs as crud_logs, vpn as crud_vpn
from utils import helpers

logger = logging.getLogger("usipipo.alerts")

async def get_expiring_vpns(
    session: AsyncSession,
    hours: int = 24,
    limit: int = 100,
    offset: int = 0,
) -> List[models.VPNConfig]:
    """
    Devuelve VPNs activas que expiran en las próximas `hours` horas.
    - Usa AsyncSession.
    - Soporta paginación (limit, offset).
    - Evita alertas repetidas con extra_data['alerted'].
    """
    try:
        now = datetime.now(tz=timezone.utc)
        limit_time = now + timedelta(hours=hours)
        stmt = (
            select(models.VPNConfig)
            .where(
                models.VPNConfig.status == "active",
                models.VPNConfig.expires_at.isnot(None),
                models.VPNConfig.expires_at <= limit_time,
                (models.VPNConfig.extra_data["alerted"].is_(None))
            )
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        vpns = result.scalars().all()

        for vpn in vpns:
            await crud_logs.create_audit_log(
                session=session,
                user_id=vpn.user_id,
                action="vpn_expiring_soon",
                details=f"VPN ID {vpn.id} ({vpn.vpn_type}) expira el {vpn.expires_at.strftime('%Y-%m-%d %H:%M UTC')}",
                commit=False,
            )
            extra = dict(vpn.extra_data or {})
            extra["alerted"] = datetime.now(tz=timezone.utc).isoformat()
            vpn.extra_data = extra

        logger.info(
            "Encontradas %d VPNs próximas a expirar",
            len(vpns),
            extra={"user_id": None}
        )
        return vpns
    except Exception as e:
        logger.exception("Error obteniendo VPNs próximas a expirar", extra={"user_id": None})
        raise

async def get_expired_vpns(
    session: AsyncSession,
    limit: int = 100,
    offset: int = 0,
) -> List[models.VPNConfig]:
    """
    Devuelve VPNs activas ya expiradas.
    - Usa AsyncSession.
    - Soporta paginación.
    """
    try:
        now = datetime.now(tz=timezone.utc)
        stmt = (
            select(models.VPNConfig)
            .where(
                models.VPNConfig.status == "active",
                models.VPNConfig.expires_at.isnot(None),
                models.VPNConfig.expires_at < now,
            )
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        vpns = result.scalars().all()

        for vpn in vpns:
            await crud_logs.create_audit_log(
                session=session,
                user_id=vpn.user_id,
                action="vpn_expired",
                details=f"VPN ID {vpn.id} ({vpn.vpn_type}) expiró el {vpn.expires_at.strftime('%Y-%m-%d %H:%M UTC')}",
                commit=False,
            )

        logger.info("Encontradas %d VPNs expiradas", len(vpns), extra={"user_id": None})
        return vpns
    except Exception as e:
        logger.exception("Error obteniendo VPNs expiradas", extra={"user_id": None})
        raise

async def send_expiration_alerts(
    session: AsyncSession,
    bot: Bot,
    hours: int = 24,
    limit: int = 100,
) -> None:
    """
    Envía alertas a usuarios con VPNs próximas a expirar.
    - Usa format_expiration_message de helpers.
    - Registra logs y notifica admins en errores.
    """
    try:
        vpns = await get_expiring_vpns(session, hours=hours, limit=limit)
        for vpn in vpns:
            chat_id = vpn.user_id
            msg = await helpers.format_expiration_message(vpn)
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=msg,
                    parse_mode="HTML",
                )
                await crud_logs.create_audit_log(
                    session=session,
                    user_id=vpn.user_id,
                    action="alert_expiration_sent",
                    details=f"Alerta enviada para VPN {vpn.id}",
                    commit=False,
                )
            except Exception as e:
                await crud_logs.create_audit_log(
                    session=session,
                    user_id=vpn.user_id,
                    action="alert_expiration_failed",
                    details=f"VPN {vpn.id} | Error: {str(e)}",
                    commit=False,
                )
                await helpers.notify_admins(
                    session=session,
                    bot=bot,
                    message=f"Error enviando alerta para VPN {vpn.id}: {str(e)}",
                    action="alert_expiration_failed",
                    details=str(e),
                )
    except Exception as e:
        logger.exception("Error enviando alertas de expiración", extra={"user_id": None})
        raise