"""
Teclados para funcionalidades de operaciones e integración del bot uSipipo.

Organiza los teclados relacionados con:
- Operaciones financieras (balance, depósitos)
- Shop y planes VIP
- Referidos
- Juegos
- Logros y rankings

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any, Optional


class OperationKeyboards:
    """Teclados para operaciones financieras y sistemas de monetización."""
    
    # ============================================
    # OPERATIONS MENU
    # ============================================
    
    @staticmethod
    def operations_menu(user=None) -> InlineKeyboardMarkup:
        """
        Menú principal de operaciones con botones condicionales según roles.
        
        Args:
            user: Objeto usuario para verificar roles especiales
        """
        keyboard = [
            [
                InlineKeyboardButton("💰 Mi Balance", callback_data="my_balance"),
                InlineKeyboardButton("⭐ Recargar Estrellas", callback_data="deposit_stars")
            ],
            [
                InlineKeyboardButton("🛒 Shop", callback_data="shop_menu"),
                InlineKeyboardButton("🎮 Juega y Gana", callback_data="games_menu")
            ],
            [
                InlineKeyboardButton("👥 Referidos", callback_data="referrals_menu"),
                InlineKeyboardButton("✅ Centro de Tareas", callback_data="task_center")
            ]
        ]
        
        # Agregar botones de roles especiales si el usuario los posee
        if user:
            role_buttons = []
            
            # Verificar rol de Gestor de Tareas
            if hasattr(user, 'is_task_manager_active') and user.is_task_manager_active():
                role_buttons.append(InlineKeyboardButton("📋 Gestor de Tareas", callback_data="user_task_manager"))
            
            # Verificar rol de Anunciante
            if hasattr(user, 'is_announcer_active') and user.is_announcer_active():
                role_buttons.append(InlineKeyboardButton("📣 Anunciante", callback_data="user_announcer"))
            
            # Agregar fila de roles si hay botones
            if role_buttons:
                keyboard.append(role_buttons)
        
        keyboard.append([InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")])
        
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # VIP PLANS
    # ============================================
    
    @staticmethod
    def vip_plans() -> InlineKeyboardMarkup:
        """Planes VIP disponibles."""
        keyboard = [
            [
                InlineKeyboardButton("1 Mes - 10 Estrellas", callback_data="vip_1_month"),
                InlineKeyboardButton("3 Meses - 27 Estrellas", callback_data="vip_3_months")
            ],
            [
                InlineKeyboardButton("6 Meses - 50 Estrellas", callback_data="vip_6_months"),
                InlineKeyboardButton("12 Meses - 90 Estrellas", callback_data="vip_12_months")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def vip_payment_options(telegram_id: int, months: int, cost: int) -> InlineKeyboardMarkup:
        """
        Teclado con opciones de pago para planes VIP.
        
        Args:
            telegram_id: ID del usuario
            months: Meses del plan
            cost: Costo en estrellas
        """
        keyboard = [
            [
                InlineKeyboardButton("💰 Pagar con Balance", callback_data=f"vip_pay_balance_{telegram_id}_{months}_{cost}"),
                InlineKeyboardButton("📋 Factura Telegram Stars", callback_data=f"vip_pay_invoice_{telegram_id}_{months}_{cost}")
            ],
            [
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_vip_purchase")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # REFERRAL SYSTEM
    # ============================================
    
    @staticmethod
    def referral_actions() -> InlineKeyboardMarkup:
        """Acciones del programa de referidos."""
        keyboard = [
            [
                InlineKeyboardButton("📋 Mi Código", callback_data="my_referral_code"),
                InlineKeyboardButton("👥 Mis Referidos", callback_data="my_referrals")
            ],
            [
                InlineKeyboardButton("💰 Mis Ganancias", callback_data="referral_earnings"),
                InlineKeyboardButton("🔗 Compartir Enlace", callback_data="share_referral")
            ],
            [
                InlineKeyboardButton("📋 Aplicar Código", callback_data="apply_referral_code"),
                InlineKeyboardButton("🔙 Volver", callback_data="operations")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # ACHIEVEMENTS & REWARDS
    # ============================================
    
    @staticmethod
    def achievements_menu() -> InlineKeyboardMarkup:
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
                InlineKeyboardButton("🏆 Ranking", callback_data="achievements_leaderboard"),
                InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def achievements_categories() -> InlineKeyboardMarkup:
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
                InlineKeyboardButton("👑 VIP", callback_data="achievements_category_vip"),
                InlineKeyboardButton("🔙 Volver", callback_data="achievements")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def achievement_detail(achievement_id: str) -> InlineKeyboardMarkup:
        """Detalles y acciones de un logro."""
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
    def achievements_leaderboard() -> InlineKeyboardMarkup:
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
                InlineKeyboardButton("🏆 Top General", callback_data="leaderboard_general"),
                InlineKeyboardButton("🔙 Volver", callback_data="achievements")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def pending_rewards(rewards: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """Recompensas pendientes por reclamar."""
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
        
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="achievements")])
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # GAMES
    # ============================================
    
    @staticmethod
    def games_menu() -> InlineKeyboardMarkup:
        """Menú principal de juegos."""
        keyboard = [
            [
                InlineKeyboardButton("🎳 Bowling", callback_data="game_bowling"),
                InlineKeyboardButton("🎯 Dardos", callback_data="game_darts")
            ],
            [
                InlineKeyboardButton("🎲 Dados", callback_data="game_dice"),
                InlineKeyboardButton("💰 Mi Balance", callback_data="game_balance")
            ],
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="game_stats"),
                InlineKeyboardButton("❓ Ayuda", callback_data="game_help")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)


class SupportKeyboards:
    """Teclados para soporte técnico del bot."""
    
    # ============================================
    # SUPPORT
    # ============================================
    
    @staticmethod
    def support_menu() -> InlineKeyboardMarkup:
        """Menú de soporte técnico."""
        keyboard = [
            [
                InlineKeyboardButton("🌊 Sip (Asistente IA)", callback_data="ai_sip_start"),
                InlineKeyboardButton("🎫 Crear Ticket", callback_data="create_ticket")
            ],
            [
                InlineKeyboardButton("📋 Mis Tickets", callback_data="my_tickets"),
                InlineKeyboardButton("❓ FAQ", callback_data="faq")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def ai_support_active() -> InlineKeyboardMarkup:
        """Opciones cuando hay una conversación IA activa."""
        keyboard = [
            [
                InlineKeyboardButton("💡 Preguntas Frecuentes", callback_data="ai_sip_suggestions")
            ],
            [
                InlineKeyboardButton("🔴 Finalizar Chat", callback_data="ai_sip_end")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def support_active() -> InlineKeyboardMarkup:
        """Opciones cuando hay un ticket activo."""
        keyboard = [
            [
                InlineKeyboardButton("🔴 Finalizar Soporte", callback_data="close_ticket"),
                InlineKeyboardButton("📝 Responder", callback_data="reply_ticket")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # HELP
    # ============================================
    
    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """Menú principal de ayuda."""
        keyboard = [
            [
                InlineKeyboardButton("📖 Guía de Uso", callback_data="usage_guide"),
                InlineKeyboardButton("🔧 Configuración", callback_data="configuration")
            ],
            [
                InlineKeyboardButton("❓ Preguntas Frecuentes", callback_data="faq"),
                InlineKeyboardButton("🎫 Soporte", callback_data="support_menu")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)


class TaskKeyboards:
    """Teclados para el sistema de tareas del bot."""
    
    # ============================================
    # TASK CENTER (USER)
    # ============================================
    
    @staticmethod
    def task_center_menu() -> InlineKeyboardMarkup:
        """Menú principal del centro de tareas."""
        keyboard = [
            [
                InlineKeyboardButton("📋 Ver Tareas Disponibles", callback_data="tasks_available"),
                InlineKeyboardButton("🔄 Mis Tareas en Progreso", callback_data="tasks_in_progress")
            ],
            [
                InlineKeyboardButton("✅ Tareas Completadas", callback_data="tasks_completed"),
                InlineKeyboardButton("📊 Resumen", callback_data="tasks_summary")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def task_list_keyboard(tasks: List[Dict], prefix: str = "task") -> InlineKeyboardMarkup:
        """
        Teclado para listar tareas.
        
        Args:
            tasks: Lista de tareas
            prefix: Prefijo para los callbacks
        """
        keyboard = []
        
        for task in tasks[:10]:  # Máximo 10 tareas por página
            task_id = str(task.get("id", ""))
            title = task.get("title", "Sin título")
            # Truncar título si es muy largo
            display_title = title[:30] + "..." if len(title) > 30 else title
            keyboard.append([
                InlineKeyboardButton(
                    f"📋 {display_title}",
                    callback_data=f"{prefix}_detail_{task_id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="task_center")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def task_detail_keyboard(task_id: str, is_completed: bool = False, reward_claimed: bool = False) -> InlineKeyboardMarkup:
        """
        Teclado para detalles de una tarea.
        
        Args:
            task_id: ID de la tarea
            is_completed: Si la tarea está completada
            reward_claimed: Si la recompensa fue reclamada
        """
        keyboard = []
        
        if not is_completed:
            keyboard.append([
                InlineKeyboardButton("✅ Completar Tarea", callback_data=f"task_complete_{task_id}")
            ])
        elif not reward_claimed:
            keyboard.append([
                InlineKeyboardButton("🎁 Reclamar Recompensa", callback_data=f"task_claim_{task_id}")
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="task_center")])
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # ADMIN TASK MANAGEMENT
    # ============================================
    
    @staticmethod
    def admin_task_menu() -> InlineKeyboardMarkup:
        """Menú de administración de tareas."""
        keyboard = [
            [
                InlineKeyboardButton("➕ Crear Tarea", callback_data="admin_task_create"),
                InlineKeyboardButton("📋 Listar Tareas", callback_data="admin_task_list")
            ],
            [
                InlineKeyboardButton("✏️ Editar Tarea", callback_data="admin_task_edit"),
                InlineKeyboardButton("🗑️ Eliminar Tarea", callback_data="admin_task_delete")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_task_list_keyboard(tasks: List[Dict]) -> InlineKeyboardMarkup:
        """Teclado para listar tareas (admin)."""
        keyboard = []
        
        for task in tasks[:10]:
            task_id = str(task.get("id", ""))
            title = task.get("title", "Sin título")
            is_active = task.get("is_active", True)
            status_icon = "✅" if is_active else "❌"
            display_title = title[:25] + "..." if len(title) > 25 else title
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_icon} {display_title}",
                    callback_data=f"admin_task_detail_{task_id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="admin_task_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_task_detail_keyboard(task_id: str) -> InlineKeyboardMarkup:
        """Teclado para detalles de tarea (admin)."""
        keyboard = [
            [
                InlineKeyboardButton("✏️ Editar", callback_data=f"admin_task_edit_{task_id}"),
                InlineKeyboardButton("🗑️ Eliminar", callback_data=f"admin_task_delete_{task_id}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin_task_list")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
