from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

class Keyboards:
    @staticmethod
    def main_menu():
        """Menú persistente de botones de texto en la parte inferior."""
        keyboard = [
            ["🛡️ Mis Llaves", "➕ Crear Nueva"],
            ["📊 Estado", "⚙️ Ayuda"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def vpn_types():
        """Botones inline para elegir el protocolo de conexión."""
        keyboard = [
            [
                InlineKeyboardButton("Outline (SS)", callback_data="type_outline"),
                InlineKeyboardButton("WireGuard", callback_data="type_wireguard")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def key_management(key_id: str):
        """Botón inline para gestionar o eliminar una llave específica."""
        keyboard = [
            [
                InlineKeyboardButton("🗑️ Eliminar Llave", callback_data=f"delete_confirm_{key_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirm_delete(key_id: str):
        """Botones de confirmación de seguridad para evitar borrados accidentales."""
        keyboard = [
            [
                InlineKeyboardButton("✅ Sí, eliminar", callback_data=f"delete_execute_{key_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_delete")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def support_menu():
        """Botón para cerrar el ticket activo."""
        keyboard = [["🔴 Finalizar Soporte"]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def help_back():
        """Botón opcional para volver al menú principal desde la ayuda."""
        keyboard = [[InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")]]
        return InlineKeyboardMarkup(keyboard)
