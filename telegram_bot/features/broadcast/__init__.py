"""
Broadcast Feature - Sistema de Difusión Masiva

Este módulo contiene toda la funcionalidad relacionada con la difusión masiva
de mensajes, anuncios y comunicaciones a usuarios.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from .handlers.broadcast import BroadcastHandler, get_broadcast_handlers, get_broadcast_callback_handlers

__all__ = [
    'BroadcastHandler',
    'get_broadcast_handlers', 
    'get_broadcast_callback_handlers'
]
