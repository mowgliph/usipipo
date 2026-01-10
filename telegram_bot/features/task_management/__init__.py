"""
Task Management Feature - Sistema de Gestión de Tareas

Este módulo contiene toda la funcionalidad relacionada con la gestión de tareas,
asignación, seguimiento y administración de proyectos.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from .handlers.task_management import TaskManagementHandler, get_task_management_handlers, get_task_management_callback_handlers

__all__ = [
    'TaskManagementHandler',
    'get_task_management_handlers', 
    'get_task_management_callback_handlers'
]
