"""
Shop Feature - Sistema de Tienda

Este módulo contiene toda la funcionalidad relacionada con la tienda,
productos, compras y gestión de inventario.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

import importlib.util
import sys

# Importar el módulo con nombre de archivo con puntos usando importlib
spec = importlib.util.spec_from_file_location(
    "handlers_shop",
    "telegram_bot/features/shop/handlers_shop.py"
)
module = importlib.util.module_from_spec(spec)
module.__package__ = "telegram_bot.features.shop"
sys.modules["handlers_shop"] = module
spec.loader.exec_module(module)

# Importar los símbolos específicos desde el módulo cargado
ShopHandler = module.ShopHandler
get_shop_handlers = module.get_shop_handlers
get_shop_callback_handlers = module.get_shop_callback_handlers

__all__ = [
    'ShopHandler',
    'get_shop_handlers', 
    'get_shop_callback_handlers'
]
