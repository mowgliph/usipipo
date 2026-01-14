"""
Teclados para gestión de usuarios de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class UserManagementKeyboards:
    """Teclados para gestión de usuarios."""

    @staticmethod
    def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
        """
        Genera el menú principal según el tipo de usuario.
        
        Args:
            is_admin: Si es True, incluye opciones de administrador
            
        Returns:
            InlineKeyboardMarkup: Teclado del menú principal
        """
        keyboard = [
            [
                InlineKeyboardButton("🛡️ Mis Llaves", callback_data="key_management"),
                InlineKeyboardButton("📊 Estado", callback_data="status")
            ],
            [
                InlineKeyboardButton("💰 Operaciones", callback_data="operations"),
                InlineKeyboardButton("🏆 Logros", callback_data="achievements")
            ],
            [
                InlineKeyboardButton("⚙️ Ayuda", callback_data="help")
            ]
        ]
        
        # Agregar opciones de administrador si corresponde
        if is_admin:
            keyboard.insert(0, [
                InlineKeyboardButton("🔧 Panel Admin", callback_data="admin")
            ])
        
        return InlineKeyboardMarkup(keyboard)
