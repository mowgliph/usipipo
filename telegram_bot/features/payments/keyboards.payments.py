"""
Teclados para sistema de procesamiento de pagos de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class PaymentsKeyboards:
    """Teclados para sistema de pagos."""

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú principal de pagos.
        
        Returns:
            InlineKeyboardMarkup: Teclado del menú principal
        """
        keyboard = [
            [
                InlineKeyboardButton("💳 Depositar Fondos", callback_data="select_amount"),
                InlineKeyboardButton("📊 Historial", callback_data="payment_history")
            ],
            [
                InlineKeyboardButton("💳 Estado de Balance", callback_data="balance_status"),
                InlineKeyboardButton("📊 Métodos de Pago", callback_data="payment_methods")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def amount_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de monto.
        
        Returns:
            InlineKeyboardMarkup: Teclado de montos
        """
        keyboard = [
            [
                InlineKeyboardButton("💰 $5", callback_data="amount_5"),
                InlineKeyboardButton("💰 $10", callback_data="amount_10"),
                InlineKeyboardButton("💰 $25", callback_data="amount_25"),
                InlineKeyboardButton("💰 $50", callback_data="amount_50")
            ],
            [
                InlineKeyboardButton("💰 $100", callback_data="amount_100"),
                InlineKeyboardButton("💰 $500", callback_data="amount_500"),
                InlineKeyboardButton("💰 $1000", callback_data="amount_1000"),
                InlineKeyboardButton("💰 Personalizado", callback_data="custom_amount")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="payment_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_amounts() -> InlineKeyboardMarkup:
        """
        Teclado para volver a opciones de monto.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver a Montos", callback_data="payment_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_payments() -> InlineKeyboardMarkup:
        """
        Teclado para volver a pagos.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver a Pagos", callback_data="payment_back")
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
    def payment_methods(amount: float) -> InlineKeyboardMarkup:
        """
        Teclado de métodos de pago.
        
        Args:
            amount: Monto a pagar
            
        Returns:
            InlineKeyboardMarkup: Teclado de métodos de pago
        """
        keyboard = [
            [
                InlineKeyboardButton("💳 Balance de Cuenta", callback_data=f"confirm_payment_balance_{amount}"),
                InlineKeyboardButton("💳 Tarjeta de Crédito", callback_data=f"confirm_payment_card_{amount}")
            ],
            [
                InlineKeyboardButton("🏦 Transferencia Bancaria", callback_data=f"confirm_payment_transfer_{amount}"),
                InlineKeyboardButton("₿ Criptomonedas", callback_data=f"confirm_payment_crypto_{amount}")
            ],
            [
                InlineKeyboardButton("🔙 Cancelar", callback_data="payment_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirm_payment(payment_method: str, amount: float) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación de pago.
        
        Args:
            payment_method: Método de pago
            amount: Monto a pagar
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar Pago", callback_data=f"process_payment_{payment_method}_{amount}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="payment_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def payment_success() -> InlineKeyboardMarkup:
        """
        Teclado para pago exitoso.
        
        Returns:
            InlineKeyboardMarkup: Teclado de éxito
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Ver Historial", callback_data="payment_history"),
                InlineKeyboardButton("💳 Estado de Balance", callback_data="balance_status")
            ],
            [
                InlineKeyboardButton("🔙 Volver a Pagos", callback_data="payment_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def balance_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones de balance.
        
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = [
            [
                InlineKeyboardButton("💳 Depositar", callback_data="select_amount"),
                InlineKeyboardButton("📊 Historial", callback_data="payment_history")
            ],
            [
                InlineKeyboardButton("📊 Métodos de Pago", callback_data="payment_methods"),
                InlineKeyboardButton("🔙 Volver", callback_data="payment_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def history_filters() -> InlineKeyboardMarkup:
        """
        Teclado de filtros para historial.
        
        Returns:
            InlineKeyboardMarkup: Teclado de filtros
        """
        keyboard = [
            [
                InlineKeyboardButton("📅 Últimos 7 días", callback_data="filter_week"),
                InlineKeyboardButton("📅 Últimos 30 días", callback_data="filter_month"),
                InlineKeyboardButton("📅 Últimos 90 días", callback_data="filter_quarter")
            ],
            [
                InlineKeyboardButton("💳 Solo Depósitos", callback_data="filter_deposits"),
                InlineKeyboardButton("💸 Solo Gastos", callback_data="filter_spending"),
                InlineKeyboardButton("📊 Todas", callback_data="filter_all")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="payment_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def transaction_actions(transaction_id: str) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para una transacción.
        
        Args:
            transaction_id: ID de la transacción
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = [
            [
                InlineKeyboardButton("📋 Ver Detalles", callback_data=f"transaction_details_{transaction_id}"),
                InlineKeyboardButton("📄 Descargar Recibo", callback_data=f"receipt_{transaction_id}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="back_to_history")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_history() -> InlineKeyboardMarkup:
        """
        Teclado para volver al historial.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver a Pagos", callback_data="payment_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirmation_dialog(action: str, details: dict) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para acciones de pago.
        
        Args:
            action: Tipo de acción
            details: Detalles de la acción
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = []
        
        if action == "deposit":
            keyboard.append([
                InlineKeyboardButton(f"✅ Confirmar ${details['amount']}", callback_data=f"confirm_deposit_{details['amount']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="payment_back")
            ])
        elif action == "withdraw":
            keyboard.append([
                InlineKeyboardButton(f"✅ Retirar ${details['amount']}", callback_data=f"confirm_withdraw_{details['amount']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="payment_back")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="payment_back")
            ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def payment_method_selection() -> InlineKeyboardMarkup:
        """
        Teclado de selección de método de pago.
        
        Returns:
            InlineKeyboardMarkup: Teclado de selección
        """
        keyboard = [
            [
                InlineKeyboardButton("💳 Balance de Cuenta", callback_data="payment_balance"),
                InlineKeyboardButton("💳 Tarjeta de Crédito", callback_data="payment_card"),
                InlineKeyboardButton("🏦 Transferencia Bancaria", callback_data="payment_transfer"),
                InlineKeyboardButton("₿ Criptomonedas", callback_data="payment_crypto")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def crypto_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de criptomonedas.
        
        Returns:
            InlineKeyboardMarkup: Teclado de criptomonedas
        """
        keyboard = [
            [
                InlineKeyboardButton("₿ Bitcoin (BTC)", callback_data="crypto_btc"),
                InlineKeyboardButton("₿ Ethereum (ETH)", callback_data="crypto_eth"),
                InlineKeyboardButton("🪙️ USDT (Tether)", callback_data="crypto_usdt")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="payment_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def card_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de tarjeta.
        
        Returns:
            InlineKeyboardMarkup: Teclado de tarjeta
        """
        keyboard = [
            [
                InlineKeyboardButton("💳 Visa", callback_data="card_visa"),
                InlineKeyboardButton("💳 Mastercard", callback_data="card_mastercard"),
                InlineKeyboardButton("💳 Amex", callback_data="card_amex")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="payment_back")
            ]
        ]
        return InlineKeyboard(keyboard)

    @staticmethod
    def bank_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones bancarias.
        
        Returns:
            InlineKeyboardMarkup: Teclado de bancos
        """
        keyboard = [
            [
                InlineKeyboardButton("🏦 Banco Central", callback_data="bank_central"),
                inlineKeyboardButton("🏦 Banco de Occidente", callback_data="bank_occidente"),
                InlineKeyboardButton("🏦 Banco Provincial", callback_data="bank_provincial")
            ],
            [
                InlineKeyboardButton("🏦 Banco Santander", callback_data="bank_santander"),
                InlineKeyboardButton("🏦 BBVA", callback_data="bank_bbva"),
                InlineKeyboardButton("🔙 Volver", callback_data="payment_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def receipt_options(transaction_id: str) -> InlineKeyboardMarkup:
        """
        Teclado de opciones de recibo.
        
        Args:
            transaction_id: ID de la transacción
            
        Returns:
            InlineKeyboardMarkup: Teclado de recibo
        """
        keyboard = [
            [
                InlineKeyboardButton("📄 Descargar PDF", callback_data=f"receipt_pdf_{transaction_id}"),
                InlineKeyboardButton("📧 Enviar por Email", callback_data=f"receipt_email_{transaction_id}"),
                InlineKeyboardButton("📋 Guardar en Nube", callback_data=f"receipt_cloud_{transaction_id}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="back_to_history")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def withdrawal_limits() -> InlineKeyboardMarkup:
        """
        Teclado de límites de retiro.
        
        Returns:
            InlineKeyboardMarkup: Teclado de límites
        """
        keyboard = [
            [
                InlineKeyboardButton("💳 $50/día", callback_data="withdraw_50"),
                InlineKeyboardButton("💳 $100/día", callback_data="withdraw_100"),
                InlineKeyboardButton("💳 $500/día", callback_data="withdraw_500"),
                InlineKeyboardButton("💳 $1000/día", callback_data="withdraw_1000")
            ],
            [
                InlineKeyboardButton("💳 Personalizado", callback_data="withdraw_custom"),
                InlineKeyboardButton("🔙 Volver", callback_data="payment_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def custom_amount_input() -> InlineKeyboardMarkup:
        """
        Teclado para entrada de monto personalizado.
        
        Returns:
            InlineKeyboardMarkup: Teclado de entrada de monto
        """
        keyboard = [
            [
                InlineKeyboardButton("1️⃣️", callback_data="custom_1"),
                InlineKeyboardButton("2️⃣️", callback_data="custom_2"),
                InlineKeyboardButton("3️⃣️", callback_data="custom_3"),
                InlineKeyboardButton("4️⃣️", callback_data="custom_4"),
                InlineKeyboardButton("5️⃣️", callback_data="custom_5")
            ],
            [
                InlineKeyboardButton("6️⃣️", callback_data="custom_6"),
                InlineKeyboardButton("7️⃣️", callback_data="custom_7"),
                InlineKeyboardButton("8️⃣️", callback_data="custom_8"),
                InlineKeyboardButton("9️⃣️", callback_data="custom_9"),
                InlineKeyboardButton("0️⃣️", callback_data="custom_0")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="payment_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def quick_amounts() -> InlineKeyboardMarkup:
        """
        Teclado de montos rápidos.
        
        Returns:
            InlineKeyboardMarkup: Teclado de montos rápidos
        """
        keyboard = [
            [
                InlineKeyboardButton("💰 $5", callback_data="amount_5"),
                InlineKeyboardButton("💰 $10", callback_data="amount_10"),
                InlineKeyboardButton("💰 $20", callback_data="amount_20"),
                InlineKeyboardButton("💰 $50", callback_data="amount_50")
            ],
            [
                InlineKeyboardButton("💰 $100", callback_data="amount_100"),
                InlineKeyboardButton("💰 $200", callback_data="amount_200"),
                InlineKeyboardButton("💰 $500", callback_data="amount_500"),
                InlineKeyboardButton("💰 $1000", callback_data="amount_1000")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def subscription_plans() -> InlineKeyboardMarkup:
        """
        Teclado de planes de suscripción.
        
        Returns:
            InlineKeyboardMarkup: Teclado de suscripción
        """
        keyboard = [
            [
                InlineKeyboardButton("📅 Mensual - $9.99/mes", callback_data="subscribe_monthly"),
                InlineKeyboardButton("📅 Trimestral - $27.99/mes", callback_data="subscribe_quarterly"),
                InlineKeyboardButton("📅 Anual - $99.99/año", callback_data="subscribe_yearly")
            ],
            [
                InlineKeyboardButton("🎁️ Personalizado", callback_data="subscribe_custom"),
                InlineKeyboardButton("🔙 Volver", callback_data="payment_back")
            ]
        ]
        return InlineKeyboard(keyboard)

    @staticmethod
    def subscription_confirmation(plan: str, price: float, interval: str) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación de suscripción.
        
        Args:
            plan: Nombre del plan
            price: Precio del plan
            interval: Intervalo del plan
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = [
            [
                InlineKeyboardButton(f"✅ Suscribir {plan} - ${price}/{interval}", callback_data=f"confirm_subscribe_{plan}_{interval}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="payment_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
