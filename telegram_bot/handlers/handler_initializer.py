"""
Handler Initializer for uSipipo VPN Manager Bot.

Centralizes the initialization and registration of all Telegram handlers
across different features following the hexagonal architecture pattern.

Author: uSipipo Team
Version: 2.0.0
"""

from typing import List
from telegram.ext import BaseHandler
from utils.logger import logger

# Import all feature handlers
from telegram_bot.features.admin.handlers_admin import (
    get_admin_handlers, get_admin_callback_handlers
)
from telegram_bot.features.achievements.handlers_achievements import (
    get_achievements_handlers, get_achievements_callback_handlers
)
from telegram_bot.features.ai_support.handlers_ai_support import (
    get_ai_support_handler, get_ai_callback_handlers
)
from telegram_bot.features.ai_support.direct_message_handler import get_direct_message_handler
from telegram_bot.features.announcer.handlers_announcer import (
    get_announcer_handlers, get_announcer_callback_handlers
)
from telegram_bot.features.broadcast.handlers_broadcast import (
    get_broadcast_handlers, get_broadcast_callback_handlers
)
from telegram_bot.features.game.handlers_game import (
    get_game_handlers, get_game_callback_handlers
)
from telegram_bot.features.key_management.handlers_key_management import (
    get_key_management_handlers, get_key_management_callback_handlers
)
from telegram_bot.features.operations.handlers_operations import (
    get_operations_handlers, get_operations_callback_handlers
)
from telegram_bot.features.payments.handlers_payments import (
    get_payments_handlers, get_payments_callback_handlers
)
from telegram_bot.features.referral.handlers_referral import (
    get_referral_handlers, get_referral_callback_handlers
)
from telegram_bot.features.shop.handlers_shop import (
    get_shop_handlers, get_shop_callback_handlers
)
from telegram_bot.features.support.handlers_support import (
    get_support_handlers, get_support_callback_handlers
)
from telegram_bot.features.task_management.handlers_task_management import (
    get_task_management_handlers, get_task_management_callback_handlers
)
from telegram_bot.features.user_management.handlers_user_management import (
    get_user_management_handlers, get_user_callback_handlers
)
from telegram_bot.features.vip.handlers_vip import (
    get_vip_handlers, get_vip_callback_handlers
)
from telegram_bot.features.vpn_keys.handlers_vpn_keys import (
    get_vpn_keys_handlers, get_vpn_keys_callback_handlers
)

# Import required services
from application.services.vpn_service import VpnService
from application.services.support_service import SupportService
from application.services.payment_service import PaymentService
from application.services.referral_service import ReferralService
from application.services.achievement_service import AchievementService
from application.services.admin_service import AdminService
from application.services.ai_support_service import AiSupportService
from application.services.announcer_service import AnnouncerService
from application.services.broadcast_service import BroadcastService
from application.services.game_service import GameService
from application.services.task_service import TaskService
from application.services.common.container import get_container


def _get_admin_handlers(container) -> List[BaseHandler]:
    """Initialize and return admin handlers."""
    admin_service = container.resolve(AdminService)
    handlers = []
    handlers.extend(get_admin_handlers(admin_service))
    handlers.extend(get_admin_callback_handlers(admin_service))
    logger.info("✅ Handlers de administración configurados")
    return handlers


def _get_ai_support_handlers(container) -> List[BaseHandler]:
    """Initialize and return AI support handlers."""
    ai_support_service = container.resolve(AiSupportService)
    handlers = []

    # 1. ConversationHandler for explicit AI chats (high priority)
    handlers.extend([get_ai_support_handler(ai_support_service)])
    handlers.extend(get_ai_callback_handlers(ai_support_service))
    logger.info("✅ Handlers de soporte IA (ConversationHandler) configurados")

    # 2. Direct message handler (fallback - registered last)
    direct_message_handler = container.resolve("direct_message_handler")
    handlers.append(direct_message_handler)
    logger.info("✅ Handler de mensajes directos registrado (fallback)")

    return handlers


