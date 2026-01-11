"""
Mensajes para sistema de difusión masiva de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""


class BroadcastMessages:
    """Mensajes para sistema de difusión masiva."""
    
    # ============================================
    # MENU
    # ============================================
    
    class Menu:
        """Mensajes del menú de broadcast."""
        
        MAIN = (
            "📢 **Centro de Difusión Masiva**\n\n"
            "Sistema de comunicación masiva para administradores.\n\n"
            "📋 **Funciones Disponibles:**\n"
            "📝 **Crear Broadcast** - Enviar mensajes masivos\n"
            "📊 **Historial** - Ver envíos anteriores\n"
            "📈 **Estadísticas** - Análisis de rendimiento\n"
            "📋 **Plantillas** - Mensajes predefinidos\n\n"
            "💡 *Comunica eficientemente con todos los usuarios*"
        )
    
    # ============================================
    # TYPE
    # ============================================
    
    class Type:
        """Mensajes de tipos de broadcast."""
        
        SELECTION = (
            "📝 **Seleccionar Tipo de Broadcast**\n\n"
            "Elige el tipo de mensaje que deseas enviar:\n\n"
            "📢 **General** - Comunicación general\n"
            "⚠️ **Urgente** - Alertas importantes\n"
            "🎉 **Promocional** - Ofertas especiales\n"
            "📚 **Informativo** - Actualizaciones y noticias\n"
            "🔧 **Mantenimiento** - Avisos técnicos\n\n"
            "💡 *Cada tipo tiene diferentes prioridades y alcance*"
        )
        
        DESCRIPTIONS = (
            "📋 **Descripción de Tipos:**\n\n"
            "📢 **General:**\n"
            "• Comunicaciones estándar\n"
            "• Alcance: Todos los usuarios activos\n"
            "• Prioridad: Normal\n\n"
            "⚠️ **Urgente:**\n"
            "• Alertas críticas y emergencias\n"
            "• Alcance: Todos los usuarios\n"
            "• Prioridad: Alta\n\n"
            "🎉 **Promocional:**\n"
            "• Ofertas y promociones\n"
            "• Alcance: Usuarios VIP y activos\n"
            "• Prioridad: Media\n\n"
            "📚 **Informativo:**\n"
            "• Actualizaciones y noticias\n"
            "• Alcance: Usuarios suscritos\n"
            "• Prioridad: Normal\n\n"
            "🔧 **Mantenimiento:**\n"
            "• Avisos técnicos y mantenimiento\n"
            "• Alcance: Todos los usuarios afectados\n"
            "• Prioridad: Alta"
        )
    
    # ============================================
    # COMPOSE
    # ============================================
    
    class Compose:
        """Mensajes de composición."""
        
        TEMPLATE = (
            "✍️ **Componer Mensaje**\n\n"
            "Tipo: **{type}**\n\n"
            "Escribe tu mensaje usando el siguiente formato:\n\n"
            "**Título:** [Tu título aquí]\n"
            "**Mensaje:** [Tu contenido aquí]\n"
            "**Acción:** [Opcional - texto del botón]\n\n"
            "💡 *Usa Markdown para formato: **negrita**, *cursiva*, `código`*\n\n"
            "📝 **Ejemplo:**\n"
            "**Título:** 🎉 Nueva Actualización\n"
            "**Mensaje:** Estamos emocionados de compartir nuestra nueva función...\n"
            "**Acción:** Ver Novedades"
        )
        
        PREVIEW = (
            "👁️ **Vista Previa del Mensaje**\n\n"
            "**Título:** {title}\n"
            "**Mensaje:** {message}\n"
            "**Acción:** {action}\n\n"
            "📊 **Estadísticas Estimadas:**\n"
            "• Usuarios potenciales: {estimated_reach}\n"
            "• Tasa de apertura esperada: {expected_open_rate}%\n"
            "• Costo estimado: ${estimated_cost}\n\n"
            "💡 *Revisa el mensaje antes de enviar*"
        )
        
        VALIDATION = (
            "⚠️ **Validación de Mensaje**\n\n"
            "Tu mensaje necesita ajustes:\n\n"
            "{validation_errors}\n\n"
            "💡 *Por favor, corrige los errores indicados*"
        )
    
    # ============================================
    # AUDIENCE
    # ============================================
    
    class Audience:
        """Mensajes de audiencia."""
        
        SELECTION = (
            "👥 **Seleccionar Audiencia**\n\n"
            "Elige a quién enviarás el mensaje:\n\n"
            "🌍 **Todos los Usuarios** - Máximo alcance\n"
            "🟢 **Usuarios Activos** - Últimos 30 días\n"
            "👑 **Usuarios VIP** - Miembros premium\n"
            "🔔 **Usuarios Suscritos** - Con notificaciones\n"
            "📊 **Por Segmento** - Personalizado\n\n"
            "💡 *La audiencia afecta el alcance y efectividad*"
        )
        
        STATISTICS = (
            "📊 **Estadísticas de Audiencia**\n\n"
            "👥 **Total de Usuarios:** {total_users}\n"
            "🟢 **Usuarios Activos:** {active_users}\n"
            "👑 **Usuarios VIP:** {vip_users}\n"
            "🔔 **Usuarios Suscritos:** {subscribed_users}\n"
            "📈 **Alcance Estimado:** {estimated_reach}\n\n"
            "💡 *Estos datos se actualizan en tiempo real*"
        )
        
        SEGMENT_OPTIONS = (
            "🎯 **Segmentación Avanzada**\n\n"
            "Filtra usuarios por:\n\n"
            "📅 **Fecha de Registro:**\n"
            "• Últimos 7 días\n"
            "• Últimos 30 días\n"
            "• Últimos 90 días\n\n"
            "💰 **Nivel de VIP:**\n"
            "• Usuarios gratuitos\n"
            "• VIP Básico\n"
            "• VIP Premium\n"
            "• VIP Elite\n\n"
            "🎮 **Actividad:**\n"
            "• Usuarios inactivos\n"
            "• Usuarios moderadamente activos\n"
            "• Usuarios muy activos\n\n"
            "💡 *Combinar filtros para mayor precisión*"
        )
    
    # ============================================
    # CONFIRMATION
    # ============================================
    
    class Confirmation:
        """Mensajes de confirmación."""
        
        SEND_CONFIRMATION = (
            "🔍 **Confirmar Envío de Broadcast**\n\n"
            "📋 **Detalles del Envío:**\n"
            "📝 **Tipo:** {type}\n"
            "👥 **Audiencia:** {audience}\n"
            "📊 **Usuarios Potenciales:** {audience_size}\n"
            "🟢 **Usuarios Activos:** {active_users}\n"
            "📈 **Alcance Estimado:** {estimated_reach}\n\n"
            "📄 **Vista Previa:**\n"
            "{message_preview}\n\n"
            "⚠️ **Esta acción enviará el mensaje a {estimated_reach} usuarios.**\n\n"
            "💡 *Verifica todos los detalles antes de confirmar*"
        )
        
        SCHEDULE_CONFIRMATION = (
            "⏰ **Programar Envío**\n\n"
            "Configura cuándo enviar tu broadcast:\n\n"
            "📅 **Fecha:** {date}\n"
            "⏰ **Hora:** {time}\n"
            "🌍 **Zona Horaria:** UTC\n\n"
            "📊 **Detalles del Envío:**\n"
            "• Tipo: {type}\n"
            "• Audiencia: {audience}\n"
            "• Alcance: {estimated_reach} usuarios\n\n"
            "💡 *El mensaje se enviará automáticamente*"
        )
    
    # ============================================
    # SUCCESS
    # ============================================
    
    class Success:
        """Mensajes de éxito."""
        
        SENT_SUCCESS = (
            "✅ **Broadcast Enviado Exitosamente**\n\n"
            "📋 **Detalles del Envío:**\n"
            "📝 **Tipo:** {type}\n"
            "👥 **Audiencia:** {audience}\n"
            "📊 **Enviados:** {sent_count}\n"
            "❌ **Fallidos:** {failed_count}\n"
            "🆔 **ID del Mensaje:** {message_id}\n\n"
            "📈 **Estadísticas Iniciales:**\n"
            "• Tasa de entrega: {delivery_rate}%\n"
            "• Tiempo de envío: {send_time}s\n\n"
            "💡 *Las estadísticas se actualizarán en tiempo real*"
        )
        
        SCHEDULED_SUCCESS = (
            "⏰ **Broadcast Programado**\n\n"
            "Tu mensaje ha sido programado exitosamente.\n\n"
            "📅 **Fecha de Envío:** {scheduled_date}\n"
            "⏰ **Hora de Envío:** {scheduled_time}\n"
            "🆔 **ID del Mensaje:** {message_id}\n\n"
            "📊 **Detalles:**\n"
            "• Tipo: {type}\n"
            "• Audiencia: {audience}\n"
            "• Alcance estimado: {estimated_reach}\n\n"
            "💡 *Recibirás una notificación cuando se envíe*"
        )
        
        DRAFT_SAVED = (
            "💾 **Borrador Guardado**\n\n"
            "Tu mensaje ha sido guardado como borrador.\n\n"
            "📝 **Título:** {title}\n"
            "📅 **Fecha de Guardado:** {save_date}\n"
            "🆔 **ID del Borrador:** {draft_id}\n\n"
            "💡 *Puedes continuar editando o enviar más tarde*"
        )
    
    # ============================================
    # HISTORY
    # ============================================
    
    class History:
        """Mensajes de historial."""
        
        NO_HISTORY = (
            "📭 **Sin Historial de Broadcasts**\n\n"
            "Aún no has enviado ningún broadcast.\n\n"
            "💡 *Tu primer broadcast aparecerá aquí*"
        )
        
        HEADER = (
            "📋 **Historial de Broadcasts**\n\n"
            "Tus envíos más recientes:\n"
        )
        
        DETAILS = (
            "📋 **Detalles del Broadcast**\n\n"
            "🆔 **ID:** {broadcast_id}\n"
            "📝 **Tipo:** {type}\n"
            "👥 **Audiencia:** {audience}\n"
            "📅 **Fecha de Envío:** {sent_date}\n"
            "📊 **Estadísticas:**\n"
            "• Enviados: {sent_count}\n"
            "• Abiertos: {open_count}\n"
            "• Clics: {click_count}\n"
            "• Tasa de apertura: {open_rate}%\n"
            "• Tasa de clics: {click_rate}%\n\n"
            "📄 **Mensaje:**\n"
            "{message_content}\n\n"
            "💡 *Este broadcast está {status}*"
        )
    
    # ============================================
    # STATS
    # ============================================
    
    class Stats:
        """Mensajes de estadísticas."""
        
        GENERAL_STATS = (
            "📊 **Estadísticas Generales de Broadcasts**\n\n"
            "📈 **Rendimiento Global:**\n"
            "• Total de Broadcasts: {total_broadcasts}\n"
            "• Total Enviados: {total_sent}\n"
            "• Total Fallidos: {total_failed}\n"
            "• Tasa de Éxito: {success_rate}%\n"
            "• Alcance Total: {total_reach}\n"
            "• Engagement Promedio: {avg_engagement}%\n\n"
            "📅 **Últimos 30 días:**\n"
            "• Broadcasts enviados: {monthly_broadcasts}\n"
            "• Usuarios alcanzados: {monthly_reach}\n"
            "• Tasa de apertura: {monthly_open_rate}%\n\n"
            "💡 *Las estadísticas se actualizan cada hora*"
        )
        
        PERFORMANCE = (
            "📈 **Análisis de Rendimiento**\n\n"
            "📊 **Métricas Clave:**\n"
            "• **Tasa de Apertura:** {open_rate}%\n"
            "• **Tasa de Clics:** {click_rate}%\n"
            "• **Tiempo Promedio de Lectura:** {avg_read_time}s\n"
            "• **Engagement:** {engagement_rate}%\n\n"
            "🎯 **Mejores Horarios:**\n"
            "• {best_hour_1}: {best_rate_1}% apertura\n"
            "• {best_hour_2}: {best_rate_2}% apertura\n"
            "• {best_hour_3}: {best_rate_3}% apertura\n\n"
            "📱 **Dispositivos:**\n"
            "• Móvil: {mobile_rate}%\n"
            "• Desktop: {desktop_rate}%\n"
            "• Tablet: {tablet_rate}%\n\n"
            "💡 *Usa estos datos para optimizar futuros broadcasts*"
        )
    
    # ============================================
    # TEMPLATES
    # ============================================
    
    class Templates:
        """Mensajes de plantillas."""
        
        NO_TEMPLATES = (
            "📭 **Sin Plantillas Disponibles**\n\n"
            "No hay plantillas guardadas.\n\n"
            "💡 *Crea tu primera plantilla para reutilizarla*"
        )
        
        LIST_HEADER = (
            "📋 **Plantillas de Broadcast**\n\n"
            "Plantillas disponibles para usar:\n"
        )
        
        PREVIEW = (
            "👁️ **Vista Previa de Plantilla**\n\n"
            "📋 **Nombre:** {template_name}\n"
            "📝 **Descripción:** {description}\n"
            "🎯 **Tipo:** {type}\n"
            "💰 **Costo Sugerido:** ${suggested_budget}\n\n"
            "📄 **Contenido:**\n"
            "{template_content}\n\n"
            "💡 *Usa esta plantilla como base para tu broadcast*"
        )
        
        CREATE_SUCCESS = (
            "✅ **Plantilla Creada**\n\n"
            "Tu plantilla ha sido guardada exitosamente.\n\n"
            "📋 **Nombre:** {template_name}\n"
            "🆔 **ID:** {template_id}\n"
            "📅 **Fecha de Creación:** {creation_date}\n\n"
            "💡 *Puedes usar esta plantilla en futuros broadcasts*"
        )
    
    # ============================================
    # ERRORS
    # ============================================
    
    class Error:
        """Mensajes de error."""
        
        SYSTEM_ERROR = (
            "❌ **Error del Sistema**\n\n"
            "No pude procesar tu solicitud de broadcast.\n\n"
            "Por favor, intenta más tarde o contacta soporte."
        )
        
        ADMIN_ONLY = (
            "🔒 **Acceso Restringido**\n\n"
            "Esta función está disponible solo para administradores.\n\n"
            "💡 *Contacta al administrador principal si necesitas acceso*"
        )
        
        SEND_FAILED = (
            "❌ **Error al Enviar Broadcast**\n\n"
            "No pude enviar el broadcast.\n\n"
            "Error: {error}\n\n"
            "💡 *Por favor, verifica los detalles e intenta nuevamente*"
        )
        
        INVALID_AUDIENCE = (
            "⚠️ **Audiencia Inválida**\n\n"
            "La audiencia seleccionada no es válida.\n\n"
            "💡 *Por favor, selecciona una audiencia válida*"
        )
        
        MESSAGE_TOO_LONG = (
            "⚠️ **Mensaje Demasiado Largo**\n\n"
            "Tu mensaje excede el límite de caracteres.\n\n"
            "Límite: {max_length} caracteres\n"
            "Actual: {current_length} caracteres\n\n"
            "💡 *Por favor, acorta tu mensaje*"
        )
    
    # ============================================
    # SCHEDULING
    # ============================================
    
    class Scheduling:
        """Mensajes de programación."""
        
        MENU = (
            "⏰ **Programar Broadcast**\n\n"
            "Configura cuándo enviar tu mensaje:\n\n"
            "📅 **Opciones de Tiempo:**\n"
            "• Enviar ahora\n"
            "• Programar para más tarde\n"
            "• Programar para fecha específica\n"
            "• Enviar recurrentemente\n\n"
            "💡 *La programación te permite llegar en el momento óptimo*"
        )
        
        DATE_SELECTION = (
            "📅 **Seleccionar Fecha**\n\n"
            "Elige la fecha para enviar tu broadcast:\n\n"
            "📆 **Calendario Disponible:**\n"
            "• Hoy\n"
            "• Mañana\n"
            "• Esta semana\n"
            "• Próxima semana\n"
            "• Fecha personalizada\n\n"
            "⏰ **Zona Horaria:** UTC\n\n"
            "💡 *Selecciona la fecha óptima para tu audiencia*"
        )
        
        TIME_SELECTION = (
            "⏰ **Seleccionar Hora**\n\n"
            "Elige la hora para enviar tu broadcast:\n\n"
            "🕐 **Horarios Recomendados:**\n"
            "• 09:00 - Mañana (alta actividad)\n"
            "• 12:00 - Mediodía (pausa laboral)\n"
            "• 18:00 - Tarde (fin de jornada)\n"
            "• 21:00 - Noche (tiempo libre)\n\n"
            "💡 *Considera la zona horaria de tu audiencia*"
        )
        
        RECURRING_OPTIONS = (
            "🔄 **Configurar Recurrencia**\n\n"
            "Elige la frecuencia de envío:\n\n"
            "📅 **Opciones:**\n"
            "• Una vez - Envío único\n"
            "• Diario - Todos los días\n"
            "• Semanal - Cada semana\n"
            "• Mensual - Cada mes\n"
            "• Personalizado - Configurar intervalo\n\n"
            "💡 *Los broadcasts recurrentes son ideales para actualizaciones regulares*"
        )
