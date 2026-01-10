"""
Teclados para el asistente IA Sip de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class AiSupportKeyboards:
    """Teclados específicos para el asistente IA Sip."""

    @staticmethod
    def ai_support_active() -> InlineKeyboardMarkup:
        """Opciones cuando hay una conversación IA activa."""
        keyboard = [
            [
                InlineKeyboardButton("💡 Preguntas Frecuentes", callback_data="ai_sip_suggestions")
            ],
            [
                InlineKeyboardButton("🔴 Finalizar Chat", callback_data="ai_sip_end")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
