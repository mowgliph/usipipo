# Refactored Keyboard Structure for uSipipo Bot

## Overview

The telegram_bot/keyboard module has been refactored from a monolithic structure into a modular, feature-based architecture. This improves maintainability, reduces redundancy, and follows SOLID principles.

## Structure

```
telegram_bot/keyboard/
├── user_keyboards.py          # Teclados para usuarios regulares
├── admin_keyboards.py          # Teclados para administración
├── operations_keyboards.py    # Teclados para operaciones y gamificación
├── common_keyboards.py        # Teclados comunes y reutilizables
├── keyboard_factory.py        # Fábrica y utilidades
├── inline_keyboards.py        # LEGACY - Retrocompatibilidad
├── keyboard.py                # LEGACY - ReplyKeyboards
├── key_submenu_keyboards.py   # LEGACY - Será consolidado
├── admin_keyboard.py          # LEGACY - Será consolidado
└── __init__.py               # Exports principales
```

## Module Breakdown

### 1. **user_keyboards.py** - User Features
Contiene todos los teclados para usuarios regulares:
- Main menu
- VPN key management (submenu, servidor específico, detalles, estadísticas)
- VPN type selection
- Confirmaciones y navegación

**Clase:** `UserKeyboards`

```python
from telegram_bot.keyboard import UserKeyboards

keyboard = UserKeyboards.main_menu(is_admin=False)
keyboard = UserKeyboards.my_keys_submenu(keys_summary)
keyboard = UserKeyboards.key_detail_menu(key_id, key_name, server_type)
```

### 2. **admin_keyboards.py** - Admin Features
Contiene todos los teclados para administradores:
- Admin main menu
- User management (list, pagination, detail, actions)
- Role and status selection
- Key management actions
- User confirmation dialogs

**Clase:** `AdminKeyboards`

```python
from telegram_bot.keyboard import AdminKeyboards

keyboard = AdminKeyboards.main_menu()
keyboard = AdminKeyboards.users_submenu()
keyboard = AdminKeyboards.user_detail_actions(user_id)
keyboard = AdminKeyboards.role_selection()
```

### 3. **operations_keyboards.py** - Gamification & Operations
Contiene tres clases principales:

#### OperationKeyboards
- Operations menu (balance, shop, games, referrals)
- VIP plans
- Referral program
- Achievements and rewards
- Games menu

#### SupportKeyboards
- Support menu
- Help menu
- Support tickets

#### TaskKeyboards
- Task center (user)
- Task list and detail
- Admin task management

```python
from telegram_bot.keyboard import OperationKeyboards, SupportKeyboards, TaskKeyboards

keyboard = OperationKeyboards.operations_menu(user)
keyboard = OperationKeyboards.achievements_menu()
keyboard = SupportKeyboards.help_menu()
keyboard = TaskKeyboards.task_center_menu()
```

### 4. **common_keyboards.py** - Reusable Patterns
Contiene patrones comunes reutilizables:
- Confirmations (generic, delete, yes/no)
- Navigation (back buttons, double navigation)
- Pagination (simple, full)
- Generic lists and choices
- Action buttons
- Special keyboards (loading, empty, noop)

**Clase:** `CommonKeyboards`

```python
from telegram_bot.keyboard import CommonKeyboards

# Confirmación genérica
keyboard = CommonKeyboards.generic_confirmation(
    action="delete_key",
    item_id=key_id,
    back_callback="my_keys"
)

# Paginación
buttons = CommonKeyboards.pagination_buttons(page, total, "users_page")

# Botones de acciones
keyboard = CommonKeyboards.action_buttons([
    ("✏️ Editar", "edit_item"),
    ("🗑️ Eliminar", "delete_item")
], "back_menu")
```

### 5. **keyboard_factory.py** - Factory & Utilities
Proporciona utilidades centralizadas:

#### KeyboardFactory
Patrón Factory para acceso dinámico a métodos de teclado:

```python
from telegram_bot.keyboard import KeyboardFactory, KeyboardType

# Crear dinámicamente
keyboard = KeyboardFactory.create_keyboard(
    KeyboardType.USER,
    "main_menu",
    is_admin=True
)

# Crear múltiples
keyboards = KeyboardFactory.create_multiple([
    ("menu", KeyboardType.USER, "main_menu", {"is_admin": False}),
    ("admin", KeyboardType.ADMIN, "main_menu", {}),
])
```

