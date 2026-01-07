# Keyboard Refactoring - Handler Migration Checklist

This document provides a checklist for updating handlers to use the new keyboard structure.

## Status Overview

| Component | Status | Priority |
|-----------|--------|----------|
| Keyboard modules refactored | ✅ DONE | - |
| Factory/utilities created | ✅ DONE | - |
| Backward compatibility | ✅ DONE | - |
| Documentation | ✅ DONE | - |
| Handler migration | ⏳ TODO | HIGH |
| Legacy file removal | ⏳ TODO | MEDIUM |
| Full test coverage | ⏳ TODO | HIGH |

## Handler Categories to Update

### 1. **User Feature Handlers** (8 files)
Handlers dealing with user functionality:

- [ ] `start_handler.py` - Main menu on /start
- [ ] `status_handler.py` - User status/profile
- [ ] `crear_llave_handler.py` - Key creation flow
- [ ] `operations_handler.py` - Operations menu (balance, shop, games)
- [ ] `referral_handler.py` - Referral system
- [ ] `achievement_handler.py` - Achievements and rewards
- [ ] `task_handler.py` - User task management
- [ ] `game_handler.py` - Game menus

**Current imports to replace:**
```python
# ❌ OLD
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards
from telegram_bot.keyboard.key_submenu_keyboards import KeySubmenuKeyboards

# ✅ NEW
from telegram_bot.keyboard import UserKeyboards, TaskKeyboards, CommonKeyboards
```

### 2. **Admin Handlers** (4 files)
Handlers for administrative functions:

- [ ] `admin_handler.py` - Admin main menu
- [ ] `admin_users_callbacks.py` - User management
- [ ] `admin_task_handler.py` - Task administration
- [ ] `support_handler.py` - Support/ticket system

**Current imports to replace:**
```python
# ❌ OLD
from telegram_bot.keyboard.admin_keyboard import AdminKeyboard
from telegram_bot.keyboard.inline_keyboards import InlineAdminKeyboards

# ✅ NEW
from telegram_bot.keyboard import AdminKeyboards, TaskKeyboards, SupportKeyboards
```

### 3. **Special Role Handlers** (2 files)
Handlers for premium/special user roles:

- [ ] `user_task_manager_handler.py` - Task manager role
- [ ] `user_announcer_handler.py` - Announcer role

**Current imports to replace:**
```python
# ❌ OLD
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards

# ✅ NEW
from telegram_bot.keyboard import OperationKeyboards, TaskKeyboards
```

### 4. **Support Handlers** (2 files)
Support-related handlers:

- [ ] `support_menu_handler.py` - Support menu
- [ ] `support_handler.py` - Support tickets

**Current imports to replace:**
```python
# ❌ OLD
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards

# ✅ NEW
from telegram_bot.keyboard import SupportKeyboards, CommonKeyboards
```

### 5. **Shop/Payment Handlers** (2 files)
Shop and payment related:

- [ ] `shop_handler.py` - Shop menu and items
- [ ] `payment_handler.py` - Payment processing

**Current imports to replace:**
```python
# ❌ OLD
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards

# ✅ NEW
from telegram_bot.keyboard import OperationKeyboards, CommonKeyboards
```

## Migration Steps Per Handler

### Step 1: Identify Current Keyboard Usage
Review the handler file and note all keyboard usages:

```python
# Example: start_handler.py
def get_main_menu(update, context):
    is_admin = check_admin(user_id)
    keyboard = InlineKeyboards.main_menu(is_admin=is_admin)  # <-- FOUND
    # ...
```

### Step 2: Map to New Classes
Find the appropriate new class and method:

