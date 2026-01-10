"""
Mensajes para sistema de procesamiento de pagos de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""


class PaymentsMessages:
    """Mensajes para sistema de pagos."""
    
    # ============================================
    # MENU
    # ============================================
    
    class Menu:
        """Mensajes del menú de pagos."""
        
        MAIN = (
            "💳 **Centro de Pagos**\n\n"
            "💰 **Tu Balance Actual:** ${balance:.2f}\n\n"
            "Gestiona tus fondos y realiza transacciones seguras:\n\n"
            "💎 **Depositar Fondos**\n"
            "📊 **Historial de Transacciones**\n"
            "💳 **Estado de Balance**\n\n"
            "💡 *Todos los pagos son seguros y procesados instantáneamente*"
        )
    
    # ============================================
    # DEPOSIT
    # ============================================
    
    class Deposit:
        """Mensajes de depósitos."""
        
        AMOUNT_OPTIONS = (
            "💳 **Selecciona Monto a Depositar**\n\n"
            "Elige una de las siguientes opciones:\n\n"
            "💰 **$5** - Rápido y económico\n"
            "💰 **$10** - Balance estándar\n"
            "💰 **$25** - Para usuarios activos\n"
            "💰 **$50** - Para usuarios premium\n"
            "💰 **$100** - Para empresas\n\n"
            "💡 *O ingresa un monto personalizado*"
        )
        
        CUSTOM_AMOUNT = (
            "💳 **Monto Personalizado**\n\n"
            "Ingresa la cantidad que deseas depositar.\n\n"
            "💡 *Mínimo: $1, Máximo: $10,000*\n"
        )
        
        INVALID_AMOUNT = (
            "❌ **Monto Inválido**\n\n"
            "El monto ingresado no es válido.\n\n"
            "💡 *Por favor, ingresa un número positivo entre 1 y 10,000*"
        )
        
        AMOUNT_TOO_HIGH = (
            "⚠️ **Monto Demasiado Alto**\n\n"
            "El monto máximo permitido es **${max_amount}**.\n\n"
            "💡 *Por seguridad, los depósitos están limitados*\n"
        )
        
        SUCCESS = (
            "✅ **Depósito Exitoso**\n\n"
            "Tu depósito ha sido procesado correctamente.\n\n"
            "💰 **Monto Depositado:** ${amount}\n"
            "💳 **Nuevo Balance:** ${new_balance}\n\n"
            "💡 *Los fondos están disponibles para usar inmediatamente*"
        )
        
        FAILED = (
            "❌ **Depósito Fallido**\n\n"
            "No pude procesar tu depósito.\n\n"
            "💡 *Por favor, intenta más tarde o contacta soporte*"
        )
    
    # ============================================
    # PAYMENT
    # ============================================
    
    class Payment:
        """Mensajes de pago."""
        
        METHODS = (
            "💳 **Métodos de Pago**\n\n"
            "Monto a depositar: **${amount}**\n\n"
            "Selecciona tu método de pago preferido:\n\n"
            "💳 **Balance de Cuenta**\n"
            "• Usa tus estrellas disponibles\n"
            "• Procesamiento instantáneo\n"
            "• Sin comisiones adicionales\n"
            "• Recomendado para montos pequeños\n\n"
            "💳 **Tarjeta de Crédito/Débito**\n"
            "• Visa, Mastercard, Amex\n"
            "• Procesamiento seguro\n"
            "• Cargo inmediato\n"
            "• Protección contra fraudes\n"
            "• Ideal para montos grandes\n\n"
            "🏦 **Transferencia Bancaria**\n"
            "• Transferencia directa\n"
            "• Seguro y confiable\n"
            "• 1-2 días hábiles de procesamiento\n"
            "• Sin comisiones bancarias\n"
            "• Ideal para empresas\n\n"
            "₿ **Criptomonedas**\n"
            "• Bitcoin, Ethereum, USDT\n"
            "• Pagos anónimos y privados\n"
            "• Confirmación rápida\n"
            "• Comisiones bajas\n"
            "• Ideal para privacidad\n\n"
            "💡 *Todos los métodos son seguros y confiables*"
        )
        
        CONFIRMATION = (
            "🔒 **Confirmar Depósito**\n\n"
            "👤 **Usuario:** {user_id}\n"
            "💰 **Monto:** ${amount}\n"
            "💳 **Método:** {payment_method}\n\n"
            "📋 **Detalles de la transacción:**\n"
            "• Depósito de fondos digitales\n"
            "• Procesamiento seguro\n"
            "• Activación inmediata\n"
            "• Sin cargos ocultos\n"
            "• Soporte incluido\n\n"
            "💡 *Revisa los detalles y confirma tu depósito*"
        )
        
        SUCCESS = (
            "✅ **Depósito Procesado**\n\n"
            "Tu depósito ha sido procesado correctamente.\n\n"
            "💰 **Monto Depositado:** ${amount}\n"
            "💳 **Método:** {payment_method}\n"
            "👤 **Usuario:** {user_id}\n\n"
            "💎 *Tus fondos están disponibles ahora*"
        )
        
        FAILED = (
            "❌ **Depósito Fallido**\n\n"
            "No pude procesar tu depósito.\n\n"
            "💡 *Por favor, intenta más tarde o contacta soporte*"
        )
        
        PROCESSING = (
            "⏳ **Procesando Pago**\n\n"
            "Tu depósito está siendo procesado.\n\n"
            "💡 *Por favor, espera un momento...*"
        )
        
        INSUFFICIENT_FUNDS = (
            "💸 **Fondos Insuficientes**\n\n"
            "No tienes suficientes fondos para esta operación.\n\n"
            "💡 *Recarga tu balance para continuar*"
        )
        
        INVALID_METHOD = (
            "❌ **Método No Válido**\n\n"
            "El método de pago seleccionado no está disponible.\n\n"
            "💡 *Por favor, selecciona un método válido*"
        )
    
    # ============================================
    # BALANCE
    # ============================================
    
    class Balance:
        """Mensajes de balance."""
        
        STATUS = (
            "💰 **Estado de Balance**\n\n"
            "💳 **Balance Actual:** ${balance:.2f} estrellas\n"
            "💸 **Total Depositado:** ${total_deposited:.2f}\n"
            "💸 **Total Gastado:** ${total_spent:.2f}\n"
            "💎 **Disponible:** ${available:.2f}\n\n"
            "💡 *Tu balance está listo para usar*"
        )
        
        UPDATED = (
            "✅ **Balance Actualizado**\n\n"
            "Tu balance ha sido actualizado.\n\n"
            "💰 **Nuevo Balance:** ${new_balance:.2f}\n\n"
            "💎 *Los fondos están disponibles ahora*"
        )
        
        INSUFFICIENT = (
            "💸 **Balance Insuficiente**\n\n"
            "No tienes suficientes fondos para esta operación.\n\n"
            "💡 *Recarga tu balance para continuar*"
        )
        
        TRANSACTION_LIMIT = (
            "⚠️ **Límite de Transacción**\n\n"
            "Has alcanzado el límite de transacción.\n\n"
            "💡 *Por seguridad, los depósitos están limitados*\n"
        )
    
    # ============================================
    # HISTORY
    # ============================================
    
    class History:
        """Mensajes de historial."""
        
        PAYMENTS = (
            "📋 **Historial de Pagos**\n\n"
            "Usuario: {user_id}\n"
            "Total de transacciones: {count}\n\n"
            "📊 *Aquí se mostrará tu historial completo de pagos*"
        )
        
        TRANSACTION_DETAIL = (
            "📋 **Detalle de Transacción**\n\n"
            "🆔 **ID:** {transaction_id}\n"
            "📅 **Fecha:** {date}\n"
            "💰 **Monto:** ${amount:.2f}\n"
            "💳 **Método:** {method}\n"
            "🟢 **Estado:** {status}\n"
            "👤 **Usuario:** {user_id}\n"
            "📝 **Descripción:** {description}\n\n"
            "💡 *Esta transacción está {status}*"
        )
        
        NO_TRANSACTIONS = (
            "📭 **Sin Transacciones**\n\n"
            "No tienes transacciones registradas.\n\n"
            "💡 *Realiza tu primer depósito para ver el historial*"
        )
        
        FILTER_RESULTS = (
            "📋 **Resultados Filtrados**\n\n"
            "Transacciones encontradas: {count}\n\n"
            "📊 *Aquí se mostrarán las transacciones filtradas*"
        )
        
        DATE_RANGE = (
            "📅 **Rango de Fechas**\n\n"
            "Transacciones del {start_date} al {end_date}\n\n"
            "📊 *Aquí se mostrarán las transacciones en el rango seleccionado*"
        )
    
    # ============================================
    # ERRORS
    # ============================================
    
    class Error:
        """Mensajes de error."""
        
        SYSTEM_ERROR = (
            "❌ **Error del Sistema**\n\n"
            "No pude procesar tu solicitud de pago.\n\n"
            "Por favor, intenta más tarde o contacta soporte."
        )
        
        INVALID_AMOUNT = (
            "❌ **Monto Inválido**\n\n"
            "El monto especificado no es válido.\n\n"
            "💡 *Por favor, ingresa un monto válido*"
        )
        
        PAYMENT_ERROR = (
            "❌ **Error en el Pago**\n\n"
            "No pude procesar tu pago.\n\n"
            "Error: {error}\n\n"
            "💡 *Por favor, intenta más tarde o contacta soporte*"
        )
        
        TRANSACTION_ERROR = (
            "❌ **Error en Transacción**\n\n"
            "No pude completar la transacción.\n\n"
            "Error: {error}\n\n"
            "💡 *Por favor, intenta más tarde o contacta soporte*"
        )
        
        INSUFFICIENT_BALANCE = (
            "💸 **Balance Insuficiente**\n\n"
            "No tienes suficientes fondos para esta operación.\n\n"
            "💡 *Recarga tu balance para continuar*"
        )
        
        METHOD_NOT_AVAILABLE = (
            "❌ **Método No Disponible**\n\n"
            "El método de pago seleccionado no está disponible temporalmente.\n\n"
            "💡 *Por favor, intenta más tarde o selecciona otro método*"
        )
    
    # ============================================
    # SUCCESS
    # ============================================
    
    class Success:
        """Mensajes de éxito."""
        
        DEPOSIT_COMPLETE = (
            "✅ **Depósito Completado**\n\n"
            "Tu depósito ha sido procesado exitosamente.\n\n"
            "💎 *Tus fondos están disponibles ahora*"
        )
        
        PAYMENT_PROCESSED = (
            "✅ **Pago Procesado**\n\n"
            "Tu pago ha sido procesado correctamente.\n\n"
            "💎 *Los fondos han sido acreditados*"
        )
        
        TRANSACTION_COMPLETE = (
            "✅ **Transacción Completada**\n\n"
            "La transacción ha sido completada exitosamente.\n\n"
            "💎 *La operación ha sido registrada*"
        )
        
        BALANCE_UPDATED = (
            "✅ **Balance Actualizado**\n\n"
            "Tu balance ha sido actualizado correctamente.\n\n"
            "💎 *Los fondos están disponibles ahora*"
        )
        
        REFERRAL_EARNED = (
            "⭐ **Ganancia de Referido**\n\n"
            "Has ganado {earnings} estrellas por un nuevo referido.\n\n"
            "💰 **Balance Actualizado:** {balance}\n\n"
            "💎 *¡Sigue compartiendo tu enlace!*"
        )
