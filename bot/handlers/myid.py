# bot/handlers/myid.py
from telegram import Update
from telegram.ext import ContextTypes
import logging

from database.db import get_session
from services.user import get_user_telegram_info
from utils.helpers import send_success, send_generic_error

logger = logging.getLogger("usipipo.handlers.myid")

async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Devuelve la información básica de Telegram del usuario (ID, nombre, username).
    Uso: /myid
    Registra la acción en AuditLog y notifica errores a admins.
    """
    user = update.effective_user
    async with get_session() as session:
        try:
            # Obtener información del usuario desde el servicio
            text = await get_user_telegram_info(session, user)
            await send_success(update, text)
        except Exception as e:
            logger.exception("Error en myid_command", extra={"tg_id": user.id})
            await send_generic_error(update, "Error obteniendo tu información. El equipo ha sido notificado.")