| Old Method | New Class | New Method |
|-----------|-----------|-----------|
| `InlineKeyboards.main_menu()` | `UserKeyboards` | `main_menu()` |
| `InlineKeyboards.operations_menu()` | `OperationKeyboards` | `operations_menu()` |
| `InlineAdminKeyboards.main_menu()` | `AdminKeyboards` | `main_menu()` |
| `KeySubmenuKeyboards.main_menu()` | `UserKeyboards` | `my_keys_submenu()` |
| `AdminKeyboard.confirm_delete()` | `AdminKeyboards` | `confirm_delete_key()` |
| `InlineKeyboards.back_button()` | `CommonKeyboards` | `back_button()` |

### Step 3: Update Imports
Replace the old imports with new ones:

```python
# ❌ OLD
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards, InlineAdminKeyboards
from telegram_bot.keyboard.key_submenu_keyboards import KeySubmenuKeyboards
from telegram_bot.keyboard.admin_keyboard import AdminKeyboard

# ✅ NEW
from telegram_bot.keyboard import (
    UserKeyboards,
    AdminKeyboards,
    OperationKeyboards,
    SupportKeyboards,
    TaskKeyboards,
    CommonKeyboards
)
```

### Step 4: Update Method Calls
Replace the old method calls with new ones:

```python
# ❌ OLD
keyboard = InlineKeyboards.main_menu(is_admin=is_admin)
keyboard = InlineKeyboards.confirm_action("delete", key_id)
keyboard = AdminKeyboard.confirm_delete(key_id)

# ✅ NEW
keyboard = UserKeyboards.main_menu(is_admin=is_admin)
keyboard = CommonKeyboards.generic_confirmation("delete", key_id)
keyboard = AdminKeyboards.confirm_delete_key(key_id)
```

### Step 5: Test
Ensure the handler still works:

```bash
# Run specific handler tests
pytest tests/handlers/test_start_handler.py -v

# Run integration tests
pytest tests/integration/ -v
```

## File-by-File Migration Guide

### start_handler.py
```python
# Old
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards

keyboard = InlineKeyboards.main_menu(is_admin=is_admin)

# New
from telegram_bot.keyboard import UserKeyboards

keyboard = UserKeyboards.main_menu(is_admin=is_admin)
```

### crear_llave_handler.py
```python
# Old
from telegram_bot.keyboard.key_submenu_keyboards import KeySubmenuKeyboards

keyboard = KeySubmenuKeyboards.main_menu(keys_summary)
keyboard = KeySubmenuKeyboards.server_keys_menu(server_type, keys, page, total_pages)

# New
from telegram_bot.keyboard import UserKeyboards

keyboard = UserKeyboards.my_keys_submenu(keys_summary)
keyboard = UserKeyboards.server_keys_menu(server_type, keys, page, total_pages)
```

### admin_handler.py
```python
# Old
from telegram_bot.keyboard.inline_keyboards import InlineAdminKeyboards

keyboard = InlineAdminKeyboards.main_menu()
keyboard = InlineAdminKeyboards.users_submenu()

# New
from telegram_bot.keyboard import AdminKeyboards

keyboard = AdminKeyboards.main_menu()
keyboard = AdminKeyboards.users_submenu()
```

### admin_users_callbacks.py
```python
# Old
from telegram_bot.keyboard.inline_keyboards import InlineAdminKeyboards

keyboard = InlineAdminKeyboards.users_list_pagination(page, total)
keyboard = InlineAdminKeyboards.user_detail_actions(user_id)

# New
from telegram_bot.keyboard import AdminKeyboards

keyboard = AdminKeyboards.users_list_pagination(page, total)
keyboard = AdminKeyboards.user_detail_actions(user_id)
```

### operations_handler.py
```python
# Old
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards

keyboard = InlineKeyboards.operations_menu(user)
keyboard = InlineKeyboards.vip_plans()
keyboard = InlineKeyboards.achievements_menu()

# New
from telegram_bot.keyboard import OperationKeyboards

keyboard = OperationKeyboards.operations_menu(user)
keyboard = OperationKeyboards.vip_plans()
keyboard = OperationKeyboards.achievements_menu()
```

