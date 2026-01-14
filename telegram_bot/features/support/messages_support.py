"""
Mensajes para sistema de soporte técnico de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""


class SupportMessages:
    """Mensajes para sistema de soporte."""
    
    # ============================================
    # TICKETS
    # ============================================
    
    class Tickets:
        """Mensajes de tickets de soporte."""
        
        OPEN_TICKET = (
            "🎫 **Soporte Activado**\n\n"
            "Tu ticket ha sido creado exitosamente.\n\n"
            "💬 Ahora puedes escribir tu mensaje y será enviado al equipo de soporte.\n\n"
            "🔴 Para finalizar, presiona el botón 'Finalizar Soporte'."
        )
        
        TICKET_CLOSED = (
            "🎫 **Soporte Finalizado**\n\n"
            "Tu ticket ha sido cerrado.\n\n"
            "📝 Si necesitas más ayuda, puedes crear un nuevo ticket en cualquier momento.\n\n"
            "🌊 ¡Gracias por usar uSipipo!"
        )
        
        NEW_TICKET_ADMIN = (
            "🎫 **Nuevo Ticket de Soporte**\n\n"
            "👤 **Usuario:** {name}\n"
            "🆔 **ID:** {user_id}\n\n"
            "💬 Responde a este mensaje para comunicarte directamente con el usuario."
        )
        
        NO_TICKETS = (
            "📭 **Sin Tickets Activos**\n\n"
            "No tienes tickets de soporte abiertos.\n\n"
            "💡 Crea un nuevo ticket si necesitas ayuda."
        )
    
    # ============================================
    # FAQ
    # ============================================
    
    class FAQ:
        """Mensajes de preguntas frecuentes."""
        
        HEADER = (
            "❓ **Preguntas Frecuentes**\n\n"
            "Selecciona una categoría para ver las preguntas más comunes:"
        )
        
        CONNECTION = (
            "🌐 **Conexión VPN**\n\n"
            "❓ **¿Por qué no conecta mi VPN?**\n"
            "• Verifica tu conexión a internet\n"
            "• Revisa que los datos de la llave sean correctos\n"
            "• Intenta con otro servidor\n\n"
            "❓ **¿Cómo configuro WireGuard?**\n"
            "• Descarga la app WireGuard\n"
            "• Escanea el QR o importa el archivo .conf\n"
            "• Activa la conexión\n\n"
            "❓ **¿Por qué es lenta mi VPN?**\n"
            "• Prueba con servidores más cercanos\n"
            "• Verifica tu velocidad de internet\n"
            "• Contacta soporte si persiste"
        )
        
        ACCOUNT = (
            "👤 **Cuenta y Perfil**\n\n"
            "❓ **¿Cómo cambio mi contraseña?**\n"
            "• Ve a Configuración > Seguridad\n"
            "• Selecciona Cambiar Contraseña\n"
            "• Confirma con tu email\n\n"
            "❓ **¿Cómo obtengo VIP?**\n"
            "• Ve a Operaciones > Plan VIP\n"
            "• Selecciona el plan deseado\n"
            "• Completa el pago\n\n"
            "❓ **¿Cómo elimino mi cuenta?**\n"
            "• Contacta a soporte para solicitar eliminación\n"
            "• Se eliminarán todos tus datos permanentemente"
        )
        
        BILLING = (
            "💰 **Pagos y Facturación**\n\n"
            "❓ **¿Métodos de pago aceptados?**\n"
            "• Tarjetas de crédito/débito\n"
            "• Transferencias bancarias\n"
            "• Criptomonedas (BTC, ETH)\n\n"
            "❓ **¿Cómo solicito un reembolso?**\n"
            "• Contacta a soporte dentro de 7 días\n"
            "• Explica el motivo del reembolso\n"
            "• Espera confirmación del equipo\n\n"
            "❓ **¿Facturas proforma?**\n"
            "• Solicítalas en soporte\n"
            "• Indica tu razón social y datos fiscales\n"
            "• Recibirás la factura en 24-48h"
        )
        
        TECHNICAL = (
            "🔧 **Problemas Técnicos**\n\n"
            "❓ **¿La app no responde?**\n"
            "• Reinicia la aplicación\n"
            "• Verifica tu conexión a internet\n"
            "• Actualiza a la última versión\n\n"
            "❓ **¿Error de autenticación?**\n"
            "• Verifica tus credenciales\n"
            "• Limpia caché de la app\n"
            "• Contacta soporte si persiste\n\n"
            "❓ **¿Problemas con el servidor?**\n"
            "• Revisa el estado del servidor\n"
            "• Prueba con otro servidor\n"
            "• Reporta el problema a soporte"
        )
    
    # ============================================
    # HELP
    # ============================================
    
    class Help:
        """Mensajes de ayuda general."""
        
        MAIN = (
            "⚙️ **Centro de Ayuda**\n\n"
            "Selecciona una opción:\n\n"
            "🎫 **Crear Ticket** - Habla con nuestro equipo\n"
            "📋 **Mis Tickets** - Revisa tus solicitudes\n"
            "❓ **FAQ** - Preguntas frecuentes\n"
            "📖 **Guía** - Tutoriales y manuales"
        )
        
        GUIDE = (
            "📖 **Guía de Uso**\n\n"
            "🔑 **Creación de Llaves VPN:**\n"
            "1. Ve a 'Mis Llaves'\n"
            "2. Presiona '➕ Crear Nueva'\n"
            "3. Selecciona el protocolo (Outline/WireGuard)\n"
            "4. Asigna un nombre\n"
            "5. ¡Listo para usar!\n\n"
            "📊 **Estado de Cuenta:**\n"
            "1. Presiona '📊 Estado'\n"
            "2. Revisa tu consumo y balance\n"
            "3. Verifica tus llaves activas\n\n"
            "💰 **Recarga de Balance:**\n"
            "1. Ve a 'Operaciones'\n"
            "2. Selecciona 'Mi Balance'\n"
            "3. Elige método de pago\n"
            "4. Confirma la transacción"
        )
    
    # ============================================
    # ERRORS
    # ============================================
    
    class Error:
        """Mensajes de error."""
        
        SYSTEM_ERROR = (
            "❌ **Error del Sistema**\n\n"
            "No pude procesar tu solicitud.\n\n"
            "Por favor, intenta más tarde o contacta soporte."
        )
        
        TICKET_ERROR = (
            "❌ **Error al Crear Ticket**\n\n"
            "No pude crear tu ticket de soporte.\n\n"
            "Por favor, intenta más tarde."
        )
        
        MESSAGE_ERROR = (
            "❌ **Error al Enviar Mensaje**\n\n"
            "Tu mensaje no pudo ser entregado.\n\n"
            "Por favor, intenta enviarlo nuevamente."
        )
        
        CLOSE_ERROR = (
            "❌ **Error al Cerrar Ticket**\n\n"
            "No pude cerrar tu ticket.\n\n"
            "Por favor, contacta al administrador."
        )
        
        ACCESS_DENIED = (
            "🚫 **Acceso Denegado**\n\n"
            "No tienes permisos para realizar esta acción."
        )
    
    # ============================================
    # SUCCESS
    # ============================================
    
    class Success:
        """Mensajes de éxito."""
        
        TICKET_CREATED = (
            "✅ **Ticket Creado**\n\n"
            "Tu ticket de soporte ha sido creado exitosamente.\n\n"
            "🆔 **ID:** #{ticket_id}\n"
            "📊 **Estado:** Abierto\n"
            "⏰ **Tiempo de respuesta:** 1-2 horas"
        )
        
        MESSAGE_SENT = (
            "✅ **Mensaje Enviado**\n\n"
            "Tu mensaje ha sido entregado al equipo de soporte.\n\n"
            "📝 Te responderán lo antes posible."
        )
        
        TICKET_CLOSED = (
            "✅ **Ticket Cerrado**\n\n"
            "Tu ticket ha sido cerrado exitosamente.\n\n"
            "📝 Si necesitas más ayuda, crea un nuevo ticket."
        )
