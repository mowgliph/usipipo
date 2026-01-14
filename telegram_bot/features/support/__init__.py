"""
Support Feature - Sistema de Soporte

Este módulo contiene toda la funcionalidad relacionada con el sistema de soporte,
tickets, atención al cliente y resolución de problemas.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con puntos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_support",
    "telegram_bot/features/support/handlers_support.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.support"
sys.modules["handlers_support"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
SupportHandler = module.SupportHandler
get_support_handlers = module.get_support_handlers
get_support_callback_handlers = module.get_support_callback_handlers
get_support_conversation_handler = module.get_support_conversation_handler

__all__ = [
    'SupportHandler',
    'get_support_handlers',
    'get_support_callback_handlers',
    'get_support_conversation_handler'
]
