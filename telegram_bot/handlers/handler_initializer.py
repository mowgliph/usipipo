from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

from config import settings
from telegram_bot.keyboard.keyboard import Keyboards
from telegram_bot.messages.messages import Messages

# Importación de Handlers
from telegram_bot.handlers.start_handler import start_handler
from telegram_bot.handlers.crear_llave_handler import get_creation_handler
from telegram_bot.handlers.keys_manager_handler import list_keys_handler, delete_callback_handler
from telegram_bot.handlers.status_handler import status_handler
from telegram_bot.handlers.ayuda_handler import ayuda_handler
from telegram_bot.handlers.support_handler import get_support_handler, admin_reply_handler
from telegram_bot.handlers.support_menu_handler import get_support_menu_handler
from telegram_bot.handlers.referral_handler import get_referral_handlers
from telegram_bot.handlers.payment_handler import get_payment_handlers
from telegram_bot.handlers.monitoring_handler import get_monitoring_handlers
from telegram_bot.handlers.broadcast_handler import get_broadcast_handler
from telegram_bot.handlers.game_handler import get_game_handlers
from telegram_bot.handlers.admin_handler import get_admin_handler
from telegram_bot.handlers.achievement_handler import (
    achievements_menu_handler, achievements_progress_handler, achievements_list_handler,
    achievements_category_handler, achievements_next_handler, achievements_rewards_handler,
    claim_reward_handler, achievements_leaderboard_handler, leaderboard_category_handler
)
from utils.bot_logger import get_logger
from application.services.game_service import GameService
from application.services.admin_service import AdminService
from application.services.achievement_service import AchievementService
from infrastructure.persistence.supabase.achievement_repository import AchievementRepository, UserStatsRepository

def initialize_handlers(vpn_service, support_service, referral_service, payment_service):
    """
    Initializes all Telegram bot handlers by taking services as parameters
    and returns a list of all handlers to be registered.

    Args:
        vpn_service: The VPN service instance.
        support_service: The support service instance.
        referral_service: The referral service instance.
        payment_service: The payment service instance.

    Returns:
        List of handler objects to be added to the Telegram application.
    """
    handlers = []

    # Obtener sesión de base de datos directamente del repositorio
    db_session = vpn_service.key_repo.client

    # Inicializar servicio de logros
    achievement_repository = AchievementRepository(db_session)
    user_stats_repository = UserStatsRepository(db_session)
    achievement_service = AchievementService(achievement_repository, user_stats_repository)

    # Comando /start y botón de registro
    handlers.append(CommandHandler("start", lambda u, c: start_handler(u, c, vpn_service)))

    # Flujo de Creación de Llaves (ConversationHandler)
    handlers.append(get_creation_handler(vpn_service))

    # Gestión de Llaves (Listar y Botones Inline de borrado)
    handlers.append(MessageHandler(filters.Regex("^🛡️ Mis Llaves$"),
                                   lambda u, c: list_keys_handler(u, c, vpn_service)))
    handlers.append(CallbackQueryHandler(lambda u, c: delete_callback_handler(u, c, vpn_service),
                                         pattern="^(delete_|cancel_delete)"))

    # Estado y Métricas
    handlers.append(MessageHandler(filters.Regex("^📊 Estado$"),
                                   lambda u, c: status_handler(u, c, vpn_service)))

    # Operaciones (Referidos, VIP, etc.)
    async def operations_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            text=Messages.Operations.MENU_TITLE,
            reply_markup=Keyboards.operations_menu(),
            parse_mode="Markdown"
        )

    handlers.append(MessageHandler(filters.Regex("^💰 Operaciones$"), operations_handler))

    # Sistema de Logros
    handlers.append(MessageHandler(filters.Regex("^🏆 Logros$"),
                                   lambda u, c: achievements_menu_handler(u, c, achievement_service)))
    
    # Callbacks del sistema de logros
    handlers.extend([
        CallbackQueryHandler(lambda u, c: achievements_progress_handler(u, c, achievement_service),
                            pattern="^achievements_progress$"),
        CallbackQueryHandler(lambda u, c: achievements_list_handler(u, c, achievement_service),
                            pattern="^achievements_list$"),
        CallbackQueryHandler(lambda u, c: achievements_category_handler(u, c, achievement_service),
                            pattern="^achievements_category_"),
        CallbackQueryHandler(lambda u, c: achievements_next_handler(u, c, achievement_service),
                            pattern="^achievements_next$"),
        CallbackQueryHandler(lambda u, c: achievements_rewards_handler(u, c, achievement_service),
                            pattern="^achievements_rewards$"),
        CallbackQueryHandler(lambda u, c: claim_reward_handler(u, c, achievement_service),
                            pattern="^claim_reward_"),
        CallbackQueryHandler(lambda u, c: achievements_leaderboard_handler(u, c, achievement_service),
                            pattern="^achievements_leaderboard$"),
        CallbackQueryHandler(lambda u, c: leaderboard_category_handler(u, c, achievement_service),
                            pattern="^leaderboard_"),
    ])

    # Ayuda General
    handlers.append(MessageHandler(filters.Regex("^⚙️ Ayuda$"), ayuda_handler))

    # Soporte Directo Chat-to-Admin (ConversationHandler)
    handlers.append(get_support_handler(support_service))

    # Handler especial para que el Admin responda
    handlers.append(MessageHandler(filters.Chat(chat_id=int(settings.ADMIN_ID)) & ~filters.COMMAND,
                                   lambda u, c: admin_reply_handler(u, c, support_service)))

    # Sistema de Referidos
    handlers.extend(get_referral_handlers(referral_service, vpn_service))

    # Sistema de Pagos
    handlers.extend(get_payment_handlers(referral_service, vpn_service, payment_service))

    # Sistema de Monitorización (solo para admin)
    monitoring_handlers, monitoring_instance = get_monitoring_handlers(settings.ADMIN_ID)
    handlers.extend(monitoring_handlers)
    
    # Conectar el logger con el sistema de monitorización
    bot_logger = get_logger()
    bot_logger.set_monitoring_handler(monitoring_instance)

    # Sistema de Broadcast (solo para admin)
    handlers.append(get_broadcast_handler())

    # Sistema de Juegos Play & Earn
    game_service = GameService()
    handlers.extend(get_game_handlers(game_service))

    # Handler de Soporte desde menú de operaciones
    handlers.extend(get_support_menu_handler(support_service))

    # Sistema de Administración (solo para admin)
    admin_service = AdminService(
        key_repository=vpn_service.key_repo,
        user_repository=vpn_service.user_repo,
        payment_repository=payment_service.transaction_repo
    )
    handlers.append(get_admin_handler(admin_service))

    return handlers