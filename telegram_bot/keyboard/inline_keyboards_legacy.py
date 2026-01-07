"""
Teclados inline estandarizados para el bot uSipipo - LEGACY

NOTICE: Este archivo mantiene retrocompatibilidad. Para nuevo desarrollo,
usar los módulos organizados por features:
- user_keyboards: UserKeyboards
- admin_keyboards: AdminKeyboards
- operations_keyboards: OperationKeyboards, SupportKeyboards, TaskKeyboards
- common_keyboards: CommonKeyboards

Author: uSipipo Team
Version: 2.0.0 - Refactored keyboard structure with backward compatibility
"""

from telegram import InlineKeyboardMarkup
from typing import List, Dict, Any, Optional
from config import settings

# Import the new modular keyboard classes
from .user_keyboards import UserKeyboards
from .admin_keyboards import AdminKeyboards
from .operations_keyboards import OperationKeyboards, SupportKeyboards, TaskKeyboards
from .common_keyboards import CommonKeyboards


def get_main_menu_for_user(user_id: int) -> InlineKeyboardMarkup:
    """Helper function para obtener el menú principal correcto según el usuario."""
    is_admin = user_id == int(settings.ADMIN_ID)
    return InlineKeyboards.main_menu(is_admin=is_admin)


class InlineKeyboards:
    """
    Clase centralizada para todos los teclados inline del bot.
    
    DEPRECATED: Esta clase mantiene retrocompatibilidad delegando a los
    módulos organizados por features. Para nuevo código, usar directamente:
    - UserKeyboards, AdminKeyboards, OperationKeyboards, etc.
    """
    
    # ============================================
    # MAIN MENUS - Delegates to UserKeyboards
    # ============================================
    
    @staticmethod
    def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
        """Menú principal inline - delegado a UserKeyboards."""
        return UserKeyboards.main_menu(is_admin=is_admin)
    
    @staticmethod
    def admin_main_menu() -> InlineKeyboardMarkup:
        """Menú principal admin (DEPRECATED) - usar main_menu(is_admin=True)."""
        return UserKeyboards.main_menu(is_admin=True)
    
    # ============================================
    # VPN & KEYS - Delegates to UserKeyboards
    # ============================================
    
    @staticmethod
    def vpn_types() -> InlineKeyboardMarkup:
        """Selección de protocolo VPN."""
        return UserKeyboards.vpn_types()
    
    @staticmethod
    def key_management(key_id: str) -> InlineKeyboardMarkup:
        """Gestión de llave específica."""
        return UserKeyboards.key_management(key_id)
    
    @staticmethod
    def confirm_delete(key_id: str) -> InlineKeyboardMarkup:
        """Confirmación de eliminación."""
        return UserKeyboards.confirm_delete(key_id)
    
    # ============================================
    # OPERATIONS - Delegates to OperationKeyboards
    # ============================================
    
    @staticmethod
    def operations_menu(user=None) -> InlineKeyboardMarkup:
        """Menú principal de operaciones."""
        return OperationKeyboards.operations_menu(user)
    
    @staticmethod
    def vip_plans() -> InlineKeyboardMarkup:
        """Planes VIP disponibles."""
        return OperationKeyboards.vip_plans()
    
    @staticmethod
    def vip_payment_options(telegram_id: int, months: int, cost: int) -> InlineKeyboardMarkup:
        """Teclado con opciones de pago para planes VIP."""
        return OperationKeyboards.vip_payment_options(telegram_id, months, cost)
    
    # ============================================
    # REFERRALS - Delegates to OperationKeyboards
    # ============================================
    
    @staticmethod
    def referral_actions() -> InlineKeyboardMarkup:
        """Acciones del programa de referidos."""
        return OperationKeyboards.referral_actions()
    
    # ============================================
    # ACHIEVEMENTS - Delegates to OperationKeyboards
    # ============================================
    
    @staticmethod
    def achievements_menu() -> InlineKeyboardMarkup:
        """Menú principal de logros."""
        return OperationKeyboards.achievements_menu()
    
    @staticmethod
    def achievements_categories() -> InlineKeyboardMarkup:
        """Categorías de logros."""
        return OperationKeyboards.achievements_categories()
    
    @staticmethod
    def achievement_detail(achievement_id: str) -> InlineKeyboardMarkup:
        """Detalles y acciones de un logro."""
        return OperationKeyboards.achievement_detail(achievement_id)
    
    @staticmethod
    def achievements_leaderboard() -> InlineKeyboardMarkup:
        """Opciones de ranking."""
        return OperationKeyboards.achievements_leaderboard()
    
    @staticmethod
    def pending_rewards(rewards: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """Recompensas pendientes por reclamar."""
        return OperationKeyboards.pending_rewards(rewards)
    
    # ============================================
    # GAMES - Delegates to OperationKeyboards
    # ============================================
    
    @staticmethod
    def games_menu() -> InlineKeyboardMarkup:
        """Menú principal de juegos."""
        return OperationKeyboards.games_menu()
    
    # ============================================
    # SUPPORT - Delegates to SupportKeyboards
    # ============================================
    
    @staticmethod
    def support_menu() -> InlineKeyboardMarkup:
        """Menú de soporte técnico."""
        return SupportKeyboards.support_menu()
    
    @staticmethod
    def support_active() -> InlineKeyboardMarkup:
        """Opciones cuando hay un ticket activo."""
        return SupportKeyboards.support_active()
    
    # ============================================
    # HELP - Delegates to SupportKeyboards
    # ============================================
    
    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """Menú principal de ayuda."""
        return SupportKeyboards.help_menu()
    
    # ============================================
    # TASKS - Delegates to TaskKeyboards
    # ============================================
    
    @staticmethod
    def task_center_menu() -> InlineKeyboardMarkup:
        """Menú principal del centro de tareas."""
        return TaskKeyboards.task_center_menu()
    
    @staticmethod
    def task_list_keyboard(tasks: List[Dict], prefix: str = "task") -> InlineKeyboardMarkup:
        """Teclado para listar tareas."""
        return TaskKeyboards.task_list_keyboard(tasks, prefix)
    
    @staticmethod
    def task_detail_keyboard(task_id: str, is_completed: bool = False, reward_claimed: bool = False) -> InlineKeyboardMarkup:
        """Teclado para detalles de una tarea."""
        return TaskKeyboards.task_detail_keyboard(task_id, is_completed, reward_claimed)
    
    @staticmethod
    def admin_task_menu() -> InlineKeyboardMarkup:
        """Menú de administración de tareas."""
        return TaskKeyboards.admin_task_menu()
    
    @staticmethod
    def admin_task_list_keyboard(tasks: List[Dict]) -> InlineKeyboardMarkup:
        """Teclado para listar tareas (admin)."""
        return TaskKeyboards.admin_task_list_keyboard(tasks)
    
    @staticmethod
    def admin_task_detail_keyboard(task_id: str) -> InlineKeyboardMarkup:
        """Teclado para detalles de tarea (admin)."""
        return TaskKeyboards.admin_task_detail_keyboard(task_id)
    
    # ============================================
    # COMMON - Delegates to CommonKeyboards
    # ============================================
    
    @staticmethod
    def back_button(target: str = "main_menu") -> InlineKeyboardMarkup:
        """Botón de volver genérico."""
        return CommonKeyboards.back_button(target)
    
    @staticmethod
    def confirm_action(action: str, item_id: str = "") -> InlineKeyboardMarkup:
        """Confirmación genérica de acciones."""
        return CommonKeyboards.generic_confirmation(action, item_id)


class InlineAdminKeyboards:
    """
    Teclados inline específicos para administración.
    
    DEPRECATED: Esta clase mantiene retrocompatibilidad delegando a
    AdminKeyboards. Para nuevo código, usar AdminKeyboards directamente.
    """
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Menú principal de administración."""
        return AdminKeyboards.main_menu()
    
    @staticmethod
    def users_actions() -> InlineKeyboardMarkup:
        """Acciones sobre usuarios."""
        return AdminKeyboards.users_actions()
    
    @staticmethod
    def key_actions(key_id: str) -> InlineKeyboardMarkup:
        """Acciones para una clave específica."""
        return AdminKeyboards.key_actions(key_id)
    
    @staticmethod
    def confirm_delete(key_id: str) -> InlineKeyboardMarkup:
        """Confirmación de eliminación admin."""
        return AdminKeyboards.confirm_delete_key(key_id)
    
    @staticmethod
    def users_submenu() -> InlineKeyboardMarkup:
        """Submenu principal de gestión de usuarios."""
        return AdminKeyboards.users_submenu()
    
    @staticmethod
    def users_list_pagination(page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
        """Teclado para paginación de lista de usuarios."""
        return AdminKeyboards.users_list_pagination(page, total_pages)
    
    @staticmethod
    def user_detail_actions(user_id: int) -> InlineKeyboardMarkup:
        """Acciones sobre un usuario específico."""
        return AdminKeyboards.user_detail_actions(user_id)
    
    @staticmethod
    def role_selection() -> InlineKeyboardMarkup:
        """Selección de roles disponibles."""
        return AdminKeyboards.role_selection()
    
    @staticmethod
    def status_selection() -> InlineKeyboardMarkup:
        """Selección de estados disponibles."""
        return AdminKeyboards.status_selection()
    
    @staticmethod
    def confirm_action(action_type: str, user_id: int, extra_data: str = "") -> InlineKeyboardMarkup:
        """Confirmación genérica de acciones."""
        return AdminKeyboards.confirm_user_action(action_type, user_id, extra_data)
    
    @staticmethod
    def premium_role_duration() -> InlineKeyboardMarkup:
        """Selección de duración para roles premium."""
        return AdminKeyboards.premium_role_duration()
