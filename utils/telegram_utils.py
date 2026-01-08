"""
Utilitarios globales para handlers del bot uSipipo.
Proporciona funciones comunes de validación y manejo de errores.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from utils.logger import logger
from telegram_bot.messages import CommonMessages
from telegram_bot.keyboard import UserKeyboards
from typing import Optional, Tuple


class TelegramHandlerUtils:
    """Clase de utilidades para handlers de Telegram."""
    
    @staticmethod
    async def validate_callback_query(
        query, 
        context: ContextTypes.DEFAULT_TYPE, 
        update: Update
    ) -> bool:
        """
        Valida que el objeto query no sea None. Si es None, envía un mensaje de error y retorna False.
        Si es válido, retorna True.
        
        Args:
            query: Objeto callback_query a validar
            context: Contexto de la aplicación
            update: Objeto Update de Telegram
            
        Returns:
            bool: True si query es válido, False si es None
        """
        if query is None:
            logger.error("Error: query es None")
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=CommonMessages.Errors.GENERIC.format(error="Operación no válida"),
                    reply_markup=UserKeyboards.quick_actions()
                )
            except Exception as e:
                logger.error(f"Error al enviar mensaje de fallback: {e}")
            return False
        return True
    
    @staticmethod
    async def safe_edit_message(
        query, 
        context: ContextTypes.DEFAULT_TYPE, 
        text: str, 
        reply_markup=None, 
        parse_mode: Optional[str] = None
    ) -> bool:
        """
        Intenta editar el mensaje; si no es posible, maneja fallbacks.
        
        Args:
            query: Objeto callback_query
            context: Contexto de la aplicación
            text: Texto del mensaje
            reply_markup: Teclado del mensaje
            parse_mode: Modo de parseo (Markdown, HTML, etc.)
            
        Returns:
            bool: True si tuvo éxito, False si falló
        """
        try:
            await query.edit_message_text(
                text=text, 
                reply_markup=reply_markup, 
                parse_mode=parse_mode
            )
            return True
        except BadRequest as e:
            err = str(e)
            logger.warning(f"safe_edit_message: edit failed: {err}")
            
            # Si el error es por parseo de entidades, reintentar sin parse_mode
            if "Can't parse entities" in err or ("character" in err and "reserved" in err):
                try:
                    await query.edit_message_text(
                        text=text, 
                        reply_markup=reply_markup
                    )
                    return True
                except BadRequest as e2:
                    logger.warning(f"safe_edit_message: retry without parse_mode failed: {e2}")
            
            try:
                # Si el mensaje tiene caption, intentar editar caption
                if getattr(query.message, 'caption', None) is not None:
                    await query.edit_message_caption(
                        caption=text, 
                        reply_markup=reply_markup, 
                        parse_mode=parse_mode
                    )
                else:
                    # Enviar nuevo mensaje como fallback
                    await context.bot.send_message(
                        chat_id=query.message.chat.id, 
                        text=text, 
                        reply_markup=reply_markup, 
                        parse_mode=parse_mode
                    )
                return True
            except BadRequest as ex:
                # Si el fallback falló por errores de parseo, reintentar sin parse_mode
                if "Can't parse entities" in str(ex) or ("character" in str(ex) and "reserved" in str(ex)):
                    try:
                        await context.bot.send_message(
                            chat_id=query.message.chat.id, 
                            text=text, 
                            reply_markup=reply_markup
                        )
                        return True
                    except Exception as ex2:
                        logger.error(f"safe_edit_message fallback failed: {ex2}")
                else:
                    logger.error(f"safe_edit_message fallback failed: {ex}")
                return False
        except Exception as e:
            logger.error(f"safe_edit_message: unexpected error: {e}")
            return False
    
    @staticmethod
    async def safe_answer_query(query) -> bool:
        """
        Responde a un callback query de forma segura.
        
        Args:
            query: Objeto callback_query
            
        Returns:
            bool: True si tuvo éxito, False si falló
        """
        if query is None:
            return False
            
        try:
            await query.answer()
            return True
        except Exception as e:
            logger.warning(f"safe_answer_query: failed to answer: {e}")
            return False
    
    @staticmethod
    def get_user_id(update: Update) -> Optional[int]:
        """
        Obtiene el ID de usuario de forma segura desde Update.
        
        Args:
            update: Objeto Update de Telegram
            
        Returns:
            Optional[int]: ID del usuario o None si no se puede obtener
        """
        try:
            return update.effective_user.id if update.effective_user else None
        except Exception as e:
            logger.error(f"get_user_id: error getting user ID: {e}")
            return None
    
    @staticmethod
    def get_chat_id(update: Update) -> Optional[int]:
        """
        Obtiene el ID del chat de forma segura desde Update.
        
        Args:
            update: Objeto Update de Telegram
            
        Returns:
            Optional[int]: ID del chat o None si no se puede obtener
        """
        try:
            return update.effective_chat.id if update.effective_chat else None
        except Exception as e:
            logger.error(f"get_chat_id: error getting chat ID: {e}")
            return None
    
    @staticmethod
    async def handle_generic_error(
        context: ContextTypes.DEFAULT_TYPE,
        update: Update,
        error: Exception,
        custom_message: Optional[str] = None
    ) -> bool:
        """
        Maneja errores genéricos de forma estandarizada.
        
        Args:
            context: Contexto de la aplicación
            update: Objeto Update de Telegram
            error: Excepción ocurrida
            custom_message: Mensaje personalizado opcional
            
        Returns:
            bool: True si tuvo éxito, False si falló
        """
        try:
            chat_id = TelegramHandlerUtils.get_chat_id(update)
            if chat_id is None:
                logger.error(f"handle_generic_error: cannot get chat_id")
                return False
                
            error_text = custom_message or str(error)
            await context.bot.send_message(
                chat_id=chat_id,
                text=CommonMessages.Errors.GENERIC.format(error=error_text),
                reply_markup=UserKeyboards.quick_actions()
            )
            return True
        except Exception as e:
            logger.error(f"handle_generic_error: failed to handle error: {e}")
            return False


# Instancia global para uso directo
telegram_utils = TelegramHandlerUtils()
