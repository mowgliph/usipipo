"""
Teclados para funcionalidades de usuario regular del bot uSipipo.

Organiza los teclados relacionados con:
- Menú principal
- VPN keys management
- Estado y operaciones
- Ayuda

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any, Optional
from config import settings


class UserKeyboards:
    """Teclados para usuarios regulares del bot."""
    
    # Class constant for pagination
    ITEMS_PER_PAGE = 5
     
    @staticmethod
    def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
        """
        Menú principal inline - incluye botón de admin solo si el usuario es administrador.
        
        Args:
            is_admin: Si el usuario tiene permisos de administrador
            
        Returns:
            InlineKeyboardMarkup con el menú principal
        """
        keyboard = [
            [
                InlineKeyboardButton("🛡️ Mis Llaves", callback_data="my_keys"),
                InlineKeyboardButton("➕ Crear Nueva", callback_data="create_key")
            ],
            [
                InlineKeyboardButton("📊 Mi Estado", callback_data="status"),
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
    
    # ============================================
    # VPN KEYS MANAGEMENT
    # ============================================
    
    @staticmethod
    def my_keys_submenu(keys_summary: Dict[str, Any]) -> InlineKeyboardMarkup:
        """
        Menú principal de gestión de llaves VPN.
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
         
        Args:
            server_type: Tipo de servidor ('wireguard' o 'outline')
            keys: Lista de llaves disponibles
            page: Página actual
            total_pages: Total de páginas
             
        Returns:
            InlineKeyboardMarkup con las llaves del servidor
        """
        keyboard = []
        
        # Mostrar llaves de la página actual
        start_idx = (page - 1) * UserKeyboards.ITEMS_PER_PAGE
        end_idx = start_idx + UserKeyboards.ITEMS_PER_PAGE
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
            pagination_row = UserKeyboards._build_pagination_row(page, total_pages, f"key_submenu_page_{server_type}")
            keyboard.append(pagination_row)
        
        # Fila de acciones
        keyboard.append([
            InlineKeyboardButton("➕ Crear Nueva", callback_data="create_key")
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
                InlineKeyboardButton("✏️ Renombrar", callback_data=f"key_rename_{key_id}")
            ],
            [
                InlineKeyboardButton("🗑️ Eliminar", callback_data=f"key_delete_confirm_{key_id}"),
                InlineKeyboardButton("📋 Ver Configuración", callback_data=f"key_config_{key_id}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data=f"key_submenu_server_{server_type}")
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
        start_idx = (page - 1) * UserKeyboards.ITEMS_PER_PAGE
        end_idx = start_idx + UserKeyboards.ITEMS_PER_PAGE
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
            pagination_row = UserKeyboards._build_pagination_row(page, total_pages, "key_submenu_all_page")
            keyboard.append(pagination_row)
        
        # Fila de acciones
        keyboard.append([
            InlineKeyboardButton("➕ Crear Nueva", callback_data="create_key")
        ])
        
        # Fila de navegación
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="key_submenu_main")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def key_statistics(key_id: str) -> InlineKeyboardMarkup:
        """Menú de estadísticas de llave."""
        keyboard = [
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data=f"key_stats_refresh_{key_id}"),
                InlineKeyboardButton("📋 Ver Configuración", callback_data=f"key_config_{key_id}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data=f"key_detail_{key_id}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def key_config(key_id: str, server_type: str) -> InlineKeyboardMarkup:
        """
        Menú de configuración de llave.
        """
        keyboard = []
        
        if server_type.lower() == 'wireguard':
            # WireGuard tiene archivo de configuración descargable
            keyboard.append([
                InlineKeyboardButton("💾 Descargar Config", callback_data=f"key_download_{key_id}"),
                InlineKeyboardButton("📋 Ver Detalles", callback_data=f"key_details_{key_id}")
            ])
        else:  # Outline
            # Outline solo muestra la clave para copiar
            keyboard.append([
                InlineKeyboardButton("📋 Ver Detalles", callback_data=f"key_details_{key_id}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔄 Actualizar", callback_data=f"key_config_refresh_{key_id}")
        ])
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data=f"key_detail_{key_id}")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # VPN TYPES & CREATION
    # ============================================
    
    @staticmethod
    def vpn_types() -> InlineKeyboardMarkup:
        """Selección de protocolo VPN para crear nueva llave."""
        keyboard = [
            [
                InlineKeyboardButton("Outline (SS)", callback_data="type_outline"),
                InlineKeyboardButton("WireGuard", callback_data="type_wireguard")
            ],
            [
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel")
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
    
    # ============================================
    # CONFIRMATION DIALOGS (Reutilizable)
    # ============================================
    
    @staticmethod
    def confirm_delete(key_id: str) -> InlineKeyboardMarkup:
        """Confirmación de eliminación de llave."""
        keyboard = [
            [
                InlineKeyboardButton("✅ Sí, eliminar", callback_data=f"delete_execute_{key_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=f"key_detail_{key_id}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def generic_confirmation(action: str, item_id: str = "", back_callback: str = "main_menu") -> InlineKeyboardMarkup:
        """
        Confirmación genérica de acciones.
        
        Args:
            action: Tipo de acción a confirmar
            item_id: ID del elemento (opcional)
            back_callback: Callback para volver atrás
        """
        callback_yes = f"confirm_{action}_{item_id}" if item_id else f"confirm_{action}"
        callback_no = f"cancel_{action}"
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=callback_yes),
                InlineKeyboardButton("❌ Cancelar", callback_data=back_callback)
            ]
        ]
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
    
    # ============================================
    # QUICK ACTIONS
    # ============================================
    
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
    def back_to_server(server: str = 'main') -> InlineKeyboardMarkup:
        """
        Botón para volver al menú de servidores.
        """
        keyboard = [
            [InlineKeyboardButton("🔙 Volver", callback_data=f"key_submenu_{server}")]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    # ============================================
    # NAVIGATION HELPERS
    # ============================================
    
    @staticmethod
    def back_button(target: str = "main_menu") -> InlineKeyboardMarkup:
        """Botón de volver genérico."""
        keyboard = [
            [InlineKeyboardButton("🔙 Volver", callback_data=target)]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def _build_pagination_row(page: int, total_pages: int, callback_prefix: str) -> List[InlineKeyboardButton]:
        """
        Construye una fila de paginación reutilizable.
        
        Args:
            page: Página actual
            total_pages: Total de páginas
            callback_prefix: Prefijo para los callbacks (ej: 'key_submenu_page_wireguard')
            
        Returns:
            Lista de botones para la fila de paginación
        """
        pagination_row = []
        
        if page > 1:
            pagination_row.append(
                InlineKeyboardButton("⬅️", callback_data=f"{callback_prefix}_{page-1}")
            )
        
        pagination_row.append(
            InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop")
        )
        
        if page < total_pages:
            pagination_row.append(
                InlineKeyboardButton("➡️", callback_data=f"{callback_prefix}_{page+1}")
            )
        
        return pagination_row
