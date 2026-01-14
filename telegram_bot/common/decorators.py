"""
Common decorators for handlers.

Author: uSipipo Team
Version: 1.0.0 - Common Components
"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger
from utils.spinner import with_spinner, database_spinner, vpn_spinner, database_spinner_callback
from .messages import CommonMessages


def handle_errors(operation_name: str = "operación"):
    """
    Decorator to handle errors consistently across handlers.
    
    Args:
        operation_name: Name of the operation for error messages
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            try:
                return await func(self, update, context, *args, **kwargs)
            except Exception as e:
                await self._handle_error(update, context, e, operation_name)
                return None
        return wrapper
    return decorator


def safe_callback_query(func):
    """
    Decorator to safely handle callback queries.
    """
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        await self._handle_callback_query(update, context)
        return await func(self, update, context, *args, **kwargs)
    return wrapper


def admin_required(func):
    """
    Decorator to require admin privileges.
    """
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        from config import settings
        
        user = update.effective_user
        if user.id != int(settings.ADMIN_ID):
            await update.message.reply_text(
                text=CommonMessages.Error.ACCESS_DENIED,
                parse_mode="Markdown"
            )
            return None
        
        return await func(self, update, context, *args, **kwargs)
    return wrapper


def require_user_data(key: str, error_message: str = None):
    """
    Decorator to require specific user data in context.
    
    Args:
        key: Key to check in user_data
        error_message: Custom error message
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            if key not in context.user_data:
                message = error_message or CommonMessages.Error.VALIDATION_ERROR
                await update.message.reply_text(
                    text=message,
                    parse_mode="Markdown"
                )
                return None
            
            return await func(self, update, context, *args, **kwargs)
        return wrapper
    return decorator


def with_conversation_state(state_key: str, state_value: bool = True):
    """
    Decorator to manage conversation state.
    
    Args:
        state_key: Key for the state in user_data
        state_value: Value to set for the state
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            # Set state before function
            context.user_data[state_key] = state_value
            
            try:
                result = await func(self, update, context, *args, **kwargs)
                return result
            except Exception as e:
                # Clear state on error
                context.user_data[state_key] = False
                raise e
        return wrapper
    return decorator


# Predefined decorators for common operations
database_operation = handle_errors("operación de base de datos")
vpn_operation = handle_errors("operación de VPN")
payment_operation = handle_errors("operación de pago")
user_operation = handle_errors("operación de usuario")

# Combined decorators
@safe_callback_query
@database_spinner_callback
@database_operation
def safe_database_operation(func):
    """Combined decorator for safe database operations."""
    return func

@safe_callback_query
@vpn_spinner
@vpn_operation
def safe_vpn_operation(func):
    """Combined decorator for safe VPN operations."""
    return func

@safe_callback_query
@with_spinner()
@handle_errors("operación")
def safe_general_operation(func):
    """Combined decorator for safe general operations."""
    return func
