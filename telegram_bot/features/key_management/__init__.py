"""
Key Management Feature - Sistema de Gestión de Llaves

Este módulo contiene toda la funcionalidad relacionada con la gestión de llaves,
generación, validación y administración de acceso.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con puntos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_key_management",
    "telegram_bot/features/key_management/handlers_key_management.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.key_management"
sys.modules["handlers_key_management"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
KeyManagementHandler = module.KeyManagementHandler
get_key_management_handlers = module.get_key_management_handlers
get_key_management_callback_handlers = module.get_key_management_callback_handlers

__all__ = [
    'KeyManagementHandler',
    'get_key_management_handlers', 
    'get_key_management_callback_handlers'
]
