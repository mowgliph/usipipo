"""
Common patterns and utilities for feature development.

Author: uSipipo Team
Version: 1.0.0 - Common Components
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .base_handler import BaseHandler
from .messages import CommonMessages
from .keyboards import CommonKeyboards


class ListPattern(BaseHandler):
    """Pattern for handling list displays with pagination."""
    
    ITEMS_PER_PAGE = 10
    
    async def show_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                       items: List[Any], page: int = 0,
                       item_formatter: callable = None,
                       empty_message: str = None) -> None:
        """
        Display a paginated list of items.
        
        Args:
            update: Update instance
            context: Context instance
            items: List of items to display
            page: Current page number
            item_formatter: Function to format each item
            empty_message: Message for empty list
        """
        if not items:
            message = empty_message or CommonMessages.Empty.NO_DATA
            keyboard = CommonKeyboards.empty_state()
            await self._edit_message_with_keyboard(update, context, message, keyboard)
            return
        
        # Calculate pagination
        start_idx = page * self.ITEMS_PER_PAGE
        end_idx = start_idx + self.ITEMS_PER_PAGE
        page_items = items[start_idx:end_idx]
        
        # Format message
        if item_formatter:
            message = "\n".join([item_formatter(item) for item in page_items])
        else:
            message = "\n".join([str(item) for item in page_items])
        
        # Add pagination info
        total_pages = (len(items) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        message += f"\n\n📄 Página {page + 1} de {total_pages} ({len(items)} totales)"
        
        # Create navigation keyboard
        has_prev = page > 0
        has_next = page < total_pages - 1
        
        keyboard = CommonKeyboards.list_navigation(
            has_next=has_next,
            has_prev=has_prev,
            next_callback=f"page_{page + 1}",
            prev_callback=f"page_{page - 1}"
        )
        
        await self._edit_message_with_keyboard(update, context, message, keyboard)


class DetailPattern(BaseHandler):
    """Pattern for handling detail views."""
    
    async def show_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                          item: Any, formatter: callable = None,
                          action_keyboard: InlineKeyboardMarkup = None) -> None:
        """
        Display detailed information about an item.
        
        Args:
            update: Update instance
            context: Context instance
            item: Item to display
            formatter: Function to format item details
            action_keyboard: Keyboard with actions for the item
        """
        if formatter:
            message = formatter(item)
        else:
            message = str(item)
        
        keyboard = action_keyboard or CommonKeyboards.back_to_previous_menu()
        
        await self._edit_message_with_keyboard(update, context, message, keyboard)


class ConfirmationPattern(BaseHandler):
    """Pattern for handling confirmation flows."""
    
    async def request_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  message: str, target_id: int,
                                  action_prefix: str = "confirm") -> None:
        """
        Request user confirmation for an action.
        
        Args:
            update: Update instance
            context: Context instance
            message: Confirmation message
            target_id: ID of the target element
            action_prefix: Prefix for callback data
        """
        keyboard = CommonKeyboards.confirmation_actions(target_id, action_prefix)
        await self._edit_message_with_keyboard(update, context, message, keyboard)
    
    async def confirm_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                           item_name: str, target_id: int) -> None:
        """
        Request deletion confirmation.
        
        Args:
            update: Update instance
            context: Context instance
            item_name: Name of the item to delete
            target_id: ID of the item
        """
        message = f"{CommonMessages.Confirmation.DELETE_CONFIRM}\n\n📦 **Elemento:** {item_name}"
        await self.request_confirmation(update, context, message, target_id, "delete")


class StatusTogglePattern(BaseHandler):
    """Pattern for handling status toggle operations."""
    
    async def toggle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                          item: Any, current_status: bool,
                          toggle_callback: callable) -> None:
        """
        Toggle item status with confirmation.
        
        Args:
            update: Update instance
            context: Context instance
            item: Item to toggle
            current_status: Current status of the item
            toggle_callback: Function to perform the toggle
        """
        try:
            new_status = not current_status
            await toggle_callback(item.id, new_status)
            
            status_text = "activado" if new_status else "desactivado"
            message = f"{CommonMessages.Success.UPDATED_SUCCESSFULLY}\n\n✅ Estado: {status_text}"
            
            keyboard = CommonKeyboards.back_to_previous_menu()
            await self._edit_message_with_keyboard(update, context, message, keyboard)
            
        except Exception as e:
            await self._handle_error(update, context, e, "toggle_status")


class SearchPattern(BaseHandler):
    """Pattern for handling search operations."""
    
    async def search_items(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                          query: str, search_callback: callable,
                          result_formatter: callable = None) -> None:
        """
        Search for items based on query.
        
        Args:
            update: Update instance
            context: Context instance
            query: Search query
            search_callback: Function to perform search
            result_formatter: Function to format results
        """
        try:
            results = await search_callback(query)
            
            if not results:
                message = CommonMessages.Empty.NO_RESULTS
                keyboard = CommonKeyboards.back_to_previous_menu()
            else:
                if result_formatter:
                    message = "\n".join([result_formatter(item) for item in results])
                else:
                    message = "\n".join([str(item) for item in results])
                
                message += f"\n\n🔍 **{len(results)} resultados encontrados**"
                keyboard = CommonKeyboards.back_to_previous_menu()
            
            await self._edit_message_with_keyboard(update, context, message, keyboard)
            
        except Exception as e:
            await self._handle_error(update, context, e, "search")


class MenuPattern(BaseHandler):
    """Pattern for handling menu navigation."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu_stack = []
    
    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                       message: str, keyboard: InlineKeyboardMarkup,
                       save_to_stack: bool = True) -> None:
        """
        Display a menu and optionally save to navigation stack.
        
        Args:
            update: Update instance
            context: Context instance
            message: Menu message
            keyboard: Menu keyboard
            save_to_stack: Whether to save to navigation stack
        """
        if save_to_stack and update.callback_query:
            # Save current state to stack
            self.menu_stack.append({
                'callback_data': update.callback_query.data,
                'message_text': update.callback_query.message.text
            })
        
        await self._edit_message_with_keyboard(update, context, message, keyboard)
    
    async def go_back(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Go back to previous menu in stack.
        
        Args:
            update: Update instance
            context: Context instance
        """
        if self.menu_stack:
            previous_state = self.menu_stack.pop()
            # Implement logic to restore previous state
            message = CommonMessages.Navigation.BACK_TO_PREVIOUS
            keyboard = CommonKeyboards.back_to_main_menu()
        else:
            message = CommonMessages.Navigation.BACK_TO_MAIN
            keyboard = CommonKeyboards.back_to_main_menu()
        
        await self._edit_message_with_keyboard(update, context, message, keyboard)


class FormPattern(BaseHandler):
    """Pattern for handling form inputs."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_data = {}
        self.current_field = None
    
    async def start_form(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                         fields: List[Dict[str, Any]], completion_callback: callable) -> None:
        """
        Start a multi-step form.
        
        Args:
            update: Update instance
            context: Context instance
            fields: List of field definitions
            completion_callback: Function to call on completion
        """
        self.form_fields = fields
        self.completion_callback = completion_callback
        self.current_field_index = 0
        
        await self._ask_current_field(update, context)
    
    async def _ask_current_field(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Ask for the current field input."""
        if self.current_field_index >= len(self.form_fields):
            await self._complete_form(update, context)
            return
        
        field = self.form_fields[self.current_field_index]
        self.current_field = field['name']
        
        message = field['prompt']
        keyboard = CommonKeyboards.cancel_only()
        
        await self._edit_message_with_keyboard(update, context, message, keyboard)
    
    async def process_form_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                input_text: str) -> None:
        """
        Process form input and move to next field.
        
        Args:
            update: Update instance
            context: Context instance
            input_text: User input
        """
        field = self.form_fields[self.current_field_index]
        
        # Validate input
        if 'validator' in field:
            try:
                validated_value = field['validator'](input_text)
            except ValueError as e:
                error_message = f"⚠️ {str(e)}\n\nPor favor, intenta nuevamente:"
                await update.message.reply_text(error_message)
                return
        
        self.form_data[self.current_field] = validated_value if 'validator' in field else input_text
        self.current_field_index += 1
        
        await self._ask_current_field(update, context)
    
    async def _complete_form(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Complete the form and call the completion callback."""
        try:
            await self.completion_callback(self.form_data)
            message = CommonMessages.Success.CREATED_SUCCESSFULLY
            keyboard = CommonKeyboards.back_to_main_menu()
            await self._edit_message_with_keyboard(update, context, message, keyboard)
        except Exception as e:
            await self._handle_error(update, context, e, "form_completion")
