"""
Mensajes del bot uSipipo VPN Manager.
Optimizado para UX/UI con tono profesional y amigable.

Author: uSipipo Team
Version: 2.0.0
"""


class Messages:
    """Contenedor principal de todos los mensajes del bot."""
    
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
        
        HELP = (
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
            "📭 **Sin llaves activas**\n\n"
            "Aún no tienes conexiones configuradas.\n\n"
            "👉 Toca **➕ Crear Nueva** para comenzar."
        )
        
        DETAIL = (
            "━━━━━━━━━━━━\n"
            "📌 **{name}**\n\n"
            "📡 Protocolo: `{type}`\n"
            "📅 Creada: {date}\n"
            "📊 Consumo: {usage}\n"
            "🆔 `{id}`\n"
        )
        
        CONFIRM_DELETE = (
            "⚠️ **Confirmar eliminación**\n\n"
            "¿Eliminar la llave **{name}**?\n\n"
            "Esta acción es irreversible y\n"
            "perderás el acceso inmediatamente."
        )
        
        DELETED = (
            "🗑️ **Llave eliminada**\n\n"
            "El acceso ha sido revocado correctamente."
        )
        
        LIMIT_REACHED = (
            "🔒 **Límite alcanzado**\n\n"
            "Has llegado al máximo de {max} llaves.\n\n"
            "💡 **Opciones:**\n"
            "• Elimina una llave existente\n"
            "• Actualiza a **VIP** para más llaves"
        )


    class Status:
        """Mensajes de estado y estadísticas."""
        
        HEADER = "📊 **Panel de Control**"
        
        INFO = (
            "━━━━━━━━━━━━\n\n"
            "👤 **{name}**\n\n"
            "🔑 Llaves: **{count}** / {max}\n"
            "📈 Consumo: **{usage}**\n"
            "⭐ Estrellas: **{stars}**\n"
            "📋 Estado: {status}\n\n"
            "━━━━━━━━━━━━"
        )
        
        VIP_BADGE = "👑 VIP"
        FREE_BADGE = "🆓 Gratuito"
    
    class Support:
        """Mensajes del sistema de soporte."""
        
        MENU_TITLE = (
            "🎫 **Centro de Soporte**\n"
            "━━━━━━━━━━━━\n\n"
            "¿En qué podemos ayudarte?"
        )
        
        OPEN_TICKET = (
            "💬 **Chat de Soporte Abierto**\n"
            "━━━━━━━━━━━━\n\n"
            "Estás conectado con nuestro equipo.\n\n"
            "📝 Describe tu problema y te\n"
            "responderemos lo antes posible.\n\n"
            "💡 *Tip: Sé específico para una\n"
            "respuesta más rápida.*"
        )
        
        TICKET_CLOSED = (
            "✅ **Ticket cerrado**\n\n"
            "Gracias por contactarnos.\n"
            "¡Esperamos haberte ayudado!"
        )
        
        NEW_TICKET_ADMIN = (
            "🔔 **Nuevo Ticket de Soporte**\n"
            "━━━━━━━━━━━━\n\n"
            "👤 Usuario: **{name}**\n"
            "🆔 ID: `{user_id}`\n\n"
            "Responde a este mensaje para contactar."
        )
        
        USER_MESSAGE_TO_ADMIN = "📩 **{name}:**\n{text}"
        
        ADMIN_MESSAGE_TO_USER = (
            "👨‍💻 **Soporte uSipipo:**\n\n"
            "{text}"
        )
        
        TICKET_AUTO_CLOSED = (
            "⏰ **Ticket cerrado automáticamente**\n\n"
            "Han pasado 48h sin actividad.\n"
            "Abre uno nuevo si necesitas ayuda."
        )


    class Errors:
        """Mensajes de error."""

        GENERIC = (
            "❌ <b>Algo salió mal</b>\n\n"
            "{error}\n\n"
            "Si persiste, contacta a soporte."
        )
        
        NETWORK = (
            "🌐 **Sin conexión**\n\n"
            "No pudimos conectar con el servidor.\n"
            "Verifica tu internet e intenta de nuevo."
        )
        
        PERMISSION_DENIED = (
            "🚫 **Acceso denegado**\n\n"
            "No tienes permisos para esta acción."
        )
        
        LIMIT_REACHED = (
            "🔒 **Límite alcanzado**\n\n"
            "Máximo de {resource} permitidos.\n"
            "Elimina uno para crear otro."
        )
        
        NOT_FOUND = (
            "🔍 **No encontrado**\n\n"
            "El recurso no existe o fue eliminado."
        )
        
        EXPIRED = (
            "⏰ **Sesión expirada**\n\n"
            "Esta operación caducó.\n"
            "Inicia el proceso nuevamente."
        )
        
        MAINTENANCE = (
            "🔧 **Mantenimiento**\n\n"
            "Sistema en mantenimiento.\n"
            "Vuelve en unos minutos."
        )
        
        INSUFFICIENT_BALANCE = (
            "💰 **Saldo insuficiente**\n\n"
            "Necesitas: **{required}** ⭐\n"
            "Tu saldo: **{current}** ⭐\n\n"
            "Recarga en **💰 Operaciones**."
        )
        
        NO_DEPOSIT_FOR_DELETE = (
            "⚠️ **Acción restringida**\n\n"
            "Realiza al menos un depósito\n"
            "para poder eliminar llaves.\n\n"
            "Esto previene el abuso del servicio."
        )
        
        REFERRAL_CODE_INVALID = (
            "❌ **Código inválido**\n\n"
            "El código `{code}` no existe.\n"
            "Verifica e intenta de nuevo."
        )
        
        REFERRAL_SELF = (
            "🚫 **Código propio**\n\n"
            "No puedes usar tu propio código."
        )


    class Operations:
        """Mensajes de operaciones y pagos."""
        
        MENU_TITLE = (
            "💰 **Centro de Operaciones**\n"
            "━━━━━━━━━━━━\n\n"
            "Gestiona tu cuenta y beneficios:"
        )
        
        BALANCE_INFO = (
            "⭐ **Mi Balance**\n"
            "━━━━━━━━━━━━\n\n"
            "👤 {name}\n\n"
            "💰 Saldo actual: **{balance}** ⭐\n"
            "📥 Total depositado: **{total_deposited}** ⭐\n"
            "👥 Por referidos: **{referral_earnings}** ⭐"
        )
        
        DEPOSIT_INSTRUCTIONS = (
            "⭐ **Recargar Estrellas**\n"
            "━━━━━━━━━━━━\n\n"
            "Envía estrellas de Telegram para\n"
            "recargar tu cuenta.\n\n"
            "📌 Tu saldo se actualiza al instante."
        )
        
        VIP_PLAN_INFO = (
            "👑 **Plan VIP**\n"
            "━━━━━━━━━━━━\n\n"
            "**Beneficios exclusivos:**\n\n"
            "✅ Hasta **{max_keys}** llaves activas\n"
            "📦 **{data_limit} GB** por llave\n"
            "🔄 Reset mensual automático\n"
            "⚡ Soporte prioritario\n\n"
            "━━━━━━━━━━━━\n\n"
            "💎 Precio: **{cost}** ⭐ / mes"
        )
        
        VIP_PURCHASE_SUCCESS = (
            "🎉 **¡Bienvenido al Club VIP!**\n"
            "━━━━━━━━━━━━\n\n"
            "Tu plan está activo hasta:\n"
            "📅 **{expiry_date}**\n\n"
            "**Beneficios activados:**\n"
            "✅ {max_keys} llaves disponibles\n"
            "✅ {data_limit} GB por llave\n"
            "✅ Reset mensual incluido\n\n"
            "¡Disfruta tu experiencia premium! 👑"
        )
        
        REFERRAL_PROGRAM = (
            "👥 **Programa de Referidos**\n"
            "━━━━━━━━━━━━\n\n"
            "🎁 Gana **10%** de cada depósito\n"
            "de tus referidos. ¡De por vida!\n\n"
            "🔗 **Tu enlace:**\n"
            "`https://t.me/{bot_username}?start={referral_code}`\n\n"
            "━━━━━━━━━━━━\n\n"
            "📊 **Tus estadísticas:**\n\n"
            "👥 Referidos: **{direct_referrals}**\n"
            "💰 Ganado: **{total_earnings}** ⭐\n"
            "📈 Comisión: **{commission}%**"
        )
        
        REFERRAL_CODE = (
            "📋 **Tu Código de Referido**\n"
            "━━━━━━━━━━━━\n\n"
            "`{referral_code}`\n\n"
            "Compártelo y gana por cada amigo."
        )
        
        SHARE_REFERRAL = (
            "🌐 <b>uSipipo VPN</b> — Internet sin límites\n\n"
            "Te invito a usar mi VPN privada:\n\n"
            "✅ WireGuard + Outline\n"
            "✅ Sin registros\n"
            "✅ Alta velocidad\n\n"
            "👉 Usa mi código: <code>{referral_code}</code>\n"
            "🔗 https://t.me/{bot_username}?start={referral_code}"
        )

    class Games:
        """Mensajes del sistema de juegos."""
        
        MENU_TITLE = (
            "🎮 **Sala de Juegos**\n"
            "━━━━━━━━━━━━\n\n"
            "¡Diviértete y gana estrellas!"
        )
        
        WIN = (
            "🎉 **¡GANASTE!**\n\n"
            "Premio: **+{amount}** ⭐"
        )
        
        LOSE = (
            "😔 **Suerte para la próxima**\n\n"
            "Perdiste: **-{amount}** ⭐"
        )

    class Admin:
        """Mensajes administrativos."""
        
        UNAUTHORIZED = (
            "🚫 **Acceso restringido**\n\n"
            "Función solo para administradores."
        )
        
        BROADCAST_CONFIRM = (
            "📢 **Confirmar Broadcast**\n\n"
            "Mensaje a enviar:\n\n"
            "{message}\n\n"
            "👥 Destinatarios: **{count}** usuarios"
        )
        
        BROADCAST_SUCCESS = (
            "✅ **Broadcast completado**\n\n"
            "📤 Enviados: **{sent}**\n"
            "❌ Fallidos: **{failed}**"
        )
