from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

from application.services.achievement_service import AchievementService
from application.services.admin_service import AdminService
from application.services.common.container import get_container
from application.services.game_service import GameService
from application.services.task_service import TaskService
from config import settings
from telegram_bot.handlers.achievement_handler import (
    achievements_menu_handler, achievements_progress_handler, achievements_list_handler,
    achievements_category_handler, achievements_next_handler, achievements_rewards_handler,
    claim_reward_handler, achievements_leaderboard_handler, leaderboard_category_handler
)
from telegram_bot.handlers.admin_handler import get_admin_handler, admin_command_handler
from telegram_bot.handlers.admin_task_handler import get_admin_task_handler
from telegram_bot.handlers.ayuda_handler import ayuda_handler, help_command_handler
from telegram_bot.handlers.broadcast_handler import get_broadcast_handler
from telegram_bot.handlers.crear_llave_handler import get_creation_handler
from telegram_bot.handlers.game_handler import get_game_handlers
from telegram_bot.handlers.inline_callbacks_handler import get_inline_callback_handlers
from telegram_bot.handlers.key_submenu_handler import get_key_submenu_handler
from telegram_bot.handlers.keys_manager_handler import list_keys_handler, delete_callback_handler
from telegram_bot.handlers.monitoring_handler import get_monitoring_handlers
from telegram_bot.handlers.payment_handler import get_payment_handlers
from telegram_bot.handlers.referral_handler import get_referral_handlers
from telegram_bot.handlers.start_handler import start_handler
from telegram_bot.handlers.status_handler import status_handler
from telegram_bot.handlers.support_handler import get_support_handler, admin_reply_handler
from telegram_bot.handlers.cancel_handler import cancel_handler
from telegram_bot.handlers.support_menu_handler import get_support_menu_handler
from telegram_bot.handlers.task_handler import get_task_handler
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards, InlineAdminKeyboards
from telegram_bot.keyboard.keyboard import Keyboards
from telegram_bot.messages.game_messages import GameMessages
from telegram_bot.messages.messages import Messages
from utils.logger import logger, get_logger

