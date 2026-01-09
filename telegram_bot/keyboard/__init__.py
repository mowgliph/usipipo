"""
Módulo de teclados para el bot uSipipo.

Organiza los teclados por features:
- user_keyboards: Teclados para usuarios regulares
- admin_keyboards: Teclados para administradores
- operations_keyboards: Teclados para operaciones financieras
- common_keyboards: Teclados comunes y reutilizables
- keyboard_factory: Fábrica centralizada y helpers

Author: uSipipo Team
Version: 3.0.0 - Deprecated legacy code removed
"""

# New modular imports
from .user_keyboards import UserKeyboards
from .admin_keyboards import AdminKeyboards
from .operations_keyboards import OperationKeyboards, SupportKeyboards, TaskKeyboards
from .common_keyboards import CommonKeyboards
from .shop_keyboards import ShopKeyboards
from .keyboard_factory import KeyboardFactory, KeyboardBuilder, KeyboardRegistry, KeyboardType

__all__ = [
    # New modular exports
    'UserKeyboards',
    'AdminKeyboards',
    'OperationKeyboards',
    'SupportKeyboards',
    'TaskKeyboards',
    'CommonKeyboards',
    'ShopKeyboards',
    # Factory and utilities
    'KeyboardFactory',
    'KeyboardBuilder',
    'KeyboardRegistry',
    'KeyboardType',
]
