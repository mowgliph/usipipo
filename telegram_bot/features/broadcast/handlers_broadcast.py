"""
Handlers para sistema de difusión masiva de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler, CommandHandler, ConversationHandler
from application.services.broadcast_service import BroadcastService
from .messages_broadcast import BroadcastMessages
from .keyboards_broadcast import BroadcastKeyboards
from config import settings
from utils.logger import logger

# Estados de conversación
BROADCAST_MENU = 0
SELECTING_TYPE = 1
COMPOSING_MESSAGE = 2
SELECTING_AUDIENCE = 3
CONFIRMING_SEND = 4


class BroadcastHandler:
    """Handler para sistema de difusión masiva."""
    
    def __init__(self, broadcast_service: BroadcastService):
        """
        Inicializa el handler de broadcast.
        
        Args:
            broadcast_service: Servicio de broadcast
        """
        self.broadcast_service = broadcast_service
        logger.info("📢 BroadcastHandler inicializado")

    async def show_broadcast_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el menú principal de broadcast.
        """
        query = update.callback_query
        
        if query:
            await query.answer()
            user_id = update.effective_user.id
        else:
            user_id = update.effective_user.id
        
        # Verificar si es admin
        if user_id != int(settings.ADMIN_ID):
            await self._show_admin_only_error(update, context)
            return ConversationHandler.END
        
        try:
            message = BroadcastMessages.Menu.MAIN
            keyboard = BroadcastKeyboards.main_menu()
            
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
            
            return BROADCAST_MENU
            
        except Exception as e:
            logger.error(f"Error en show_broadcast_menu: {e}")
            await self._show_error(update, context)
            return ConversationHandler.END

    async def select_broadcast_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra opciones de tipo de broadcast.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = BroadcastMessages.Type.SELECTION
            keyboard = BroadcastKeyboards.type_selection()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return SELECTING_TYPE
            
        except Exception as e:
            logger.error(f"Error en select_broadcast_type: {e}")
            await query.edit_message_text(
                text=BroadcastMessages.Error.SYSTEM_ERROR,
                reply_markup=BroadcastKeyboards.back_to_broadcast(),
                parse_mode="Markdown"
            )
            return BROADCAST_MENU

    async def compose_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el compositor de mensajes.
        """
        query = update.callback_query
        await query.answer()
        
        broadcast_type = query.data.replace("compose_", "")
        
        try:
            message = BroadcastMessages.Compose.TEMPLATE.format(
                type=broadcast_type.title()
            )
            keyboard = BroadcastKeyboards.compose_actions(broadcast_type)
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return COMPOSING_MESSAGE
            
        except Exception as e:
            logger.error(f"Error en compose_message: {e}")
            await query.edit_message_text(
                text=BroadcastMessages.Error.SYSTEM_ERROR,
                reply_markup=BroadcastKeyboards.back_to_broadcast(),
                parse_mode="Markdown"
            )
            return SELECTING_TYPE

    async def select_audience(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra opciones de audiencia.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = BroadcastMessages.Audience.SELECTION
            keyboard = BroadcastKeyboards.audience_selection()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return SELECTING_AUDIENCE
            
        except Exception as e:
            logger.error(f"Error en select_audience: {e}")
            await query.edit_message_text(
                text=BroadcastMessages.Error.SYSTEM_ERROR,
                reply_markup=BroadcastKeyboards.back_to_broadcast(),
                parse_mode="Markdown"
            )
            return COMPOSING_MESSAGE

    async def confirm_send(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra confirmación de envío.
        """
        query = update.callback_query
        await query.answer()
        
        # Extraer información del contexto
        message_content = context.user_data.get('broadcast_message', '')
        audience = context.user_data.get('broadcast_audience', 'all')
        broadcast_type = context.user_data.get('broadcast_type', 'general')
        
        try:
            # Obtener estadísticas de audiencia
            audience_stats = await self.broadcast_service.get_audience_stats(audience, current_user_id=user_id)
            
            message = BroadcastMessages.Confirmation.SEND_CONFIRMATION.format(
                type=broadcast_type.title(),
                audience=audience.title(),
                message_preview=message_content[:100] + "..." if len(message_content) > 100 else message_content,
                audience_size=audience_stats['total_users'],
                active_users=audience_stats['active_users'],
                estimated_reach=audience_stats['estimated_reach']
            )
            
            keyboard = BroadcastKeyboards.confirm_send()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return CONFIRMING_SEND
            
        except Exception as e:
            logger.error(f"Error en confirm_send: {e}")
            await query.edit_message_text(
                text=BroadcastMessages.Error.SYSTEM_ERROR,
                reply_markup=BroadcastKeyboards.back_to_broadcast(),
                parse_mode="Markdown"
            )
            return SELECTING_AUDIENCE

    async def send_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Envía el broadcast.
        """
        query = update.callback_query
        await query.answer()
        
        message_content = context.user_data.get('broadcast_message', '')
        audience = context.user_data.get('broadcast_audience', 'all')
        broadcast_type = context.user_data.get('broadcast_type', 'general')
        
        try:
            # Enviar broadcast
            result = await self.broadcast_service.send_broadcast(
                message=message_content,
                audience=audience,
                broadcast_type=broadcast_type,
                admin_id=update.effective_user.id,
                current_user_id=update.effective_user.id
            )
            
            if result['success']:
                message = BroadcastMessages.Success.SENT_SUCCESS.format(
                    type=broadcast_type.title(),
                    audience=audience.title(),
                    sent_count=result['sent_count'],
                    failed_count=result['failed_count'],
                    message_id=result['message_id']
                )
                keyboard = BroadcastKeyboards.broadcast_success()
            else:
                message = BroadcastMessages.Error.SEND_FAILED.format(
                    error=result.get('error', 'Unknown error')
                )
                keyboard = BroadcastKeyboards.back_to_broadcast()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            # Limpiar contexto
            context.user_data.clear()
            
        except Exception as e:
            logger.error(f"Error en send_broadcast: {e}")
            await query.edit_message_text(
                text=BroadcastMessages.Error.SYSTEM_ERROR,
                reply_markup=BroadcastKeyboards.back_to_broadcast(),
                parse_mode="Markdown"
            )

    async def show_broadcast_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el historial de broadcasts.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            # Obtener historial de broadcasts
            history = await self.broadcast_service.get_broadcast_history(limit=10, current_user_id=user_id)
            
            if not history:
                message = BroadcastMessages.History.NO_HISTORY
                keyboard = BroadcastKeyboards.back_to_broadcast()
            else:
                message = BroadcastMessages.History.HEADER
                
                for broadcast in history:
                    status = "✅ Enviado" if broadcast['status'] == 'sent' else "⏳ Pendiente"
                    message += f"\n{status} {broadcast['type'].title()}\n"
                    message += f"   📅 {broadcast['created_at']}\n"
                    message += f"   👥 Audiencia: {broadcast['audience'].title()}\n"
                    message += f"   📊 Enviados: {broadcast['sent_count']}\n"
                    message += f"   🆔 ID: {broadcast['id']}\n"
                
                keyboard = BroadcastKeyboards.history_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_broadcast_history: {e}")
            await query.edit_message_text(
                text=BroadcastMessages.Error.SYSTEM_ERROR,
                reply_markup=BroadcastKeyboards.back_to_broadcast(),
                parse_mode="Markdown"
            )

    async def show_broadcast_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra estadísticas de broadcasts.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            # Obtener estadísticas generales
            stats = await self.broadcast_service.get_broadcast_stats(current_user_id=user_id)
            
            message = BroadcastMessages.Stats.GENERAL_STATS.format(
                total_broadcasts=stats.get('total_broadcasts', 0),
                total_sent=stats.get('total_sent', 0),
                total_failed=stats.get('total_failed', 0),
                success_rate=stats.get('success_rate', 0),
                total_reach=stats.get('total_reach', 0),
                avg_engagement=stats.get('avg_engagement', 0)
            )
            
            keyboard = BroadcastKeyboards.stats_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_broadcast_stats: {e}")
            await query.edit_message_text(
                text=BroadcastMessages.Error.SYSTEM_ERROR,
                reply_markup=BroadcastKeyboards.back_to_broadcast(),
                parse_mode="Markdown"
            )

    async def show_templates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra plantillas de mensajes.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            # Obtener plantillas disponibles
            templates = await self.broadcast_service.get_broadcast_templates(current_user_id=user_id)
            
            if not templates:
                message = BroadcastMessages.Templates.NO_TEMPLATES
                keyboard = BroadcastKeyboards.back_to_broadcast()
            else:
                message = BroadcastMessages.Templates.LIST_HEADER
                
                for template in templates:
                    message += f"\n📋 {template['name']}\n"
                    message += f"   📝 {template['description']}\n"
                    message += f"   🎯 Tipo: {template['type']}\n"
                
                keyboard = BroadcastKeyboards.template_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_templates: {e}")
            await query.edit_message_text(
                text=BroadcastMessages.Error.SYSTEM_ERROR,
                reply_markup=BroadcastKeyboards.back_to_broadcast(),
                parse_mode="Markdown"
            )

    # Métodos privados
    async def _show_admin_only_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra error de permisos."""
        message = BroadcastMessages.Error.ADMIN_ONLY
        keyboard = BroadcastKeyboards.back_to_operations()
        
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

    async def _show_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra error genérico."""
        message = BroadcastMessages.Error.SYSTEM_ERROR
        keyboard = BroadcastKeyboards.back_to_operations()
        
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


def get_broadcast_handlers(broadcast_service):
    """
    Retorna los handlers de broadcast.
    
    Args:
        broadcast_service: Servicio de broadcast
        
    Returns:
        list: Lista de handlers
    """
    handler = BroadcastHandler(broadcast_service)
    
    return [
        MessageHandler(filters.Regex("^📢 Broadcast$"), handler.show_broadcast_menu),
        CommandHandler("broadcast", handler.show_broadcast_menu),
    ]


def get_broadcast_callback_handlers(broadcast_service):
    """
    Retorna los handlers de callbacks de broadcast.
    
    Args:
        broadcast_service: Servicio de broadcast
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = BroadcastHandler(broadcast_service)
    
    return [
        CallbackQueryHandler(handler.select_broadcast_type, pattern="^select_type_"),
        CallbackQueryHandler(handler.compose_message, pattern="^compose_"),
        CallbackQueryHandler(handler.select_audience, pattern="^select_audience_"),
        CallbackQueryHandler(handler.confirm_send, pattern="^confirm_send$"),
        CallbackQueryHandler(handler.send_broadcast, pattern="^send_broadcast$"),
        CallbackQueryHandler(handler.show_broadcast_history, pattern="^broadcast_history$"),
        CallbackQueryHandler(handler.show_broadcast_stats, pattern="^broadcast_stats$"),
        CallbackQueryHandler(handler.show_templates, pattern="^broadcast_templates$"),
    ]


