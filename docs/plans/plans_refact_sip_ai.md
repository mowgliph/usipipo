# Revisión Completa de la Implementación del Asistente IA Sip

Voy a analizar **toda la cadena** de la implementación, desde la configuración hasta los handlers, identificando todos los problemas y proporcionando las correcciones.

---

## 1️⃣ `config.py` - Configuración

### ❌ Problemas Encontrados:
```python
# Línea ~150-180
GROQ_MAX_TOKENS: int = Field(
    default=4096,
    description="Tokens máximos de respuesta"
)
```

### ✅ Corrección:
```python
# En config.py, sección GROQ IA API

GROQ_API_KEY: str = Field(
    default="",
    min_length=1,  # Agregar validación mínima
    description="API Key de Groq para el asistente IA Sip"
)

GROQ_MODEL: str = Field(
    default="llama-3.3-70b-versatile",  # Modelo más estable por defecto
    description="Modelo de IA: openai/gpt-oss-120b, llama-3.3-70b-versatile, llama-3.1-8b-instant"
)

GROQ_MAX_TOKENS: int = Field(
    default=2048,  # Reducir para respuestas más rápidas
    ge=100,
    le=8000,
    description="Máximo de tokens en respuesta (max_completion_tokens en API)"
)

GROQ_TEMPERATURE: float = Field(
    default=0.7,
    ge=0.0,
    le=2.0,
    description="Temperatura: 0.0=determinista, 1.0=balanceado, 2.0=creativo"
)

GROQ_TIMEOUT: int = Field(
    default=60,  # Aumentar timeout
    ge=10,
    le=120,
    description="Timeout en segundos para peticiones a Groq API"
)

# Agregar nuevo campo para reasoning
GROQ_REASONING_EFFORT: str = Field(
    default="medium",
    description="Esfuerzo de razonamiento: none, low, medium, high (solo para modelos compatibles)"
)
```

---

## 2️⃣ `groq_client.py` - Cliente API (REESCRITURA COMPLETA)

