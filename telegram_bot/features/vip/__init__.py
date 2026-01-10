"""
VIP Feature - Sistema de Membresía Premium

Este módulo contiene toda la funcionalidad relacionada con el sistema VIP,
incluyendo planes, actualizaciones, beneficios y gestión de suscripciones.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from .handlers.vip import VipHandler, get_vip_handlers, get_vip_callback_handlers

__all__ = [
    'VipHandler',
    'get_vip_handlers', 
    'get_vip_callback_handlers'
]
