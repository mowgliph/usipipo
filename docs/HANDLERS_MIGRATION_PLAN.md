# Plan de Migración de Handlers a Nuevos Message Classes

## Estado General
- **Handlers encontrados:** 31 total
- **Handlers a migrar:** 18 (usando `Messages` legacy)
- **Handlers ya migrados:** 5 (ya usan `*Messages`)
- **Status:** En Progreso

## Mapeo de Handlers por Categoría

### 🟢 YA MIGRADOS (5)
1. `game_handler.py` - Usa `GameMessages`
2. `achievement_handler.py` - Usa `AchievementMessages`
3. `key_submenu_handler.py` - Usa `KeySubmenuMessages`
4. `admin_users_handler.py` - Usa `AdminMessages`
5. `admin_users_callbacks.py` - Usa `AdminMessages`

### 🔴 POR MIGRAR (18)

#### User Messages (8)
- `start_handler.py` → `UserMessages`
- `info_handler.py` → `UserMessages`
- `ayuda_handler.py` → `UserMessages`
- `keys_manager_handler.py` → `UserMessages`
- `crear_llave_handler.py` → `UserMessages`
- `status_handler.py` → `UserMessages`
- `user_announcer_handler.py` → `UserMessages`
- `user_task_manager_handler.py` → `UserMessages`

#### Admin Messages (3)
- `admin_handler.py` → `AdminMessages`
- `admin_task_handler.py` → `AdminMessages`
- `broadcast_handler.py` → `AdminMessages` (estimado)

#### Operation Messages (4)
- `operations_handler.py` → `OperationMessages`
- `payment_handler.py` → `OperationMessages`
- `referral_handler.py` → `OperationMessages`
- `shop_handler.py` → `OperationMessages`

#### Support Messages (2)
- `support_handler.py` → `SupportMessages`
- `support_menu_handler.py` → `SupportMessages`

#### Mixed/General (1)
- `cancel_handler.py` → `CommonMessages` (para Cancel)
- `error_handler.py` → `CommonMessages` (para Errors)
- `inline_callbacks_handler.py` → Mixed
- `handler_initializer.py` → Actualizar imports
- `task_handler.py` → `TaskMessages`
- `juega_y_gana_handler.py` → `GameMessages`
- `monitoring_handler.py` → Sin referencias (revisar)

## Mapeo Detallado de Referencias

### Legacy Message Classes → New Message Classes

| Legacy | New Location | Clase New | Nota |
|--------|--------------|-----------|------|
| `Messages.Welcome.*` | `user_messages.py` | `UserMessages.Welcome` | Bienvenida |
| `Messages.Keys.*` | `user_messages.py` | `UserMessages.Keys` | Gestión llaves usuario |
| `Messages.Status.*` | `user_messages.py` | `UserMessages.Status` | Estado usuario |
| `Messages.Help.*` | `user_messages.py` | `UserMessages.Help` | Ayuda |
| `Messages.Confirmation.*` | `user_messages.py` | `UserMessages.Confirmation` | Confirmaciones |
| `Messages.Errors.*` | Mixed | Ver tabla errors | Errores genéricos |
| `Messages.Cancel.CANCEL_MESSAGE` | `common_messages.py` | `CommonMessages.Confirmation.CANCELLED` | Cancelación |
| `Messages.Admin.*` | `admin_messages.py` | `AdminMessages.*` | Admin |
| `Messages.Tasks.*` | `support_messages.py` | `TaskMessages.*` | Tareas |
| `Messages.Support.*` | `support_messages.py` | `SupportMessages.*` | Soporte |
| `Messages.Operations.*` | `operations_messages.py` | `OperationMessages.*` | Operaciones |

## Patrón de Migración

### Antes:
```python
from telegram_bot.messages.messages import Messages

text = Messages.Welcome.NEW_USER.format(name=user.first_name)
```

### Después:
```python
from telegram_bot.messages import UserMessages

text = UserMessages.Welcome.NEW_USER.format(name=user.first_name)
```

## Herramientas de Búsqueda/Reemplazo por Handler

### 1. start_handler.py
```
Messages.Welcome. → UserMessages.Welcome.
Messages.Errors. → CommonMessages.Errors.  # O según contexto
```

### 2. cancel_handler.py
```
Messages.Cancel.CANCEL_MESSAGE → CommonMessages.Confirmation.CANCELLED
Messages.Errors. → CommonMessages.Errors.
```

### 3. admin_task_handler.py
```
Messages.Admin. → AdminMessages.
Messages.Tasks. → TaskMessages.
```

### 4. support_handler.py
```
Messages.Support. → SupportMessages.
Messages.Errors. → CommonMessages.Errors.
```

### 5. task_handler.py
```
Messages.Tasks. → TaskMessages.
```

### 6. operations_handler.py
```
Messages.Operations. → OperationMessages.
Messages.Errors. → CommonMessages.Errors.
```

### 7. payment_handler.py
```
Messages.Operations. → OperationMessages.
Messages.Errors. → CommonMessages.Errors.
```

### 8. referral_handler.py
```
Messages.Operations. → OperationMessages.
Messages.Errors. → CommonMessages.Errors. O OperationMessages.Errors
```

### 9. inline_callbacks_handler.py
```
Messages.Errors. → CommonMessages.Errors.
Messages.Operations. → OperationMessages.
Messages.Help. → UserMessages.Help.
Messages.Support. → SupportMessages.
Messages.Cancel. → CommonMessages.Confirmation.CANCELLED
AdminMessages. (ya usa)
```

### 10. status_handler.py
```
Messages.Status. → UserMessages.Status.
Messages.Errors. → CommonMessages.Errors.
```

### 11. info_handler.py
```
Messages.Errors. → CommonMessages.Errors.
```

### 12. error_handler.py
```
Messages.Errors. → CommonMessages.Errors.
```

### 13. keys_manager_handler.py
```
Messages.Keys. → UserMessages.Keys.
Messages.Errors. → CommonMessages.Errors.
```

### 14. ayuda_handler.py
```
Messages.Welcome. → UserMessages.Welcome. (Para HELP)
Messages.Help. → UserMessages.Help.
```

### 15. crear_llave_handler.py
```
Messages.Keys. → UserMessages.Keys.
Messages.Errors. → CommonMessages.Errors.
```

### 16. user_task_manager_handler.py
```
Messages.Errors. → CommonMessages.Errors.
```

### 17. user_announcer_handler.py
```
Messages.Errors. → CommonMessages.Errors. (Estimado)
```

### 18. support_menu_handler.py
```
Messages.Support. → SupportMessages.
```

## Orden de Migración Recomendado

1. **Fase 1 - Críticos (3):** start_handler, cancel_handler, error_handler
2. **Fase 2 - Usuarios (5):** status_handler, keys_manager_handler, crear_llave_handler, info_handler, ayuda_handler
3. **Fase 3 - Admin/Tasks (3):** admin_handler, admin_task_handler, task_handler
4. **Fase 4 - Operaciones (4):** operations_handler, payment_handler, referral_handler, shop_handler
5. **Fase 5 - Soporte (2):** support_handler, support_menu_handler
6. **Fase 6 - Mixto (1):** inline_callbacks_handler

## Validación Post-Migración

- [ ] Sin imports de `Messages` legacy en handlers
- [ ] Todos los imports son de las nuevas clases
- [ ] No hay referencias rotas
- [ ] Formato de mensajes consistente
- [ ] Tests ejecutados
- [ ] Manual testing de flujos principales

---

**Fecha de creación:** 2026-01-07
**Estado:** En Progreso
**Próximo paso:** Iniciar Fase 1
