"""
Teclados para sistema de soporte técnico de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class SupportKeyboards:
    """Teclados para sistema de soporte."""

    @staticmethod
    def support_active() -> InlineKeyboardMarkup:
        """
        Teclado cuando hay un ticket activo.
        
        Returns:
            InlineKeyboardMarkup: Teclado de soporte activo
        """
        keyboard = [
            [
                InlineKeyboardButton("🔴 Finalizar Soporte", callback_data="close_ticket"),
                InlineKeyboardButton("📋 Mis Tickets", callback_data="my_tickets")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú de ayuda.
        
        Returns:
            InlineKeyboardMarkup: Teclado de ayuda
        """
        keyboard = [
            [
                InlineKeyboardButton("🎫 Crear Ticket", callback_data="create_ticket"),
                InlineKeyboardButton("📋 Mis Tickets", callback_data="my_tickets")
            ],
            [
                InlineKeyboardButton("❓ FAQ", callback_data="faq"),
                InlineKeyboardButton("📖 Guía", callback_data="guide")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """
        Teclado para volver al menú principal.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def faq_categories() -> InlineKeyboardMarkup:
        """
        Teclado de categorías de FAQ.
        
        Returns:
            InlineKeyboardMarkup: Teclado de categorías FAQ
        """
        keyboard = [
            [
                InlineKeyboardButton("🌐 Conexión VPN", callback_data="faq_connection"),
                InlineKeyboardButton("👤 Cuenta y Perfil", callback_data="faq_account")
            ],
            [
                InlineKeyboardButton("💰 Pagos y Facturación", callback_data="faq_billing"),
                InlineKeyboardButton("🔧 Problemas Técnicos", callback_data="faq_technical")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def ticket_actions(ticket_id: int, is_open: bool) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para un ticket específico.
        
        Args:
            ticket_id: ID del ticket
            is_open: Si el ticket está abierto
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = []
        
        if is_open:
            keyboard.append([
                InlineKeyboardButton("🔴 Cerrar Ticket", callback_data=f"close_ticket_{ticket_id}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("📊 Ver Detalles", callback_data=f"ticket_details_{ticket_id}")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="my_tickets")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def admin_ticket_actions(ticket_id: int, user_id: int) -> InlineKeyboardMarkup:
        """
        Teclado de acciones administrativas para un ticket.
        
        Args:
            ticket_id: ID del ticket
            user_id: ID del usuario
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones admin
        """
        keyboard = [
            [
                InlineKeyboardButton("💬 Responder", callback_data=f"reply_ticket_{ticket_id}"),
                InlineKeyboardButton("🔒 Cerrar Ticket", callback_data=f"admin_close_{ticket_id}")
            ],
            [
                InlineKeyboardButton("👤 Ver Usuario", callback_data=f"user_info_{user_id}"),
                InlineKeyboardButton("📊 Estadísticas", callback_data=f"ticket_stats_{ticket_id}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin_tickets")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirmation_dialog(action: str, target_id: int) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para acciones críticas.
        
        Args:
            action: Acción a confirmar
            target_id: ID del objetivo
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{action}_{target_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_{action}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def priority_selector() -> InlineKeyboardMarkup:
        """
        Teclado para seleccionar prioridad de ticket.
        
        Returns:
            InlineKeyboardMarkup: Teclado de prioridades
        """
        keyboard = [
            [
                InlineKeyboardButton("🔴 Urgente", callback_data="priority_urgent"),
                InlineKeyboardButton("🟡 Alta", callback_data="priority_high")
            ],
            [
                InlineKeyboardButton("🟠 Media", callback_data="priority_medium"),
                InlineKeyboardButton("🟢 Baja", callback_data="priority_low")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def ticket_list(tickets: list) -> InlineKeyboardMarkup:
        """
        Genera teclado dinámico para lista de tickets.
        
        Args:
            tickets: Lista de tickets
            
        Returns:
            InlineKeyboardMarkup: Teclado de tickets
        """
        keyboard = []
        
        for ticket in tickets:
            status_emoji = "🟢" if ticket.status == "open" else "🔴"
            button_text = f"{status_emoji} Ticket #{ticket.id} - {ticket.subject[:20]}..."
            callback_data = f"ticket_details_{ticket.id}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="help")
        ])
        
        return InlineKeyboardMarkup(keyboard)
