"""
Interfaz de dominio para el servicio de soporte con IA Sip.

Author: uSipipo Team
Version: 1.0.0
"""

from typing import Protocol, Optional
from domain.entities.conversation import Conversation, Message


class IAiSupportService(Protocol):
    """Contrato para el servicio de soporte con IA Sip."""
    
    async def start_conversation(self, user_id: int, user_name: str) -> Conversation:
        """
        Inicia una nueva conversación con Sip.
        
        Args:
            user_id: ID del usuario de Telegram
            user_name: Nombre del usuario
            
        Returns:
            Conversation: Nueva conversación creada
        """
        ...
    
    async def send_message(self, user_id: int, user_message: str) -> str:
        """
        Envía mensaje de usuario y obtiene respuesta de Sip.
        
        Args:
            user_id: ID del usuario de Telegram
            user_message: Mensaje del usuario
            
        Returns:
            str: Respuesta generada por Sip
        """
        ...
    
    async def get_active_conversation(self, user_id: int) -> Optional[Conversation]:
        """
        Obtiene la conversación activa del usuario.
        
        Args:
            user_id: ID del usuario de Telegram
            
        Returns:
            Optional[Conversation]: Conversación activa o None
        """
        ...
    
    async def end_conversation(self, user_id: int) -> bool:
        """
        Finaliza la conversación activa del usuario.
        
        Args:
            user_id: ID del usuario de Telegram
            
        Returns:
            bool: True si se finalizó correctamente
        """
        ...
    
    async def escalate_conversation(self, user_id: int, reason: str) -> bool:
        """
        Escala la conversación a soporte humano.
        
        Args:
            user_id: ID del usuario de Telegram
            reason: Razón del escalado
            
        Returns:
            bool: True si se escaló correctamente
        """
        ...
    
    async def get_conversation_history(self, user_id: int, limit: int = 10) -> list[Message]:
        """
        Obtiene el historial de conversación del usuario.
        
        Args:
            user_id: ID del usuario de Telegram
            limit: Límite de mensajes a retornar
            
        Returns:
            list[Message]: Lista de mensajes
        """
        ...
    
    async def cleanup_stale_conversations(self, hours: int = 24) -> int:
        """
        Limpia conversaciones inactivas.
        
        Args:
            hours: Horas de inactividad para considerar una conversación como vieja
            
        Returns:
            int: Número de conversaciones limpiadas
        """
        ...
