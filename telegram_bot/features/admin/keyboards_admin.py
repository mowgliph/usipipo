"""
Teclados para panel administrativo de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class AdminKeyboards:
    """Teclados para panel administrativo."""

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú principal administrativo.
        
        Returns:
            InlineKeyboardMarkup: Teclado del menú admin
        """
        keyboard = [
            [
                InlineKeyboardButton("👥 Usuarios", callback_data="show_users"),
                InlineKeyboardButton("🔑 Llaves VPN", callback_data="show_keys")
            ],
            [
                InlineKeyboardButton("📊 Estado Servidor", callback_data="server_status"),
                InlineKeyboardButton("📋 Ver Logs", callback_data="logs")
            ],
            [
                InlineKeyboardButton("⚙️ Configuración", callback_data="settings"),
                InlineKeyboardButton("🔧 Mantenimiento", callback_data="maintenance")
            ],
            [
                InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu"),
                InlineKeyboardButton("🚪 Salir Admin", callback_data="end_admin")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """
        Teclado para volver al menú admin.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver al Menú Admin", callback_data="admin")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_user_menu() -> InlineKeyboardMarkup:
        """
        Teclado para volver al menú de usuario.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno a usuario
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def user_actions(user_id: int, is_active: bool, is_vip: bool) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para un usuario específico.
        
        Args:
            user_id: ID del usuario
            is_active: Si el usuario está activo
            is_vip: Si el usuario es VIP
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = []
        
        # Acciones básicas
        keyboard.append([
            InlineKeyboardButton("📊 Ver Detalles", callback_data=f"user_details_{user_id}")
        ])
        
        # Acciones de estado
        if is_active:
            keyboard.append([
                InlineKeyboardButton("⏸️ Suspender", callback_data=f"user_suspend_{user_id}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("✅ Reactivar", callback_data=f"user_reactivate_{user_id}")
            ])
        
        # Acciones VIP
        if not is_vip:
            keyboard.append([
                InlineKeyboardButton("👑 Dar VIP", callback_data=f"user_grant_vip_{user_id}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("🚫 Quitar VIP", callback_data=f"user_revoke_vip_{user_id}")
            ])
        
        # Acciones peligrosas
        keyboard.append([
            InlineKeyboardButton("🗑️ Eliminar Usuario", callback_data=f"user_delete_{user_id}")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="show_users")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def key_actions(key_id: int, is_active: bool) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para una llave específica.
        
        Args:
            key_id: ID de la llave
            is_active: Si la llave está activa
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = []
        
        keyboard.append([
            InlineKeyboardButton("📊 Ver Detalles", callback_data=f"key_details_{key_id}")
        ])
        
        if is_active:
            keyboard.append([
                InlineKeyboardButton("⏸️ Suspender", callback_data=f"key_suspend_{key_id}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("✅ Reactivar", callback_data=f"key_reactivate_{key_id}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🗑️ Eliminar Llave", callback_data=f"key_delete_{key_id}")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="show_keys")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirmation(action: str, target_id: int) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para acciones peligrosas.
        
        Args:
            action: Tipo de acción
            target_id: ID del objetivo
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{action}_{target_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_{action}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú de configuración.
        
        Returns:
            InlineKeyboardMarkup: Teclado de configuración
        """
        keyboard = [
            [
                InlineKeyboardButton("🌐 Servidores", callback_data="settings_servers"),
                InlineKeyboardButton("📊 Límites", callback_data="settings_limits")
            ],
            [
                InlineKeyboardButton("🔐 Seguridad", callback_data="settings_security"),
                InlineKeyboardButton("📧 Notificaciones", callback_data="settings_notifications")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def maintenance_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú de mantenimiento.
        
        Returns:
            InlineKeyboardMarkup: Teclado de mantenimiento
        """
        keyboard = [
            [
                InlineKeyboardButton("🔄 Reiniciar Servicios", callback_data="restart_services"),
                InlineKeyboardButton("🧹 Limpiar Caché", callback_data="clear_cache")
            ],
            [
                InlineKeyboardButton("📦 Crear Backup", callback_data="create_backup"),
                InlineKeyboardButton("🔧 Modo Mantenimiento", callback_data="maintenance_mode")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
