"""
Teclados para sistema de comercio electrónico de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class ShopKeyboards:
    """Teclados para sistema de comercio electrónico."""

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú principal de la tienda.
        
        Returns:
            InlineKeyboardMarkup: Teclado del menú principal
        """
        keyboard = [
            [
                InlineKeyboardButton("👑 Planes VIP", callback_data="shop_vip"),
                InlineKeyboardButton("🎭 Roles Premium", callback_data="shop_roles")
            ],
            [
                InlineKeyboardButton("💾 Almacenamiento", callback_data="shop_storage"),
                InlineKeyboardButton("📊 Historial", callback_data="shop_history")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def vip_plans() -> InlineKeyboardMarkup:
        """
        Teclado de planes VIP.
        
        Returns:
            InlineKeyboardMarkup: Teclado de planes VIP
        """
        keyboard = [
            [
                InlineKeyboardButton("🌟 Plan Básico - $9.99", callback_data="shop_details_vip_basic"),
                InlineKeyboardButton("💎 Plan Premium - $19.99", callback_data="shop_details_vip_premium")
            ],
            [
                InlineKeyboardButton("💎 Plan Elite - $39.99", callback_data="shop_details_vip_elite"),
                InlineKeyboardButton("🎁 Ver Beneficios", callback_data="shop_vip_benefits")
            ],
            [
                InlineKeyboardButton("📊 Comparar Planes", callback_data="shop_compare_vip"),
                InlineKeyboardButton("🔙 Volver", callback_data="shop_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def premium_roles() -> InlineKeyboardMarkup:
        """
        Teclado de roles premium.
        
        Returns:
            InlineKeyboardMarkup: Teclado de roles premium
        """
        keyboard = [
            [
                InlineKeyboardButton("📋 Gestor de Tareas - $29.99", callback_data="shop_details_role_task_manager"),
                InlineKeyboardButton("📢 Anunciante - $49.99", callback_data="shop_details_role_announcer")
            ],
            [
                InlineKeyboardButton("🎯 Comparar Roles", callback_data="shop_compare_roles"),
                InlineKeyboardButton("🎁 Ver Beneficios", callback_data="shop_roles_benefits")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="shop_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def storage_plans() -> InlineKeyboardMarkup:
        """
        Teclado de planes de almacenamiento.
        
        Returns:
            InlineKeyboardMarkup: Teclado de planes de almacenamiento
        """
        keyboard = [
            [
                InlineKeyboardButton("📦 100 GB - $4.99", callback_data="shop_details_storage_100gb"),
                InlineKeyboardButton("📦 500 GB - $19.99", callback_data="shop_details_storage_500gb")
            ],
            [
                InlineKeyboardButton("📦 1 TB - $34.99", callback_data="shop_details_storage_1tb"),
                InlineKeyboardButton("📊 Comparar Planes", callback_data="shop_compare_storage")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="shop_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def product_actions(product_type: str, product_id: str, price: float) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para un producto específico.
        
        Args:
            product_type: Tipo de producto
            product_id: ID del producto
            price: Precio del producto
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = [
            [
                InlineKeyboardButton(f"💳 Comprar ${price:.2f}", callback_data=f"shop_payment_balance_{product_type}_{product_id}"),
                InlineKeyboardButton("🎁 Ver Beneficios", callback_data=f"shop_benefits_{product_type}_{product_id}")
            ],
            [
                InlineKeyboardButton("📊 Comparar", callback_data=f"shop_compare_{product_type}_{product_id}"),
                InlineKeyboardButton("📋 Detalles", callback_data=f"shop_details_{product_type}_{product_id}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="shop_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def payment_methods(product_type: str, product_id: str, price: float) -> InlineKeyboardMarkup:
        """
        Teclado de métodos de pago.
        
        Args:
            product_type: Tipo de producto
            product_id: ID del producto
            price: Precio del producto
            
        Returns:
            InlineKeyboardMarkup: Teclado de métodos de pago
        """
        keyboard = [
            [
                InlineKeyboardButton("💳 Balance de Cuenta", callback_data=f"shop_confirm_balance_{product_type}_{product_id}"),
                InlineKeyboardButton("🏦 Transferencia Bancaria", callback_data=f"shop_confirm_transfer_{product_type}_{product_id}")
            ],
            [
                InlineKeyboardButton("💳 Tarjeta de Crédito", callback_data=f"shop_confirm_card_{product_type}_{product_id}"),
                InlineKeyboardButton("₿ Criptomonedas", callback_data=f"shop_confirm_crypto_{product_type}_{product_id}")
            ],
            [
                InlineKeyboardButton("🔙 Cancelar", callback_data="shop_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirm_purchase(product_type: str, product_id: str, payment_method: str) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación de compra.
        
        Args:
            product_type: Tipo de producto
            product_id: ID del producto
            payment_method: Método de pago
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar Compra", callback_data=f"shop_buy_{payment_method}_{product_type}_{product_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="shop_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def purchase_success() -> InlineKeyboardMarkup:
        """
        Teclado para compra exitosa.
        
        Returns:
            InlineKeyboardMarkup: Teclado de compra exitosa
        """
        keyboard = [
            [
                InlineKeyboardButton("🎁 Ver Mis Productos", callback_data="shop_my_products"),
                InlineKeyboardButton("📊 Historial", callback_data="shop_history")
            ],
            [
                InlineKeyboardButton("🔙 Volver a Tienda", callback_data="shop_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_shop() -> InlineKeyboardMarkup:
        """
        Teclado para volver a la tienda.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver a Tienda", callback_data="shop_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_operations() -> InlineKeyboardMarkup:
        """
        Teclado para volver a operaciones.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno a operaciones
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver a Operaciones", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def comparison_table(category: str = "all") -> InlineKeyboardMarkup:
        """
        Teclado de tabla de comparación.
        
        Args:
            category: Categoría a comparar
            
        Returns:
            InlineKeyboardMarkup: Teclado de comparación
        """
        keyboard = []
        
        if category == "vip":
            keyboard.append([
                InlineKeyboardButton("📊 Comparar VIP", callback_data="shop_compare_vip_full"),
                InlineKeyboardButton("🎁 Beneficios VIP", callback_data="shop_vip_benefits")
            ])
        elif category == "roles":
            keyboard.append([
                InlineKeyboardButton("📊 Comparar Roles", callback_data="shop_compare_roles_full"),
                InlineKeyboardButton("🎁 Beneficios Roles", callback_data="shop_roles_benefits")
            ])
        elif category == "storage":
            keyboard.append([
                InlineKeyboardButton("📊 Comparar Almacenamiento", callback_data="shop_compare_storage_full"),
                InlineKeyboardButton("🎁 Beneficios Storage", callback_data="shop_storage_benefits")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("📊 Comparar Todo", callback_data="shop_compare_all"),
                InlineKeyboardButton("🎁 Todos los Beneficios", callback_data="shop_all_benefits")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="shop_back")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def benefits_preview(category: str = "all") -> InlineKeyboardMarkup:
        """
        Teclado de vista previa de beneficios.
        
        Args:
            category: Categoría de beneficios
            
        Returns:
            InlineKeyboardMarkup: Teclado de vista previa
        """
        keyboard = []
        
        if category == "vip":
            keyboard.append([
                InlineKeyboardButton("🌟 Beneficios Básico", callback_data="shop_benefits_vip_basic"),
                InlineKeyboardButton("💎 Beneficios Premium", callback_data="shop_benefits_vip_premium")
            ])
            keyboard.append([
                InlineKeyboardButton("💎 Beneficios Elite", callback_data="shop_benefits_vip_elite")
            ])
        elif category == "roles":
            keyboard.append([
                InlineKeyboardButton("📋 Beneficios Gestor", callback_data="shop_benefits_role_task_manager"),
                InlineKeyboardButton("📢 Beneficios Anunciante", callback_data="shop_benefits_role_announcer")
            ])
        elif category == "storage":
            keyboard.append([
                InlineKeyboardButton("📦 Beneficios 100GB", callback_data="shop_benefits_storage_100gb"),
                InlineKeyboardButton("📦 Beneficios 500GB", callback_data="shop_benefits_storage_500gb")
            ])
            keyboard.append([
                InlineKeyboardButton("📦 Beneficios 1TB", callback_data="shop_benefits_storage_1tb")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("👑 Beneficios VIP", callback_data="shop_benefits_vip"),
                InlineKeyboardButton("🎭 Beneficios Roles", callback_data="shop_benefits_roles")
            ])
            keyboard.append([
                InlineKeyboardButton("💾 Beneficios Storage", callback_data="shop_benefits_storage"),
                InlineKeyboardButton("🎁 Todos los Beneficios", callback_data="shop_all_benefits")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="shop_back")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def my_products() -> InlineKeyboardMarkup:
        """
        Teclado de productos del usuario.
        
        Returns:
            InlineKeyboardMarkup: Teclado de productos del usuario
        """
        keyboard = [
            [
                InlineKeyboardButton("📋 Mis Productos Activos", callback_data="shop_my_products"),
                InlineKeyboardButton("📊 Estadísticas de Uso", callback_data="shop_usage_stats")
            ],
            [
                InlineKeyboardButton("🔄 Renovar Productos", callback_data="shop_renew_products"),
                InlineKeyboardButton("📜 Historial de Compras", callback_data="shop_history")
            ],
            [
                InlineKeyboardButton("🔙 Volver a Tienda", callback_data="shop_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirmation_dialog(action: str, details: dict) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para acciones de tienda.
        
        Args:
            action: Tipo de acción
            details: Detalles de la acción
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = []
        
        if action == "purchase":
            keyboard.append([
                InlineKeyboardButton(f"✅ Comprar ${details['price']:.2f}", callback_data=f"confirm_purchase_{details['product_id']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_purchase")
            ])
        elif action == "renew":
            keyboard.append([
                InlineKeyboardButton(f"✅ Renovar ${details['price']:.2f}", callback_data=f"confirm_renew_{details['product_id']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_renew")
            ])
        elif action == "cancel":
            keyboard.append([
                InlineKeyboardButton("✅ Confirmar Cancelación", callback_data=f"confirm_cancel_{details['product_id']}"),
                InlineKeyboardButton("❌ Mantener Producto", callback_data="keep_product")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_{action}")
            ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def product_filters() -> InlineKeyboardMarkup:
        """
        Teclado de filtros de productos.
        
        Returns:
            InlineKeyboardMarkup: Teclado de filtros
        """
        keyboard = [
            [
                InlineKeyboardButton("👑 VIP", callback_data="filter_vip"),
                InlineKeyboardButton("🎭 Roles", callback_data="filter_roles")
            ],
            [
                InlineKeyboardButton("💾 Almacenamiento", callback_data="filter_storage"),
                InlineKeyboardButton("📊 Todos", callback_data="filter_all")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="shop_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def sort_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de ordenamiento.
        
        Returns:
            InlineKeyboardMarkup: Teclado de ordenamiento
        """
        keyboard = [
            [
                InlineKeyboardButton("💰 Menor Precio", callback_data="sort_price_asc"),
                InlineKeyboardButton("💰 Mayor Precio", callback_data="sort_price_desc")
            ],
            [
                InlineKeyboardButton("🆕 Más Nuevos", callback_data="sort_newest"),
                InlineKeyboardButton("📈 Más Populares", callback_data="sort_popular")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="shop_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
