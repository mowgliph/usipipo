"""
AI Support Feature - Asistente IA Sip

Este módulo contiene toda la funcionalidad relacionada con el asistente de IA
para soporte de usuarios, incluyendo handlers, mensajes y teclados específicos.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from .handlers import AiSupportHandler, get_ai_support_handler, get_ai_callback_handlers

__all__ = [
    'AiSupportHandler',
    'get_ai_support_handler', 
    'get_ai_callback_handlers'
]
