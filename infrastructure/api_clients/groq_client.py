"""
Cliente de infraestructura para la API de Groq - Asistente IA Sip.

Author: uSipipo Team
Version: 1.0.0
"""

from typing import List, Dict, Optional
from groq import Groq
from config import settings
from utils.logger import logger


class GroqClient:
    """Cliente de infraestructura para API de Groq."""
    
    def __init__(self):
        """Inicializa el cliente de Groq con configuración."""
        if not settings.GROQ_API_KEY:
            logger.warning("⚠️ GROQ_API_KEY no configurada. Sip no funcionará correctamente.")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.temperature = settings.GROQ_TEMPERATURE
        self.max_tokens = settings.GROQ_MAX_TOKENS
        self.timeout = settings.GROQ_TIMEOUT
        
        logger.info(f"🌊 GroqClient inicializado con modelo: {self.model}")
    
    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """
        Realiza petición de chat completion a Groq.
        
        Args:
            messages: Lista de mensajes en formato dict [{"role": "user", "content": "..."}]
            
        Returns:
            str: Respuesta generada por el modelo
            
        Raises:
            Exception: Si hay error en la API de Groq
        """
        try:
            logger.debug(f"🌊 Enviando {len(messages)} mensajes a Groq API")
            
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
            
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                logger.debug(f"🌊 Respuesta recibida de Groq: {len(content)} caracteres")
                return content
            else:
                logger.error("🌊 Groq API devolvió respuesta vacía")
                raise Exception("La API de Groq devolvió una respuesta vacía")
                
        except Exception as e:
            logger.error(f"🌊 Error en Groq API: {str(e)}")
            raise Exception(f"Error al comunicarse con Sip: {str(e)}")
    
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
            test_messages = [
                {"role": "system", "content": "Eres un asistente de prueba."},
                {"role": "user", "content": "Responde con 'OK' si puedes leer esto."}
            ]
            
            response = await self.chat_completion(test_messages)
            return "OK" in response.upper()
            
        except Exception as e:
            logger.error(f"🌊 Error en test de conexión: {str(e)}")
            return False
