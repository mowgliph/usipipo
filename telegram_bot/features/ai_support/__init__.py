"""
AI Support Feature - Sistema de Soporte con IA

Este módulo contiene toda la funcionalidad relacionada con el soporte de inteligencia artificial,
incluyendo chatbot, generación de respuestas y análisis de conversaciones.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con puntos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_ai_support",
    "telegram_bot/features/ai_support/handlers_ai_support.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.ai_support"
sys.modules["handlers_ai_support"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
AiSupportHandler = module.AiSupportHandler
get_ai_support_handler = module.get_ai_support_handler
get_ai_callback_handlers = module.get_ai_callback_handlers

# Import direct message handler
from .direct_message_handler import DirectMessageHandler, get_direct_message_handler

__all__ = [
    'AiSupportHandler',
    'get_ai_support_handler',
    'get_ai_callback_handlers',
    'DirectMessageHandler',
    'get_direct_message_handler'
]
