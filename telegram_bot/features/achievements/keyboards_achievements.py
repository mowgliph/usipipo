"""
Teclados para sistema de logros de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram_bot.common.keyboards import CommonKeyboards


class AchievementsKeyboards:
    """Teclados para sistema de logros."""

    @staticmethod
    def achievements_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú principal de logros.
        
        Returns:
            InlineKeyboardMarkup: Teclado del menú de logros
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Mi Progreso", callback_data="achievements_progress"),
                InlineKeyboardButton("📋 Mis Logros", callback_data="achievements_list")
            ],
            [
                InlineKeyboardButton("🎁 Recompensas", callback_data="achievements_rewards"),
                InlineKeyboardButton("🏆 Líderes", callback_data="achievements_leaderboard")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """
        Teclado para volver al menú de logros.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        return CommonKeyboards.back_to_previous_menu()

    @staticmethod
    def achievement_actions(achievement_id: int, is_completed: bool, reward_claimed: bool) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para un logro específico.
        
        Args:
            achievement_id: ID del logro
            is_completed: Si el logro está completado
            reward_claimed: Si la recompensa ya fue reclamada
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = []
        
        if is_completed and not reward_claimed:
            keyboard.append([
                InlineKeyboardButton("🎁 Reclamar Recompensa", callback_data=f"claim_reward_{achievement_id}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("📋 Ver Detalles", callback_data=f"achievement_details_{achievement_id}")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="achievements_list")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def reward_list(pending_rewards: list) -> InlineKeyboardMarkup:
        """
        Teclado para lista de recompensas pendientes.
        
        Args:
            pending_rewards: Lista de recompensas pendientes
            
        Returns:
            InlineKeyboardMarkup: Teclado de recompensas
        """
        keyboard = []
        
        for reward in pending_rewards:
            button_text = f"🎁 {reward['title']} (+{reward['stars']} ⭐)"
            callback_data = f"claim_reward_{reward['achievement_id']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        if not pending_rewards:
            keyboard.append([
                InlineKeyboardButton("📭 Sin recompensas pendientes", callback_data="no_action")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="achievements_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def category_filter(categories: list) -> InlineKeyboardMarkup:
        """
        Teclado para filtrar logros por categoría.
        
        Args:
            categories: Lista de categorías disponibles
            
        Returns:
            InlineKeyboardMarkup: Teclado de categorías
        """
        keyboard = []
        
        # Agregar opción "Todas"
        keyboard.append([
            InlineKeyboardButton("📋 Todas", callback_data="achievements_category_all")
        ])
        
        # Agregar categorías específicas
        for category in categories:
            button_text = f"📂 {category}"
            callback_data = f"achievements_category_{category.lower().replace(' ', '_')}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="achievements_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
