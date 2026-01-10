"""
Mensajes para sistema de referidos de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""


class ReferralMessages:
    """Mensajes para sistema de referidos."""
    
    # ============================================
    # MENU
    # ============================================
    
    class Menu:
        """Mensajes del menú de referidos."""
        
        MAIN = (
            "👥 **Sistema de Referidos**\n\n"
            "🔗 **Tu Enlace de Referido:**\n"
            "`{referral_link}`\n\n"
            "📋 **Tu Código:** `{referral_code}`\n\n"
            "📊 **Estadísticas:**\n"
            "• **Referidos Directos:** {direct_referrals}\n"
            "• **Ganancias Totales:** ${total_earnings:.2f}\n"
            "• **Comisión:** {commission}% por cada depósito\n\n"
            "💡 *Comparte tu enlace y gana estrellas!*"
        )
    
    # ============================================
    # STATS
    # ============================================
    
    class Stats:
        """Mensajes de estadísticas."""
        
        DETAILED = (
            "📊 **Estadísticas Detalladas**\n\n"
            "👥 **Total de Referidos:** {total_referrals}\n"
            "🟢 **Referidos Activos:** {active_referrals}\n"
            "🔴 **Referidos Pendientes:** {pending_referrals}\n"
            "💰 **Ganancias Totales:** ${total_earnings:.2f}\n"
            "💸 **Ganancias Mensuales:** ${monthly_earnings:.2f}\n"
            "📈 **Tasa de Comisión:** {commission}%\n"
            "🔑 **Tu Código:** `{referral_code}`\n\n"
            "💡 *Tus referidos están generando ingresos pasivos*"
        )
        
        PERFORMANCE = (
            "📈 **Rendimiento de Referidos**\n\n"
            "🎯 **Métricas Clave:**\n"
            "• **Tasa de Conversión:** 15.3%\n"
            "• **Valor Promedio:** $25.50\n"
            "• **Retención Mensual:** 78.5%\n"
            "• **Tiempo Promedio:** 3.2 días\n\n"
            "📊 **Comparación con el mes anterior:**\n"
            "• 📈 +12.5% más referidos\n"
            "• 💰 +8.3% más ganancias\n"
            "• 🎯 +5.2% mejor conversión\n\n"
            "💡 *Estás por encima del promedio!*"
        )
    
    # ============================================
    # LIST
    # ============================================
    
    class List:
        """Mensajes de lista de referidos."""
        
        HEADER = (
            "👥 **Tus Referidos**\n\n"
            "Lista de usuarios que se han registrado con tu código:\n"
        )
        
        NO_REFERRALS = (
            "📭 **Sin Referidos**\n\n"
            "Aún no tienes referidos registrados.\n\n"
            "💡 *Comparte tu enlace para empezar a ganar!*"
        )
        
        DETAILS = (
            "👤 **Detalles del Referido**\n\n"
            "👤 **Usuario:** {username}\n"
            "📅 **Fecha de Registro:** {registration_date}\n"
            "🟢 **Estado:** {status}\n"
            "💰 **Depósitos Totales:** ${total_deposits:.2f}\n"
            "💸 **Ganancias Generadas:** ${earnings:.2f}\n"
            "📈 **Última Actividad:** {last_activity}\n\n"
            "💡 *Este referido te ha generado {earnings:.2f}*"
        )
    
    # ============================================
    # SHARE
    # ============================================
    
    class Share:
        """Mensajes para compartir."""
        
        LINK = (
            "📢 **Comparte tu Enlace de Referido**\n\n"
            "🔗 **Enlace:** {referral_link}\n"
            "📋 **Código:** `{referral_code}`\n\n"
            "💰 **Gana {commission}%** por cada depósito de tus referidos.\n\n"
            "📱 **Opciones para compartir:**\n"
            "• Copia y pega en redes sociales\n"
            "• Envía a amigos y familiares\n"
            "• Publica en grupos de VPN\n"
            "• Comparte en foros de tecnología\n\n"
            "💡 *Cuanta más gente invites, más ganas!*"
        )
        
        SUCCESS = (
            "✅ **Enlace Compartido**\n\n"
            "Tu enlace de referido está listo para compartir.\n\n"
            "💡 *Recuerda: Cada depósito de tus referidos te genera ganancias*"
        )
        
        TIPS = (
            "💡 **Consejos para Atraer Referidos:**\n\n"
            "🎯 **Estrategias Efectivas:**\n"
            "• Comparte en grupos relacionados con VPN\n"
            "• Ofrece ayuda técnica a nuevos usuarios\n"
            "• Crea contenido sobre seguridad en línea\n"
            "• Participa en comunidades de tecnología\n\n"
            "📢 **Mensajes Sugeridos:**\n"
            "• \"🔥 ¡VPN gratis y segura! Únete con mi enlace: {referral_link}\"\n"
            "• \"🛡️ Protege tu privacidad online. Prueba esta VPN: {referral_link}\"\n"
            "• \"🌐 Acceso global a contenido. Mi código: {referral_code}\"\n\n"
            "💎 *Sé creativo y honesto en tus promociones*"
        )
    
    # ============================================
    # LEADERBOARD
    # ============================================
    
    class Leaderboard:
        """Mensajes de leaderboard."""
        
        MAIN = (
            "🏆 **Leaderboard de Referidos**\n\n"
            "📊 **Tu Posición:** #{user_rank}\n"
            "👤 **Tu ID:** {user_id}\n\n"
            "🥇 **Top Referidores del Mes:**\n"
        )
        
        USER_RANK = (
            "🎯 **Tu Posición en el Leaderboard**\n\n"
            "🏆 **Posición Actual:** #{user_rank}\n"
            "👥 **Referidos:** {referral_count}\n"
            "💰 **Ganancias:** ${earnings:.2f}\n"
            "📈 **Cambio Semanal:** {weekly_change:+.1f}%\n\n"
            "💡 *Sigue así para llegar al top!*"
        )
        
        REWARDS = (
            "🎁 **Recompensas del Leaderboard**\n\n"
            "🥇 **Top 1:** $100 bonus + 15% comisión extra\n"
            "🥈 **Top 2-3:** $50 bonus + 10% comisión extra\n"
            "🥉 **Top 4-10:** $25 bonus + 5% comisión extra\n"
            "🎯 **Top 11-50:** $10 bonus + 2% comisión extra\n\n"
            "💡 *Las recompensas se pagan mensualmente*"
        )
    
    # ============================================
    # APPLY
    # ============================================
    
    class Apply:
        """Mensajes para aplicar código."""
        
        INPUT_CODE = (
            "🔑 **Aplicar Código de Referido**\n\n"
            "Ingresa el código de referido que recibiste:\n\n"
            "💡 *Formato: 6 caracteres alfanuméricos*\n"
        )
        
        SUCCESS = (
            "✅ **Código Aplicado Exitosamente**\n\n"
            "¡Bienvenido! Has sido referido por {referrer_name}.\n\n"
            "🎁 **Beneficios Activados:**\n"
            "• 10 estrellas de bienvenida\n"
            "• Acceso a tutoriales exclusivos\n"
            "• Soporte prioritario por 24 horas\n\n"
            "💡 *Disfruta de tu bono de bienvenida!*"
        )
        
        INVALID_CODE = (
            "❌ **Código Inválido**\n\n"
            "El código ingresado no es válido o ya fue utilizado.\n\n"
            "💡 *Por favor, verifica el código e intenta nuevamente*"
        )
        
        ALREADY_USED = (
            "⚠️ **Código Ya Utilizado**\n\n"
            "Ya has aplicado un código de referido anteriormente.\n\n"
            "💡 *Cada usuario solo puede usar un código de referido*"
        )
    
    # ============================================
    # EARNINGS
    # ============================================
    
    class Earnings:
        """Mensajes de ganancias."""
        
        HISTORY_HEADER = (
            "💰 **Historial de Ganancias**\n\n"
            "Tus ganancias generadas por referidos:\n"
        )
        
        NO_EARNINGS = (
            "📭 **Sin Ganancias**\n\n"
            "Aún no tienes ganancias de referidos.\n\n"
            "💡 *Comparte tu enlace para empezar a ganar!*"
        )
        
        MONTHLY_SUMMARY = (
            "📊 **Resumen Mensual**\n\n"
            "💰 **Ganancias del Mes:** ${monthly_earnings:.2f}\n"
            "👥 **Nuevos Referidos:** {new_referrals}\n"
            "📈 **Promedio por Referido:** ${avg_per_referral:.2f}\n"
            "🎯 **Meta Mensual:** {monthly_goal}% alcanzada\n\n"
            "💡 *Estás generando ingresos pasivos!*"
        )
        
        WITHDRAWAL = (
            "💸 **Retiro de Ganancias**\n\n"
            "💰 **Saldo Disponible:** ${available_balance:.2f}\n"
            "📊 **Próximo Pago:** {next_payment_date}\n"
            "💳 **Método de Pago:** {payment_method}\n\n"
            "💡 *Las ganancias se procesan mensualmente*"
        )
    
    # ============================================
    # TIPS
    # ============================================
    
    class Tips:
        """Mensajes de consejos."""
        
        MAIN = (
            "💡 **Consejos para Maximizar tus Referidos**\n\n"
            "🎯 **Estrategias Probadas:**\n\n"
            "📱 **Redes Sociales:**\n"
            "• Comparte en grupos de tecnología\n"
            "• Usa hashtags relevantes (#VPN, #Seguridad, #Privacidad)\n"
            "• Crea contenido educativo sobre VPN\n\n"
            "💬 **Comunidades:**\n"
            "• Participa en foros de seguridad informática\n"
            "• Ayuda a nuevos usuarios con problemas técnicos\n"
            "• Comparte tus experiencias positivas\n\n"
            "📢 **Marketing Personal:**\n"
            "• Crea tutoriales en video\n"
            "• Escribe reseñas honestas\n"
            "• Ofrece soporte técnico gratuito\n\n"
            "🎁 **Incentivos Adicionales:**\n"
            "• Ofrece ayuda personalizada\n"
            "• Comparte trucos y consejos\n"
            "• Crea contenido exclusivo\n\n"
            "💡 *La autenticidad genera más confianza*"
        )
        
        BEST_PRACTICES = (
            "🏆 **Mejores Prácticas**\n\n"
            "✅ **Lo que SÍ funciona:**\n"
            "• Ser honesto sobre beneficios y limitaciones\n"
            "• Proporcionar valor real antes de pedir\n"
            "• Crear relaciones genuinas\n"
            "• Educar sobre seguridad en línea\n"
            "• Ser paciente y persistente\n\n"
            "❌ **Lo que NO funciona:**\n"
            "• Spam masivo sin contexto\n"
            "• Promesas exageradas\n"
            "• Compartir en lugares irrelevantes\n"
            "• Ser insistente o agresivo\n"
            "• Ocultar información importante\n\n"
            "💡 *La calidad es más importante que la cantidad*"
        )
    
    # ============================================
    # ERRORS
    # ============================================
    
    class Error:
        """Mensajes de error."""
        
        SYSTEM_ERROR = (
            "❌ **Error del Sistema**\n\n"
            "No pude procesar tu solicitud de referidos.\n\n"
            "Por favor, intenta más tarde o contacta soporte."
        )
        
        INVALID_CODE = (
            "❌ **Código Inválido**\n\n"
            "El código ingresado no es válido.\n\n"
            "💡 *Por favor, verifica el código e intenta nuevamente*"
        )
        
        CODE_EXPIRED = (
            "⏰ **Código Expirado**\n\n"
            "El código de referido ha expirado.\n\n"
            "💡 *Los códigos expiran después de 30 días*"
        )
        
        ALREADY_REFERRED = (
            "⚠️ **Ya Referido**\n\n"
            "Ya estás referido por otro usuario.\n\n"
            "💡 *Cada usuario solo puede tener un referido*"
        )
        
        REFERRAL_LIMIT = (
            "📊 **Límite Alcanzado**\n\n"
            "Has alcanzado el límite de referidos para tu plan.\n\n"
            "💡 *Actualiza tu plan para más referidos*"
        )
    
    # ============================================
    # SUCCESS
    # ============================================
    
    class Success:
        """Mensajes de éxito."""
        
        REFERRAL_REGISTERED = (
            "✅ **Referido Registrado**\n\n"
            "¡Nuevo referido registrado exitosamente!\n\n"
            "👤 **Usuario:** {username}\n"
            "📅 **Fecha:** {registration_date}\n\n"
            "💎 *Ganarás cuando realice su primer depósito*"
        )
        
        EARNING_RECORDED = (
            "💰 **Ganancia Registrada**\n\n"
            "Has ganado una nueva comisión de referido.\n\n"
            "💰 **Monto:** ${amount:.2f}\n"
            "👤 **De:** {referral_username}\n"
            "📅 **Fecha:** {date}\n\n"
            "💎 *Tus ganancias están disponibles para retirar*"
        )
        
        CODE_SHARED = (
            "📢 **Código Compartido**\n\n"
            "Tu código de referido ha sido compartido.\n\n"
            "💡 *Recuerda: Cada depósito de tus referidos te genera ganancias*"
        )
        
        LEADERBOARD_UPDATED = (
            "🏆 **Posición Actualizada**\n\n"
            "Tu posición en el leaderboard ha sido actualizada.\n\n"
            "🎯 **Nueva Posición:** #{new_rank}\n"
            "📈 **Cambio:** {change:+.1f} posiciones\n\n"
            "💎 *Sigue así para llegar al top!*"
        )