def _get_service_handlers(container, vpn_service) -> List[BaseHandler]:
    """Initialize and return all service-based handlers."""
    handlers = []

    # Announcer handlers
    announcer_service = container.resolve(AnnouncerService)
    handlers.extend(get_announcer_handlers(announcer_service, vpn_service))
    handlers.extend(get_announcer_callback_handlers(announcer_service, vpn_service))
    logger.info("✅ Handlers de anunciador configurados")

    # Broadcast handlers
    broadcast_service = container.resolve(BroadcastService)
    handlers.extend(get_broadcast_handlers(broadcast_service))
    handlers.extend(get_broadcast_callback_handlers(broadcast_service))
    logger.info("✅ Handlers de difusión configurados")

    # Game handlers
    game_service = container.resolve(GameService)
    handlers.extend(get_game_handlers(game_service))
    handlers.extend(get_game_callback_handlers(game_service))
    logger.info("✅ Handlers de juego configurados")

    # Task management handlers
    task_service = container.resolve(TaskService)
    handlers.extend(get_task_management_handlers(task_service, vpn_service))
    handlers.extend(get_task_management_callback_handlers(task_service, vpn_service))
    logger.info("✅ Handlers de gestión de tareas configurados")

    return handlers


def _get_core_handlers(vpn_service, referral_service, payment_service,
                      support_service, achievement_service) -> List[BaseHandler]:
    """Initialize and return core feature handlers."""
    handlers = []

    # Achievement handlers
    handlers.extend(get_achievements_handlers(achievement_service))
    handlers.extend(get_achievements_callback_handlers(achievement_service))
    logger.info("✅ Handlers de logros configurados")

    # Key management handlers
    handlers.extend(get_key_management_handlers(vpn_service))
    handlers.extend(get_key_management_callback_handlers(vpn_service))
    logger.info("✅ Handlers de gestión de claves configurados")

    # Operations handlers
    handlers.extend(get_operations_handlers(vpn_service, referral_service))
    handlers.extend(get_operations_callback_handlers(vpn_service, referral_service))
    logger.info("✅ Handlers de operaciones configurados")

    # Payment handlers
    handlers.extend(get_payments_handlers(payment_service, vpn_service, referral_service))
    handlers.extend(get_payments_callback_handlers(payment_service, vpn_service, referral_service))
    logger.info("✅ Handlers de pagos configurados")

    # Referral handlers
    handlers.extend(get_referral_handlers(referral_service, vpn_service))
    handlers.extend(get_referral_callback_handlers(referral_service, vpn_service))
    logger.info("✅ Handlers de referidos configurados")

    # Shop handlers
    handlers.extend(get_shop_handlers(payment_service, vpn_service))
    handlers.extend(get_shop_callback_handlers(payment_service, vpn_service))
    logger.info("✅ Handlers de tienda configurados")

    # Support handlers
    handlers.extend(get_support_handlers(support_service))
    handlers.extend(get_support_callback_handlers(support_service))
    logger.info("✅ Handlers de soporte configurados")

    # User management handlers
    handlers.extend(get_user_management_handlers(vpn_service, achievement_service))
    handlers.extend(get_user_callback_handlers(vpn_service, achievement_service))
    logger.info("✅ Handlers de gestión de usuarios configurados")

    # VIP handlers
    handlers.extend(get_vip_handlers(payment_service, vpn_service))
    handlers.extend(get_vip_callback_handlers(payment_service, vpn_service))
    logger.info("✅ Handlers VIP configurados")

    # VPN keys handlers
    handlers.extend(get_vpn_keys_handlers(vpn_service))
    handlers.extend(get_vpn_keys_callback_handlers(vpn_service))
    logger.info("✅ Handlers de claves VPN configurados")

    return handlers


def initialize_handlers(
    vpn_service: VpnService,
    support_service: SupportService,
    referral_service: ReferralService,
    payment_service: PaymentService,
    achievement_service: AchievementService
) -> List[BaseHandler]:
    """
    Initialize and return all Telegram handlers for the bot.

    This function follows the hexagonal architecture pattern by:
    - Centralizing handler registration
    - Using dependency injection for services
    - Maintaining clean separation of concerns

    Args:
        vpn_service: VPN management service
        support_service: Customer support service
        referral_service: Referral system service
        payment_service: Payment processing service
        achievement_service: Achievement system service

    Returns:
        List[BaseHandler]: List of all configured handlers
    """
    logger.info("🔧 Inicializando handlers del bot...")
    handlers = []

    try:
        container = get_container()

        # Admin handlers
        handlers.extend(_get_admin_handlers(container))

        # AI Support handlers
        handlers.extend(_get_ai_support_handlers(container))

        # Service-based handlers
        handlers.extend(_get_service_handlers(container, vpn_service))

        # Core feature handlers
        handlers.extend(_get_core_handlers(
            vpn_service, referral_service, payment_service, support_service, achievement_service
        ))

        logger.info(f"🎉 Total de handlers configurados: {len(handlers)}")
        return handlers

    except Exception as e:
        logger.error(f"❌ Error al inicializar handlers: {e}")
        raise