def get_broadcast_conversation_handler(broadcast_service) -> ConversationHandler:
    """
    Retorna el ConversationHandler para broadcast.
    
    Args:
        broadcast_service: Servicio de broadcast
        
    Returns:
        ConversationHandler: Handler configurado
    """
    handler = BroadcastHandler(broadcast_service)
    
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📢 Broadcast$"), handler.show_broadcast_menu),
            CommandHandler("broadcast", handler.show_broadcast_menu),
        ],
        states={
            BROADCAST_MENU: [
                CallbackQueryHandler(handler.select_broadcast_type, pattern="^select_type_"),
                CallbackQueryHandler(handler.show_broadcast_history, pattern="^broadcast_history$"),
                CallbackQueryHandler(handler.show_broadcast_stats, pattern="^broadcast_stats$"),
                CallbackQueryHandler(handler.show_templates, pattern="^broadcast_templates$"),
                CallbackQueryHandler(handler.back_to_operations, pattern="^back_to_operations$"),
            ],
            SELECTING_TYPE: [
                CallbackQueryHandler(handler.compose_message, pattern="^compose_"),
                CallbackQueryHandler(handler.back_to_broadcast, pattern="^back_to_broadcast$"),
            ],
            COMPOSING_MESSAGE: [
                CallbackQueryHandler(handler.select_audience, pattern="^select_audience_"),
                CallbackQueryHandler(handler.back_to_broadcast, pattern="^back_to_broadcast$"),
            ],
            SELECTING_AUDIENCE: [
                CallbackQueryHandler(handler.confirm_send, pattern="^confirm_send$"),
                CallbackQueryHandler(handler.back_to_broadcast, pattern="^back_to_broadcast$"),
            ],
            CONFIRMING_SEND: [
                CallbackQueryHandler(handler.send_broadcast, pattern="^send_broadcast$"),
                CallbackQueryHandler(handler.back_to_broadcast, pattern="^back_to_broadcast$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handler.show_broadcast_menu),
            CallbackQueryHandler(handler.back_to_broadcast, pattern="^back_to_broadcast$"),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )
