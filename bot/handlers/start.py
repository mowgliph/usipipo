# bot/handlers/start.py

from __future__ import annotations

import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from database.db import AsyncSessionLocal
from services import user as user_service
from utils.helpers import log_and_notify, log_error_and_notify

logger = logging.getLogger("usipipo.handlers.start")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /start handler asíncrono.
    Envía mensaje de bienvenida y muestra un teclado inline con comandos útiles.
    Registra la acción mediante log_and_notify (audit/logger) y envía el mensaje con botones inline.
    """
    if not update.effective_chat or not update.message or not update.effective_user:
        return

    tg_user = update.effective_user
    bot = context.bot
    chat_id = update.effective_chat.id
    user_id = None

    async with AsyncSessionLocal() as session:
        try:
            # Obtener user_id si está registrado
            db_user = await user_service.get_user_by_telegram_id(session, tg_user.id)
            if db_user:
                user_id = str(db_user.id)  # UUID como string

            welcome_msg = (
                f"¡Hola <b>{tg_user.first_name}</b>! 👋 Bienvenido a <b>uSipipo</b> 🚀\n\n"
                "Aquí podrás generar configuraciones de VPN <b>Outline</b> y <b>WireGuard</b> "
                "de forma sencilla, rápida y segura.\n\n"
                "Usa <code>/help</code> para ver los comandos disponibles.\n"
                "👉 Recuerda registrarte primero con <code>/register</code>."
            )

            # Teclado inline con comandos frecuentes
            keyboard = [
                [
                    InlineKeyboardButton("ℹ️ Info", callback_data="info"),
                    InlineKeyboardButton("📝 Registrarse", callback_data="register")
                ],
                [
                    InlineKeyboardButton("🆕 Nueva VPN", callback_data="newvpn"),
                    InlineKeyboardButton("🔒 Proxy MTProto", callback_data="proxy")
                ],
                [
                    InlineKeyboardButton("🆓 Trial WireGuard", callback_data="trialvpn_wireguard"),
                    InlineKeyboardButton("🆓 Trial Outline", callback_data="trialvpn_outline")                    
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Registrar auditoría / log
            await log_and_notify(
                session,           # session para DB audit
                bot,               # bot para enviar mensaje
                chat_id,           # chat_id para notificación
                user_id,           # user_id como string UUID
                action="command_start",
                details="Usuario ejecutó /start",
                message=welcome_msg,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error en start_command: %s", type(e).__name__, extra={"tg_id": tg_user.id, "user_id": user_id})
            await log_error_and_notify(
                session,
                bot,
                chat_id,
                user_id,
                action="command_start",
                error=e,
                public_message="Ha ocurrido un error al procesar /start. Intenta más tarde.",
            )
