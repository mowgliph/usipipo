from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards

async def ayuda_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra la guía de uso del bot y explica las diferencias 
    entre los protocolos disponibles.
    """
    try:
        await update.message.reply_text(
            text=Messages.Welcome.HELP,
            reply_markup=InlineKeyboards.main_menu(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error en ayuda_handler: {e}")
        await update.message.reply_text(
            "Hubo un error al cargar la ayuda, pero puedes usar el menú inferior para navegar."
        )


async def help_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para el comando /help.
    Muestra el menú del centro de ayuda con todas las opciones disponibles.
    """
    try:
        await update.message.reply_text(
            text=Messages.Help.MENU_TITLE,
            reply_markup=InlineKeyboards.help_menu(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error en help_command_handler: {e}")
        await update.message.reply_text(
            "Hubo un error al cargar el centro de ayuda. Por favor, intenta nuevamente."
        )