```python
"""
Cliente de infraestructura para la API de Groq - Asistente IA Sip.

Documentación oficial: https://console.groq.com/docs/api-reference#chat-create

Author: uSipipo Team
Version: 3.0.0
"""

from typing import List, Dict, Optional, Any
import httpx
from groq import Groq, AsyncGroq
from groq import RateLimitError, APIConnectionError, APIStatusError, AuthenticationError

from config import settings
from utils.logger import logger


class GroqClient:
    """Cliente de infraestructura para API de Groq."""
    
    # Configuración de modelos según documentación oficial
    MODELS_CONFIG = {
        "openai/gpt-oss-120b": {
            "description": "GPT OSS 120B - High capability agentic model",
            "context_window": 131072,
            "supports_reasoning": True,
            "reasoning_values": ["low", "medium", "high"],
        },
        "openai/gpt-oss-20b": {
            "description": "GPT OSS 20B - Fast agentic model", 
            "context_window": 131072,
            "supports_reasoning": True,
            "reasoning_values": ["low", "medium", "high"],
        },
        "llama-3.3-70b-versatile": {
            "description": "Llama 3.3 70B - Versatile and reliable",
            "context_window": 131072,
            "supports_reasoning": False,
        },
        "llama-3.1-8b-instant": {
            "description": "Llama 3.1 8B - Fast instant responses",
            "context_window": 131072,
            "supports_reasoning": False,
        },
        "mixtral-8x7b-32768": {
            "description": "Mixtral 8x7B - Mixture of experts",
            "context_window": 32768,
            "supports_reasoning": False,
        },
    }
    
    def __init__(self):
        """Inicializa el cliente de Groq con configuración validada."""
        
        # 1. Validar API Key
        if not settings.GROQ_API_KEY or len(settings.GROQ_API_KEY) < 10:
            error_msg = "GROQ_API_KEY no está configurada o es inválida"
            logger.critical(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        # 2. Configurar modelo
        self.model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"
        self.model_config = self.MODELS_CONFIG.get(self.model, {})
        
        if not self.model_config:
            logger.warning(f"⚠️ Modelo '{self.model}' no está en la lista conocida. Usando configuración por defecto.")
            self.model_config = {"supports_reasoning": False, "context_window": 8192}
        
        # 3. Configurar parámetros
        self.temperature = settings.GROQ_TEMPERATURE
        self.max_completion_tokens = settings.GROQ_MAX_TOKENS
        self.supports_reasoning = self.model_config.get("supports_reasoning", False)
        
        # 4. Configurar timeout a nivel de cliente HTTP
        timeout_seconds = float(settings.GROQ_TIMEOUT)
        self.timeout_config = httpx.Timeout(
            timeout=timeout_seconds,
            connect=15.0,
            read=timeout_seconds,
            write=30.0
        )
        
        # 5. Crear clientes
        try:
            self.client = Groq(
                api_key=settings.GROQ_API_KEY,
                timeout=self.timeout_config
            )
            self.async_client = AsyncGroq(
                api_key=settings.GROQ_API_KEY,
                timeout=self.timeout_config
            )
        except Exception as e:
            logger.critical(f"❌ Error creando cliente Groq: {e}")
            raise
        
        # 6. Log de inicialización
        logger.info("🌊 GroqClient inicializado correctamente")
        logger.info(f"   📦 Modelo: {self.model}")
        logger.info(f"   🧠 Soporta reasoning: {self.supports_reasoning}")
        logger.info(f"   🎯 Temperature: {self.temperature}")
        logger.info(f"   📊 Max tokens: {self.max_completion_tokens}")
        logger.info(f"   ⏱️ Timeout: {timeout_seconds}s")

    def _build_api_params(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Construye los parámetros para la API según la documentación oficial.
        
        Args:
            messages: Lista de mensajes del chat
            
        Returns:
            Dict con parámetros válidos para la API
        """
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_completion_tokens": self.max_completion_tokens,  # ✅ Correcto (no max_tokens)
        }
        
        # Agregar reasoning_effort solo si el modelo lo soporta
        if self.supports_reasoning:
            reasoning_effort = getattr(settings, 'GROQ_REASONING_EFFORT', 'medium')
            valid_values = self.model_config.get("reasoning_values", ["low", "medium", "high"])
            
            if reasoning_effort in valid_values:
                params["reasoning_effort"] = reasoning_effort
                logger.debug(f"🧠 Reasoning effort: {reasoning_effort}")
            else:
                params["reasoning_effort"] = "medium"  # Default seguro
        
        return params

    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """
        Genera una respuesta de chat asíncrona.
        
        Args:
            messages: Lista de mensajes [{"role": "system/user/assistant", "content": "..."}]
            
        Returns:
            str: Respuesta generada por el modelo
            
        Raises:
            ValueError: Si hay error de validación
            Exception: Para otros errores
        """
        if not messages:
            logger.warning("⚠️ Lista de mensajes vacía")
            return "No recibí ningún mensaje para procesar."
        
        try:
            # Log de debug
            logger.debug(f"📤 Enviando {len(messages)} mensajes a Groq")
            logger.debug(f"📤 Primer mensaje: {messages[0].get('role', 'unknown')}")
            if len(messages) > 1:
                logger.debug(f"📤 Último mensaje: {messages[-1].get('content', '')[:50]}...")
            
            # Construir parámetros
            api_params = self._build_api_params(messages)
            
            # Realizar petición
            completion = await self.async_client.chat.completions.create(**api_params)
            
            # Validar respuesta
            if not completion.choices or len(completion.choices) == 0:
                logger.error("❌ Groq no devolvió ninguna opción de respuesta")
                return "Lo siento, no pude generar una respuesta. Intenta reformular tu pregunta."
            
            response_content = completion.choices[0].message.content
            
            if not response_content or response_content.strip() == "":
                logger.error("❌ Groq devolvió contenido vacío")
                return "Lo siento, la respuesta está vacía. Por favor, intenta de nuevo."
            
            # Log de tokens usados
            if hasattr(completion, 'usage') and completion.usage:
                usage = completion.usage
                logger.info(
                    f"💰 Tokens: prompt={usage.prompt_tokens}, "
                    f"completion={usage.completion_tokens}, "
                    f"total={usage.total_tokens}"
                )
            
            logger.debug(f"✅ Respuesta exitosa: {len(response_content)} caracteres")
            return response_content

        except AuthenticationError as e:
            logger.error(f"🔐 Error de autenticación: {e}")
            raise ValueError("Error de autenticación con el servicio de IA. Contacta al administrador.")

        except RateLimitError as e:
            logger.warning(f"⚠️ Rate limit excedido: {e}")
            raise ValueError("El servicio de IA está muy ocupado. Por favor, espera unos segundos.")

        except APIConnectionError as e:
            logger.error(f"🌐 Error de conexión: {e}")
            raise ValueError("No se pudo conectar con el servicio de IA. Verifica tu conexión.")

        except APIStatusError as e:
            logger.error(f"❌ Error de API (HTTP {e.status_code}): {e.message}")
            
            error_messages = {
                400: "Solicitud inválida. Por favor, reformula tu pregunta.",
                401: "Error de autenticación. Contacta al administrador.",
                403: "Acceso denegado al servicio de IA.",
                404: f"El modelo '{self.model}' no está disponible.",
                429: "Demasiadas solicitudes. Espera un momento.",
                500: "Error interno del servidor de IA.",
                503: "El servicio de IA no está disponible temporalmente.",
            }
            
            error_msg = error_messages.get(e.status_code, f"Error del servicio (código {e.status_code})")
            raise ValueError(error_msg)

        except httpx.TimeoutException as e:
            logger.error(f"⏱️ Timeout: {e}")
            raise ValueError("La respuesta tardó demasiado. Intenta con una pregunta más corta.")

        except Exception as e:
            logger.error(f"❌ Error inesperado ({type(e).__name__}): {e}")
            raise ValueError(f"Error inesperado: {str(e)[:100]}")

    def chat_completion_sync(self, messages: List[Dict[str, str]]) -> str:
        """Versión síncrona de chat_completion."""
        if not messages:
            return "No recibí ningún mensaje para procesar."
        
        try:
            api_params = self._build_api_params(messages)
            completion = self.client.chat.completions.create(**api_params)
            
            if completion.choices and len(completion.choices) > 0:
                content = completion.choices[0].message.content
                if content:
                    return content
            
            return "No se pudo generar una respuesta."
            
        except Exception as e:
            logger.error(f"❌ [SYNC] Error: {e}")
            return f"Error: {str(e)[:100]}"

    def validate_api_key(self) -> bool:
        """Valida si la API key está configurada."""
        return bool(settings.GROQ_API_KEY and len(settings.GROQ_API_KEY) > 20)

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna información del modelo configurado."""
        return {
            "model": self.model,
            "description": self.model_config.get("description", "Modelo personalizado"),
            "context_window": self.model_config.get("context_window", "N/A"),
            "supports_reasoning": self.supports_reasoning,
            "temperature": self.temperature,
            "max_completion_tokens": self.max_completion_tokens,
            "api_key_valid": self.validate_api_key(),
        }

    async def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con Groq API.
        
        Returns:
            Dict con resultado del test
        """
        result = {
            "success": False,
            "model": self.model,
            "response": None,
            "error": None,
            "tokens_used": 0,
        }
        
        try:
            logger.info("🧪 Probando conexión con Groq API...")
            
            test_messages = [
                {"role": "user", "content": "Responde únicamente con la palabra 'OK'."}
            ]
            
            response = await self.chat_completion(test_messages)
            
            result["success"] = True
            result["response"] = response[:100]
            
            logger.info(f"✅ Test exitoso. Respuesta: {response[:50]}")
            
        except ValueError as e:
            result["error"] = str(e)
            logger.error(f"❌ Test fallido: {e}")
            
        except Exception as e:
            result["error"] = f"Error inesperado: {str(e)}"
            logger.error(f"❌ Test fallido: {e}")
        
        return result

    def get_available_models(self) -> Dict[str, Dict]:
        """Retorna todos los modelos disponibles."""
        return self.MODELS_CONFIG
```

