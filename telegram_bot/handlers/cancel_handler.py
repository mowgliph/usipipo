from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger

from telegram_bot.messages import CommonMessages
from telegram_bot.keyboard import CommonKeyboards

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para el comando /cancelar.
    Cancela cualquier proceso en curso y devuelve al usuario al menú principal.
    """
    try:
        user = update.effective_user
        logger.log_bot_event("INFO", f"Comando /cancelar ejecutado por usuario {user.id}")
        
        # Determinar si es admin para mostrar el menú correspondiente
        from config import settings
        is_admin = user.id == int(settings.ADMIN_ID)
        
        await update.message.reply_text(
            text=CommonMessages.Confirmation.CANCELLED,
            reply_markup=CommonKeyboards.back_button("main_menu"),
            parse_mode="Markdown"
        )
        
        # Cancelar cualquier conversación en curso
        if context.user_data:
            context.user_data.clear()
            logger.log_bot_event("INFO", f"Datos de usuario limpiados para usuario {user.id}")
            
    except Exception as e:
        logger.log_error(e, context='cancel_handler', user_id=user.id)
        await update.message.reply_text(
            text=CommonMessages.Errors.GENERIC.format(error="No se pudo procesar la cancelación"),
            reply_markup=CommonKeyboards.back_button("main_menu")
        )