"""
User Management Feature - Sistema de Gestión de Usuarios

Este módulo contiene toda la funcionalidad relacionada con la gestión de usuarios,
perfiles, autenticación y autorización.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con puntos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_user_management",
    "telegram_bot/features/user_management/handlers_user_management.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.user_management"
sys.modules["handlers_user_management"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
UserManagementHandler = module.UserManagementHandler
get_user_management_handlers = module.get_user_management_handlers
get_user_callback_handlers = module.get_user_callback_handlers

__all__ = [
    'UserManagementHandler',
    'get_user_management_handlers', 
    'get_user_callback_handlers'
]
