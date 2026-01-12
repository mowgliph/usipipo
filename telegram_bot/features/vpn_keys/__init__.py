"""
VPN Keys Feature - Sistema de Gestión de Llaves VPN

Este módulo contiene toda la funcionalidad relacionada con la gestión de llaves VPN,
generación, validación y administración de acceso a la red privada.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con puntos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_vpn_keys",
    "telegram_bot/features/vpn_keys/handlers_vpn_keys.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.vpn_keys"
sys.modules["handlers_vpn_keys"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
VpnKeysHandler = module.VpnKeysHandler
get_vpn_keys_handler = module.get_vpn_keys_handler
get_vpn_keys_handlers = module.get_vpn_keys_handlers
get_vpn_keys_callback_handlers = module.get_vpn_keys_callback_handlers

__all__ = [
    'VpnKeysHandler',
    'get_vpn_keys_handler',
    'get_vpn_keys_handlers', 
    'get_vpn_keys_callback_handlers'
]
