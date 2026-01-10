"""
Mensajes para operaciones del usuario de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""


class OperationsMessages:
    """Mensajes para operaciones del usuario."""
    
    # ============================================
    # MENU
    # ============================================
    
    class Menu:
        """Mensajes del menú de operaciones."""
        
        MAIN = (
            "💰 **Centro de Operaciones**\n\n"
            "Gestiona tu cuenta y accede a servicios premium:\n\n"
            "💎 **Balance y Transacciones**\n"
            "👥 **Sistema de Referidos**\n"
            "👑 **Planes VIP**\n"
            "🎮 **Juegos y Recompensas**\n\n"
            "Selecciona una opción:"
        )
    
    # ============================================
    # BALANCE
    # ============================================
    
    class Balance:
        """Mensajes de balance."""
        
        DISPLAY = (
            "💰 **Tu Balance**\n\n"
            "👤 **Usuario:** {name}\n"
            "⭐ **Balance Actual:** {balance} estrellas\n"
            "💳 **Total Depositado:** ${total_deposited:.2f}\n"
            "💸 **Total Gastado:** ${total_spent:.2f}\n"
            "🎁 **Ganancias Referidos:** {referral_earnings} estrellas\n\n"
            "💡 Usa tus estrellas para desbloquear contenido premium."
        )
        
        NO_BALANCE = (
            "💰 **Sin Balance**\n\n"
            "No tienes estrellas en tu cuenta.\n\n"
            "💡 *Opciones para obtener estrellas:*\n"
            "• Deposita fondos\n"
            "• Invita amigos (referidos)\n"
            "• Completa logros y juegos"
        )
        
        TRANSACTION_SUCCESS = (
            "✅ **Transacción Exitosa**\n\n"
            "Tu balance ha sido actualizado.\n\n"
            "💰 **Nuevo Balance:** {balance} estrellas"
        )
        
        TRANSACTION_FAILED = (
            "❌ **Transacción Fallida**\n\n"
            "No pude procesar tu transacción.\n\n"
            "Error: {error}"
        )
    
    # ============================================
    # REFERRAL
    # ============================================
    
    class Referral:
        """Mensajes de referidos."""
        
        MENU = (
            "👥 **Sistema de Referidos**\n\n"
            "🔗 **Tu Enlace de Referido:**\n"
            "`{referral_link}`\n\n"
            "📋 **Tu Código:** `{referral_code}`\n\n"
            "📊 **Estadísticas:**\n"
            "• **Referidos Directos:** {direct_referrals}\n"
            "• **Ganancias Totales:** {total_earnings} estrellas\n"
            "• **Comisión:** {commission}% por cada depósito\n\n"
            "💡 *Comparte tu enlace y gana estrellas!*"
        )
        
        NEW_REFERRAL = (
            "🎉 **¡Nuevo Referido!**\n\n"
            "Alguien se ha registrado con tu código.\n\n"
            "🎁 **Ganarás estrellas cuando realice su primer depósito.**"
        )
        
        REFERRAL_EARNED = (
            "⭐ **¡Ganancia de Referido!**\n\n"
            "Has ganado {earnings} estrellas por el depósito de tu referido.\n\n"
            "💰 **Balance Actualizado:** {balance} estrellas"
        )
        
        NO_REFERRALS = (
            "📭 **Sin Referidos**\n\n"
            "Aún no tienes referidos registrados.\n\n"
            "💡 *Comparte tu enlace para empezar a ganar!*"
        )
    
    # ============================================
    # VIP
    # ============================================
    
    class VIP:
        """Mensajes de planes VIP."""
        
        PLANS = (
            "👑 **Planes VIP uSipipo**\n\n"
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
        
        ALREADY_VIP = (
            "👑 **Ya eres VIP**\n\n"
            "Tu plan actual está activo.\n\n"
            "📅 **Renueva:** {renewal_date}\n"
            "🎁 **Beneficios activos:** Disfruta de todas las funciones VIP"
        )
        
        UPGRADE_SUCCESS = (
            "🎉 **¡Actualización VIP Exitosa!**\n\n"
            "Tu plan ha sido actualizado correctamente.\n\n"
            "👑 **Plan:** {plan_name}\n"
            "📅 **Válido hasta:** {expiry_date}\n\n"
            "💎 *Disfruta de tus nuevos beneficios VIP*"
        )
    
    # ============================================
    # GAME
    # ============================================
    
    class Game:
        """Mensajes de juegos."""
        
        MENU = (
            "🎮 **Juegos y Recompensas**\n\n"
            "Diviértete mientras ganas estrellas:\n\n"
            "🎲 **Ruleta de la Suerte**\n"
            "• Gana hasta 100 estrellas\n"
            "• 1 tirada gratis cada 24h\n\n"
            "🎯 **Trivia uSipipo**\n"
            "• Preguntas sobre VPN y seguridad\n"
            "• 10 estrellas por respuesta correcta\n\n"
            "🏆 **Desafíos Diarios**\n"
            "• Completa misiones especiales\n"
            "• Recompensas variables\n\n"
            "💡 *Juega responsablemente y diviértete*"
        )
        
        SPIN_SUCCESS = (
            "🎲 **Resultado de la Ruleta**\n\n"
            "🎯 **Premio:** {prize}\n"
            "⭐ **Ganado:** {winnings} estrellas\n\n"
            "💰 **Nuevo Balance:** {balance} estrellas\n\n"
            "🔄 **Próxima tirada gratis:** {next_spin}"
        )
        
        SPIN_FAILED = (
            "❌ **Error en la Ruleta**\n\n"
            "No pude procesar tu tirada.\n\n"
            "💡 *Inténtalo de nuevo más tarde*"
        )
    
    # ============================================
    # TRANSACTIONS
    # ============================================
    
    class Transactions:
        """Mensajes de transacciones."""
        
        HISTORY = (
            "📊 **Historial de Transacciones**\n\n"
            "Usuario: {user_id}\n"
            "Total de transacciones: {count}\n\n"
            "📋 *Aquí se mostrará tu historial completo*"
        )
        
        TRANSACTION_DETAIL = (
            "📋 **Detalle de Transacción**\n\n"
            "🆔 **ID:** {transaction_id}\n"
            "📅 **Fecha:** {date}\n"
            "💰 **Monto:** ${amount:.2f}\n"
            "📝 **Descripción:** {description}\n"
            "🟢 **Estado:** {status}\n\n"
            "💡 *Esta transacción ya ha sido procesada*"
        )
        
        NO_TRANSACTIONS = (
            "📭 **Sin Transacciones**\n\n"
            "No tienes transacciones registradas.\n\n"
            "💡 *Realiza tu primera operación para ver el historial*"
        )
    
    # ============================================
    # ERRORS
    # ============================================
    
    class Error:
        """Mensajes de error."""
        
        SYSTEM_ERROR = (
            "❌ **Error del Sistema**\n\n"
            "No pude procesar tu solicitud.\n\n"
            "Por favor, intenta más tarde."
        )
        
        SERVICE_UNAVAILABLE = (
            "⚠️ **Servicio No Disponible**\n\n"
            "Esta función no está disponible temporalmente.\n\n"
            "Por favor, intenta más tarde."
        )
        
        INSUFFICIENT_BALANCE = (
            "💸 **Balance Insuficiente**\n\n"
            "No tienes suficientes estrellas para esta operación.\n\n"
            "💡 *Recarga tu balance para continuar*"
        )
        
        INVALID_AMOUNT = (
            "❌ **Monto Inválido**\n\n"
            "El monto especificado no es válido.\n\n"
            "💡 *Verifica el amounto e intenta nuevamente*"
        )
    
    # ============================================
    # SUCCESS
    # ============================================
    
    class Success:
        """Mensajes de éxito."""
        
        OPERATION_COMPLETED = (
            "✅ **Operación Completada**\n\n"
            "Tu solicitud ha sido procesada exitosamente."
        )
        
        PAYMENT_PROCESSED = (
            "💳 **Pago Procesado**\n\n"
            "Tu pago ha sido procesado correctamente.\n\n"
            "💰 **Balance Actualizado:** {balance} estrellas"
        )
        
        REFERRAL_LINK_SHARED = (
            "🔗 **Enlace Compartido**\n\n"
            "Tu enlace de referido está listo para compartir.\n\n"
            "💡 *Cuanta más gente invites, más ganas!*"
        )
