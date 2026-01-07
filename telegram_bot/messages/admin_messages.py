"""
Mensajes para funcionalidades administrativas del bot uSipipo.

Organiza los mensajes relacionados con:
- Gestión de usuarios
- Gestión de llaves administrativas
- Estadísticas y reportes
- Configuración del sistema

Author: uSipipo Team
Version: 1.0.0
"""


class AdminMessages:
    """Mensajes para administradores del bot."""
    
    # ============================================
    # ADMIN MENU
    # ============================================
    
    class Menu:
        """Mensajes de menú administrativo."""
        
        MAIN = (
            "⚙️ **Panel de Administración**\n"
            "━━━━━━━━━━━━\n\n"
            "🔹 **Gestión:**\n"
            "• 👥 Usuarios\n"
            "• 🔑 Llaves\n"
            "• 📊 Estadísticas\n"
            "• 🎯 Tareas\n\n"
            "🔹 **Sistema:**\n"
            "• ⚙️ Configuración\n"
            "• 📢 Broadcast\n"
            "• 🔄 Sincronización\n"
            "• 📋 Logs\n\n"
            "━━━━━━━━━━━━\n\n"
            "Selecciona una opción:"
        )
        
        USERS_SUBMENU = (
            "👥 **Gestión de Usuarios**\n"
            "━━━━━━━━━━━━\n\n"
            "• 🔍 Buscar usuario\n"
            "• 📋 Listar todos\n"
            "• 🚫 Bloquear/Desbloquear\n"
            "• 🗑️ Eliminar usuario\n"
            "• ⬅️ Volver\n"
        )
        
        USERS_SUBMENU_TITLE = (
            "👥 **Gestión de Usuarios**\n"
            "━━━━━━━━━━━━\n\n"
            "Selecciona una opción:"
        )
        
        KEYS_SUBMENU = (
            "🔑 **Gestión de Llaves**\n"
            "━━━━━━━━━━━━\n\n"
            "• 🔍 Buscar llave\n"
            "• 📋 Listar todas\n"
            "• 🔄 Renovar\n"
            "• 🚫 Desactivar\n"
            "• ⬅️ Volver\n"
        )
        
        STATS_SUBMENU = (
            "📊 **Estadísticas**\n"
            "━━━━━━━━━━━━\n\n"
            "• 👥 Usuarios totales\n"
            "• 🔑 Llaves en uso\n"
            "• 📈 Consumo de datos\n"
            "• 💰 Ingresos\n"
            "• ⬅️ Volver\n"
        )
    
    # ============================================
    # USER MANAGEMENT
    # ============================================
    
    class Users:
        """Mensajes para gestión de usuarios."""
        
        SEARCH_PROMPT = (
            "🔍 **Buscar Usuario**\n\n"
            "Envía el nombre, Telegram ID o username:"
        )
        
        LIST_HEADER = (
            "👥 **Lista de Usuarios**\n"
            "━━━━━━━━━━━━\n"
        )
        
        USERS_LIST_HEADER = (
            "👥 **Lista de Usuarios**\n"
            "━━━━━━━━━━━━\n\n"
            "Total: {total_users} | Página {page}/{total_pages}\n\n"
            "{users}"
        )
        
        NO_USERS = (
            "📭 **Sin usuarios**\n\n"
            "La base de datos está vacía."
        )
        
        USER_ENTRY = (
            "👤 {name} | ID: `{user_id}`\n"
            "   📅 Unido: {join_date} | Estado: {status}"
        )
        
        USER_DETAIL = (
            "👤 **Detalles del Usuario**\n"
            "━━━━━━━━━━━━\n\n"
            "📛 **Nombre:** {name}\n"
            "🆔 **ID:** `{user_id}`\n"
            "📞 **Username:** @{username}\n"
            "📅 **Unido:** {join_date}\n"
            "🟢 **Estado:** {status}\n"
            "🚫 **Bloqueado:** {blocked}\n"
            "🔑 **Llaves:** {keys_count}\n"
            "📊 **Consumo:** {total_usage} GB\n"
            "👑 **VIP:** {is_vip}\n"
            "💰 **Saldo:** ${balance}\n"
            "🎫 **Tickets:** {tickets_count}\n"
        )
        
        BLOCK_USER = (
            "🚫 **Usuario bloqueado**\n\n"
            "Usuario: **{name}**\n"
            "ID: `{user_id}`\n\n"
            "El usuario no podrá usar el bot."
        )
        
        UNBLOCK_USER = (
            "✅ **Usuario desbloqueado**\n\n"
            "Usuario: **{name}**\n"
            "ID: `{user_id}`"
        )
        
        DELETE_USER = (
            "🗑️ **Usuario eliminado**\n\n"
            "Usuario: **{name}**\n"
            "ID: `{user_id}`\n\n"
            "Todos sus datos han sido eliminados."
        )
        
        USER_NOT_FOUND = (
            "❌ **Usuario no encontrado**\n\n"
            "No hay coincidencias con: **{query}**"
        )
    
    # ============================================
    # KEY MANAGEMENT
    # ============================================
    
    class Keys:
        """Mensajes para gestión de llaves."""
        
        LIST_HEADER = (
            "🔑 **Lista de Llaves**\n"
            "━━━━━━━━━━━━\n"
        )
        
        NO_KEYS = (
            "📭 **Sin llaves**\n\n"
            "No hay llaves registradas."
        )
        
        LIST = (
            "🔑 **Lista de Llaves**\n"
            "━━━━━━━━━━━━\n\n"
            "🔐 **WireGuard:** {wireguard_count}\n"
            "🌐 **Outline:** {outline_count}\n\n"
            "Total: {total_keys} llaves"
        )
        
        KEY_ENTRY = (
            "🔑 {name} ({protocol}) | Usuario: {owner}\n"
            "   📊 {usage}/{limit} GB | Expira: {expiration}"
        )
        
        KEY_DETAIL = (
            "🔑 **Detalles de Llave**\n"
            "━━━━━━━━━━━━\n\n"
            "📛 **Nombre:** {name}\n"
            "👤 **Propietario:** {owner}\n"
            "🆔 **ID:** `{key_id}`\n"
            "📡 **Protocolo:** {protocol}\n"
            "🖥️ **Servidor:** {server}\n"
            "📊 **Consumo:** {usage} / {limit} GB\n"
            "⏰ **Expiración:** {expiration}\n"
            "🟢 **Estado:** {status}\n"
            "📅 **Creada:** {created_date}\n"
            "🔄 **Última sincronización:** {last_sync}\n"
        )
        
        RENEW_KEY = (
            "🔄 **Llave renovada**\n\n"
            "Nombre: **{name}**\n"
            "Nueva expiración: **{expiration}**\n"
            "Nuevos datos: **{limit} GB**"
        )
        
        DEACTIVATE_KEY = (
            "🚫 **Llave desactivada**\n\n"
            "Nombre: **{name}**\n"
            "Usuario: **{owner}**\n\n"
            "La conexión ha sido interrumpida."
        )
        
        NO_KEYS = (
            "📭 **Sin llaves**\n\n"
            "No hay llaves en el sistema."
        )
        
        KEYS_NOT_FOUND = (
            "❌ **Llaves no encontradas**\n\n"
            "No hay coincidencias con: **{query}**"
        )
    
    # ============================================
    # STATISTICS & REPORTING
    # ============================================
    
    class Statistics:
        """Mensajes de estadísticas."""
        
        GENERAL = (
            "📊 **Estadísticas Generales**\n"
            "━━━━━━━━━━━━\n\n"
            "👥 **Usuarios:**\n"
            "   • Totales: {total_users}\n"
            "   • Activos (hoy): {active_today}\n"
            "   • Nuevos (hoy): {new_today}\n"
            "   • VIP: {vip_users}\n\n"
            "🔑 **Llaves:**\n"
            "   • Totales: {total_keys}\n"
            "   • Activas: {active_keys}\n"
            "   • WireGuard: {wireguard_count}\n"
            "   • Outline: {outline_count}\n\n"
            "📈 **Tráfico:**\n"
            "   • Consumo total: {total_traffic} GB\n"
            "   • Promedio por usuario: {avg_per_user} GB\n"
            "   • Hoy: {traffic_today} GB\n\n"
            "💰 **Ingresos:**\n"
            "   • Total: ${total_revenue}\n"
            "   • VIP: ${vip_revenue}\n"
            "   • Hoy: ${revenue_today}\n"
        )
        
        USER_STATS = (
            "👥 **Estadísticas de Usuarios**\n"
            "━━━━━━━━━━━━\n\n"
            "🔹 **Resumen:**\n"
            "   Totales: {total}\n"
            "   Activos: {active}\n"
            "   Inactivos: {inactive}\n"
            "   Bloqueados: {blocked}\n\n"
            "📈 **Tendencias (últimos 7 días):**\n"
            "{growth_chart}\n\n"
            "🏆 **Top usuarios por consumo:**\n"
            "{top_users}"
        )
        
        KEY_STATS = (
            "🔑 **Estadísticas de Llaves**\n"
            "━━━━━━━━━━━━\n\n"
            "📊 **Distribución:**\n"
            "   WireGuard: {wireguard_pct}% ({wireguard_count})\n"
            "   Outline: {outline_pct}% ({outline_count})\n\n"
            "⏰ **Estado:**\n"
            "   Activas: {active_count}\n"
            "   Próximas a expirar: {expiring_soon}\n"
            "   Expiradas: {expired_count}\n\n"
            "📈 **Utilización:**\n"
            "{utilization_chart}"
        )
        
        TRAFFIC_STATS = (
            "📈 **Consumo de Datos**\n"
            "━━━━━━━━━━━━\n\n"
            "📊 **Total:**\n"
            "   {total_traffic} GB consumidos\n"
            "   {total_limit} GB limite asignado\n\n"
            "📉 **Últimos 7 días:**\n"
            "{traffic_chart}\n\n"
            "🏆 **Top 5 consumidores:**\n"
            "{top_consumers}"
        )
    
    # ============================================
    # BROADCAST & ANNOUNCEMENTS
    # ============================================
    
    class Broadcast:
        """Mensajes para broadcasts."""
        
        CONFIRM = (
            "📢 **Confirmar Broadcast**\n"
            "━━━━━━━━━━━━\n\n"
            "Destinatarios: {recipients}\n"
            "Tipo: {message_type}\n\n"
            "Vista previa:\n\n"
            "{preview}\n\n"
            "━━━━━━━━━━━━\n\n"
            "¿Enviar a {recipients} usuarios?"
        )
        
        SENDING = (
            "📤 **Enviando broadcast...**\n\n"
            "Enviados: {sent}/{total}"
        )
        
        COMPLETED = (
            "✅ **Broadcast completado**\n\n"
            "Enviados: {sent}/{total}\n"
            "Fallidos: {failed}\n"
            "Bloqueados: {blocked}\n"
        )
        
        FAILED = (
            "❌ **Error en broadcast**\n\n"
            "Mensaje: {error}\n"
            "Intentos fallidos: {failed_count}"
        )
    
    # ============================================
    # CONFIRMATIONS
    # ============================================
    
    class Confirmation:
        """Mensajes de confirmación."""
        
        DELETE_KEY = (
            "⚠️ **¿Eliminar Llave?**\n\n"
            "🔑 **Llave:** {key_name}\n"
            "👤 **Usuario:** {user_name}\n"
            "📡 **Tipo:** {key_type}\n"
            "📊 **Datos usados:** {data_used}\n\n"
            "Esta acción es **irreversible**."
        )
        
        DELETE_SUCCESS = (
            "✅ **Llave Eliminada**\n\n"
            "🔑 **ID:** {key_id}\n"
            "📡 **Tipo:** {key_type}\n"
            "🗄️ **BD:** {db_deleted}\n"
            "🖥️ **Servidor:** {server_deleted}\n\n"
            "Llave eliminada exitosamente."
        )
        
        DELETE_ERROR = (
            "❌ **Error al Eliminar**\n\n"
            "🔑 **ID:** {key_id}\n"
            "❌ **Error:** {message}\n\n"
            "No se pudo eliminar la llave."
        )
        
        BLOCK_USER_CONFIRM = (
            "⚠️ **¿Bloquear Usuario?**\n\n"
            "👤 **Usuario:** {user_name} (ID: {user_id})\n"
            "📊 **Estado actual:** {current_status}\n\n"
            "El usuario no podrá acceder al bot."
        )
        
        UNBLOCK_USER_CONFIRM = (
            "⚠️ **¿Desbloquear Usuario?**\n\n"
            "👤 **Usuario:** {user_name} (ID: {user_id})\n"
            "📊 **Estado actual:** {current_status}\n\n"
            "El usuario podrá acceder nuevamente."
        )
        
        BLOCK_USER_SUCCESS = (
            "✅ **Usuario Bloqueado**\n\n"
            "👤 **Usuario:** {user_name}\n"
            "🆔 **ID:** {user_id}\n\n"
            "El usuario ha sido bloqueado."
        )
        
        UNBLOCK_USER_SUCCESS = (
            "✅ **Usuario Desbloqueado**\n\n"
            "👤 **Usuario:** {user_name}\n"
            "🆔 **ID:** {user_id}\n\n"
            "El usuario ha sido desbloqueado."
        )
        
        DELETE_USER_CONFIRM = (
            "⚠️ **¿Eliminar Usuario?**\n\n"
            "👤 **Usuario:** {user_name} (ID: {user_id})\n"
            "📊 **Estado actual:** {current_status}\n\n"
            "⚠️ **Esta acción es irreversible**\n"
            "Se eliminarán todos los datos del usuario."
        )
        
        ASSIGN_ROLE_MENU = (
            "👑 **Asignar Rol**\n\n"
            "👤 **Usuario:** {user_name}\n"
            "🆔 **ID:** {user_id}\n\n"
            "Selecciona el rol a asignar:"
        )
        
        USER_ACTION_SUCCESS = (
            "✅ **Acción Completada**\n\n"
            "👤 **Usuario:** {user_name}\n"
            "🆔 **ID:** {user_id}\n"
            "✅ **Operación:** {operation}\n\n"
            "Acción realizada exitosamente."
        )
        
        USER_ACTION_ERROR = (
            "❌ **Error en Acción**\n\n"
            "👤 **Usuario:** {user_id}\n"
            "❌ **Operación:** {operation}\n"
            "📝 **Error:** {message}\n\n"
            "No se pudo completar la acción."
        )
    
    # ============================================
    # SYSTEM & CONFIGURATION
    # ============================================
    
    class System:
        """Mensajes de sistema."""
        
        CONFIG_MENU = (
            "⚙️ **Configuración del Sistema**\n"
            "━━━━━━━━━━━━\n\n"
            "• 🔑 Límites de llaves\n"
            "• 📊 Límites de datos\n"
            "• 💰 Precios VIP\n"
            "• 🎁 Bonificaciones\n"
            "• ⬅️ Volver\n"
        )
        
        SETTINGS = (
            "⚙️ **Configuración Actual**\n"
            "━━━━━━━━━━━━\n\n"
            "🔑 **Llaves por usuario:** {keys_limit}\n"
            "📊 **Datos por llave:** {data_limit} GB\n"
            "💰 **Precio VIP (mes):** ${vip_price}\n"
            "💰 **Precio VIP (año):** ${vip_yearly_price}\n"
            "🎁 **Datos iniciales:** {initial_data} GB\n"
            "⏰ **Ciclo de renovación:** {renewal_cycle} días\n"
        )
        
        SYNC_RUNNING = (
            "🔄 **Sincronización en progreso...**\n\n"
            "Esto puede tomar unos minutos."
        )
        
        SYNC_COMPLETED = (
            "✅ **Sincronización completada**\n\n"
            "Llaves actualizadas: {updated}\n"
            "Cambios detectados: {changes}\n"
            "Duración: {duration}s"
        )
        
        SERVER_STATUS_HEADER = (
            "🖥️ **Estado de Servidores**\n"
            "━━━━━━━━━━━━\n\n"
        )
        
        SERVER_STATUS = (
            "📊 **{server_type}**\n"
            "━━━━━━━━━━━━\n"
            "🟢 **Estado:** {health_emoji}\n"
            "🔑 **Total llaves:** {total_keys}\n"
            "✅ **Activas:** {active_keys}\n"
            "📊 **Uso:** {usage}%\n"
            "📦 **Versión:** {version}\n"
            "❌ **Errores:** {error}\n\n"
        )
    
   
    # ============================================
    # ROLE MANAGEMENT
    # ============================================
    
    class Roles:
        """Mensajes para gestión de roles."""
        
        ROLE_SELECTION = (
            "👑 **Seleccionar Rol**\n\n"
            "Elige el rol a asignar:"
        )
        
        PREMIUM_ROLE_DURATION = (
            "⏱️ **Duración del Rol Premium**\n\n"
            "Selecciona la duración:"
        )
    
    # ============================================
    # ERRORS & WARNINGS
    # ============================================
    
    class Errors:
        """Mensajes de error administrativos."""
        
        UNAUTHORIZED = (
            "❌ **No autorizado**\n\n"
            "No tienes permisos para esta acción."
        )
        
        GENERIC = (
            "❌ **Error**\n\n"
            "No se pudo completar la operación: {error}"
        )
        
        USER_NOT_FOUND = (
            "❌ **Usuario no encontrado**\n\n"
            "No hay registros de: **{query}**"
        )
        
        KEY_NOT_FOUND = (
            "❌ **Llave no encontrada**\n\n"
            "No hay registros de: **{query}**"
        )
        
        OPERATION_FAILED = (
            "❌ **Error en operación**\n\n"
            "No se pudo completar: {reason}"
        )
        
        DATABASE_ERROR = (
            "🔴 **Error de base de datos**\n\n"
            "Intenta más tarde."
        )
        
        API_ERROR = (
            "🔌 **Error de servidor**\n\n"
            "No se pudo conectar: {error}"
        )
