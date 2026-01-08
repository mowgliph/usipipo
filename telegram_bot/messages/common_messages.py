"""
Mensajes comunes reutilizables en toda la aplicación.

Organiza mensajes generales:
- Confirmaciones y diálogos
- Errores y excepciones
- Navegación y menús
- Estados y estatus

Author: uSipipo Team
Version: 1.0.0
"""


class CommonMessages:
    """Mensajes comunes a toda la aplicación."""
    
    # ============================================
    # NAVIGATION & MENUS
    # ============================================
    
    class Navigation:
        """Mensajes de navegación."""
        
        MAIN_MENU = (
            "🏠 **Menú Principal**\n"
            "━━━━━━━━━━━━\n\n"
            "Bienvenido a **uSipipo VPN**\n\n"
            "¿Qué deseas hacer?"
        )
        
        BACK = "⬅️ Volver"
        HOME = "🏠 Inicio"
        HELP = "❓ Ayuda"
        CANCEL = (
            "❌ **Operación Cancelada**\n\n"
            "Has vuelto al menú principal."
        )
        
        INVALID_OPTION = (
            "❌ **Opción inválida**\n\n"
            "Por favor, selecciona una opción válida."
        )
        
        LOADING = "⏳ Cargando..."
        
        TIMEOUT = (
            "⏱️ **Sesión expirada**\n\n"
            "Por favor, comienza de nuevo."
        )
    
    # ============================================
    # CONFIRMATIONS
    # ============================================
    
    class Confirmation:
        """Mensajes de confirmación."""
        
        YES = "✅ Sí"
        NO = "❌ No"
        CONFIRM = "✅ Confirmar"
        CANCEL = "❌ Cancelar"
        
        GENERIC = (
            "⚠️ **Confirmar acción**\n\n"
            "{message}\n\n"
            "¿Deseas continuar?"
        )
        
        DELETE = (
            "⚠️ **Confirmar eliminación**\n\n"
            "{item}\n\n"
            "⚠️ Esta acción no se puede deshacer."
        )
        
        SUCCESS = "✅ **Acción completada exitosamente.**"
        
        CANCELLED = "❌ **Acción cancelada.**"
    
    # ============================================
    # ERRORS & EXCEPTIONS
    # ============================================
    
    class Errors:
        """Mensajes de error."""
        
        GENERIC = (
            "❌ Error\n\n"
            "Algo salió mal. Intenta de nuevo.\n\n"
            "Detalle: {error}"
        )
        
        NETWORK = (
            "🌐 **Error de Conexión**\n\n"
            "No se pudo conectar con el servidor.\n"
            "Verifica tu conexión a internet."
        )
        
        TIMEOUT = (
            "⏱️ **Tiempo Agotado**\n\n"
            "La solicitud tardó demasiado.\n"
            "Intenta de nuevo."
        )
        
        SERVER_ERROR = (
            "🔴 **Error del Servidor**\n\n"
            "Estamos experimentando problemas.\n"
            "Intenta más tarde."
        )
        
        NOT_FOUND = (
            "🔍 **No Encontrado**\n\n"
            "El recurso solicitado no existe."
        )
        
        UNAUTHORIZED = (
            "🔐 **No Autorizado**\n\n"
            "No tienes permisos para esta acción."
        )
        
        FORBIDDEN = (
            "🚫 **Acceso Denegado**\n\n"
            "Esta acción no está permitida."
        )
        
        VALIDATION_ERROR = (
            "⚠️ **Datos Inválidos**\n\n"
            "{details}\n\n"
            "Por favor, intenta de nuevo."
        )
        
        MAINTENANCE = (
            "🔧 **Mantenimiento**\n\n"
            "Estamos mejorando nuestros servicios.\n"
            "Estaremos de vuelta en: {time}"
        )
        
        RATE_LIMIT = (
            "⏱️ **Demasiadas Solicitudes**\n\n"
            "Has excedido el límite de intentos.\n"
            "Intenta en {time} segundos."
        )
        
        REFERRAL_CODE_INVALID = (
            "❌ **Código de Referido Inválido**\n\n"
            "El código `{code}` no es válido\n"
            "o ya ha sido utilizado."
        )
    
    # ============================================
    # STATUS MESSAGES
    # ============================================
    
    class Status:
        """Mensajes de estado."""
        
        ACTIVE = "🟢 Activo"
        INACTIVE = "🔴 Inactivo"
        PENDING = "🟡 Pendiente"
        PROCESSING = "🔄 Procesando"
        COMPLETED = "✅ Completado"
        FAILED = "❌ Fallido"
        BLOCKED = "🚫 Bloqueado"
        
        LOADING = (
            "⏳ **Procesando...**\n\n"
            "Por favor espera."
        )
        
        PLEASE_WAIT = "⏳ Por favor espera..."
        
        SYNCING = "🔄 Sincronizando..."
    
    # ============================================
    # INPUT DIALOGS
    # ============================================
    
    class Input:
        """Mensajes para entrada de usuario."""
        
        SEND_TEXT = (
            "Escribe tu mensaje:\n\n"
            "(O presiona Cancelar para volver)"
        )
        
        SEND_NUMBER = (
            "Ingresa un número:\n\n"
            "(O presiona Cancelar para volver)"
        )
        
        INVALID_INPUT = (
            "❌ **Entrada Inválida**\n\n"
            "Por favor, intenta de nuevo."
        )
        
        INVALID_FORMAT = (
            "❌ **Formato Incorrecto**\n\n"
            "Usa el formato: {format}"
        )
        
        TOO_SHORT = (
            "❌ **Muy Corto**\n\n"
            "Mínimo {min_chars} caracteres."
        )
        
        TOO_LONG = (
            "❌ **Muy Largo**\n\n"
            "Máximo {max_chars} caracteres."
        )
    
    # ============================================
    # PAGINATION
    # ============================================
    
    class Pagination:
        """Mensajes de paginación."""
        
        HEADER = "Página {current}/{total} | Elementos: {count}"
        
        FIRST = "⏮️ Primera"
        PREVIOUS = "◀️ Anterior"
        NEXT = "▶️ Siguiente"
        LAST = "⏭️ Última"
        
        NO_MORE = (
            "ℹ️ **No hay más elementos**"
        )
        
        SHOWING = "Mostrando {start}-{end} de {total} elementos"
    
    # ============================================
    # DIALOGS
    # ============================================
    
    class Dialogs:
        """Mensajes de diálogos especiales."""
        
        WELCOME_BACK = (
            "👋 **¡Bienvenido de vuelta, {name}!**\n\n"
            "Fue un placer verte nuevamente."
        )
        
        GOODBYE = (
            "👋 **¡Hasta luego!**\n\n"
            "Que disfrutes tu día."
        )
        
        THANK_YOU = (
            "🙏 **Gracias**\n\n"
            "Apreciamos tu feedback."
        )
        
        COMING_SOON = (
            "🔜 **Próximamente**\n\n"
            "Esta funcionalidad estará disponible pronto."
        )
        
        BETA_FEATURE = (
            "🧪 **Función Beta**\n\n"
            "Estamos probando esta funcionalidad.\n"
            "Tu feedback nos ayuda a mejorar."
        )
    
    # ============================================
    # BUTTONS
    # ============================================
    
    class Buttons:
        """Etiquetas para botones comunes."""
        
        OK = "✅ Aceptar"
        CANCEL = "❌ Cancelar"
        BACK = "⬅️ Volver"
        NEXT = "▶️ Siguiente"
        SKIP = "⏭️ Omitir"
        DELETE = "🗑️ Eliminar"
        EDIT = "✏️ Editar"
        SAVE = "💾 Guardar"
        CLOSE = "✖️ Cerrar"
        REFRESH = "🔄 Actualizar"
        SHARE = "📤 Compartir"
        COPY = "📋 Copiar"
        DOWNLOAD = "📥 Descargar"
        UPLOAD = "📤 Cargar"
        ADD = "➕ Agregar"
        CREATE = "🆕 Crear"
        REMOVE = "➖ Quitar"
        MANAGE = "⚙️ Gestionar"
        SETTINGS = "⚙️ Configuración"
        INFO = "ℹ️ Información"
        DETAILS = "📋 Detalles"
        MORE = "➕ Más"
        LESS = "➖ Menos"
        SHOW = "👁️ Ver"
        HIDE = "👁️‍🗨️ Ocultar"
        ENABLE = "✅ Habilitar"
        DISABLE = "❌ Deshabilitar"
        START = "▶️ Iniciar"
        STOP = "⏹️ Detener"
        PAUSE = "⏸️ Pausar"
        RESUME = "▶️ Reanudar"
    
    # ============================================
    # RESPONSES
    # ============================================
    
    class Responses:
        """Respuestas comunes del bot."""
        
        UNDERSTANDING = "🤔 Entiendo..."
        
        THINKING = "🧠 Pensando..."
        
        PROCESSING = "⚙️ Procesando tu solicitud..."
        
        CHECKING = "🔍 Verificando..."
        
        READY = "✅ Listo para continuar."
        
        DONE = "✅ ¡Listo!"
        
        NOT_AVAILABLE = (
            "🚫 **No disponible**\n\n"
            "Esta función no está disponible en tu región o cuenta."
        )
        
        CONTACT_SUPPORT = (
            "🆘 **¿Necesitas ayuda?**\n\n"
            "Abre un ticket de soporte y te ayudaremos."
        )
    
    # ============================================
    # FORMATTING
    # ============================================
    
    class Formatting:
        """Patrones de formato de mensajes."""
        
        SECTION_HEADER = "━━━━━━━━━━━━"
        
        DIVIDER = "┌─────────────┐"
        
        BULLET = "•"
        
        ARROW = "→"
        
        SEPARATOR = "━━━━━━━━━━━━"
        
        INFO_ICON = "ℹ️"
        SUCCESS_ICON = "✅"
        ERROR_ICON = "❌"
        WARNING_ICON = "⚠️"
        LOADING_ICON = "⏳"