---

## 3️⃣ `conversation.py` - Entidad de Dominio

### ❌ Problemas:
- El método `to_dict()` no incluye timestamp en formato ISO correcto para serialización

### ✅ Corrección:
```python
"""
Entidades de dominio para conversaciones del asistente IA Sip.

Author: uSipipo Team
Version: 1.1.0
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
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
        """Convierte el mensaje a formato dict para API de Groq."""
        return {
            "role": self.role.value,
            "content": self.content
        }
    
    def to_storage_dict(self) -> dict:
        """Convierte el mensaje a formato dict para almacenamiento."""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __len__(self) -> int:
        """Retorna la longitud del contenido en caracteres."""
        return len(self.content)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Crea un Message desde un diccionario."""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                timestamp = now_utc()
        elif timestamp is None:
            timestamp = now_utc()
            
        return cls(
            role=MessageRole(data.get("role", "user")),
            content=data.get("content", ""),
            timestamp=timestamp
        )


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
    
    def add_user_message(self, content: str) -> Message:
        """Agrega un mensaje del usuario."""
        message = Message(role=MessageRole.USER, content=content)
        self.add_message(message)
        return message
    
    def add_assistant_message(self, content: str) -> Message:
        """Agrega un mensaje del asistente."""
        message = Message(role=MessageRole.ASSISTANT, content=content)
        self.add_message(message)
        return message
    
    def add_system_message(self, content: str) -> Message:
        """Agrega un mensaje del sistema."""
        message = Message(role=MessageRole.SYSTEM, content=content)
        self.add_message(message)
        return message
    
    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Retorna los mensajes más recientes hasta el límite especificado."""
        if not self.messages:
            return []
        return self.messages[-limit:]
    
    def get_messages_for_api(self, limit: int = 10) -> List[dict]:
        """
        Retorna mensajes en formato para API de Groq.
        Excluye mensajes del sistema duplicados, mantiene solo el primero.
        """
        recent = self.get_recent_messages(limit)
        
        result = []
        has_system = False
        
        for msg in recent:
            if msg.role == MessageRole.SYSTEM:
                if not has_system:
                    result.append(msg.to_dict())
                    has_system = True
                # Omitir mensajes de sistema duplicados
            else:
                result.append(msg.to_dict())
        
        return result
    
    def get_context_messages(self, limit: int = 10) -> List[dict]:
        """Alias para get_messages_for_api (compatibilidad)."""
        return self.get_messages_for_api(limit)
    
    def is_stale(self, hours: int = 24) -> bool:
        """Verifica si la conversación debe cerrarse por inactividad."""
        delta = now_utc() - self.last_activity
        return delta.total_seconds() > (hours * 3600)
    
    def is_active(self) -> bool:
        """Verifica si la conversación está activa."""
        return self.status == "active"
    
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
    
    def get_user_message_count(self) -> int:
        """Retorna el número de mensajes del usuario."""
        return sum(1 for msg in self.messages if msg.role == MessageRole.USER)
    
    def get_total_tokens_estimate(self) -> int:
        """Estima el total de tokens en la conversación (aprox 4 chars = 1 token)."""
        total_chars = sum(len(msg.content) for msg in self.messages)
        return int(total_chars / 4)
    
    def get_duration_minutes(self) -> int:
        """Retorna la duración de la conversación en minutos."""
        delta = self.last_activity - self.started_at
        return int(delta.total_seconds() / 60)
```

---

## 4️⃣ `conversation_repository.py` - Repositorio

### ❌ Problemas:
- No maneja correctamente las sesiones async
- El método `save` puede tener problemas de concurrencia

