"""
Game Feature - Sistema de Juegos

Este módulo contiene toda la funcionalidad relacionada con el sistema de juegos,
competiciones y actividades interactivas.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con guiones bajos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_game",
    "telegram_bot/features/game/handlers_game.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.game"
sys.modules["handlers_game"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
GameHandler = module.GameHandler
get_game_handlers = module.get_game_handlers
get_game_callback_handlers = module.get_game_callback_handlers

__all__ = [
    'GameHandler',
    'get_game_handlers', 
    'get_game_callback_handlers'
]
