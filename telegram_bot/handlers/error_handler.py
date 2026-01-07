"""
Handler centralizado de errores para el bot de Telegram.
Captura, registra y notifica errores de forma elegante.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import (
    TelegramError,
    Forbidden,
    BadRequest,
    TimedOut,
    ChatMigrated,
    NetworkError
)
#from loguru import logger
from datetime import datetime
import traceback
import sys

from config import settings
from telegram_bot.keyboard import CommonKeyboards
from telegram_bot.messages import CommonMessages
from utils.logger import logger


class ErrorHandler:
    """
    Clase que centraliza el manejo de errores del bot.
    Proporciona logging detallado y respuestas amigables al usuario.
    """
    
    @staticmethod
    async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handler principal de errores. Captura todas las excepciones no manejadas.
        
        Args:
            update: El update que causó el error
            context: Contexto de la aplicación con información del error
        """
        try:
            # Obtener información del error
            error = context.error
            error_type = type(error).__name__
            
            # Información del usuario (si está disponible)
            user_info = "Unknown"
            chat_info = "Unknown"
            
            if update:
                if update.effective_user:
                    user_info = f"{update.effective_user.id} (@{update.effective_user.username or 'No username'})"
                if update.effective_chat:
                    chat_info = f"{update.effective_chat.id} ({update.effective_chat.type})"
            
            # Log detallado del error usando unified_logger
            context = f"Error en bot - Usuario: {user_info}, Chat: {chat_info}, Timestamp: {datetime.now().isoformat()}"
            logger.log_error(error, context)
            
            # Manejar diferentes tipos de errores
            await ErrorHandler._handle_specific_error(update, context, error)
            
            # Notificar al admin en errores críticos
            if ErrorHandler._is_critical_error(error):
                await ErrorHandler._notify_admin(context, error, user_info, chat_info)
        
        except Exception as e:
            # Error en el handler de errores (meta-error)
            logger.critical(f"💥 ERROR EN EL ERROR HANDLER: {e}", error=e)
    
    @staticmethod
    async def _handle_specific_error(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE, 
        error: Exception
    ) -> None:
        """
        Maneja errores específicos de Telegram con respuestas apropiadas.
        
        Args:
            update: Update de Telegram
            context: Contexto de la aplicación
            error: Excepción capturada
        """
        
        # No hay update (error en job o callback)
        if not update or not update.effective_message:
            logger.warning("⚠️ Error sin update asociado (posiblemente en job)")
            return
        
        try:
            # === ERRORES DE PERMISOS ===
            if isinstance(error, Forbidden):
                logger.warning(f"🚫 Usuario bloqueó el bot: {update.effective_user.id}")
                # No intentar responder, el usuario bloqueó al bot
                return
            
            # === ERRORES DE RED ===
            elif isinstance(error, (TimedOut, NetworkError)):
                await update.effective_message.reply_text(
                    "⏱️ **Timeout de red**\n\n"
                    "Hubo un problema de conexión. Por favor, intenta nuevamente en unos segundos.",
                    parse_mode="Markdown",
                    reply_markup=CommonKeyboards.back_button("main_menu")
                )
            
            # === ERRORES DE SOLICITUD INVÁLIDA ===
            elif isinstance(error, BadRequest):
                error_str = str(error).lower()
                
                if "message is not modified" in error_str:
                    logger.debug("ℹ️ Intento de modificar mensaje sin cambios (ignorado)")
                    return

                elif "message to delete not found" in error_str:
                    logger.debug("ℹ️ Intento de borrar mensaje inexistente (ignorado)")
                    return
                
                elif "query is too old" in error_str:
                    await update.effective_message.reply_text(
                        "⏰ Esta operación expiró. Por favor, inicia el proceso nuevamente.",
                        reply_markup=CommonKeyboards.back_button("main_menu")
                    )
                
                elif "message can't be edited" in error_str:
                    await update.effective_message.reply_text(
                        "⚠️ No se pudo editar el mensaje. Intenta la operación nuevamente.",
                        reply_markup=CommonKeyboards.back_button("main_menu")
                    )
                
                else:
                    # BadRequest genérico
                    await update.effective_message.reply_text(
                        CommonMessages.Errors.GENERIC.format(
                            error="Solicitud inválida. Verifica los datos e intenta nuevamente."
                        ),
                        reply_markup=CommonKeyboards.back_button("main_menu")
                    )
            
            # === MIGRACIÓN DE CHAT ===
            elif isinstance(error, ChatMigrated):
                logger.info(f"🔄 Chat migrado: {error.old_chat_id} → {error.new_chat_id}")
                # Aquí podrías actualizar la base de datos si guardas chat_ids
            
            # === ERROR GENÉRICO DE TELEGRAM ===
            elif isinstance(error, TelegramError):
                await update.effective_message.reply_text(
                    "⚠️ **Error de Telegram**\n\n"
                    "Ocurrió un problema con la API de Telegram. "
                    "Intenta nuevamente en unos momentos.",
                    parse_mode="Markdown",
                    reply_markup=CommonKeyboards.back_button("main_menu")
                )
            
            # === ERRORES DE APLICACIÓN ===
            else:
                # Error personalizado de la aplicación
                error_message = str(error) if str(error) else "Error inesperado"
                
                await update.effective_message.reply_text(
                    CommonMessages.Errors.GENERIC.format(error=error_message),
                    reply_markup=CommonKeyboards.back_button("main_menu")
                )
        
        except Exception as e:
            logger.error(f"❌ Error al enviar mensaje de error al usuario: {e}", error=e)
    
    @staticmethod
    def _is_critical_error(error: Exception) -> bool:
        """
        Determina si un error es crítico y debe notificarse al admin.
        
        Args:
            error: Excepción a evaluar
            
        Returns:
            True si es crítico, False en caso contrario
        """
        # Errores que NO son críticos (esperados)
        non_critical = (
            Forbidden,  # Usuario bloqueó el bot
            BadRequest,  # Solicitud malformada
        )
        
        if isinstance(error, non_critical):
            return False
        
        # Errores de red tampoco son críticos (transitorios)
        if isinstance(error, (TimedOut, NetworkError)):
            return False
        
        # Todo lo demás es potencialmente crítico
        return True
    
    @staticmethod
    async def _notify_admin(
        context: ContextTypes.DEFAULT_TYPE,
        error: Exception,
        user_info: str,
        chat_info: str
    ) -> None:
        """
        Envía una notificación al administrador sobre un error crítico.
        
        Args:
            context: Contexto de la aplicación
            error: Excepción que ocurrió
            user_info: Información del usuario afectado
            chat_info: Información del chat afectado
        """
        try:
            error_type = type(error).__name__
            error_msg = str(error)[:500]  # Limitar longitud
            
            notification = (
                "🚨 **ERROR CRÍTICO EN EL BOT** 🚨\n\n"
                f"**Tipo:** `{error_type}`\n"
                f"**Usuario:** `{user_info}`\n"
                f"**Chat:** `{chat_info}`\n"
                f"**Timestamp:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
                f"**Detalles:**\n`{error_msg}`\n\n"
                "Revisa los logs para más información."
            )
            
            await context.bot.send_message(
                chat_id=settings.ADMIN_ID,
                text=notification,
                parse_mode="Markdown"
            )
            
            logger.info(f"✅ Notificación de error enviada al admin {settings.ADMIN_ID}")

        except Exception as e:
            logger.error(f"❌ No se pudo notificar al admin: {e}", error=e)


# Función standalone para compatibilidad con main.py
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Wrapper del handler de errores para registrar en la aplicación.
    
    Usage:
        application.add_error_handler(error_handler)
    """
    await ErrorHandler.handle_error(update, context)
