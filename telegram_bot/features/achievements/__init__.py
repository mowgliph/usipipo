"""
Achievements Feature - Sistema de Logros

Este módulo contiene toda la funcionalidad relacionada con el sistema de logros,
recompensas y progreso de usuarios.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con puntos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_achievements",
    "telegram_bot/features/achievements/handlers_achievements.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.achievements"
sys.modules["handlers_achievements"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
AchievementsHandler = module.AchievementsHandler
get_achievements_handlers = module.get_achievements_handlers
get_achievements_callback_handlers = module.get_achievements_callback_handlers

__all__ = [
    'AchievementsHandler',
    'get_achievements_handlers', 
    'get_achievements_callback_handlers'
]
