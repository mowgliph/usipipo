"""
Teclados para sistema VIP de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class VipKeyboards:
    """Teclados para sistema VIP."""

    @staticmethod
    def vip_plans() -> InlineKeyboardMarkup:
        """
        Teclado de planes VIP.
        
        Returns:
            InlineKeyboardMarkup: Teclado de planes VIP
        """
        keyboard = [
            [
                InlineKeyboardButton("🌟 Plan Básico - $9.99/mes", callback_data="vip_plan_basic"),
                InlineKeyboardButton("💎 Plan Premium - $19.99/mes", callback_data="vip_plan_premium")
            ],
            [
                InlineKeyboardButton("💎 Plan Elite - $39.99/mes", callback_data="vip_plan_elite"),
                InlineKeyboardButton("📊 Comparar Planes", callback_data="vip_compare")
            ],
            [
                InlineKeyboardButton("🎁 Ver Beneficios", callback_data="vip_benefits"),
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def plan_actions(plan: str, price: float) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para un plan específico.
        
        Args:
            plan: Nombre del plan
            price: Precio del plan
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = [
            [
                InlineKeyboardButton(f"💳 Comprar ${price:.2f}", callback_data=f"vip_buy_{plan}_{price}"),
                InlineKeyboardButton("🎁 Ver Beneficios", callback_data=f"vip_benefits_{plan}")
            ],
            [
                InlineKeyboardButton("📊 Comparar con otros", callback_data="vip_compare_{plan}"),
                InlineKeyboardButton("🔙 Volver", callback_data="vip_plans")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def payment_options(plan: str, price: float) -> InlineKeyboardMarkup:
        """
        Teclado de opciones de pago.
        
        Args:
            plan: Nombre del plan
            price: Precio del plan
            
        Returns:
            InlineKeyboardMarkup: Teclado de pago
        """
        keyboard = [
            [
                InlineKeyboardButton("💳 Pagar con Balance", callback_data=f"vip_pay_balance_{plan}_{price}"),
                InlineKeyboardButton("🏦 Transferencia Bancaria", callback_data=f"vip_pay_transfer_{plan}_{price}")
            ],
            [
                InlineKeyboardButton("💳 Tarjeta de Crédito", callback_data=f"vip_pay_card_{plan}_{price}"),
                InlineKeyboardButton("₿ Criptomonedas", callback_data=f"vip_pay_crypto_{plan}_{price}")
            ],
            [
                InlineKeyboardButton("🔙 Cancelar", callback_data="vip_plans")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def vip_status_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones para estado VIP.
        
        Returns:
            InlineKeyboardMarkup: Teclado de estado VIP
        """
        keyboard = [
            [
                InlineKeyboardButton("🎁 Mis Beneficios", callback_data="vip_benefits"),
                InlineKeyboardButton("📊 Estadísticas", callback_data="vip_stats")
            ],
            [
                InlineKeyboardButton("⏰ Extender Membresía", callback_data="vip_extend"),
                InlineKeyboardButton("🔄 Cambiar Plan", callback_data="vip_change")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def vip_benefits_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones de beneficios VIP.
        
        Returns:
            InlineKeyboardMarkup: Teclado de beneficios VIP
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Estadísticas de Uso", callback_data="vip_usage_stats"),
                InlineKeyboardButton("🎁 Historial de Beneficios", callback_data="vip_benefits_history")
            ],
            [
                InlineKeyboardButton("⏰ Extender Membresía", callback_data="vip_extend"),
                InlineKeyboardButton("🔄 Actualizar Plan", callback_data="vip_upgrade")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="vip_status")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def extension_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de extensión.
        
        Returns:
            InlineKeyboardMarkup: Teclado de extensión
        """
        keyboard = [
            [
                InlineKeyboardButton("📅 +1 Mes (10% desc)", callback_data="vip_extend_1m"),
                InlineKeyboardButton("📅 +3 Meses (15% desc)", callback_data="vip_extend_3m")
            ],
            [
                InlineKeyboardButton("📅 +6 Meses (20% desc)", callback_data="vip_extend_6m"),
                InlineKeyboardButton("📅 +1 Año (25% desc)", callback_data="vip_extend_1y")
            ],
            [
                InlineKeyboardButton("🔄 Cambiar de Plan", callback_data="vip_change_plan"),
                InlineKeyboardButton("🔙 Volver", callback_data="vip_status")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def upgrade_to_vip() -> InlineKeyboardMarkup:
        """
        Teclado para actualizar a VIP.
        
        Returns:
            InlineKeyboardMarkup: Teclado de actualización VIP
        """
        keyboard = [
            [
                InlineKeyboardButton("👑 Ver Planes VIP", callback_data="vip_plans"),
                InlineKeyboardButton("🎁 Ver Beneficios", callback_data="vip_benefits_preview")
            ],
            [
                InlineKeyboardButton("📊 Comparar Planes", callback_data="vip_compare"),
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def vip_activated() -> InlineKeyboardMarkup:
        """
        Teclado para VIP activado.
        
        Returns:
            InlineKeyboardMarkup: Teclado VIP activado
        """
        keyboard = [
            [
                InlineKeyboardButton("🎁 Ver Beneficios", callback_data="vip_benefits"),
                InlineKeyboardButton("📊 Estadísticas", callback_data="vip_stats")
            ],
            [
                InlineKeyboardButton("🔙 Volver a Operaciones", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_plans() -> InlineKeyboardMarkup:
        """
        Teclado para volver a planes.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno a planes
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver a Planes", callback_data="vip_plans")
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
    def confirmation_dialog(action: str, details: dict) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para acciones VIP.
        
        Args:
            action: Tipo de acción
            details: Detalles de la acción
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = []
        
        if action == "extend":
            keyboard.append([
                InlineKeyboardButton(f"✅ Confirmar {details['duration']}", callback_data=f"confirm_extend_{details['duration']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_extend")
            ])
        elif action == "upgrade":
            keyboard.append([
                InlineKeyboardButton(f"✅ Actualizar a {details['plan']}", callback_data=f"confirm_upgrade_{details['plan']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_upgrade")
            ])
        elif action == "buy":
            keyboard.append([
                InlineKeyboardButton(f"✅ Comprar ${details['price']:.2f}", callback_data=f"confirm_buy_{details['plan']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_buy")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_{action}")
            ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def comparison_table() -> InlineKeyboardMarkup:
        """
        Teclado de tabla de comparación.
        
        Returns:
            InlineKeyboardMarkup: Teclado de comparación
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Ver Tabla Completa", callback_data="vip_comparison_full"),
                InlineKeyboardButton("🎁 Comparar Beneficios", callback_data="vip_benefits_compare")
            ],
            [
                InlineKeyboardButton("🔙 Volver a Planes", callback_data="vip_plans")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def benefits_preview() -> InlineKeyboardMarkup:
        """
        Teclado de vista previa de beneficios.
        
        Returns:
            InlineKeyboardMarkup: Teclado de vista previa
        """
        keyboard = [
            [
                InlineKeyboardButton("🌟 Beneficios Básico", callback_data="benefits_basic"),
                InlineKeyboardButton("💎 Beneficios Premium", callback_data="benefits_premium")
            ],
            [
                InlineKeyboardButton("💎 Beneficios Elite", callback_data="benefits_elite"),
                InlineKeyboardButton("📊 Todos los Beneficios", callback_data="benefits_all")
            ],
            [
                InlineKeyboardButton("👑 Ver Planes", callback_data="vip_plans"),
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
