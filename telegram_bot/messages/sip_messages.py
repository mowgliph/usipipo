"""
Mensajes para el asistente IA Sip de uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""


class SipMessages:
    """Mensajes del asistente IA Sip."""
    
    # ============================================
    # BIENVENIDA E INTRODUCCIÓN
    # ============================================
    
    WELCOME = """🌊 **¡Hola! Soy Sip, tu asistente especializado de uSipipo** 🌊

Estoy aquí para ayudarte con todo lo relacionado con VPN, seguridad y privacidad.

🤖 **¿En qué puedo ayudarte?**

🔌 **Conexiones VPN:**
• Problemas para conectar
• Configuración en diferentes dispositivos
• Solución de errores comunes

🔒 **Seguridad y Privacidad:**
• Cifrado de datos
• Protección en redes públicas
• Mejores prácticas de seguridad

⚡ **Optimización:**
• Mejorar velocidad de conexión
• Elegir el servidor adecuado
• Solucionar lentitud

📱 **Configuración:**
• WireGuard y Outline
• iOS, Android, Windows, Mac, Linux
• Importación de configuraciones

💡 **Escribe tu pregunta** y te ayudaré de inmediato.

🔴 *Para finalizar el chat, escribe "Finalizar"*

🌊 *Sip aquí para ayudarte*"""
    
    # ============================================
    # ESTADOS DE CONVERSACIÓN
    # ============================================
    
    CONVERSATION_STARTED = """🌊 **Conversación iniciada con Sip**

¡Perfecto! Ahora puedes hacerme cualquier pregunta sobre VPN, seguridad o privacidad.

Escribe tu pregunta y responderé lo antes posible. 🌊"""
    
    CONVERSATION_ENDED = """🌊 **Conversación finalizada**

¡Gracias por usar el asistente Sip de uSipipo!

Si necesitas más ayuda, puedes:
• Volver a iniciar una conversación con Sip
• Crear un ticket de soporte con un humano
• Consultar las preguntas frecuentes

🌊 *Sip aquí para ayudarte cuando lo necesites*"""
    
    CONVERSATION_ESCALATED = """🌊 **Conversación escalada a soporte humano**

He detectado que tu problema requiere atención especializada.

✅ **Ticket creado automáticamente**
📝 Un especialista te ayudará lo antes posible
⏰ Tiempo de respuesta estimado: 1-2 horas

🌊 *Sip aquí para ayudarte*"""
    
    # ============================================
    # MENSAJES DE ERROR
    # ============================================
    
    ERROR_NO_ACTIVE_CONVERSATION = """🌊 **No hay conversación activa**

Para comenzar a chatear con Sip, primero inicia una conversación desde el menú de soporte.

🔙 Vuelve al menú de soporte para comenzar."""
    
    ERROR_PROCESSING_MESSAGE = """🌊 **Lo siento, tuve un problema**

No pude procesar tu mensaje correctamente. Por favor:

1. Intenta reformular tu pregunta
2. Si el problema persiste, crea un ticket de soporte
3. O vuelve a intentar en unos momentos

🌊 *Sip aquí para ayudarte*"""
    
    ERROR_API_UNAVAILABLE = """🌊 **Sip no está disponible temporalmente**

El servicio de IA no está respondiendo en este momento. Por favor:

1. Intenta de nuevo en unos minutos
2. Crea un ticket de soporte con un humano
3. Vuelve más tarde

Disculpa las molestias. 🌊"""
    
    ERROR_RATE_LIMIT = """🌊 **Demasiadas solicitudes**

Has enviado demasiados mensajes en poco tiempo. Por favor:

1. Espera unos segundos antes de continuar
2. Sé más específico en tus preguntas
3. Si necesitas ayuda urgente, crea un ticket

🌊 *Sip aquí para ayudarte*"""
    
    # ============================================
    # MENSAJES DE INFORMACIÓN
    # ============================================
    
    TYPING_INDICATOR = """🌊 Sip está pensando..."""
    
    SEARCHING_INFO = """🌊 Sip está buscando la mejor solución..."""
    
    ANALYZING_PROBLEM = """🌊 Sip está analizando tu problema..."""
    
    # ============================================
    # SUGERENCIAS DE PREGUNTAS
    # ============================================
    
    SUGGESTED_QUESTIONS = """💡 **Preguntas frecuentes que puedo responder:**

