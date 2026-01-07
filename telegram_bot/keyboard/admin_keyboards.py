"""
Teclados para funcionalidades de administración del bot uSipipo.

Organiza los teclados relacionados con:
- Administración de usuarios
- Gestión de claves
- Estadísticas y monitoreo
- Broadcast y comunicaciones

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


class AdminKeyboards:
    """Teclados para administradores del bot."""
    
    # ============================================
    # MAIN ADMIN MENU
    # ============================================
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Menú principal de administración."""
        keyboard = [
            [
                InlineKeyboardButton("👥 Usuarios", callback_data="admin_users_submenu"),
                InlineKeyboardButton("🔐 Ver Claves", callback_data="show_keys")
            ],
            [
                InlineKeyboardButton("🖥️ Estado Servidores", callback_data="server_status"),
                InlineKeyboardButton("📊 Estadísticas", callback_data="stats")
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
                InlineKeyboardButton("✅ Gestionar Tareas", callback_data="admin_task_menu")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # USERS MANAGEMENT
    # ============================================
    
    @staticmethod
    def users_submenu() -> InlineKeyboardMarkup:
        """Submenu principal de gestión de usuarios."""
        keyboard = [
            [
                InlineKeyboardButton("📋 Ver Usuarios", callback_data="admin_users_list"),
                InlineKeyboardButton("🔍 Buscar Usuario", callback_data="admin_search_user")
            ],
            [
                InlineKeyboardButton("🎖️ Asignar Roles", callback_data="admin_assign_roles"),
                InlineKeyboardButton("📌 Cambiar Estado", callback_data="admin_change_status")
            ],
            [
                InlineKeyboardButton("🔴 Bloquear Usuario", callback_data="admin_block_user"),
                InlineKeyboardButton("🟢 Desbloquear", callback_data="admin_unblock_user")
            ],
            [
                InlineKeyboardButton("🗑️ Eliminar Usuario", callback_data="admin_delete_user"),
                InlineKeyboardButton("ℹ️ Detalle", callback_data="admin_user_detail")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def users_list_pagination(page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
        """Teclado para paginación de lista de usuarios."""
        keyboard = []
        
        # Botones de navegación
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ Anterior", callback_data=f"admin_users_page_{page - 1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="noop"))
        
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("Siguiente ➡️", callback_data=f"admin_users_page_{page + 1}"))
        
        keyboard.append(nav_buttons)
        
        # Acciones
        keyboard.append([
            InlineKeyboardButton("🔄 Actualizar", callback_data="admin_users_list"),
            InlineKeyboardButton("🔍 Buscar", callback_data="admin_search_user")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="admin_users_submenu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def user_detail_actions(user_id: int) -> InlineKeyboardMarkup:
        """Acciones sobre un usuario específico."""
        keyboard = [
            [
                InlineKeyboardButton("🎖️ Cambiar Rol", callback_data=f"admin_user_role_{user_id}"),
                InlineKeyboardButton("📌 Cambiar Estado", callback_data=f"admin_user_status_{user_id}")
            ],
            [
                InlineKeyboardButton("🔴 Bloquear", callback_data=f"admin_user_block_{user_id}"),
                InlineKeyboardButton("🟢 Desbloquear", callback_data=f"admin_user_unblock_{user_id}")
            ],
            [
                InlineKeyboardButton("🗑️ Eliminar", callback_data=f"admin_user_delete_{user_id}"),
                InlineKeyboardButton("👀 Ver Claves", callback_data=f"admin_user_keys_{user_id}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin_users_list")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def role_selection() -> InlineKeyboardMarkup:
        """Selección de roles disponibles."""
        keyboard = [
            [InlineKeyboardButton("👤 Usuario Regular", callback_data="admin_assign_role_user")],
            [InlineKeyboardButton("🔑 Administrador", callback_data="admin_assign_role_admin")],
            [InlineKeyboardButton("📋 Gestor de Tareas (Premium)", callback_data="admin_assign_role_task_manager")],
            [InlineKeyboardButton("📣 Anunciante (Premium)", callback_data="admin_assign_role_announcer")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="admin_users_submenu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def status_selection() -> InlineKeyboardMarkup:
        """Selección de estados disponibles."""
        keyboard = [
            [InlineKeyboardButton("🟢 Activo", callback_data="admin_assign_status_active")],
            [InlineKeyboardButton("🟡 Suspendido", callback_data="admin_assign_status_suspended")],
            [InlineKeyboardButton("🔴 Bloqueado", callback_data="admin_assign_status_blocked")],
            [InlineKeyboardButton("📋 Prueba Gratis", callback_data="admin_assign_status_free_trial")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="admin_users_submenu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def premium_role_duration() -> InlineKeyboardMarkup:
        """Selección de duración para roles premium."""
        keyboard = [
            [InlineKeyboardButton("1 Mes", callback_data="admin_role_duration_30")],
            [InlineKeyboardButton("3 Meses", callback_data="admin_role_duration_90")],
            [InlineKeyboardButton("6 Meses", callback_data="admin_role_duration_180")],
            [InlineKeyboardButton("1 Año", callback_data="admin_role_duration_365")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="admin_users_submenu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_user_action(action_type: str, user_id: int, extra_data: str = "") -> InlineKeyboardMarkup:
        """Confirmación genérica de acciones sobre usuarios."""
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=f"admin_confirm_{action_type}_{user_id}_{extra_data}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="admin_users_list")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # KEYS MANAGEMENT
    # ============================================
    
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
    def confirm_delete_key(key_id: str) -> InlineKeyboardMarkup:
        """Confirmación de eliminación de clave."""
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar Eliminación", callback_data=f"confirm_delete_{key_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_delete")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # GENERAL ACTIONS
    # ============================================
    
    @staticmethod
    def users_actions() -> InlineKeyboardMarkup:
        """Acciones disponibles en la vista de usuarios."""
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
    def back_to_menu() -> InlineKeyboardMarkup:
        """Botón para volver al menú principal de admin."""
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver al Menú", callback_data="admin")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
