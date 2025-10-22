# bot/handlers/info.py

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from database.crud import users as crud_users
from database.db import AsyncSessionLocal
from utils.helpers import log_and_notify, log_error_and_notify, safe_chat_id_from_update

logger = logging.getLogger("usipipo.handlers.info")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /info handler: muestra información del bot, enlaces y botones rápidos.
    Similar a /start pero orientado a documentación breve y FAQ.
    """
    tg_user = update.effective_user
    bot = context.bot
    chat_id = safe_chat_id_from_update(update)

    # Obtener o crear usuario con sesión async
    async with AsyncSessionLocal() as session:
        user = await crud_users.ensure_user(session, {
            "id": tg_user.id,
            "username": tg_user.username,
            "first_name": tg_user.first_name,
            "last_name": tg_user.last_name,
        }, commit=False)
        user_id = user.id  # UUID string

    info_msg = (
        f"ℹ️ Información de uSipipo\n\n"
        f"Hola <b>{tg_user.first_name}</b> — euSipipo te permite crear y administrar VPNs de Wireguard y Outline fácil, rapido y seguro.\n\n"
        "Comandos importantes:\n"
        "• <code>/register</code> — Registrar tu cuenta\n"
        "• <code>/trialvpn &lt;wireguard|outline&gt;</code> — Solicitar un trial de 7 días\n"
        "• <code>/newvpn</code> — Crear un config de VPN completa\n\n"
        "Soporte y seguridad:\n"
        "- Tus acciones quedan registradas para auditoría.\n"
        "- Los administradores reciben notificaciones de eventos relevantes.\n\n"
        "¿Listo para comenzar? Usa los botones debajo para ejecutar un comando."
    )

    keyboard = [
        [InlineKeyboardButton("Registrar", callback_data='/register')],
        [InlineKeyboardButton("Nueva VPN", callback_data='/newvpn')],
        [InlineKeyboardButton("Trial Wireguard", callback_data='/trialvpn wireguard')],
        [InlineKeyboardButton("Trial Outline", callback_data='/trialvpn outline')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        # Registrar auditoría / log con sesión y user_id correcto
        await log_and_notify(
            session,
            bot,
            chat_id,
            user_id,
            action="command_info",
            details="Usuario ejecutó /info",
            message=info_msg,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

    except Exception as e:  # pylint: disable=broad-except
        logger.exception("Error in info_command: %s", type(e).__name__, extra={"tg_id": tg_user.id})
        await log_error_and_notify(
            session,
            bot,
            chat_id,
            user_id,
            action="command_info",
            error=e,
            public_message="Ha ocurrido un error mostrando la información. Intenta más tarde.",
        )
