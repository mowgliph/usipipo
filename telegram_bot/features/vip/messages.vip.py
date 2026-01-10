"""
Mensajes para sistema VIP de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""


class VipMessages:
    """Mensajes para sistema VIP."""
    
    # ============================================
    # PLANS
    # ============================================
    
    class Plans:
        """Mensajes de planes VIP."""
        
        MAIN = (
            "👑 **Planes VIP uSipipo**\n\n"
            "💰 **Tu Balance Actual:** ${balance:.2f}\n\n"
            "Desbloquea funciones exclusivas y beneficios premium:\n\n"
            "🌟 **Plan Básico - $9.99/mes**\n"
            "• Llaves VPN ilimitadas\n"
            "• 100 GB de datos por llave\n"
            "• Soporte prioritario\n\n"
            "💎 **Plan Premium - $19.99/mes**\n"
            "• Todo del plan básico +\n"
            "• 500 GB de datos por llave\n"
            "• Acceso a servidores dedicados\n"
            "• Sin límites de velocidad\n\n"
            "💎 **Plan Elite - $39.99/mes**\n"
            "• Todo del plan premium +\n"
            "• Datos ilimitados\n"
            "• Acceso a todos los servidores\n"
            "• Soporte 24/7 exclusivo\n\n"
            "💡 *Selecciona el plan que mejor se adapte a tus necesidades*"
        )
        
        DETAILS = (
            "👑 **{plan_name}**\n\n"
            "💰 **Precio:** ${price}/mes\n"
            "⏰ **Duración:** {duration}\n\n"
            "🎯 **Características:**\n{features}\n\n"
            "🎁 **Beneficios Exclusivos:**\n{benefits}\n\n"
            "💡 *Mejora tu experiencia con beneficios premium*"
        )
        
        COMPARISON = (
            "📊 **Comparación de Planes**\n\n"
            "| Característica | Básico | Premium | Elite |\n"
            "|---------------|---------|---------|-------|\n"
            "| Precio | $9.99 | $19.99 | $39.99 |\n"
            "| Llaves VPN | Ilimitadas | Ilimitadas | Ilimitadas |\n"
            "| Datos por llave | 100 GB | 500 GB | Ilimitados |\n"
            "| Servidores dedicados | ❌ | ✅ | ✅ |\n"
            "| Límites de velocidad | ❌ | ✅ | ✅ |\n"
            "| Soporte 24/7 | ❌ | ✅ | ✅ |\n"
            "| Backup en la nube | ❌ | ✅ | ✅ |\n"
            "| Cuenta dedicada | ❌ | ❌ | ✅ |\n\n"
            "💡 *Elige el plan que mejor se adapte a tus necesidades*"
        )
    
    # ============================================
    # STATUS
    #============================================
    
    class Status:
        """Mensajes de estado VIP."""
        
        ALREADY_VIP = (
            "👑 **Ya eres VIP**\n\n"
            "Tu plan **{plan_name}** está activo.\n\n"
            "📅 **Válido hasta:** {expiry_date}\n"
            "🎁 **Beneficios activos:**\n{benefits}\n\n"
            "💎 *Disfruta de todas las funciones VIP*"
        )
        
        NOT_VIP = (
            "📭 **Aún no eres VIP**\n\n"
            "Desbloquea funciones exclusivas y beneficios premium.\n\n"
            "💡 *Actualiza a VIP para disfrutar de:* \n"
            "• Llaves VPN ilimitadas\n"
            "• Datos ilimitados\n"
            "• Soporte prioritario\n"
            "• Acceso a servidores exclusivos"
        )
        
        EXPIRED = (
            "⏰ **Membresía VIP Expirada**\n\n"
            "Tu membresía VIP ha expirado.\n\n"
            "💡 *Renueva para seguir disfrutando de:* \n"
            "• Beneficios exclusivos\n"
            "• Funciones premium\n"
            "• Soporte prioritario"
        )
        
        EXTENDED = (
            "🎉 **Membresía VIP Extendida**\n\n"
            "Tu membresía VIP ha sido extendida.\n\n"
            "👑 **Plan:** {plan_name}\n"
            "📅 **Nueva fecha de expiración:** {new_expiry_date}\n\n"
            "💎 *Sigue disfrutando de todos los beneficios VIP*"
        )
    
    # ============================================
    # PAYMENT
    #============================================
    
    class Payment:
        """Mensajes de pago VIP."""
        
        INSUFFICIENT_BALANCE = (
            "💸 **Balance Insuficiente**\n\n"
            "No tienes suficientes fondos para este plan.\n\n"
            "💰 **Balance Actual:** ${current_balance:.2f}\n"
            "💳 **Requerido:** ${required:.2f}\n"
            "📉 **Faltante:** ${missing:.2f}\n\n"
            "💡 *Recarga tu balance para continuar*"
        )
        
        SUCCESS = (
            "🎉 **¡Actualización VIP Exitosa!**\n\n"
            "Tu pago ha sido procesado correctamente.\n\n"
            "👑 **Plan:** {plan_name}\n"
            "💳 **Pagado:** ${price:.2f}\n"
            "💰 **Nuevo Balance:** ${new_balance:.2f}\n\n"
            "💎 *Disfruta de tus nuevos beneficios VIP*"
        )
        
        FAILED = (
            "❌ **Pago Fallido**\n\n"
            "No pude procesar tu pago.\n\n"
            "💡 *Por favor, intenta más tarde o contacta soporte.*"
        )
        
        PROCESSING = (
            "⏳ **Procesando Pago**\n\n"
            "Tu pago está siendo procesado.\n\n"
            "💡 *Por favor, espera un momento...*"
        )
    
    # ============================================
    # BENEFITS
    #============================================
    
    class Benefits:
        """Mensajes de beneficios VIP."""
        
        ACTIVE = (
            "🎁 **Tus Beneficios VIP**\n\n"
            "👑 **Plan:** {plan_name}\n"
            "📅 **Días restantes:** {remaining_days}\n\n"
            "🎯 **Beneficios Activos:**\n{benefits}\n\n"
            "📊 **Estadísticas de Uso:**\n{usage_stats}\n\n"
            "💎 *Aprovecha al máximo tus beneficios VIP*"
        )
        
        NEW_BENEFIT = (
            "🎁 **¡Nuevo Beneficio VIP!**\n\n"
            "Se ha desbloqueado un nuevo beneficio:\n\n"
            "🎯 **{benefit_name}**\n"
            "{benefit_description}\n\n"
            "💎 *Disfruta de tu nueva ventaja VIP*"
        )
        
        USAGE_STATS = (
            "📊 **Estadísticas de Uso VIP**\n\n"
            "🔑 **Llaves VIP creadas:** {vip_keys_created}\n"
            "📈 **Datos consumidos:** {data_consumed} GB\n"
            "🌐 **Servidores utilizados:** {servers_used}\n"
            "⏰ **Tiempo activo:** {active_time} horas\n\n"
            "💎 *Estás aprovechando bien tu membresía VIP*"
        )
    
    # ============================================
    # EXTENSION
    #============================================
    
    class Extension:
        """Mensajes de extensión VIP."""
        
        EXTENSION_OPTIONS = (
            "⏰ **Extender Membresía VIP**\n\n"
            "Selecciona cómo quieres extender tu membresía:\n\n"
            "📅 **Por tiempo:**\n"
            "• 1 mes - 10% descuento\n"
            "• 3 meses - 15% descuento\n"
            "• 6 meses - 20% descuento\n"
            "• 1 año - 25% descuento\n\n"
            "💎 **Por plan:**\n"
            "• Mantener plan actual\n"
            "• Actualizar a plan superior\n\n"
            "💡 *Las extensiones acumulan beneficios*"
        )
        
        CONFIRMATION = (
            "⏰ **Confirmar Extensión**\n\n"
            "📅 **Duración:** {duration}\n"
            "💰 **Costo:** ${price:.2f}\n"
            "🎁 **Descuento:** {discount}%\n"
            "💳 **Total:** ${total:.2f}\n\n"
            "💡 *Tu membresía se extenderá automáticamente*"
        )
        
        SUCCESS = (
            "🎉 **Extensión Confirmada**\n\n"
            "Tu membresía VIP ha sido extendida.\n\n"
            "📅 **Nueva fecha de expiración:** {new_expiry_date}\n"
            "💰 **Pagado:** ${total:.2f}\n\n"
            "💎 *Sigue disfrutando de todos los beneficios VIP*"
        )
    
    # ============================================
    # ERRORS
    #============================================
    
    class Error:
        """Mensajes de error."""
        
        SYSTEM_ERROR = (
            "❌ **Error del Sistema**\n\n"
            "No pude procesar tu solicitud VIP.\n\n"
            "Por favor, intenta más tarde o contacta soporte."
        )
        
        PLAN_NOT_FOUND = (
            "❌ **Plan No Encontrado**\n\n"
            "El plan seleccionado no está disponible.\n\n"
            "💡 *Por favor, selecciona un plan válido*"
        )
        
        ALREADY_VIP = (
            "⚠️ **Ya eres VIP**\n\n"
            "Ya tienes una membresía VIP activa.\n\n"
            "💡 *Puedes extender tu membresía o cambiar de plan*"
        )
        
        PAYMENT_ERROR = (
            "❌ **Error en el Pago**\n\n"
            "No pude procesar tu pago.\n\n"
            "Error: {error}\n\n"
            "💡 *Por favor, verifica tu balance e intenta nuevamente*"
        )
        
        EXTENSION_ERROR = (
            "❌ **Error en Extensión**\n\n"
            "No pude extender tu membresía.\n\n"
            "💡 *Por favor, intenta más tarde o contacta soporte*"
        )
    
    # ============================================
    # SUCCESS
    #============================================
    
    class Success:
        """Mensajes de éxito."""
        
        UPGRADE_COMPLETE = (
            "✅ **Actualización Completa**\n\n"
            "Tu cuenta ha sido actualizada a VIP.\n\n"
            "🎁 *Todos los beneficios están disponibles ahora*"
        )
        
        BENEFIT_UNLOCKED = (
            "🎁 **Beneficio Desbloqueado**\n\n"
            "Has desbloqueado un nuevo beneficio VIP.\n\n"
            "💎 *Disfruta de tu nueva ventaja*"
        )
        
        EXTENSION_SUCCESS = (
            "✅ **Extensión Exitosa**\n\n"
            "Tu membresía VIP ha sido extendida.\n\n"
            "💎 *Sigue disfrutando de todos los beneficios*"
        )
