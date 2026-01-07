"""
Fábrica centralizada y métodos helper para teclados del bot uSipipo.

Proporciona utilidades para:
- Generar teclados dinámicamente
- Acceso centralizado a métodos de teclado
- Funciones helper para casos comunes
- Factory pattern para construcción de teclados

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum

# Import all keyboard classes
from .user_keyboards import UserKeyboards
from .admin_keyboards import AdminKeyboards
from .operations_keyboards import OperationKeyboards, SupportKeyboards, TaskKeyboards
from .common_keyboards import CommonKeyboards


class KeyboardType(Enum):
    """Enumeración de tipos de teclados disponibles."""
    USER = "user"
    ADMIN = "admin"
    OPERATIONS = "operations"
    SUPPORT = "support"
    TASKS = "tasks"
    COMMON = "common"


class KeyboardFactory:
    """
    Fábrica centralizada para acceder a todos los métodos de teclado.
    
    Proporciona un punto único de acceso a todos los teclados del bot,
    facilita la inyección de dependencias y permite extender fácilmente.
    """
    
    # Mapeo de clases de teclado
    _keyboard_classes: Dict[KeyboardType, type] = {
        KeyboardType.USER: UserKeyboards,
        KeyboardType.ADMIN: AdminKeyboards,
        KeyboardType.OPERATIONS: OperationKeyboards,
        KeyboardType.SUPPORT: SupportKeyboards,
        KeyboardType.TASKS: TaskKeyboards,
        KeyboardType.COMMON: CommonKeyboards,
    }
    
    @classmethod
    def get_keyboard_class(cls, keyboard_type: KeyboardType) -> type:
        """
        Obtiene la clase de teclado para un tipo específico.
        
        Args:
            keyboard_type: Tipo de teclado
            
        Returns:
            Clase de teclado correspondiente
            
        Raises:
            ValueError: Si el tipo de teclado no existe
        """
        if keyboard_type not in cls._keyboard_classes:
            raise ValueError(f"Keyboard type '{keyboard_type}' not found")
        return cls._keyboard_classes[keyboard_type]
    
    @classmethod
    def get_keyboard_method(cls, keyboard_type: KeyboardType, method_name: str) -> Callable:
        """
        Obtiene un método específico de una clase de teclado.
        
        Args:
            keyboard_type: Tipo de teclado
            method_name: Nombre del método
            
        Returns:
            El método callable
            
        Raises:
            AttributeError: Si el método no existe
            ValueError: Si el tipo de teclado no existe
        """
        keyboard_class = cls.get_keyboard_class(keyboard_type)
        method = getattr(keyboard_class, method_name, None)
        
        if method is None:
            raise AttributeError(
                f"Method '{method_name}' not found in {keyboard_class.__name__}"
            )
        
        return method
    
    @classmethod
    def create_keyboard(
        cls,
        keyboard_type: KeyboardType,
        method_name: str,
        **kwargs
    ) -> InlineKeyboardMarkup:
        """
        Factory method para crear teclados dinámicamente.
        
        Args:
            keyboard_type: Tipo de teclado
            method_name: Nombre del método a llamar
            **kwargs: Argumentos para pasarle al método
            
        Returns:
            InlineKeyboardMarkup del teclado creado
        """
        method = cls.get_keyboard_method(keyboard_type, method_name)
        return method(**kwargs)
    
    @classmethod
    def create_multiple(
        cls,
        keyboards: List[tuple]
    ) -> Dict[str, InlineKeyboardMarkup]:
        """
        Crea múltiples teclados a la vez.
        
        Args:
            keyboards: Lista de tuplas (nombre, keyboard_type, method_name, kwargs)
            
        Returns:
            Diccionario con los teclados creados {nombre: InlineKeyboardMarkup}
        """
        result = {}
        
        for item in keyboards:
            name = item[0]
            keyboard_type = item[1]
            method_name = item[2]
            kwargs = item[3] if len(item) > 3 else {}
            
            result[name] = cls.create_keyboard(keyboard_type, method_name, **kwargs)
        
        return result


class KeyboardBuilder:
    """
    Constructor fluido para crear teclados complejos.
    
    Facilita la creación programática de teclados con una interfaz más limpia.
    """
    
    def __init__(self):
        """Inicializa el constructor."""
        self.keyboard: List[List[InlineKeyboardButton]] = []
    
    def add_button(
        self,
        text: str,
        callback_data: str,
        emoji: str = ""
    ) -> "KeyboardBuilder":
        """
        Añade un botón simple en su propia fila.
        
        Args:
            text: Texto del botón
            callback_data: Callback del botón
            emoji: Emoji opcional para anteponer al texto
        """
        button_text = f"{emoji} {text}" if emoji else text
        button = InlineKeyboardButton(button_text, callback_data=callback_data)
        self.keyboard.append([button])
        return self
    
    def add_row(
        self,
        buttons: List[tuple]
    ) -> "KeyboardBuilder":
        """
        Añade una fila completa de botones.
        
        Args:
            buttons: Lista de tuplas (texto, callback_data) o (emoji, texto, callback_data)
        """
        row = []
        for button_data in buttons:
            if len(button_data) == 2:
                text, callback = button_data
                row.append(InlineKeyboardButton(text, callback_data=callback))
            elif len(button_data) == 3:
                emoji, text, callback = button_data
                row.append(InlineKeyboardButton(f"{emoji} {text}", callback_data=callback))
        
        if row:
            self.keyboard.append(row)
        return self
    
    def add_back_button(
        self,
        target: str = "main_menu",
        text: str = "🔙 Volver"
    ) -> "KeyboardBuilder":
        """
        Añade un botón de volver.
        
        Args:
            target: Callback del botón de volver
            text: Texto del botón
        """
        self.keyboard.append([InlineKeyboardButton(text, callback_data=target)])
        return self
    
    def add_confirmation_buttons(
        self,
        yes_callback: str,
        no_callback: str,
        yes_text: str = "✅ Confirmar",
        no_text: str = "❌ Cancelar"
    ) -> "KeyboardBuilder":
        """
        Añade botones de confirmación.
        
        Args:
            yes_callback: Callback para confirmar
            no_callback: Callback para cancelar
            yes_text: Texto del botón de confirmación
            no_text: Texto del botón de cancelación
        """
        row = [
            InlineKeyboardButton(yes_text, callback_data=yes_callback),
            InlineKeyboardButton(no_text, callback_data=no_callback)
        ]
        self.keyboard.append(row)
        return self
    
    def add_pagination(
        self,
        page: int,
        total_pages: int,
        callback_prefix: str
    ) -> "KeyboardBuilder":
        """
        Añade botones de paginación.
        
        Args:
            page: Página actual
            total_pages: Total de páginas
            callback_prefix: Prefijo para los callbacks
        """
        pagination_buttons = CommonKeyboards.simple_pagination(page, total_pages, callback_prefix)
        if pagination_buttons:
            self.keyboard.append(pagination_buttons)
        return self
    
    def build(self) -> InlineKeyboardMarkup:
        """
        Construye el teclado final.
        
        Returns:
            InlineKeyboardMarkup con el teclado construido
        """
        return InlineKeyboardMarkup(self.keyboard)
    
    def clear(self) -> "KeyboardBuilder":
        """
        Limpia el constructor para reutilizarlo.
        
        Returns:
            self para encadenamiento
        """
        self.keyboard = []
        return self


class KeyboardRegistry:
    """
    Registro global de teclados predefinidos.
    
    Permite registrar teclados predefinidos y accederlos por nombre,
    facilitando la reutilización y el mantenimiento centralizado.
    """
    
    _keyboards: Dict[str, Union[Callable, InlineKeyboardMarkup]] = {}
    
    @classmethod
    def register(
        cls,
        name: str,
        keyboard: Union[Callable, InlineKeyboardMarkup]
    ) -> None:
        """
        Registra un teclado predefinido.
        
        Args:
            name: Nombre único del teclado
            keyboard: Callable que retorna InlineKeyboardMarkup o InlineKeyboardMarkup directa
        """
        cls._keyboards[name] = keyboard
    
    @classmethod
    def get(
        cls,
        name: str,
        **kwargs
    ) -> InlineKeyboardMarkup:
        """
        Obtiene un teclado registrado.
        
        Args:
            name: Nombre del teclado
            **kwargs: Argumentos si el teclado es callable
            
        Returns:
            InlineKeyboardMarkup
            
        Raises:
            KeyError: Si el teclado no está registrado
        """
        if name not in cls._keyboards:
            raise KeyError(f"Keyboard '{name}' not registered")
        
        keyboard = cls._keyboards[name]
        
        if callable(keyboard):
            return keyboard(**kwargs)
        return keyboard
    
    @classmethod
    def register_multiple(
        cls,
        keyboards: Dict[str, Union[Callable, InlineKeyboardMarkup]]
    ) -> None:
        """
        Registra múltiples teclados a la vez.
        
        Args:
            keyboards: Diccionario {nombre: teclado}
        """
        cls._keyboards.update(keyboards)
    
    @classmethod
    def list_keyboards(cls) -> List[str]:
        """
        Lista todos los teclados registrados.
        
        Returns:
            Lista de nombres de teclados
        """
        return list(cls._keyboards.keys())
    
    @classmethod
    def clear(cls) -> None:
        """Limpia todos los teclados registrados."""
        cls._keyboards.clear()


# Registro de teclados comunes
_common_keyboards = {
    # User keyboards
    "user_main_menu": lambda is_admin=False: UserKeyboards.main_menu(is_admin),
    "user_vpn_types": UserKeyboards.vpn_types,
    "user_back_button": lambda target="main_menu": UserKeyboards.back_button(target),
    
    # Admin keyboards
    "admin_main_menu": AdminKeyboards.main_menu,
    "admin_users_submenu": AdminKeyboards.users_submenu,
    
    # Operations keyboards
    "operations_menu": lambda user=None: OperationKeyboards.operations_menu(user),
    "vip_plans": OperationKeyboards.vip_plans,
    "achievements_menu": OperationKeyboards.achievements_menu,
    "games_menu": OperationKeyboards.games_menu,
    
    # Support keyboards
    "support_menu": SupportKeyboards.support_menu,
    "help_menu": SupportKeyboards.help_menu,
    
    # Task keyboards
    "task_center_menu": TaskKeyboards.task_center_menu,
    "admin_task_menu": TaskKeyboards.admin_task_menu,
    
    # Common keyboards
    "back_button": lambda target="main_menu": CommonKeyboards.back_button(target),
    "empty_keyboard": CommonKeyboards.empty_keyboard,
}

# Registrar los teclados comunes
KeyboardRegistry.register_multiple(_common_keyboards)
