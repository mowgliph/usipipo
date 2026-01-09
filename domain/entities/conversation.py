"""
Entidades de dominio para conversaciones del asistente IA Sip.

Author: uSipipo Team
Version: 1.0.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from enum import Enum
import uuid

from utils.datetime_utils import now_utc


class MessageRole(str, Enum):
    """Roles posibles en una conversación."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """Representa un mensaje en una conversación con Sip."""
    
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=now_utc)
    
    def to_dict(self) -> dict:
        """Convierte el mensaje a formato dict para API."""
        return {
            "role": self.role.value,
            "content": self.content
        }
    
    def __len__(self) -> int:
        """Retorna la longitud del contenido en caracteres."""
        return len(self.content)


@dataclass
class Conversation:
    """Representa una conversación completa con el asistente IA Sip."""
    
    id: uuid.UUID
    user_id: int
    user_name: str
    started_at: datetime = field(default_factory=now_utc)
    last_activity: datetime = field(default_factory=now_utc)
    messages: List[Message] = field(default_factory=list)
    status: str = "active"  # "active" | "ended" | "escalated"
    
    def add_message(self, message: Message) -> None:
        """Agrega un mensaje a la conversación y actualiza timestamp."""
        self.messages.append(message)
        self.last_activity = now_utc()
    
    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Retorna los mensajes más recientes hasta el límite especificado."""
        return self.messages[-limit:] if self.messages else []
    
    def get_context_messages(self, limit: int = 10) -> List[dict]:
        """Retorna mensajes en formato dict para contexto de API."""
        recent = self.get_recent_messages(limit)
        return [msg.to_dict() for msg in recent]
    
    def is_stale(self, hours: int = 24) -> bool:
        """Verifica si la conversación debe cerrarse por inactividad."""
        delta = now_utc() - self.last_activity
        return delta.total_seconds() > (hours * 3600)
    
    def end_conversation(self) -> None:
        """Marca la conversación como terminada."""
        self.status = "ended"
        self.last_activity = now_utc()
    
    def escalate_conversation(self) -> None:
        """Marca la conversación como escalada a soporte humano."""
        self.status = "escalated"
        self.last_activity = now_utc()
    
    def get_message_count(self) -> int:
        """Retorna el total de mensajes en la conversación."""
        return len(self.messages)
    
    def get_total_tokens_estimate(self) -> int:
        """Estima el total de tokens en la conversación."""
        total_chars = sum(len(msg.content) for msg in self.messages)
        return int(total_chars / 4)
