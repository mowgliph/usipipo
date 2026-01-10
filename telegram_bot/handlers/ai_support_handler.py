"""
Handler para conversaciones con el asistente IA Sip.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from telegram_bot.messages import SipMessages
from telegram_bot.keyboard import SupportKeyboards, CommonKeyboards
from utils.logger import logger

CHATTING = 1


class AiSupportHandler:
    """Handler para conversaciones con IA de soporte."""
    
    def __init__(self, ai_support_service):
        """
        Inicializa el handler de IA Sip.
        
        Args:
            ai_support_service: Servicio de soporte con IA
        """
        self.ai_support_service = ai_support_service
        logger.info("🌊 AiSupportHandler inicializado")
    
    async def start_ai_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Inicia conversación con IA Sip.

        Args:
            update: Update de Telegram
            context: Contexto de Telegram

        Returns:
            int: Estado de la conversación
        """
        user = update.effective_user

        try:
            await self.ai_support_service.start_conversation(
                user_id=user.id,
                user_name=user.first_name
            )

            await update.message.reply_text(
                text=SipMessages.WELCOME,
                reply_markup=SupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )

            logger.info(f"🌊 Conversación IA iniciada por usuario {user.id}")
            return CHATTING

        except Exception as e:
            logger.error(f"❌ Error iniciando soporte IA: {e}")
            await update.message.reply_text(
                "❌ No pude iniciar el asistente IA. Intenta más tarde."
            )
            return ConversationHandler.END

    async def start_ai_support_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Inicia conversación con IA Sip desde callback del menú.

        Args:
            update: Update de Telegram
            context: Contexto de Telegram

        Returns:
            int: Estado de la conversación
        """
        query = update.callback_query
        await query.answer()

        user = update.effective_user

        try:
            await self.ai_support_service.start_conversation(
                user_id=user.id,
                user_name=user.first_name
            )

            await query.edit_message_text(
                text=SipMessages.WELCOME,
                reply_markup=SupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )

            logger.info(f"🌊 Conversación IA iniciada por usuario {user.id} (callback)")
            return CHATTING

        except Exception as e:
            logger.error(f"❌ Error iniciando soporte IA: {e}")
            await query.edit_message_text(
                "❌ No pude iniciar el asistente IA. Intenta más tarde."
            )
            return ConversationHandler.END
    
    async def handle_ai_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Procesa mensaje del usuario y responde con IA.
        
        Args:
            update: Update de Telegram
            context: Contexto de Telegram
            
        Returns:
            int: Estado de la conversación
        """
        user_message = update.message.text
        
        if user_message.lower() in ["finalizar", "salir", "exit"]:
            return await self.end_ai_support(update, context)
        
        try:
            await update.message.chat.send_action(action="typing")
            
            ai_response = await self.ai_support_service.send_message(
                user_id=update.effective_user.id,
                user_message=user_message
            )
            
            await update.message.reply_text(
                f"🌊 **Sip:**\n\n{ai_response}",
                parse_mode="Markdown"
            )
            
            return CHATTING
            
        except ValueError as e:
            logger.warning(f"⚠️ Error de validación: {e}")
            await update.message.reply_text(
                SipMessages.ERROR_NO_ACTIVE_CONVERSATION,
                reply_markup=CommonKeyboards.back_button(),
                parse_mode="Markdown"
            )
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"❌ Error en chat IA: {e}")
            await update.message.reply_text(
                SipMessages.ERROR_PROCESSING_MESSAGE,
                parse_mode="Markdown"
            )
            return CHATTING
    
    async def end_ai_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Finaliza conversación con IA.
        
        Args:
            update: Update de Telegram
            context: Contexto de Telegram
            
        Returns:
            int: Estado final de la conversación
        """
        user_id = update.effective_user.id
        
        try:
            await self.ai_support_service.end_conversation(user_id)
            
            # Manejar tanto mensajes como callbacks
            if update.message:
                await update.message.reply_text(
                    text=SipMessages.CONVERSATION_ENDED,
                    reply_markup=CommonKeyboards.back_button(),
                    parse_mode="Markdown"
                )
            elif update.callback_query:
                await update.callback_query.edit_message_text(
                    text=SipMessages.CONVERSATION_ENDED,
                    reply_markup=CommonKeyboards.back_button(),
                    parse_mode="Markdown"
                )
            
            logger.info(f"🌊 Conversación IA finalizada por usuario {user_id}")
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"❌ Error finalizando conversación: {e}")
            if update.message:
                await update.message.reply_text(
                    "❌ Hubo un error al finalizar la conversación.",
                    reply_markup=CommonKeyboards.back_button()
                )
            elif update.callback_query:
                await update.callback_query.edit_message_text(
                    "❌ Hubo un error al finalizar la conversación.",
                    reply_markup=CommonKeyboards.back_button()
                )
            return ConversationHandler.END
    
    async def show_suggested_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra preguntas sugeridas al usuario.
        
        Args:
            update: Update de Telegram
            context: Contexto de Telegram
        """
        query = update.callback_query
        await query.answer()
        
        try:
            await query.edit_message_text(
                text=SipMessages.SUGGESTED_QUESTIONS,
                reply_markup=SupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"❌ Error mostrando sugerencias: {e}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja callbacks de botones en conversación IA.
        
        Args:
            update: Update de Telegram
            context: Contexto de Telegram
        """
        query = update.callback_query
        await query.answer()
        
        if query.data == "ai_sip_end":
            await self.end_ai_support(update, context)
        elif query.data == "ai_sip_suggestions":
            await self.show_suggested_questions(update, context)


def get_ai_support_handler(ai_support_service):
    """
    Retorna el handler de conversación con IA Sip.
    
    Args:
        ai_support_service: Servicio de soporte con IA
        
    Returns:
        ConversationHandler: Handler configurado
    """
    handler = AiSupportHandler(ai_support_service)
    
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🌊 Sip$"), handler.start_ai_support),
            MessageHandler(filters.Regex("^🤖 Asistente IA$"), handler.start_ai_support),
            CommandHandler("sipai", handler.start_ai_support),
            CallbackQueryHandler(handler.start_ai_support_callback, pattern="^ai_sip_start$")
        ],
        states={
            CHATTING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_ai_message)
            ]
        },
        fallbacks=[
            MessageHandler(filters.Regex("^(Finalizar|Salir|Exit)$"), handler.end_ai_support),
            CallbackQueryHandler(handler.handle_callback, pattern="^ai_sip_")
        ],
        name="ai_support_conversation",
        per_chat=True,   # Asegúrate de que esto sea True
        per_user=True,
        per_message=False
    )


def get_ai_callback_handler(ai_support_service):
    """
    Retorna el handler de callbacks para IA Sip.
    
    Args:
        ai_support_service: Servicio de soporte con IA
        
    Returns:
        CallbackQueryHandler: Handler de callbacks
    """
    handler = AiSupportHandler(ai_support_service)
    return CallbackQueryHandler(handler.handle_callback, pattern="^ai_sip_")
