"""
Teclados para gestión de llaves VPN de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class VpnKeysKeyboards:
    """Teclados para gestión de llaves VPN."""

    @staticmethod
    def vpn_types() -> InlineKeyboardMarkup:
        """
        Teclado para seleccionar tipo de VPN.
        
        Returns:
            InlineKeyboardMarkup: Teclado de tipos VPN
        """
        keyboard = [
            [
                InlineKeyboardButton("🌐 Outline", callback_data="type_outline"),
                InlineKeyboardButton("🔒 WireGuard", callback_data="type_wireguard")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def cancel_creation() -> InlineKeyboardMarkup:
        """
        Teclado con botón de cancelar creación.
        
        Returns:
            InlineKeyboardMarkup: Teclado de cancelación
        """
        keyboard = [
            [
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_create_key")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def key_actions(is_admin: bool = False) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para una llave específica.
        
        Args:
            is_admin: Si es True, incluye opciones adicionales
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="key_stats_{key_id}"),
                InlineKeyboardButton("📋 Configuración", callback_data="key_config_{key_id}")
            ],
            [
                InlineKeyboardButton("✏️ Renombrar", callback_data="key_rename_{key_id}"),
                InlineKeyboardButton("🗑️ Eliminar", callback_data="key_delete_{key_id}")
            ]
        ]
        
        if is_admin:
            keyboard.append([
                InlineKeyboardButton("🔧 Admin Options", callback_data="key_admin_{key_id}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="back_to_keys")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
        """
        Teclado del menú principal contextual.
        
        Args:
            is_admin: Si es True, incluye opciones de administrador
            
        Returns:
            InlineKeyboardMarkup: Teclado del menú principal
        """
        keyboard = [
            [
                InlineKeyboardButton("🛡️ Mis Llaves", callback_data="operations"),
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

    @staticmethod
    def key_list(keys: list, is_admin: bool = False) -> InlineKeyboardMarkup:
        """
        Genera teclado dinámico para lista de llaves.
        
        Args:
            keys: Lista de llaves VPN
            is_admin: Si es True, incluye opciones adicionales
            
        Returns:
            InlineKeyboardMarkup: Teclado de lista de llaves
        """
        keyboard = []
        
        for key in keys:
            # Botón principal de la llave
            button_text = f"🔑 {key.name} ({key.type.upper()})"
            callback_data = f"key_details_{key.id}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        # Opciones adicionales
        keyboard.append([
            InlineKeyboardButton("➕ Crear Nueva", callback_data="create_key")
        ])
        
        if is_admin:
            keyboard.append([
                InlineKeyboardButton("🔧 Admin Keys", callback_data="admin_keys")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
