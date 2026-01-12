"""
Admin Feature - Panel Administrativo

Este módulo contiene toda la funcionalidad relacionada con la administración del bot,
incluyendo gestión de usuarios, llaves, estadísticas y configuración del sistema.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con puntos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_admin",
    "telegram_bot/features/admin/handlers_admin.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.admin"
sys.modules["handlers_admin"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
AdminHandler = module.AdminHandler
get_admin_handlers = module.get_admin_handlers
get_admin_callback_handlers = module.get_admin_callback_handlers

__all__ = [
    'AdminHandler',
    'get_admin_handlers', 
    'get_admin_callback_handlers'
]
