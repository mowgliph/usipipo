"""
VPN Keys Feature - Gestión de Llaves VPN

Este módulo contiene toda la funcionalidad relacionada con la gestión de llaves VPN,
incluyendo creación, configuración, estadísticas y eliminación de llaves.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from .handlers.vpn_keys import VpnKeysHandler, get_vpn_keys_handler, get_vpn_keys_handlers, get_vpn_keys_callback_handlers

__all__ = [
    'VpnKeysHandler',
    'get_vpn_keys_handler', 
    'get_vpn_keys_handlers',
    'get_vpn_keys_callback_handlers'
]
