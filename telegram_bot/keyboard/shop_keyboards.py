"""
Teclados para la tienda y planes del bot uSipipo.

Organiza los teclados relacionados con:
- Menú principal de la tienda
- Planes VIP y opciones de compra
- Roles premium
- Paquetes de almacenamiento
- Confirmaciones de compra

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class ShopKeyboards:
    """Teclados para la tienda y planes del sistema."""
    
    # ============================================
    # SHOP MENU
    # ============================================
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Teclado del menú principal de la tienda."""
        keyboard = [
            [InlineKeyboardButton("👑 Planes VIP", callback_data="vip_plans")],
            [InlineKeyboardButton("📋 Roles Premium", callback_data="shop_roles")],
            [InlineKeyboardButton("💾 Almacenamiento", callback_data="shop_storage")],
            [InlineKeyboardButton("⭐ Recargar Estrellas", callback_data="deposit_stars")],
            [InlineKeyboardButton("🔙 Volver", callback_data="operations")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def main_menu_command() -> InlineKeyboardMarkup:
        """Teclado del menú principal para comando /shop."""
        keyboard = [
            [InlineKeyboardButton("👑 Planes VIP", callback_data="vip_plans")],
            [InlineKeyboardButton("📋 Roles Premium", callback_data="shop_roles")],
            [InlineKeyboardButton("💾 Almacenamiento", callback_data="shop_storage")],
            [InlineKeyboardButton("⭐ Recargar Estrellas", callback_data="deposit_stars")],
            [InlineKeyboardButton("🔙 Volver", callback_data="operations")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # VIP PLANS
    # ============================================
    
    @staticmethod
    def vip_plans() -> InlineKeyboardMarkup:
        """Teclado para planes VIP."""
        keyboard = [
            [InlineKeyboardButton("1 Mes - 10⭐", callback_data="shop_vip_1month")],
            [InlineKeyboardButton("3 Meses - 27⭐", callback_data="shop_vip_3months")],
            [InlineKeyboardButton("6 Meses - 50⭐", callback_data="shop_vip_6months")],
            [InlineKeyboardButton("12 Meses - 90⭐", callback_data="shop_vip_12months")],
            [InlineKeyboardButton("⭐ Recargar Estrellas", callback_data="deposit_stars")],
            [InlineKeyboardButton("🔙 Volver", callback_data="shop_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # PREMIUM ROLES
    # ============================================
    
    @staticmethod
    def premium_roles() -> InlineKeyboardMarkup:
        """Teclado para roles premium."""
        keyboard = [
            [InlineKeyboardButton("📋 Gestor de Tareas", callback_data="shop_role_task_manager")],
            [InlineKeyboardButton("📣 Anunciante", callback_data="shop_role_announcer")],
            [InlineKeyboardButton("✨ Ambos Roles", callback_data="shop_role_both")],
            [InlineKeyboardButton("🔙 Volver", callback_data="shop_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # STORAGE PLANS
    # ============================================
    
    @staticmethod
    def storage_plans() -> InlineKeyboardMarkup:
        """Teclado para paquetes de almacenamiento."""
        keyboard = [
            [InlineKeyboardButton("+10 GB - 5⭐", callback_data="shop_storage_10gb")],
            [InlineKeyboardButton("+25 GB - 12⭐", callback_data="shop_storage_25gb")],
            [InlineKeyboardButton("+50 GB - 25⭐", callback_data="shop_storage_50gb")],
            [InlineKeyboardButton("+200 GB - 100⭐", callback_data="shop_storage_200gb")],
            [InlineKeyboardButton("🔙 Volver", callback_data="shop_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # PURCHASE CONFIRMATION
    # ============================================
    
    @staticmethod
    def confirm_purchase(product_type: str, product_id: str) -> InlineKeyboardMarkup:
        """Teclado para confirmar compra."""
        keyboard = [
            [
                InlineKeyboardButton("✅ Comprar", callback_data=f"shop_buy_{product_type}_{product_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="shop_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def insufficient_balance() -> InlineKeyboardMarkup:
        """Teclado para balance insuficiente."""
        keyboard = [
            [InlineKeyboardButton("⭐ Recargar Estrellas", callback_data="deposit_stars")],
            [InlineKeyboardButton("🔙 Volver", callback_data="shop_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def purchase_success() -> InlineKeyboardMarkup:
        """Teclado para compra exitosa."""
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="operations")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def purchase_error() -> InlineKeyboardMarkup:
        """Teclado para error en compra."""
        keyboard = [[InlineKeyboardButton("🔙 Reintentar", callback_data="shop_menu")]]
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # NAVIGATION
    # ============================================
    
    @staticmethod
    def back_to_shop() -> InlineKeyboardMarkup:
        """Teclado para volver a la tienda."""
        keyboard = [[InlineKeyboardButton("🔙 Volver a Tienda", callback_data="shop_menu")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_operations() -> InlineKeyboardMarkup:
        """Teclado para volver a operaciones."""
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="operations")]]
        return InlineKeyboardMarkup(keyboard)
