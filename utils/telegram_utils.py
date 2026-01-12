"""
Telegram Handler Utilities

This module provides Telegram-specific utilities for handlers.

Author: uSipipo Team
Version: 2.0.0 - Enhanced with Telegram Utils
"""

from typing import Any, List, Dict, Optional
from datetime import datetime
import re

# Telegram-specific imports
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from utils.logger import logger
from telegram_bot.common.messages import CommonMessages
from telegram_bot.common.keyboards import CommonKeyboards


def format_bytes(bytes_count: int) -> str:
    """
    Format bytes into human readable format.
    
    Args:
        bytes_count: Number of bytes
        
    Returns:
        str: Formatted string (e.g., "1.5 GB")
    """
    if bytes_count == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    
    while bytes_count >= 1024 and unit_index < len(units) - 1:
        bytes_count /= 1024.0
        unit_index += 1
    
    return f"{bytes_count:.1f} {units[unit_index]}"


def format_datetime(dt: datetime, include_time: bool = True) -> str:
    """
    Format datetime in user-friendly format.
    
    Args:
        dt: DateTime object
        include_time: Whether to include time
        
    Returns:
        str: Formatted datetime string
    """
    if include_time:
        return dt.strftime("%d/%m/%Y %H:%M")
    return dt.strftime("%d/%m/%Y")


def format_relative_time(dt: datetime) -> str:
    """
    Format datetime as relative time (e.g., "hace 2 horas").
    
    Args:
        dt: DateTime object
        
    Returns:
        str: Relative time string
    """
    now = datetime.now()
    delta = now - dt
    
    if delta.days > 0:
        if delta.days == 1:
            return "ayer"
        elif delta.days < 7:
            return f"hace {delta.days} días"
        elif delta.days < 30:
            weeks = delta.days // 7
            return f"hace {weeks} semana{'s' if weeks > 1 else ''}"
        else:
            months = delta.days // 30
            return f"hace {months} mes{'es' if months > 1 else ''}"
    
    hours = delta.seconds // 3600
    if hours > 0:
        return f"hace {hours} hora{'s' if hours > 1 else ''}"
    
    minutes = (delta.seconds % 3600) // 60
    if minutes > 0:
        return f"hace {minutes} minuto{'s' if minutes > 1 else ''}"
    
    return "ahora mismo"


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount.
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        str: Formatted currency string
    """
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥'
    }
    
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:.2f}"


def format_percentage(value: float, total: float) -> str:
    """
    Format percentage with progress bar.
    
    Args:
        value: Current value
        total: Total value
        
    Returns:
        str: Formatted percentage with progress bar
    """
    if total == 0:
        percentage = 0
    else:
        percentage = min(100, (value / total) * 100)
    
    # Create progress bar
    bar_length = 10
    filled_length = int(bar_length * percentage / 100)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    
    return f"{bar} {percentage:.1f}%"


def sanitize_text(text: str, max_length: int = None) -> str:
    """
    Sanitize text for Telegram messages.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length (optional)
        
    Returns:
        str: Sanitized text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Escape markdown special characters if needed
    # text = text.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
    
    if max_length and len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    return text


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number string
        
    Returns:
        bool: True if valid
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if it has reasonable length (10-15 digits)
    return 10 <= len(digits) <= 15


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email string
        
    Returns:
        bool: True if valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def extract_id_from_callback(callback_data: str, prefix: str) -> Optional[int]:
    """
    Extract ID from callback data.
    
    Args:
        callback_data: Callback data string
        prefix: Prefix to look for
        
    Returns:
        int or None: Extracted ID
    """
    pattern = f"^{prefix}_(\\d+)$"
    match = re.match(pattern, callback_data)
    
    if match:
        return int(match.group(1))
    
    return None


def create_callback_data(prefix: str, *args) -> str:
    """
    Create callback data from parts.
    
    Args:
        prefix: Prefix for the callback
        *args: Additional parts
        
    Returns:
        str: Callback data string
    """
    parts = [prefix] + [str(arg) for arg in args]
    return "_".join(parts)


