"""
Mensajes para operaciones del bot uSipipo (pagos, VIP, referidos).

Organiza los mensajes relacionados con:
- Gestión de saldo y pagos
- Sistema VIP
- Referidos y bonificaciones
- Transacciones

Author: uSipipo Team
Version: 1.0.0
"""


class OperationMessages:
    """Mensajes para operaciones y transacciones."""
    
    # ============================================
    # BALANCE & WALLET
    # ============================================
    
    class Balance:
        """Mensajes de saldo y cartera."""
        
        HEADER = (
            "💰 **Mi Saldo**\n"
            "━━━━━━━━━━━━\n"
        )
        
        DISPLAY = (
            "💵 **Saldo Disponible:** ${balance}\n"
            "📊 **Total Depositado:** ${total_deposited}\n"
            "📉 **Gastado:** ${total_spent}\n"
            "📈 **Ganado (Referidos):** ${referral_earnings}\n"
        )
        
        ADD_FUNDS = (
            "💳 **Agregar Fondos**\n"
            "━━━━━━━━━━━━\n\n"
            "Elige tu método de pago:"
        )
        
        NO_BALANCE = (
            "❌ **Sin Saldo**\n\n"
            "Tu saldo es $0\n"
            "Agrega fondos para disfrutar de VIP."
        )
        
        TRANSACTION_HISTORY = (
            "📋 **Historial de Transacciones**\n"
            "━━━━━━━━━━━━\n"
        )
        
        NO_TRANSACTIONS = (
            "📭 **Sin transacciones**\n\n"
            "Aquí aparecerán tus movimientos."
        )
    
    # ============================================
    # VIP MEMBERSHIP
    # ============================================
    
    class VIP:
        """Mensajes del sistema VIP."""
        
        MENU = (
            "👑 **Membresía VIP**\n"
            "━━━━━━━━━━━━\n\n"
            "Disfruta de beneficios exclusivos:\n\n"
            "✨ **Beneficios VIP:**\n"
            "• 🚀 Datos ilimitados\n"
            "• ⚡ Velocidad prioritaria\n"
            "• 🌍 Acceso a todos los servidores\n"
            "• 🔐 10 llaves simultáneas\n"
            "• 📊 Estadísticas avanzadas\n"
            "• 🎁 Acceso a promociones exclusivas\n"
            "• 👥 Referidos con bonus 5x\n"
        )
        
        PRICING = (
            "👑 **Planes VIP**\n"
            "━━━━━━━━━━━━\n\n"
            "📅 **Mensual:** ${monthly_price}/mes\n"
            "   → Cancela cuando quieras\n\n"
            "📈 **Trimestral:** ${quarterly_price}/3 meses\n"
            "   → Ahorra {quarterly_discount}%\n\n"
            "📊 **Anual:** ${yearly_price}/año\n"
            "   → Ahorra {yearly_discount}%\n"
        )
        
        ACTIVE = (
            "👑 **Eres VIP**\n"
            "━━━━━━━━━━━━\n\n"
            "✨ Plan: **{plan}**\n"
            "⏰ Expira: **{expiration}**\n"
            "🔄 Renovación automática: **{auto_renew}**\n\n"
            "🎉 ¡Disfruta de tus beneficios exclusivos!"
        )
        
        EXPIRED = (
            "⏰ **Tu VIP ha expirado**\n\n"
            "📅 Expiró el: **{expired_date}**\n\n"
            "👑 Renueva para recuperar beneficios."
        )
        
        PURCHASE_CONFIRM = (
            "👑 **Confirmar Compra VIP**\n"
            "━━━━━━━━━━━━\n\n"
            "📋 **Plan:** {plan}\n"
            "💰 **Precio:** ${price}\n"
            "⏰ **Duración:** {duration}\n"
            "🔄 **Renovación:** {auto_renew}\n\n"
            "Presiona confirmar para procesar."
        )
        
        PURCHASE_SUCCESS = (
            "✅ **¡Bienvenido a VIP!**\n\n"
            "👑 Plan: **{plan}**\n"
            "⏰ Expira: **{expiration}**\n\n"
            "🎉 Ahora disfruta de:\n"
            "• Datos ilimitados\n"
            "• Velocidad prioritaria\n"
            "• Acceso a todos los servidores\n"
            "• 10 llaves simultáneas\n"
        )
        
        UPGRADE_AVAILABLE = (
            "💎 **Oportunidad de Mejora**\n\n"
            "Mejora a {target_plan} y obtén:\n"
            "✨ {additional_benefits}\n\n"
            "Ahorra {discount}% en tu próxima renovación."
        )
    
    # ============================================
    # PAYMENTS & METHODS
    # ============================================
    
    class Payments:
        """Mensajes de pagos y métodos."""
        
        METHODS = (
            "💳 **Métodos de Pago**\n"
            "━━━━━━━━━━━━\n\n"
            "Elige cómo pagar:"
        )
        
        CRYPTO_PAYMENT = (
            "₿ **Pago con Criptomonedas**\n"
            "━━━━━━━━━━━━\n\n"
            "💰 **Monto:** ${amount}\n"
            "💱 **Moneda:** {crypto_type}\n"
            "💳 **Dirección:** `{wallet_address}`\n\n"
            "⏰ **Válido por:** 10 minutos\n\n"
            "✅ Envía exactamente **{amount_crypto}**"
        )
        
        CRYPTO_PENDING = (
            "⏳ **Transacción en Espera**\n\n"
            "Hemos recibido tu pago.\n"
            "Esperando confirmación en blockchain...\n\n"
            "Esto puede tomar 5-10 minutos."
        )
        
        CRYPTO_CONFIRMED = (
            "✅ **¡Pago Confirmado!**\n\n"
            "💰 ${amount} acreditados a tu cuenta.\n"
            "💱 TxID: `{transaction_id}`\n\n"
            "Disfruta tus nuevos fondos."
        )
        
        CRYPTO_EXPIRED = (
            "❌ **Transacción Expirada**\n\n"
            "No se recibió pago en tiempo.\n\n"
            "🔄 Intenta crear una nueva solicitud."
        )
        
        CRYPTO_INVALID = (
            "❌ **Monto Incorrecto**\n\n"
            "Enviaste {wrong_amount} pero era {required_amount}\n\n"
            "🔄 Intenta de nuevo o contacta soporte."
        )
        
        PAYPAL_REDIRECT = (
            "🔗 **Redireccionando a PayPal...**\n\n"
            "Si no se abre automáticamente,\n"
            "[haz clic aquí]({paypal_url})"
        )
        
        PAYPAL_SUCCESS = (
            "✅ **Pago exitoso**\n\n"
            "💰 ${amount} completados via PayPal\n"
            "🆔 ID: `{transaction_id}`"
        )
    
    # ============================================
    # MENU SYSTEM
    # ============================================
    
    class Menu:
        """Mensajes de menú de operaciones."""
        
        MAIN = (
            "💰 **Operaciones**\n"
            "━━━━━━━━━━━━\n\n"
            "Selecciona una operación:"
        )
    
    # ============================================
    # REFERRAL SYSTEM
    # ============================================
    
    class Referral:
        """Mensajes del sistema de referidos."""
        
        MENU = (
            "🤝 **Programa de Referidos**\n"
            "━━━━━━━━━━━━\n\n"
            "Invita amigos y gana dinero.\n\n"
            "📊 **Tu Enlace:**\n"
            "`{referral_link}`\n\n"
            "💰 **Ganancias Totales:** ${total_earned}\n"
            "👥 **Referidos:** {referral_count}\n"
        )
        
        CODE = (
            "🔗 **Tu Código de Referido**\n"
            "━━━━━━━━━━━━\n\n"
            "📋 **Código:** `{referral_code}`\n\n"
            "¡Compártelo y gana recompensas!"
        )
        
        SHARE = (
            "📤 **Compartir Referido**\n\n"
            "🔗 **Enlace de referido:**\n"
            "https://t.me/{bot_username}?start={referral_code}\n\n"
            "📋 **Código:** `{referral_code}`\n\n"
            "¡Invita amigos y gana estrellas!"
        )
        
        TERMS = (
            "🤝 **Cómo Funciona**\n"
            "━━━━━━━━━━━━\n\n"
            "1️⃣ Comparte tu link único\n"
            "2️⃣ Tus amigos se registran\n"
            "3️⃣ Ganas el 20% de su gasto\n"
            "4️⃣ Retira a tu cartera\n\n"
            "👑 **Bonificación VIP:**\n"
            "Si eres VIP, ganas 5x más → 100%"
        )
        
        REFERRAL_LIST = (
            "👥 **Mis Referidos**\n"
            "━━━━━━━━━━━━\n"
        )
        
        REFERRAL_ENTRY = (
            "👤 {name} | ID: `{user_id}`\n"
            "   Registrado: {join_date}\n"
            "   Gasto: ${spent} | Tu comisión: ${earned}\n"
        )
        
        NO_REFERRALS = (
            "📭 **Sin referidos aún**\n\n"
            "Invita amigos para empezar a ganar."
        )
        
        EARNINGS_SUMMARY = (
            "💰 **Resumen de Ganancias**\n"
            "━━━━━━━━━━━━\n\n"
            "📊 **Este mes:** ${monthly}\n"
            "📈 **Total:** ${total}\n"
            "👥 **Referidos activos:** {active_count}\n"
            "🔔 **Pendiente de pago:** ${pending}\n"
        )
        
        WITHDRAWAL = (
            "💳 **Solicitar Retiro**\n"
            "━━━━━━━━━━━━\n\n"
            "💰 **Saldo disponible:** ${available}\n"
            "💵 **Monto mínimo:** $5\n\n"
            "¿Cuánto deseas retirar?"
        )
        
        WITHDRAWAL_SUCCESS = (
            "✅ **Retiro Procesado**\n\n"
            "💰 ${amount} será transferido a tu cuenta\n"
            "⏰ Tiempo estimado: 24-48 horas\n"
            "🆔 ID del retiro: `{withdrawal_id}`"
        )
    
    # ============================================
    # BONUSES & PROMOTIONS
    # ============================================
    
    class Bonuses:
        """Mensajes de bonificaciones y promociones."""
        
        AVAILABLE = (
            "🎁 **Bonificaciones Disponibles**\n"
            "━━━━━━━━━━━━\n"
        )
        
        BONUS_OFFER = (
            "🎉 **{bonus_name}**\n\n"
            "📊 Recompensa: {reward}\n"
            "⏰ Válido hasta: {expiration}\n"
            "📋 Requisitos: {requirements}\n"
        )
        
        CLAIMED = (
            "✅ **Bonificación Reclamada**\n\n"
            "🎉 {bonus_name}\n"
            "💰 Recompensa: {reward}\n\n"
            "Revisa tu saldo actualizado."
        )
        
        ALREADY_CLAIMED = (
            "ℹ️ **Ya reclamada**\n\n"
            "Esta bonificación ya fue utilizada."
        )
        
        EXPIRED = (
            "⏰ **Expirada**\n\n"
            "Esta bonificación ya no es válida."
        )
    
    # ============================================
    # ERRORS & CONFIRMATIONS
    # ============================================
    
    class Errors:
        """Mensajes de error en operaciones."""
        
        INSUFFICIENT_BALANCE = (
            "❌ **Saldo Insuficiente**\n\n"
            "Tu saldo: **${balance}**\n"
            "Requerido: **${required}**\n\n"
            "Agrega fondos para continuar."
        )
        
        PAYMENT_ERROR = (
            "❌ **Error en Pago**\n\n"
            "{error}\n\n"
            "Intenta con otro método."
        )
        
        TRANSACTION_ERROR = (
            "❌ **Error en Transacción**\n\n"
            "No se pudo procesar.\n"
            "Contacta a soporte."
        )
        
        VIP_ALREADY_ACTIVE = (
            "ℹ️ **Ya tienes VIP activo**\n\n"
            "Expira el: **{expiration}**"
        )
        
        INVALID_AMOUNT = (
            "❌ **Monto inválido**\n\n"
            "Mínimo: **${min_amount}**\n"
            "Máximo: **${max_amount}**"
        )
