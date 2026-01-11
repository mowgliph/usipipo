"""
Mensajes para sistema de anuncios de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""


class AnnouncerMessages:
    """Mensajes para sistema de anuncios."""
    
    # ============================================
    # MENU
    # ============================================
    
    class Menu:
        """Mensajes del menú de anuncios."""
        
        MAIN = (
            "📢 **Centro de Anuncios**\n\n"
            "Sistema profesional de marketing y publicidad.\n\n"
            "📊 **Tus Estadísticas:**\n"
            "• Total de Campañas: {total_campaigns}\n"
            "• Campañas Activas: {active_campaigns}\n"
            "• Alcance Total: {total_reach}\n"
            "• Inversión Total: ${total_spent}\n\n"
            "💡 *Crea campañas efectivas y alcanza a tu audiencia*"
        )
    
    # ============================================
    # CAMPAIGN
    # ============================================
    
    class Campaign:
        """Mensajes de campañas."""
        
        CREATE_FORM = (
            "✍️ **Crear Nueva Campaña**\n\n"
            "Configura tu campaña publicitaria:\n\n"
            "📝 **Nombre de la Campaña:**\n"
            "[Nombre descriptivo y único]\n\n"
            "🎯 **Audiencia Objetivo:**\n"
            "[Define tu público objetivo]\n\n"
            "💰 **Presupuesto:**\n"
            "[Cantidad en USD]\n\n"
            "📅 **Duración:**\n"
            "[Días que estará activa]\n\n"
            "📄 **Contenido del Anuncio:**\n"
            "[Texto del mensaje publicitario]\n\n"
            "💡 *Sé específico y profesional*"
        )
        
        CONFIRMATION = (
            "🔍 **Confirmar Campaña**\n\n"
            "📋 **Detalles de la Campaña:**\n"
            "📝 **Nombre:** {name}\n"
            "👥 **Audiencia:** {audience}\n"
            "💰 **Presupuesto:** ${budget}\n"
            "📊 **Alcance Estimado:** {estimated_reach}\n"
            "💳 **Costo por Impresión:** ${cost_per_impression}\n\n"
            "📄 **Vista Previa del Anuncio:**\n"
            "{ad_preview}\n\n"
            "⚠️ **Esta campaña gastará ${budget} de tu presupuesto.**\n\n"
            "💡 *Revisa todos los detalles antes de lanzar*"
        )
        
        LAUNCH_SUCCESS = (
            "✅ **Campaña Lanzada Exitosamente**\n\n"
            "Tu campaña está ahora activa.\n\n"
            "📋 **Detalles:**\n"
            "📝 **Nombre:** {campaign_name}\n"
            "🆔 **ID de Campaña:** {campaign_id}\n"
            "📊 **Alcance Estimado:** {estimated_reach}\n"
            "📅 **Fecha de Inicio:** {start_date}\n\n"
            "💡 *Las estadísticas se actualizarán en tiempo real*"
        )
        
        NO_CAMPAIGNS = (
            "📭 **Sin Campañas**\n\n"
            "Aún no has creado ninguna campaña.\n\n"
            "💡 *Crea tu primera campaña para empezar*"
        )
        
        LIST_HEADER = (
            "📋 **Tus Campañas**\n\n"
            "Lista de todas tus campañas:\n"
        )
        
        DETAILS = (
            "📋 **Detalles de la Campaña**\n\n"
            "📝 **Nombre:** {name}\n"
            "🆔 **ID:** {campaign_id}\n"
            "📊 **Estado:** {status}\n"
            "👥 **Audiencia:** {audience}\n"
            "💰 **Presupuesto:** ${budget}\n"
            "📈 **Alcance:** {reach}\n"
            "📅 **Creada:** {created_at}\n"
            "⏰ **Finaliza:** {end_date}\n\n"
            "📄 **Contenido:**\n"
            "{content}\n\n"
            "💡 *Esta campaña está {status}*"
        )
    
    # ============================================
    # AUDIENCE
    # ============================================
    
    class Audience:
        """Mensajes de audiencia."""
        
        SELECTION = (
            "👥 **Seleccionar Audiencia**\n\n"
            "Define tu público objetivo:\n\n"
            "🌍 **Todos los Usuarios:**\n"
            "• Máximo alcance\n"
            "• Ideal para anuncios generales\n\n"
            "🟢 **Usuarios Activos:**\n"
            "• Usuarios de los últimos 30 días\n"
            "• Mayor probabilidad de conversión\n\n"
            "👑 **Usuarios VIP:**\n"
            "• Miembros premium\n"
            "• Mayor poder adquisitivo\n\n"
            "🔔 **Usuarios Suscritos:**\n"
            "• Con notificaciones activas\n"
            "• Alta tasa de apertura\n\n"
            "🎯 **Personalizado:**\n"
            "• Segmentación avanzada\n"
            "• Filtros personalizados\n\n"
            "💡 *La audiencia correcta es clave para el éxito*"
        )
        
        STATISTICS = (
            "📊 **Estadísticas de Audiencia**\n\n"
            "👥 **Datos Demográficos:**\n"
            "• Total de usuarios: {total_users}\n"
            "• Usuarios activos: {active_users}\n"
            "• Usuarios VIP: {vip_users}\n"
            "• Usuarios suscritos: {subscribed_users}\n\n"
            "📈 **Comportamiento:**\n"
            "• Tasa de apertura: {open_rate}%\n"
            "• Tasa de clics: {click_rate}%\n"
            "• Tiempo promedio: {avg_time}s\n\n"
            "🌍 **Distribución Geográfica:**\n"
            "• América: {america}%\n"
            "• Europa: {europe}%\n"
            "• Asia: {asia}%\n"
            "• Otros: {others}%\n\n"
            "💡 *Usa estos datos para optimizar tus campañas*"
        )
        
        NO_USERS_AVAILABLE = (
            "📭 **Sin Usuarios Disponibles**\n\n"
            "No hay usuarios disponibles para esta audiencia.\n\n"
            "💡 *Intenta con una audiencia diferente*"
        )
        
        SELECT_USER = (
            "👥 **Seleccionar Usuario para Asignación**\n\n"
            "Elige el usuario que recibirá la tarea:\n\n"
            "💡 *Selecciona el miembro más adecuado*"
        )
    
    # ============================================
    # AD
    # ============================================
    
    class Ad:
        """Mensajes de anuncios."""
        
        COMPOSE_TEMPLATE = (
            "✍️ **Crear Anuncio**\n\n"
            "Audiencia: **{audience}**\n\n"
            "Escribe tu anuncio usando el siguiente formato:\n\n"
            "📝 **Título:** [Título llamativo]\n"
            "📄 **Descripción:** [Descripción detallada]\n"
            "🎯 **Llamada a la Acción:** [Texto del botón]\n"
            "🔗 **Enlace:** [URL opcional]\n\n"
            "💡 *Usa Markdown: **negrita**, *cursiva*, `código`*\n\n"
            "📝 **Ejemplo:**\n"
            "📝 **Título:** 🎉 Oferta Especial Limitada\n"
            "📄 **Descripción:** Obtén 50% de descuento en todos nuestros planes VIP...\n"
            "🎯 **Llamada a la Acción:** Ver Oferta\n"
            "🔗 **Enlace:** https://t.me/tu_bot"
        )
        
        PREVIEW = (
            "👁️ **Vista Previa del Anuncio**\n\n"
            "📝 **Título:** {title}\n"
            "📄 **Descripción:** {description}\n"
            "🎯 **Llamada a la Acción:** {cta}\n"
            "🔗 **Enlace:** {link}\n\n"
            "📊 **Estimaciones:**\n"
            "• Alcance potencial: {estimated_reach}\n"
            "• Tasa de apertura esperada: {expected_open_rate}%\n"
            "• Tasa de clics esperada: {expected_ctr}%\n"
            "• Costo estimado: ${estimated_cost}\n\n"
            "💡 *Revisa el anuncio antes de publicar*"
        )
        
        VALIDATION = (
            "⚠️ **Validación de Anuncio**\n\n"
            "Tu anuncio necesita ajustes:\n\n"
            "{validation_errors}\n\n"
            "💡 *Por favor, corrige los errores indicados*"
        )
    
    # ============================================
    # STATS
    # ============================================
    
    class Stats:
        """Mensajes de estadísticas."""
        
        CAMPAIGN_STATS = (
            "📊 **Estadísticas de Campañas**\n\n"
            "📈 **Rendimiento General:**\n"
            "• Total de Campañas: {total_campaigns}\n"
            "• Campañas Activas: {active_campaigns}\n"
            "• Alcance Total: {total_reach}\n"
            "• Inversión Total: ${total_spent}\n"
            "• CTR Promedio: {avg_ctr}%\n"
            "• CPC Promedio: ${avg_cpc}\n\n"
            "📅 **Últimos 30 días:**\n"
            "• Campañas lanzadas: {monthly_campaigns}\n"
            "• Alcance mensual: {monthly_reach}\n"
            "• Inversión mensual: ${monthly_spent}\n"
            "• ROI mensual: {monthly_roi}%\n\n"
            "💡 *Las estadísticas se actualizan cada hora*"
        )
        
        PERFORMANCE = (
            "📈 **Análisis de Rendimiento**\n\n"
            "🎯 **Métricas Clave:**\n"
            "• **Tasa de Apertura:** {open_rate}%\n"
            "• **Tasa de Clics:** {click_rate}%\n"
            "• **Tasa de Conversión:** {conversion_rate}%\n"
            "• **Costo por Clic:** ${cpc}\n"
            "• **Costo por Conversión:** ${cpc}\n"
            "• **ROI:** {roi}%\n\n"
            "📊 **Comparación con el Mes Anterior:**\n"
            "• Apertura: {open_change:+.1f}%\n"
            "• Clics: {click_change:+.1f}%\n"
            "• Conversiones: {conversion_change:+.1f}%\n"
            "• ROI: {roi_change:+.1f}%\n\n"
            "💡 *Usa estos datos para optimizar futuras campañas*"
        )
        
        AUDIENCE_ANALYSIS = (
            "👥 **Análisis de Audiencia**\n\n"
            "📊 **Demografía:**\n"
            "• Edad promedio: {avg_age} años\n"
            "• Género: {gender_distribution}\n"
            "• Ubicación: {location_distribution}\n"
            "• Dispositivos: {device_distribution}\n\n"
            "🎯 **Comportamiento:**\n"
            "• Horario pico: {peak_hour}:00\n"
            "• Día más activo: {most_active_day}\n"
            "• Tiempo promedio: {avg_time}s\n"
            "• Tasa de retención: {retention_rate}%\n\n"
            "💡 *Conoce a tu audiencia para mejores resultados*"
        )
    
    # ============================================
    # TEMPLATES
    # ============================================
    
    class Templates:
        """Mensajes de plantillas."""
        
        NO_TEMPLATES = (
            "📭 **Sin Plantillas Disponibles**\n\n"
            "No hay plantillas de anuncios guardadas.\n\n"
            "💡 *Crea plantillas para reutilizar anuncios efectivos*"
        )
        
        LIST_HEADER = (
            "📋 **Plantillas de Anuncios**\n\n"
            "Plantillas disponibles para usar:\n"
        )
        
        PREVIEW = (
            "👁️ **Vista Previa de Plantilla**\n\n"
            "📋 **Nombre:** {template_name}\n"
            "📝 **Descripción:** {description}\n"
            "🎯 **Tipo:** {type}\n"
            "💰 **Costo Sugerido:** ${suggested_budget}\n"
            "📊 **Rendimiento Histórico:**\n"
            "• CTR: {historical_ctr}%\n"
            "• Conversiones: {historical_conversions}%\n\n"
            "📄 **Contenido:**\n"
            "{template_content}\n\n"
            "💡 *Usa esta plantilla como base para tu campaña*"
        )
        
        CREATE_SUCCESS = (
            "✅ **Plantilla Creada**\n\n"
            "Tu plantilla ha sido guardada exitosamente.\n\n"
            "📋 **Nombre:** {template_name}\n"
            "🆔 **ID:** {template_id}\n"
            "📅 **Fecha de Creación:** {creation_date}\n\n"
            "💡 *Puedes usar esta plantilla en futuras campañas*"
        )
    
    # ============================================
    # ERRORS
    # ============================================
    
    class Error:
        """Mensajes de error."""
        
        SYSTEM_ERROR = (
            "❌ **Error del Sistema**\n\n"
            "No pude procesar tu solicitud de anuncios.\n\n"
            "Por favor, intenta más tarde o contacta soporte."
        )
        
        ANNOUNCER_ROLE_REQUIRED = (
            "🔒 **Rol de Anunciante Requerido**\n\n"
            "Esta función está disponible solo para usuarios con rol de anunciante.\n\n"
            "💡 *Actualiza tu plan para obtener acceso a marketing*"
        )
        
        CAMPAIGN_FAILED = (
            "❌ **Error al Crear Campaña**\n\n"
            "No pude crear tu campaña.\n\n"
            "Error: {error}\n\n"
            "💡 *Por favor, verifica los detalles e intenta nuevamente*"
        )
        
        INSUFFICIENT_BUDGET = (
            "💸 **Presupuesto Insuficiente**\n\n"
            "No tienes suficiente presupuesto para esta campaña.\n\n"
            "💡 *Recarga tu balance o ajusta el presupuesto*"
        )
        
        INVALID_AUDIENCE = (
            "⚠️ **Audiencia Inválida**\n\n"
            "La audiencia seleccionada no es válida.\n\n"
            "💡 *Por favor, selecciona una audiencia válida*"
        )
    
    # ============================================
    # SUCCESS
    # ============================================
    
    class Success:
        """Mensajes de éxito."""
        
        CAMPAIGN_COMPLETED = (
            "✅ **Campaña Completada**\n\n"
            "Tu campaña ha finalizado exitosamente.\n\n"
            "📋 **Resultados Finales:**\n"
            "• Nombre: {campaign_name}\n"
            "• Alcance: {final_reach}\n"
            "• Inversión: ${total_spent}\n"
            "• CTR: {final_ctr}%\n"
            "• Conversiones: {conversions}\n"
            "• ROI: {roi}%\n\n"
            "💎 *¡Excelente trabajo en tu campaña!*"
        )
        
        TARGET_REACHED = (
            "🎯 **Objetivo Alcanzado**\n\n"
            "¡Tu campaña ha alcanzado su objetivo!\n\n"
            "📊 **Métricas:**\n"
            "• Objetivo: {target_type}\n"
            "• Meta: {target_value}\n"
            "• Logrado: {achieved_value}\n"
            "• Eficiencia: {efficiency}%\n\n"
            "🎁 **Recompensa:** {reward}\n\n"
            "💎 *¡Sigue así para alcanzar más metas!*"
        )
        
        BONUS_EARNED = (
            "🎁 **Bonus de Rendimiento**\n\n"
            "Has ganado un bonus por excelente rendimiento.\n\n"
            "📊 **Criterios:**\n"
            "• CTR superior al promedio: {ctr_bonus}\n"
            "• Conversiones altas: {conversion_bonus}\n"
            "• ROI positivo: {roi_bonus}\n\n"
            "🎁 **Bonus Total:** ${total_bonus}\n\n"
            "💎 *¡Tu trabajo está dando excelentes resultados!*"
        )
    
    # ============================================
    # BILLING
    # ============================================
    
    class Billing:
        """Mensajes de facturación."""
        
        CHARGE_CONFIRMATION = (
            "💳 **Confirmación de Cargo**\n\n"
            "Se realizará un cargo a tu cuenta:\n\n"
            "📝 **Concepto:** {description}\n"
            "💰 **Monto:** ${amount}\n"
            "📅 **Fecha:** {date}\n"
            "💳 **Método:** {payment_method}\n\n"
            "💡 *Este cargo es por el uso del sistema de anuncios*"
        )
        
        CHARGE_SUCCESS = (
            "✅ **Cargo Procesado**\n\n"
            "El cargo ha sido procesado exitosamente.\n\n"
            "💰 **Monto:** ${amount}\n"
            "📝 **Concepto:** {description}\n"
            "🆔 **ID de Transacción:** {transaction_id}\n"
            "📅 **Fecha:** {date}\n\n"
            "💡 *Tu saldo ha sido actualizado*"
        )
        
        INSUFFICIENT_FUNDS = (
            "💸 **Fondos Insuficientes**\n\n"
            "No tienes suficientes fondos para esta operación.\n\n"
            "💰 **Saldo Actual:** ${current_balance}\n"
            "💰 **Requerido:** ${required_amount}\n"
            "💰 **Faltante:** ${missing_amount}\n\n"
            "💡 *Recarga tu balance para continuar*"
        )
    
    # ============================================
    # SCHEDULING
    # ============================================
    
    class Scheduling:
        """Mensajes de programación."""
        
        MENU = (
            "⏰ **Programar Campaña**\n\n"
            "Configura cuándo lanzar tu campaña:\n\n"
            "📅 **Opciones:**\n"
            "• Lanzar ahora\n"
            "• Programar para más tarde\n"
            "• Lanzar recurrentemente\n"
            "• Pausar campaña\n\n"
            "💡 *La programación te permite optimizar el alcance*"
        )
        
        DATE_SELECTION = (
            "📅 **Seleccionar Fecha**\n\n"
            "Elige la fecha para lanzar tu campaña:\n\n"
            "📆 **Opciones:**\n"
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
            "Elige la hora para lanzar tu campaña:\n\n"
            "🕐 **Horarios Recomendados:**\n"
            "• 09:00 - Mañana (alta actividad)\n"
            "• 12:00 - Mediodía (pausa laboral)\n"
            "• 18:00 - Tarde (fin de jornada)\n"
            "• 21:00 - Noche (tiempo libre)\n\n"
            "💡 *Considera la zona horaria de tu audiencia*"
        )
        
        RECURRING_OPTIONS = (
            "🔄 **Configurar Recurrencia**\n\n"
            "Elige la frecuencia de lanzamiento:\n\n"
            "📅 **Opciones:**\n"
            "• Una vez - Lanzamiento único\n"
            "• Diario - Todos los días\n"
            "• Semanal - Cada semana\n"
            "• Mensual - Cada mes\n"
            "• Personalizado - Configurar intervalo\n\n"
            "💡 *Las campañas recurrentes son ideales para branding*"
        )
