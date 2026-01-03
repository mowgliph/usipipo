"""
Mensajes de administración para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

class AdminMessages:
    """Mensajes del sistema de administración."""
    
    # Menú principal
    MAIN_MENU = """🔧 **Panel de Administración**

👑 Bienvenido al panel de control de uSipipo VPN

Elige una opción para gestionar el sistema:"""
    
    # Usuarios
    NO_USERS = """📊 **Usuarios Registrados**

No hay usuarios registrados en el sistema."""
    
    USERS_LIST = """📊 **Usuarios Registrados**

{users}

*Mostrando los 10 usuarios más recientes*"""
    
    # Claves
    NO_KEYS = """🔐 **Claves VPN**

No hay claves registradas en el sistema."""
    
    KEYS_LIST = """🔐 **Claves VPN Registradas**

🔐 **WireGuard:** {wireguard_count} claves
🔒 **Outline:** {outline_count} claves

Selecciona una clave para gestionar:"""
    
    # Confirmación de eliminación
    KEY_NOT_FOUND = """⚠️ **Clave No Encontrada**

La clave solicitada no existe en el sistema."""
    
    CONFIRM_DELETE = """⚠️ **Confirmar Eliminación**

¿Estás seguro de eliminar esta clave?

🔑 **Nombre:** {key_name}
👤 **Usuario:** {user_name}
🔒 **Tipo:** {key_type}
📊 **Datos usados:** {data_used}

⚠️ **Esta acción:**
- ❌ Eliminará la clave de los servidores VPN
- ❌ Eliminará la clave de la base de datos
- ❌ El usuario perderá acceso inmediatamente
- ❌ No se puede deshacer

**Confirma si deseas continuar:**"""
    
    # Resultados de operaciones
    DELETE_SUCCESS = """✅ **Clave Eliminada Correctamente**

🔑 **ID:** {key_id}
🔒 **Tipo:** {key_type}

📊 **Estado de eliminación:**
🖥️ **Servidores:** {server_deleted}
💾 **Base de datos:** {db_deleted}

La clave ha sido completamente eliminada del sistema."""
    
    DELETE_ERROR = """❌ **Error Eliminando Clave**

🔑 **ID:** {key_id}
❌ **Error:** {error}

Por favor, revisa los logs del sistema para más detalles."""
    
    # Estado de servidores
    SERVER_STATUS_HEADER = """🖥️ **Estado de Servidores VPN**

"""
    
    SERVER_STATUS = """
{health_emoji} **{server_type}**
📊 **Claves totales:** {total_keys}
🟢 **Claves activas:** {active_keys}
🔧 **Versión:** {version}
❌ **Errores:** {error}
"""
    
    # Errores generales
    ERROR = """⚠️ **Error**

❌ **Detalles:** {error}

Por favor, intenta nuevamente o contacta soporte técnico."""
