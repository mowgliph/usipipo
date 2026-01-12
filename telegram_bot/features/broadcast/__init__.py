"""
Broadcast Feature - Sistema de Transmisión

Este módulo contiene toda la funcionalidad relacionada con el sistema de transmisión,
difusión de mensajes y comunicación masiva.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con puntos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_broadcast",
    "telegram_bot/features/broadcast/handlers_broadcast.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.broadcast"
sys.modules["handlers_broadcast"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
BroadcastHandler = module.BroadcastHandler
get_broadcast_handlers = module.get_broadcast_handlers
get_broadcast_callback_handlers = module.get_broadcast_callback_handlers

__all__ = [
    'BroadcastHandler',
    'get_broadcast_handlers', 
    'get_broadcast_callback_handlers'
]