### ✅ Corrección:
```python
"""
Repositorio de conversaciones con el asistente IA Sip.

Author: uSipipo Team
Version: 1.1.0
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import delete, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from utils.datetime_utils import now_utc
from utils.logger import logger
from domain.entities.conversation import Conversation, Message, MessageRole


# Importar el modelo - asegúrate de que exista
try:
    from .models import ConversationModel
except ImportError:
    from infrastructure.persistence.supabase.models import ConversationModel


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
                messages_data = json.loads(model.messages) if isinstance(model.messages, str) else model.messages
                
                for msg_data in messages_data:
                    messages.append(Message.from_dict(msg_data))
                    
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                logger.warning(f"Error decodificando mensajes para conversación {model.id}: {e}")

        return Conversation(
            id=uuid.UUID(model.id) if isinstance(model.id, str) else model.id,
            user_id=model.user_id,
            user_name=model.user_name or "Usuario",
            status=model.status or "active",
            started_at=model.started_at or now_utc(),
            last_activity=model.last_activity or now_utc(),
            messages=messages,
        )

    def _serialize_messages(self, messages: List[Message]) -> str:
        """Serializa lista de mensajes a JSON string."""
        return json.dumps([msg.to_storage_dict() for msg in messages], ensure_ascii=False)

    def _entity_to_model(self, entity: Conversation) -> ConversationModel:
        """Convierte una entidad de dominio a modelo SQLAlchemy."""
        return ConversationModel(
            id=str(entity.id),
            user_id=entity.user_id,
            user_name=entity.user_name,
            status=entity.status,
            started_at=entity.started_at,
            last_activity=entity.last_activity,
            messages=self._serialize_messages(entity.messages),
        )

    async def get_active_by_user(self, user_id: int) -> Optional[Conversation]:
        """
        Obtiene la conversación activa de un usuario.
        
        Args:
            user_id: ID del usuario de Telegram
            
        Returns:
            Conversation si existe, None si no
        """
        try:
            query = (
                select(ConversationModel)
                .where(
                    ConversationModel.user_id == user_id,
                    ConversationModel.status == "active"
                )
                .order_by(desc(ConversationModel.last_activity))
                .limit(1)
            )

            result = await self.session.execute(query)
            model = result.scalar_one_or_none()

            if model is None:
                logger.debug(f"No hay conversación activa para usuario {user_id}")
                return None

            conversation = self._model_to_entity(model)
            logger.debug(f"Conversación activa encontrada para usuario {user_id}: {conversation.id}")
            return conversation

        except SQLAlchemyError as e:
            logger.error(f"Error de BD al obtener conversación activa del usuario {user_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al obtener conversación: {e}")
            return None

    async def save(self, conversation: Conversation) -> Conversation:
        """
        Guarda o actualiza una conversación.
        
        Args:
            conversation: Entidad de conversación a guardar
            
        Returns:
            Conversation guardada
            
        Raises:
            Exception: Si hay error de BD
        """
        try:
            conversation_id = str(conversation.id)
            
            # Buscar si existe
            existing = await self.session.get(ConversationModel, conversation_id)

            if existing:
                # Actualizar existente
                existing.status = conversation.status
                existing.last_activity = conversation.last_activity
                existing.messages = self._serialize_messages(conversation.messages)
                existing.user_name = conversation.user_name
                
                logger.debug(f"Actualizando conversación {conversation_id}")
            else:
                # Crear nueva
                model = self._entity_to_model(conversation)
                self.session.add(model)
                logger.debug(f"Creando nueva conversación {conversation_id}")

            await self.session.commit()
            logger.debug(f"Conversación {conversation_id} guardada correctamente")
            return conversation

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error de BD al guardar conversación: {e}")
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error inesperado al guardar conversación: {e}")
            raise

    async def get_all_active(self) -> List[Conversation]:
        """Obtiene todas las conversaciones activas."""
        try:
            query = (
                select(ConversationModel)
                .where(ConversationModel.status == "active")
                .order_by(desc(ConversationModel.last_activity))
            )
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

        except SQLAlchemyError as e:
            logger.error(f"Error de BD al obtener conversaciones activas: {e}")
            return []

    async def close_conversation(self, conversation_id: uuid.UUID) -> bool:
        """Cierra una conversación por ID."""
        try:
            query = (
                update(ConversationModel)
                .where(ConversationModel.id == str(conversation_id))
                .values(status="ended", last_activity=now_utc())
            )
            result = await self.session.execute(query)
            await self.session.commit()

            success = result.rowcount > 0
            if success:
                logger.debug(f"Conversación {conversation_id} cerrada")
            else:
                logger.warning(f"No se encontró conversación {conversation_id} para cerrar")
            
            return success

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error de BD al cerrar conversación {conversation_id}: {e}")
            return False

    async def close_user_conversations(self, user_id: int) -> int:
        """Cierra todas las conversaciones activas de un usuario."""
        try:
            query = (
                update(ConversationModel)
                .where(
                    ConversationModel.user_id == user_id,
                    ConversationModel.status == "active"
                )
                .values(status="ended", last_activity=now_utc())
            )
            result = await self.session.execute(query)
            await self.session.commit()

            logger.debug(f"Cerradas {result.rowcount} conversaciones del usuario {user_id}")
            return result.rowcount

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error de BD al cerrar conversaciones del usuario {user_id}: {e}")
            return 0

    async def delete_stale_conversations(self, hours: int = 24) -> int:
        """Elimina conversaciones inactivas."""
        try:
            cutoff_time = now_utc() - timedelta(hours=hours)

            query = delete(ConversationModel).where(
                ConversationModel.last_activity < cutoff_time
            )
            result = await self.session.execute(query)
            await self.session.commit()

            deleted_count = result.rowcount
            logger.info(f"Eliminadas {deleted_count} conversaciones inactivas (>{hours}h)")
            return deleted_count

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error de BD al eliminar conversaciones inactivas: {e}")
            return 0

    async def get_by_id(self, conversation_id: uuid.UUID) -> Optional[Conversation]:
        """Obtiene una conversación por su ID."""
        try:
            model = await self.session.get(ConversationModel, str(conversation_id))

            if model is None:
                return None

            return self._model_to_entity(model)

        except SQLAlchemyError as e:
            logger.error(f"Error de BD al obtener conversación {conversation_id}: {e}")
            return None
```

---

## 5️⃣ `ai_support_service.py` - Servicio de Aplicación (REESCRITURA)

