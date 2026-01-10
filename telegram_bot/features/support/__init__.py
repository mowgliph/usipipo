"""
Support Feature - Sistema de Soporte Técnico

Este módulo contiene toda la funcionalidad relacionada con el soporte técnico,
incluyendo tickets, chat con admin, FAQ y gestión de incidencias.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from .handlers.support import SupportHandler, get_support_handlers, get_support_callback_handlers

__all__ = [
    'SupportHandler',
    'get_support_handlers', 
    'get_support_callback_handlers'
]
