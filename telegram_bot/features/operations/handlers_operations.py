"""
Handlers para operaciones del usuario de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from application.services.vpn_service import VpnService
from application.services.referral_service import ReferralService
from .messages_operations import OperationsMessages
from .keyboards_operations import OperationsKeyboards
from telegram_bot.features.user_management.keyboards_user_management import UserManagementKeyboards
from config import settings
from utils.logger import logger


class OperationsHandler:
    """Handler para operaciones del usuario."""
    
    def __init__(self, vpn_service: VpnService, referral_service: ReferralService = None):
        """
        Inicializa el handler de operaciones.
        
        Args:
            vpn_service: Servicio de VPN
            referral_service: Servicio de referidos (opcional)
        """
        self.vpn_service = vpn_service
        self.referral_service = referral_service
        logger.info("💰 OperationsHandler inicializado")

    async def operations_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el menú principal de operaciones.
        """
        await update.message.reply_text(
            text=OperationsMessages.Menu.MAIN,
            reply_markup=OperationsKeyboards.operations_menu(),
            parse_mode="Markdown"
        )

    async def mi_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el balance del usuario.
        """
        user_id = update.effective_user.id

        try:
            user_status = await self.vpn_service.get_user_status(user_id, current_user_id=user_id)
            user = user_status["user"]

            # Verificar si el atributo total_spent existe, de lo contrario usar 0
            total_spent = getattr(user, 'total_spent', 0)

            text = OperationsMessages.Balance.DISPLAY.format(
                name=user.full_name or user.username or f"Usuario {user.telegram_id}",
                balance=user.balance_stars,
                total_deposited=user.total_deposited,
                total_spent=total_spent,
                referral_earnings=user.total_referral_earnings
            )

            # Manejar tanto mensaje como callback
            if update.message:
                await update.message.reply_text(
                    text=text,
                    reply_markup=OperationsKeyboards.operations_menu(),
                    parse_mode="Markdown"
                )
            elif update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    text=text,
                    reply_markup=OperationsKeyboards.operations_menu(),
                    parse_mode="Markdown"
                )

        except Exception as e:
            logger.error(f"Error en mi_balance: {e}")
            error_text = OperationsMessages.Error.SYSTEM_ERROR

            if update.message:
                await update.message.reply_text(
                    text=error_text,
                    reply_markup=OperationsKeyboards.operations_menu(),
                    parse_mode="Markdown"
                )
            elif update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    text=error_text,
                    reply_markup=OperationsKeyboards.operations_menu(),
                    parse_mode="Markdown"
                )

    async def referidos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el sistema de referidos.
        """
        if not self.referral_service:
            error_text = OperationsMessages.Error.SERVICE_UNAVAILABLE
            
            if update.message:
                await update.message.reply_text(
                    text=error_text,
                    reply_markup=OperationsKeyboards.operations_menu(),
                    parse_mode="Markdown"
                )
            elif update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    text=error_text,
                    reply_markup=OperationsKeyboards.operations_menu(),
                    parse_mode="Markdown"
                )
            return
            
        user_id = update.effective_user.id
        
        try:
            referral_data = await self.referral_service.get_user_referral_data(user_id, current_user_id=user_id)
            
            # Generar el enlace de referido
            referral_code = referral_data.get("code", "N/A")
            referral_link = f"https://t.me/{settings.BOT_USERNAME}?start={referral_code}"
            
            text = OperationsMessages.Referral.MENU.format(
                bot_username=settings.BOT_USERNAME,
                referral_link=referral_link,
                referral_code=referral_code,
                direct_referrals=referral_data.get("direct_referrals", 0),
                total_earnings=referral_data.get("total_earnings", 0),
                commission=10
            )
            
            # Manejar tanto mensaje como callback
            if update.message:
                await update.message.reply_text(
                    text=text,
                    reply_markup=OperationsKeyboards.referral_actions(),
                    parse_mode="Markdown"
                )
            elif update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    text=text,
                    reply_markup=OperationsKeyboards.referral_actions(),
                    parse_mode="Markdown"
                )
            
        except Exception as e:
            logger.error(f"Error en referidos: {e}")
            error_text = OperationsMessages.Error.SYSTEM_ERROR
            
            if update.message:
                await update.message.reply_text(
                    text=error_text,
                    reply_markup=OperationsKeyboards.operations_menu(),
                    parse_mode="Markdown"
                )
            elif update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    text=error_text,
                    reply_markup=OperationsKeyboards.operations_menu(),
                    parse_mode="Markdown"
                )

    async def back_to_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja el botón 'Volver' para volver al menú principal.
        """
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        is_admin = user.id == int(settings.ADMIN_ID)

        # Import common messages for consistency
        from telegram_bot.common.messages import CommonMessages  # noqa: E402
        from telegram_bot.common.keyboards import CommonKeyboards  # noqa: E402

        await query.edit_message_text(
            text=CommonMessages.Menu.WELCOME_BACK,
            reply_markup=CommonKeyboards.main_menu(is_admin=is_admin),
            parse_mode="Markdown"
        )

    async def operations_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja el callback para volver al menú de operaciones.
        """
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            text=OperationsMessages.Menu.MAIN,
            reply_markup=OperationsKeyboards.operations_menu(),
            parse_mode="Markdown"
        )

    async def show_vip_plans(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra los planes VIP disponibles.
        """
        await update.message.reply_text(
            text=OperationsMessages.VIP.PLANS,
            reply_markup=OperationsKeyboards.vip_plans(),
            parse_mode="Markdown"
        )

    async def show_game_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el menú de juegos.
        """
        await update.message.reply_text(
            text=OperationsMessages.Game.MENU,
            reply_markup=OperationsKeyboards.game_menu(),
            parse_mode="Markdown"
        )

    async def show_transactions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el historial de transacciones.
        """
        user_id = update.effective_user.id
        
        try:
            # Aquí iría la lógica para obtener el historial de transacciones
            # Por ahora mostramos un mensaje placeholder
            
            text = OperationsMessages.Transactions.HISTORY.format(
                user_id=user_id,
                count=0  # Placeholder
            )
            
            await update.message.reply_text(
                text=text,
                reply_markup=OperationsKeyboards.operations_menu(),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_transactions: {e}")
            await update.message.reply_text(
                text=OperationsMessages.Error.SYSTEM_ERROR,
                reply_markup=OperationsKeyboards.operations_menu(),
                parse_mode="Markdown"
            )


def get_operations_handlers(vpn_service: VpnService, referral_service: ReferralService = None):
    """
    Retorna los handlers de operaciones.
    
    Args:
        vpn_service: Servicio de VPN
        referral_service: Servicio de referidos (opcional)
        
    Returns:
        list: Lista de handlers
    """
    handler = OperationsHandler(vpn_service, referral_service)
    
    return [
        MessageHandler(filters.Regex("^💰 Operaciones$"), handler.operations_menu),
        MessageHandler(filters.Regex("^💰 Mi Balance$"), handler.mi_balance),
        CommandHandler("balance", handler.mi_balance),
        MessageHandler(filters.Regex("^👑 Plan VIP$"), handler.show_vip_plans),
        CommandHandler("vip", handler.show_vip_plans),
        MessageHandler(filters.Regex("^🎮 Juega y Gana$"), handler.show_game_menu),
        CommandHandler("game", handler.show_game_menu),
        MessageHandler(filters.Regex("^👥 Referidos$"), handler.referidos),
        CommandHandler("referrals", handler.referidos),
        MessageHandler(filters.Regex("^🔙 Atrás$"), handler.back_to_main_menu),
    ]


def get_operations_callback_handlers(vpn_service: VpnService, referral_service: ReferralService = None):
    """
    Retorna los handlers de callbacks para operaciones.
    
    Args:
        vpn_service: Servicio de VPN
        referral_service: Servicio de referidos (opcional)
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = OperationsHandler(vpn_service, referral_service)
    
    return [
        CallbackQueryHandler(handler.operations_menu_callback, pattern="^operations_menu$"),
        CallbackQueryHandler(handler.operations_menu_callback, pattern="^operations$"),
        CallbackQueryHandler(handler.back_to_main_menu, pattern="^main_menu$"),
        CallbackQueryHandler(handler.mi_balance, pattern="^balance$"),
        CallbackQueryHandler(handler.referidos, pattern="^referrals$"),
        CallbackQueryHandler(handler.show_vip_plans, pattern="^vip_plans$"),
        CallbackQueryHandler(handler.show_game_menu, pattern="^game_menu$"),
        CallbackQueryHandler(handler.show_transactions, pattern="^transactions$"),
        CallbackQueryHandler(handler.show_transactions, pattern="^rewards$"),  # Usar mismo handler para recompensas
    ]