#### KeyboardBuilder
Constructor fluido para crear teclados complejos:

```python
from telegram_bot.keyboard import KeyboardBuilder

keyboard = (KeyboardBuilder()
    .add_button("Opción 1", "opt1", "🔘")
    .add_row([
        ("✏️", "Editar", "edit"),
        ("🗑️", "Eliminar", "delete")
    ])
    .add_pagination(page, total, "items_page")
    .add_confirmation_buttons("confirm", "cancel")
    .add_back_button("main_menu")
    .build())
```

#### KeyboardRegistry
Registro global de teclados predefinidos:

```python
from telegram_bot.keyboard import KeyboardRegistry

# Registrar
KeyboardRegistry.register("my_menu", UserKeyboards.main_menu)

# Obtener
keyboard = KeyboardRegistry.get("my_menu", is_admin=True)

# Listar
all_keyboards = KeyboardRegistry.list_keyboards()
```

## Consolidation of Redundancies

Se han consolidado los siguientes patrones redundantes:

### 1. Confirmación de Eliminación
**Antes:**
- `inline_keyboards.py`: `confirm_delete()`
- `admin_keyboard.py`: `confirm_delete()`
- `key_submenu_keyboards.py`: `confirm_delete()`

**Ahora:**
```python
UserKeyboards.confirm_delete(key_id)           # Para usuarios
AdminKeyboards.confirm_delete_key(key_id)      # Para admins
CommonKeyboards.delete_confirmation(...)       # Genérico
```

### 2. Botones de Navegación
**Antes:** Dispersos en diferentes archivos

**Ahora:** Centralizados en `CommonKeyboards`:
```python
CommonKeyboards.back_button()
CommonKeyboards.double_back_button()
CommonKeyboards.pagination_buttons()
```

### 3. Diálogos de Confirmación
**Antes:** Múltiples implementaciones

**Ahora:** Un patrón genérico:
```python
CommonKeyboards.generic_confirmation()
CommonKeyboards.yes_no_dialog()
```

### 4. Paginación
**Antes:** Código repetido en `key_submenu_keyboards.py` y otros

**Ahora:** Helper centralizado:
```python
UserKeyboards._build_pagination_row()
CommonKeyboards.pagination_buttons()
```

## Migration Guide

### For New Code
Use los módulos organizados por features:

```python
# ✅ BIEN - Nuevo código
from telegram_bot.keyboard import UserKeyboards, AdminKeyboards, CommonKeyboards

keyboard = UserKeyboards.main_menu(is_admin=is_admin)
keyboard = AdminKeyboards.users_submenu()
keyboard = CommonKeyboards.back_button("main_menu")
```

### For Existing Code (Backward Compatibility)
Los métodos legacy en `InlineKeyboards` siguen funcionando:

```python
# ⚠️ COMPATIBLE - Funciona pero deprecado
from telegram_bot.keyboard import InlineKeyboards

keyboard = InlineKeyboards.main_menu(is_admin=is_admin)
keyboard = InlineKeyboards.confirm_delete(key_id)

# Internamente delegan a:
# - UserKeyboards
# - AdminKeyboards  
# - CommonKeyboards
```

## Best Practices

### 1. Use Specific Classes
```python
# ✅ Mejor
from telegram_bot.keyboard import UserKeyboards

keyboard = UserKeyboards.key_detail_menu(key_id, name, "wireguard")
```

```python
# ❌ Evitar
from telegram_bot.keyboard import InlineKeyboards

keyboard = InlineKeyboards.key_detail_menu(...)  # No existe en nuevo código
```

### 2. Use CommonKeyboards for Reusable Patterns
```python
# ✅ Mejor - Reutilizable
keyboard = CommonKeyboards.generic_confirmation(
    action="delete",
    item_id=item_id,
    back_callback="menu"
)
```

```python
# ❌ Peor - Código duplicado
keyboard = [
    [
        InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_delete_{item_id}"),
        InlineKeyboardButton("❌ Cancelar", callback_data="menu")
    ]
]
```

