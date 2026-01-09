"""
Cliente de infraestructura para la API de Groq - Asistente IA Sip.

Author: uSipipo Team
Version: 1.1.0
"""

from typing import List, Dict, Optional
from groq import Groq, AsyncGroq
from groq import RateLimitError, APIConnectionError, APIStatusError
from config import settings
from utils.logger import logger


class GroqClient:
    """Cliente de infraestructura para API de Groq."""
    
    def __init__(self):
        """Inicializa el cliente de Groq con configuración."""
        if not settings.GROQ_API_KEY:
            logger.warning("⚠️ GROQ_API_KEY no configurada. Sip no funcionará correctamente.")
        
        # Cliente síncrono (para operaciones que no requieren async)
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        # Cliente asíncrono (para operaciones async)
        self.async_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        
        self.model = settings.GROQ_MODEL
        self.temperature = settings.GROQ_TEMPERATURE
        self.max_tokens = settings.GROQ_MAX_TOKENS
        self.timeout = settings.GROQ_TIMEOUT
        
        logger.info(f"🌊 GroqClient inicializado con modelo: {self.model}")
    
    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """
        Realiza petición de chat completion a Groq de forma asíncrona.
        
        Args:
            messages: Lista de mensajes en formato dict [{"role": "user", "content": "..."}]
            
        Returns:
            str: Respuesta generada por el modelo
            
        Raises:
            ValueError: Si la API key no está configurada
            RateLimitError: Si se excede el límite de llamadas
            APIConnectionError: Si hay error de conexión
            APIStatusError: Si hay error en la respuesta de la API
            Exception: Para otros errores
        """
        if not self.validate_api_key():
            raise ValueError("API key de Groq no configurada o inválida")
        
        try:
            logger.debug(f"🌊 Enviando {len(messages)} mensajes a Groq API")
            logger.debug(f"🌊 Modelo: {self.model}, Timeout: {self.timeout}s")
            
            # Usar cliente asíncrono para mantener el event loop libre
            response = await self.async_client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=float(self.timeout) if self.timeout else None
            )
            
            logger.debug(f"🌊 Respuesta recibida de Groq: {response}")
            
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    logger.debug(f"🌊 Contenido de respuesta: {len(content)} caracteres")
                    return content
                else:
                    logger.error("🌊 Groq API devolvió contenido vacío en la respuesta")
                    raise ValueError("La API de Groq devolvió una respuesta vacía")
            else:
                logger.error(f"🌊 Groq API no devolvió choices. Response: {response}")
                raise ValueError("La API de Groq no devolvió ninguna opción de respuesta")
                
        except RateLimitError as e:
            logger.error(f"🌊 Rate limit excedido en Groq API: {str(e)}")
            raise ValueError("Has excedido el límite de llamadas a la IA. Por favor, espera un momento.")
        
        except APIConnectionError as e:
            logger.error(f"🌊 Error de conexión con Groq API: {str(e)}")
            raise ValueError("No se pudo conectar con el servicio de IA. Verifica tu conexión a internet.")
        
        except APIStatusError as e:
            logger.error(f"🌊 Error de estado en Groq API: {str(e)}")
            raise ValueError(f"Error del servicio de IA: código {e.status_code}")
        
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"🌊 Error en Groq API [{error_type}]: {error_msg}")
            
            if "timeout" in error_msg.lower():
                raise ValueError("Sip está tardando mucho en responder. Por favor, intenta con un mensaje más corto.")
            elif "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                raise ValueError("Error de autenticación con Sip. Contacta al administrador.")
            elif "rate limit" in error_msg.lower():
                raise ValueError("Sip está recibiendo muchas solicitudes. Por favor, espera un momento.")
            elif "model" in error_msg.lower():
                raise ValueError("El modelo de IA no está disponible. Contacta al administrador.")
            else:
                raise ValueError(f"Error al comunicarse con Sip: {error_msg}")
    
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
        return {
            "model": self.model,
            "temperature": str(self.temperature),
            "max_tokens": str(self.max_tokens),
            "timeout": str(self.timeout),
            "api_key_configured": self.validate_api_key()
        }
    
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
            
        except Exception as e:
            logger.error(f"🌊 Error en test de conexión: {str(e)}")
            return False
