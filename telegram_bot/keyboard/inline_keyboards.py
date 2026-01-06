"""
Teclados inline estandarizados para el bot uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Migración a teclados inline
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any, Optional
from config import settings


def get_main_menu_for_user(user_id: int) -> InlineKeyboardMarkup:
    """Helper function para obtener el menú principal correcto según el usuario."""
    is_admin = user_id == int(settings.ADMIN_ID)
    return InlineKeyboards.main_menu(is_admin=is_admin)


class InlineKeyboards:
    """Clase centralizada para todos los teclados inline del bot."""
    
    # Navegación principal
    @staticmethod
    def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
        """Menú principal inline - incluye botón de admin solo si el usuario es administrador."""
        keyboard = [
            [
                InlineKeyboardButton("🛡️ Mis Llaves", callback_data="my_keys"),
                InlineKeyboardButton("➕ Crear Nueva", callback_data="create_key")
            ],
            [
                InlineKeyboardButton("📊 Estado", callback_data="status"),
                InlineKeyboardButton("💰 Operaciones", callback_data="operations")
            ]
        ]
        
        # Tercera fila: incluir botón de admin solo si es administrador
        if is_admin:
            keyboard.append([
                InlineKeyboardButton("🔧 Admin", callback_data="admin"),
                InlineKeyboardButton("🏆 Logros", callback_data="achievements"),
                InlineKeyboardButton("⚙️ Ayuda", callback_data="help")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("🏆 Logros", callback_data="achievements"),
                InlineKeyboardButton("⚙️ Ayuda", callback_data="help")
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_main_menu() -> InlineKeyboardMarkup:
        """Menú principal inline con acceso de administración (DEPRECATED - usar main_menu(is_admin=True))."""
        return InlineKeyboards.main_menu(is_admin=True)
    
    # Sistema de VPN y Llaves
    @staticmethod
    def vpn_types() -> InlineKeyboardMarkup:
        """Selección de protocolo VPN."""
        keyboard = [
            [
                InlineKeyboardButton("Outline (SS)", callback_data="type_outline"),
                InlineKeyboardButton("WireGuard", callback_data="type_wireguard")
            ],
            [
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_create_key")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def key_management(key_id: str) -> InlineKeyboardMarkup:
        """Gestión de llave específica."""
        keyboard = [
            [
                InlineKeyboardButton("🗑️ Eliminar Llave", callback_data=f"delete_confirm_{key_id}"),
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data=f"key_stats_{key_id}")
            ],
            [
                InlineKeyboardButton("🔄 Renovar", callback_data=f"renew_key_{key_id}"),
                InlineKeyboardButton("🔙 Volver", callback_data="my_keys")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_delete(key_id: str) -> InlineKeyboardMarkup:
        """Confirmación de eliminación."""
        keyboard = [
            [
                InlineKeyboardButton("✅ Sí, eliminar", callback_data=f"delete_execute_{key_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_delete")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # Sistema de Operaciones
    @staticmethod
    def operations_menu() -> InlineKeyboardMarkup:
        """Menú principal de operaciones."""
        keyboard = [
            [
                InlineKeyboardButton("💰 Mi Balance", callback_data="my_balance"),
                InlineKeyboardButton("⭐ Recargar Estrellas", callback_data="deposit_stars")
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
                InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # Sistema VIP
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
    
    # Sistema de Referidos
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
    
    # Sistema de Logros
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
    
    # Sistema de Juegos
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
    
    # Sistema de Soporte
    @staticmethod
    def support_menu() -> InlineKeyboardMarkup:
        """Menú de soporte técnico."""
        keyboard = [
            [
                InlineKeyboardButton("🎫 Crear Ticket", callback_data="create_ticket"),
                InlineKeyboardButton("📋 Mis Tickets", callback_data="my_tickets")
            ],
            [
                InlineKeyboardButton("❓ FAQ", callback_data="faq"),
                InlineKeyboardButton("🔙 Volver", callback_data="operations")
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
    
    # Sistema de Ayuda
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
    
    # Utilidades generales
    @staticmethod
    def back_button(target: str = "main_menu") -> InlineKeyboardMarkup:
        """Botón de volver genérico."""
        keyboard = [
            [InlineKeyboardButton("🔙 Volver", callback_data=target)]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_action(action: str, item_id: str = "") -> InlineKeyboardMarkup:
        """Confirmación genérica de acciones."""
        callback_yes = f"confirm_{action}_{item_id}" if item_id else f"confirm_{action}"
        callback_no = f"cancel_{action}_{item_id}" if item_id else f"cancel_{action}"
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=callback_yes),
                InlineKeyboardButton("❌ Cancelar", callback_data=callback_no)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)


class InlineAdminKeyboards:
    """Teclados inline específicos para administración."""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Menú principal de administración."""
        keyboard = [
            [
                InlineKeyboardButton("👥 Ver Usuarios", callback_data="show_users"),
                InlineKeyboardButton("🔐 Ver Claves", callback_data="show_keys")
            ],
            [
                InlineKeyboardButton("🖥️ Estado Servidores", callback_data="server_status"),
                InlineKeyboardButton("📊 Estadísticas", callback_data="stats")
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
                InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def users_actions() -> InlineKeyboardMarkup:
        """Acciones sobre usuarios."""
        keyboard = [
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data="show_users"),
                InlineKeyboardButton("📊 Estadísticas", callback_data="stats")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def key_actions(key_id: str) -> InlineKeyboardMarkup:
        """Acciones para una clave específica."""
        keyboard = [
            [
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data=f"stats_{key_id}"),
                InlineKeyboardButton("👤 Ver Usuario", callback_data=f"user_{key_id}")
            ],
            [
                InlineKeyboardButton("🗑️ Eliminar Clave", callback_data=f"delete_key_{key_id}"),
                InlineKeyboardButton("🔄 Renovar", callback_data=f"renew_{key_id}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="show_keys")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_delete(key_id: str) -> InlineKeyboardMarkup:
        """Confirmación de eliminación admin."""
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar Eliminación", callback_data=f"confirm_delete_{key_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_delete")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
