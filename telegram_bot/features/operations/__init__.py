"""
Operations Feature - Sistema de Operaciones

Este módulo contiene toda la funcionalidad relacionada con las operaciones principales
del bot, incluyendo comandos básicos y flujo de trabajo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con guiones bajos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_operations",
    "telegram_bot/features/operations/handlers_operations.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.operations"
sys.modules["handlers_operations"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
OperationsHandler = module.OperationsHandler
get_operations_handlers = module.get_operations_handlers
get_operations_callback_handlers = module.get_operations_callback_handlers

__all__ = [
    'OperationsHandler',
    'get_operations_handlers', 
    'get_operations_callback_handlers'
]
