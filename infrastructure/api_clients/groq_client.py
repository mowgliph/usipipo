"""
Cliente de infraestructura para la API de Groq - Asistente IA Sip.

Basado en la documentación oficial de Groq:
- https://console.groq.com/docs/quickstart
- https://console.groq.com/docs/text-chat
- https://console.groq.com/docs/model/openai/gpt-oss-120b

Author: uSipipo Team
Version: 2.0.0
"""
from typing import List, Dict, Optional
from groq import Groq, AsyncGroq
from groq import RateLimitError, APIConnectionError, APIStatusError
from config import settings
from utils.logger import logger

class GroqClient:
    """Cliente de infraestructura para API de Groq."""
    
    # Actualizamos el diccionario con los datos REALES que me diste
    MODELS = {
        "openai/gpt-oss-120b": {
            "description": "GPT OSS 120B - High capability agentic model",
            "context_window": 131072,
        }
    }
    
    def __init__(self):
        """Inicializa el cliente de Groq con configuración."""
        
        # 1. Verificación explícita de la API Key
        if not settings.GROQ_API_KEY:
            logger.critical("❌ ERROR CRÍTICO: GROQ_API_KEY está vacía en config.py o .env")
            # Esto ayudará a ver si el problema es la llave
        
        try:
            # Cliente síncrono
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            # Cliente asíncrono
            self.async_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        except Exception as e:
            logger.error(f"❌ Error al crear cliente Groq: {e}")
        
        # 2. IMPORTANTE: Usar el modelo de settings, no el hardcodeado
        # Si settings.GROQ_MODEL tiene valor, lo usa. Si no, usa el string directo.
        self.model = settings.GROQ_MODEL if settings.GROQ_MODEL else "openai/gpt-oss-120b"
        
        self.temperature = settings.GROQ_TEMPERATURE
        self.max_tokens = settings.GROQ_MAX_TOKENS
        self.timeout = settings.GROQ_TIMEOUT
        
        logger.info(f"🌊 GroqClient inicializado. Modelo objetivo: {self.model}")

    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """
        Genera una respuesta de chat asíncrona usando el modelo configurado.
        """
        try:
            # Log para depuración: Ver qué estamos enviando
            logger.debug(f"📤 Enviando request a Groq: {self.model}")
            
            completion = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
            
            # Extraer respuesta
            response_content = completion.choices[0].message.content
            
            # Log de uso de tokens (útil para ver si conecta)
            if hasattr(completion, 'usage'):
                logger.info(f"💰 Tokens usados: {completion.usage.total_tokens}")
                
            return response_content

        except APIConnectionError:
            logger.error("❌ Error de conexión con Groq. Revisa tu internet o DNS.")
            return "Lo siento, tengo problemas de conexión en este momento."
            
        except RateLimitError:
            logger.error("⚠️ Límite de velocidad alcanzado (Rate Limit).")
            return "Estoy un poco saturado, por favor intenta en unos segundos."
            
        except APIStatusError as e:
            logger.error(f"❌ Error de estado API ({e.status_code}): {e.message}")
            if e.status_code == 404:
                 logger.error(f"🔍 El modelo '{self.model}' no fue encontrado. Verifica el nombre exacto.")
            return "Ocurrió un error en el servidor de IA."
            
        except Exception as e:
            logger.error(f"❌ Error inesperado en Groq: {str(e)}")
            return "Ocurrió un error inesperado al procesar tu mensaje."
        
# from typing import List, Dict
# from groq import Groq, AsyncGroq
# from groq import RateLimitError, APIConnectionError, APIStatusError
# from config import settings
# from utils.logger import logger


# class GroqClient:
#     """Cliente de infraestructura para API de Groq."""
    
#     # Modelo por defecto utilizado
#     DEFAULT_MODEL = "openai/gpt-oss-120b"
    
#     MODELS = {
#         DEFAULT_MODEL: {
#             "description": "Modelo GPT-OSS 120B de OpenAI (disponible en Groq)",
#             "context_window": 131072,
#         },
#     }
    
#     def __init__(self):
#         """Inicializa el cliente de Groq con configuración."""
#         if not settings.GROQ_API_KEY:
#             logger.warning("⚠️ GROQ_API_KEY no configurada. Sip no funcionará correctamente.")
        
