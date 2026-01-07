# 🚀 GUÍA DE INTEGRACIÓN RÁPIDA

## Paso 1: Actualizar handler_initializer.py

En el archivo `telegram_bot/handlers/handler_initializer.py`, agregar los siguientes imports al inicio:

```python
from telegram_bot.handlers.admin_users_callbacks import create_admin_users_callbacks
from telegram_bot.handlers.shop_handler import get_shop_handler
```

## Paso 2: Registrar los Handlers

En la función `initialize_handlers()`, agregar antes de `return handlers`:

```python
def initialize_handlers(vpn_service, support_service, referral_service, payment_service, achievement_service=None):
    # ... código existente ...
    
    # ============================================
    # NUEVOS HANDLERS AGREGADOS
    # ============================================
    
    # Handlers de gestión de usuarios (admin)
    admin_users_callbacks = create_admin_users_callbacks(admin_service)
    handlers.extend(admin_users_callbacks)
    
    # Handlers de Shop/Planes
    shop_callbacks = get_shop_handler(payment_service)
    handlers.extend(shop_callbacks)
    
    # ... resto del código ...
    
    return handlers
```

## Paso 3: Actualizar Callbacks Existentes en inline_callbacks_handler

En `telegram_bot/handlers/inline_callbacks_handler.py`, reemplazar el callback de "vip_plan":

```python
# ANTES:
handlers.append(CallbackQueryHandler(vip_plans_handler, pattern="^vip_plan$"))

# DESPUÉS (usar el nuevo shop):
handlers.append(CallbackQueryHandler(admin_handler_instance.shop_menu, pattern="^plan_vip$|^vip_plan$|^shop_menu$"))
```

## Paso 4: Verificar Métodos Auxiliares en PaymentService

El `ShopHandler` requiere estos métodos en `PaymentService`:

```python
# En application/services/payment_service.py, agregar:

async def get_user_balance(user_id: int) -> Dict:
    """Obtener balance de usuario"""
    pass

async def deduct_balance(user_id: int, amount: int) -> bool:
    """Descontar del balance"""
    pass

async def activate_vip(user_id: int, expires_at: datetime) -> bool:
    """Activar VIP"""
    pass

async def add_storage(user_id: int, gb: int) -> bool:
    """Agregar almacenamiento"""
    pass
```

## Paso 5: Actualizar Base de Datos (Migraciones)

Crear una nueva migración con `alembic`:

```bash
alembic revision --autogenerate -m "add_user_roles_and_premium_features"
```

Luego ejecutar:

```bash
alembic upgrade head
```

### Campos a Agregar/Actualizar:

**Tabla: users**
```sql
ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user';
ALTER TABLE users ADD COLUMN task_manager_expires_at TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN announcer_expires_at TIMESTAMP NULL;
ALTER TABLE users MODIFY COLUMN status ENUM('active', 'suspended', 'blocked', 'free_trial') DEFAULT 'active';
```

## ✅ Verificación Post-Integración

1. **Acceder al Admin Panel**
   ```
   /admin comando en el bot
   ```

2. **Verificar nuevo submenu**
   ```
   Admin Panel → 👥 Usuarios (nuevo botón)
   ```

3. **Acceder a Shop**
   ```
   Operaciones → 🛒 Shop (antes era 👑 Plan VIP)
   ```

4. **Probar funcionalidades básicas**
   - Ver lista de usuarios
   - Asignar roles
   - Cambiar estado
   - Bloquear/Desbloquear usuario
   - Hacer compra en Shop (requiere balance de estrellas)

---

## 🔧 Configuración Personalizada

### En config.py, puedes personalizar precios:

```python
# SISTEMA DE TIENDA
SHOP_VIP_PRICES = {
    '1_month': 10,
    '3_months': 27,
    '6_months': 50,
    '12_months': 90
}

SHOP_ROLES_PRICES = {
    'task_manager': 50,      # por mes
    'announcer': 80,         # por mes
    'both': 120              # por mes
}

SHOP_STORAGE_PRICES = {
    '10gb': 5,
    '25gb': 12,
    '50gb': 25,
    '200gb': 100
}
```

---

## 📝 Notas Importantes

1. **Seguridad**: Solo accesible desde ADMIN_ID en settings
2. **Transacciones**: Las compras son definitivas una vez procesadas
3. **Roles Premium**: Se asignan con fecha de expiración automática
4. **Estados de Usuario**: El estado BLOCKED deshabilita acceso completo
5. **Paginación**: Configurable en `get_users_paginated(per_page=10)`

---

## 🐛 Troubleshooting

**Error: "admin_users_submenu callback not found"**
→ Verificar que los imports de `admin_users_callbacks.py` estén correctos

**Error: "PaymentService method not found"**
→ Implementar los métodos auxiliares en PaymentService

**Error: "UserRole not found"**
→ Asegurarse que `domain/entities/user.py` fue actualizado correctamente

**No aparece el botón de Shop**
→ Verificar que `operations_menu()` fue actualizado en inline_keyboards.py

---

## 📞 Support

Para más información, ver:
- `docs/ADMIN_USERS_SHOP_GUIDE.md` - Guía completa de funcionalidades
- `telegram_bot/messages/admin_messages.py` - Mensajes personalizables
- `application/services/admin_service.py` - Métodos disponibles

