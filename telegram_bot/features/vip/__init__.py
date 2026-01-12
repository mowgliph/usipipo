"""
VIP Feature - Sistema VIP

Este módulo contiene toda la funcionalidad relacionada con el sistema VIP,
beneficios premium y gestión de membresías.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con puntos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_vip",
    "telegram_bot/features/vip/handlers_vip.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.vip"
sys.modules["handlers_vip"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
VipHandler = module.VipHandler
get_vip_handlers = module.get_vip_handlers
get_vip_callback_handlers = module.get_vip_callback_handlers

__all__ = [
    'VipHandler',
    'get_vip_handlers', 
    'get_vip_callback_handlers'
]
