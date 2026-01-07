"""
Mensajes para funcionalidades de usuario regular del bot uSipipo.

Organiza los mensajes relacionados con:
- Menú principal y bienvenida
- Gestión de llaves VPN
- Estado y estadísticas
- Ayuda y soporte general

Author: uSipipo Team
Version: 1.0.0
"""


class UserMessages:
    """Mensajes para usuarios regulares del bot."""
    
    # ============================================
    # WELCOME & ONBOARDING
    # ============================================
    
    class Welcome:
        """Mensajes de bienvenida y onboarding."""
        
        START = (
            "👋 ¡Hola! Bienvenido a **uSipipo VPN**\n\n"
            "🔐 Tu servicio privado de túneles seguros.\n\n"
            "Navega sin restricciones, con total privacidad.\n\n"
            "👇 Usa el menú para comenzar:"
        )
        
        NEW_USER = (
            "🎉 ¡Bienvenido, **{name}**!\n\n"
            "Tu cuenta ha sido creada exitosamente.\n\n"
            "🎁 **Regalo de bienvenida:**\n"
            "• 2 llaves VPN gratuitas\n"
            "• 10 GB de datos por llave\n\n"
            "📱 Toca **➕ Crear Nueva** para generar tu primera conexión."
        )
        
        EXISTING_USER = (
            "👋 ¡Hola de nuevo, **{name}**!\n\n"
            "Todo listo para continuar.\n\n"
            "📊 Usa el menú para gestionar tus accesos."
        )
    
    # ============================================
    # KEYS MANAGEMENT
    # ============================================
    
    class Keys:
        """Mensajes relacionados con llaves VPN."""
        
        SELECT_TYPE = (
            "🛡️ **Selecciona tu protocolo**\n\n"
            "Elige según tu dispositivo y necesidad:"
        )
        
        CREATED = (
            "✅ **¡Llave creada exitosamente!**\n\n"
            "📡 Protocolo: **{type}**\n\n"
            "Sigue las instrucciones para conectarte."
        )
        
        LIST_HEADER = (
            "🔑 **Mis Llaves de Acceso**\n"
            "━━━━━━━━━━━━\n"
        )
        
        NO_KEYS = (
            "📭 **Sin llaves**\n\n"
            "Aún no tienes ninguna llave VPN.\n"
            "Toca **➕ Crear Nueva** para generar tu primera conexión."
        )
        
        DETAIL_HEADER = (
            "🔑 **Detalles de la Llave**\n"
            "━━━━━━━━━━━━\n"
            "\n"
            "📛 **Nombre:** {name}\n"
            "🖥️ **Servidor:** {server}\n"
            "📡 **Protocolo:** {protocol}\n"
            "📊 **Consumo:** {usage} / {limit} GB\n"
            "⏰ **Expiración:** {expiration}\n"
            "🟢 **Estado:** {status}\n"
        )
        
        STATISTICS = (
            "📊 **Estadísticas de Uso**\n"
            "━━━━━━━━━━━━\n"
            "\n"
            "📛 **Llave:** {name}\n"
            "📉 **Consumo Total:** {total_usage} GB\n"
            "📈 **Velocidad Promedio:** {avg_speed} Mbps\n"
            "🔴 **Descarga:** {download_usage} GB\n"
            "🔵 **Carga:** {upload_usage} GB\n"
            "⏱️ **Tiempo Conectado:** {connection_time}\n"
            "🟢 **Sesiones Activas:** {active_sessions}\n"
        )
        
        DELETED = "🗑️ **Llave eliminada exitosamente.**"
        
        RENAMED = "✅ **Llave renombrada a:** {new_name}"
    
    # ============================================
    # STATUS & INFO
    # ============================================
    
    class Status:
        """Mensajes de estado y información."""
        
        HEADER = (
            "📊 **Mi Estado en uSipipo**\n"
            "━━━━━━━━━━━━\n"
        )
        
        USER_INFO = (
            "👤 **Usuario:** {name}\n"
            "📞 **ID:** `{user_id}`\n"
            "📅 **Miembro desde:** {join_date}\n"
            "🟢 **Estado:** {status}\n"
        )
        
        KEYS_SUMMARY = (
            "🔐 **Resumen de Llaves:**\n"
            "   • Totales: {total_keys}\n"
            "   • Activas: {active_keys}\n"
            "   • WireGuard: {wireguard_count}\n"
            "   • Outline: {outline_count}\n"
        )
        
        DATA_USAGE = (
            "📈 **Consumo General:**\n"
            "   • Total: {total_usage} GB\n"
            "   • Límite: {total_limit} GB\n"
            "   • Disponible: {available} GB\n"
            "   • Porcentaje: {percentage}%\n"
        )
        
        ACHIEVEMENTS_SUMMARY = (
            "🏆 **Logros:**\n"
            "   • Completados: {completed}\n"
            "   • En Progreso: {in_progress}\n"
            "   • Puntos: {points}\n"
            "   • Recompensas Pendientes: {pending}\n"
        )
        
        VIP_STATUS = (
            "👑 **Estado VIP:**\n"
            "   • VIP: {is_vip}\n"
            "   • Plan: {vip_plan}\n"
            "   • Expira: {expiration}\n"
            "   • Descuento: {discount}%\n"
        )
    
    # ============================================
    # HELP & INFORMATION
    # ============================================
    
    class Help:
        """Mensajes de ayuda y documentación."""
        
        MAIN_MENU = (
            "📚 **Centro de Ayuda**\n"
            "━━━━━━━━━━━━\n\n"
            "🔹 **Protocolos disponibles:**\n\n"
            "📱 **Outline (Shadowsocks)**\n"
            "   Ideal para móviles. Ligero y eficiente.\n"
            "   Perfecto para saltar bloqueos.\n\n"
            "💻 **WireGuard**\n"
            "   Máxima velocidad. Ideal para PC,\n"
            "   gaming y streaming en HD.\n\n"
            "━━━━━━━━━━━━\n\n"
            "🎮 **Menú Principal:**\n\n"
            "• **➕ Crear Nueva** — Genera una llave\n"
            "• **🛡️ Mis Llaves** — Administra accesos\n"
            "• **📊 Estado** — Consumo y límites\n"
            "• **💰 Operaciones** — Referidos y VIP\n"
            "• **🎫 Soporte** — Ayuda directa\n\n"
            "━━━━━━━━━━━━\n\n"
            "💡 **Tip:** Si una conexión falla, elimínala\n"
            "y crea una nueva. ¡Es instantáneo!"
        )
        
        CONFIGURATION = (
            "🔧 **Configuración de Conexión**\n"
            "━━━━━━━━━━━━\n\n"
            "**Para Outline:**\n"
            "1. Descarga la app Outline\n"
            "2. Importa la clave QR o texto\n"
            "3. ¡Conecta y disfruta!\n\n"
            "**Para WireGuard:**\n"
            "1. Descarga la app WireGuard\n"
            "2. Descarga el archivo .conf\n"
            "3. Importa y conecta\n\n"
            "━━━━━━━━━━━━\n\n"
            "📱 **Apps recomendadas:**\n"
            "• Outline (iOS/Android)\n"
            "• WireGuard (todas las plataformas)\n"
        )
        
        TROUBLESHOOTING = (
            "🛠️ **Solución de Problemas**\n"
            "━━━━━━━━━━━━\n\n"
            "❓ **¿No funciona la conexión?**\n"
            "✓ Verifica tu conexión a internet\n"
            "✓ Prueba con otra llave\n"
            "✓ Reinicia la app\n\n"
            "❓ **¿Lenta la velocidad?**\n"
            "✓ Cambia de servidor\n"
            "✓ Verifica tu ancho de banda\n"
            "✓ Desconecta otros dispositivos\n\n"
            "❓ **¿Límite de datos alcanzado?**\n"
            "✓ Crea una nueva llave\n"
            "✓ Compra plan VIP\n"
            "✓ Espera a la renovación\n"
        )
        
        FAQ = (
            "❓ **Preguntas Frecuentes**\n"
            "━━━━━━━━━━━━\n\n"
            "**¿Es seguro?**\n"
            "Sí, usamos encriptación de grado militar.\n\n"
            "**¿Cuántas conexiones simultáneas?**\n"
            "Hasta 3 dispositivos por llave.\n\n"
            "**¿Se reinician los datos?**\n"
            "Sí, mensualmente. Puedes renovar antes.\n\n"
            "**¿Qué es VIP?**\n"
            "Datos ilimitados y velocidad prioritaria.\n"
        )
    
    # ============================================
    # CONFIRMATION DIALOGS
    # ============================================
    
    class Confirmation:
        """Mensajes de confirmación."""
        
        DELETE_KEY = (
            "⚠️ **¿Eliminar llave?**\n\n"
            "Nombre: **{name}**\n"
            "Servidor: **{server}**\n\n"
            "Esta acción no se puede deshacer."
        )
        
        RENAME_KEY = (
            "✏️ **Renombrar llave**\n\n"
            "Nombre actual: **{old_name}**\n\n"
            "Escribe el nuevo nombre:"
        )
        
        ERROR_RENAME = (
            "❌ **Error al renombrar**\n\n"
            "Por favor, intenta de nuevo."
        )
        
        SUCCESS_RENAME = (
            "✅ **Llave renombrada**\n\n"
            "Nuevo nombre: **{new_name}**"
        )
    
    # ============================================
    # ERRORS & WARNINGS
    # ============================================
    
    class Errors:
        """Mensajes de error y advertencias."""
        
        GENERIC_ERROR = (
            "❌ **Error procesando tu solicitud**\n\n"
            "Por favor, intenta más tarde."
        )
        
        NO_KEYS = (
            "❌ **Sin llaves disponibles**\n\n"
            "Crea una nueva llave para empezar."
        )
        
        LIMIT_EXCEEDED = (
            "⚠️ **Límite alcanzado**\n\n"
            "Has alcanzado el límite de llaves.\n"
            "Elimina una para crear una nueva."
        )
        
        KEY_EXPIRED = (
            "⏰ **Llave expirada**\n\n"
            "Esta llave ya no es válida.\n"
            "Crea una nueva."
        )
        
        INVALID_PROTOCOL = (
            "❌ **Protocolo inválido**\n\n"
            "Selecciona Outline o WireGuard."
        )
        
        CONNECTION_ERROR = (
            "🔌 **Error de conexión**\n\n"
            "No puedo conectar con el servidor.\n"
            "Intenta más tarde."
        )
