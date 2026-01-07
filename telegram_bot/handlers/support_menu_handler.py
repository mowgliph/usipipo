"""
Handler de soporte para el menú de operaciones del bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from telegram_bot.messages import SupportMessages
from telegram_bot.keyboard import SupportKeyboards

class SupportMenuHandler:
    """Handler para el menú de soporte desde operaciones."""
    
    def __init__(self, support_service):
        self.support_service = support_service
    
    async def show_support_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú de soporte desde operaciones."""
        await update.message.reply_text(
            text=SupportMessages.Tickets.MENU,
            reply_markup=SupportKeyboards.support_active(),
            parse_mode="Markdown"
        )
    
    def get_handlers(self):
        """Retorna los handlers de soporte para el menú de operaciones."""
        return [
            MessageHandler(filters.Regex("^🎫 Soporte$"), self.show_support_menu)
        ]

def get_support_menu_handler(support_service):
    """Función para obtener el handler de soporte del menú de operaciones."""
    handler = SupportMenuHandler(support_service)
    return handler.get_handlers()
