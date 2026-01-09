"""
Repositorio de conversaciones con el asistente IA Sip.

Author: uSipipo Team
Version: 1.0.0
"""

import json
import uuid
from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger

from domain.entities.conversation import Conversation, Message, MessageRole
from .models import ConversationModel


class ConversationRepository:
    """Implementación del repositorio de conversaciones con SQLAlchemy Async."""
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el repositorio con una sesión de base de datos.
        
        Args:
            session: Sesión async de SQLAlchemy.
        """
        self.session = session
    
    def _model_to_entity(self, model: ConversationModel) -> Conversation:
        """Convierte un modelo SQLAlchemy a entidad de dominio."""
        messages = []
        if model.messages:
            try:
                messages_data = json.loads(model.messages)
                for msg_data in messages_data:
                    messages.append(Message(
                        role=MessageRole(msg_data.get("role")),
                        content=msg_data.get("content"),
                        timestamp=msg_data.get("timestamp")
                    ))
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"⚠️ Error decodificando mensajes: {e}")
        
        return Conversation(
            id=uuid.UUID(model.id),
            user_id=model.user_id,
            user_name=model.user_name,
            status=model.status,
            started_at=model.started_at,
            last_activity=model.last_activity,
            messages=messages
        )
    
    def _entity_to_model(self, entity: Conversation) -> ConversationModel:
        """Convierte una entidad de dominio a modelo SQLAlchemy."""
        messages_json = json.dumps([
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in entity.messages
        ])
        
        return ConversationModel(
            id=str(entity.id),
            user_id=entity.user_id,
            user_name=entity.user_name,
            status=entity.status,
            started_at=entity.started_at,
            last_activity=entity.last_activity,
            messages=messages_json
        )
    
    async def get_active_by_user(self, user_id: int) -> Optional[Conversation]:
        """Obtiene la conversación activa de un usuario."""
        try:
            from sqlalchemy import desc
            
            query = select(ConversationModel).where(
                (ConversationModel.user_id == user_id) & 
                (ConversationModel.status == "active")
            ).order_by(desc(ConversationModel.last_activity)).limit(1)
            
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()
            
            if model is None:
                return None
            
            return self._model_to_entity(model)
            
        except Exception as e:
            logger.error(f"❌ Error al obtener conversación activa del usuario {user_id}: {e}")
            return None
    
    async def save(self, conversation: Conversation) -> Conversation:
        """Guarda o actualiza una conversación."""
        try:
            if conversation.id:
                existing = await self.session.get(ConversationModel, str(conversation.id))
                
                if existing:
                    existing.status = conversation.status
                    existing.last_activity = conversation.last_activity
                    existing.messages = json.dumps([
                        {
                            "role": msg.role.value,
                            "content": msg.content,
                            "timestamp": msg.timestamp.isoformat()
                        }
                        for msg in conversation.messages
                    ])
                else:
                    model = self._entity_to_model(conversation)
                    self.session.add(model)
            else:
                conversation.id = uuid.uuid4()
                model = self._entity_to_model(conversation)
                self.session.add(model)
            
            await self.session.commit()
            logger.debug(f"💾 Conversación {conversation.id} guardada correctamente.")
            return conversation
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al guardar conversación: {e}")
            raise
    
    async def get_all_active(self) -> List[Conversation]:
        """Obtiene todas las conversaciones activas."""
        try:
            query = select(ConversationModel).where(ConversationModel.status == "active")
            result = await self.session.execute(query)
            models = result.scalars().all()
            
            return [self._model_to_entity(m) for m in models]
            
        except Exception as e:
            logger.error(f"❌ Error al obtener conversaciones activas: {e}")
            return []
    
    async def close_conversation(self, conversation_id: uuid.UUID) -> bool:
        """Cierra una conversación."""
        try:
            query = (
                update(ConversationModel)
                .where(ConversationModel.id == str(conversation_id))
                .values(status="ended")
            )
            await self.session.execute(query)
            await self.session.commit()
            
            logger.debug(f"✅ Conversación {conversation_id} cerrada.")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al cerrar conversación {conversation_id}: {e}")
            return False
    
    async def escalate_conversation(self, conversation_id: uuid.UUID) -> bool:
        """Escalada una conversación a soporte humano."""
        try:
            query = (
                update(ConversationModel)
                .where(ConversationModel.id == str(conversation_id))
                .values(status="escalated")
            )
            await self.session.execute(query)
            await self.session.commit()
            
            logger.debug(f"✅ Conversación {conversation_id} escalada.")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al escalar conversación {conversation_id}: {e}")
            return False
    
    async def get_by_id(self, conversation_id: uuid.UUID) -> Optional[Conversation]:
        """Obtiene una conversación por su ID."""
        try:
            model = await self.session.get(ConversationModel, str(conversation_id))
            
            if model is None:
                return None
            
            return self._model_to_entity(model)
            
        except Exception as e:
            logger.error(f"❌ Error al obtener conversación {conversation_id}: {e}")
            return None
    
    async def delete_stale_conversations(self, hours: int = 24) -> int:
        """Elimina conversaciones inactivas."""
        try:
            from sqlalchemy import delete
            from datetime import datetime, timedelta
            from utils.datetime_utils import now_utc
            
            cutoff_time = now_utc() - timedelta(hours=hours)
            
            query = (
                delete(ConversationModel)
                .where(ConversationModel.last_activity < cutoff_time)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            
            deleted_count = result.rowcount
            logger.debug(f"🗑️ Eliminadas {deleted_count} conversaciones inactivas.")
            return deleted_count
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al eliminar conversaciones inactivas: {e}")
            return 0
