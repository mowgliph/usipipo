"""
Common keyboards shared across all features.

Author: uSipipo Team
Version: 1.0.0 - Common Components
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class CommonKeyboards:
    """Common keyboards used across all features."""

    @staticmethod
    def back_to_main_menu() -> InlineKeyboardMarkup:
        """
        Keyboard to return to main menu.
        
        Returns:
            InlineKeyboardMarkup: Back to main menu keyboard
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_previous_menu() -> InlineKeyboardMarkup:
        """
        Keyboard to return to previous menu.
        
        Returns:
            InlineKeyboardMarkup: Back to previous menu keyboard
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver", callback_data="back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirmation_actions(target_id: int = None, action_prefix: str = "confirm") -> InlineKeyboardMarkup:
        """
        Standard confirmation keyboard.
        
        Args:
            target_id: ID of the target element
            action_prefix: Prefix for callback data
            
        Returns:
            InlineKeyboardMarkup: Confirmation keyboard
        """
        callback_data = f"{action_prefix}_{target_id}" if target_id else action_prefix
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=callback_data),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def delete_confirmation(target_id: int) -> InlineKeyboardMarkup:
        """
        Delete confirmation keyboard.
        
        Args:
            target_id: ID of the element to delete
            
        Returns:
            InlineKeyboardMarkup: Delete confirmation keyboard
        """
        return CommonKeyboards.confirmation_actions(target_id, "delete")

    @staticmethod
    def cancel_only() -> InlineKeyboardMarkup:
        """
        Keyboard with only cancel button.
        
        Returns:
            InlineKeyboardMarkup: Cancel only keyboard
        """
        keyboard = [
            [
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def help_and_back() -> InlineKeyboardMarkup:
        """
        Keyboard with help and back options.
        
        Returns:
            InlineKeyboardMarkup: Help and back keyboard
        """
        keyboard = [
            [
                InlineKeyboardButton("❓ Ayuda", callback_data="help"),
                InlineKeyboardButton("🔙 Volver", callback_data="back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def refresh_and_back() -> InlineKeyboardMarkup:
        """
        Keyboard with refresh and back options.
        
        Returns:
            InlineKeyboardMarkup: Refresh and back keyboard
        """
        keyboard = [
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data="refresh"),
                InlineKeyboardButton("🔙 Volver", callback_data="back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def navigation_row(back_callback: str = "back", help_callback: str = "help") -> list:
        """
        Standard navigation row for keyboards.
        
        Args:
            back_callback: Callback data for back button
            help_callback: Callback data for help button
            
        Returns:
            list: Navigation row buttons
        """
        return [
            InlineKeyboardButton("❓ Ayuda", callback_data=help_callback),
            InlineKeyboardButton("🔙 Volver", callback_data=back_callback)
        ]

    @staticmethod
    def main_navigation_row() -> list:
        """
        Standard main navigation row.
        
        Returns:
            list: Main navigation row buttons
        """
        return [
            InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu")
        ]

    @staticmethod
    def action_buttons(primary_text: str, primary_callback: str,
                      secondary_text: str = None, secondary_callback: str = None) -> InlineKeyboardMarkup:
        """
        Keyboard with primary and optional secondary action buttons.
        
        Args:
            primary_text: Text for primary button
            primary_callback: Callback data for primary button
            secondary_text: Text for secondary button (optional)
            secondary_callback: Callback data for secondary button (optional)
            
        Returns:
            InlineKeyboardMarkup: Action buttons keyboard
        """
        keyboard = []
        
        # Primary action row
        keyboard.append([
            InlineKeyboardButton(primary_text, callback_data=primary_callback)
        ])
        
        # Secondary action row (if provided)
        if secondary_text and secondary_callback:
            keyboard.append([
                InlineKeyboardButton(secondary_text, callback_data=secondary_callback)
            ])
        
        # Navigation row
        keyboard.append(CommonKeyboards.main_navigation_row())
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def list_navigation(has_next: bool = False, has_prev: bool = False,
                      next_callback: str = "next", prev_callback: str = "prev") -> InlineKeyboardMarkup:
        """
        Navigation keyboard for paginated lists.
        
        Args:
            has_next: Whether there's a next page
            has_prev: Whether there's a previous page
            next_callback: Callback data for next button
            prev_callback: Callback data for previous button
            
        Returns:
            InlineKeyboardMarkup: List navigation keyboard
        """
        keyboard = []
        
        # Pagination row
        nav_row = []
        if has_prev:
            nav_row.append(InlineKeyboardButton("⬅️ Anterior", callback_data=prev_callback))
        if has_next:
            nav_row.append(InlineKeyboardButton("Siguiente ➡️", callback_data=next_callback))
        
        if nav_row:
            keyboard.append(nav_row)
        
        # Back to menu row
        keyboard.append(CommonKeyboards.main_navigation_row())
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def status_actions(is_active: bool, target_id: int, action_prefix: str = "toggle") -> InlineKeyboardMarkup:
        """
        Status toggle keyboard.
        
        Args:
            is_active: Current status
            target_id: ID of the target element
            action_prefix: Prefix for callback data
            
        Returns:
            InlineKeyboardMarkup: Status actions keyboard
        """
        if is_active:
            action_text = "⏸️ Desactivar"
            action_callback = f"{action_prefix}_deactivate_{target_id}"
        else:
            action_text = "✅ Activar"
            action_callback = f"{action_prefix}_activate_{target_id}"
        
        keyboard = [
            [
                InlineKeyboardButton(action_text, callback_data=action_callback)
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="back")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
        """
        Main menu keyboard.

        Args:
            is_admin: Whether to include admin options

        Returns:
            InlineKeyboardMarkup: Main menu keyboard
        """
        keyboard = [
            [
                InlineKeyboardButton("🛡️ Mis Llaves", callback_data="key_management"),
                InlineKeyboardButton("📊 Estado", callback_data="status")
            ],
            [
                InlineKeyboardButton("💰 Operaciones", callback_data="operations"),
                InlineKeyboardButton("🏆 Logros", callback_data="achievements")
            ],
            [
                InlineKeyboardButton("⚙️ Ayuda", callback_data="help")
            ]
        ]

        # Add admin options if applicable
        if is_admin:
            keyboard.insert(0, [
                InlineKeyboardButton("🔧 Panel Admin", callback_data="admin")
            ])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def empty_state(help_callback: str = "help", back_callback: str = "back") -> InlineKeyboardMarkup:
        """
        Keyboard for empty states.

        Args:
            help_callback: Callback data for help button
            back_callback: Callback data for back button

        Returns:
            InlineKeyboardMarkup: Empty state keyboard
        """
        keyboard = [
            [
                InlineKeyboardButton("❓ Ayuda", callback_data=help_callback),
                InlineKeyboardButton("🔄 Actualizar", callback_data="refresh")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data=back_callback)
            ]
        ]

        return InlineKeyboardMarkup(keyboard)
