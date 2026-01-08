"""
Fábrica y utilidades para mensajes del bot uSipipo.

Proporciona:
- Factory pattern para acceso dinámico a mensajes
- Builder pattern para mensajes complejos
- Registry para mensajes predefinidos
- Tipos y enums para mensajes

Author: uSipipo Team
Version: 1.0.0
"""

from enum import Enum
from typing import Any, Dict, Optional, Type, Union
from .user_messages import UserMessages
from .admin_messages import AdminMessages
from .operations_messages import OperationMessages
from .support_messages import SupportMessages, TaskMessages, AchievementMessages
from .common_messages import CommonMessages


# ============================================
# ENUMS
# ============================================

class MessageType(Enum):
    """Tipos de mensajes disponibles."""
    
    USER = "user"
    ADMIN = "admin"
    OPERATIONS = "operations"
    SUPPORT = "support"
    TASKS = "tasks"
    ACHIEVEMENTS = "achievements"
    COMMON = "common"


class MessageCategory(Enum):
    """Categorías de mensajes."""
    
    WELCOME = "welcome"
    KEYS = "keys"
    STATUS = "status"
    HELP = "help"
    BALANCE = "balance"
    VIP = "vip"
    PAYMENTS = "payments"
    REFERRAL = "referral"
    SUPPORT = "support"
    TASKS = "tasks"
    ACHIEVEMENTS = "achievements"
    ERRORS = "errors"
    CONFIRMATION = "confirmation"
    COMMON = "common"


# ============================================
# MESSAGE FACTORY
# ============================================

class MessageFactory:
    """Fábrica para acceso dinámico a mensajes."""
    
    _message_classes: Dict[MessageType, Type] = {
        MessageType.USER: UserMessages,
        MessageType.ADMIN: AdminMessages,
        MessageType.OPERATIONS: OperationMessages,
        MessageType.SUPPORT: SupportMessages,
        MessageType.TASKS: TaskMessages,
        MessageType.ACHIEVEMENTS: AchievementMessages,
        MessageType.COMMON: CommonMessages,
    }
    
    @classmethod
    def get_message_class(cls, message_type: MessageType) -> Type:
        """
        Obtiene la clase de mensajes para un tipo específico.
        
        Args:
            message_type: El tipo de mensaje
            
        Returns:
            La clase de mensajes correspondiente
            
        Raises:
            ValueError: Si el tipo no es válido
        """
        if message_type not in cls._message_classes:
            raise ValueError(f"Tipo de mensaje inválido: {message_type}")
        return cls._message_classes[message_type]
    
    @classmethod
    def get_message(
        cls,
        message_type: MessageType,
        category: str,
        message_name: str,
        **kwargs
    ) -> str:
        """
        Obtiene un mensaje formateado dinámicamente.
        
        Args:
            message_type: El tipo de mensaje (user, admin, etc)
            category: La categoría dentro del tipo (Welcome, Keys, etc)
            message_name: El nombre del mensaje (START, CREATED, etc)
            **kwargs: Variables para formatear el mensaje
            
        Returns:
            El mensaje formateado
            
        Raises:
            AttributeError: Si la categoría o mensaje no existe
        """
        message_class = cls.get_message_class(message_type)
        category_class = getattr(message_class, category)
        message_template = getattr(category_class, message_name)
        
        if isinstance(message_template, str):
            return message_template.format(**kwargs) if kwargs else message_template
        return str(message_template)
    
    @classmethod
    def register_message_class(
        cls,
        message_type: MessageType,
        message_class: Type
    ) -> None:
        """
        Registra una nueva clase de mensajes.
        
        Args:
            message_type: El tipo de mensaje
            message_class: La clase a registrar
        """
        cls._message_classes[message_type] = message_class


# ============================================
# MESSAGE BUILDER
# ============================================

class MessageBuilder:
    """Constructor fluido para mensajes complejos."""
    
    def __init__(self, base_message: str = ""):
        """
        Inicializa el constructor.
        
        Args:
            base_message: Mensaje base para empezar
        """
        self._content = base_message
        self._variables: Dict[str, Any] = {}
    
    def add_header(self, text: str) -> "MessageBuilder":
        """Agrega un encabezado."""
        self._content += f"\n{text}\n{CommonMessages.Formatting.SEPARATOR}\n"
        return self
    
    def add_section(self, title: str, content: str) -> "MessageBuilder":
        """Agrega una sección con título."""
        self._content += f"\n**{title}**\n"
        self._content += content
        return self
    
    def add_line(self, text: str = "") -> "MessageBuilder":
        """Agrega una línea."""
        self._content += text + "\n"
        return self
    
    def add_bullet(self, text: str, level: int = 0) -> "MessageBuilder":
        """Agrega un punto de lista."""
        indent = "   " * level
        self._content += f"{indent}• {text}\n"
        return self
    
    def add_emphasis(self, text: str, style: str = "bold") -> "MessageBuilder":
        """Agrega texto con énfasis."""
        if style == "bold":
            self._content += f"**{text}**\n"
        elif style == "italic":
            self._content += f"*{text}*\n"
        elif style == "code":
            self._content += f"`{text}`\n"
        return self
    
    def add_divider(self) -> "MessageBuilder":
        """Agrega un divisor."""
        self._content += f"{CommonMessages.Formatting.SEPARATOR}\n"
        return self
    
    def add_footer(self, text: str) -> "MessageBuilder":
        """Agrega un pie de página."""
        self._content += f"\n{CommonMessages.Formatting.SEPARATOR}\n{text}"
        return self
    
    def set_variable(self, name: str, value: Any) -> "MessageBuilder":
        """Establece una variable para formateo."""
        self._variables[name] = value
        return self
    
    def build(self) -> str:
        """Construye el mensaje final."""
        return self._content.format(**self._variables) if self._variables else self._content


