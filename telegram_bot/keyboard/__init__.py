"""
Módulo de teclados para el bot uSipipo.

Organiza los teclados por features:
- user_keyboards: Teclados para usuarios regulares
- admin_keyboards: Teclados para administradores
- operations_keyboards: Teclados para operaciones financieras
- common_keyboards: Teclados comunes y reutilizables
- keyboard_factory: Fábrica centralizada y helpers
- inline_keyboards: Teclados legacy (en transición)

Author: uSipipo Team
Version: 2.0.0 - Refactored keyboard structure
"""

# Legacy imports (deprecados pero mantenidos para compatibilidad)
from .keyboard import Keyboards
from .inline_keyboards import InlineKeyboards, InlineAdminKeyboards

# New modular imports
from .user_keyboards import UserKeyboards
from .admin_keyboards import AdminKeyboards
from .operations_keyboards import OperationKeyboards, SupportKeyboards, TaskKeyboards
from .common_keyboards import CommonKeyboards
from .shop_keyboards import ShopKeyboards
from .keyboard_factory import KeyboardFactory, KeyboardBuilder, KeyboardRegistry, KeyboardType

__all__ = [
    # Legacy exports
    'Keyboards',
    'InlineKeyboards',
    'InlineAdminKeyboards',
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
