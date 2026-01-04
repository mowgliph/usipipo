from .inline_keyboards import InlineKeyboards
from telegram import ReplyKeyboardMarkup, KeyboardButton

class Keyboards:
    """Clase legacy - mantenida por compatibilidad. Usar InlineKeyboards para nuevo desarrollo."""
    
    # Métodos ReplyKeyboardMarkup eliminados - migrados a InlineKeyboards
    # main_menu() -> InlineKeyboards.main_menu()
    # admin_main_menu() -> InlineKeyboards.admin_main_menu()
    # operations_menu() -> InlineKeyboards.operations_menu()
    # support_menu() -> InlineKeyboards.support_active()
    # admin_menu() -> InlineAdminKeyboards.main_menu()

    @staticmethod
    def show_menu_button():
        """Botón de respaldo para mostrar el menú principal inline."""
        keyboard = [[KeyboardButton("📋 Mostrar Menú")]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    @staticmethod
    def vpn_types():
        """Botones inline para elegir el protocolo de conexión - LEGACY: Usar InlineKeyboards.vpn_types()"""
        return InlineKeyboards.vpn_types()

    @staticmethod
    def key_management(key_id: str):
        """Botón inline para gestionar o eliminar una llave específica - LEGACY: Usar InlineKeyboards.key_management()"""
        return InlineKeyboards.key_management(key_id)

    @staticmethod
    def confirm_delete(key_id: str):
        """Botones de confirmación de seguridad para evitar borrados accidentales - LEGACY: Usar InlineKeyboards.confirm_delete()"""
        return InlineKeyboards.confirm_delete(key_id)
    
    @staticmethod
    def vip_plans():
        """Opciones de compra de VIP - LEGACY: Usar InlineKeyboards.vip_plans()"""
        return InlineKeyboards.vip_plans()

    @staticmethod
    def referral_actions():
        """Acciones para el programa de referidos - LEGACY: Usar InlineKeyboards.referral_actions()"""
        return InlineKeyboards.referral_actions()

    @staticmethod
    def achievements_menu():
        """Menú principal de logros - LEGACY: Usar InlineKeyboards.achievements_menu()"""
        return InlineKeyboards.achievements_menu()

    @staticmethod
    def achievements_categories():
        """Categorías de logros - LEGACY: Usar InlineKeyboards.achievements_categories()"""
        return InlineKeyboards.achievements_categories()

    @staticmethod
    def achievement_detail(achievement_id: str):
        """Botones para detalles de un logro - LEGACY: Usar InlineKeyboards.achievement_detail()"""
        return InlineKeyboards.achievement_detail(achievement_id)

    @staticmethod
    def achievements_leaderboard():
        """Opciones de ranking - LEGACY: Usar InlineKeyboards.achievements_leaderboard()"""
        return InlineKeyboards.achievements_leaderboard()

    @staticmethod
    def pending_rewards(rewards: list):
        """Botones para recompensas pendientes - LEGACY: Usar InlineKeyboards.pending_rewards()"""
        return InlineKeyboards.pending_rewards(rewards)
