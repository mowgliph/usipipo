class Messages:
    class Welcome:
        START = (
            "👋 ¡Bienvenido a **uSipipo VPN Manager**!\n\n"
            "Tu centro de control privado para túneles seguros.\n\n"
            "Usa el menú inferior para gestionar tus accesos."
        )
        HELP = (
            "📖 **Guía de Uso - uSipipo VPN**\n\n"
            "Este bot te permite gestionar tus propios accesos VPN de forma privada.\n\n"
            "🔹 **Protocolos disponibles:**\n"
            "• **Outline (Shadowsocks):** Ideal para saltar bloqueos de internet y censura. Es muy ligero en el consumo de batería.\n"
            "• **WireGuard:** El estándar moderno. Extremadamente rápido y seguro, ideal para gaming o streaming.\n\n"
            "🕹️ **Comandos principales:**\n"
            "• `➕ Crear Nueva`: Inicia el asistente de creación.\n"
            "• `🛡️ Mis Llaves`: Lista tus llaves, permite borrarlas o ver los datos de conexión.\n"
            "• `📊 Estado`: Muestra tu consumo y límites.\n\n"
            "⚠️ **Soporte:** Si tienes problemas con una conexión, intenta borrar la llave y crear una nueva."
        )

    class Keys:
        SELECT_TYPE = "🛡️ Selecciona el protocolo que deseas utilizar:"
        CREATED = "✅ ¡Llave **{type}** generada con éxito!"
        LIST_HEADER = "🔑 **Tus llaves de acceso:**"
        NO_KEYS = "📭 No tienes ninguna llave activa todavía."
        DETAIL = (
            "📌 **Nombre:** {name}\n"
            "📡 **Protocolo:** {type}\n"
            "📅 **Creada:** {date}\n"
            "🆔 `ID: {id}`"
        )
        CONFIRM_DELETE = "¿Estás seguro de que deseas eliminar la llave **{name}**? Esta acción revocará tu acceso inmediatamente."
        DELETED = "🗑️ Llave eliminada correctamente."

    class Status:
        HEADER = "📊 **Estado de tu cuenta**"
        INFO = (
            "👤 **Usuario:** {name}\n"
            "🔑 **Llaves:** {count} / {max}\n"
            "📈 **Consumo Total:** {usage} MB\n"
            "✅ **Estado:** {status}"
        )
    
    class Support:
        OPEN_TICKET = (
            "🎫 **Soporte Técnico**\n\n"
            "Se ha abierto un canal directo con el administrador.\n"
            "Escribe tu duda a continuación y te responderemos lo antes posible.\n\n"
            "📌 *Usa el botón de abajo para cerrar el chat cuando termines.*"
        )
        TICKET_CLOSED = "✅ El ticket ha sido cerrado. ¡Gracias por contactarnos!"
        NEW_TICKET_ADMIN = "⚠️ **Nuevo Ticket Abierto**\n👤 Usuario: {name}\n🆔 ID: `{user_id}`\n\nEscribe aquí para responderle."
        USER_MESSAGE_TO_ADMIN = "📩 **Mensaje de {name}:**\n{text}"
        ADMIN_MESSAGE_TO_USER = "👨‍💻 **Respuesta del Soporte:**\n{text}"

    class Errors:
        GENERIC = (
            "⚠️ **Error**\n\n"
            "{error}\n\n"
            "Si el problema persiste, contacta al soporte."
        )
        
        NETWORK = (
            "🌐 **Error de Conexión**\n\n"
            "No se pudo conectar con el servidor. "
            "Verifica tu conexión e intenta nuevamente."
        )
        
        PERMISSION_DENIED = (
            "🚫 **Acceso Denegado**\n\n"
            "No tienes permisos para realizar esta acción."
        )
        
        LIMIT_REACHED = (
            "🛑 **Límite Alcanzado**\n\n"
            "Has alcanzado el límite máximo de {resource}.\n"
            "Elimina uno existente antes de crear otro."
        )
        
        NOT_FOUND = (
            "🔍 **No Encontrado**\n\n"
            "El recurso solicitado no existe o fue eliminado."
        )
        
        EXPIRED = (
            "⏰ **Operación Expirada**\n\n"
            "Esta acción ha caducado. Inicia el proceso nuevamente."
        )
        
        MAINTENANCE = (
            "🔧 **Mantenimiento**\n\n"
            "El sistema está en mantenimiento temporalmente.\n"
            "Intenta nuevamente en unos minutos."
        )
