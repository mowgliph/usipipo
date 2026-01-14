"""
Mensajes para gestión de usuarios de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""


class UserManagementMessages:
    """Mensajes para gestión de usuarios."""
    
    # ============================================
    # WELCOME & ONBOARDING
    # ============================================
    
    class Welcome:
        """Mensajes de bienvenida y onboarding."""
        
        NEW_USER = (
            "🎉 ¡Bienvenido, **{name}**!\n\n"
            "Tu cuenta ha sido creada exitosamente.\n\n"
            "🎁 **Regalo de bienvenida:**\n"
            "• 2 llaves VPN gratuitas\n"
            "• 10 GB de datos por llave\n\n"
            "📱 Toca **➕ Crear Nueva** para generar tu primera conexión."
        )
        
        RETURNING_USER = (
            "👋 ¡Hola de nuevo, **{name}**!\n\n"
            "Todo listo para continuar.\n\n"
            "📊 Usa el menú para gestionar tus accesos."
        )
    
    # ============================================
    # STATUS
    # ============================================
    
    class Status:
        """Mensajes de estado del usuario."""
        
        HEADER = "📊 **Estado de tu Cuenta**"
        
        USER_INFO = (
            "👤 **Usuario:** {name}\n"
            "🆔 **ID:** {user_id}\n"
            "📅 **Fecha de registro:** {join_date}\n"
            "🟢 **Estado:** {status}"
        )
        
        ADMIN_DASHBOARD = (
            "🔧 **Panel Administrativo**\n\n"
            "👋 **Admin:** {name}\n\n"
            "📊 **Estadísticas Generales:**\n"
            "👥 **Usuarios totales:** {total_users}\n"
            "✅ **Usuarios activos:** {active_users}\n"
            "🔑 **Llaves totales:** {total_keys}\n"
            "🟢 **Llaves activas:** {active_keys}\n"
            "📈 **Carga del servidor:** {server_load}"
        )
    
    # ============================================
    # INFO
    # ============================================
    
    class Info:
        """Mensajes de información del usuario."""
        
        HEADER = "ℹ️ **Información de tu Cuenta**"
        
        USER_INFO = (
            "ℹ️ **Información Detallada**\n\n"
            "👤 **Usuario:** {name}\n"
            "🆔 **ID:** {user_id}\n"
            "👥 **Username:** @{username}\n"
            "📅 **Registro:** {join_date}\n"
            "🟢 **Estado:** {status}\n"
            "👑 **Plan:** {plan}\n"
            "🔑 **Llaves:** {keys_used}/{keys_total}\n"
            "📊 **Datos usados:** {data_used}\n"
            "💰 **Balance:** {balance} estrellas\n"
            "🎮 **Nivel:** {level}\n"
            "🏆 **Logros:** {achievements}"
        )
    
    # ============================================
    # ERRORS
    # ============================================
    
    class Error:
        """Mensajes de error."""
        
        REGISTRATION_FAILED = (
            "❌ **Error en el registro**\n\n"
            "No pude crear tu cuenta. Por favor, intenta más tarde.\n"
            "Si el problema persiste, contacta soporte."
        )
        
        STATUS_FAILED = (
            "❌ **Error obteniendo estado**\n\n"
            "No pude cargar tu información. Intenta más tarde."
        )
        
        INFO_FAILED = (
            "❌ **Error obteniendo información**\n\n"
            "No pude cargar tu información detallada. Intenta más tarde."
        )