def parse_callback_data(callback_data: str) -> List[str]:
    """
    Parse callback data into parts.
    
    Args:
        callback_data: Callback data string
        
    Returns:
        list: Parts of the callback data
    """
    return callback_data.split("_")


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary.
    
    Args:
        dictionary: Dictionary to get value from
        key: Key to look for
        default: Default value if key not found
        
    Returns:
        Any: Value or default
    """
    return dictionary.get(key, default)


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        list: List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def generate_unique_id() -> str:
    """
    Generate a unique ID.
    
    Returns:
        str: Unique ID
    """
    import uuid
    return str(uuid.uuid4())[:8]


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def escape_markdown(text: str) -> str:
    """
    Escape markdown special characters.
    
    Args:
        text: Text to escape
        
    Returns:
        str: Escaped text
    """
    escape_chars = ['*', '_', '`', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text


def is_admin(user_id: int) -> bool:
    """
    Check if user is admin.
    
    Args:
        user_id: User ID to check
        
    Returns:
        bool: True if admin
    """
    from config import settings
    return user_id == int(settings.ADMIN_ID)


def format_user_name(user) -> str:
    """
    Format user name for display.
    
    Args:
        user: Telegram user object
        
    Returns:
        str: Formatted name
    """
    if user.full_name:
        return user.full_name
    elif user.username:
        return f"@{user.username}"
    else:
        return f"Usuario {user.id}"


def calculate_page_bounds(total_items: int, page: int, items_per_page: int = 10) -> tuple:
    """
    Calculate page bounds for pagination.
    
    Args:
        total_items: Total number of items
        page: Current page (0-based)
        items_per_page: Items per page
        
    Returns:
        tuple: (start_idx, end_idx, total_pages)
    """
    total_pages = (total_items + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    return start_idx, end_idx, total_pages


class TelegramUtils:
    """Telegram-specific utilities for handlers."""
    
    @staticmethod
    async def safe_edit_message(
        query,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
        reply_markup=None,
        parse_mode: Optional[str] = None
    ) -> bool:
        """
        Safely edit message with multiple fallback strategies.
        
        This enhanced version integrates with CommonMessages and CommonKeyboards
        for consistent error handling and navigation.
        
        Args:
            query: Callback query object
            context: Application context
            text: Message text
            reply_markup: Message keyboard markup
            parse_mode: Parse mode (Markdown, HTML, etc.)
            
        Returns:
            bool: True if successful, False if failed
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
            
            # If the error is due to entity parsing, retry without parse_mode
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
                # If the message has caption, try to edit caption
                if getattr(query.message, 'caption', None) is not None:
                    await query.edit_message_caption(
                        caption=text,
                        reply_markup=reply_markup,
                        parse_mode=parse_mode
                    )
                else:
                    # Send new message as fallback
                    await context.bot.send_message(
                        chat_id=query.message.chat.id,
                        text=text,
                        reply_markup=reply_markup,
                        parse_mode=parse_mode
                    )
                return True
            except BadRequest as ex:
                # If the fallback failed due to parsing errors, retry without parse_mode
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
        Safely answer callback query.
        
        Args:
            query: Callback query object
            
        Returns:
            bool: True if successful, False if failed
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
        Get user ID from update.
        
        Args:
            update: Telegram Update object
            
        Returns:
            Optional[int]: User ID or None if cannot be obtained
        """
        try:
            return update.effective_user.id if update.effective_user else None
        except Exception as e:
            logger.error(f"get_user_id: error getting user ID: {e}")
            return None
    
    @staticmethod
    def get_chat_id(update: Update) -> Optional[int]:
        """
        Get chat ID from update.
        
        Args:
            update: Telegram Update object
            
        Returns:
            Optional[int]: Chat ID or None if cannot be obtained
        """
        try:
            return update.effective_chat.id if update.effective_chat else None
        except Exception as e:
            logger.error(f"get_chat_id: error getting chat ID: {e}")
            return None
    
    @staticmethod
    async def validate_callback_query(
        query,
        context: ContextTypes.DEFAULT_TYPE,
        update: Update
    ) -> bool:
        """
        Validate callback query and handle errors.
        
        This enhanced version uses CommonMessages and CommonKeyboards for
        consistent error handling and navigation.
        
        Args:
            query: Callback query object to validate
            context: Application context
            update: Telegram Update object
            
        Returns:
            bool: True if query is valid, False if None
        """
        if query is None:
            logger.error("Error: query es None")
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=CommonMessages.Error.SYSTEM_ERROR,
                    reply_markup=CommonKeyboards.back_to_main_menu()
                )
            except Exception as e:
                logger.error(f"Error al enviar mensaje de fallback: {e}")
            return False
        return True
    
    @staticmethod
    async def handle_generic_error(
        context: ContextTypes.DEFAULT_TYPE,
        update: Update,
        error: Exception,
        custom_message: Optional[str] = None
    ) -> bool:
        """
        Handle generic errors consistently.
        
        This enhanced version uses CommonMessages and CommonKeyboards for
        standardized error responses.
        
        Args:
            context: Application context
            update: Telegram Update object
            error: Exception that occurred
            custom_message: Optional custom error message
            
        Returns:
            bool: True if successful, False if failed
        """
        try:
            chat_id = TelegramUtils.get_chat_id(update)
            if chat_id is None:
                logger.error(f"handle_generic_error: cannot get chat_id")
                return False
                 
            error_text = custom_message or str(error)
            await context.bot.send_message(
                chat_id=chat_id,
                text=CommonMessages.Error.SYSTEM_ERROR,
                reply_markup=CommonKeyboards.back_to_main_menu()
            )
            return True
        except Exception as e:
            logger.error(f"handle_generic_error: failed to handle error: {e}")
            return False


# Create TelegramHandlerUtils as an alias for backward compatibility
TelegramHandlerUtils = TelegramUtils