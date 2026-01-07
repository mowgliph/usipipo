"""
Handler del sistema de juegos Play and Earn para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler

from domain.entities.game import GameType, GameResult
from telegram_bot.messages.game_messages import GameMessages
from telegram_bot.keyboard import OperationKeyboards, CommonKeyboards
from utils.logger import get_logger

# Estados de conversación
SELECTING_GAME = 1
PLAYING_GAME = 2
GAME_RESULT = 3

class GameHandler:
    """Handler del sistema de juegos."""
    
    def __init__(self, game_service):
        self.game_service = game_service
        self.bot_logger = get_logger()
        
    async def show_game_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú principal de juegos."""
        user_id = update.effective_user.id
        
        # Obtener estadísticas del usuario
        balance = await self.game_service.get_user_balance(user_id)
        stats = await self.game_service.get_game_stats(user_id)
        
        # Determinar mensaje de estado
        can_play = await self.game_service.can_play_today(user_id)
        can_win = await self.game_service.can_win_this_week(user_id)
        
        if not can_play:
            status_message = "⏰ Ya jugaste hoy. Vuelve mañana."
        elif not can_win:
            status_message = "🏆 ¡Límite de victorias semanales alcanzado!"
        else:
            status_message = "✅ ¡Puedes jugar y ganar hoy!"
        
        # Crear mensaje de estado
        status_text = GameMessages.GAME_STATUS.format(
            stars=balance.stars_balance,
            games_today=1 if not can_play else 0,
            weekly_wins=len(stats.current_week_wins),
            last_game=stats.last_play_date.strftime("%d/%m/%Y") if stats.last_play_date else "Nunca",
            status_message=status_message
        )
        
        # Crear teclado de juegos
        keyboard = [
            [
                InlineKeyboardButton("🎳 Bowling", callback_data="game_bowling"),
                InlineKeyboardButton("🎯 Dardos", callback_data="game_darts")
            ],
            [
                InlineKeyboardButton("🎲 Dados", callback_data="game_dice"),
                InlineKeyboardButton("💰 Mi Balance", callback_data="game_balance")
            ],
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="game_stats"),
                InlineKeyboardButton("❓ Ayuda", callback_data="game_help")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"{GameMessages.MENU}\n\n{status_text}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def show_game_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú de juegos desde callback."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        # Obtener estadísticas del usuario
        balance = await self.game_service.get_user_balance(user_id)
        stats = await self.game_service.get_game_stats(user_id)
        
        # Determinar mensaje de estado
        can_play = await self.game_service.can_play_today(user_id)
        can_win = await self.game_service.can_win_this_week(user_id)
        
        if not can_play:
            status_message = "⏰ Ya jugaste hoy. Vuelve mañana."
        elif not can_win:
            status_message = "🏆 ¡Límite de victorias semanales alcanzado!"
        else:
            status_message = "✅ ¡Puedes jugar y ganar hoy!"
        
        # Crear mensaje de estado
        status_text = GameMessages.GAME_STATUS.format(
            stars=balance.stars_balance,
            games_today=1 if not can_play else 0,
            weekly_wins=len(stats.current_week_wins),
            last_game=stats.last_play_date.strftime("%d/%m/%Y") if stats.last_play_date else "Nunca",
            status_message=status_message
        )
        
        from telegram_bot.keyboard import OperationKeyboards
        
        await query.edit_message_text(
            f"{GameMessages.MENU}\n\n{status_text}",
            reply_markup=OperationKeyboards.games_menu(),
            parse_mode="Markdown"
        )
    
    async def game_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja callbacks del menú de juegos."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        action = query.data
        
        if action == "games_menu":
            await self.show_game_menu_callback(update, context)
        elif action.startswith("game_"):
            game_type_str = action.replace("game_", "")
            
            if game_type_str in ["bowling", "darts", "dice"]:
                await self._handle_game_selection(query, game_type_str)
            elif game_type_str == "balance":
                await self._show_balance(query, user_id)
            elif game_type_str == "stats":
                await self._show_stats(query, user_id)
            elif game_type_str == "help":
                await self._show_help(query)
    
    async def _handle_game_selection(self, query, game_type_str: str):
        """Maneja la selección de un juego."""
        user_id = query.from_user.id
        
        # Verificar si puede jugar
        if not await self.game_service.can_play_today(user_id):
            await query.edit_message_text(
                GameMessages.ALREADY_PLAYED_TODAY.format(
                    hours_left=24 - datetime.now().hour
                ),
                parse_mode="Markdown"
            )
            return
        
        # Verificar si puede ganar esta semana
        if not await self.game_service.can_win_this_week(user_id):
            await query.edit_message_text(
                GameMessages.WEEKLY_LIMIT_REACHED,
                parse_mode="Markdown"
            )
            return
        
        # Mostrar mensaje del juego específico
        game_messages = {
            "bowling": GameMessages.BOWLING_GAME,
            "darts": GameMessages.DARTS_GAME,
            "dice": GameMessages.DICE_GAME
        }
        
        game_type = GameType(game_type_str)
        
        # Crear teclado para jugar
        keyboard = [
            [
                InlineKeyboardButton("🎮 JUGAR AHORA", callback_data=f"play_{game_type_str}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            game_messages[game_type_str],
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def _play_game(self, query, game_type_str: str):
        """Ejecuta el juego."""
        user_id = query.from_user.id
        game_type = GameType(game_type_str)
        
        # Animación de juego
        await query.edit_message_text(
            f"🎮 Jugando {GameMessages.get_game_name(game_type_str)}...\n\n"
            f"{GameMessages.get_game_emoji(game_type_str)} ¡Prepárate!",
            parse_mode="Markdown"
        )
        
        # Pequeña pausa para suspense
        import asyncio
        await asyncio.sleep(2)
        
        # Jugar y obtener resultado
        try:
            result, stars_earned = await self.game_service.play_game(user_id, game_type)
            
            # Obtener balance actualizado
            balance = await self.game_service.get_user_balance(user_id)
            
            if result == GameResult.WIN:
                message = GameMessages.WIN_MESSAGE.format(
                    game_type=GameMessages.get_game_name(game_type_str),
                    stars=stars_earned,
                    total_stars=balance.stars_balance
                )
            else:
                message = GameMessages.LOSE_MESSAGE.format(
                    game_type=GameMessages.get_game_name(game_type_str)
                )
            
            # Teclado para volver al menú
            keyboard = CommonKeyboards.action_buttons([
                ("🎮 Volver a Juegos", "games_menu"),
                ("💰 Ver Balance", "game_balance")
            ])
            
            reply_markup = keyboard
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            self.bot_logger.log_error(e, f"Error playing game for user {user_id}")
            await query.edit_message_text(
                "❌ Ocurrió un error al jugar. Inténtalo de nuevo.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Volver", callback_data="games_menu")
                ]])
            )
    
    async def _show_balance(self, query, user_id: int):
        """Muestra el balance del usuario."""
        balance = await self.game_service.get_user_balance(user_id)
        
        message = GameMessages.BALANCE_INFO.format(
            stars=balance.stars_balance,
            last_updated=balance.last_updated.strftime("%d/%m/%Y %H:%M")
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🎮 Volver a Juegos", callback_data="games_menu"),
                InlineKeyboardButton("🔙 Volver a Operaciones", callback_data="operations")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def _show_stats(self, query, user_id: int):
        """Muestra estadísticas del usuario."""
        stats = await self.game_service.get_game_stats(user_id)
        recent_games = await self.game_service.get_recent_games(user_id, 5)
        
        # Construir mensaje de estadísticas
        stats_text = f"""📊 **Tus Estadísticas**

🎮 **Total de juegos:** {stats.total_games}
🏆 **Total de victorias:** {stats.total_wins}
📈 **Tasa de victoria:** {(stats.total_wins / max(stats.total_games, 1) * 100):.1f}%

📅 **Último juego:** {stats.last_play_date.strftime("%d/%m/%Y") if stats.last_play_date else "Nunca"}
🏅 **Victorias esta semana:** {len(stats.current_week_wins)}/3

🕐 **Juegos recientes:"""
        
        if recent_games:
            for game in recent_games:
                emoji = "🏆" if game.result == GameResult.WIN else "❌"
                game_emoji = GameMessages.get_game_emoji(game.game_type.value)
                stats_text += f"\n{emoji} {game_emoji} {game.played_at.strftime('%d/%m %H:%M')}"
        else:
            stats_text += "\nNo hay juegos recientes"
        
        keyboard = [
            [
                InlineKeyboardButton("🎮 Volver a Juegos", callback_data="games_menu"),
                InlineKeyboardButton("🔙 Volver a Operaciones", callback_data="operations")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            stats_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def _show_help(self, query):
        """Muestra la ayuda del sistema de juegos."""
        keyboard = [
            [
                InlineKeyboardButton("🎮 Volver a Juegos", callback_data="games_menu"),
                InlineKeyboardButton("🔙 Volver a Operaciones", callback_data="operations")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            GameMessages.HELP,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def play_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el callback de jugar."""
        query = update.callback_query
        await query.answer()
        
        action = query.data
        if action.startswith("play_"):
            game_type_str = action.replace("play_", "")
            await self._play_game(query, game_type_str)
    
    def get_handlers(self):
        """Retorna los handlers de juegos."""
        return [
            # Handler para comando /juegos o desde menú
            MessageHandler(filters.Regex("^🎮 Juga y Gana$"), self.show_game_menu),
            
            # Callback para mostrar menú de juegos desde operaciones
            CallbackQueryHandler(self.show_game_menu_callback, pattern="^games_menu$"),
            
            # Callbacks del menú de juegos
            CallbackQueryHandler(self.game_callback, pattern="^(game_|play_)"),
        ]


def get_game_handlers(game_service):
    """Función para obtener los handlers de juegos."""
    handler = GameHandler(game_service)
    return handler.get_handlers()
