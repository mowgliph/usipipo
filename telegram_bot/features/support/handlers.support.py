"""
Handlers para sistema de soporte técnico de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from application.services.support_service import SupportService
from .messages.support import SupportMessages
from .keyboards.support import SupportKeyboards
from config import settings
from utils.logger import logger

# Estado de la conversación
CHATTING = 1


class SupportHandler:
    """Handler para sistema de soporte técnico."""
    
    def __init__(self, support_service: SupportService):
        """
        Inicializa el handler de soporte.
        
        Args:
            support_service: Servicio de soporte
        """
        self.support_service = support_service
        logger.info("🎧 SupportHandler inicializado")

    async def start_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Abre el canal de soporte y registra el ticket en la BD."""
        user = update.effective_user
        
        try:
            # Registrar o recuperar ticket abierto en Infraestructura
            await self.support_service.open_ticket(user_id=user.id, user_name=user.first_name)
            
            # Notificar al Admin con un mensaje que incluya el ID del usuario para facilitar el reply
            await context.bot.send_message(
                chat_id=settings.ADMIN_ID,
                text=SupportMessages.Tickets.NEW_TICKET_ADMIN.format(name=user.first_name, user_id=user.id),
                parse_mode="HTML"
            )
            
            await update.message.reply_text(
                text=SupportMessages.Tickets.OPEN_TICKET,
                reply_markup=SupportKeyboards.support_active(),
                parse_mode="Markdown"
            )
            return CHATTING
            
        except Exception as e:
            logger.error(f"Error al abrir ticket: {e}")
            await update.message.reply_text(
                text=SupportMessages.Error.TICKET_ERROR,
                parse_mode="Markdown"
            )
            return ConversationHandler.END

    async def relay_to_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reenvía mensajes al admin y actualiza la actividad del ticket."""
        user = update.effective_user
        text = update.message.text

        if text == "🔴 Finalizar Soporte":
            return await self.close_ticket(update, context)

        try:
            # Actualizar timestamp de actividad en la BD
            await self.support_service.update_activity(user.id)
            
            # Reenviar mensaje al admin
            await context.bot.send_message(
                chat_id=settings.ADMIN_ID,
                text=f"📩 **{user.first_name}** (ID: {user.id}):\n\n{text}",
                parse_mode="Markdown"
            )
            
            # Confirmar al usuario
            await update.message.reply_text(
                "✅ Mensaje enviado al equipo de soporte.",
                reply_markup=SupportKeyboards.support_active()
            )
            return CHATTING
            
        except Exception as e:
            logger.error(f"Error al reenviar mensaje: {e}")
            await update.message.reply_text(
                text=SupportMessages.Error.MESSAGE_ERROR,
                parse_mode="Markdown"
            )
            return CHATTING

    async def close_ticket(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cierra el ticket de soporte."""
        user = update.effective_user.id
        
        try:
            await self.support_service.close_ticket(user)
            
            # Notificar al admin
            await context.bot.send_message(
                chat_id=settings.ADMIN_ID,
                text=f"🎫 Ticket del usuario {user} cerrado."
            )
            
            # Confirmar al usuario
            if update.message:
                await update.message.reply_text(
                    text=SupportMessages.Tickets.TICKET_CLOSED,
                    reply_markup=SupportKeyboards.back_to_menu(),
                    parse_mode="Markdown"
                )
            elif update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    text=SupportMessages.Tickets.TICKET_CLOSED,
                    reply_markup=SupportKeyboards.back_to_menu(),
                    parse_mode="Markdown"
                )
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Error al cerrar ticket: {e}")
            error_msg = SupportMessages.Error.CLOSE_ERROR
            
            if update.message:
                await update.message.reply_text(error_msg, parse_mode="Markdown")
            elif update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(error_msg, parse_mode="Markdown")
            
            return ConversationHandler.END

    async def show_tickets(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra los tickets del usuario."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Obtener ticket abierto si existe
            open_ticket = await self.support_service.ticket_repo.get_open_by_user(user_id)
            
            if open_ticket:
                text = "📋 **Mis Tickets**\n"
                text += "━━━━━━━━━━━━\n\n"
                text += f"🎫 **Ticket Activo**\n\n"
                text += f"📅 Creado: {open_ticket.created_at.strftime('%d/%m/%Y %H:%M')}\n"
                if open_ticket.last_message_at:
                    text += f"💬 Último mensaje: {open_ticket.last_message_at.strftime('%d/%m/%Y %H:%M')}\n"
                text += f"📊 Estado: {'Abierto' if open_ticket.status == 'open' else 'Cerrado'}\n\n"
                text += "💡 Escribe un mensaje para continuar la conversación."
            else:
                text = "📋 **Mis Tickets**\n"
                text += "━━━━━━━━━━━━\n\n"
                text += "📭 No tienes tickets activos.\n\n"
                text += "💡 Toca **🎫 Crear Ticket** para iniciar una conversación con soporte."
            
            await query.edit_message_text(
                text=text,
                reply_markup=SupportKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error al mostrar tickets: {e}")
            await query.edit_message_text(
                text=SupportMessages.Error.SYSTEM_ERROR,
                reply_markup=SupportKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )

    async def admin_reply_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler especial para que el admin responda a los tickets."""
        # Este handler es manejado por el sistema principal, pero lo incluimos aquí para completitud
        pass


def get_support_handlers(support_service: SupportService):
    """
    Retorna los handlers de soporte.
    
    Args:
        support_service: Servicio de soporte
        
    Returns:
        list: Lista de handlers
    """
    handler = SupportHandler(support_service)
    
    return [
        MessageHandler(filters.Regex("^🎫 Soporte$"), handler.start_support),
        CommandHandler("support", handler.start_support),
    ]


def get_support_callback_handlers(support_service: SupportService):
    """
    Retorna los handlers de callbacks para soporte.
    
    Args:
        support_service: Servicio de soporte
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = SupportHandler(support_service)
    
    return [
        CallbackQueryHandler(handler.show_tickets, pattern="^my_tickets$"),
        CallbackQueryHandler(handler.close_ticket, pattern="^close_ticket$"),
    ]


def get_support_conversation_handler(support_service: SupportService) -> ConversationHandler:
    """
    Retorna el ConversationHandler para soporte.
    
    Args:
        support_service: Servicio de soporte
        
    Returns:
        ConversationHandler: Handler configurado
    """
    handler = SupportHandler(support_service)
    
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🎫 Soporte$"), handler.start_support),
            CommandHandler("support", handler.start_support),
        ],
        states={
            CHATTING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handler.relay_to_admin),
                MessageHandler(filters.Regex("^🔴 Finalizar Soporte$"), handler.close_ticket),
            ]
        },
        fallbacks=[
            CommandHandler("cancel", handler.close_ticket),
            CallbackQueryHandler(handler.close_ticket, pattern="^close_ticket$"),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )
