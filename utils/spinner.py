"""
Sistema de Spinner para mejorar UX en operaciones asíncronas del bot.

Este módulo proporciona decoradores y utilidades para mostrar spinners
durante operaciones que pueden tomar tiempo, mejorando la experiencia
del usuario al proporcionar feedback visual inmediato.
"""

import asyncio
import random
import time
from typing import Callable, Optional, Any
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger


class SpinnerManager:
    """Gestiona los spinners para operaciones asíncronas."""
    
    # Emojis para animación de spinner
    SPINNER_FRAMES = [
        "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
    ]
    
    # Mensajes predefinidos para diferentes tipos de operaciones
    MESSAGES = {
        "loading": "🔄 Cargando...",
        "processing": "⚙️ Procesando...",
        "connecting": "🔌 Conectando...",
        "creating": "🔨 Creando...",
        "updating": "📝 Actualizando...",
        "deleting": "🗑️ Eliminando...",
        "searching": "🔍 Buscando...",
        "validating": "✅ Validando...",
        "database": "💾 Accediendo a la base de datos...",
        "vpn": "🌐 Configurando VPN...",
        "payment": "💳 Procesando pago...",
        "register": "👤 Registrando usuario...",
        "ai_thinking": "🌊 Sip está pensando...",
        "ai_searching": "🌊 Sip está buscando información...",
        "ai_analyzing": "🌊 Sip está analizando tu problema...",
        "ai_generating": "🌊 Sip está generando respuesta...",
        "default": "⏳ Procesando solicitud..."
    }
    
    @staticmethod
    def get_random_spinner_message(operation_type: str = "default") -> str:
        """Obtiene un mensaje de spinner con emoji animado."""
        base_message = SpinnerManager.MESSAGES.get(operation_type, SpinnerManager.MESSAGES["default"])
        # Usar índice simple en lugar de random.choice para evitar importaciones
        
        try:
            frame_index = int(time.time() * 10) % len(SpinnerManager.SPINNER_FRAMES)
            frame = SpinnerManager.SPINNER_FRAMES[frame_index]
            return f"{frame} {base_message}"
        except AttributeError as e:
            logger.error(f"❌ Error en get_random_spinner_message: {e}")
            logger.error(f"Atributos disponibles en SpinnerManager: {dir(SpinnerManager)}")
            # Fallback a mensaje simple
            return f"🌀 {base_message}"
    
    @staticmethod
    async def send_spinner_message(
        update: Update,
        operation_type: str = "default",
        custom_message: Optional[str] = None
    ) -> int:
        """
        Envía un mensaje de spinner y retorna el message_id.
        
        Args:
            update: Objeto Update de Telegram
            operation_type: Tipo de operación para mensaje predefinido
            custom_message: Mensaje personalizado (sobrescribe operation_type)
             
        Returns:
            message_id del spinner enviado
        """
        try:
            message_text = custom_message or SpinnerManager.get_random_spinner_message(operation_type)
            logger.info(f"🌀 Preparando spinner: {message_text}")
            
            # Verificar si update.message existe
            if not update.message:
                logger.error("❌ No se puede enviar spinner: update.message es None")
                return None
            
            # Enviar mensaje de spinner
            spinner_message = await update.message.reply_text(
                text=message_text,
                parse_mode="Markdown"
            )
            
            logger.info(f"✅ Spinner enviado: {message_text} (ID: {spinner_message.message_id})")
            return spinner_message.message_id
             
        except Exception as e:
            logger.error(f"❌ Error enviando spinner: {e}")
            logger.error(f"Tipo de excepción: {type(e).__name__}")
            return None
    
    @staticmethod
    async def update_spinner_message(
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        message_id: int,
        operation_type: str = "default",
        custom_message: Optional[str] = None
    ) -> bool:
        """
        Actualiza un mensaje de spinner existente.
        
        Args:
            context: Contexto del bot
            chat_id: ID del chat
            message_id: ID del mensaje a actualizar
            operation_type: Tipo de operación para mensaje predefinido
            custom_message: Mensaje personalizado
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            message_text = custom_message or SpinnerManager.get_random_spinner_message(operation_type)
            
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=message_text,
                parse_mode="Markdown"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando spinner: {e}")
            return False
    
    @staticmethod
    async def delete_spinner_message(
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        message_id: int
    ) -> bool:
        """
        Elimina un mensaje de spinner.
        
        Args:
            context: Contexto del bot
            chat_id: ID del chat
            message_id: ID del mensaje a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id
            )
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando spinner: {e}")
            return False