```python
"""
Servicio de aplicación para soporte con IA Sip.

Author: uSipipo Team
Version: 2.0.0
"""

import uuid
from typing import Optional, List

from domain.entities.conversation import Conversation, Message, MessageRole
from domain.interfaces.iai_support_service import IAiSupportService
from infrastructure.persistence.supabase.conversation_repository import ConversationRepository
from infrastructure.api_clients.groq_client import GroqClient
from utils.sip_prompts import get_system_prompt
from utils.logger import logger


class AiSupportService(IAiSupportService):
    """Servicio de aplicación para soporte con IA Sip."""
    
    # Configuración
    MAX_CONTEXT_MESSAGES = 10  # Mensajes a enviar como contexto
    MAX_MESSAGE_LENGTH = 4000  # Longitud máxima de mensaje de usuario
    
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
        logger.info("🌊 AiSupportService inicializado")
    
    async def start_conversation(self, user_id: int, user_name: str) -> Conversation:
        """
        Inicia una nueva conversación con Sip.
        
        Si ya existe una conversación activa, la cierra primero.
        """
        try:
            # Cerrar conversaciones previas del usuario
            await self.conversation_repo.close_user_conversations(user_id)
            
            # Crear nueva conversación
            conversation = Conversation(
                id=uuid.uuid4(),
                user_id=user_id,
                user_name=user_name or "Usuario"
            )
            
            # Agregar mensaje del sistema
            system_prompt = get_system_prompt()
            conversation.add_system_message(system_prompt)
            
            # Guardar en BD
            await self.conversation_repo.save(conversation)
            
            logger.info(f"🌊 Conversación {conversation.id} iniciada para usuario {user_id} ({user_name})")
            return conversation
            
        except Exception as e:
            logger.error(f"❌ Error iniciando conversación para usuario {user_id}: {e}")
            raise
    
    async def send_message(self, user_id: int, user_message: str) -> str:
        """
        Envía mensaje de usuario y obtiene respuesta de Sip.
        
        Args:
            user_id: ID del usuario de Telegram
            user_message: Mensaje del usuario
            
        Returns:
            str: Respuesta generada por Sip
            
        Raises:
            ValueError: Si no hay conversación activa o hay error de validación
        """
        # 1. Validar mensaje
        if not user_message or not user_message.strip():
            return "No recibí ningún mensaje. ¿En qué puedo ayudarte?"
        
        # Truncar mensaje si es muy largo
        if len(user_message) > self.MAX_MESSAGE_LENGTH:
            user_message = user_message[:self.MAX_MESSAGE_LENGTH] + "..."
            logger.warning(f"Mensaje truncado para usuario {user_id}")
        
        try:
            # 2. Obtener conversación activa
            conversation = await self.conversation_repo.get_active_by_user(user_id)
            
            if not conversation:
                logger.warning(f"⚠️ No hay conversación activa para usuario {user_id}")
                raise ValueError("No hay conversación activa. Por favor, inicia una nueva conversación.")
            
            # 3. Agregar mensaje del usuario
            conversation.add_user_message(user_message)
            
            # 4. Construir contexto para API
            messages = self._build_context(conversation)
            
            logger.debug(f"📤 Enviando {len(messages)} mensajes a Groq para usuario {user_id}")
            
            # 5. Obtener respuesta de IA
            try:
                ai_response = await self.groq_client.chat_completion(messages)
            except ValueError as e:
                # Error manejado del cliente Groq
                logger.warning(f"⚠️ Error de Groq para usuario {user_id}: {e}")
                ai_response = str(e)
            
            # 6. Agregar respuesta a la conversación
            conversation.add_assistant_message(ai_response)
            
            # 7. Guardar conversación actualizada
            await self.conversation_repo.save(conversation)
            
            # 8. Verificar si se debe escalar
            if self._should_escalate(user_message, ai_response):
                logger.info(f"🔔 Posible escalado detectado para usuario {user_id}")
                # Aquí podrías notificar al admin o crear un ticket
            
            logger.debug(f"✅ Respuesta enviada a usuario {user_id}: {len(ai_response)} chars")
            return ai_response
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje de usuario {user_id}: {e}")
            raise ValueError(f"Error procesando tu mensaje. Por favor, intenta de nuevo.")
    
    async def get_active_conversation(self, user_id: int) -> Optional[Conversation]:
        """Obtiene la conversación activa del usuario."""
        try:
            return await self.conversation_repo.get_active_by_user(user_id)
        except Exception as e:
            logger.error(f"❌ Error obteniendo conversación activa para {user_id}: {e}")
            return None
    
    async def end_conversation(self, user_id: int) -> bool:
        """Finaliza la conversación activa del usuario."""
        try:
            conversation = await self.conversation_repo.get_active_by_user(user_id)
            
            if not conversation:
                logger.debug(f"No hay conversación activa para finalizar (usuario {user_id})")
                return True  # No hay nada que cerrar, considerarlo éxito
            
            conversation.end_conversation()
            await self.conversation_repo.save(conversation)
            
            logger.info(f"🌊 Conversación finalizada para usuario {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error finalizando conversación para {user_id}: {e}")
            return False
    
    async def escalate_conversation(self, user_id: int, reason: str) -> bool:
        """Escala la conversación a soporte humano."""
        try:
            conversation = await self.conversation_repo.get_active_by_user(user_id)
            
            if not conversation:
                logger.warning(f"⚠️ No hay conversación para escalar (usuario {user_id})")
                return False
            
            conversation.escalate_conversation()
            
            # Agregar nota de escalado
            conversation.add_system_message(f"[ESCALADO] Razón: {reason}")
            
            await self.conversation_repo.save(conversation)
            
            logger.info(f"🔔 Conversación escalada para usuario {user_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error escalando conversación para {user_id}: {e}")
            return False
    
    async def get_conversation_history(self, user_id: int, limit: int = 10) -> List[Message]:
        """Obtiene el historial de conversación del usuario."""
        try:
            conversation = await self.conversation_repo.get_active_by_user(user_id)
            
            if not conversation:
                return []
            
            return conversation.get_recent_messages(limit)
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo historial para {user_id}: {e}")
            return []
    
    async def cleanup_stale_conversations(self, hours: int = 24) -> int:
        """Limpia conversaciones inactivas."""
        try:
            deleted_count = await self.conversation_repo.delete_stale_conversations(hours)
            logger.info(f"🧹 Limpieza: {deleted_count} conversaciones eliminadas")
            return deleted_count
        except Exception as e:
            logger.error(f"❌ Error en limpieza de conversaciones: {e}")
            return 0
    
    def _build_context(self, conversation: Conversation) -> List[dict]:
        """
        Construye el contexto de mensajes para la API de Groq.
        
        Siempre incluye el system prompt primero, luego los mensajes recientes.
        """
        messages = []
        
        # 1. Siempre agregar system prompt primero
        system_prompt = get_system_prompt()
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # 2. Agregar mensajes recientes (excluyendo system messages duplicados)
        recent_messages = conversation.get_recent_messages(self.MAX_CONTEXT_MESSAGES)
        
        for msg in recent_messages:
            if msg.role != MessageRole.SYSTEM:  # No duplicar system messages
                messages.append(msg.to_dict())
        
        return messages
    
    def _should_escalate(self, user_message: str, ai_response: str) -> bool:
        """Determina si se debe escalar a soporte humano."""
        user_lower = user_message.lower()
        
        # Palabras clave de escalado
        escalation_keywords = [
            "hablar con humano",
            "soporte humano", 
            "agente real",
            "persona real",
            "ayuda urgente",
            "emergencia",
            "no funciona nada",
            "quiero quejarme",
            "denuncia",
            "reembolso",
        ]
        
        for keyword in escalation_keywords:
            if keyword in user_lower:
                return True
        
        # Si la IA menciona crear ticket
        if "ticket de soporte" in ai_response.lower():
            return True
        
        return False
```

