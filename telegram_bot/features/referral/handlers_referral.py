"""
Handlers para sistema de referidos de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler, CommandHandler, ConversationHandler
from application.services.referral_service import ReferralService
from application.services.vpn_service import VpnService
from .messages_referral import ReferralMessages
from .keyboards_referral import ReferralKeyboards
from config import settings
from utils.logger import logger

# Estados de conversación para referidos
APPLY_REFERRAL = range(1)
REFERRAL_MENU = 0


class ReferralHandler:
    """Handler para sistema de referidos."""
    
    def __init__(self, referral_service: ReferralService, vpn_service: VpnService = None):
        """
        Inicializa el handler de referidos.
        
        Args:
            referral_service: Servicio de referidos
            vpn_service: Servicio de VPN (opcional)
        """
        self.referral_service = referral_service
        self.vpn_service = vpn_service
        logger.info("👥 ReferralHandler inicializado")

    async def show_referral_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el menú principal de referidos.
        """
        query = update.callback_query
        
        if query:
            await query.answer()
            user_id = update.effective_user.id
        else:
            user_id = update.effective_user.id
        
        try:
            # Obtener datos de referidos
            referral_data = await self.referral_service.get_user_referral_data(user_id)
            
            # Generar el enlace de referido
            referral_code = referral_data.get("code", "N/A")
            referral_link = f"https://t.me/{settings.BOT_USERNAME}?start={referral_code}"
            
            message = ReferralMessages.Menu.MAIN.format(
                bot_username=settings.BOT_USERNAME,
                referral_link=referral_link,
                referral_code=referral_code,
                direct_referrals=referral_data.get("direct_referrals", 0),
                total_earnings=referral_data.get("total_earnings", 0),
                commission=10
            )
            
            keyboard = ReferralKeyboards.main_menu()
            
            if query:
                await query.edit_message_text(
                    text=message,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    text=message,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            
            return REFERRAL_MENU
            
        except Exception as e:
            logger.error(f"Error en show_referral_menu: {e}")
            error_message = ReferralMessages.Error.SYSTEM_ERROR
            
            if query:
                await query.edit_message_text(
                    text=error_message,
                    reply_markup=ReferralKeyboards.back_to_operations(),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    text=error_message,
                    reply_markup=ReferralKeyboards.back_to_operations(),
                    parse_mode="Markdown"
                )
            
            return ConversationHandler.END

    async def show_referral_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra estadísticas detalladas de referidos.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            referral_data = await self.referral_service.get_user_referral_data(user_id)
            referrals = await self.referral_service.get_referrals(user_id)
            
            # Calcular estadísticas adicionales
            active_referrals = len([r for r in referrals if r.is_active])
            pending_referrals = len([r for r in referrals if not r.is_active])
            monthly_earnings = await self._calculate_monthly_earnings(user_id)
            
            message = ReferralMessages.Stats.DETAILED.format(
                total_referrals=len(referrals),
                active_referrals=active_referrals,
                pending_referrals=pending_referrals,
                total_earnings=referral_data.get("total_earnings", 0),
                monthly_earnings=monthly_earnings,
                commission_rate=10,
                referral_code=referral_data.get("code", "N/A")
            )
            
            keyboard = ReferralKeyboards.stats_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_referral_stats: {e}")
            await query.edit_message_text(
                text=ReferralMessages.Error.SYSTEM_ERROR,
                reply_markup=ReferralKeyboards.back_to_referral(),
                parse_mode="Markdown"
            )

    async def show_referral_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra la lista de referidos.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            referrals = await self.referral_service.get_referrals(user_id)
            
            if not referrals:
                message = ReferralMessages.List.NO_REFERRALS
                keyboard = ReferralKeyboards.back_to_referral()
            else:
                message = ReferralMessages.List.HEADER
                
                for i, referral in enumerate(referrals[:10], 1):  # Mostrar solo primeros 10
                    status = "🟢 Activo" if referral.is_active else "🔴 Pendiente"
                    message += f"\n{i}. 👤 {referral.username or 'Usuario ' + str(referral.telegram_id)}\n"
                    message += f"   📅 {referral.created_at.strftime('%d/%m/%Y')}\n"
                    message += f"   {status}\n"
                
                if len(referrals) > 10:
                    message += f"\n📊 ... y {len(referrals) - 10} más"
                
                keyboard = ReferralKeyboards.list_actions(len(referrals))
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_referral_list: {e}")
            await query.edit_message_text(
                text=ReferralMessages.Error.SYSTEM_ERROR,
                reply_markup=ReferralKeyboards.back_to_referral(),
                parse_mode="Markdown"
            )

    async def share_referral_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Comparte el enlace de referido.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            referral_data = await self.referral_service.get_user_referral_data(user_id)
            referral_code = referral_data.get("code", "N/A")
            referral_link = f"https://t.me/{settings.BOT_USERNAME}?start={referral_code}"
            
            message = ReferralMessages.Share.LINK.format(
                referral_link=referral_link,
                referral_code=referral_code,
                commission=10
            )
            
            keyboard = ReferralKeyboards.share_actions(referral_link)
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en share_referral_link: {e}")
            await query.edit_message_text(
                text=ReferralMessages.Error.SYSTEM_ERROR,
                reply_markup=ReferralKeyboards.back_to_referral(),
                parse_mode="Markdown"
            )

    async def show_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el leaderboard de referidos.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            # Obtener leaderboard
            leaderboard = await self.referral_service.get_leaderboard(limit=10)
            user_id = update.effective_user.id
            user_rank = await self.referral_service.get_user_rank(user_id)
            
            message = ReferralMessages.Leaderboard.MAIN.format(
                user_rank=user_rank,
                user_id=user_id
            )
            
            for i, user in enumerate(leaderboard, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                message += f"\n{medal} 👤 {user.username or 'Usuario ' + str(user.telegram_id)}\n"
                message += f"   👥 {user.referral_count} referidos\n"
                message += f"   💰 ${user.earnings:.2f} ganados\n"
            
            keyboard = ReferralKeyboards.leaderboard_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_leaderboard: {e}")
            await query.edit_message_text(
                text=ReferralMessages.Error.SYSTEM_ERROR,
                reply_markup=ReferralKeyboards.back_to_referral(),
                parse_mode="Markdown"
            )

    async def apply_referral_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja la aplicación de código de referido.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = ReferralMessages.Apply.INPUT_CODE
            keyboard = ReferralKeyboards.back_to_referral()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return APPLY_REFERRAL
            
        except Exception as e:
            logger.error(f"Error en apply_referral_code: {e}")
            await query.edit_message_text(
                text=ReferralMessages.Error.SYSTEM_ERROR,
                reply_markup=ReferralKeyboards.back_to_referral(),
                parse_mode="Markdown"
            )

    async def show_earnings_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el historial de ganancias.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Obtener historial de ganancias
            earnings_history = await self.referral_service.get_earnings_history(user_id)
            
            if not earnings_history:
                message = ReferralMessages.Earnings.NO_EARNINGS
                keyboard = ReferralKeyboards.back_to_referral()
            else:
                message = ReferralMessages.Earnings.HISTORY_HEADER
                
                for earning in earnings_history[:10]:  # Mostrar solo primeros 10
                    message += f"\n💰 ${earning.amount:.2f}\n"
                    message += f"   👤 De: {earning.referral_username or 'Usuario ' + str(earning.referral_id)}\n"
                    message += f"   📅 {earning.created_at.strftime('%d/%m/%Y %H:%M')}\n"
                    message += f"   📝 {earning.description}\n"
                
                if len(earnings_history) > 10:
                    message += f"\n📊 ... y {len(earnings_history) - 10} más"
                
                keyboard = ReferralKeyboards.earnings_actions(len(earnings_history))
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_earnings_history: {e}")
            await query.edit_message_text(
                text=ReferralMessages.Error.SYSTEM_ERROR,
                reply_markup=ReferralKeyboards.back_to_referral(),
                parse_mode="Markdown"
            )

    async def show_referral_tips(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra consejos para referidos.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = ReferralMessages.Tips.MAIN
            keyboard = ReferralKeyboards.tips_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_referral_tips: {e}")
            await query.edit_message_text(
                text=ReferralMessages.Error.SYSTEM_ERROR,
                reply_markup=ReferralKeyboards.back_to_referral(),
                parse_mode="Markdown"
            )

    # Métodos privados
    async def _calculate_monthly_earnings(self, user_id: int) -> float:
        """Calcula las ganancias mensuales del usuario."""
        try:
            # Aquí iría la lógica real para calcular ganancias mensuales
            # Por ahora, simulamos el cálculo
            earnings = await self.referral_service.get_referral_earnings(user_id)
            return earnings * 0.3  # Simulación: 30% del total es mensual
        except Exception as e:
            logger.error(f"Error calculando ganancias mensuales: {e}")
            return 0.0


def get_referral_handlers(referral_service: ReferralService, vpn_service: VpnService = None):
    """
    Retorna los handlers de referidos.
    
    Args:
        referral_service: Servicio de referidos
        vpn_service: Servicio de VPN (opcional)
        
    Returns:
        list: Lista de handlers
    """
    handler = ReferralHandler(referral_service, vpn_service)
    
    return [
        MessageHandler(filters.Regex("^👥 Referidos$"), handler.show_referral_menu),
        CommandHandler("referrals", handler.show_referral_menu),
    ]


def get_referral_callback_handlers(referral_service: ReferralService, vpn_service: VpnService = None):
    """
    Retorna los handlers de callbacks de referidos.
    
    Args:
        referral_service: Servicio de referidos
        vpn_service: Servicio de VPN (opcional)
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = ReferralHandler(referral_service, vpn_service)
    
    return [
        CallbackQueryHandler(handler.show_referral_stats, pattern="^referral_stats$"),
        CallbackQueryHandler(handler.show_referral_list, pattern="^referral_list$"),
        CallbackQueryHandler(handler.share_referral_link, pattern="^referral_share$"),
        CallbackQueryHandler(handler.show_leaderboard, pattern="^referral_leaderboard$"),
        CallbackQueryHandler(handler.apply_referral_code, pattern="^referral_apply$"),
        CallbackQueryHandler(handler.show_earnings_history, pattern="^referral_earnings$"),
        CallbackQueryHandler(handler.show_referral_tips, pattern="^referral_tips$"),
    ]


def get_referral_conversation_handler(referral_service: ReferralService, vpn_service: VpnService = None) -> ConversationHandler:
    """
    Retorna el ConversationHandler para referidos.
    
    Args:
        referral_service: Servicio de referidos
        vpn_service: Servicio de VPN (opcional)
        
    Returns:
        ConversationHandler: Handler configurado
    """
    handler = ReferralHandler(referral_service, vpn_service)
    
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^👥 Referidos$"), handler.show_referral_menu),
            CommandHandler("referrals", handler.show_referral_menu),
        ],
        states={
            REFERRAL_MENU: [
                CallbackQueryHandler(handler.show_referral_stats, pattern="^referral_stats$"),
                CallbackQueryHandler(handler.show_referral_list, pattern="^referral_list$"),
                CallbackQueryHandler(handler.share_referral_link, pattern="^referral_share$"),
                CallbackQueryHandler(handler.show_leaderboard, pattern="^referral_leaderboard$"),
                CallbackQueryHandler(handler.apply_referral_code, pattern="^referral_apply$"),
                CallbackQueryHandler(handler.show_earnings_history, pattern="^referral_earnings$"),
                CallbackQueryHandler(handler.show_referral_tips, pattern="^referral_tips$"),
            ],
            APPLY_REFERRAL: [
                # Aquí iría el handler para procesar el código de referido
                CallbackQueryHandler(handler.show_referral_menu, pattern="^referral_back$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handler.show_referral_menu),
            CallbackQueryHandler(handler.show_referral_menu, pattern="^referral_back$"),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )
