"""
Teclados para operaciones del usuario de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class OperationsKeyboards:
    """Teclados para operaciones del usuario."""

    @staticmethod
    def operations_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú principal de operaciones.
        
        Returns:
            InlineKeyboardMarkup: Teclado del menú de operaciones
        """
        keyboard = [
            [
                InlineKeyboardButton("💰 Mi Balance", callback_data="balance"),
                InlineKeyboardButton("👥 Referidos", callback_data="referrals")
            ],
            [
                InlineKeyboardButton("👑 Plan VIP", callback_data="vip_plans"),
                InlineKeyboardButton("🎮 Juega y Gana", callback_data="game_menu")
            ],
            [
                InlineKeyboardButton("📊 Transacciones", callback_data="transactions"),
                InlineKeyboardButton("🎁 Recompensas", callback_data="rewards")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
        """
        Teclado para volver al menú principal del bot.
        
        Args:
            is_admin: Si es True, incluye opciones de administrador
            
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [
                InlineKeyboardButton("🛡️ Mis Llaves", callback_data="operations"),
                InlineKeyboardButton("📊 Estado", callback_data="status")
            ],
            [
                InlineKeyboardButton("💰 Operaciones", callback_data="operations"),
                InlineKeyboardButton("🏆 Logros", callback_data="achievements")
            ],
            [
                InlineKeyboardButton("⚙️ Ayuda", callback_data="help")
            ]
        ]
        
        # Agregar opciones de administrador si corresponde
        if is_admin:
            keyboard.insert(0, [
                InlineKeyboardButton("🔧 Panel Admin", callback_data="admin")
            ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def referral_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones de referidos.
        
        Returns:
            InlineKeyboardMarkup: Teclado de referidos
        """
        keyboard = [
            [
                InlineKeyboardButton("📋 Copiar Enlace", callback_data="copy_referral"),
                InlineKeyboardButton("📤 Compartir", callback_data="share_referral")
            ],
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="referral_stats"),
                InlineKeyboardButton("🎆 Ranking", callback_data="referral_leaderboard")
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
                InlineKeyboardButton("🌟 Plan Básico - $9.99/mes", callback_data="vip_basic"),
                InlineKeyboardButton("💎 Plan Premium - $19.99/mes", callback_data="vip_premium")
            ],
            [
                InlineKeyboardButton("💎 Plan Elite - $39.99/mes", callback_data="vip_elite"),
                InlineKeyboardButton("🔍 Comparar Planes", callback_data="compare_vip")
            ],
            [
                InlineKeyboardButton("🎁 Prueba Gratuita", callback_data="vip_trial"),
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def game_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú de juegos.
        
        Returns:
            InlineKeyboardMarkup: Teclado de juegos
        """
        keyboard = [
            [
                InlineKeyboardButton("🎲 Ruleta de la Suerte", callback_data="spin_wheel"),
                InlineKeyboardButton("🎯 Trivia uSipipo", callback_data="trivia_game")
            ],
            [
                InlineKeyboardButton("🏆 Desafíos Diarios", callback_data="daily_challenges"),
                InlineKeyboardButton("🎁 Recompensas", callback_data="game_rewards")
            ],
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="game_stats"),
                InlineKeyboardButton("🏅 Leaderboard", callback_data="game_leaderboard")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def balance_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones de balance.
        
        Returns:
            InlineKeyboardMarkup: Teclado de balance
        """
        keyboard = [
            [
                InlineKeyboardButton("💳 Recargar", callback_data="add_balance"),
                InlineKeyboardButton("📊 Historial", callback_data="balance_history")
            ],
            [
                InlineKeyboardButton("🎁 Canjear Recompensas", callback_data="redeem_rewards"),
                InlineKeyboardButton("📈 Estadísticas", callback_data="balance_stats")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def payment_methods() -> InlineKeyboardMarkup:
        """
        Teclado de métodos de pago.
        
        Returns:
            InlineKeyboardMarkup: Teclado de pagos
        """
        keyboard = [
            [
                InlineKeyboardButton("💳 Tarjeta de Crédito", callback_data="pay_card"),
                InlineKeyboardButton("🏦 Transferencia", callback_data="pay_transfer")
            ],
            [
                InlineKeyboardButton("₿ Criptomonedas", callback_data="pay_crypto"),
                InlineKeyboardButton("📱 PayPal", callback_data="pay_paypal")
            ],
            [
                InlineKeyboardButton("🔙 Cancelar", callback_data="cancel_payment")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirmation_dialog(action: str, amount: float = None) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para operaciones.
        
        Args:
            action: Tipo de acción
            amount: Monto (opcional)
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = []
        
        if action == "add_balance" and amount:
            keyboard.append([
                InlineKeyboardButton(f"✅ Confirmar ${amount:.2f}", callback_data=f"confirm_add_{amount}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_add")
            ])
        elif action == "vip_upgrade":
            keyboard.append([
                InlineKeyboardButton("✅ Confirmar Actualización", callback_data="confirm_vip"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_vip")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_{action}")
            ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def transaction_filters() -> InlineKeyboardMarkup:
        """
        Teclado de filtros para transacciones.
        
        Returns:
            InlineKeyboardMarkup: Teclado de filtros
        """
        keyboard = [
            [
                InlineKeyboardButton("📅 Todas", callback_data="filter_all"),
                InlineKeyboardButton("💳 Depósitos", callback_data="filter_deposits")
            ],
            [
                InlineKeyboardButton("💸 Gastos", callback_data="filter_spending"),
                InlineKeyboardButton("🎁 Recompensas", callback_data="filter_rewards")
            ],
            [
                InlineKeyboardButton("📊 Últimos 7 días", callback_data="filter_week"),
                InlineKeyboardButton("📅 Últimos 30 días", callback_data="filter_month")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def spin_wheel(spins_left: int) -> InlineKeyboardMarkup:
        """
        Teclado para la ruleta de la suerte.
        
        Args:
            spins_left: Tiradas restantes
            
        Returns:
            InlineKeyboardMarkup: Teclado de ruleta
        """
        if spins_left > 0:
            button_text = f"🎲 Girar ({spins_left} restantes)"
        else:
            button_text = "🎲 Girar (0 restantes)"
        
        keyboard = [
            [
                InlineKeyboardButton(button_text, callback_data="spin_wheel"),
                InlineKeyboardButton("💰 Comprar Tiradas", callback_data="buy_spins")
            ],
            [
                InlineKeyboardButton("📊 Historial", callback_data="spin_history"),
                InlineKeyboardButton("🔙 Volver", callback_data="game_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def trivia_categories() -> InlineKeyboardMarkup:
        """
        Teclado de categorías de trivia.
        
        Returns:
            InlineKeyboardMarkup: Teclado de categorías
        """
        keyboard = [
            [
                InlineKeyboardButton("🔐 VPN y Seguridad", callback_data="trivia_security"),
                InlineKeyboardButton("🌐 Internet", callback_data="trivia_internet")
            ],
            [
                InlineKeyboardButton("💻 Tecnología", callback_data="trivia_tech"),
                InlineKeyboardButton("🎮 General", callback_data="trivia_general")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="game_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