#         # Cliente síncrono (para operaciones que no requieren async)
#         self.client = Groq(api_key=settings.GROQ_API_KEY)
#         # Cliente asíncrono (para operaciones async)
#         self.async_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        
#         # Configuración del modelo (hardcodeado para usar solo GPT-OSS 120B)
#         self.model = self.DEFAULT_MODEL
#         self.temperature = settings.GROQ_TEMPERATURE
#         self.max_tokens = settings.GROQ_MAX_TOKENS
#         self.timeout = settings.GROQ_TIMEOUT
        
#         logger.info(f"🌊 GroqClient inicializado con modelo: {self.model}")
    
#     async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
#         """
#         Realiza petición de chat completion a Groq de forma asíncrona.
        
#         Args:
#             messages: Lista de mensajes en formato dict [{"role": "user", "content": "..."}]
#                       Roles soportados: "system", "user", "assistant"
            
#         Returns:
#             str: Respuesta generada por el modelo
            
#         Raises:
#             ValueError: Si la API key no está configurada
#             RateLimitError: Si se excede el límite de llamadas
#             APIConnectionError: Si hay error de conexión
#             APIStatusError: Si hay error en la respuesta de la API
#             Exception: Para otros errores
#         """
#         if not self.validate_api_key():
#             raise ValueError("API key de Groq no configurada o inválida")
        
#         try:
#             logger.debug(f"🌊 Enviando {len(messages)} mensajes a Groq API")
#             logger.debug(f"🌊 Modelo: {self.model}, Timeout: {self.timeout}s")
            
#             # Usar cliente asíncrono para mantener el event loop libre
#             response = await self.async_client.chat.completions.create(
#                 messages=messages,
#                 model=self.model,
#                 temperature=self.temperature,
#                 max_tokens=self.max_tokens,
#                 timeout=float(self.timeout) if self.timeout else None
#             )
            
#             logger.debug(f"🌊 Respuesta recibida de Groq: {response}")
            
#             if response.choices and len(response.choices) > 0:
#                 content = response.choices[0].message.content
#                 if content:
#                     logger.debug(f"🌊 Contenido de respuesta: {len(content)} caracteres")
#                     return content
#                 else:
#                     logger.error("🌊 Groq API devolvió contenido vacío en la respuesta")
#                     raise ValueError("La API de Groq devolvió una respuesta vacía")
#             else:
#                 logger.error(f"🌊 Groq API no devolvió choices. Response: {response}")
#                 raise ValueError("La API de Groq no devolvió ninguna opción de respuesta")
                
#         except RateLimitError as e:
#             logger.error(f"🌊 Rate limit excedido en Groq API: {str(e)}")
#             raise ValueError("Has excedido el límite de llamadas a la IA. Por favor, espera un momento.") from e
        
#         except APIConnectionError as e:
#             logger.error(f"🌊 Error de conexión con Groq API: {str(e)}")
#             raise ValueError("No se pudo conectar con el servicio de IA. Verifica tu conexión a internet.") from e
        
#         except APIStatusError as e:
#             logger.error(f"🌊 Error de estado en Groq API: {str(e)}")
#             raise ValueError(f"Error del servicio de IA: código {e.status_code}") from e
        
#         except (ValueError, TypeError, KeyError, AttributeError, TimeoutError) as e:
#             error_type = type(e).__name__
#             error_msg = str(e)
#             logger.error(f"🌊 Error en Groq API [{error_type}]: {error_msg}")
            
