"""
Admin Feature - Panel Administrativo

Este módulo contiene toda la funcionalidad relacionada con la administración del bot,
incluyendo gestión de usuarios, llaves, estadísticas y configuración del sistema.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from .handlers.admin import AdminHandler, get_admin_handlers, get_admin_callback_handlers

__all__ = [
    'AdminHandler',
    'get_admin_handlers', 
    'get_admin_callback_handlers'
]
