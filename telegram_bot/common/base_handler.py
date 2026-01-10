"""
Base handler class with common functionality for all features.

Author: uSipipo Team
Version: 1.0.0 - Common Components
"""

from abc import ABC
from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger
from utils.telegram_utils import TelegramHandlerUtils


class BaseHandler(ABC):
    """Base class for all feature handlers with common functionality."""
    
    def __init__(self, service=None, service_name: str = "Service"):
        """
        Initialize base handler.
        
        Args:
            service: Service instance for the handler
            service_name: Name of the service for logging
        """
        self.service = service
        self.service_name = service_name
        handler_class = self.__class__.__name__
        logger.info(f"🔧 {handler_class} inicializado con {service_name}")
    
    async def _handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Safely handle callback query with answer.
        
        Args:
            update: Update instance
            context: Context instance
        """
        if update.callback_query:
            await TelegramHandlerUtils.safe_answer_query(update.callback_query)
    
    async def _handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                          error: Exception, operation: str = "operación"):
        """
        Handle errors consistently across all handlers.
        
        Args:
            update: Update instance
            context: Context instance
            error: Exception that occurred
            operation: Description of the operation that failed
        """
        handler_class = self.__class__.__name__
        logger.error(f"Error en {handler_class}.{operation}: {error}")
        
        from .messages import CommonMessages
        
        error_message = CommonMessages.Error.SYSTEM_ERROR
        
        if update.callback_query:
            await TelegramHandlerUtils.safe_edit_message(
                update.callback_query, context,
                text=error_message,
                reply_markup=self._get_back_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                text=error_message,
                parse_mode="Markdown"
            )
    
    def _get_back_keyboard(self):
        """
        Get appropriate back keyboard. Override in subclasses.
        
        Returns:
            InlineKeyboardMarkup: Back navigation keyboard
        """
        from .keyboards import CommonKeyboards
        return CommonKeyboards.back_to_main_menu()
    
    async def _edit_message_with_keyboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                        text: str, reply_markup=None, parse_mode="Markdown"):
        """
        Safely edit message with keyboard.
        
        Args:
            update: Update instance
            context: Context instance
            text: Message text
            reply_markup: Keyboard markup
            parse_mode: Parse mode for message
        """
        if update.callback_query:
            await TelegramHandlerUtils.safe_edit_message(
                update.callback_query, context,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
    
    async def _reply_message(self, update: Update, text: str, reply_markup=None, parse_mode="Markdown"):
        """
        Reply to message with keyboard.
        
        Args:
            update: Update instance
            text: Message text
            reply_markup: Keyboard markup
            parse_mode: Parse mode for message
        """
        await update.message.reply_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )


class BaseConversationHandler(BaseHandler):
    """Base class for conversation handlers."""
    
    async def _end_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                              message: str = "Conversación finalizada."):
        """
        End conversation consistently.
        
        Args:
            update: Update instance
            context: Context instance
            message: Farewell message
        """
        from telegram.ext import ConversationHandler
        
        if update.message:
            await update.message.reply_text(message)
        elif update.callback_query:
            await self._handle_callback_query(update, context)
            await TelegramHandlerUtils.safe_edit_message(
                update.callback_query, context,
                text=message
            )
        
        return ConversationHandler.END