---

## 6️⃣ `ai_support_handler.py` - Handler Principal (REESCRITURA COMPLETA)

```python
"""
Handler para conversaciones con el asistente IA Sip.

Author: uSipipo Team
Version: 2.0.0
"""

from telegram import Update
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler, 
    CommandHandler
)

from telegram_bot.messages import SipMessages
from telegram_bot.keyboard import SupportKeyboards, CommonKeyboards
from utils.logger import logger

# Estado de la conversación
CHATTING = 1

# Clave para marcar que el usuario está en chat IA
AI_CHAT_KEY = 'in_ai_conversation'


class AiSupportHandler:
    """Handler para conversaciones con IA de soporte."""
    
    def __init__(self, ai_support_service):
        """
        Inicializa el handler de IA Sip.
        
        Args:
            ai_support_service: Servicio de soporte con IA
        """
        self.ai_support_service = ai_support_service
        logger.info("🌊 AiSupportHandler inicializado")
    
    def _set_ai_chat_active(self, context: ContextTypes.DEFAULT_TYPE, active: bool = True):
        """Marca si el usuario está en conversación IA."""
        context.user_data[AI_CHAT_KEY] = active
    
    def _is_ai_chat_active(self, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Verifica si el usuario está en conversación IA."""
        return context.user_data.get(AI_CHAT_KEY, False)
    
    async def start_ai_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Inicia conversación con IA Sip desde mensaje de texto.
        """
        user = update.effective_user
        logger.info(f"🌊 Iniciando conversación IA para usuario {user.id} ({user.first_name})")

        try:
            await self.ai_support_service.start_conversation(
                user_id=user.id,
                user_name=user.first_name
            )
            
            # Marcar que estamos en conversación IA
            self._set_ai_chat_active(context, True)

            await update.message.reply_text(
                text=SipMessages.WELCOME,
                reply_markup=SupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )

            logger.info(f"✅ Conversación IA iniciada para usuario {user.id}")
            return CHATTING

        except Exception as e:
            logger.error(f"❌ Error iniciando soporte IA para {user.id}: {e}")
            await update.message.reply_text(
                "❌ No pude iniciar el asistente IA. Por favor, intenta más tarde.",
                reply_markup=CommonKeyboards.back_button()
            )
            return ConversationHandler.END

    async def start_ai_support_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Inicia conversación con IA Sip desde callback (botón inline).
        """
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        logger.info(f"🌊 Iniciando conversación IA (callback) para usuario {user.id}")

        try:
            await self.ai_support_service.start_conversation(
                user_id=user.id,
                user_name=user.first_name
            )
            
            # Marcar que estamos en conversación IA
            self._set_ai_chat_active(context, True)

            await query.edit_message_text(
                text=SipMessages.WELCOME,
                reply_markup=SupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )

            logger.info(f"✅ Conversación IA iniciada (callback) para usuario {user.id}")
            return CHATTING

        except Exception as e:
            logger.error(f"❌ Error iniciando soporte IA (callback) para {user.id}: {e}")
            await query.edit_message_text(
                "❌ No pude iniciar el asistente IA. Por favor, intenta más tarde.",
                reply_markup=CommonKeyboards.back_button()
            )
            return ConversationHandler.END
    
    async def handle_ai_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Procesa mensaje del usuario y responde con IA.
        """
        user_message = update.message.text
        user_id = update.effective_user.id
        
        # Log para debugging
        logger.info(f"🔍 handle_ai_message: usuario {user_id}, mensaje: '{user_message[:50]}...'")
        
        # Comandos de salida
        if user_message.lower().strip() in ["finalizar", "salir", "exit", "fin", "terminar"]:
            return await self.end_ai_support(update, context)
        
        try:
            # Mostrar indicador de escritura
            await update.message.chat.send_action(action="typing")
            
            # Obtener respuesta de IA
            ai_response = await self.ai_support_service.send_message(
                user_id=user_id,
                user_message=user_message
            )
            
            # Enviar respuesta
            await update.message.reply_text(
                f"🌊 **Sip:**\n\n{ai_response}",
                reply_markup=SupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )
            
            logger.debug(f"✅ Respuesta IA enviada a usuario {user_id}")
            return CHATTING
            
        except ValueError as e:
            # Error de validación (conversación no existe, etc.)
            logger.warning(f"⚠️ Error de validación para {user_id}: {e}")
            self._set_ai_chat_active(context, False)
            
            await update.message.reply_text(
                f"⚠️ {str(e)}\n\nUsa el botón para iniciar una nueva conversación.",
                reply_markup=CommonKeyboards.back_button(),
                parse_mode="Markdown"
            )
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje de {user_id}: {e}")
            await update.message.reply_text(
                "❌ Tuve un problema procesando tu mensaje. Por favor, intenta de nuevo.",
                reply_markup=SupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )
            return CHATTING
    
    async def end_ai_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Finaliza conversación con IA.
        """
        user_id = update.effective_user.id
        
        # Limpiar flag de conversación
        self._set_ai_chat_active(context, False)
        
        try:
            await self.ai_support_service.end_conversation(user_id)
            
            message_text = SipMessages.CONVERSATION_ENDED
            keyboard = CommonKeyboards.back_button()
            
            if update.message:
                await update.message.reply_text(
                    text=message_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            elif update.callback_query:
                await update.callback_query.edit_message_text(
                    text=message_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            
            logger.info(f"🌊 Conversación IA finalizada para usuario {user_id}")
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"❌ Error finalizando conversación para {user_id}: {e}")
            
            error_msg = "❌ Hubo un error al finalizar. La conversación se cerrará de todos modos."
            keyboard = CommonKeyboards.back_button()
            
            if update.message:
                await update.message.reply_text(error_msg, reply_markup=keyboard)
            elif update.callback_query:
                await update.callback_query.edit_message_text(error_msg, reply_markup=keyboard)
            
            return ConversationHandler.END
    
    async def show_suggested_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Muestra preguntas sugeridas al usuario.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            await query.edit_message_text(
                text=SipMessages.SUGGESTED_QUESTIONS,
                reply_markup=SupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )
            return CHATTING
        except Exception as e:
            logger.error(f"❌ Error mostrando sugerencias: {e}")
            return CHATTING
    
    async def handle_end_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Maneja el callback del botón finalizar.
        """
        query = update.callback_query
        await query.answer("Finalizando conversación...")
        return await self.end_ai_support(update, context)
    
    async def cancel_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Maneja el comando /cancelar durante la conversación.
        """
        return await self.end_ai_support(update, context)


def get_ai_support_handler(ai_support_service):
    """
    Retorna el ConversationHandler configurado para IA Sip.
    
    Args:
        ai_support_service: Servicio de soporte con IA
        
    Returns:
        ConversationHandler: Handler configurado
    """
    handler = AiSupportHandler(ai_support_service)
    
    # Patrones de entrada para iniciar conversación
    entry_patterns = [
        MessageHandler(filters.Regex(r"^🌊\s*Sip$"), handler.start_ai_support),
        MessageHandler(filters.Regex(r"^🤖\s*Asistente\s*IA$"), handler.start_ai_support),
        CommandHandler("sipai", handler.start_ai_support),
        CallbackQueryHandler(handler.start_ai_support_callback, pattern=r"^ai_sip_start$"),
    ]
    
    # Estados de la conversación
    states = {
        CHATTING: [
            # Callbacks primero (mayor prioridad)
            CallbackQueryHandler(handler.handle_end_callback, pattern=r"^ai_sip_end$"),
            CallbackQueryHandler(handler.show_suggested_questions, pattern=r"^ai_sip_suggestions$"),
            
            # Mensajes de texto (excluyendo comandos)
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handler.handle_ai_message
            ),
        ]
    }
    
    # Fallbacks (siempre disponibles)
    fallbacks = [
        # Palabras de salida
        MessageHandler(
            filters.Regex(r"^(Finalizar|Salir|Exit|Fin|Terminar)$"),
            handler.end_ai_support
        ),
        # Callbacks de salida
        CallbackQueryHandler(handler.handle_end_callback, pattern=r"^ai_sip_end$"),
        # Comando cancelar
        CommandHandler("cancelar", handler.cancel_handler),
        CommandHandler("cancel", handler.cancel_handler),
    ]
    
    return ConversationHandler(
        entry_points=entry_patterns,
        states=states,
        fallbacks=fallbacks,
        name="ai_support_conversation",
        persistent=False,
        per_chat=True,
        per_user=True,
        per_message=False,
        allow_reentry=True,  # Permitir reiniciar la conversación
    )
```

