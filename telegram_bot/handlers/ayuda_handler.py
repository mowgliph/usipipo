"""
Handler para el centro de ayuda del bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger

from telegram_bot.messages import UserMessages, Messages
from telegram_bot.keyboard import SupportKeyboards

async def ayuda_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra la guía de uso del bot y explica las diferencias 
    entre los protocolos disponibles.
    """
    try:
        await update.message.reply_text(
            text=UserMessages.Help.HELP,
            reply_markup=SupportKeyboards.help_menu(),
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
        # Try to use Messages.Help.MENU_TITLE if it exists
        # otherwise use UserMessages.Help.MAIN_MENU
        menu_title = getattr(Messages.Help, 'MENU_TITLE', None)
        if menu_title is None:
            menu_title = UserMessages.Help.MAIN_MENU

        await update.message.reply_text(
            text=menu_title,
            reply_markup=SupportKeyboards.help_menu(),
            parse_mode="Markdown"
        )
    except AttributeError:
        # Fallback to UserMessages.Help.MAIN_MENU
        await update.message.reply_text(
            text=UserMessages.Help.MAIN_MENU,
            reply_markup=SupportKeyboards.help_menu(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error en help_command_handler: {e}")
        await update.message.reply_text(
            "Hubo un error al cargar el centro de ayuda. Por favor, intenta nuevamente."
        )
