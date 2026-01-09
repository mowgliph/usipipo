"""
Servicio de aplicación para soporte con IA Sip.

Author: uSipipo Team
Version: 1.0.0
"""

import uuid
from typing import Optional, List

from domain.entities.conversation import Conversation, Message, MessageRole
from domain.interfaces.iai_support_service import IAiSupportService
from infrastructure.persistence.supabase.conversation_repository import ConversationRepository
from infrastructure.api_clients.groq_client import GroqClient
from utils.sip_prompts import get_system_prompt, get_escalation_prompt
from utils.logger import logger


class AiSupportService(IAiSupportService):
    """Servicio de aplicación para soporte con IA Sip."""
    
    def __init__(
        self,
        conversation_repo: ConversationRepository,
        groq_client: GroqClient
    ):
        """
        Inicializa el servicio de IA Sip.
        
        Args:
            conversation_repo: Repositorio de conversaciones
            groq_client: Cliente de API de Groq
        """
        self.conversation_repo = conversation_repo
        self.groq_client = groq_client
        logger.info("🌊 AiSupportService inicializado correctamente")
    
    async def start_conversation(self, user_id: int, user_name: str) -> Conversation:
        """
        Inicia una nueva conversación con Sip.
        
        Args:
            user_id: ID del usuario de Telegram
            user_name: Nombre del usuario
            
        Returns:
            Conversation: Nueva conversación creada
        """
        try:
            conversation = Conversation(
                id=uuid.uuid4(),
                user_id=user_id,
                user_name=user_name
            )
            
            system_message = Message(
                role=MessageRole.SYSTEM,
                content=get_system_prompt()
            )
            conversation.add_message(system_message)
            
            await self.conversation_repo.save(conversation)
            logger.info(f"🌊 Conversación iniciada para usuario {user_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"❌ Error iniciando conversación: {e}")
            raise
    
    async def send_message(self, user_id: int, user_message: str) -> str:
        """
        Envía mensaje de usuario y obtiene respuesta de Sip.
        
        Args:
            user_id: ID del usuario de Telegram
            user_message: Mensaje del usuario
            
        Returns:
            str: Respuesta generada por Sip
        """
        try:
            conversation = await self.conversation_repo.get_active_by_user(user_id)
            if not conversation:
                raise ValueError("No hay conversación activa. Inicia una conversación primero.")
            
            user_msg = Message(role=MessageRole.USER, content=user_message)
            conversation.add_message(user_msg)
            
            messages = self._build_context(conversation)
            
            ai_response = await self.groq_client.chat_completion(messages)
            
            assistant_msg = Message(role=MessageRole.ASSISTANT, content=ai_response)
            conversation.add_message(assistant_msg)
            
            await self.conversation_repo.save(conversation)
            
            if self._should_escalate(user_message, ai_response):
                logger.info(f"🌊 Conversación escalada para usuario {user_id}")
                await self.escalate_conversation(user_id, "Detección automática de escalado")
                return ai_response + "\n\n📝 *Nota: He creado un ticket de soporte para que un especialista te ayude con este problema.*"
            
            logger.debug(f"🌊 Respuesta enviada a usuario {user_id}")
            return ai_response
            
        except ValueError as e:
            logger.warning(f"⚠️ {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            raise Exception(f"Lo siento, tuve problemas procesando tu mensaje. {str(e)}")
    
    async def get_active_conversation(self, user_id: int) -> Optional[Conversation]:
        """
        Obtiene la conversación activa del usuario.
        
        Args:
            user_id: ID del usuario de Telegram
            
        Returns:
            Optional[Conversation]: Conversación activa o None
        """
        try:
            return await self.conversation_repo.get_active_by_user(user_id)
        except Exception as e:
            logger.error(f"❌ Error obteniendo conversación activa: {e}")
            return None
    
    async def end_conversation(self, user_id: int) -> bool:
        """
        Finaliza la conversación activa del usuario.
        
        Args:
            user_id: ID del usuario de Telegram
            
        Returns:
            bool: True si se finalizó correctamente
        """
        try:
            conversation = await self.conversation_repo.get_active_by_user(user_id)
            if not conversation:
                logger.warning(f"⚠️ No hay conversación activa para usuario {user_id}")
                return False
            
            conversation.end_conversation()
            await self.conversation_repo.save(conversation)
            
            logger.info(f"🌊 Conversación finalizada para usuario {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error finalizando conversación: {e}")
            return False
    
    async def escalate_conversation(self, user_id: int, reason: str) -> bool:
        """
        Escala la conversación a soporte humano.
        
        Args:
            user_id: ID del usuario de Telegram
            reason: Razón del escalado
            
        Returns:
            bool: True si se escaló correctamente
        """
        try:
            conversation = await self.conversation_repo.get_active_by_user(user_id)
            if not conversation:
                logger.warning(f"⚠️ No hay conversación activa para usuario {user_id}")
                return False
            
            conversation.escalate_conversation()
            await self.conversation_repo.save(conversation)
            
            logger.info(f"🌊 Conversación escalada para usuario {user_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error escalando conversación: {e}")
            return False
    
    async def get_conversation_history(self, user_id: int, limit: int = 10) -> List[Message]:
        """
        Obtiene el historial de conversación del usuario.
        
        Args:
            user_id: ID del usuario de Telegram
            limit: Límite de mensajes a retornar
            
        Returns:
            List[Message]: Lista de mensajes
        """
        try:
            conversation = await self.conversation_repo.get_active_by_user(user_id)
            if not conversation:
                return []
            
            return conversation.get_recent_messages(limit)
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo historial: {e}")
            return []
    
    async def cleanup_stale_conversations(self, hours: int = 24) -> int:
        """
        Limpia conversaciones inactivas.
        
        Args:
            hours: Horas de inactividad para considerar una conversación como vieja
            
        Returns:
            int: Número de conversaciones limpiadas
        """
        try:
            deleted_count = await self.conversation_repo.delete_stale_conversations(hours)
            logger.info(f"🌊 Limpieza completada: {deleted_count} conversaciones eliminadas")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error en limpieza de conversaciones: {e}")
            return 0
    
    def _build_context(self, conversation: Conversation) -> List[dict]:
        """
        Construye contexto de mensajes para API de Groq.
        
        Args:
            conversation: Conversación actual
            
        Returns:
            List[dict]: Lista de mensajes en formato API
        """
        messages = []
        
        system_message = Message(
            role=MessageRole.SYSTEM,
            content=get_system_prompt()
        )
        messages.append(system_message.to_dict())
        
        recent_messages = conversation.get_recent_messages(10)
        for msg in recent_messages:
            if msg.role != MessageRole.SYSTEM:
                messages.append(msg.to_dict())
        
        return messages
    
    def _should_escalate(self, user_message: str, ai_response: str) -> bool:
        """
        Determina si se debe escalar a soporte humano.
        
        Args:
            user_message: Mensaje del usuario
            ai_response: Respuesta de la IA
            
        Returns:
            bool: True si se debe escalar
        """
        escalation_keywords = [
            "hablar con humano",
            "soporte humano",
            "agente real",
            "persona",
            "ayuda urgente",
            "emergencia",
            "problema grave",
            "no funciona",
            "frustrado",
            "enojado"
        ]
        
        user_message_lower = user_message.lower()
        
        for keyword in escalation_keywords:
            if keyword in user_message_lower:
                return True
        
        if "ticket de soporte" in ai_response.lower():
            return True
        
        return False
