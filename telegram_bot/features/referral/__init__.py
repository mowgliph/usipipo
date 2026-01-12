"""
Referral Feature - Sistema de Referidos

Este módulo contiene toda la funcionalidad relacionada con el sistema de referidos,
programa de afiliados y recompensas por invitación.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con puntos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_referral",
    "telegram_bot/features/referral/handlers_referral.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.referral"
sys.modules["handlers_referral"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
ReferralHandler = module.ReferralHandler
get_referral_handlers = module.get_referral_handlers
get_referral_callback_handlers = module.get_referral_callback_handlers

__all__ = [
    'ReferralHandler',
    'get_referral_handlers', 
    'get_referral_callback_handlers'
]
