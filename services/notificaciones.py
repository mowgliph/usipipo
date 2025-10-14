# services/notification.py

from typing import Optional, List
import logging
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Bot
from telegram.error import TelegramError

from database import models
from database.crud import users as crud_users, logs as crud_logs
from utils.helpers import log_and_notify, log_error_and_notify, notify_admins

logger = logging.getLogger("usipipo.notification")

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
                    await log_and_notify(
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
                    await log_error_and_notify(
                        session=session,
                        bot=bot,
                        chat_id=None,  # No notificar al usuario
                        user_id=user.id,
                        action="broadcast_message_failed",
                        error=te,
                        public_message=None,
                    )

            offset += batch_size

        except Exception as e:
            logger.exception("Error en broadcast", extra={"user_id": sender_user_id})
            await notify_admins(
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