---

## 7️⃣ `direct_message_handler.py` - Handler de Mensajes Directos

```python
"""
Handler para responder mensajes directos con IA Sip.

Este handler solo actúa cuando NO hay una conversación activa
en el ConversationHandler.

Author: uSipipo Team
Version: 1.1.0
"""

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from telegram_bot.messages import SipMessages
from telegram_bot.keyboard import CommonKeyboards, SupportKeyboards
from utils.logger import logger


# Patrones de botones del menú que NO deben ser procesados por IA
MENU_BUTTON_PATTERNS = [
    r"^🛡️\s*Mis\s*Llaves$",
    r"^📊\s*Estado$",
    r"^💰\s*Operaciones$",
    r"^💰\s*Mi\s*Balance$",
    r"^👑\s*Plan\s*VIP$",
    r"^🎮\s*Juega\s*y\s*Gana$",
    r"^👥\s*Referidos$",
    r"^🔙\s*Atrás$",
    r"^🏆\s*Logros$",
    r"^⚙️\s*Ayuda$",
    r"^📋\s*Mostrar\s*Menú$",
    r"^🎫\s*Soporte$",
    r"^🌊\s*Sip$",
    r"^🤖\s*Asistente\s*IA$",
    r"^➕\s*Crear\s*Nueva$",
    r"^Finalizar$",
    r"^Salir$",
    r"^Exit$",
    r"^Fin$",
    r"^Terminar$",
]

# Clave para verificar si hay conversación IA activa
AI_CHAT_KEY = 'in_ai_conversation'


class DirectMessageHandler:
    """Handler para responder mensajes directos del usuario con IA."""
    
    def __init__(self, ai_support_service):
        """
        Inicializa el handler de mensajes directos.
        
        Args:
            ai_support_service: Servicio de soporte con IA
        """
        self.ai_support_service = ai_support_service
        self._menu_patterns_compiled = None
        logger.info("📨 DirectMessageHandler inicializado")
    
    def _compile_patterns(self):
        """Compila los patrones de menú una sola vez."""
        if self._menu_patterns_compiled is None:
            import re
            self._menu_patterns_compiled = [
                re.compile(pattern, re.IGNORECASE) 
                for pattern in MENU_BUTTON_PATTERNS
            ]
        return self._menu_patterns_compiled
    
    def _is_menu_button(self, text: str) -> bool:
        """Verifica si el texto es un botón del menú."""
        patterns = self._compile_patterns()
        return any(pattern.match(text) for pattern in patterns)
    
    async def handle_direct_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Procesa mensaje directo del usuario.
        
        Solo responde si:
        1. No es un botón del menú
        2. No hay conversación IA activa en el ConversationHandler
        """
        user_message = update.message.text
        user_id = update.effective_user.id
        
        # 1. Ignorar botones del menú
        if self._is_menu_button(user_message):
            logger.debug(f"📨 Ignorando botón de menú: '{user_message}'")
            return
        
        # 2. Verificar si hay conversación IA activa (gestionada por ConversationHandler)
        if context.user_data.get(AI_CHAT_KEY, False):
            logger.debug(f"📨 Usuario {user_id} tiene conversación IA activa, delegando al ConversationHandler")
            return
        
        logger.info(f"📨 Mensaje directo de usuario {user_id}: '{user_message[:30]}...'")
        
        try:
            # Mostrar indicador de escritura
            await update.message.chat.send_action(action="typing")
            
            # Verificar si hay conversación en BD
            conversation = await self.ai_support_service.get_active_conversation(user_id)
            
            if not conversation:
                # Iniciar conversación automática
                logger.info(f"📨 Iniciando conversación automática para usuario {user_id}")
                await self.ai_support_service.start_conversation(
                    user_id=user_id,
                    user_name=update.effective_user.first_name
                )
            
            # Obtener respuesta de IA
            ai_response = await self.ai_support_service.send_message(
                user_id=user_id,
                user_message=user_message
            )
            
            # Enviar respuesta con instrucciones
            await update.message.reply_text(
                f"🌊 **Sip:**\n\n{ai_response}\n\n"
                f"_💡 Escribe 'Finalizar' para terminar o usa /sipai para modo completo_",
                reply_markup=SupportKeyboards.ai_support_active(),
                parse_mode="Markdown"
            )
            
            logger.debug(f"📨 Respuesta automática enviada a usuario {user_id}")
            
        except ValueError as e:
            logger.warning(f"⚠️ Error en mensaje directo de {user_id}: {e}")
            await update.message.reply_text(
                f"⚠️ {str(e)}",
                reply_markup=CommonKeyboards.back_button(),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"❌ Error en mensaje directo de {user_id}: {e}")
            await update.message.reply_text(
                "❌ Tuve un problema procesando tu mensaje. Usa /sipai para iniciar el asistente.",
                parse_mode="Markdown"
            )


def get_direct_message_handler(ai_support_service):
    """
    Retorna el handler para mensajes directos.
    
    IMPORTANTE: Este handler debe registrarse DESPUÉS del ai_support_handler
    para que el ConversationHandler tenga prioridad.
    """
    handler = DirectMessageHandler(ai_support_service)
    
    return MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handler.handle_direct_message
    )
```

