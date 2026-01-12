"""
Announcer Feature - Sistema de Anuncios

Este módulo contiene toda la funcionalidad relacionada con el sistema de anuncios,
notificaciones masivas y comunicación con usuarios.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con puntos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_announcer",
    "telegram_bot/features/announcer/handlers_announcer.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.announcer"
sys.modules["handlers_announcer"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
AnnouncerHandler = module.AnnouncerHandler
get_announcer_handlers = module.get_announcer_handlers
get_announcer_callback_handlers = module.get_announcer_callback_handlers

__all__ = [
    'AnnouncerHandler',
    'get_announcer_handlers', 
    'get_announcer_callback_handlers'
]
