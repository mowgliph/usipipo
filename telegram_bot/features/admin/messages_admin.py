"""
Mensajes para panel administrativo de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""


class AdminMessages:
    """Mensajes para panel administrativo."""
    
    # ============================================
    # MENU
    # ============================================
    
    class Menu:
        """Mensajes del menú administrativo."""
        
        MAIN = (
            "🔧 **Panel Administrativo**\n\n"
            "Selecciona una opción para gestionar el sistema:\n\n"
            "👥 **Usuarios** - Gestión de cuentas\n"
            "🔑 **Llaves VPN** - Administración de accesos\n"
            "📊 **Servidor** - Estado y métricas\n"
            "⚙️ **Configuración** - Ajustes del sistema"
        )
    
    # ============================================
    # USERS
    # ============================================
    
    class Users:
        """Mensajes de gestión de usuarios."""
        
        HEADER = "👥 **Gestión de Usuarios**\n\n"
        
        NO_USERS = (
            "📭 **Sin Usuarios**\n\n"
            "No hay usuarios registrados en el sistema."
        )
        
        USER_DETAILS = (
            "👤 **Detalles del Usuario**\n\n"
            "🆔 **ID:** {user_id}\n"
            "👤 **Nombre:** {full_name}\n"
            "🔖 **Username:** @{username}\n"
            "📅 **Registro:** {created_at}\n"
            "🟢 **Estado:** {status}\n"
            "⭐ **Balance:** {balance} estrellas\n"
            "👑 **VIP:** {vip_status}\n"
            "🔑 **Llaves:** {keys_count} activas"
        )
        
        USER_BANNED = "🚫 **Usuario Baneado**\n\nEl usuario ha sido suspendido exitosamente."
        USER_UNBANNED = "✅ **Usuario Rehabilitado**\n\nEl usuario ha sido rehabilitado exitosamente."
        USER_DELETED = "🗑️ **Usuario Eliminado**\n\nEl usuario y todos sus datos han sido eliminados."
    
    # ============================================
    # KEYS
    # ============================================
    
    class Keys:
        """Mensajes de gestión de llaves."""
        
        HEADER = "🔑 **Gestión de Llaves VPN**\n\n"
        
        NO_KEYS = (
            "📭 **Sin Llaves**\n\n"
            "No hay llaves VPN registradas en el sistema."
        )
        
        KEY_DETAILS = (
            "🔑 **Detalles de la Llave**\n\n"
            "🆔 **ID:** {key_id}\n"
            "📛 **Nombre:** {name}\n"
            "👤 **Usuario:** {user_id}\n"
            "📡 **Protocolo:** {type}\n"
            "🖥️ **Servidor:** {server}\n"
            "📊 **Uso:** {usage}/{limit} GB\n"
            "🟢 **Estado:** {status}\n"
            "📅 **Creada:** {created_at}\n"
            "⏰ **Expira:** {expires_at}"
        )
        
        KEY_DELETED = "🗑️ **Llave Eliminada**\n\nLa llave VPN ha sido eliminada exitosamente."
        KEY_SUSPENDED = "⏸️ **Llave Suspendida**\n\nLa llave ha sido suspendida temporalmente."
        KEY_REACTIVATED = "✅ **Llave Reactivada**\n\nLa llave ha sido reactivada exitosamente."
    
    # ============================================
    # SERVER
    # ============================================
    
    class Server:
        """Mensajes de estado del servidor."""
        
        HEADER = "📊 **Estado del Servidor**\n\n"
        
        SYSTEM_HEALTHY = "✅ **Sistema Saludable**\n\nTodos los servicios funcionando correctamente."
        SYSTEM_WARNING = "⚠️ **Advertencia del Sistema**\n\nSe detectaron problemas que requieren atención."
        SYSTEM_CRITICAL = "🚨 **Estado Crítico**\n\nSe requieren acciones inmediatas."
        
        RESTART_SUCCESS = "🔄 **Servicio Reiniciado**\n\nEl servicio se ha reiniciado exitosamente."
        MAINTENANCE_MODE = "🔧 **Modo Mantenimiento**\n\nEl sistema está en modo mantenimiento."
    
    # ============================================
    # ERRORS
    # ============================================
    
    class Error:
        """Mensajes de error."""
        
        SYSTEM_ERROR = (
            "❌ **Error del Sistema**\n\n"
            "No pude completar la operación solicitada.\n\n"
            "Por favor, revisa los logs e intenta más tarde."
        )
        
        ACCESS_DENIED = (
            "🚫 **Acceso Denegado**\n\n"
            "No tienes permisos para realizar esta acción.\n\n"
            "Esta función está reservada para administradores."
        )
        
        USER_NOT_FOUND = (
            "❌ **Usuario No Encontrado**\n\n"
            "El usuario especificado no existe en el sistema."
        )
        
        KEY_NOT_FOUND = (
            "❌ **Llave No Encontrada**\n\n"
            "La llave especificada no existe en el sistema."
        )
        
        OPERATION_FAILED = (
            "❌ **Operación Fallida**\n\n"
            "No se pudo completar la operación.\n\n"
            "Error: {error}"
        )
    
    # ============================================
    # SUCCESS
    # ============================================
    
    class Success:
        """Mensajes de éxito."""
        
        OPERATION_COMPLETED = (
            "✅ **Operación Completada**\n\n"
            "La acción se ha realizado exitosamente."
        )
        
        CHANGES_SAVED = (
            "💾 **Cambios Guardados**\n\n"
            "La configuración ha sido actualizada correctamente."
        )
        
        BACKUP_CREATED = (
            "📦 **Backup Creado**\n\n"
            "Se ha creado una copia de seguridad exitosamente.\n"
            "📁 Archivo: {filename}"
        )
    
    # ============================================
    # LOGS
    # ============================================
    
    class Logs:
        """Mensajes de gestión de logs."""
        
        HEADER = "📋 **Logs del Sistema**\n\n"
        
        NO_LOGS = (
            "📭 **Sin Logs**\n\n"
            "No hay archivos de logs disponibles."
        )
        
        LOGS_DISPLAY = (
            "📋 **Últimas Líneas de Log**\n\n"
            "```{logs_content}```\n\n"
            "📅 *Extraído: {timestamp}*"
        )
        
        LOGS_ERROR = (
            "❌ **Error al Leer Logs**\n\n"
            "No se pudieron leer los archivos de log.\n"
            "Error: {error}"
        )
        
        LOGS_CLEARED = "🧹 **Logs Limpiados**\n\nLos archivos de log han sido limpiados exitosamente."