# ============================================
# MESSAGE REGISTRY
# ============================================

class MessageRegistry:
    """Registro de mensajes predefinidos."""
    
    _registry: Dict[str, str] = {}
    
    @classmethod
    def register(cls, key: str, message: str) -> None:
        """
        Registra un mensaje predefinido.
        
        Args:
            key: Identificador único
            message: El mensaje
        """
        cls._registry[key] = message
    
    @classmethod
    def get(cls, key: str, **kwargs) -> Optional[str]:
        """
        Obtiene un mensaje registrado.
        
        Args:
            key: Identificador del mensaje
            **kwargs: Variables para formatear
            
        Returns:
            El mensaje formateado o None
        """
        if key not in cls._registry:
            return None
        
        message = cls._registry[key]
        return message.format(**kwargs) if kwargs else message
    
    @classmethod
    def has(cls, key: str) -> bool:
        """Verifica si existe un mensaje registrado."""
        return key in cls._registry
    
    @classmethod
    def all(cls) -> Dict[str, str]:
        """Obtiene todos los mensajes registrados."""
        return cls._registry.copy()
    
    @classmethod
    def clear(cls) -> None:
        """Limpia el registro."""
        cls._registry.clear()


# ============================================
# MESSAGE FORMATTER
# ============================================

class MessageFormatter:
    """Utilidades para formateo de mensajes."""
    
    @staticmethod
    def format_list(items: list, bullet: str = "•") -> str:
        """
        Formatea una lista como puntos.
        
        Args:
            items: Los elementos a formatear
            bullet: El símbolo de punto
            
        Returns:
            Lista formateada
        """
        return "\n".join(f"{bullet} {item}" for item in items)
    
    @staticmethod
    def format_table(
        headers: list,
        rows: list,
        separator: str = " | "
    ) -> str:
        """
        Formatea datos como tabla simple.
        
        Args:
            headers: Encabezados de columna
            rows: Filas de datos
            separator: Separador entre columnas
            
        Returns:
            Tabla formateada
        """
        header_row = separator.join(str(h) for h in headers)
        separator_row = separator.join("-" * 10 for _ in headers)
        data_rows = [separator.join(str(cell) for cell in row) for row in rows]
        
        return "\n".join([header_row, separator_row] + data_rows)
    
    @staticmethod
    def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """
        Trunca texto a un máximo de caracteres.
        
        Args:
            text: El texto a truncar
            max_length: Longitud máxima
            suffix: Sufijo al truncar
            
        Returns:
            Texto truncado
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def add_emoji(text: str, emoji: str, position: str = "start") -> str:
        """
        Agrega un emoji al texto.
        
        Args:
            text: El texto
            emoji: El emoji a agregar
            position: 'start' o 'end'
            
        Returns:
            Texto con emoji
        """
        if position == "start":
            return f"{emoji} {text}"
        return f"{text} {emoji}"
    
    @staticmethod
    def highlight(text: str, style: str = "bold") -> str:
        """
        Resalta texto con formato Markdown.
        
        Args:
            text: El texto
            style: 'bold', 'italic' o 'code'
            
        Returns:
            Texto formateado
        """
        if style == "bold":
            return f"**{text}**"
        elif style == "italic":
            return f"*{text}*"
        elif style == "code":
            return f"`{text}`"
        return text


# ============================================
# PREDEFINED MESSAGES
# ============================================

# Registrar mensajes comunes predefinidos
MessageRegistry.register("loading", "⏳ {task}...")
MessageRegistry.register("success", "✅ {message}")
MessageRegistry.register("error", "❌ {message}")
MessageRegistry.register("warning", "⚠️ {message}")
MessageRegistry.register("info", "ℹ️ {message}")
MessageRegistry.register("home", "🏠 {location}")
MessageRegistry.register("back", "⬅️ Volver")
MessageRegistry.register("next", "▶️ Siguiente")
MessageRegistry.register("previous", "◀️ Anterior")
