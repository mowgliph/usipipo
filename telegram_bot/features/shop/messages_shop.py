"""
Mensajes para sistema de comercio electrónico de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""


class ShopMessages:
    """Mensajes para sistema de comercio electrónico."""
    
    # ============================================
    # MENU
    # ============================================
    
    class Menu:
        """Mensajes del menú de tienda."""
        
        MAIN = (
            "🛍️ **Tienda uSipipo**\n\n"
            "💰 **Tu Balance:** ${balance:.2f}\n\n"
            "Bienvenido a nuestra tienda premium:\n\n"
            "👑 **Planes VIP** - Acceso exclusivo\n"
            "🎭 **Roles Premium** - Funciones avanzadas\n"
            "💾 **Almacenamiento** - Espacio extra\n\n"
            "💡 *Mejora tu experiencia con nuestros productos*"
        )
    
    # ============================================
    # VIP PLANS
    # ============================================
    
    class VipPlans:
        """Mensajes de planes VIP."""
        
        HEADER = (
            "👑 **Planes VIP**\n\n"
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
        
        BENEFITS = (
            "🎁 **Beneficios VIP**\n\n"
            "🌟 **Plan Básico:**\n"
            "• Servidores básicos\n"
            "• Sin límites de velocidad\n"
            "• Backup automático\n"
            "• Soporte prioritario\n\n"
            "💎 **Plan Premium:**\n"
            "• Todos los servidores\n"
            "• Soporte 24/7\n"
            "• Backup en la nube\n"
            "• Prioridad máxima\n\n"
            "💎 **Plan Elite:**\n"
            "• Cuenta personal dedicada\n"
            "• Acceso beta features\n"
            "• Eventos exclusivos\n"
            "• Regalos mensuales"
        )
    
    # ============================================
    # PREMIUM ROLES
    # ============================================
    
    class PremiumRoles:
        """Mensajes de roles premium."""
        
        HEADER = (
            "🎭 **Roles Premium**\n\n"
            "Desbloquea funciones avanzadas y herramientas profesionales:\n\n"
            "📋 **Gestor de Tareas** - $29.99/mes\n"
            "• Panel de gestión completa\n"
            "• Creación y asignación de tareas\n"
            "• Estadísticas avanzadas\n\n"
            "📢 **Anunciante** - $49.99/mes\n"
            "• Sistema de anuncios masivos\n"
            "• Segmentación avanzada\n"
            "• Analytics completo\n\n"
            "💡 *Potencia tus capacidades con roles profesionales*"
        )
        
        TASK_MANAGER = (
            "📋 **Gestor de Tareas**\n\n"
            "🎯 **Características:**\n"
            "• Panel administrativo intuitivo\n"
            "• Creación de tareas personalizadas\n"
            "• Asignación automática y manual\n"
            "• Seguimiento en tiempo real\n"
            "• Estadísticas detalladas\n\n"
            "🎁 **Beneficios:**\n"
            "• Soporte prioritario\n"
            "• Acceso a funciones avanzadas\n"
            "• Integración con otros sistemas\n\n"
            "💡 *Ideal para gestión de equipos y proyectos*"
        )
        
        ANNOUNCER = (
            "📢 **Anunciante**\n\n"
            "🎯 **Características:**\n"
            "• Creación de anuncios masivos\n"
            "• Segmentación avanzada de usuarios\n"
            "• Programación de campañas\n"
            "• Analytics y métricas detalladas\n"
            "• A/B testing integrado\n\n"
            "🎁 **Beneficios:**\n"
            "• Alcance ilimitado\n"
            "• Soporte dedicado\n"
            "• Herramientas profesionales\n"
            "• API de acceso\n\n"
            "💡 *Perfecto para marketing y comunicación*"
        )
    
    # ============================================
    # STORAGE PLANS
    # ============================================
    
    class StoragePlans:
        """Mensajes de planes de almacenamiento."""
        
        HEADER = (
            "💾 **Planes de Almacenamiento**\n\n"
            "Amplía tu espacio de almacenamiento con planes flexibles:\n\n"
            "📦 **100 GB - $4.99/mes**\n"
            "• Espacio adicional para datos\n"
            "• Compatible entre llaves\n"
            "• Backup automático\n\n"
            "• Seguridad mejorada\n\n"
            "📦 **500 GB - $19.99/mes**\n"
            "• Gran capacidad de almacenamiento\n"
            "• Ideal para empresas\n"
            "• Backup empresarial\n"
            "• Seguridad enterprise\n\n"
            "📦 **1 TB - $34.99/mes**\n"
            "• Capacidad máxima\n"
            "• Sin restricciones\n"
            "• Seguridad total\n"
            "• Soporte dedicado\n\n"
            "💡 *Elige el plan que se adapte a tus necesidades*"
        )
        
        PLAN_100GB = (
            "📦 **100 GB Adicionales**\n\n"
            "💰 **Precio:** $4.99/mes\n"
            "🎯 **Características:**\n"
            "• 100 GB de espacio extra\n"
            "• Compartible entre todas tus llaves\n"
            "• Backup automático diario\n"
            "• Encriptación de extremo a extremo\n\n"
            "🎁 **Beneficios:**\n"
            "• Más espacio para archivos\n"
            "• Flexibilidad total\n"
            "• Seguridad mejorada\n"
            "• Acceso desde cualquier dispositivo"
        )
        
        PLAN_500GB = (
            "📦 **500 GB Adicionales**\n\n"
            "💰 **Precio:** $19.99/mes\n"
            "🎯 **Características:**\n"
            "• 500 GB de espacio premium\n"
            "• Compartible entre todas tus llaves\n"
            "• Backup en tiempo real\n"
            "• Encriptación militar\n"
            "• Recuperación de desastres\n\n"
            "🎁 **Beneficios:**\n"
            "• Gran capacidad para empresas\n"
            "• Backup empresarial\n"
            "• Seguridad enterprise\n"
            "• Soporte prioritario"
        )
        
        PLAN_1TB = (
            "📦 **1 TB Adicional**\n\n"
            "💰 **Precio:** $34.99/mes\n"
            "🎯 **Características:**\n"
            "• 1 TB de espacio ilimitado\n"
            "• Compartible entre todas tus llaves\n"
            "• Backup continuo\n"
            "• Encriptación cuántica\n"
            "• Redundancia geográfica\n\n"
            "🎁 **Beneficios:**\n"
            "• Capacidad máxima\n"
            "• Sin restricciones\n"
            "• Seguridad total\n"
            "• Soporte dedicado 24/7"
        )
    
    # ============================================
    # PRODUCTS
    # ============================================
    
    class Products:
        """Mensajes de productos."""
        
        DETAILS = (
            "🛍️ **{name}**\n\n"
            "💰 **Precio:** ${price}/mes\n"
            "📝 **Descripción:** {description}\n\n"
            "🎯 **Características:**\n{features}\n\n"
            "🎁 **Beneficios Exclusivos:**\n{benefits}\n\n"
            "💡 *Mejora tu experiencia con este producto*"
        )
        
        COMPARISON = (
            "📊 **Comparación de Productos**\n\n"
            "| Producto | Precio | Características Principales |\n"
            "|----------|--------|------------------------|\n"
            "| VIP Básico | $9.99 | Llaves ilimitadas, 100 GB |\n"
            "| VIP Premium | $19.99 | 500 GB, servidores dedicados |\n"
            "| VIP Elite | $39.99 | Datos ilimitados, soporte 24/7 |\n"
            "| Gestor Tareas | $29.99 | Panel completo, estadísticas |\n"
            "| Anunciante | $49.99 | Anuncios masivos, analytics |\n"
            "| 100 GB | $4.99 | Espacio extra, backup |\n"
            "| 500 GB | $19.99 | Almacenamiento enterprise |\n"
            "| 1 TB | $34.99 | Capacidad máxima |\n\n"
            "💡 *Compara y elige el producto ideal para ti*"
        )
    
    # ============================================
    # PAYMENT
    # ============================================
    
    class Payment:
        """Mensajes de pago."""
        
        METHODS = (
            "💳 **Métodos de Pago**\n\n"
            "Producto: **{product_name}**\n"
            "Total: **${price}**\n\n"
            "Selecciona tu método de pago preferido:\n\n"
            "💳 **Balance de Cuenta**\n"
            "• Usa tus estrellas disponibles\n"
            "• Procesamiento instantáneo\n"
            "• Sin comisiones adicionales\n\n"
            "🏦 **Transferencia Bancaria**\n"
            "• Transferencia directa\n"
            "• Seguro y confiable\n"
            "• 1-2 días hábiles de procesamiento\n\n"
            "💳 **Tarjeta de Crédito/Débito**\n"
            "• Visa, Mastercard, Amex\n"
            "• Procesamiento seguro\n"
            "• Cargo inmediato\n\n"
            "₿ **Criptomonedas**\n"
            "• Bitcoin, Ethereum, USDT\n"
            "• Pagos anónimos\n"
            "• Confirmación rápida"
        )
        
        CONFIRMATION = (
            "🔒 **Confirmar Compra**\n\n"
            "🛍️ **Producto:** {product_name}\n"
            "💰 **Total:** ${price}\n"
            "💳 **Método:** {payment_method}\n\n"
            "📋 **Detalles del pedido:**\n"
            "• Producto digital\n"
            "• Activación inmediata\n"
            "• Soporte incluido\n"
            "• Sin cargos ocultos\n\n"
            "💡 *Revisa los detalles y confirma tu compra*"
        )
        
        SUCCESS = (
            "🎉 **¡Compra Exitosa!**\n\n"
            "Tu pedido ha sido procesado correctamente.\n\n"
            "🛍️ **Producto:** {product_name}\n"
            "💰 **Pagado:** ${price}\n"
            "💳 **Método:** {payment_method}\n\n"
            "🎁 **Tu producto está activo ahora**\n\n"
            "💡 *Disfruta de tu nueva adquisición*"
        )
        
        FAILED = (
            "❌ **Compra Fallida**\n\n"
            "No pude procesar tu compra.\n\n"
            "💡 *Por favor, intenta más tarde o contacta soporte*"
        )
        
        PROCESSING = (
            "⏳ **Procesando Pago**\n\n"
            "Tu compra está siendo procesada.\n\n"
            "💡 *Por favor, espera un momento...*"
        )
    
    # ============================================
    # HISTORY
    # ============================================
    
    class History:
        """Mensajes de historial."""
        
        PURCHASES = (
            "📋 **Historial de Compras**\n\n"
            "Usuario: {user_id}\n"
            "Total de compras: {count}\n\n"
            "📊 *Aquí se mostrará tu historial completo de compras*"
        )
        
        PURCHASE_DETAIL = (
            "📋 **Detalle de Compra**\n\n"
            "🆔 **ID del Pedido:** {order_id}\n"
            "📅 **Fecha:** {date}\n"
            "🛍️ **Producto:** {product_name}\n"
            "💰 **Precio:** ${price}\n"
            "💳 **Método de Pago:** {payment_method}\n"
            "🟢 **Estado:** {status}\n"
            "⏰ **Activación:** {activation_date}\n\n"
            "💡 *Esta compra está {status}*"
        )
        
        NO_PURCHASES = (
            "📭 **Sin Compras**\n\n"
            "No tienes compras registradas.\n\n"
            "💡 *Realiza tu primera compra para ver el historial*"
        )
    
    # ============================================
    # ERRORS
    # ============================================
    
    class Error:
        """Mensajes de error."""
        
        SYSTEM_ERROR = (
            "❌ **Error del Sistema**\n\n"
            "No pude procesar tu solicitud en la tienda.\n\n"
            "Por favor, intenta más tarde o contacta soporte."
        )
        
        PRODUCT_NOT_FOUND = (
            "❌ **Producto No Encontrado**\n\n"
            "El producto seleccionado no está disponible.\n\n"
            "💡 *Por favor, selecciona un producto válido*"
        )
        
        INSUFFICIENT_BALANCE = (
            "💸 **Balance Insuficiente**\n\n"
            "No tienes suficientes fondos para esta compra.\n\n"
            "💡 *Recarga tu balance para continuar*"
        )
        
        PAYMENT_ERROR = (
            "❌ **Error en el Pago**\n\n"
            "No pude procesar tu pago.\n\n"
            "Error: {error}\n\n"
            "💡 *Por favor, verifica tu método e intenta nuevamente*"
        )
        
        PURCHASE_ERROR = (
            "❌ **Error en la Compra**\n\n"
            "No pude completar tu compra.\n\n"
            "💡 *Por favor, intenta más tarde o contacta soporte*"
        )
    
    # ============================================
    # SUCCESS
    # ============================================
    
    class Success:
        """Mensajes de éxito."""
        
        PURCHASE_COMPLETE = (
            "✅ **Compra Completada**\n\n"
            "Tu pedido ha sido procesado exitosamente.\n\n"
            "🎁 *Tu producto está activo ahora*"
        )
        
        PRODUCT_ACTIVATED = (
            "✅ **Producto Activado**\n\n"
            "Tu producto ha sido activado correctamente.\n\n"
            "🎁 *Disfruta de todas las funciones*"
        )
        
        PAYMENT_PROCESSED = (
            "✅ **Pago Procesado**\n\n"
            "Tu pago ha sido procesado correctamente.\n\n"
            "💰 *Fondos descontados de tu balance*"
        )
