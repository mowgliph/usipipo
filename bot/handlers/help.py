import logging

from telegram import Update
from telegram.ext import ContextTypes

from database.db import AsyncSessionLocal
from services import user as user_service
from utils.helpers import send_generic_error

logger = logging.getLogger("usipipo.handlers.help")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # pylint: disable=unused-argument
    """
    Responde al comando /help mostrando los comandos disponibles según rol.
    """
    if not update.effective_chat or not update.message or not update.effective_user:
        return

    tg_user = update.effective_user

    async with AsyncSessionLocal() as db:
        try:
            # Buscar usuario en DB
            db_user = await user_service.get_user_by_telegram_id(db, tg_user.id)
            user_id = db_user.id if db_user else None

            # Generar mensaje de ayuda usando service layer
            help_msg = await user_service.get_help_message(db, user_id)

            # Enviar mensaje de ayuda
            await update.message.reply_text(help_msg, parse_mode="HTML")

        except Exception as e:  # pylint: disable=broad-except
            logger.exception(
                "Error in help_command: %s",
                type(e).__name__,
                extra={"tg_id": tg_user.id}
            )
            await send_generic_error(
                update,
                "Error obteniendo ayuda. El equipo ha sido notificado."
            )