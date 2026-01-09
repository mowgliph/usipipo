# 📘 Guía de la API de Groq - Integración con OpenAI y Modelo oss120

> **Documentación basada en https://console.groq.com**  
> Guía completa para usar la API de Groq con compatibilidad con OpenAI

## 📋 Tabla de Contenidos

1. [🎯 Resumen](#-resumen)
2. [🔑 Configuración de Credenciales](#-configuración-de-credenciales)
3. [📡 Endpoints de la API](#-endpoints-de-la-api)
4. [🤖 Modelos Disponibles](#-modelos-disponibles)
5. [💻 Ejemplos de Código](#-ejemplos-de-código)
6. [⚙️ Parámetros de Configuración](#-parámetros-de-configuración)
7. [🐛 Solución de Problemas](#-solución-de-problemas)
8. [📊 Límites y Cuotas](#-límites-y-cuotas)

---

## 🎯 Resumen

Groq proporciona una API **compatible con OpenAI**, lo que significa que puedes usar cualquier cliente de OpenAI existente pointing a los endpoints de Groq. Esto facilita la migración y el uso de modelos de alto rendimiento.

**Ventajas de Groq:**
- ⚡ **Inferencia ultrarrápida** - Modelos respondiendo en milisegundos
- 💰 **Precios competitivos** - Más económico que muchos proveedores
- 🔄 **Compatible con OpenAI** - Migra tu código sin cambios
- 🎯 **Modelos especializados** - Optimizados para diferentes casos de uso

---

## 🔑 Configuración de Credenciales

### 1. Obtener tu API Key

1. Ve a [https://console.groq.com](https://console.groq.com)
2. Inicia sesión o crea una cuenta
3. Navega a **API Keys** en el menú lateral
4. Clic en **Create API Key**
5. Copia tu key y guárdala en un lugar seguro

### 2. Configuración en tu Proyecto

#### Usando Variables de Entorno

```bash
# En tu archivo .env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### En Python

```python
import os
from groq import Groq

# Opción 1: Usar variable de entorno
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Opción 2: Directamente (no recomendado para producción)
client = Groq(
    api_key="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)
```

---

## 📡 Endpoints de la API

### Endpoint Principal

```
https://api.groq.com/openai/v1
```

### Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/chat/completions` | Generar respuestas de chat |
| `POST` | `/completions` | Generación de texto |
| `POST` | `/embeddings` | Obtener embeddings |
| `GET` | `/models` | Listar modelos disponibles |
| `GET` | `/models/{model_id}` | Obtener detalles de un modelo |

### Estructura de Chat Completion

```json
POST https://api.groq.com/openai/v1/chat/completions

{
  "model": "llama-3.1-8b-instant",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello!"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false
}
```

---

## 🤖 Modelos Disponibles

### Modelos de Chat (Chat Completions)

| Modelo | Descripción | Contexto | Velocidad |
|--------|-------------|----------|-----------|
| `llama-3.3-70b-versatile` | Llama 3.3 70B - Versátil | 128K | Rápido |
| `llama-3.1-8b-instant` | Llama 3.1 8B - Instantáneo | 128K | Muy Rápido |
| `llama-3.2-1b-preview` | Llama 3.2 1B - Preview | 128K | Ultrarrápido |
| `llama-3.2-3b-preview` | Llama 3.2 3B - Preview | 128K | Rápido |
| `gemma-7b-it` | Gemma 7B - Instruction | 8K | Rápido |
| **`gpt-oss-120b`** | OpenAI OSS 120B - Premium | 128K | Rápido ⭐ |

### Características del Modelo OSS120

El modelo **`gpt-oss-120b`** es un modelo premium de OpenAI disponible a través de Groq con las siguientes características:

- 📏 **128K tokens de contexto** - Capacidad para conversaciones largas
- 🧠 **120B parámetros** - Alta capacidad de razonamiento
- 🎯 **Optimizado para asistencia** - Ideal para chatbots y soporte
- ⚡ **Alta velocidad de inferencia** - Respuestas rápidas
- 💰 **Precio competitivo** - Más económico que la API directa de OpenAI

---

## 💻 Ejemplos de Código

### Python con SDK de Groq

```python
from groq import Groq
import os

# Inicializar cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Chat básico
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "Eres un asistente amable y útil."
        },
        {
            "role": "user",
            "content": "¿Cómo puedo configurar mi VPN?"
        }
    ],
    model="gpt-oss-120b",  # Usando el modelo OSS120
    temperature=0.7,
    max_tokens=1000,
)

print(chat_completion.choices[0].message.content)
```

### Python con Cliente OpenAI (Compatible)

```python
from openai import OpenAI

# Groq es compatible con OpenAI - solo cambia el base_url
client = OpenAI(
    api_key="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    base_url="https://api.groq.com/openai/v1"
)

# El código es idéntico a OpenAI
response = client.chat.completions.create(
    model="gpt-oss-120b",
    messages=[
        {"role": "user", "content": "Explica qué es WireGuard"}
    ],
    temperature=0.5,
)

print(response.choices[0].message.content)
```

### Streaming Responses

```python
from groq import Groq

client = Groq(api_key="tu_api_key")

stream = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "Crea un tutorial de 5 pasos para usar VPN"}
    ],
    model="gpt-oss-120b",
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Integración con uSipipo

```python
# infrastructure/api_clients/groq_client.py

from groq import Groq
from config import settings
import logging

logger = logging.getLogger(__name__)

class GroqClient:
    """Cliente para la API de Groq con soporte para modelos OSS120."""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.default_model = settings.GROQ_MODEL  # gpt-oss-120b
    
    async def get_chat_response(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Obtener respuesta del modelo de chat.
        
        Args:
            messages: Lista de mensajes [{role, content}]
            model: Modelo a usar (default: gpt-oss-120b)
            temperature: Creatividad (0.0-2.0)
            max_tokens: Máximo de tokens en respuesta
            
        Returns:
            Respuesta del modelo como string
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=model or self.default_model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error en Groq API: {e}")
            raise
    
    async def stream_response(
        self,
        messages: list,
        model: str = None
    ):
        """Generar respuesta con streaming."""
        stream = self.client.chat.completions.create(
            messages=messages,
            model=model or self.default_model,
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

# Uso en el servicio de IA
groq_client = GroqClient()

async def get_sip_response(user_message: str, context: list) -> str:
    """Obtener respuesta de Sip AI."""
    messages = [
        {"role": "system", "content": "Eres Sip, asistente de VPN de uSipipo."},
        *context,
        {"role": "user", "content": user_message}
    ]
    
    return await groq_client.get_chat_response(
        messages=messages,
        model="gpt-oss-120b",
        temperature=0.7,
        max_tokens=1000
    )
```

### Node.js / JavaScript

```javascript
import { Groq } from "groq-sdk";

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
});

async function chat() {
  const chatCompletion = await groq.chat.completions.create({
    messages: [
      { role: "system", content: "You are a helpful VPN assistant." },
      { role: "user", content: "How do I configure WireGuard?" }
    ],
    model: "gpt-oss-120b",
    temperature: 0.7,
  });

  console.log(chatCompletion.choices[0].message.content);
}

chat();
```

### cURL

```bash
curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -d '{
    "model": "gpt-oss-120b",
    "messages": [
      {
        "role": "system",
        "content": "You are Sip, a helpful VPN assistant."
      },
      {
        "role": "user",
        "content": "What is the difference between WireGuard and Outline?"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

---

## ⚙️ Parámetros de Configuración

### Parámetros de Chat Completion

| Parámetro | Tipo | Default | Rango | Descripción |
|-----------|------|---------|-------|-------------|
| `model` | string | Requerido | - | Modelo a usar |
| `messages` | array | Requerido | - | Mensajes de la conversación |
| `temperature` | float | 0.7 | 0.0-2.0 | Creatividad de respuestas |
| `max_tokens` | int | 1000 | 1-4096 | Máximo de tokens en respuesta |
| `top_p` | float | 1.0 | 0.0-1.0 | Nucleus sampling |
| `stream` | bool | false | - | Respuesta en streaming |
| `stop` | array | null | - | Secuencias de parada |
| `presence_penalty` | float | 0.0 | -2.0 a 2.0 | Penalización por presencia |
| `frequency_penalty` | float | 0.0 | -2.0 a 2.0 | Penalización por frecuencia |

### Configuración Recomendada para Sip AI

```python
# Configuración optimizada para asistente de VPN
config = {
    "model": "gpt-oss-120b",
    "temperature": 0.7,        # Balance entre creatividad y consistencia
    "max_tokens": 1000,        # Respuestas completas pero no excesivas
    "top_p": 0.95,             # Buena diversidad de respuestas
    "presence_penalty": 0.0,   # Mantener话题 relevante
    "frequency_penalty": 0.0,  # Evitar repeticiones
}
```

---

## 🐛 Solución de Problemas

### Error: "Invalid API Key"

```bash
# Verificar que la API key sea correcta
echo $GROQ_API_KEY

# Debe empezar con "gsk_"
```

**Solución:**
1. Verifica que la API key esté correctamente configurada
2. Asegúrate de no tener espacios extra
3. Regenera la key si es necesario

### Error: "Model not found"

```python
# Verificar modelos disponibles
import requests

response = requests.get(
    "https://api.groq.com/openai/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)
print(response.json())
```

**Solución:**
1. Verifica que el nombre del modelo sea correcto
2. Algunos modelos pueden estar en preview

### Error: "Rate limit exceeded"

```python
import time
from groq import Groq

client = Groq(api_key="tu_key")

# Implementar retry con backoff
for attempt in range(3):
    try:
        response = client.chat.completions.create(...)
        break
    except Exception as e:
        if "rate_limit" in str(e):
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            raise
```

**Solución:**
1. Implementar rate limiting en tu aplicación
2. Usar cacheo de respuestas cuando sea posible
3. Contactar a soporte si los límites son muy restrictivos

### Error: "Connection timeout"

```python
import httpx
from groq import Groq

# Usar cliente con timeout configurado
client = Groq(
    api_key="tu_key",
    http_client=httpx.Client(
        timeout=30.0,  # 30 segundos
        verify=True
    )
)
```

---

## 📊 Límites y Cuotas

### Límites de Rate (Típicos)

| Plan | RPM (Requests/Min) | TPM (Tokens/Min) |
|------|-------------------|------------------|
| Free | 10 | 10,000 |
| Pro | 100 | 500,000 |

### Precios (Ejemplos)

| Modelo | Input ($/1M tokens) | Output ($/1M tokens) |
|--------|---------------------|----------------------|
| llama-3.1-8b-instant | $0.04 | $0.04 |
| llama-3.3-70b-versatile | $0.59 | $0.79 |
| **gpt-oss-120b** | $1.00 | $1.50 |

### Optimización de Costos

```python
# Estrategias para reducir costos

# 1. Limitar max_tokens
async def get_response(user_message: str) -> str:
    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Más económico
        messages=[{"role": "user", "content": user_message}],
        max_tokens=500,  # Limitar respuesta
    )
    return response.choices[0].message.content

# 2. Usar caching
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_response(question: str) -> str:
    # Preguntas frecuentes cacheadas
    return get_response_sync(question)

# 3. Resumir contexto
async def summarize_context(context: str) -> str:
    """Resume el contexto para reducir tokens."""
    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Resume esto en 100 palabras:"},
            {"role": "user", "content": context}
        ],
        max_tokens=100,
    )
    return response.choices[0].message.content
```

---

## 🔐 Mejores Prácticas de Seguridad

### 1. No expongas tu API Key

```python
# ❌ MALO - Key en código
api_key = "gsk_xxxxxxxxxxxxxxxx"

# ✅ BUENO - Usar variables de entorno
import os
api_key = os.environ.get("GROQ_API_KEY")
```

### 2. Usa .env para desarrollo

```bash
# .env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
```

```python
# .gitignore
.env
*.env
```

### 3. Implementa logging seguro

```python
import logging

# Configurar logging sin exponer datos sensibles
logging.basicConfig(level=logging.INFO)

def log_interaction(user_id: str, response_length: int):
    logging.info(f"User {user_id} - Response length: {response_length} chars")
    # NO loguear el contenido de los mensajes
```

### 4. Valida inputs de usuario

```python
import re

def sanitize_message(message: str) -> str:
    """Sanitizar mensaje para prevenir inyecciones."""
    # Eliminar caracteres especiales problemáticos
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', message)
    # Limitar longitud
    return cleaned[:4000]  # Max contexto
```

---

## 📈 Integración con uSipipo

### Configuración en config.py

```python
# config.py

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # ... otras configuraciones ...
    
    # Groq AI Configuration
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "gpt-oss-120b"  # Modelo por defecto
    GROQ_TEMPERATURE: float = 0.7
    GROQ_MAX_TOKENS: int = 1000
    GROQ_TIMEOUT: int = 15
    
    @property
    def is_groq_configured(self) -> bool:
        return bool(self.GROQ_API_KEY)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

### Uso en AI Support Service

```python
# application/services/ai_support_service.py

from infrastructure.api_clients.groq_client import GroqClient
from config import settings

class AISupportService:
    """Servicio de soporte con IA."""
    
    def __init__(self):
        self.groq_client = GroqClient() if settings.is_groq_configured else None
    
    async def get_assistant_response(
        self,
        user_message: str,
        conversation_history: list = None
    ) -> str:
        """Obtener respuesta del asistente de IA."""
        
        if not self.groq_client:
            return "⚠️ El servicio de IA no está configurado."
        
        # Construir mensajes
        system_prompt = """Eres Sip, el asistente de VPN de uSipipo.
        Ayudas a usuarios con problemas de conexión VPN, configuración
        y seguridad. Sé amable, claro y conciso."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.groq_client.get_chat_response(
                messages=messages,
                model=settings.GROQ_MODEL,
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS
            )
            return response
            
        except Exception as e:
            logging.error(f"Error getting AI response: {e}")
            return "⚠️ Lo siento, tuve un problema procesando tu solicitud."
```

---

## 🔗 Recursos Adicionales

- 📖 [Documentación Oficial de Groq](https://console.groq.com/docs)
- 💻 [SDK Python de Groq](https://github.com/groq/groq-sdk)
- 📚 [Referencia de la API OpenAI](https://platform.openai.com/docs/api-reference)
- 🐛 [Reportar Issues](https://github.com/groq/groq-sdk/issues)

---

## 📝 Notas de la Versión

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2026-01-09 | Documentación inicial para uSipipo |
| 1.0.1 | 2026-01-09 | Añadido modelo gpt-oss-120b |

---

<div align="center">

**📘 Documentación de la API de Groq para uSipipo**  
*Integración rápida y sencilla con modelos de alto rendimiento*

[⬆️ Volver al inicio](#-guía-de-la-api-de-groq---integración-con-openai-y-modelo-oss120)

</div>
