"""
Teclados inline para el sistema de submenús de llaves VPN del bot uSipipo.
Proporciona navegación organizada por servidor con funcionalidades avanzadas.

Author: uSipipo Team
Version: 2.0.0 - Sistema de submenús para llaves
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any, Optional


class KeySubmenuKeyboards:
    """Teclados inline para el sistema de submenús de llaves VPN."""
    
    # Configuración de paginación
    ITEMS_PER_PAGE = 5
    
    @staticmethod
    def main_menu(keys_summary: Dict[str, Any]) -> InlineKeyboardMarkup:
        """
        Menú principal del submenú de llaves.
        Muestra resumen de llaves por servidor.
        """
        keyboard = []
        
        # Mostrar servidores con llaves
        wireguard_count = keys_summary.get('wireguard_count', 0)
        outline_count = keys_summary.get('outline_count', 0)
        
        # Fila 1: WireGuard Server
        keyboard.append([
            InlineKeyboardButton(
                f"🟦 WireGuard ({wireguard_count})", 
                callback_data="key_submenu_server_wireguard"
            )
        ])
        
        # Fila 2: Outline Server  
        keyboard.append([
            InlineKeyboardButton(
                f"🟩 Outline ({outline_count})", 
                callback_data="key_submenu_server_outline"
            )
        ])
        
        # Fila 3: Acciones rápidas
        keyboard.append([
            InlineKeyboardButton("➕ Crear Nueva", callback_data="create_key"),
            InlineKeyboardButton("🔄 Ver Todas", callback_data="key_submenu_all_keys")
        ])
        
        # Fila 4: Navegación
        keyboard.append([
            InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def server_keys_menu(server_type: str, keys: List[Dict[str, Any]], page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
        """
        Menú de llaves para un servidor específico con paginación.
        """
        keyboard = []
        
        # Mostrar llaves de la página actual
        start_idx = (page - 1) * KeySubmenuKeyboards.ITEMS_PER_PAGE
        end_idx = start_idx + KeySubmenuKeyboards.ITEMS_PER_PAGE
        page_keys = keys[start_idx:end_idx]
        
        for key in page_keys:
            key_id = key.get('id', '')
            key_name = key.get('name', 'Llave sin nombre')
            
            # Determinar emoji según estado
            is_active = key.get('is_active', False)
            usage_percent = (key.get('used_gb', 0) / key.get('limit_gb', 1)) * 100 if key.get('limit_gb', 0) > 0 else 0
            
            if not is_active:
                status_emoji = "🔴"
            elif usage_percent >= 90:
                status_emoji = "🟡"
            else:
                status_emoji = "🟢"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_emoji} {key_name}",
                    callback_data=f"key_detail_{key_id}"
                )
            ])
        
        # Controles de paginación
        if total_pages > 1:
            pagination_row = []
            
            if page > 1:
                pagination_row.append(
                    InlineKeyboardButton("⬅️", callback_data=f"key_submenu_page_{server_type}_{page-1}")
                )
            
            pagination_row.append(
                InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop")
            )
            
            if page < total_pages:
                pagination_row.append(
                    InlineKeyboardButton("➡️", callback_data=f"key_submenu_page_{server_type}_{page+1}")
                )
            
            keyboard.append(pagination_row)
        
        # Fila de acciones
        keyboard.append([
            InlineKeyboardButton("➕ Crear Nueva", callback_data="create_key"),
            InlineKeyboardButton("🔄 Migrar Llave", callback_data=f"key_submenu_migrate_{server_type}")
        ])
        
        # Fila de navegación
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="key_submenu_main")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def key_detail_menu(key_id: str, key_name: str, server_type: str) -> InlineKeyboardMarkup:
        """
        Menú de acciones para una llave específica.
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data=f"key_stats_{key_id}"),
                InlineKeyboardButton("🔄 Migrar", callback_data=f"key_migrate_{key_id}")
            ],
            [
                InlineKeyboardButton("✏️ Renombrar", callback_data=f"key_rename_{key_id}"),
                InlineKeyboardButton("🗑️ Eliminar", callback_data=f"key_delete_confirm_{key_id}")
            ],
            [
                InlineKeyboardButton("📋 Ver Configuración", callback_data=f"key_config_{key_id}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data=f"key_submenu_server_{server_type}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_delete(key_id: str, key_name: str) -> InlineKeyboardMarkup:
        """
        Confirmación de eliminación de llave.
        """
        keyboard = [
            [
                InlineKeyboardButton("✅ Sí, eliminar", callback_data=f"key_delete_execute_{key_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=f"key_detail_{key_id}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def server_migration_menu(key_id: str, current_server: str) -> InlineKeyboardMarkup:
        """
        Menú de migración entre servidores.
        """
        keyboard = []
        
        # Opciones de migración
        if current_server.lower() == 'wireguard':
            keyboard.append([
                InlineKeyboardButton("🟩 Migrar a Outline", callback_data=f"key_migrate_execute_{key_id}_outline")
            ])
        elif current_server.lower() == 'outline':
            keyboard.append([
                InlineKeyboardButton("🟦 Migrar a WireGuard", callback_data=f"key_migrate_execute_{key_id}_wireguard")
            ])
        
        # En caso de servidores múltiples
        keyboard.append([
            InlineKeyboardButton("🔄 Elegir Servidor", callback_data=f"key_migrate_choose_{key_id}")
        ])
        
        # Cancelar
        keyboard.append([
            InlineKeyboardButton("❌ Cancelar", callback_data=f"key_detail_{key_id}")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def server_selection(key_id: str, available_servers: List[Dict[str, str]]) -> InlineKeyboardMarkup:
        """
        Selección específica de servidor para migración.
        """
        keyboard = []
        
        for server in available_servers:
            server_name = server.get('name', 'Unknown')
            server_type = server.get('type', 'unknown')
            
            keyboard.append([
                InlineKeyboardButton(
                    f"📡 {server_name}",
                    callback_data=f"key_migrate_execute_{key_id}_{server_type}"
                )
            ])
        
        # Cancelar
        keyboard.append([
            InlineKeyboardButton("❌ Cancelar", callback_data=f"key_detail_{key_id}")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_server(server_type: str) -> InlineKeyboardMarkup:
        """
        Botones de navegación hacia el servidor.
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver", callback_data=f"key_submenu_server_{server_type}"),
                InlineKeyboardButton("🏠 Menú Principal", callback_data="key_submenu_main")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def quick_actions() -> InlineKeyboardMarkup:
        """
        Botones de acciones rápidas.
        """
        keyboard = [
            [
                InlineKeyboardButton("➕ Crear Llave", callback_data="create_key"),
                InlineKeyboardButton("🔄 Ver Todas", callback_data="key_submenu_all_keys")
            ],
            [
                InlineKeyboardButton("📊 Estado General", callback_data="status"),
                InlineKeyboardButton("🏠 Menú Principal", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def all_keys_overview(keys: List[Dict[str, Any]], page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
        """
        Vista general de todas las llaves con paginación.
        """
        keyboard = []
        
        # Mostrar llaves de la página actual
        start_idx = (page - 1) * KeySubmenuKeyboards.ITEMS_PER_PAGE
        end_idx = start_idx + KeySubmenuKeyboards.ITEMS_PER_PAGE
        page_keys = keys[start_idx:end_idx]
        
        for key in page_keys:
            key_id = key.get('id', '')
            key_name = key.get('name', 'Llave sin nombre')
            server_type = key.get('server_type', 'unknown')
            
            # Determinar emoji según servidor y estado
            server_emoji = "🟦" if server_type.lower() == 'wireguard' else "🟩"
            is_active = key.get('is_active', False)
            
            status_emoji = "🟢" if is_active else "🔴"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{server_emoji} {status_emoji} {key_name}",
                    callback_data=f"key_detail_{key_id}"
                )
            ])
        
        # Controles de paginación
        if total_pages > 1:
            pagination_row = []
            
            if page > 1:
                pagination_row.append(
                    InlineKeyboardButton("⬅️", callback_data=f"key_submenu_all_page_{page-1}")
                )
            
            pagination_row.append(
                InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop")
            )
            
            if page < total_pages:
                pagination_row.append(
                    InlineKeyboardButton("➡️", callback_data=f"key_submenu_all_page_{page+1}")
                )
            
            keyboard.append(pagination_row)
        
        # Fila de acciones
        keyboard.append([
            InlineKeyboardButton("➕ Crear Nueva", callback_data="create_key"),
            InlineKeyboardButton("🔄 Por Servidor", callback_data="key_submenu_main")
        ])
        
        # Fila de navegación
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="key_submenu_main")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def key_rename(key_id: str) -> InlineKeyboardMarkup:
        """
        Menú para renombrar llave.
        """
        keyboard = [
            [
                InlineKeyboardButton("✏️ Cambiar Nombre", callback_data=f"key_rename_start_{key_id}")
            ],
            [
                InlineKeyboardButton("❌ Cancelar", callback_data=f"key_detail_{key_id}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def key_statistics(key_id: str) -> InlineKeyboardMarkup:
        """
        Menú de estadísticas de llave.
        """
        keyboard = [
            [
                InlineKeyboardButton("📈 Ver Gráfico", callback_data=f"key_chart_{key_id}"),
                InlineKeyboardButton("📋 Ver Detalles", callback_data=f"key_details_{key_id}")
            ],
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data=f"key_stats_refresh_{key_id}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data=f"key_detail_{key_id}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def migration_confirmation(key_id: str, from_server: str, to_server: str) -> InlineKeyboardMarkup:
        """
        Confirmación específica de migración.
        """
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar Migración", callback_data=f"key_migrate_confirm_{key_id}_{to_server}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=f"key_detail_{key_id}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)