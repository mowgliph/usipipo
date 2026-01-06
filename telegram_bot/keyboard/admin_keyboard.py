"""
Teclados de administración para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

class AdminKeyboard:
    """Teclados del sistema de administración."""
    
    @staticmethod
    def main_menu():
        """Menú principal de administración."""
        keyboard = [
            [
                InlineKeyboardButton("👥 Ver Usuarios", callback_data="show_users"),
                InlineKeyboardButton("🔐 Ver Claves", callback_data="show_keys")
            ],
            [
                InlineKeyboardButton("🖥️ Estado Servidores", callback_data="server_status"),
                InlineKeyboardButton("📊 Estadísticas", callback_data="stats")
            ],
            [
                InlineKeyboardButton("✅ Gestionar Tareas", callback_data="admin_task_menu")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def users_actions():
        """Acciones disponibles en la vista de usuarios."""
        keyboard = [
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data="show_users"),
                InlineKeyboardButton("📊 Estadísticas", callback_data="stats")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_delete(key_id: str):
        """Teclado de confirmación de eliminación."""
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar Eliminación", callback_data=f"confirm_delete_{key_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_delete")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_menu():
        """Botón para volver al menú principal."""
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver al Menú", callback_data="admin")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def key_actions(key_id: str):
        """Acciones para una clave específica."""
        keyboard = [
            [
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data=f"stats_{key_id}"),
                InlineKeyboardButton("👤 Ver Usuario", callback_data=f"user_{key_id}")
            ],
            [
                InlineKeyboardButton("🗑️ Eliminar Clave", callback_data=f"delete_key_{key_id}"),
                InlineKeyboardButton("🔄 Renovar", callback_data=f"renew_{key_id}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="show_keys")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