---

## 8️⃣ `handler_initializer.py` - Verificar Orden de Registro

El orden de registro es **crítico**. Asegúrate de que esté así:

```python
# ... (otros handlers) ...

    # ========================================
    # SISTEMA DE SOPORTE CON IA SIP
    # ========================================
    
    # 1. PRIMERO: ConversationHandler de IA (tiene prioridad)
    ai_support_handler = container.resolve("ai_support_handler")
    handlers.append(ai_support_handler)
    logger.log_bot_event("INFO", "✅ Handler de IA Sip (ConversationHandler) registrado")

    # 2. ÚLTIMO: Handler de mensajes directos (fallback)
    # DEBE ir AL FINAL de todos los handlers
    direct_message_handler = container.resolve("direct_message_handler")
    handlers.append(direct_message_handler)
    logger.log_bot_event("INFO", "✅ Handler de mensajes directos registrado (fallback)")

    return handlers
```

---

## 📋 Resumen de Cambios

| Archivo | Cambios Principales |
|---------|-------------------|
| `config.py` | Agregar `GROQ_REASONING_EFFORT`, ajustar defaults |
| `groq_client.py` | Reescritura completa: `max_completion_tokens`, timeout en cliente, `reasoning_effort` |
| `conversation.py` | Agregar `from_dict()`, `to_storage_dict()`, métodos auxiliares |
| `conversation_repository.py` | Mejor manejo de errores, `close_user_conversations()` |
| `ai_support_service.py` | Reescritura: mejor manejo de errores, cierre de conversaciones previas |
| `ai_support_handler.py` | Reescritura completa: flag de conversación, mejor logging |
| `direct_message_handler.py` | Verificar flag antes de actuar, patrones compilados |
| `handler_initializer.py` | Verificar orden de registro |