### support_handler.py
```python
# Old
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards

keyboard = InlineKeyboards.support_menu()
keyboard = InlineKeyboards.help_menu()

# New
from telegram_bot.keyboard import SupportKeyboards

keyboard = SupportKeyboards.support_menu()
keyboard = SupportKeyboards.help_menu()
```

### task_handler.py
```python
# Old
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards

keyboard = InlineKeyboards.task_center_menu()
keyboard = InlineKeyboards.task_list_keyboard(tasks)

# New
from telegram_bot.keyboard import TaskKeyboards

keyboard = TaskKeyboards.task_center_menu()
keyboard = TaskKeyboards.task_list_keyboard(tasks)
```

### achievement_handler.py
```python
# Old
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards

keyboard = InlineKeyboards.achievements_menu()
keyboard = InlineKeyboards.achievements_categories()

# New
from telegram_bot.keyboard import OperationKeyboards

keyboard = OperationKeyboards.achievements_menu()
keyboard = OperationKeyboards.achievements_categories()
```

## Testing Checklist

After updating each handler, verify:

- [ ] Handler imports without errors
- [ ] Keyboard methods return valid `InlineKeyboardMarkup` objects
- [ ] Callback data matches handler expectations
- [ ] Inline buttons render correctly in Telegram
- [ ] Navigation flows work (back buttons, next/previous, etc.)
- [ ] No deprecation warnings in logs

## Automated Migration Script (Optional)

A simple find-and-replace guide:

```bash
# Replace imports
find . -name "*.py" -type f -exec sed -i \
  's/from telegram_bot\.keyboard\.inline_keyboards import InlineKeyboards/from telegram_bot.keyboard import UserKeyboards, AdminKeyboards, OperationKeyboards, SupportKeyboards, TaskKeyboards, CommonKeyboards/g' \
  {} \;

# Replace method calls (example)
find . -name "*.py" -type f -exec sed -i \
  's/InlineKeyboards\.main_menu/UserKeyboards.main_menu/g' \
  {} \;
```

## Migration Priority

**Priority 1 (Critical):**
- [ ] start_handler.py
- [ ] admin_handler.py
- [ ] operations_handler.py

**Priority 2 (High):**
- [ ] crear_llave_handler.py
- [ ] admin_users_callbacks.py
- [ ] task_handler.py

**Priority 3 (Medium):**
- [ ] achievement_handler.py
- [ ] support_handler.py
- [ ] referral_handler.py

**Priority 4 (Low):**
- [ ] shop_handler.py
- [ ] payment_handler.py
- [ ] user_task_manager_handler.py
- [ ] user_announcer_handler.py

## Rollback Plan

If issues arise during migration:

1. Check git history:
   ```bash
   git log --oneline telegram_bot/handlers/
   ```

2. Revert specific handler:
   ```bash
   git checkout HEAD~1 telegram_bot/handlers/start_handler.py
   ```

3. The backward compatibility layer ensures old code still works

## Validation Checklist

After all handlers are migrated:

- [ ] All handlers compile without errors
- [ ] No import errors in any file
- [ ] Bot starts successfully
- [ ] Main menu works for regular users
- [ ] Admin menu works for admins
- [ ] All keyboard callbacks execute
- [ ] No deprecation warnings in logs
- [ ] Integration tests pass
- [ ] Manual testing on development bot

## Support

If you encounter issues:

1. Check [KEYBOARD_REFACTORING_GUIDE.md](KEYBOARD_REFACTORING_GUIDE.md) for detailed docs
2. Review the usage examples in each keyboard class docstring
3. Look at the mapping tables in this document
4. Check backward compatibility layer still works

## Timeline Estimate

- **Phase 1** (Priority 1): 2-3 hours
- **Phase 2** (Priority 2): 3-4 hours  
- **Phase 3** (Priority 3): 2-3 hours
- **Phase 4** (Priority 4): 1-2 hours
- **Testing & Validation**: 2-3 hours

**Total Estimated Time:** 10-15 hours

---

**Last Updated:** January 7, 2026  
**Status:** Ready for Handler Migration
