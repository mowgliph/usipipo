"""
Payments Feature - Sistema de Pagos

Este módulo contiene toda la funcionalidad relacionada con el sistema de pagos,
transacciones y gestión financiera.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con guiones bajos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_payments",
    "telegram_bot/features/payments/handlers_payments.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.payments"
sys.modules["handlers_payments"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
PaymentsHandler = module.PaymentsHandler
get_payments_handlers = module.get_payments_handlers
get_payments_callback_handlers = module.get_payments_callback_handlers

__all__ = [
    'PaymentsHandler',
    'get_payments_handlers', 
    'get_payments_callback_handlers'
]
