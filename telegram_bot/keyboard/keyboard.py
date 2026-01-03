from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

class Keyboards:
    @staticmethod
    def main_menu():
        """Menú persistente de botones de texto en la parte inferior."""
        keyboard = [
            ["🛡️ Mis Llaves", "➕ Crear Nueva"],
            ["📊 Estado", "💰 Operaciones"],
            ["⚙️ Ayuda"]
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
        """Botón opcional para?? Volver al menú principal desde la ayuda."""
        keyboard = [[InlineKeyboardButton("🔙?? Volver al Menú", callback_data="main_menu")]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def operations_menu():
        """Genera el teclado del menú de operaciones."""
        return ReplyKeyboardMarkup(
            [
                ["� Mi Balance", "👑 Plan VIP"],
                ["🎮 Juga y Gana", "👥 Referidos"],
                ["⚙️ Ayuda"]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

    @staticmethod
    def vip_plans():
        """Opciones de compra de VIP."""
        keyboard = [
            [
                InlineKeyboardButton("1 Mes - 10 Estrellas", callback_data="vip_1_month"),
                InlineKeyboardButton("3 Meses - 27 Estrellas", callback_data="vip_3_months")
            ],
            [
                InlineKeyboardButton("6 Meses - 50 Estrellas", callback_data="vip_6_months"),
                InlineKeyboardButton("12 Meses - 90 Estrellas", callback_data="vip_12_months")
            ],
            [
                InlineKeyboardButton("🔙?? Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def referral_actions():
        """Acciones para el programa de referidos."""
        keyboard = [
            [
                InlineKeyboardButton("📋 Mi Código de Referido", callback_data="my_referral_code"),
                InlineKeyboardButton("👥 Mis Referidos", callback_data="my_referrals")
            ],
            [
                InlineKeyboardButton("💰 Mis Ganancias", callback_data="referral_earnings"),
                InlineKeyboardButton("🔗 Compartir Enlace", callback_data="share_referral")
            ],
            [
                InlineKeyboardButton("📋 Aplicar Código", callback_data="apply_referral_code")
            ],
            [
                InlineKeyboardButton("�?? Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
