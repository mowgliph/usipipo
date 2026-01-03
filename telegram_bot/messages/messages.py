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
            "• `📊 Estado`: Muestra tu consumo y límites.\n"
            "• `💰 Operaciones`: Sistema de referidos, VIP y pagos.\n\n"
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
        MENU_TITLE = "🎫 **Soporte**\n\nElige una opción:"

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
        
        INSUFFICIENT_BALANCE = (
            "💰 **Saldo Insuficiente**\n\n"
            "Necesitas {required} estrellas. Tu saldo actual es: {current}.\n"
            "Recarga en el menú de Operaciones."
        )
        
        NO_DEPOSIT_FOR_DELETE = (
            "⚠️ **Depósito Requerido**\n\n"
            "Debes realizar al menos un depósito para poder eliminar claves.\n"
            "Esto asegura un uso responsable del servicio."
        )
        
        REFERRAL_CODE_INVALID = (
            "❌ **Código de Referido Inválido**\n\n"
            "El código '{code}' no existe o ha expirado.\n"
            "Verifica el código e intenta nuevamente."
        )
        
        REFERRAL_SELF = (
            "🚫 **Auto-Referido**\n\n"
            "No puedes usar tu propio código de referido."
        )

    class Operations:
        MENU_TITLE = "💰 **Operaciones**\n\nElige una opción:"
        BALANCE_INFO = (
            "⭐ **Balance de Estrellas**\n\n"
            "👤 **Usuario:** {name}\n"
            "💰 **Saldo:** {balance} estrellas\n"
            "📥 **Total Depositado:** {total_deposited} estrellas\n"
            "👥 **Ganancias por Referidos:** {referral_earnings} estrellas"
        )
        DEPOSIT_INSTRUCTIONS = (
            "⭐ **Recargar Estrellas**\n\n"
            "1. Ve a @BotFather y envía el comando `/mybots`\n"
            "2. Selecciona tu bot y luego 'Payments'\n"
            "3. Sigue las instrucciones para enviar estrellas\n\n"
            "Una vez completado, tu saldo se actualizará automáticamente."
        )
        VIP_PLAN_INFO = (
            "👑 **Plan VIP**\n\n"
            "Beneficios:\n"
            "• ✅ Hasta {max_keys} claves simultáneas\n"
            "• 📦 {data_limit} GB por clave\n"
            "• 🔄 Reset mensual de datos\n"
            "• 🚀 Prioridad en soporte\n\n"
            "Precio: {cost} estrellas por mes\n\n"
            "Selecciona la duración:"
        )
        VIP_PURCHASE_SUCCESS = (
            "🎉 **¡Felicidades! Ahora eres VIP**\n\n"
            "Tu plan VIP está activo hasta el {expiry_date}\n\n"
            "✅ Límite de claves aumentado a {max_keys}\n"
            "✅ Límite de datos por clave: {data_limit} GB\n"
            "✅ Reset mensual automático"
        )
        REFERRAL_PROGRAM = (
            "👥 **Programa de Referidos**\n\n"
            "¡Invita a tus amigos y gana **10%** de por vida!\n\n"
            "🔗 **Tu enlace personalizado:**\n"
            "`https://t.me/{bot_username}?start={referral_code}`\n\n"
            "📊 **Estadísticas:**\n"
            "• 👥 Referidos directos: {direct_referrals}\n"
            "• 💰 Ganancias totales: {total_earnings} estrellas\n"
            "• 📈 Comisión: {commission}% de cada depósito\n\n"
            "El pago es automático cuando tus referidos recargan."
        )
        REFERRAL_CODE = (
            "📋 **Tu código de referido:**\n\n"
            "`{referral_code}`\n\n"
            "Comparte este código con tus amigos o usa el enlace:"
        )
        SHARE_REFERRAL = (
            "¡Hola! Te recomiendo usar **uSipipo VPN Manager** 🌐\n\n"
            "Es un servicio de VPN privado y seguro con:\n"
            "• ✅ WireGuard y Outline\n"
            "• 🔒 Sin registros\n"
            "• 🚀 Alta velocidad\n\n"
            "Usa mi código de referido: **{referral_code}**\n"
            "O haz clic aquí: https://t.me/{bot_username}?start={referral_code}"
        )
