from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

class Keyboards:
    @staticmethod
    def main_menu():
        """Menú persistente de botones de texto en la parte inferior."""
        keyboard = [
            ["🛡️ Mis Llaves", "➕ Crear Nueva"],
            ["📊 Estado", "💰 Operaciones"],
            ["🏆 Logros", "⚙️ Ayuda"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def admin_main_menu():
        """Menú principal con acceso de administración."""
        keyboard = [
            ["🛡️ Mis Llaves", "➕ Crear Nueva"],
            ["📊 Estado", "💰 Operaciones"],
            ["🔧 Admin", "🏆 Logros", "⚙️ Ayuda"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def vpn_types():
        """Botones inline para elegir el protocolo de conexión."""
        keyboard = [
            [
                InlineKeyboardButton("Outline (SS)", callback_data="type_outline"),
                InlineKeyboardButton("WireGuard", callback_data="type_wireguard")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def key_management(key_id: str):
        """Botón inline para gestionar o eliminar una llave específica."""
        keyboard = [
            [
                InlineKeyboardButton("🗑️ Eliminar Llave", callback_data=f"delete_confirm_{key_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirm_delete(key_id: str):
        """Botones de confirmación de seguridad para evitar borrados accidentales."""
        keyboard = [
            [
                InlineKeyboardButton("✅ Sí, eliminar", callback_data=f"delete_execute_{key_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_delete")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def support_menu():
        """Botón para cerrar el ticket activo."""
        keyboard = [["🔴 Finalizar Soporte"]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def help_back():
        """Botón opcional para?? Volver al menú principal desde la ayuda."""
        keyboard = [[InlineKeyboardButton("🔙?? Volver al Menú", callback_data="main_menu")]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def operations_menu():
        """Genera el teclado del menú de operaciones."""
        return ReplyKeyboardMarkup(
            [
                ["💰 Mi Balance", "👑 Plan VIP"],
                ["🎮 Juega y Gana", "👥 Referidos"],
                ["🎫 Soporte"],
                ["🔙 Atrás"]
            ],
            resize_keyboard=True
        )

    @staticmethod
    def operations_menu_inline():
        """Genera el teclado inline del menú de operaciones para edición de mensajes."""
        keyboard = [
            [
                InlineKeyboardButton("💰 Mi Balance", callback_data="my_balance"),
                InlineKeyboardButton("⭐ Recargar Saldo", callback_data="deposit_stars")
            ],
            [
                InlineKeyboardButton("👑 Plan VIP", callback_data="vip_plan"),
                InlineKeyboardButton("🎮 Juega y Gana", callback_data="games_menu")
            ],
            [
                InlineKeyboardButton("👥 Referidos", callback_data="referrals_menu"),
                InlineKeyboardButton("🎫 Soporte", callback_data="support_menu")
            ],
            [
                InlineKeyboardButton("🔙 Atrás", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def admin_menu():
        """Menú de administración para el admin."""
        keyboard = [["🔧 Admin"]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def vip_plans():
        """Opciones de compra de VIP."""
        keyboard = [
            [
                InlineKeyboardButton("1 Mes - 10 Estrellas", callback_data="vip_1_month"),
                InlineKeyboardButton("3 Meses - 27 Estrellas", callback_data="vip_3_months")
            ],
            [
                InlineKeyboardButton("6 Meses - 50 Estrellas", callback_data="vip_6_months"),
                InlineKeyboardButton("12 Meses - 90 Estrellas", callback_data="vip_12_months")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def referral_actions():
        """Acciones para el programa de referidos."""
        keyboard = [
            [
                InlineKeyboardButton("📋 Mi Código de Referido", callback_data="my_referral_code"),
                InlineKeyboardButton("👥 Mis Referidos", callback_data="my_referrals")
            ],
            [
                InlineKeyboardButton("💰 Mis Ganancias", callback_data="referral_earnings"),
                InlineKeyboardButton("🔗 Compartir Enlace", callback_data="share_referral")
            ],
            [
                InlineKeyboardButton("📋 Aplicar Código", callback_data="apply_referral_code")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def achievements_menu():
        """Menú principal de logros."""
        keyboard = [
            [
                InlineKeyboardButton("📊 Mi Progreso", callback_data="achievements_progress"),
                InlineKeyboardButton("🏆 Mis Logros", callback_data="achievements_list")
            ],
            [
                InlineKeyboardButton("🎯 Próximos Logros", callback_data="achievements_next"),
                InlineKeyboardButton("🎁 Recompensas", callback_data="achievements_rewards")
            ],
            [
                InlineKeyboardButton("🏆 Ranking", callback_data="achievements_leaderboard")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def achievements_categories():
        """Categorías de logros."""
        keyboard = [
            [
                InlineKeyboardButton("📊 Consumo de Datos", callback_data="achievements_category_data"),
                InlineKeyboardButton("📅 Días Activos", callback_data="achievements_category_days")
            ],
            [
                InlineKeyboardButton("👥 Referidos", callback_data="achievements_category_referrals"),
                InlineKeyboardButton("💰 Estrellas", callback_data="achievements_category_stars")
            ],
            [
                InlineKeyboardButton("🔑 Claves", callback_data="achievements_category_keys"),
                InlineKeyboardButton("🎮 Juegos", callback_data="achievements_category_games")
            ],
            [
                InlineKeyboardButton("👑 VIP", callback_data="achievements_category_vip")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="achievements_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def achievement_detail(achievement_id: str):
        """Botones para detalles de un logro."""
        keyboard = [
            [
                InlineKeyboardButton("🎁 Reclamar Recompensa", callback_data=f"claim_reward_{achievement_id}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="achievements_list")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def achievements_leaderboard():
        """Opciones de ranking."""
        keyboard = [
            [
                InlineKeyboardButton("📊 Consumo de Datos", callback_data="leaderboard_data"),
                InlineKeyboardButton("📅 Días Activos", callback_data="leaderboard_days")
            ],
            [
                InlineKeyboardButton("👥 Referidos", callback_data="leaderboard_referrals"),
                InlineKeyboardButton("💰 Estrellas", callback_data="leaderboard_stars")
            ],
            [
                InlineKeyboardButton("🏆 Top General", callback_data="leaderboard_general")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="achievements_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def pending_rewards(rewards: list):
        """Botones para recompensas pendientes."""
        keyboard = []
        
        # Agrupar recompensas en filas de 2
        for i in range(0, len(rewards), 2):
            row = []
            if i < len(rewards):
                achievement = rewards[i]
                row.append(InlineKeyboardButton(
                    f"{achievement['icon']} {achievement['name']}", 
                    callback_data=f"claim_reward_{achievement['id']}"
                ))
            if i + 1 < len(rewards):
                achievement = rewards[i + 1]
                row.append(InlineKeyboardButton(
                    f"{achievement['icon']} {achievement['name']}", 
                    callback_data=f"claim_reward_{achievement['id']}"
                ))
            if row:
                keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="achievements_menu")])
        return InlineKeyboardMarkup(keyboard)
