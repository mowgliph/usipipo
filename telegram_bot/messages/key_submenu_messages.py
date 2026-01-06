"""
Mensajes para el sistema de submenús de llaves VPN del bot uSipipo.
Proporciona mensajes organizados por servidor con funcionalidad de gestión avanzada.

Author: uSipipo Team
Version: 2.0.0 - Sistema de submenús para llaves
"""

from datetime import datetime
from typing import Dict, Any


class KeySubmenuMessages:
    """Mensajes para el sistema de submenús de llaves VPN."""
    
    # Menú principal de submenú
    MAIN_MENU = (
        "🛡️ **Centro de Gestión de Llaves**\n"
        "━━━━━━━━━━━━\n\n"
        "Administra tus conexiones VPN organizadas por servidor:\n"
    )
    
    # Headers por tipo de servidor
    WIREGUARD_HEADER = (
        "🟦 **WireGuard Server**\n"
        "━━━━━━━━━━━━\n"
        "Protocolo de alta velocidad para PC y gaming\n"
    )
    
    OUTLINE_HEADER = (
        "🟩 **Outline Server**\n"
        "━━━━━━━━━━━━\n"
        "Protocolo ligero ideal para móviles\n"
    )
    
    # Lista de llaves por servidor (muestra en bloque de cita)
    SERVER_KEYS_LIST = (
        "🔑 **Llaves en {server_name}:**\n"
        "━━━━━━━━━━━━\n\n"
        "{keys_list}\n"
        "━━━━━━━━━━━━━"
    )
    
    # Vista detallada de llave
    KEY_DETAIL_ENHANCED = (
        "🔑 **Detalle de Llave**\n"
        "━━━━━━━━━━━━\n\n"
        "📌 **Nombre:** {name}\n"
        "📡 **Protocolo:** {protocol}\n"
        "🆔 **ID:** `{key_id}`\n"
        "📅 **Creada:** {created_date}\n"
        "📊 **Datos:** {used_gb} GB / {limit_gb} GB\n"
        "⚡ **Estado:** {status}\n"
        "━━━━━━━━━━━━\n"
        "{server_info}"
    )
    
    # Menú de acciones para llaves
    KEY_ACTIONS_MENU = (
        "⚙️ **Acciones para {key_name}**\n"
        "━━━━━━━━━━━━\n\n"
        "¿Qué deseas hacer con esta llave?"
    )
    
    # Estados y badges
    @staticmethod
    def get_status_badge(key_data: Dict[str, Any]) -> str:
        """Genera badge de estado según los datos de la llave."""
        if not key_data.get('is_active', False):
            return "🔴 Inactiva"
        
        usage_percent = (key_data.get('used_gb', 0) / key_data.get('limit_gb', 1)) * 100
        
        if usage_percent >= 90:
            return "🟡 Límite cerca"
        elif usage_percent >= 100:
            return "🔴 Límite agotado"
        else:
            return "🟢 Activa"
    
    @staticmethod
    def get_server_badge(server_type: str) -> str:
        """Genera badge según el tipo de servidor."""
        if server_type.upper() == 'WIREGUARD':
            return "🟦 WireGuard"
        elif server_type.upper() == 'OUTLINE':
            return "🟩 Outline"
        else:
            return "🔧 Desconocido"
    
    @staticmethod
    def format_key_list(keys: list, server_type: str) -> str:
        """Formatea la lista de llaves para mostrar (prefija cada línea con '> ' para cita)."""
        if not keys:
            return f"> No hay llaves en {server_type}"
        
        formatted_keys = []
        for i, key in enumerate(keys, 1):
            status_badge = KeySubmenuMessages.get_status_badge(key)
            name = key.get('name', f'Llave {i}')
            usage = f"{key.get('used_gb', 0):.1f} GB"
            
            formatted_keys.append(
                f"{i}. **{name}** {status_badge}\n"
                f"   📊 {usage} / {key.get('limit_gb', 0):.1f} GB"
            )
        
        raw = "\n".join(formatted_keys)
        # Prefijar cada línea con '> ' para que Telegram lo muestre como cita en Markdown
        return "\n".join(f"> {line}" if line.strip() != "" else ">" for line in raw.splitlines())
    
    @staticmethod
    def format_server_info(server_data: Dict[str, Any]) -> str:
        """Formatea información adicional del servidor."""
        if not server_data:
            return ""
        
        location = server_data.get('location', 'Desconocido')
        ping = server_data.get('ping', 'N/A')
        load = server_data.get('load', 'N/A')
        
        return (
            f"📍 **Servidor:** {location}\n"
            f"⏱️ **Ping:** {ping}ms\n"
            f"📈 **Carga:** {load}%"
        )
    
    # Mensajes de error específicos
    NO_KEYS_IN_SERVER = (
        "📭 **Sin llaves en {server_name}**\n\n"
        "Aún no tienes conexiones configuradas en este servidor.\n"
        "👉 Toca **➕ Crear Nueva** para generar tu primera llave."
    )
    
    SERVER_NOT_AVAILABLE = (
        "⚠️ **Servidor no disponible**\n\n"
        "El servidor {server_name} no está disponible en este momento.\n"
        "Intenta más tarde o usa otro protocolo."
    )
    
    KEY_LIMIT_REACHED_SERVER = (
        "🔒 **Límite alcanzado en {server_name}**\n\n"
        "Has alcanzado el máximo de llaves permitidas en este servidor.\n\n"
        "💡 **Opciones:**\n"
        "• Elimina una llave existente\n"
        "• Actualiza a VIP para más llaves"
    )
    
    # Mensajes de navegación
    PAGINATION_INFO = (
        "📄 **Página {current} de {total}**\n"
        "━━━━━━━━━━━━"
    )
    
    QUICK_ACTIONS_HINT = (
        "⚡ **Acciones Rápidas:**\n"
        "• Ver todas las llaves\n"
        "• Crear nueva llave"
    )