"""
Teclados comunes y reutilizables para el bot uSipipo.

Proporciona patrones generales para:
- Confirmaciones
- Navegación
- Diálogos genéricos
- Acciones comunes

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any, Optional


class CommonKeyboards:
    """Teclados comunes y reutilizables a través del bot."""
    
    # ============================================
    # CONFIRMATION DIALOGS
    # ============================================
    
    @staticmethod
    def generic_confirmation(
        action: str,
        item_id: str = "",
        back_callback: str = "main_menu",
        yes_text: str = "✅ Confirmar",
        no_text: str = "❌ Cancelar"
    ) -> InlineKeyboardMarkup:
        """
        Confirmación genérica de acciones reutilizable.
        
        Args:
            action: Tipo de acción a confirmar
            item_id: ID del elemento (opcional)
            back_callback: Callback para volver atrás
            yes_text: Texto del botón de confirmación
            no_text: Texto del botón de cancelación
        """
        callback_yes = f"confirm_{action}_{item_id}" if item_id else f"confirm_{action}"
        callback_no = f"cancel_{action}"
        
        keyboard = [
            [
                InlineKeyboardButton(yes_text, callback_data=callback_yes),
                InlineKeyboardButton(no_text, callback_data=back_callback)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def yes_no_dialog(
        yes_callback: str,
        no_callback: str,
        yes_text: str = "✅ Sí",
        no_text: str = "❌ No"
    ) -> InlineKeyboardMarkup:
        """
        Diálogo simple sí/no con callbacks personalizados.
        
        Args:
            yes_callback: Callback al presionar sí
            no_callback: Callback al presionar no
            yes_text: Texto del botón de sí
            no_text: Texto del botón de no
        """
        keyboard = [
            [
                InlineKeyboardButton(yes_text, callback_data=yes_callback),
                InlineKeyboardButton(no_text, callback_data=no_callback)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def delete_confirmation(
        item_name: str,
        delete_callback: str,
        cancel_callback: str,
        item_id: str = ""
    ) -> InlineKeyboardMarkup:
        """
        Confirmación especializada para eliminaciones.
        
        Args:
            item_name: Nombre del elemento a eliminar
            delete_callback: Callback para confirmar eliminación
            cancel_callback: Callback para cancelar
            item_id: ID del elemento
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    f"🗑️ Sí, eliminar {item_name}",
                    callback_data=delete_callback
                ),
                InlineKeyboardButton(
                    "❌ Cancelar",
                    callback_data=cancel_callback
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # NAVIGATION
    # ============================================
    
    @staticmethod
    def back_button(target: str = "main_menu", text: str = "🔙 Volver") -> InlineKeyboardMarkup:
        """
        Botón de volver genérico.
        
        Args:
            target: Callback del destino
            text: Texto del botón
        """
        keyboard = [
            [InlineKeyboardButton(text, callback_data=target)]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def double_back_button(
        back1_text: str = "🔙 Volver",
        back1_callback: str = "main_menu",
        back2_text: str = "🏠 Menú Principal",
        back2_callback: str = "main_menu"
    ) -> InlineKeyboardMarkup:
        """
        Dos botones de navegación en una sola fila.
        
        Args:
            back1_text: Texto del primer botón
            back1_callback: Callback del primer botón
            back2_text: Texto del segundo botón
            back2_callback: Callback del segundo botón
        """
        keyboard = [
            [
                InlineKeyboardButton(back1_text, callback_data=back1_callback),
                InlineKeyboardButton(back2_text, callback_data=back2_callback)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # PAGINATION
    # ============================================
    
    @staticmethod
    def pagination_buttons(
        page: int,
        total_pages: int,
        callback_prefix: str
    ) -> List[InlineKeyboardButton]:
        """
        Construye botones de paginación reutilizables.
        
        Args:
            page: Página actual
            total_pages: Total de páginas
            callback_prefix: Prefijo para los callbacks (ej: 'users_page')
            
        Returns:
            Lista de botones para la fila de paginación
        """
        buttons = []
        
        if page > 1:
            buttons.append(
                InlineKeyboardButton("⬅️ Anterior", callback_data=f"{callback_prefix}_{page-1}")
            )
        
        buttons.append(
            InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="noop")
        )
        
        if page < total_pages:
            buttons.append(
                InlineKeyboardButton("Siguiente ➡️", callback_data=f"{callback_prefix}_{page+1}")
            )
        
        return buttons
    
    @staticmethod
    def simple_pagination(
        page: int,
        total_pages: int,
        callback_prefix: str
    ) -> List[InlineKeyboardButton]:
        """
        Construye botones de paginación simples (solo flechas).
        
        Args:
            page: Página actual
            total_pages: Total de páginas
            callback_prefix: Prefijo para los callbacks
            
        Returns:
            Lista de botones para la fila de paginación
        """
        buttons = []
        
        if page > 1:
            buttons.append(
                InlineKeyboardButton("⬅️", callback_data=f"{callback_prefix}_{page-1}")
            )
        
        buttons.append(
            InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop")
        )
        
        if page < total_pages:
            buttons.append(
                InlineKeyboardButton("➡️", callback_data=f"{callback_prefix}_{page+1}")
            )
        
        return buttons
    
    # ============================================
    # GENERIC LISTS
    # ============================================
    
    @staticmethod
    def button_list(
        items: List[Dict[str, str]],
        back_callback: str = "main_menu",
        max_buttons_per_row: int = 1
    ) -> InlineKeyboardMarkup:
        """
        Genera un teclado a partir de una lista de items.
        
        Args:
            items: Lista de dicts con 'text' y 'callback_data'
            back_callback: Callback del botón de volver
            max_buttons_per_row: Máximo de botones por fila
            
        Returns:
            InlineKeyboardMarkup con los botones
        """
        keyboard = []
        
        # Agrupar botones por filas
        for i in range(0, len(items), max_buttons_per_row):
            row = []
            for j in range(max_buttons_per_row):
                if i + j < len(items):
                    item = items[i + j]
                    row.append(InlineKeyboardButton(
                        item['text'],
                        callback_data=item['callback_data']
                    ))
            if row:
                keyboard.append(row)
        
        # Botón de volver
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data=back_callback)])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def choice_buttons(
        choices: Dict[str, str],
        back_callback: str = "main_menu",
        max_buttons_per_row: int = 2
    ) -> InlineKeyboardMarkup:
        """
        Genera un teclado de opciones a elegir.
        
        Args:
            choices: Dict con {texto: callback_data}
            back_callback: Callback del botón de volver
            max_buttons_per_row: Máximo de botones por fila
        """
        items = [
            {'text': text, 'callback_data': callback}
            for text, callback in choices.items()
        ]
        
        return CommonKeyboards.button_list(items, back_callback, max_buttons_per_row)
    
    # ============================================
    # ACTION BUTTONS
    # ============================================
    
    @staticmethod
    def action_buttons(
        actions: List[tuple],
        back_callback: str = "main_menu"
    ) -> InlineKeyboardMarkup:
        """
        Genera botones de acciones con emojis.
        
        Args:
            actions: Lista de tuplas (emoji + texto, callback)
            back_callback: Callback del botón de volver
        """
        keyboard = []
        
        for action_text, callback in actions:
            keyboard.append([
                InlineKeyboardButton(action_text, callback_data=callback)
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data=back_callback)])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def two_column_buttons(
        left_text: str,
        left_callback: str,
        right_text: str,
        right_callback: str,
        bottom_text: Optional[str] = None,
        bottom_callback: Optional[str] = None
    ) -> InlineKeyboardMarkup:
        """
        Genera un teclado con dos botones en la primera fila y opcionalmente uno en la segunda.
        
        Args:
            left_text: Texto del botón izquierdo
            left_callback: Callback del botón izquierdo
            right_text: Texto del botón derecho
            right_callback: Callback del botón derecho
            bottom_text: Texto del botón inferior (opcional)
            bottom_callback: Callback del botón inferior (opcional)
        """
        keyboard = [
            [
                InlineKeyboardButton(left_text, callback_data=left_callback),
                InlineKeyboardButton(right_text, callback_data=right_callback)
            ]
        ]
        
        if bottom_text and bottom_callback:
            keyboard.append([
                InlineKeyboardButton(bottom_text, callback_data=bottom_callback)
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # SPECIAL KEYBOARDS
    # ============================================
    
    @staticmethod
    def loading_keyboard() -> InlineKeyboardMarkup:
        """Teclado con indicador de carga."""
        keyboard = [
            [InlineKeyboardButton("⏳ Procesando...", callback_data="noop")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def empty_keyboard() -> InlineKeyboardMarkup:
        """Teclado vacío para limpiar interfaz."""
        return InlineKeyboardMarkup([])
    
    @staticmethod
    def noop_button(text: str = "⏳") -> InlineKeyboardMarkup:
        """Botón sin acción (para información o decoración)."""
        keyboard = [[InlineKeyboardButton(text, callback_data="noop")]]
        return InlineKeyboardMarkup(keyboard)
