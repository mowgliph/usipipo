from telegram import Update
from telegram.ext import ContextTypes
from database.db import AsyncSessionLocal
from database.crud import users as crud_user
from services import user as user_service
from utils.helpers import log_and_notify, log_error_and_notify
from database import models


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Responde al comando /help mostrando los comandos disponibles según rol.
    """
    tg_user = update.effective_user
    db_user = None

    async with AsyncSessionLocal() as db:
        try:
            # Buscar usuario en DB
            db_user = await crud_user.get_user_by_telegram_id(db, tg_user.id)
            user_id = db_user.id if db_user else None

            # Generar mensaje de ayuda usando service layer
            help_msg = await user_service.get_help_message(db, user_id)

            # Log + notificación
            chat_id = update.effective_chat.id if update.effective_chat else None
            bot = context.bot
            await log_and_notify(
                db,
                bot,
                chat_id,
                user_id,
                "command_help",
                "Usuario ejecutó /help",
                help_msg,
                parse_mode="HTML",
            )

        except Exception as e:
            chat_id = update.effective_chat.id if update.effective_chat else None
            bot = context.bot
            uid = db_user.id if db_user and isinstance(db_user, models.User) else None
            await log_error_and_notify(db, bot, chat_id, uid, "command_help", e)