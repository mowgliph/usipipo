"""
Task Management Feature - Sistema de Gestión de Tareas

Este módulo contiene toda la funcionalidad relacionada con la gestión de tareas,
asignación, seguimiento y administración de proyectos.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con puntos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_task_management",
    "telegram_bot/features/task_management/handlers_task_management.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.task_management"
sys.modules["handlers_task_management"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
TaskManagementHandler = module.TaskManagementHandler
get_task_management_handlers = module.get_task_management_handlers
get_task_management_callback_handlers = module.get_task_management_callback_handlers

__all__ = [
    'TaskManagementHandler',
    'get_task_management_handlers', 
    'get_task_management_callback_handlers'
]