def with_spinner(
    operation_type: str = "default",
    custom_message: Optional[str] = None,
    show_duration: bool = False
):
    """
    Decorador para agregar spinner a funciones asíncronas.
    
    Args:
        operation_type: Tipo de operación para mensaje predefinido
        custom_message: Mensaje personalizado
        show_duration: Si True, muestra el tiempo de ejecución
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extraer update y context de los argumentos
            update = None
            context = None

            # Buscar update y context en argumentos posicionales
            for arg in args:
                if isinstance(arg, Update):
                    update = arg
                elif hasattr(arg, 'bot'):
                    context = arg

            # También buscar en kwargs por si acaso
            if 'context' in kwargs and hasattr(kwargs['context'], 'bot'):
                context = kwargs['context']
            if 'update' in kwargs and isinstance(kwargs['update'], Update):
                update = kwargs['update']
            
            # Si no hay update, no podemos mostrar spinner
            if not update:
                return await func(*args, **kwargs)
            
            chat_id = update.effective_chat.id
            spinner_message_id = None
            start_time = None
            
            try:
                logger.info(f"🌀 Iniciando spinner para {func.__name__}")
                
                # Enviar spinner
                spinner_message_id = await SpinnerManager.send_spinner_message(
                    update, operation_type, custom_message
                )
                
                logger.info(f"🌀 Spinner enviado con ID: {spinner_message_id}")
                 
                if show_duration:
                    import time
                    start_time = time.time()
                 
                # Ejecutar la función original
                result = await func(*args, **kwargs)
                
                # Asegurar que el spinner sea visible por al menos 1 segundo
                if show_duration and start_time:
                    duration = time.time() - start_time
                    if duration < 1.0:
                        await asyncio.sleep(1.0 - duration)
                 
                # Eliminar spinner si se envió correctamente
                if spinner_message_id and context:
                    logger.info(f"🗑️  Eliminando spinner ID: {spinner_message_id}")
                    success = await SpinnerManager.delete_spinner_message(
                        context, chat_id, spinner_message_id
                    )
                    logger.info(f"🗑️  Spinner eliminado: {success}")
                else:
                    logger.warning(f"⚠️  No se pudo eliminar spinner - ID: {spinner_message_id}, Context: {context is not None}")
                 
                # Mostrar duración si se solicita
                if show_duration and start_time and context:
                    duration = time.time() - start_time
                    await update.message.reply_text(
                        f"✅ Operación completada en {duration:.2f}s"
                    )
                 
                return result
                 
            except Exception as e:
                logger.error(f"❌ Error en función con spinner {func.__name__}: {e}")
                logger.error(f"❌ Tipo de excepción: {type(e).__name__}")
                
                # Intentar eliminar spinner y mostrar error
                if spinner_message_id and context:
                    try:
                        logger.info(f"🗑️  Intentando eliminar spinner después de error")
                        await SpinnerManager.delete_spinner_message(
                            context, chat_id, spinner_message_id
                        )
                        await update.message.reply_text(
                            "❌ Ocurrió un error durante la operación. Por favor, intenta nuevamente."
                        )
                    except Exception as delete_error:
                        logger.error(f"❌ Error eliminando spinner: {delete_error}")
                        pass  # Si no podemos eliminar el spinner, continuamos
                else:
                    logger.warning(f"⚠️  No se pudo eliminar spinner después de error - ID: {spinner_message_id}, Context: {context is not None}")
                 
                # Re-lanzar la excepción para manejo normal
                raise e
        
        return wrapper
    return decorator


def with_animated_spinner(
    operation_type: str = "default",
    custom_message: Optional[str] = None,
    update_interval: float = 0.5
):
    """
    Decorador para spinner animado que se actualiza periódicamente.
    
    Args:
        operation_type: Tipo de operación para mensaje predefinido
        custom_message: Mensaje personalizado
        update_interval: Intervalo de actualización en segundos
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extraer update y context de los argumentos
            update = None
            context = None

            # Buscar update y context en argumentos posicionales
            for arg in args:
                if isinstance(arg, Update):
                    update = arg
                elif hasattr(arg, 'bot'):
                    context = arg

            # También buscar en kwargs por si acaso
            if 'context' in kwargs and hasattr(kwargs['context'], 'bot'):
                context = kwargs['context']
            if 'update' in kwargs and isinstance(kwargs['update'], Update):
                update = kwargs['update']
            
            if not update:
                return await func(*args, **kwargs)
            
            chat_id = update.effective_chat.id
            spinner_message_id = None
            animation_task = None
            
            async def animate_spinner():
                """Tarea asíncrona para animar el spinner."""
                while True:
                    if spinner_message_id and context:
                        await SpinnerManager.update_spinner_message(
                            context, chat_id, spinner_message_id, 
                            operation_type, custom_message
                        )
                    await asyncio.sleep(update_interval)
            
            try:
                # Enviar spinner inicial
                spinner_message_id = await SpinnerManager.send_spinner_message(
                    update, operation_type, custom_message
                )
                
                # Iniciar animación
                animation_task = asyncio.create_task(animate_spinner())
                
                # Ejecutar función original
                result = await func(*args, **kwargs)
                
                # Cancelar animación
                if animation_task:
                    animation_task.cancel()
                    try:
                        await animation_task
                    except asyncio.CancelledError:
                        pass
                
                # Eliminar spinner
                if spinner_message_id and context:
                    await SpinnerManager.delete_spinner_message(
                        context, chat_id, spinner_message_id
                    )
                
                return result
                
            except Exception as e:
                logger.error(f"Error en función con spinner animado {func.__name__}: {e}")
                
                # Cancelar animación
                if animation_task:
                    animation_task.cancel()
                    try:
                        await animation_task
                    except asyncio.CancelledError:
                        pass
                
                # Eliminar spinner y mostrar error
                if spinner_message_id and context:
                    try:
                        await SpinnerManager.delete_spinner_message(
                            context, chat_id, spinner_message_id
                        )
                        await update.message.reply_text(
                            "❌ Ocurrió un error durante la operación. Por favor, intenta nuevamente."
                        )
                    except:
                        pass
                
                raise e
        
        return wrapper
    return decorator


# Funciones de conveniencia para operaciones comunes
def database_spinner(func: Callable) -> Callable:
    """Spinner específico para operaciones de base de datos."""
    return with_spinner("database")(func)

def vpn_spinner(func: Callable) -> Callable:
    """Spinner específico para operaciones VPN."""
    return with_spinner("vpn")(func)

def registration_spinner(func: Callable) -> Callable:
    """Spinner específico para registro de usuarios."""
    return with_spinner("register", show_duration=True)(func)

def payment_spinner(func: Callable) -> Callable:
    """Spinner específico para operaciones de pago."""
    return with_spinner("payment")(func)