### 3. Use KeyboardBuilder for Complex Keyboards
```python
# ✅ Bien - Legible y mantenible
keyboard = (KeyboardBuilder()
    .add_button("Opción 1", "opt1")
    .add_button("Opción 2", "opt2")
    .add_pagination(page, total, "items_page")
    .add_back_button("menu")
    .build())
```

### 4. Use KeyboardFactory for Dynamic Creation
```python
# ✅ Bien - Dinámico y desacoplado
keyboard = KeyboardFactory.create_keyboard(
    KeyboardType.USER,
    "main_menu",
    is_admin=user.is_admin()
)
```

## Handler Integration

Los handlers pueden usar la nueva estructura de dos formas:

### Opción 1: Direct Import (Recomendado)
```python
from telegram_bot.keyboard import UserKeyboards, CommonKeyboards

async def handle_keys_menu(update, context):
    keyboard = UserKeyboards.my_keys_submenu(keys_summary)
    await update.message.reply_text("Selecciona un servidor:", reply_markup=keyboard)
```

### Opción 2: Factory Pattern
```python
from telegram_bot.keyboard import KeyboardFactory, KeyboardType

async def handle_keys_menu(update, context):
    keyboard = KeyboardFactory.create_keyboard(
        KeyboardType.USER,
        "my_keys_submenu",
        keys_summary=keys_summary
    )
    await update.message.reply_text("Selecciona un servidor:", reply_markup=keyboard)
```

## Testing

Para testear teclados:

```python
from telegram_bot.keyboard import UserKeyboards, CommonKeyboards

def test_user_main_menu():
    keyboard = UserKeyboards.main_menu(is_admin=False)
    assert keyboard is not None
    assert len(keyboard.inline_keyboard) == 3  # 3 filas

def test_back_button():
    keyboard = CommonKeyboards.back_button("menu")
    assert keyboard.inline_keyboard[0][0].callback_data == "menu"

def test_factory():
    keyboard = KeyboardFactory.create_keyboard(
        KeyboardType.USER,
        "main_menu",
        is_admin=True
    )
    assert keyboard is not None
```

## Files to Remove (Soon)

Los siguientes archivos son legacy y serán removidos en futuras versiones:
- `key_submenu_keyboards.py` - Contenido consolidado en `UserKeyboards`
- `admin_keyboard.py` - Contenido consolidado en `AdminKeyboards`
- `keyboard.py` - ReplyKeyboards legacy

Mientras tanto, mantienen compatibilidad backward compatible.

## Files to Update (Handlers)

Los handlers que aún usen los módulos legacy deberían actualizarse:

```bash
# Handlers que necesitan actualización
telegram_bot/handlers/
  ├── start_handler.py
  ├── status_handler.py
  ├── operations_handler.py
  ├── admin_handler.py
  ├── admin_users_callbacks.py
  ├── achievement_handler.py
  ├── task_handler.py
  ├── game_handler.py
  ├── shop_handler.py
  ├── referral_handler.py
  ├── support_handler.py
  └── ... (y otros)
```

Actualizar imports:
```python
# ❌ Viejo
from telegram_bot.keyboard.key_submenu_keyboards import KeySubmenuKeyboards
from telegram_bot.keyboard.admin_keyboard import AdminKeyboard
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards

# ✅ Nuevo
from telegram_bot.keyboard import UserKeyboards, AdminKeyboards, CommonKeyboards
```

## Summary of Benefits

1. **Modular Architecture**: Código organizad por features, no por tipo
2. **Reduced Redundancy**: Patrones comunes consolidados
3. **SOLID Principles**: Single responsibility, Open/Closed, etc.
4. **Backward Compatible**: Código legacy sigue funcionando
5. **Centralized Access**: Factory pattern para acceso dinámico
6. **Fluent Builder**: Construcción declarativa de teclados complejos
7. **Easy Maintenance**: Cambios en un lugar, reflejan en todas partes
8. **Testability**: Mejor para escribir tests unitarios
9. **Type Safe**: Enums y tipos claros
10. **Documentation**: Cada módulo bien documentado

## Next Steps

1. Actualizar handlers para usar nuevos módulos
2. Remover archivos legacy
3. Extender tests para cubrir todos los teclados
4. Considerar añadir más helpers según necesidad
