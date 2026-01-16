"""
Handler para conversaciones con el asistente IA Sip.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from .messages_ai_support import SipMessages
from .keyboards_ai_support import AiSupportKeyboards
from utils.logger import logger
from telegram_bot.common.base_handler import BaseConversationHandler

CHATTING = 1


class AiSupportHandler(BaseConversationHandler):
    """Handler para conversaciones con IA de soporte."""

    def __init__(self, ai_support_service):
        """
        Inicializa el handler de IA Sip.

        Args:
            ai_support_service: Servicio de soporte con IA
        """
        super().__init__(ai_support_service, "AiSupportService")
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
        user_id = user.id

        try:
            await self.service.start_conversation(
                user_id=user_id,
                user_name=user.first_name,
                current_user_id=user_id
            )

            # Marcar en el contexto que estamos en conversación IA
            context.user_data['in_ai_conversation'] = True

            await self._reply_message(
                update,
                text=SipMessages.WELCOME,
                reply_markup=AiSupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )

            logger.info(f"🌊 Conversación IA iniciada por usuario {user.id}")
            return CHATTING

        except Exception as e:
            logger.error(f"❌ Error iniciando soporte IA: {e}")
            await self._reply_message(update, "❌ No pude iniciar el asistente IA. Intenta más tarde.")
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
        await self._safe_answer_query(query)

        user = update.effective_user
        user_id = user.id

        try:
            await self.service.start_conversation(
                user_id=user_id,
                user_name=user.first_name,
                current_user_id=user_id
            )

            # Marcar en el contexto que estamos en conversación IA
            context.user_data['in_ai_conversation'] = True

            await self._safe_edit_message(
                query, context,
                text=SipMessages.WELCOME,
                reply_markup=AiSupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )

            logger.info(f"🌊 Conversación IA iniciada por usuario {user.id} (callback)")
            return CHATTING

        except Exception as e:
            logger.error(f"❌ Error iniciando soporte IA: {e}")
            await self._safe_edit_message(query, context, "❌ No pude iniciar el asistente IA. Intenta más tarde.")
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
        user_id = update.effective_user.id
        
        # Debug log
        logger.info(f"🔍 handle_ai_message llamado para usuario {user_id}: '{user_message[:50]}...'")
        
        if user_message.lower() in ["finalizar", "salir", "exit"]:
            return await self.end_ai_support(update, context)
        
        try:
            await update.message.chat.send_action(action="typing")

            ai_response = await self.service.send_message(
                user_id=user_id,
                user_message=user_message,
                current_user_id=user_id
            )

            await self._reply_message(
                update,
                f"🌊 **Sip:**\n\n{ai_response}",
                reply_markup=AiSupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )

            logger.info(f"🌊 Respuesta IA enviada a usuario {user_id}")
            return CHATTING

        except ValueError as e:
            logger.warning(f"⚠️ Error de validación: {e}")
            context.user_data['in_ai_conversation'] = False
            await self._reply_message(
                update,
                SipMessages.ERROR_NO_ACTIVE_CONVERSATION,
                reply_markup=AiSupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )
            return ConversationHandler.END

        except Exception as e:
            logger.error(f"❌ Error en chat IA: {e}")
            await self._reply_message(
                update,
                SipMessages.ERROR_PROCESSING_MESSAGE,
                reply_markup=AiSupportKeyboards.ai_support_active(),
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
        
        # Limpiar el flag de conversación
        context.user_data['in_ai_conversation'] = False
        
        try:
            await self.service.end_conversation(user_id, current_user_id=user_id)

            # Manejar tanto mensajes como callbacks
            if update.message:
                await self._reply_message(
                    update,
                    text=SipMessages.CONVERSATION_ENDED,
                    reply_markup=AiSupportKeyboards.ai_support_active(),
                    parse_mode="Markdown"
                )
            elif update.callback_query:
                await self._handle_callback_query(update, context)
                await self._safe_edit_message(
                    update.callback_query, context,
                    text=SipMessages.CONVERSATION_ENDED,
                    reply_markup=AiSupportKeyboards.ai_support_active(),
                    parse_mode="Markdown"
                )

            logger.info(f"🌊 Conversación IA finalizada por usuario {user_id}")
            return ConversationHandler.END

        except Exception as e:
            logger.error(f"❌ Error finalizando conversación: {e}")
            if update.message:
                await self._reply_message(
                    update,
                    "❌ Hubo un error al finalizar la conversación.",
                    reply_markup=AiSupportKeyboards.ai_support_active()
                )
            elif update.callback_query:
                await self._handle_callback_query(update, context)
                await self._safe_edit_message(
                    update.callback_query, context,
                    "❌ Hubo un error al finalizar la conversación.",
                    reply_markup=AiSupportKeyboards.ai_support_active()
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
        await self._safe_answer_query(query)

        try:
            await self._safe_edit_message(
                query, context,
                text=SipMessages.SUGGESTED_QUESTIONS,
                reply_markup=AiSupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )
        except Exception as e:
            await self._handle_error(update, context, e, "show_suggested_questions")
    
    async def handle_end_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja el callback de finalizar conversación.

        Args:
            update: Update de Telegram
            context: Contexto de Telegram

        Returns:
            int: Estado final de la conversación
        """
        query = update.callback_query
        await self._safe_answer_query(query)
        return await self.end_ai_support(update, context)


def get_ai_support_handler(ai_support_service):
    """
    Retorna el handler de conversación con IA Sip.
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
                # Callbacks primero para que tengan prioridad
                CallbackQueryHandler(handler.handle_end_callback, pattern="^ai_sip_end$"),
                CallbackQueryHandler(handler.show_suggested_questions, pattern="^ai_sip_suggestions$"),
                # Mensajes de texto (excluyendo comandos y ciertos patrones)
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(Finalizar|Salir|Exit)$"),
                    handler.handle_ai_message
                ),
                # Comandos de salida
                MessageHandler(filters.Regex("^(Finalizar|Salir|Exit)$"), handler.end_ai_support),
            ]
        },
        fallbacks=[
            MessageHandler(filters.Regex("^(Finalizar|Salir|Exit)$"), handler.end_ai_support),
            CallbackQueryHandler(handler.handle_end_callback, pattern="^ai_sip_end$"),
            CommandHandler("cancelar", handler.end_ai_support),
        ],
        name="ai_support_conversation",
        persistent=False,
        per_chat=True,
        per_user=True,
        per_message=False,
        allow_reentry=True
    )


def get_ai_callback_handlers(ai_support_service):
    """
    Retorna los handlers de callbacks para IA Sip (para uso fuera del ConversationHandler).

    Estos handlers permiten que los botones inline funcionen incluso cuando
    el ConversationHandler no está en el estado CHATTING.

    Args:
        ai_support_service: Servicio de soporte con IA

    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = AiSupportHandler(ai_support_service)

    return [
        CallbackQueryHandler(handler.start_ai_support_callback, pattern="^ai_sip_start$"),
        CallbackQueryHandler(handler.handle_end_callback, pattern="^ai_sip_end$"),
        CallbackQueryHandler(handler.show_suggested_questions, pattern="^ai_sip_suggestions$"),
    ]
