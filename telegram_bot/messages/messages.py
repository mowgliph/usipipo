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
            "🔑 **Llaves Activas:** **{count}** / {max}\n"
            "📈 **Consumo Total:** **{usage}** MB\n"
            "⭐ **Estrellas Disponibles:** **{stars}**\n"
            "📋 **Estado de la Cuenta:** {status}\n\n"
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
            "💬 *Chat de Soporte Abierto*\n"
            "━━━━━━━━━━━━\n\n"
            "Estás conectado con nuestro equipo.\n\n"
            "📝 Describe tu problema y te\n"
            "responderemos lo antes posible.\n\n"
            "💡 _Tip: Sé específico para una_\n"
            "_respuesta más rápida._"
        )
        
        TICKET_CLOSED = (
            "✅ **Ticket cerrado**\n\n"
            "Gracias por contactarnos.\n"
            "¡Esperamos haberte ayudado!"
        )
        
        NEW_TICKET_ADMIN = (
            "🔔 <b>Nuevo Ticket de Soporte</b>\n"
            "━━━━━━━━━━━━\n\n"
            "👤 Usuario: <b>{name}</b>\n"
            "🆔 ID: <code>{user_id}</code>\n\n"
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

    class Tasks:
        """Mensajes del sistema de tareas."""
        
        MENU_TITLE = (
            "✅ **Centro de Tareas**\n"
            "━━━━━━━━━━━━\n\n"
            "Completa tareas y gana estrellas ⭐\n"
            "para comprar planes VIP 👑"
        )
        
        NO_TASKS = (
            "📭 **No hay tareas disponibles**\n\n"
            "Vuelve más tarde para ver nuevas tareas."
        )
        
        TASK_DETAIL = (
            "📋 **{title}**\n"
            "━━━━━━━━━━━━\n\n"
            "{description}\n\n"
            "━━━━━━━━━━━━\n\n"
            "⭐ **Recompensa:** {reward_stars} estrellas\n"
            "{guide_section}"
        )
        
        TASK_GUIDE = (
            "📖 **Guía:**\n{guide_text}\n\n"
        )
        
        TASK_COMPLETED = (
            "✅ **¡Tarea Completada!**\n\n"
            "Has completado: **{title}**\n\n"
            "🎁 Recompensa disponible: **{reward_stars}** ⭐\n\n"
            "Toca el botón para reclamar tu recompensa."
        )
        
        REWARD_CLAIMED = (
            "🎉 **¡Recompensa Reclamada!**\n\n"
            "Se han acreditado **{reward_stars}** ⭐ a tu cuenta.\n\n"
            "💰 Nuevo balance: **{balance}** ⭐"
        )
        
        TASK_ALREADY_COMPLETED = (
            "ℹ️ Esta tarea ya está completada.\n\n"
            "Puedes reclamar tu recompensa si aún no lo has hecho."
        )
        
        TASK_ALREADY_CLAIMED = (
            "ℹ️ Ya reclamaste la recompensa de esta tarea."
        )
        
        SUMMARY = (
            "📊 **Resumen de Tareas**\n"
            "━━━━━━━━━━━━\n\n"
            "✅ Disponibles: **{available}**\n"
            "🔄 En progreso: **{in_progress}**\n"
            "🎉 Completadas: **{completed}**\n\n"
            "Selecciona una opción para ver más detalles:"
        )
        
        ADMIN_CREATE_TASK = (
            "📝 **Crear Nueva Tarea**\n\n"
            "Envía los datos de la tarea en el siguiente formato:\n\n"
            "**Título**\n"
            "Descripción de la tarea\n\n"
            "**Recompensa:** X estrellas\n"
            "**Guía:** (opcional) Instrucciones detalladas\n\n"
            "Ejemplo:\n"
            "Únete a nuestro canal\n"
            "Síguenos en nuestro canal de Telegram para recibir actualizaciones\n\n"
            "**Recompensa:** 5 estrellas\n"
            "**Guía:** 1. Busca @canal_usipipo\n2. Únete al canal\n3. ¡Listo!"
        )
        
        ADMIN_TASK_CREATED = (
            "✅ **Tarea Creada**\n\n"
            "**Título:** {title}\n"
            "**Recompensa:** {reward_stars} ⭐\n"
            "**ID:** `{task_id}`"
        )
        
        ADMIN_TASK_LIST = (
            "📋 **Lista de Tareas**\n"
            "━━━━━━━━━━━━\n\n"
            "{tasks_list}"
        )
        
        ADMIN_TASK_ITEM = (
            "{status} **{title}**\n"
            "Recompensa: {reward_stars} ⭐\n"
            "ID: `{task_id}`\n\n"
        )

    class Help:
        """Mensajes del centro de ayuda."""
        
        MENU_TITLE = (
            "⚙️ **Centro de Ayuda**\n\n"
            "¿En qué podemos ayudarte?\n\n"
            "Selecciona una opción:"
        )
        
        USAGE_GUIDE = (
            "📖 **Guía de Uso**\n"
            "━━━━━━━━━━━━\n\n"
            "🔹 **¿Cómo crear una llave VPN?**\n\n"
            "1. Toca el botón **➕ Crear Nueva**\n"
            "2. Selecciona el protocolo:\n"
            "   • **Outline (SS)** - Para móviles\n"
            "   • **WireGuard** - Para PC y gaming\n"
            "3. ¡Listo! Tu llave se generará automáticamente\n\n"
            "━━━━━━━━━━━━\n\n"
            "🔹 **¿Cómo usar mis llaves?**\n\n"
            "1. Ve a **🛡️ Mis Llaves**\n"
            "2. Selecciona la llave que quieres usar\n"
            "3. Copia la configuración o el enlace\n"
            "4. Configúrala en tu cliente VPN\n\n"
            "━━━━━━━━━━━━\n\n"
            "🔹 **Protocolos disponibles:**\n\n"
            "📱 **Outline (Shadowsocks)**\n"
            "   • Ideal para móviles\n"
            "   • Ligero y eficiente\n"
            "   • Perfecto para saltar bloqueos\n\n"
            "💻 **WireGuard**\n"
            "   • Máxima velocidad\n"
            "   • Ideal para PC y gaming\n"
            "   • Streaming en HD sin lag\n\n"
            "━━━━━━━━━━━━\n\n"
            "💡 **Tip:** Si una conexión falla,\n"
            "elimínala y crea una nueva. ¡Es instantáneo!"
        )
        
        CONFIGURATION = (
            "🔧 **Guía de Configuración**\n"
            "━━━━━━━━━━━━\n\n"
            "📱 **Para Android/iOS (Outline):**\n\n"
            "1. Descarga la app **Outline** desde:\n"
            "   • Google Play Store\n"
            "   • App Store\n"
            "2. Abre la app y toca **➕ Agregar servidor**\n"
            "3. Escanea el código QR o pega el enlace\n"
            "4. Toca **Conectar** y ¡listo!\n\n"
            "━━━━━━━━━━━━\n\n"
            "💻 **Para Windows/Mac/Linux (WireGuard):**\n\n"
            "1. Descarga WireGuard desde:\n"
            "   • https://www.wireguard.com/install/\n"
            "2. Abre WireGuard y toca **➕ Agregar túnel**\n"
            "3. Selecciona **Crear desde archivo**\n"
            "4. Pega la configuración que te enviamos\n"
            "5. Activa el túnel y ¡conectado!\n\n"
            "━━━━━━━━━━━━\n\n"
            "🌐 **Para routers (WireGuard):**\n\n"
            "1. Configura WireGuard en tu router\n"
            "2. Importa el archivo de configuración\n"
            "3. Todos tus dispositivos estarán protegidos\n\n"
            "━━━━━━━━━━━━\n\n"
            "❓ **¿Problemas de conexión?**\n\n"
            "• Verifica que copiaste bien la configuración\n"
            "• Asegúrate de tener internet activo\n"
            "• Intenta eliminar y crear una nueva llave\n"
            "• Contacta a soporte si persiste el problema"
        )
        
        FAQ = (
            "❓ **Preguntas Frecuentes**\n"
            "━━━━━━━━━━━━\n\n"
            "🔹 **¿Cuántas llaves puedo tener?**\n\n"
            "• Plan Gratis: **2 llaves** simultáneas\n"
            "• Plan VIP: **10 llaves** simultáneas\n\n"
            "━━━━━━━━━━━━\n\n"
            "🔹 **¿Cuánto datos incluye cada llave?**\n\n"
            "• Plan Gratis: **10 GB** por llave\n"
            "• Plan VIP: **100 GB** por llave\n"
            "• Los datos se renuevan mensualmente\n\n"
            "━━━━━━━━━━━━\n\n"
            "🔹 **¿Cómo obtengo más estrellas?**\n\n"
            "• Recarga directamente desde Telegram\n"
            "• Invita amigos con tu código de referido\n"
            "• Gana estrellas jugando en la sala de juegos\n"
            "• Completa logros y desbloquea recompensas\n\n"
            "━━━━━━━━━━━━\n\n"
            "🔹 **¿Qué es el plan VIP?**\n\n"
            "El plan VIP te da:\n"
            "• Hasta 10 llaves simultáneas\n"
            "• 100 GB por llave (vs 10 GB gratis)\n"
            "• Reset mensual automático\n"
            "• Soporte prioritario\n"
            "• Sin límites de velocidad\n\n"
            "━━━━━━━━━━━━\n\n"
            "🔹 **¿Cómo funciona el programa de referidos?**\n\n"
            "• Comparte tu código único\n"
            "• Gana **10%** de cada depósito de tus referidos\n"
            "• Las ganancias son de por vida\n"
            "• Sin límite de referidos\n\n"
            "━━━━━━━━━━━━\n\n"
            "🔹 **¿Mis datos están seguros?**\n\n"
            "✅ Sí, garantizamos:\n"
            "• **Cero logs** - No guardamos tu actividad\n"
            "• **Encriptación** de extremo a extremo\n"
            "• **Sin registros** de conexión\n"
            "• **Privacidad total**\n\n"
            "━━━━━━━━━━━━\n\n"
            "🔹 **¿Puedo usar la VPN en múltiples dispositivos?**\n\n"
            "Sí, cada llave puede usarse en un dispositivo.\n"
            "Crea múltiples llaves para múltiples dispositivos.\n\n"
            "━━━━━━━━━━━━\n\n"
            "💡 **¿Tienes más preguntas?**\n\n"
            "Contacta a nuestro equipo de soporte:\n"
            "• Toca **🎫 Soporte** en el menú\n"
            "• Crea un ticket y te responderemos pronto"
        )

    class Cancel:
        """Mensajes para cancelación de operaciones."""
        
        CANCEL_MESSAGE = (
            "❌ **Operación cancelada**\n\n"
            "Has cancelado el proceso actual.\n"
            "👇 Usa el menú principal para continuar:"
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

    class Broadcast:
        """Mensajes del sistema de broadcast mejorado."""
        
        WELCOME = (
            "📢 **Sistema de Broadcast**\n"
            "━━━━━━━━━━━━\n\n"
            "Envía mensajes masivos a todos los usuarios.\n\n"
            "**Opciones disponibles:**\n"
            "• 📝 Escribir mensaje personalizado\n"
            "• 📋 Usar template predefinido\n"
            "• 📸 Enviar con foto\n"
            "• ⚙️ Configurar opciones avanzadas\n\n"
            "👇 Selecciona una opción:"
        )
        
        SELECT_TEMPLATE = (
            "📋 **Seleccionar Template**\n"
            "━━━━━━━━━━━━\n\n"
            "Elige un template o escribe tu mensaje personalizado:\n\n"
            "👇 Selecciona un template:"
        )
        
        INPUT_MESSAGE = (
            "✍️ **Crear Mensaje Personalizado**\n"
            "━━━━━━━━━━━━\n\n"
            "Envía el contenido del mensaje:\n\n"
            "**Formato soportado:**\n"
            "• Texto con formato *Markdown*\n"
            "• Emojis y símbolos\n"
            "• Enlaces y menciones\n\n"
            "💡 **Tip:** Puedes usar /cancel en cualquier momento."
        )
        
        INPUT_PHOTO = (
            "📸 **Agregar Foto**\n"
            "━━━━━━━━━━━━\n\n"
            "Envía una foto para acompañar el mensaje.\n\n"
            "O escribe 'continuar' para enviar solo texto."
        )
        
        PREVIEW_HEADER = (
            "👁️ **Vista Previa del Broadcast**\n"
            "━━━━━━━━━━━━\n\n"
        )
        
        PREVIEW_FOOTER = (
            "━━━━━━━━━━━━\n\n"
            "👥 **Destinatarios:** {count} usuarios\n"
            "📊 **Tipo:** {type}\n\n"
            "¿Confirmar el envío?"
        )
        
        SENDING = (
            "🚀 **Enviando Broadcast...**\n"
            "━━━━━━━━━━━━\n\n"
            "⏳ Por favor espera, esto puede tomar unos momentos...\n\n"
            "📊 Progreso: {current}/{total}"
        )
        
        SUCCESS_SUMMARY = (
            "✅ **Broadcast Completado**\n"
            "━━━━━━━━━━━━\n\n"
            "📤 **Enviados exitosamente:** {success}\n"
            "❌ **Errores:** {errors}\n"
            "👥 **Total usuarios:** {total}\n"
            "⏱️ **Tiempo:** {duration}s\n\n"
            "📝 **Mensaje enviado:**\n"
            "_{preview}_"
        )
        
        CANCELLED = (
            "❌ **Broadcast Cancelado**\n"
            "━━━━━━━━━━━━\n\n"
            "El proceso de broadcast ha sido cancelado.\n"
            "No se envió ningún mensaje."
        )
        
        NO_USERS = (
            "⚠️ **Sin Usuarios**\n"
            "━━━━━━━━━━━━\n\n"
            "No hay usuarios registrados para enviar el broadcast."
        )
        
        ERROR_PREVIEW = (
            "❌ **Error al Generar Preview**\n\n"
            "Por favor, intenta de nuevo o contacta al soporte técnico."
        )
        
        # Templates predefinidos
        TEMPLATES = {
            "maintenance": (
                "🔧 **Mantenimiento Programado**\n"
                "━━━━━━━━━━━━\n\n"
                "Estimado usuario,\n\n"
                "Te informamos que realizaremos un mantenimiento programado.\n\n"
                "**Fecha:** {date}\n"
                "**Hora:** {time}\n"
                "**Duración estimada:** {duration}\n\n"
                "Durante este período, el servicio puede experimentar interrupciones.\n\n"
                "Gracias por tu comprensión.\n\n"
                "— Equipo uSipipo"
            ),
            "update": (
                "🎉 **Nueva Actualización Disponible**\n"
                "━━━━━━━━━━━━\n\n"
                "¡Hola!\n\n"
                "Tenemos excelentes noticias: hemos lanzado una nueva actualización con mejoras importantes.\n\n"
                "**Nuevas características:**\n"
                "• {feature1}\n"
                "• {feature2}\n"
                "• {feature3}\n\n"
                "¡Actualiza la app para disfrutar de estas mejoras!\n\n"
                "— Equipo uSipipo"
            ),
            "promotion": (
                "🎁 **Oferta Especial**\n"
                "━━━━━━━━━━━━\n\n"
                "¡Aprovecha esta oportunidad única!\n\n"
                "**{promo_title}**\n\n"
                "{promo_description}\n\n"
                "**Válido hasta:** {expiry_date}\n\n"
                "No te lo pierdas. ¡Actúa ahora!\n\n"
                "— Equipo uSipipo"
            ),
            "welcome": (
                "👋 **¡Bienvenido a uSipipo VPN!**\n"
                "━━━━━━━━━━━━\n\n"
                "Gracias por unirte a nuestra comunidad.\n\n"
                "**Para comenzar:**\n"
                "1. Crea tu primera llave VPN\n"
                "2. Configura tu dispositivo\n"
                "3. ¡Disfruta de navegación segura!\n\n"
                "Si necesitas ayuda, estamos aquí para ti.\n\n"
                "— Equipo uSipipo"
            ),
            "custom": None  # Para mensajes personalizados
        }
