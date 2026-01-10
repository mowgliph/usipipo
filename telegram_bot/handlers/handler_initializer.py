from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

from application.services.achievement_service import AchievementService
from application.services.admin_service import AdminService
from application.services.common.container import get_container
from config import settings
from telegram_bot.handlers.achievement_handler import (
    achievements_menu_handler, achievements_progress_handler, achievements_list_handler,
    achievements_category_handler, achievements_next_handler, achievements_rewards_handler,
    claim_reward_handler, achievements_leaderboard_handler, leaderboard_category_handler
)
from telegram_bot.handlers.admin_handler import admin_command_handler
from telegram_bot.handlers.ayuda_handler import ayuda_handler, help_command_handler
from telegram_bot.handlers.info_handler import info_handler
from telegram_bot.handlers.start_handler import start_handler
from telegram_bot.handlers.keys_manager_handler import delete_callback_handler
from telegram_bot.handlers.status_handler import status_handler
from telegram_bot.handlers.support_handler import admin_reply_handler
from telegram_bot.handlers.cancel_handler import cancel_handler
from telegram_bot.handlers.operations_handler import (
    operations_handler, mi_balance_handler, 
    referidos_handler, atras_handler, operations_menu_callback
)
from telegram_bot.handlers.juega_y_gana_handler import juega_y_gana_handler
from telegram_bot.handlers.menu_handler import show_menu_handler
from telegram_bot.keyboard import UserKeyboards
from telegram_bot.messages import UserMessages
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
    
    # Resolver vip_command_handler para el comando /vip
    vip_command_handler, vip_callback_handlers = container.resolve("vip_command_handler")

    # Comando /start y botón de registro
    handlers.append(CommandHandler("start", start_handler))

    # Comando /help
    handlers.append(CommandHandler("help", help_command_handler))
    
    # Comando /info
    handlers.append(CommandHandler("info", info_handler))
    
    # Comando /cancelar
    handlers.append(CommandHandler("cancelar", cancel_handler))
    
    # Comando /admin
    handlers.append(CommandHandler("admin", admin_command_handler))

    # Flujo de Creación de Llaves (ConversationHandler)
    creation_handler = container.resolve("creation_handlers")
    handlers.append(creation_handler)

    # Gestión de Llaves (Sistema de Submenús)
    key_submenu_handler = container.resolve("key_submenu_handlers")
    handlers.append(MessageHandler(filters.Regex("^🛡️ Mis Llaves$"),
                                   lambda u, c: key_submenu_handler.show_key_submenu(u, c)))
    handlers.append(CommandHandler("mykeys", lambda u, c: key_submenu_handler.show_key_submenu(u, c)))
    
    # Submenú de llaves - Callback handlers
    handlers.extend(key_submenu_handler.get_handlers())
    
    # Submenú de llaves - Message handlers
    handlers.extend(key_submenu_handler.get_message_handlers())
    
    # Legacy handlers (mantener compatibilidad)
    handlers.append(CallbackQueryHandler(lambda u, c: delete_callback_handler(u, c, vpn_service),
                                         pattern="^(delete_|cancel_delete)"))

    # Estado y Métricas
    handlers.append(MessageHandler(filters.Regex("^📊 Estado$"),
                                   lambda u, c: status_handler(u, c, vpn_service, admin_service)))
    handlers.append(CommandHandler("status", lambda u, c: status_handler(u, c, vpn_service, admin_service)))

    # Operaciones (Referidos, VIP, etc.)
    handlers.append(MessageHandler(filters.Regex("^💰 Operaciones$"), operations_handler))
    # Botones del menú de operaciones
    handlers.append(MessageHandler(filters.Regex("^💰 Mi Balance$"), 
                                   lambda u, c: mi_balance_handler(u, c, vpn_service)))
    handlers.append(CommandHandler("balance", lambda u, c: mi_balance_handler(u, c, vpn_service)))

    handlers.append(MessageHandler(filters.Regex("^👑 Plan VIP$"), lambda u, c: vip_command_handler.show_vip_plans(u, c)))
    handlers.append(CommandHandler("vip", lambda u, c: vip_command_handler.show_vip_plans(u, c)))

    handlers.append(MessageHandler(filters.Regex("^🎮 Juega y Gana$"), juega_y_gana_handler))
    handlers.append(CommandHandler("game", juega_y_gana_handler))

    handlers.append(MessageHandler(filters.Regex("^👥 Referidos$"), 
                                   lambda u, c: referidos_handler(u, c, referral_service)))
    handlers.append(CommandHandler("referrals", lambda u, c: referidos_handler(u, c, referral_service)))

    handlers.append(MessageHandler(filters.Regex("^🔙 Atrás$"), atras_handler))
    
    # Callback handler para operaciones
    handlers.append(CallbackQueryHandler(operations_menu_callback, pattern="^operations_menu$"))

    # Sistema de Logros
    handlers.append(MessageHandler(filters.Regex("^🏆 Logros$"),
                                   lambda u, c: achievements_menu_handler(u, c, achievement_service)))
    handlers.append(CommandHandler("achievements", lambda u, c: achievements_menu_handler(u, c, achievement_service)))
    
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
    handlers.append(MessageHandler(filters.Regex(r"^📋\s*Mostrar\s*Menú$"), show_menu_handler))

    # Soporte Directo Chat-to-Admin (ConversationHandler)
    support_handler = container.resolve("support_handlers")
    handlers.append(support_handler)

    # Handler especial para que el Admin responda
    handlers.append(MessageHandler(filters.Chat(chat_id=int(settings.ADMIN_ID)) & ~filters.COMMAND,
                                   lambda u, c: admin_reply_handler(u, c, support_service)))

    # Sistema de Referidos
    referral_handlers_list = container.resolve("referral_handlers")
    handlers.extend(referral_handlers_list)

    # Sistema de Pagos
    payment_handlers_list = container.resolve("payment_handlers")
    handlers.extend(payment_handlers_list)

    # Sistema de Monitorización (solo para admin)
    monitoring_handlers, monitoring_instance = container.resolve("monitoring_handlers")
    handlers.extend(monitoring_handlers)
    
    # Conectar el logger con el sistema de monitorización
    logger.set_monitoring_handler(monitoring_instance)

    # Sistema de Broadcast (solo para admin)
    broadcast_handler = container.resolve("broadcast_handlers")
    handlers.append(broadcast_handler)

    # Sistema de Juegos Play & Earn
    game_handlers_list = container.resolve("game_handlers")
    handlers.extend(game_handlers_list)

    # Handler de Soporte desde menú de operaciones
    support_menu_handlers_list = container.resolve("support_menu_handlers")
    handlers.extend(support_menu_handlers_list)

    # Sistema de Administración (solo para admin)
    admin_handler = container.resolve("admin_handlers")
    handlers.append(admin_handler)

    # Sistema de Tareas
    task_handler = container.resolve("task_handlers")
    handlers.extend(task_handler.get_handlers())
     
    # Sistema de Administración de Tareas (solo para admin)
    admin_task_handler = container.resolve("admin_task_handlers")
    handlers.extend(admin_task_handler.get_handlers())

    # Sistema de Gestor de Tareas para Usuarios con Rol Premium
    user_task_manager_handlers = container.resolve("user_task_manager_handlers")
    handlers.extend(user_task_manager_handlers)

    # Sistema de Anunciante para Usuarios con Rol Premium
    user_announcer_handlers = container.resolve("user_announcer_handlers")
    handlers.extend(user_announcer_handlers)

    # Sistema de Tienda (Shop)
    logger.log_bot_event("INFO", "Registrando handlers de tienda (shop)")
    shop_handlers = container.resolve("shop_handlers")
    handlers.extend(shop_handlers)
    logger.log_bot_event("INFO", f"Se registraron {len(shop_handlers)} handlers de tienda")

    # Callbacks del handler VIP para integración con tienda
    handlers.extend(vip_callback_handlers)
    logger.log_bot_event("INFO", f"Se registraron {len(vip_callback_handlers)} callbacks VIP")

    # Handlers para callbacks inline del nuevo sistema
    inline_callback_handlers_list = container.resolve("inline_callback_handlers")
    handlers.extend(inline_callback_handlers_list)

    # Sistema de Soporte con IA Sip (usando nueva feature structure)
    from telegram_bot.features.ai_support import get_ai_callback_handlers
    ai_support_handler = container.resolve("ai_support_handler")
    handlers.append(ai_support_handler)

    # Callbacks de IA Sip para uso fuera del ConversationHandler
    ai_support_service = container.resolve("ai_support_service")
    ai_callback_handlers = get_ai_callback_handlers(ai_support_service)
    handlers.extend(ai_callback_handlers)

    # Sistema de Gestión de Usuarios (usando nueva feature structure)
    from telegram_bot.features.user_management import get_user_management_handlers
    user_management_handlers = get_user_management_handlers(vpn_service, achievement_service)
    handlers.extend(user_management_handlers)

    # Sistema de Gestión de Llaves VPN (usando nueva feature structure)
    from telegram_bot.features.vpn_keys import get_vpn_keys_handlers
    vpn_keys_handlers = get_vpn_keys_handlers(vpn_service)
    handlers.extend(vpn_keys_handlers)

    # Sistema de Logros (usando nueva feature structure)
    from telegram_bot.features.achievements import get_achievements_handlers
    achievements_handlers = get_achievements_handlers(achievement_service)
    handlers.extend(achievements_handlers)

    # Debug logging para verificar el handler
    logger.info(f"🔍 ai_support_handler type: {type(ai_support_handler)}")
    logger.info(f"🔍 ai_support_handler entry_points: {ai_support_handler.entry_points}")

    # Handler para responder mensajes directos del usuario con IA
    # Se registra al final para que otros handlers tengan prioridad
    direct_message_handler = container.resolve("direct_message_handler")
    handlers.append(direct_message_handler)
    logger.log_bot_event("INFO", "✅ Handler de mensajes directos con IA registrado correctamente")

    return handlers