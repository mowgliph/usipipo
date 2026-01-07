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
    
    # SUBMENU USUARIOS
    # ================
    USERS_SUBMENU_TITLE = """👥 **Gestión de Usuarios**

Selecciona una opción:"""
    
    # Lista de usuarios
    USERS_LIST_HEADER = """📊 **Lista de Usuarios**

Total: {total_users} | Página {page}/{total_pages}

{users}"""
    
    USER_ENTRY = """• **{name}** (ID: `{user_id}`)
  Estado: {status} | Rol: {role} | VIP: {vip}
  Claves: {keys} | Balance: ⭐{balance} | Registrado: {created_at}"""
    
    NO_USERS = """📊 **Usuarios Registrados**

No hay usuarios registrados en el sistema."""
    
    # Detalle de usuario
    USER_DETAIL = """👤 **Información del Usuario**

**DATOS PERSONALES**
👤 **ID Telegram:** `{user_id}`
🔤 **Nombre:** {full_name}
🔍 **Usuario:** {username}

**ESTADO Y ACCESO**
📌 **Estado:** {status}
🎖️ **Rol:** {role}
👑 **VIP:** {vip_status}

**CLAVES VPN**
🔑 **Total:** {total_keys}
🟢 **Activas:** {active_keys}

**BALANCE Y TRANSACCIONES**
⭐ **Estrellas:** {balance_stars}
💰 **Total Depositado:** {total_deposited}

**ROLES ESPECIALES**
📋 **Gestor de Tareas:** {task_manager}
📣 **Anunciante:** {announcer}

**FECHAS IMPORTANTES**
📅 **Registrado:** {created_at}
📆 **VIP Expira:** {vip_expires}"""
    
    # Acciones de usuario
    USER_ACTION_SUCCESS = """✅ **Acción Completada**

**Operación:** {operation}
**Usuario:** {user_name} (ID: `{user_id}`)
**Detalle:** {message}"""
    
    USER_ACTION_ERROR = """❌ **Error en la Operación**

**Operación:** {operation}
**Usuario:** {user_id}
**Error:** {message}"""
    
    # Cambio de rol
    ASSIGN_ROLE_MENU = """🎖️ **Asignar Rol a Usuario**

👤 **Usuario:** {user_name} (ID: `{user_id}`)

Selecciona el nuevo rol:"""
    
    ROLE_DESCRIPTIONS = {
        'user': '👤 **Usuario Regular** - Rol básico',
        'admin': '🔑 **Administrador** - Control total del sistema',
        'task_manager': '📋 **Gestor de Tareas** - Crear y gestionar tareas (Rol Premium)',
        'announcer': '📣 **Anunciante** - Enviar anuncios a otros usuarios (Rol Premium)'
    }
    
    # Bloqueo de usuarios
    BLOCK_USER_CONFIRM = """⚠️ **Confirmar Bloqueo**

¿Deseas bloquear al usuario `{user_id}` - **{user_name}**?

**Consecuencias:**
❌ No podrá acceder al bot
❌ Sus claves serán inactivas
❌ Perderá acceso a sus servicios"""
    
    BLOCK_USER_SUCCESS = """✅ **Usuario Bloqueado**

✅ Usuario `{user_id}` - **{user_name}** ha sido bloqueado
📌 Estado: BLOQUEADO"""
    
    # Desbloqueo de usuarios
    UNBLOCK_USER_CONFIRM = """⚠️ **Confirmar Desbloqueo**

¿Deseas desbloquear al usuario `{user_id}` - **{user_name}**?"""
    
    UNBLOCK_USER_SUCCESS = """✅ **Usuario Desbloqueado**

✅ Usuario `{user_id}` - **{user_name}** ha sido desbloqueado
📌 Estado: ACTIVO"""
    
    # Eliminación de usuario
    DELETE_USER_CONFIRM = """⚠️⚠️ **ADVERTENCIA: ELIMINAR USUARIO** ⚠️⚠️

¿ESTÁS SEGURO de que deseas eliminar al usuario?

👤 **Usuario:** {user_name} (ID: `{user_id}`)
📊 **Claves:** {total_keys}
⭐ **Balance:** {balance_stars}

**⚠️ ESTA ACCIÓN ES IRREVERSIBLE:**
❌ Se eliminarán TODAS las claves VPN del usuario
❌ Se perderán todos los datos asociados
❌ Se cancelarán suscripciones activas
❌ No se puede deshacer

**Escribe el ID del usuario para confirmar: `{user_id}`**"""
    
    DELETE_USER_SUCCESS = """✅ **Usuario Eliminado**

✅ Usuario `{user_id}` - **{user_name}** ha sido completamente eliminado
📊 Claves eliminadas: {deleted_keys}"""
    
    # Cambio de estado
    CHANGE_STATUS_MENU = """📌 **Cambiar Estado del Usuario**

👤 **Usuario:** {user_name} (ID: `{user_id}`)
Estado actual: {current_status}

Selecciona el nuevo estado:"""
    
    STATUS_OPTIONS = {
        'active': '🟢 **Activo** - Usuario con acceso completo',
        'suspended': '🟡 **Suspendido** - Usuario sin acceso temporal',
        'blocked': '🔴 **Bloqueado** - Usuario sin acceso (manual)',
        'free_trial': '📋 **Prueba Gratis** - Usuario en período de prueba'
    }
    
    # Usuarios
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
