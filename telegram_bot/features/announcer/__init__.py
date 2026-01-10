"""
Announcer Feature - Sistema de Anuncios

Este módulo contiene toda la funcionalidad relacionada con el sistema de anuncios,
campañas de marketing y comunicación masiva.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from .handlers.announcer import AnnouncerHandler, get_announcer_handlers, get_announcer_callback_handlers

__all__ = [
    'AnnouncerHandler',
    'get_announcer_handlers', 
    'get_announcer_callback_handlers'
]
