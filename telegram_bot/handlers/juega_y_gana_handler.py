"""
Handler del Botón 'Juega y Gana'.

Maneja la lógica del botón de juegos en el menú de operaciones.
Los teclados se gestionan en telegram_bot/keyboard/inline_keyboards.py

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update
from telegram.ext import ContextTypes

from application.services.game_service import GameService
from telegram_bot.keyboard import OperationKeyboards
from telegram_bot.messages.game_messages import GameMessages
from telegram_bot.messages import CommonMessages
from utils.logger import logger


async def juega_y_gana_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para el botón 'Juega y Gana'."""
    user_id = update.effective_user.id
    try:
        game_service = GameService()
        
        # Obtener estadísticas del usuario
        balance = await game_service.get_user_balance(user_id)
        stats = await game_service.get_game_stats(user_id)
        
        # Determinar mensaje de estado
        can_play = await game_service.can_play_today(user_id)
        can_win = await game_service.can_win_this_week(user_id)
        
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
        
        await update.message.reply_text(
            f"{GameMessages.MENU}\n\n{status_text}",
            reply_markup=OperationKeyboards.games_menu(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.log_error(e, context='juega_y_gana_handler', user_id=user_id)
        await update.message.reply_text(
            text=CommonMessages.Errors.GENERIC.format(error=str(e)),
            reply_markup=OperationKeyboards.operations_menu()
        )