#             if "timeout" in error_msg.lower():
#                 raise ValueError("Sip está tardando mucho en responder. Por favor, intenta con un mensaje más corto.") from e
#             elif "authentication" in error_msg.lower() or "api key" in error_msg.lower():
#                 raise ValueError("Error de autenticación con Sip. Contacta al administrador.") from e
#             elif "rate limit" in error_msg.lower():
#                 raise ValueError("Sip está recibiendo muchas solicitudes. Por favor, espera un momento.") from e
#             elif "model" in error_msg.lower():
#                 raise ValueError("El modelo de IA no está disponible. Contacta al administrador.") from e
#             else:
#                 raise ValueError(f"Error al comunicarse con Sip: {error_msg}") from e
    
    def chat_completion_sync(self, messages: List[Dict[str, str]]) -> str:
        """
        Realiza petición de chat completion a Groq de forma síncrona.
        
        Args:
            messages: Lista de mensajes en formato dict
            
        Returns:
            str: Respuesta generada por el modelo
        """
        if not self.validate_api_key():
            raise ValueError("API key de Groq no configurada o inválida")
        
        try:
            logger.debug(f"🌊 [SYNC] Enviando {len(messages)} mensajes a Groq API")
            logger.debug(f"🌊 [SYNC] Modelo: {self.model}")
            
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=float(self.timeout) if self.timeout else None
            )
            
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    return content
                else:
                    raise ValueError("La API de Groq devolvió una respuesta vacía")
            else:
                raise ValueError("La API de Groq no devolvió ninguna opción de respuesta")
                
        except (RateLimitError, APIConnectionError, APIStatusError) as e:
            logger.error(f"🌊 [SYNC] Error en Groq API: {str(e)}")
            raise ValueError(f"Error al comunicarse con Sip: {str(e)}") from e
    
    def stream_chat_completion(self, messages: List[Dict[str, str]]):
        """
        Realiza streaming de chat completion desde Groq.
        
        Args:
            messages: Lista de mensajes en formato dict
            
        Yields:
            str: Fragmentos de la respuesta generada
        """
        if not self.validate_api_key():
            raise ValueError("API key de Groq no configurada o inválida")
        
        try:
            logger.debug(f"🌊 [STREAM] Iniciando streaming con modelo: {self.model}")
            
            stream = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
                        
        except (RateLimitError, APIConnectionError, APIStatusError) as e:
            logger.error(f"🌊 [STREAM] Error en streaming: {str(e)}")
            raise ValueError(f"Error en streaming: {str(e)}") from e
    
    def validate_api_key(self) -> bool:
        """
        Valida si la API key está configurada correctamente.
        
        Returns:
            bool: True si la API key es válida
        """
        return bool(settings.GROQ_API_KEY and len(settings.GROQ_API_KEY) > 10)
    
    def get_model_info(self) -> Dict[str, str]:
        """
        Retorna información sobre la configuración del modelo.
        
        Returns:
            Dict: Información del modelo
        """
        model_info = self.MODELS.get(self.model, {})
        return {
            "model": self.model,
            "description": model_info.get("description", "Modelo personalizado"),
            "context_window": str(model_info.get("context_window", "N/A")),
            "temperature": str(self.temperature),
            "max_tokens": str(self.max_tokens),
            "timeout": str(self.timeout),
            "api_key_configured": self.validate_api_key()
        }
    
    def get_available_models(self) -> Dict[str, Dict]:
        """
        Retorna el modelo disponible en Groq.
        
        Returns:
            Dict: Información del modelo disponible
        """
        return self.MODELS
    
    async def test_connection(self) -> bool:
        """
        Prueba la conexión con la API de Groq.
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            logger.info("🌊 Probando conexión con Groq API...")
            
            test_messages = [
                {"role": "system", "content": "Eres un asistente de prueba."},
                {"role": "user", "content": "Responde con 'OK' si puedes leer esto."}
            ]
            
            response = await self.chat_completion(test_messages)
            success = "OK" in response.upper()
            
            if success:
                logger.info("✅ Conexión con Groq API exitosa")
            else:
                logger.warning(f"⚠️ Respuesta inesperada en test: {response}")
            
            return success
            
        except (RateLimitError, APIConnectionError, APIStatusError) as e:
            logger.error(f"🌊 Error en test de conexión: {str(e)}")
            return False
    
    def set_model(self, model_name: str) -> bool:
        """
        Cambia el modelo utilizado por el cliente.
        Nota: Por defecto solo está disponible openai/gpt-oss-120b.
        
        Args:
            model_name: Nombre del modelo a usar
            
        Returns:
            bool: True si el modelo fue cambiado exitosamente
        """
        if model_name in self.MODELS:
            self.model = model_name
            logger.info(f"🌊 Modelo cambiado a: {model_name}")
            return True
        else:
            logger.error(f"🌊 Modelo no encontrado: {model_name}")
            logger.info(f"🌊 Solo disponible: {self.DEFAULT_MODEL}")
            return False
