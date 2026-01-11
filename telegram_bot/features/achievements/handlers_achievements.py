"""
Handlers para sistema de logros de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from application.services.achievement_service import AchievementService
from .messages_achievements import AchievementsMessages
from .keyboards_achievements import AchievementsKeyboards
from utils.logger import logger
from utils.spinner import database_spinner
from common.base_handler import BaseHandler
from common.decorators import safe_callback_query, database_operation
from common.patterns import ListPattern


class AchievementsHandler(BaseHandler, ListPattern):
    """Handler para sistema de logros."""
    
    def __init__(self, achievement_service: AchievementService):
        """
        Inicializa el handler de logros.
        
        Args:
            achievement_service: Servicio de logros
        """
        super().__init__(achievement_service, "AchievementService")

    @database_spinner
    @database_operation
    async def achievements_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el menú principal de logros."""
        user_id = update.effective_user.id
        
        # Obtener resumen del usuario
        summary = await self.service.get_user_summary(user_id)
        
        if not summary:
            # Inicializar logros si no existen
            await self.service.initialize_user_achievements(user_id)
            summary = await self.service.get_user_summary(user_id)
        
        # Formatear mensaje principal
        message = AchievementsMessages.Menu.MAIN.format(
            completed=summary.get('completed_achievements', 0),
            total=summary.get('total_achievements', 0),
            stars=summary.get('total_reward_stars', 0),
            pending=summary.get('pending_rewards', 0)
        )
        
        await self._reply_message(
            update,
            text=message,
            reply_markup=AchievementsKeyboards.achievements_menu(),
            parse_mode="Markdown"
        )

    @safe_callback_query
    @database_spinner
    @database_operation
    async def achievements_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el progreso general de logros."""
        user_id = update.effective_user.id
        
        summary = await self.service.get_user_summary(user_id)
        
        message = AchievementsMessages.Progress.OVERVIEW.format(
            completed=summary.get('completed_achievements', 0),
            total=summary.get('total_achievements', 0),
            percentage=int((summary.get('completed_achievements', 0) / max(summary.get('total_achievements', 1), 1)) * 100),
            stars=summary.get('total_reward_stars', 0),
            pending=summary.get('pending_rewards', 0)
        )
        
        await self._edit_message_with_keyboard(
            update, context,
            text=message,
            reply_markup=AchievementsKeyboards.back_to_menu(),
            parse_mode="Markdown"
        )

    @database_spinner
    async def achievements_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra la lista de logros disponibles."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            user_achievements = await self.achievement_service.get_user_achievements(user_id)
            
            if not user_achievements:
                message = AchievementsMessages.List.NO_ACHIEVEMENTS
            else:
                # Agrupar por categorías
                categories = {}
                for achievement in user_achievements:
                    category = achievement.category or "General"
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(achievement)
                
                message = AchievementsMessages.List.HEADER
                
                for category, achievements in categories.items():
                    message += f"\n📂 **{category}**\n"
                    for achievement in achievements:
                        status = "✅" if achievement.completed else "⏳"
                        message += f"{status} {achievement.title}\n"
            
            await query.edit_message_text(
                text=message,
                reply_markup=AchievementsKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en achievements_list: {e}")
            await query.edit_message_text(
                text=AchievementsMessages.Error.SYSTEM_ERROR,
                reply_markup=AchievementsKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )

    @database_spinner
    async def claim_reward(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reclama una recompensa de logro."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Extraer achievement_id del callback_data
            achievement_id = int(query.data.split("_")[-1])
            
            result = await self.achievement_service.claim_reward(user_id, achievement_id)
            
            if result:
                message = AchievementsMessages.Reward.CLAIMED.format(
                    title=result.get('title', 'Logro'),
                    stars=result.get('reward_stars', 0)
                )
            else:
                message = AchievementsMessages.Reward.ALREADY_CLAIMED
            
            await query.edit_message_text(
                text=message,
                reply_markup=AchievementsKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en claim_reward: {e}")
            await query.edit_message_text(
                text=AchievementsMessages.Error.SYSTEM_ERROR,
                reply_markup=AchievementsKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )

    @database_spinner
    async def achievements_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el leaderboard de logros."""
        query = update.callback_query
        await query.answer()
        
        try:
            leaderboard = await self.achievement_service.get_leaderboard(limit=10)
            
            if not leaderboard:
                message = AchievementsMessages.Leaderboard.NO_DATA
            else:
                message = AchievementsMessages.Leaderboard.HEADER
                
                for i, entry in enumerate(leaderboard, 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    message += f"\n{medal} **{entry['name']}** - {entry['total_achievements']} logros, {entry['total_stars']} ⭐"
            
            await query.edit_message_text(
                text=message,
                reply_markup=AchievementsKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en achievements_leaderboard: {e}")
            await query.edit_message_text(
                text=AchievementsMessages.Error.SYSTEM_ERROR,
                reply_markup=AchievementsKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )


def get_achievements_handlers(achievement_service: AchievementService):
    """
    Retorna los handlers de logros.
    
    Args:
        achievement_service: Servicio de logros
        
    Returns:
        list: Lista de handlers
    """
    handler = AchievementsHandler(achievement_service)
    
    return [
        MessageHandler(filters.Regex("^🏆 Logros$"), handler.achievements_menu),
        CommandHandler("achievements", handler.achievements_menu),
    ]


def get_achievements_callback_handlers(achievement_service: AchievementService):
    """
    Retorna los handlers de callbacks para logros.
    
    Args:
        achievement_service: Servicio de logros
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = AchievementsHandler(achievement_service)
    
    return [
        CallbackQueryHandler(handler.achievements_progress, pattern="^achievements_progress$"),
        CallbackQueryHandler(handler.achievements_list, pattern="^achievements_list$"),
        CallbackQueryHandler(handler.claim_reward, pattern="^claim_reward_"),
        CallbackQueryHandler(handler.achievements_leaderboard, pattern="^achievements_leaderboard$"),
    ]