def initialize_handlers(vpn_service, support_service, referral_service, payment_service, achievement_service=None):
    """
    Inicializa todos los handlers del bot de Telegram.

    Args:
        vpn_service: Servicio de VPN.
        support_service: Servicio de soporte.
        referral_service: Servicio de referidos.
        payment_service: Servicio de pagos.
        achievement_service: Servicio de logros (si es None, se obtiene del contenedor).

    Returns:
        Lista de handlers para registrar en la aplicación.
    """
    handlers = []
    
    # Obtener contenedor de dependencias
    container = get_container()

    # Si no se proporciona achievement_service, obtenerlo del contenedor
    if achievement_service is None:
        achievement_service = container.resolve(AchievementService)

    # Resolver admin_service (se usará para handlers inline que delegan a AdminHandler)
    admin_service = container.resolve(AdminService)

    # Comando /start y botón de registro
    handlers.append(CommandHandler("start", start_handler))

    # Comando /help
    handlers.append(CommandHandler("help", help_command_handler))
    
    # Comando /cancelar
    handlers.append(CommandHandler("cancelar", cancel_handler))
    
    # Comando /admin
    handlers.append(CommandHandler("admin", admin_command_handler))

    # Flujo de Creación de Llaves (ConversationHandler)
    handlers.append(get_creation_handler(vpn_service))

    # Gestión de Llaves (Sistema de Submenús)
    key_submenu_handler = get_key_submenu_handler(vpn_service)
    handlers.append(MessageHandler(filters.Regex("^🛡️ Mis Llaves$"),
                                   lambda u, c: key_submenu_handler.show_key_submenu(u, c)))
    
    # Submenú de llaves - Callback handlers
    handlers.extend(key_submenu_handler.get_handlers())
    
    # Submenú de llaves - Message handlers
    handlers.extend(key_submenu_handler.get_message_handlers())
    
    # Legacy handlers (mantener compatibilidad)
    handlers.append(CallbackQueryHandler(lambda u, c: delete_callback_handler(u, c, vpn_service),
                                         pattern="^(delete_|cancel_delete)"))

    # Estado y Métricas
    handlers.append(MessageHandler(filters.Regex("^📊 Estado$"),
                                   lambda u, c: status_handler(u, c, vpn_service)))

    # Operaciones (Referidos, VIP, etc.)
    async def operations_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el botón '💰 Operaciones'."""
        await update.message.reply_text(
            text=Messages.Operations.MENU_TITLE,
            reply_markup=InlineKeyboards.operations_menu(),
            parse_mode="Markdown"
        )

    handlers.append(MessageHandler(filters.Regex("^💰 Operaciones$"), operations_handler))

    # Botones del menú de operaciones
    async def mi_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el botón 'Mi Balance'."""
        user_id = update.effective_user.id
        try:
            user_status = await vpn_service.get_user_status(user_id)
            user = user_status["user"]
            
            text = Messages.Operations.BALANCE_INFO.format(
                name=user.full_name or user.username or f"Usuario {user.telegram_id}",
                balance=user.balance_stars,
                total_deposited=user.total_deposited,
                referral_earnings=user.total_referral_earnings
            )
            
            await update.message.reply_text(
                text=text,
                reply_markup=InlineKeyboards.operations_menu(),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.log_error(e, context='mi_balance_handler', user_id=user_id)
            await update.message.reply_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=InlineKeyboards.operations_menu()
            )

    async def plan_vip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el botón 'Plan VIP'."""
        text = Messages.Operations.VIP_PLAN_INFO.format(
            max_keys=settings.VIP_PLAN_MAX_KEYS,
            data_limit=settings.VIP_PLAN_DATA_LIMIT_GB,
            cost="10 estrellas por mes"
        )

        await update.message.reply_text(
            text=text,
            reply_markup=InlineKeyboards.vip_plans(),
            parse_mode="Markdown"
        )

    async def juega_y_gana_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el botón 'Juega y Gana'."""
        user_id = update.effective_user.id
        try:
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
                reply_markup=InlineKeyboards.games_menu(),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.log_error(e, context='juega_y_gana_handler', user_id=user_id)
            await update.message.reply_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=InlineKeyboards.operations_menu()
            )

    async def referidos_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el botón 'Referidos'."""
        user_id = update.effective_user.id
        try:
            referral_data = await referral_service.get_user_referral_data(user_id)
            
            text = Messages.Operations.REFERRAL_PROGRAM.format(
                bot_username="usipipo_vpn_bot",  # Reemplazar con el nombre del bot real
                referral_code=referral_data.get("code", "N/A"),
                direct_referrals=referral_data.get("direct_referrals", 0),
                total_earnings=referral_data.get("total_earnings", 0),
                commission=10
            )
            
            await update.message.reply_text(
                text=text,
                reply_markup=InlineKeyboards.referral_actions(),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.log_error(e, context='referidos_handler', user_id=user_id)
            await update.message.reply_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=InlineKeyboards.operations_menu()
            )

    async def atras_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el botón 'Atrás' en el menú de operaciones."""
        user = update.effective_user
        
        # Determinar si es admin
        is_admin = user.id == int(settings.ADMIN_ID)
        
        await update.message.reply_text(
            text="👇 Menú Principal",
            reply_markup=InlineKeyboards.main_menu(is_admin=is_admin),
            parse_mode="Markdown"
        )

    handlers.append(MessageHandler(filters.Regex("^💰 Mi Balance$"), mi_balance_handler))
    handlers.append(MessageHandler(filters.Regex("^👑 Plan VIP$"), plan_vip_handler))
    handlers.append(MessageHandler(filters.Regex("^🎮 Juega y Gana$"), juega_y_gana_handler))
    handlers.append(MessageHandler(filters.Regex("^👥 Referidos$"), referidos_handler))
    handlers.append(MessageHandler(filters.Regex("^🔙 Atrás$"), atras_handler))

    # Callback handler para el botón "Volver" desde operaciones (usado en menús inline)
    async def operations_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el callback 'operations_menu'."""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            text=Messages.Operations.MENU_TITLE,
            reply_markup=InlineKeyboards.operations_menu(),
            parse_mode="Markdown"
        )

    handlers.append(CallbackQueryHandler(operations_menu_callback, pattern="^operations_menu$"))

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

    # Botón de respaldo para mostrar menú principal
    async def show_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el botón '📋 Mostrar Menú' del teclado de respaldo."""
        user = update.effective_user
        logger.log_bot_event("INFO", f"Botón 'Mostrar Menú' presionado por usuario {user.id}")
        
        try:
            # Determinar si es admin para mostrar el menú correspondiente
            is_admin = user.id == int(settings.ADMIN_ID)
            
            await update.message.reply_text(
                text="👇 Menú Principal",
                reply_markup=InlineKeyboards.main_menu(is_admin=is_admin),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.log_error(e, context="show_menu_handler", user_id=user.id)
            await update.message.reply_text(
                text="❌ Error al mostrar el menú. Por favor, intenta nuevamente.",
                reply_markup=Keyboards.show_menu_button()
            )

    handlers.append(MessageHandler(filters.Regex(r"^📋\s*Mostrar\s*Menú$"), show_menu_handler))

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
    logger.set_monitoring_handler(monitoring_instance)

    # Sistema de Broadcast (solo para admin)
    handlers.append(get_broadcast_handler())

    # Sistema de Juegos Play & Earn
    game_service = GameService()
    handlers.extend(get_game_handlers(game_service))

    # Handler de Soporte desde menú de operaciones
    handlers.extend(get_support_menu_handler(support_service))

    # Sistema de Administración (solo para admin)
    admin_service = container.resolve(AdminService)
    handlers.append(get_admin_handler(admin_service))

    # Sistema de Tareas
    task_service = container.resolve(TaskService)
    task_handler = get_task_handler(task_service)
    handlers.extend(task_handler.get_handlers())
    
    # Sistema de Administración de Tareas (solo para admin)
    admin_task_handler = get_admin_task_handler(task_service)
    handlers.extend(admin_task_handler.get_handlers())

    # Handlers para callbacks inline del nuevo sistema
    handlers.extend(get_inline_callback_handlers(vpn_service, achievement_service, support_service, admin_service))
    

    return handlers