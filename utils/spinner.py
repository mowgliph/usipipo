"""
Sistema de Spinner para mejorar UX en operaciones asíncronas del bot.

Este módulo proporciona decoradores y utilidades para mostrar spinners
durante operaciones que pueden tomar tiempo, mejorando la experiencia
del usuario al proporcionar feedback visual inmediato.
"""

import asyncio
import random
from typing import Callable, Optional, Any
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger


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
        "default": "⏳ Procesando solicitud..."
    }
    
    @staticmethod
    def get_random_spinner_message(operation_type: str = "default") -> str:
        """Obtiene un mensaje de spinner con emoji animado."""
        base_message = SpinnerManager.MESSAGES.get(operation_type, SpinnerManager.MESSAGES["default"])
        frame = random.choice(SpinnerManager.FRAMES)
        return f"{frame} {base_message}"
    
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
            
            # Enviar mensaje de spinner
            spinner_message = await update.message.reply_text(
                text=message_text,
                parse_mode="Markdown"
            )
            
            logger.debug(f"Spinner enviado: {message_text} (ID: {spinner_message.message_id})")
            return spinner_message.message_id
            
        except Exception as e:
            logger.error(f"Error enviando spinner: {e}")
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
            
            for arg in args:
                if isinstance(arg, Update):
                    update = arg
                elif isinstance(arg, ContextTypes.DEFAULT_TYPE):
                    context = arg
            
            # Si no hay update, no podemos mostrar spinner
            if not update:
                return await func(*args, **kwargs)
            
            chat_id = update.effective_chat.id
            spinner_message_id = None
            start_time = None
            
            try:
                # Enviar spinner
                spinner_message_id = await SpinnerManager.send_spinner_message(
                    update, operation_type, custom_message
                )
                
                if show_duration:
                    import time
                    start_time = time.time()
                
                # Ejecutar la función original
                result = await func(*args, **kwargs)
                
                # Eliminar spinner si se envió correctamente
                if spinner_message_id and context:
                    await SpinnerManager.delete_spinner_message(
                        context, chat_id, spinner_message_id
                    )
                
                # Mostrar duración si se solicita
                if show_duration and start_time and context:
                    duration = time.time() - start_time
                    await update.message.reply_text(
                        f"✅ Operación completada en {duration:.2f}s"
                    )
                
                return result
                
            except Exception as e:
                logger.error(f"Error en función con spinner {func.__name__}: {e}")
                
                # Intentar eliminar spinner y mostrar error
                if spinner_message_id and context:
                    try:
                        await SpinnerManager.delete_spinner_message(
                            context, chat_id, spinner_message_id
                        )
                        await update.message.reply_text(
                            "❌ Ocurrió un error durante la operación. Por favor, intenta nuevamente."
                        )
                    except:
                        pass  # Si no podemos eliminar el spinner, continuamos
                
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
            
            for arg in args:
                if isinstance(arg, Update):
                    update = arg
                elif isinstance(arg, ContextTypes.DEFAULT_TYPE):
                    context = arg
            
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
    return with_spinner("register")(func)

def payment_spinner(func: Callable) -> Callable:
    """Spinner específico para operaciones de pago."""
    return with_spinner("payment")(func)
