"""
Shop Feature - Sistema de Comercio Electrónico

Este módulo contiene toda la funcionalidad relacionada con el sistema de tienda,
incluyendo catálogo, carrito de compras, procesamiento de pedidos y gestión de productos.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from .handlers.shop import ShopHandler, get_shop_handlers, get_shop_callback_handlers

__all__ = [
    'ShopHandler',
    'get_shop_handlers', 
    'get_shop_callback_handlers'
]
