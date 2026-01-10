"""
Referral Feature - Sistema de Referidos

Este módulo contiene toda la funcionalidad relacionada con el sistema de referidos,
incluyendo gestión de códigos, enlaces, estadísticas y ganancias.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from .handlers.referral import ReferralHandler, get_referral_handlers, get_referral_callback_handlers

__all__ = [
    'ReferralHandler',
    'get_referral_handlers', 
    'get_referral_callback_handlers'
]
