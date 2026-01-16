"""
Handlers para sistema de juegos de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler, CommandHandler, ConversationHandler
from domain.entities.game import GameType, GameResult
from .messages_game import GameMessages
from .keyboards_game import GameKeyboards
from utils.logger import get_logger

# Estados de conversación
SELECTING_GAME = 1
PLAYING_GAME = 2
GAME_RESULT = 3


class GameHandler:
    """Handler del sistema de juegos."""
    
    def __init__(self, game_service):
        """
        Inicializa el handler de juegos.
        
        Args:
            game_service: Servicio de juegos
        """
        self.game_service = game_service
        self.bot_logger = get_logger()
        self.bot_logger.info("🎮 GameHandler inicializado")

    async def show_game_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el menú principal de juegos.
        """
        try:
            message = GameMessages.Menu.MAIN
            keyboard = GameKeyboards.main_menu()
            
            await update.message.reply_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return SELECTING_GAME
            
        except Exception as e:
            self.bot_logger.error(f"Error en show_game_menu: {e}")
            await update.message.reply_text(
                text=GameMessages.Error.SYSTEM_ERROR,
                reply_markup=GameKeyboards.back_to_operations(),
                parse_mode="Markdown"
            )
            return ConversationHandler.END

    async def show_spin_wheel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra la ruleta de la suerte.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = GameMessages.SpinWheel.DESCRIPTION
            keyboard = GameKeyboards.spin_wheel()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return PLAYING_GAME
            
        except Exception as e:
            self.bot_logger.error(f"Error en show_spin_wheel: {e}")
            await query.edit_message_text(
                text=GameMessages.Error.SYSTEM_ERROR,
                reply_markup=GameKeyboards.back_to_game(),
                parse_mode="Markdown"
            )
            return SELECTING_GAME

    async def play_spin_wheel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Juega a la ruleta de la suerte.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Verificar si el usuario tiene giros disponibles
            spins_left = await self.game_service.get_user_spins(user_id, current_user_id=user_id)
            
            if spins_left <= 0:
                message = GameMessages.SpinWheel.NO_SPINS
                keyboard = GameKeyboards.buy_spins()
            else:
                # Simular el juego de la ruleta
                result = await self._play_spin_game(user_id)
                
                message = GameMessages.SpinWheel.RESULT.format(
                    prize=result['prize'],
                    winnings=result['winnings'],
                    new_balance=result['new_balance'],
                    spins_left=result['spins_left']
                )
                keyboard = GameKeyboards.spin_result(result['prize'])
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return GAME_RESULT
            
        except Exception as e:
            self.bot_logger.error(f"Error en play_spin_wheel: {e}")
            await query.edit_message_text(
                text=GameMessages.Error.SYSTEM_ERROR,
                reply_markup=GameKeyboards.back_to_game(),
                parse_mode="Markdown"
            )
            return PLAYING_GAME

    async def show_trivia(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el juego de trivia.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = GameMessages.Trivia.DESCRIPTION
            keyboard = GameKeyboards.trivia_categories()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return PLAYING_GAME
            
        except Exception as e:
            self.bot_logger.error(f"Error en show_trivia: {e}")
            await query.edit_message_text(
                text=GameMessages.Error.SYSTEM_ERROR,
                reply_markup=GameKeyboards.back_to_game(),
                parse_mode="Markdown"
            )
            return SELECTING_GAME

    async def play_trivia(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Juega a la trivia.
        """
        query = update.callback_query
        await query.answer()
        
        category = query.data.replace("trivia_", "")
        user_id = update.effective_user.id
        
        try:
            # Obtener pregunta de trivia
            question = await self.game_service.get_trivia_question(category, current_user_id=user_id)
            
            if not question:
                message = GameMessages.Trivia.NO_QUESTIONS
                keyboard = GameKeyboards.back_to_game()
            else:
                message = GameMessages.Trivia.QUESTION.format(
                    category=category.title(),
                    question=question['question'],
                    options='\n'.join([f"{i}. {opt}" for i, opt in enumerate(question['options'], 1)])
                )
                keyboard = GameKeyboards.trivia_answers(question['correct_answer'])
                
                # Guardar respuesta correcta en contexto
                context.user_data['trivia_answer'] = question['correct_answer']
                context.user_data['trivia_category'] = category
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return PLAYING_GAME
            
        except Exception as e:
            self.bot_logger.error(f"Error en play_trivia: {e}")
            await query.edit_message_text(
                text=GameMessages.Error.SYSTEM_ERROR,
                reply_markup=GameKeyboards.back_to_game(),
                parse_mode="Markdown"
            )
            return SELECTING_GAME

    async def check_trivia_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Verifica la respuesta de la trivia.
        """
        query = update.callback_query
        await query.answer()
        
        user_answer = int(query.data.split("_")[-1])
        correct_answer = context.user_data.get('trivia_answer')
        category = context.user_data.get('trivia_category')
        user_id = update.effective_user.id
        
        try:
            if user_answer == correct_answer:
                # Respuesta correcta
                winnings = 10  # Estrellas por respuesta correcta
                await self.game_service.add_user_earnings(user_id, winnings, current_user_id=user_id)
                
                message = GameMessages.Trivia.CORRECT.format(
                    category=category.title(),
                    winnings=winnings
                )
                keyboard = GameKeyboards.trivia_success()
            else:
                # Respuesta incorrecta
                message = GameMessages.Trivia.INCORRECT.format(
                    category=category.title(),
                    correct_answer=correct_answer
                )
                keyboard = GameKeyboards.trivia_retry()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return GAME_RESULT
            
        except Exception as e:
            self.bot_logger.error(f"Error en check_trivia_answer: {e}")
            await query.edit_message_text(
                text=GameMessages.Error.SYSTEM_ERROR,
                reply_markup=GameKeyboards.back_to_game(),
                parse_mode="Markdown"
            )
            return PLAYING_GAME

    async def show_daily_challenges(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra los desafíos diarios.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Obtener desafíos diarios del usuario
            challenges = await self.game_service.get_user_daily_challenges(user_id, current_user_id=user_id)
            
            if not challenges:
                message = GameMessages.Challenges.NO_CHALLENGES
                keyboard = GameKeyboards.back_to_game()
            else:
                message = GameMessages.Challenges.LIST_HEADER
                
                for challenge in challenges:
                    status = "✅" if challenge.completed else "⏳"
                    progress = f"({challenge.progress}/{challenge.goal})"
                    message += f"\n{status} {challenge.name} {progress}"
                    message += f"\n   🎁 Recompensa: {challenge.reward} estrellas"
                
                keyboard = GameKeyboards.challenges_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            self.bot_logger.error(f"Error en show_daily_challenges: {e}")
            await query.edit_message_text(
                text=GameMessages.Error.SYSTEM_ERROR,
                reply_markup=GameKeyboards.back_to_game(),
                parse_mode="Markdown"
            )

    async def show_game_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra las estadísticas de juegos.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Obtener estadísticas del usuario
            stats = await self.game_service.get_user_game_stats(user_id, current_user_id=user_id)
            
            message = GameMessages.Stats.USER_STATS.format(
                total_games=stats.get('total_games', 0),
                total_winnings=stats.get('total_winnings', 0),
                total_earnings=stats.get('total_earnings', 0),
                favorite_game=stats.get('favorite_game', 'N/A'),
                win_rate=stats.get('win_rate', 0),
                current_streak=stats.get('current_streak', 0)
            )
            
            keyboard = GameKeyboards.stats_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            self.bot_logger.error(f"Error en show_game_stats: {e}")
            await query.edit_message_text(
                text=GameMessages.Error.SYSTEM_ERROR,
                reply_markup=GameKeyboards.back_to_game(),
                parse_mode="Markdown"
            )

    async def show_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el leaderboard de juegos.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Obtener leaderboard
            leaderboard = await self.game_service.get_game_leaderboard(limit=10, current_user_id=user_id)
            user_rank = await self.game_service.get_user_game_rank(user_id, current_user_id=user_id)
            
            message = GameMessages.Leaderboard.MAIN.format(
                user_rank=user_rank
            )
            
            for i, player in enumerate(leaderboard, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                message += f"\n{medal} 👤 {player.username or 'Usuario ' + str(player.user_id)}\n"
                message += f"   🎮 Juegos: {player.games_played}\n"
                message += f"   💰 Ganancias: ${player.earnings:.2f}\n"
                message += f"   🏆 Tasa de Victoria: {player.win_rate:.1f}%\n"
            
            keyboard = GameKeyboards.leaderboard_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            self.bot_logger.error(f"Error en show_leaderboard: {e}")
            await query.edit_message_text(
                text=GameMessages.Error.SYSTEM_ERROR,
                reply_markup=GameKeyboards.back_to_game(),
                parse_mode="Markdown"
            )

    # Métodos privados
    async def _play_spin_game(self, user_id: int) -> dict:
        """Simula el juego de la ruleta."""
        try:
            # Verificar giros disponibles
            spins_left = await self.game_service.get_user_spins(user_id, current_user_id=user_id)
            
            if spins_left <= 0:
                return {'error': 'No spins left'}
            
            # Simular resultado de la ruleta
            prizes = [
                {'name': '⭐ 5 Estrellas', 'winnings': 5, 'probability': 0.3},
                {'name': '⭐ 10 Estrellas', 'winnings': 10, 'probability': 0.2},
                {'name': '⭐ 25 Estrellas', 'winnings': 25, 'probability': 0.1},
                {'name': '⭐ 50 Estrellas', 'winnings': 50, 'probability': 0.05},
                {'name': '⭐ 100 Estrellas', 'winnings': 100, 'probability': 0.02},
                {'name': '💎 Giro Extra', 'winnings': 0, 'probability': 0.03},
                {'name': '😊 Suerte', 'winnings': 1, 'probability': 0.3}
            ]
            
            # Seleccionar premio basado en probabilidad
            import random
            prize = random.choices(prizes, weights=[p['probability'] for p in prizes])[0]
            
            # Actualizar giros y ganancias
            await self.game_service.use_spin(user_id, current_user_id=user_id)
            await self.game_service.add_user_earnings(user_id, prize['winnings'], current_user_id=user_id)
            
            # Obtener estadísticas actualizadas
            new_balance = await self.game_service.get_user_balance(user_id, current_user_id=user_id)
            new_spins_left = await self.game_service.get_user_spins(user_id, current_user_id=user_id)
            
            return {
                'prize': prize['name'],
                'winnings': prize['winnings'],
                'new_balance': new_balance,
                'spins_left': new_spins_left
            }
            
        except Exception as e:
            self.bot_logger.error(f"Error en _play_spin_game: {e}")
            return {'error': str(e)}


def get_game_handlers(game_service):
    """
    Retorna los handlers de juegos.
    
    Args:
        game_service: Servicio de juegos
        
    Returns:
        list: Lista de handlers
    """
    handler = GameHandler(game_service)
    
    return [
        MessageHandler(filters.Regex("^🎮 Juega y Gana$"), handler.show_game_menu),
        CommandHandler("game", handler.show_game_menu),
    ]


def get_game_callback_handlers(game_service):
    """
    Retorna los handlers de callbacks de juegos.
    
    Args:
        game_service: Servicio de juegos
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = GameHandler(game_service)
    
    return [
        CallbackQueryHandler(handler.show_spin_wheel, pattern="^spin_wheel$"),
        CallbackQueryHandler(handler.play_spin_wheel, pattern="^play_spin_wheel$"),
        CallbackQueryHandler(handler.show_trivia, pattern="^trivia_"),
        CallbackQueryHandler(handler.play_trivia, pattern="^trivia_answer_"),
        CallbackQueryHandler(handler.show_daily_challenges, pattern="^daily_challenges$"),
        CallbackQueryHandler(handler.show_game_stats, pattern="^game_stats$"),
        CallbackQueryHandler(handler.show_leaderboard, pattern="^game_leaderboard$"),
    ]


def get_game_conversation_handler(game_service) -> ConversationHandler:
    """
    Retorna el ConversationHandler para juegos.
    
    Args:
        game_service: Servicio de juegos
        
    Returns:
        ConversationHandler: Handler configurado
    """
    handler = GameHandler(game_service)
    
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🎮 Juega y Gana$"), handler.show_game_menu),
            CommandHandler("game", handler.show_game_menu),
        ],
        states={
            SELECTING_GAME: [
                CallbackQueryHandler(handler.show_spin_wheel, pattern="^spin_wheel$"),
                CallbackQueryHandler(handler.show_trivia, pattern="^trivia_"),
                CallbackQueryHandler(handler.show_daily_challenges, pattern="^daily_challenges$"),
                CallbackQueryHandler(handler.show_game_stats, pattern="^game_stats$"),
                CallbackQueryHandler(handler.show_leaderboard, pattern="^game_leaderboard$"),
                CallbackQueryHandler(handler.back_to_operations, pattern="^back_to_operations$"),
            ],
            PLAYING_GAME: [
                CallbackQueryHandler(handler.play_spin_wheel, pattern="^play_spin_wheel$"),
                CallbackQueryHandler(handler.play_trivia, pattern="^trivia_answer_"),
                CallbackQueryHandler(handler.back_to_game, pattern="^back_to_game$"),
            ],
            GAME_RESULT: [
                CallbackQueryHandler(handler.show_game_menu, pattern="^play_again$"),
                CallbackQueryHandler(handler.back_to_game, pattern="^back_to_game$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handler.show_game_menu),
            CallbackQueryHandler(handler.back_to_game, pattern="^back_to_game$"),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )
