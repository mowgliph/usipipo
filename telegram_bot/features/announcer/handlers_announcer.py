"""
Handlers para sistema de anuncios de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler, CommandHandler, ConversationHandler
from application.services.announcer_service import AnnouncerService
from application.services.vpn_service import VpnService
from .messages_announcer import AnnouncerMessages
from .keyboards_announcer import AnnouncerKeyboards
from utils.logger import logger
from telegram_bot.common.base_handler import BaseConversationHandler

# Estados de conversación
ANNOUNCER_MENU = 0
CREATING_CAMPAIGN = 1
SELECTING_AUDIENCE = 2
COMPOSING_AD = 3
CONFIRMING_CAMPAIGN = 4


class AnnouncerHandler(BaseConversationHandler):
    """Handler para sistema de anuncios."""

    def __init__(self, announcer_service: AnnouncerService, vpn_service: VpnService = None):
        """
        Inicializa el handler de anuncios.

        Args:
            announcer_service: Servicio de anuncios
            vpn_service: Servicio de VPN (opcional)
        """
        super().__init__(announcer_service, "AnnouncerService")
        self.vpn_service = vpn_service
        logger.info("📢 AnnouncerHandler inicializado")

    async def show_announcer_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el menú principal de anuncios.
        """
        query = update.callback_query
        
        if query:
            await query.answer()
            user_id = update.effective_user.id
        else:
            user_id = update.effective_user.id
        
        try:
            # Verificar si el usuario tiene rol de anunciante
            has_announcer_role = await self._check_announcer_role(user_id)
            
            if not has_announcer_role:
                message = AnnouncerMessages.Error.ANNOUNCER_ROLE_REQUIRED
                keyboard = AnnouncerKeyboards.upgrade_to_announcer()
            else:
                # Obtener estadísticas de campañas
                stats = await self.announcer_service.get_user_campaign_stats(user_id, current_user_id=user_id)
                
                message = AnnouncerMessages.Menu.MAIN.format(
                    total_campaigns=stats.get('total_campaigns', 0),
                    active_campaigns=stats.get('active_campaigns', 0),
                    total_reach=stats.get('total_reach', 0),
                    total_spent=stats.get('total_spent', 0)
                )
                keyboard = AnnouncerKeyboards.main_menu()
            
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
            
            return ANNOUNCER_MENU
            
        except Exception as e:
            logger.error(f"Error en show_announcer_menu: {e}")
            await self._show_error(update, context)
            return ConversationHandler.END

    async def create_campaign(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el formulario para crear campaña.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = AnnouncerMessages.Campaign.CREATE_FORM
            keyboard = AnnouncerKeyboards.create_campaign_form()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return CREATING_CAMPAIGN
            
        except Exception as e:
            logger.error(f"Error en create_campaign: {e}")
            await query.edit_message_text(
                text=AnnouncerMessages.Error.SYSTEM_ERROR,
                reply_markup=AnnouncerKeyboards.back_to_announcer(),
                parse_mode="Markdown"
            )
            return ANNOUNCER_MENU

    async def select_audience(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra opciones de audiencia para la campaña.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = AnnouncerMessages.Audience.SELECTION
            keyboard = AnnouncerKeyboards.audience_selection()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return SELECTING_AUDIENCE
            
        except Exception as e:
            logger.error(f"Error en select_audience: {e}")
            await query.edit_message_text(
                text=AnnouncerMessages.Error.SYSTEM_ERROR,
                reply_markup=AnnouncerKeyboards.back_to_announcer(),
                parse_mode="Markdown"
            )
            return CREATING_CAMPAIGN

    async def compose_ad(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el compositor de anuncios.
        """
        query = update.callback_query
        await query.answer()
        
        audience = query.data.replace("audience_", "")
        context.user_data['campaign_audience'] = audience
        
        try:
            message = AnnouncerMessages.Ad.COMPOSE_TEMPLATE.format(
                audience=audience.title()
            )
            keyboard = AnnouncerKeyboards.compose_ad_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return COMPOSING_AD
            
        except Exception as e:
            logger.error(f"Error en compose_ad: {e}")
            await query.edit_message_text(
                text=AnnouncerMessages.Error.SYSTEM_ERROR,
                reply_markup=AnnouncerKeyboards.back_to_announcer(),
                parse_mode="Markdown"
            )
            return SELECTING_AUDIENCE

    async def confirm_campaign(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra confirmación de campaña.
        """
        query = update.callback_query
        await query.answer()
        
        # Extraer información del contexto
        campaign_name = context.user_data.get('campaign_name', 'Sin nombre')
        campaign_audience = context.user_data.get('campaign_audience', 'all')
        ad_content = context.user_data.get('ad_content', '')
        budget = context.user_data.get('campaign_budget', 0)
        
        try:
            # Obtener estadísticas de audiencia
            audience_stats = await self.announcer_service.get_audience_stats(campaign_audience, current_user_id=user_id)
            
            message = AnnouncerMessages.Campaign.CONFIRMATION.format(
                name=campaign_name,
                audience=campaign_audience.title(),
                budget=budget,
                estimated_reach=audience_stats['estimated_reach'],
                cost_per_impression=budget / audience_stats['estimated_reach'] if audience_stats['estimated_reach'] > 0 else 0,
                ad_preview=ad_content[:100] + "..." if len(ad_content) > 100 else ad_content
            )
            
            keyboard = AnnouncerKeyboards.confirm_campaign()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return CONFIRMING_CAMPAIGN
            
        except Exception as e:
            logger.error(f"Error en confirm_campaign: {e}")
            await query.edit_message_text(
                text=AnnouncerMessages.Error.SYSTEM_ERROR,
                reply_markup=AnnouncerKeyboards.back_to_announcer(),
                parse_mode="Markdown"
            )
            return COMPOSING_AD

    async def launch_campaign(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Lanza la campaña de anuncios.
        """
        query = update.callback_query
        await query.answer()
        
        campaign_data = {
            'name': context.user_data.get('campaign_name', 'Sin nombre'),
            'audience': context.user_data.get('campaign_audience', 'all'),
            'content': context.user_data.get('ad_content', ''),
            'budget': context.user_data.get('campaign_budget', 0),
            'user_id': update.effective_user.id
        }
        
        try:
            # Lanzar campaña
            result = await self.announcer_service.create_campaign(campaign_data, current_user_id=user_id)
            
            if result['success']:
                message = AnnouncerMessages.Campaign.LAUNCH_SUCCESS.format(
                    name=result['campaign_name'],
                    campaign_id=result['campaign_id'],
                    estimated_reach=result['estimated_reach'],
                    start_date=result['start_date']
                )
                keyboard = AnnouncerKeyboards.campaign_success()
            else:
                message = AnnouncerMessages.Error.CAMPAIGN_FAILED.format(
                    error=result.get('error', 'Unknown error')
                )
                keyboard = AnnouncerKeyboards.back_to_announcer()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            # Limpiar contexto
            context.user_data.clear()
            
        except Exception as e:
            logger.error(f"Error en launch_campaign: {e}")
            await query.edit_message_text(
                text=AnnouncerMessages.Error.SYSTEM_ERROR,
                reply_markup=AnnouncerKeyboards.back_to_announcer(),
                parse_mode="Markdown"
            )

    async def show_campaign_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra la lista de campañas del usuario.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Obtener campañas del usuario
            campaigns = await self.announcer_service.get_user_campaigns(user_id, current_user_id=user_id)
            
            if not campaigns:
                message = AnnouncerMessages.Campaign.NO_CAMPAIGNS
                keyboard = AnnouncerKeyboards.back_to_announcer()
            else:
                message = AnnouncerMessages.Campaign.LIST_HEADER
                
                for campaign in campaigns[:10]:  # Mostrar solo primeros 10
                    status = "🟢 Activa" if campaign['status'] == 'active' else "⏸️ Pausada" if campaign['status'] == 'paused' else "🔴 Finalizada"
                    message += f"\n{status} {campaign['name']}\n"
                    message += f"   📊 Alcance: {campaign['reach']:,}\n"
                    message += f"   💰 Presupuesto: ${campaign['budget']:.2f}\n"
                    message += f"   📅 {campaign['created_at']}\n"
                
                if len(campaigns) > 10:
                    message += f"\n📊 ... y {len(campaigns) - 10} más"
                
                keyboard = AnnouncerKeyboards.campaign_actions(len(campaigns))
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_campaign_list: {e}")
            await query.edit_message_text(
                text=AnnouncerMessages.Error.SYSTEM_ERROR,
                reply_markup=AnnouncerKeyboards.back_to_announcer(),
                parse_mode="Markdown"
            )

    async def show_campaign_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra estadísticas de campañas.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Obtener estadísticas generales
            stats = await self.announcer_service.get_user_campaign_stats(user_id, current_user_id=user_id)
            
            message = AnnouncerMessages.Stats.CAMPAIGN_STATS.format(
                total_campaigns=stats.get('total_campaigns', 0),
                active_campaigns=stats.get('active_campaigns', 0),
                total_reach=stats.get('total_reach', 0),
                total_spent=stats.get('total_spent', 0),
                avg_ctr=stats.get('avg_ctr', 0),
                avg_cpc=stats.get('avg_cpc', 0)
            )
            
            keyboard = AnnouncerKeyboards.stats_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_campaign_stats: {e}")
            await query.edit_message_text(
                text=AnnouncerMessages.Error.SYSTEM_ERROR,
                reply_markup=AnnouncerKeyboards.back_to_announcer(),
                parse_mode="Markdown"
            )

    async def show_ad_templates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra plantillas de anuncios.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            # Obtener plantillas disponibles
            templates = await self.announcer_service.get_ad_templates(current_user_id=user_id)
            
            if not templates:
                message = AnnouncerMessages.Templates.NO_TEMPLATES
                keyboard = AnnouncerKeyboards.back_to_announcer()
            else:
                message = AnnouncerMessages.Templates.LIST_HEADER
                
                for template in templates:
                    message += f"\n📋 {template['name']}\n"
                    message += f"   📝 {template['description']}\n"
                    message += f"   🎯 Tipo: {template['type']}\n"
                    message += f"   💰 Costo sugerido: ${template['suggested_budget']}\n"
                
                keyboard = AnnouncerKeyboards.template_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_ad_templates: {e}")
            await query.edit_message_text(
                text=AnnouncerMessages.Error.SYSTEM_ERROR,
                reply_markup=AnnouncerKeyboards.back_to_announcer(),
                parse_mode="Markdown"
            )

    async def back_to_announcer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Vuelve al menú principal de anuncios.
        """
        return await self.show_announcer_menu(update, context)
    
    async def back_to_operations(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Vuelve al menú de operaciones.
        """
        query = update.callback_query
        await query.answer()
        
        message = "🔙 Volviendo al menú principal..."
        keyboard = None  # Aquí iría el teclado del menú principal
        
        await query.edit_message_text(
            text=message,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        return ConversationHandler.END

    # Métodos privados
    async def _check_announcer_role(self, user_id: int) -> bool:
        """Verifica si el usuario tiene rol de anunciante."""
        try:
            # Aquí iría la lógica real para verificar rol de anunciante
            # Por ahora, simulamos la verificación
            if self.vpn_service:
                user_status = await self.vpn_service.get_user_status(user_id, current_user_id=user_id)
                user = user_status.get("user")
                return user.has_announcer_role if user else False
            return False
        except Exception as e:
            logger.error(f"Error verificando rol de anunciante: {e}")
            return False

    async def _show_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra error genérico."""
        message = AnnouncerMessages.Error.SYSTEM_ERROR
        keyboard = AnnouncerKeyboards.back_to_operations()
        
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
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


def get_announcer_handlers(announcer_service: AnnouncerService, vpn_service: VpnService = None):
    """
    Retorna los handlers de anuncios.
    
    Args:
        announcer_service: Servicio de anuncios
        vpn_service: (opcional) Servicio de VPN
        
    Returns:
        list: Lista de handlers
    """
    handler = AnnouncerHandler(announcer_service, vpn_service)
    
    return [
        MessageHandler(filters.Regex("^📢 Anuncios$"), handler.show_announcer_menu),
        CommandHandler("announcer", handler.show_announcer_menu),
    ]


def get_announcer_callback_handlers(announcer_service: AnnouncerService, vpn_service: VpnService = None):
    """
    Retorna los handlers de callbacks de anuncios.
    
    Args:
        announcer_service: Servicio de anuncios
        vpn_service: (opcional) Servicio de VPN
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = AnnouncerHandler(announcer_service, vpn_service)
    
    return [
        CallbackQueryHandler(handler.create_campaign, pattern="^create_campaign$"),
        CallbackQueryHandler(handler.select_audience, pattern="^select_audience_"),
        CallbackQueryHandler(handler.compose_ad, pattern="^compose_ad_"),
        CallbackQueryHandler(handler.confirm_campaign, pattern="^confirm_campaign$"),
        CallbackQueryHandler(handler.launch_campaign, pattern="^launch_campaign$"),
        CallbackQueryHandler(handler.show_campaign_list, pattern="^campaign_list$"),
        CallbackQueryHandler(handler.show_campaign_stats, pattern="^campaign_stats$"),
        CallbackQueryHandler(handler.show_ad_templates, pattern="^ad_templates$"),
    ]


def get_announcer_conversation_handler(announcer_service: AnnouncerService, vpn_service: VpnService = None) -> ConversationHandler:
    """
    Retorna el ConversationHandler para anuncios.
    
    Args:
        announcer_service: Servicio de anuncios
        vpn_service: (opcional) Servicio de VPN
        
    Returns:
        ConversationHandler: Handler configurado
    """
    handler = AnnouncerHandler(announcer_service, vpn_service)
    
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📢 Anuncios$"), handler.show_announcer_menu),
            CommandHandler("announcer", handler.show_announcer_menu),
        ],
        states={
            ANNOUNCER_MENU: [
                CallbackQueryHandler(handler.create_campaign, pattern="^create_campaign$"),
                CallbackQueryHandler(handler.show_campaign_list, pattern="^campaign_list$"),
                CallbackQueryHandler(handler.show_campaign_stats, pattern="^campaign_stats$"),
                CallbackQueryHandler(handler.show_ad_templates, pattern="^ad_templates$"),
                CallbackQueryHandler(handler.back_to_operations, pattern="^back_to_operations$"),
            ],
            CREATING_CAMPAIGN: [
                CallbackQueryHandler(handler.select_audience, pattern="^select_audience_"),
                CallbackQueryHandler(handler.back_to_announcer, pattern="^back_to_announcer$"),
            ],
            SELECTING_AUDIENCE: [
                CallbackQueryHandler(handler.compose_ad, pattern="^compose_ad_"),
                CallbackQueryHandler(handler.back_to_announcer, pattern="^back_to_announcer$"),
            ],
            COMPOSING_AD: [
                CallbackQueryHandler(handler.confirm_campaign, pattern="^confirm_campaign$"),
                CallbackQueryHandler(handler.back_to_announcer, pattern="^back_to_announcer$"),
            ],
            CONFIRMING_CAMPAIGN: [
                CallbackQueryHandler(handler.launch_campaign, pattern="^launch_campaign$"),
                CallbackQueryHandler(handler.back_to_announcer, pattern="^back_to_announcer$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handler.show_announcer_menu),
            CallbackQueryHandler(handler.back_to_announcer, pattern="^back_to_announcer$"),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )
