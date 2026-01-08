"""
Mensajes para la tienda y planes del bot uSipipo.

Organiza los mensajes relacionados con:
- Planes VIP y suscripciones
- Roles premium (Gestor de Tareas, Anunciante)
- Paquetes de almacenamiento
- Confirmaciones de compra

Author: uSipipo Team
Version: 1.0.0
"""


class ShopMessages:
    """Mensajes para la tienda y planes del sistema."""
    
    # ============================================
    # SHOP MENU
    # ============================================
    
    class Menu:
        """Mensajes del menú principal de la tienda."""
        
        HEADER = "🛒 **SHOP uSipipo**"
        
        BALANCE = "Tu Balance: ⭐ {balance}"
        
        CATEGORIES = "Selecciona una categoría:"
        
        VIP_DESCRIPTION = "👑 **Planes VIP**\n   Obtén acceso a más claves y GB"
        
        ROLES_DESCRIPTION = "📋 **Roles Premium**\n   Sé Gestor de Tareas o Anunciante"
        
        STORAGE_DESCRIPTION = "💾 **Almacenamiento Adicional**\n   Amplía tus GB de conexión"
        
        RECHARGE_DESCRIPTION = "⭐ **Recargar Estrellas**\n   Compra más estrellas con Telegram Stars"
    
    # ============================================
    # VIP PLANS
    # ============================================
    
    class VIPPlans:
        """Mensajes para planes VIP."""
        
        HEADER = "👑 **Planes VIP**\n\nDisfruta de beneficios exclusivos con nuestros planes VIP:"
        
        PLAN_1MONTH = "🟢 **Plan VIP 1 Mes** - 10 ⭐\n   • 10 claves VPN simultáneas\n   • 50 GB de datos por clave\n   • Soporte prioritario\n   • Sin anuncios"
        
        PLAN_3MONTHS = "🟡 **Plan VIP 3 Meses** - 27 ⭐\n   • 10 claves VPN simultáneas\n   • 50 GB de datos por clave\n   • Soporte prioritario\n   • Sin anuncios\n   • Ahorra 3 ⭐"
        
        PLAN_6MONTHS = "🔵 **Plan VIP 6 Meses** - 50 ⭐\n   • 10 claves VPN simultáneas\n   • 50 GB de datos por clave\n   • Soporte prioritario\n   • Sin anuncios\n   • Ahorra 10 ⭐"
        
        PLAN_12MONTHS = "🔴 **Plan VIP 12 Meses** - 90 ⭐\n   • 10 claves VPN simultáneas\n   • 50 GB de datos por clave\n   • Soporte prioritario\n   • Sin anuncios\n   • Ahorra 30 ⭐"
    
    # ============================================
    # PREMIUM ROLES
    # ============================================
    
    class PremiumRoles:
        """Mensajes para roles premium."""
        
        HEADER = "📋 **Roles Premium**\n\nObtén roles especiales para funcionalidades exclusivas:"
        
        TASK_MANAGER = "📋 **GESTOR DE TAREAS** - 50 ⭐ / mes\n   Crea y gestiona tareas para otros usuarios\n   • Crear tareas públicas/privadas\n   • Ver participación de usuarios\n   • Recompensas por tareas completadas\n   • Estadísticas detalladas\n   \n   Planes: 1 mes | 3 meses | 6 meses | 1 año"
        
        ANNOUNCER = "📣 **ANUNCIANTE** - 80 ⭐ / mes\n   Envía anuncios y promociones a otros usuarios\n   • Crear campañas de anuncios\n   • Targeting por región/tipo de usuario\n   • Estadísticas de visualización\n   • Hasta 100 anuncios por mes\n   \n   Planes: 1 mes | 3 meses | 6 meses | 1 año"
        
        BOTH_ROLES = "✨ **Ambos Roles** - 120 ⭐ / mes\n   Obtén acceso a ambos roles premium\n   • Todas las funciones de Gestor de Tareas\n   • Todas las funciones de Anunciante\n   • Descuento especial en paquetes\n   \n   Planes: 1 mes | 3 meses | 6 meses | 1 año"
    
    # ============================================
    # STORAGE PLANS
    # ============================================
    
    class StoragePlans:
        """Mensajes para paquetes de almacenamiento."""
        
        HEADER = "💾 **Paquetes de Almacenamiento**\n\nAmplía tu límite de datos mensuales:"
        
        BASIC = "🟢 **Paquete Básico** - 5 ⭐\n   • +10 GB de datos\n   • Válido por 30 días\n   • Aplicable a todas tus claves"
        
        STANDARD = "🟡 **Paquete Estándar** - 12 ⭐\n   • +25 GB de datos\n   • Válido por 30 días\n   • Aplicable a todas tus claves\n   • Ahorra 3 ⭐ vs Paquete Básico x3"
        
        PREMIUM = "🔵 **Paquete Premium** - 25 ⭐\n   • +50 GB de datos\n   • Válido por 30 días\n   • Aplicable a todas tus claves\n   • Ahorra 5 ⭐ vs Paquete Estándar x2"
        
        UNLIMITED = "🔴 **Paquete Ilimitado** - 100 ⭐\n   • +200 GB de datos\n   • Válido por 30 días\n   • Aplicable a todas tus claves\n   • Mejor ahorro"
    
    # ============================================
    # PURCHASE CONFIRMATION
    # ============================================
    
    class Purchase:
        """Mensajes para confirmación y ejecución de compras."""
        
        CONFIRM_HEADER = "✅ **Confirmar Compra**\n\nProducto: {product_name}\nCosto: ⭐ {cost}\n\n¿Deseas proceder con la compra?"
        
        SUCCESS_HEADER = "✅ **Compra Exitosa**\n\nProducto: {product_name}\nCosto: ⭐ {cost}\nBalance anterior: ⭐ {old_balance}\nBalance nuevo: ⭐ {new_balance}\n\n{additional_message}"
        
        ERROR_HEADER = "❌ **Error en la Compra**\n\n{error_message}"
        
        INSUFFICIENT_BALANCE = "❌ **Balance Insuficiente**\n\nBalance actual: ⭐ {current_balance}\nCosto del producto: ⭐ {cost}\nNecesitas: ⭐ {needed} más\n\nRecargar estrellas con el botón de abajo."
    
    # ============================================
    # BUTTONS
    # ============================================
    
    class Buttons:
        """Etiquetas para botones de la tienda."""
        
        BUY = "✅ Comprar"
        CANCEL = "❌ Cancelar"
        BACK = "🔙 Volver"
        CONFIRM = "✅ Confirmar"
        RECHARGE = "⭐ Recargar Estrellas"
