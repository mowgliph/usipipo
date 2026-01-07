"""
Handler del Menú Principal.

Maneja la navegación del menú principal.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards
from telegram_bot.keyboard.keyboard import Keyboards
from utils.logger import logger


async def show_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para el botón '📋 Mostrar Menú' del teclado de respaldo."""
    user = update.effective_user
    logger.log_bot_event("INFO", f"Botón 'Mostrar Menú' presionado por usuario {user.id}")
    
    try:
        is_admin = user.id == int(settings.ADMIN_ID)
        
        await update.message.reply_text(
            text="👇 Menú Principal",
            reply_markup=InlineKeyboards.main_menu(is_admin=is_admin),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.log_error(e, context="show_menu_handler", user_id=user.id)
        await update.message.reply_text(
            text="❌ Error al mostrar el menú. Por favor, intenta nuevamente.",
            reply_markup=Keyboards.show_menu_button()
        )
