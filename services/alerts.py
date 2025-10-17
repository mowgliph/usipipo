# services/alerts.py

from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
import logging
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from database import models
from database.crud import logs as crud_logs, vpn as crud_vpn, users as crud_users
from utils import helpers

from typing import List
from config.superadmins import SUPERADMINS
from services.status import get_status_metrics
from database.crud.logs import get_audit_logs
from database.db import AsyncSessionLocal

logger = logging.getLogger("usipipo.alerts")


async def send_broadcast_message(
    session: AsyncSession,
    bot: Bot,
    sender_user_id: str,
    message: str,
    batch_size: int = 100,
) -> tuple[int, List[str]]:
    """
    Envía un mensaje a todos los usuarios activos con paginación y rate limiting.
    - Valida que el sender sea admin o superadmin.
    - Registra en AuditLog el envío y errores.
    - Devuelve (total_enviados, lista_de_errores).
    """
    # Validar permisos
    is_admin = await crud_users.is_user_admin(session, sender_user_id)
    is_superadmin = await crud_users.is_user_superadmin(session, sender_user_id)
    if not (is_admin or is_superadmin):
        logger.warning("Usuario no autorizado para broadcast", extra={"user_id": sender_user_id})
        raise ValueError("Se requiere permiso de admin o superadmin")

    # Sanitizar mensaje
    if not message or len(message) > 4096:
        logger.error("Mensaje inválido para broadcast", extra={"user_id": sender_user_id})
        raise ValueError("El mensaje debe estar entre 1 y 4096 caracteres")

    total_sent = 0
    errors = []
    offset = 0

    while True:
        try:
            users = []
            async for user in crud_users.get_active_users(session, batch_size, offset):
                users.append(user)
            if not users:
                break

            for user in users:
                try:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=message,
                        parse_mode="HTML",
                    )
                    await helpers.log_and_notify(
                        session=session,
                        bot=bot,
                        chat_id=user.telegram_id,
                        user_id=user.id,
                        action="broadcast_message_sent",
                        details=f"Broadcast enviado por {sender_user_id}",
                        message=message,
                    )
                    total_sent += 1
                    # Rate limiting: Telegram permite ~30 mensajes/segundo
                    await asyncio.sleep(0.035)  # ~28 mensajes/segundo
                except TelegramError as te:
                    error_msg = f"Fallo al enviar a {user.telegram_id}: {str(te)}"
                    errors.append(error_msg)
                    await helpers.log_error_and_notify(
                        session=session,
                        bot=bot,
                        chat_id=None,  # No notificar al usuario
                        user_id=user.id,
                        action="broadcast_message_failed",
                        error=te,
                        public_message="",  # No enviar mensaje público
                        notify_user=False,
                    )

            offset += batch_size

        except Exception as e:
            logger.exception("Error en broadcast", extra={"user_id": sender_user_id})
            await helpers.notify_admins(
                session=session,
                bot=bot,
                message=f"⚠️ Error en broadcast: {str(e)}\nEnviados: {total_sent}\nErrores: {len(errors)}",
                action="broadcast_error",
            )
            errors.append(str(e))
            break

    # Registrar resumen en AuditLog
    await crud_logs.create_audit_log(
        session=session,
        user_id=sender_user_id,
        action="broadcast_message",
        payload={
            "message": message[:1000],  # Truncar para DB
            "total_sent": total_sent,
            "errors": errors[:10],  # Limitar para DB
        },
        commit=True,
    )

    return total_sent, errors

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
    - Carga la relación user con joinedload para evitar N+1 queries.
    """
    try:
        now = datetime.now(tz=timezone.utc)
        limit_time = now + timedelta(hours=hours)
        stmt = (
            select(models.VPNConfig)
            .options(joinedload(models.VPNConfig.user))
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
        vpns = result.scalars().unique().all()

        for vpn in vpns:
            await crud_logs.create_audit_log(
                session=session,
                user_id=vpn.user_id,
                action="vpn_expiring_soon",
                payload={"vpn_id": vpn.id, "vpn_type": vpn.vpn_type, "expires_at": vpn.expires_at.isoformat()},
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
    - Carga la relación user con joinedload para evitar N+1 queries.
    """
    try:
        now = datetime.now(tz=timezone.utc)
        stmt = (
            select(models.VPNConfig)
            .options(joinedload(models.VPNConfig.user))
            .where(
                models.VPNConfig.status == "active",
                models.VPNConfig.expires_at.isnot(None),
                models.VPNConfig.expires_at < now,
            )
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        vpns = result.scalars().unique().all()

        for vpn in vpns:
            await crud_logs.create_audit_log(
                session=session,
                user_id=vpn.user_id,
                action="vpn_expired",
                payload={"vpn_id": vpn.id, "vpn_type": vpn.vpn_type, "expired_at": vpn.expires_at.isoformat()},
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
    - Usa vpn.user.telegram_id como chat_id (ya que user_id es UUID string).
    """
    try:
        vpns = await get_expiring_vpns(session, hours=hours, limit=limit)
        for vpn in vpns:
            if not vpn.user:
                logger.warning("VPN sin usuario relacionado", extra={"user_id": vpn.user_id, "vpn_id": vpn.id})
                continue
            chat_id = vpn.user.telegram_id
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
                    payload={"vpn_id": vpn.id},
                    commit=False,
                )
            except Exception as e:
                await crud_logs.create_audit_log(
                    session=session,
                    user_id=vpn.user_id,
                    action="alert_expiration_failed",
                    payload={"vpn_id": vpn.id, "error": str(e)},
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


# -------------------------
# Notificaciones del sistema
# -------------------------

async def format_status_message(metrics: dict, logs: List) -> str:
    """Formatea el mensaje de status diario con métricas y logs."""
    message = "📊 **Status Diario del Sistema**\n\n"
    message += f"👥 Usuarios totales: {metrics['total_users']}\n"
    message += f"🔒 VPN WireGuard: {metrics['total_wireguard']}\n"
    message += f"🌐 VPN Outline: {metrics['total_outline']}\n"
    message += f"📈 Bandwidth total: {metrics['total_bandwidth']} GB\n"
    message += f"⏱️ Uptime: {metrics['uptime']}\n"
    message += f"🗄️ DB Status: {metrics['db_status']}\n\n"
    message += "📝 **Últimos 5 Logs de Auditoría:**\n"

    if logs:
        for log in logs:
            user_info = f"@{log.user.username}" if log.user else "Sistema"
            action = log.action.replace('_', ' ').title()
            timestamp = log.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            message += f"• {timestamp} - {user_info}: {action}\n"
    else:
        message += "No hay logs recientes.\n"

    return message


async def send_daily_status_notification(bot: Bot = None, context: ContextTypes.DEFAULT_TYPE = None) -> None:
    """
    Envía notificación de status diario a superadmins.
    Puede ser llamado con bot (para reinicio) o context (para jobs).
    """
    try:
        if context:
            bot = context.bot

        async with AsyncSessionLocal() as session:
            metrics = await get_status_metrics(session)
            logs = await get_audit_logs(session, limit=5)

            message = await format_status_message(metrics, logs)

            for admin_id in SUPERADMINS:
                try:
                    await bot.send_message(chat_id=admin_id, text=message, parse_mode='Markdown')
                    logger.info("Notificación diaria enviada", extra={"admin_id": admin_id})
                except Exception as e:
                    logger.error("Error enviando notificación a superadmin", extra={"admin_id": admin_id, "error": str(e)})

    except Exception as e:
        logger.exception("Error en send_daily_status_notification")