🔌 **Conexión:**
• "¿Por qué no conecta mi VPN?"
• "¿Cómo configuro WireGuard en mi celular?"
• "¿Por qué se desconecta mi VPN?"

🔒 **Seguridad:**
• "¿Es segura mi conexión VPN?"
• "¿Qué cifrado usa uSipipo?"
• "¿Puedo usar VPN en WiFi público?"

⚡ **Velocidad:**
• "¿Por qué mi VPN es lenta?"
• "¿Cómo mejoro la velocidad de conexión?"
• "¿Qué servidor debo elegir?"

📱 **Configuración:**
• "¿Cómo instalo la app de WireGuard?"
• "¿Cómo importo mi configuración?"
• "¿Dónde encuentro mi llave VPN?"

Escribe tu pregunta o selecciona una de estas opciones. 🌊"""
    
    # ============================================
    # MENSAJES DE ESCALADO
    # ============================================
    
    ESCALATION_NOTICE = """🌊 **Escalando a soporte humano**

Tu pregunta requiere atención especializada. Voy a crear un ticket de soporte para que un especialista te ayude.

📝 *Resumen de lo que intentamos:*
{summary}

✅ *Ticket creado: #{ticket_id}*
⏰ *Tiempo de respuesta: 1-2 horas*

🌊 *Sip aquí para ayudarte*"""
    
    ESCALATION_CONFIRMATION = """🌊 **Ticket de soporte creado**

✅ Tu ticket ha sido creado exitosamente

🆔 **Ticket ID:** #{ticket_id}
📋 **Estado:** Pendiente de revisión
⏰ **Tiempo estimado:** 1-2 horas

Un especialista revisará tu caso y te responderá lo antes posible.

Mientras tanto, puedes:
• Revisar el estado de tu ticket
• Hacer otras preguntas a Sip
• Consultar las preguntas frecuentes

🌊 *Sip aquí para ayudarte*"""
    
    # ============================================
    # MENSAJES DE FINALIZACIÓN
    # ============================================
    
    FAREWELL_MESSAGE = """🌊 **¡Hasta pronto!**

Gracias por usar el asistente Sip de uSipipo.

📊 **Resumen de esta sesión:**
• Mensajes intercambiados: {message_count}
• Duración: {duration}
• Temas tratados: {topics}

¿Necesitas más ayuda?
• 🤖 Iniciar nueva conversación con Sip
• 🎫 Crear ticket de soporte
• 📋 Consultar preguntas frecuentes

🌊 *Sip aquí para ayudarte cuando lo necesites*"""
    
    # ============================================
    # MENSAJES DE CONTEXTO
    # ============================================
    
    CONTEXT_REMINDER = """🌊 **Recordatorio de contexto**

Estamos hablando sobre: {topic}

Último mensaje: "{last_message}"

¿Deseas continuar con este tema o cambiar de conversación?

🌊 *Sip aquí para ayudarte*"""
    
    # ============================================
    # MENSAJES DE LÍMITES
    # ============================================
    
    MESSAGE_LIMIT_REACHED = """🌊 **Límite de mensajes alcanzado**

Has alcanzado el límite de mensajes en esta conversación.

Para continuar:
1. Finaliza esta conversación
2. Inicia una nueva conversación
3. O crea un ticket de soporte

Esto me ayuda a mantener conversaciones enfocadas y eficientes.

🌊 *Sip aquí para ayudarte*"""
    
    SESSION_TIMEOUT = """🌊 **Sesión expirada**

Tu conversación ha expirado por inactividad.

Para continuar:
1. Inicia una nueva conversación con Sip
2. O crea un ticket de soporte

Las conversaciones inactivas se cierran automáticamente después de 24 horas para proteger tu privacidad.

🌊 *Sip aquí para ayudarte*"""
