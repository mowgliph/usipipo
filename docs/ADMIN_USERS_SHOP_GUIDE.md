# 📋 Guía de Implementación: Sistema de Gestión de Usuarios y Shop

## 🎯 Resumen de Cambios

Se ha implementado un sistema completo de gestión de usuarios en el panel de administración, junto con un shop integrado con planes especiales.

---

## 📊 CAMBIOS REALIZADOS

### 1. **Actualización de Entidades de Dominio**

#### Archivo: `domain/entities/user.py`

**Nuevos Enumeradores:**
- `UserStatus` - Ahora incluye: ACTIVE, SUSPENDED, BLOCKED, FREE_TRIAL
- `UserRole` - Nuevos roles: USER, ADMIN, TASK_MANAGER, ANNOUNCER

**Nuevos Atributos en la clase `User`:**
- `role: UserRole` - Rol actual del usuario
- `task_manager_expires_at: Optional[datetime]` - Expiración del rol Gestor de Tareas
- `announcer_expires_at: Optional[datetime]` - Expiración del rol Anunciante

**Nuevos Métodos:**
- `is_blocked` - Verifica si el usuario está bloqueado
- `is_task_manager_active()` - Verifica si el usuario tiene el rol de Gestor de Tareas activo
- `is_announcer_active()` - Verifica si el usuario tiene el rol de Anunciante activo

---

### 2. **Extensión del Servicio de Administración**

#### Archivo: `application/services/admin_service.py`

**Nuevos Métodos Implementados:**

```python
# Obtener información de usuario
async def get_user_by_id(user_id: int) -> Optional[Dict]

# Gestión de estado
async def update_user_status(user_id: int, status: str) -> AdminOperationResult
async def block_user(user_id: int) -> AdminOperationResult
async def unblock_user(user_id: int) -> AdminOperationResult

# Gestión de roles
async def assign_role_to_user(user_id: int, role: str, duration_days: Optional[int]) -> AdminOperationResult

# Eliminación
async def delete_user(user_id: int) -> AdminOperationResult

# Paginación
async def get_users_paginated(page: int = 1, per_page: int = 10) -> Dict
```

---

### 3. **Nuevo Handler de Gestión de Usuarios**

#### Archivo: `telegram_bot/handlers/admin_users_handler.py`

**Funcionalidades:**
- Ver lista paginada de usuarios
- Ver detalle completo de cada usuario
- Asignar roles (Usuario, Admin, Gestor de Tareas, Anunciante)
- Cambiar estado (Activo, Suspendido, Bloqueado, Prueba Gratis)
- Bloquear/Desbloquear usuarios
- Eliminar usuarios (con confirmación)
- Ver claves de cada usuario

---

### 4. **Integración de Callbacks para Usuarios**

#### Archivo: `telegram_bot/handlers/admin_users_callbacks.py`

Gestiona todos los callbacks relacionados con:
- Submenu de usuarios
- Listado y paginación
- Detalle de usuario
- Asignación de roles
- Cambios de estado
- Operaciones de bloqueo/desbloqueo

---

### 5. **Nuevo Handler de Shop (Tienda)**

#### Archivo: `telegram_bot/handlers/shop_handler.py`

**Categorías Implementadas:**

**1. Planes VIP**
- 1 Mes - 10⭐
- 3 Meses - 27⭐ (Ahorra 3⭐)
- 6 Meses - 50⭐ (Ahorra 10⭐)
- 12 Meses - 90⭐ (Ahorra 30⭐)

Beneficios:
- 10 claves VPN simultáneas
- 50 GB de datos por clave
- Soporte prioritario
- Sin anuncios

**2. Roles Premium**

**Gestor de Tareas:**
- 50⭐/mes
- Crear y gestionar tareas
- Ver participación de usuarios
- Estadísticas detalladas

**Anunciante:**
- 80⭐/mes
- Crear campañas de anuncios
- Targeting por región/usuario
- Hasta 100 anuncios/mes

**Ambos Roles:**
- 120⭐/mes
- Acceso a todas las funciones

Cada rol tiene planes: 1 mes, 3 meses, 6 meses, 1 año

**3. Paquetes de Almacenamiento**
- +10 GB - 5⭐
- +25 GB - 12⭐ (Ahorra 3⭐)
- +50 GB - 25⭐ (Ahorra 5⭐)
- +200 GB - 100⭐ (Mejor ahorro)

---

### 6. **Actualización de Teclados**

#### Archivo: `telegram_bot/keyboard/inline_keyboards.py`

**Nuevos Métodos en `InlineAdminKeyboards`:**
- `users_submenu()` - Submenu principal de usuarios
- `users_list_pagination()` - Paginación de lista
- `user_detail_actions()` - Acciones sobre usuario
- `role_selection()` - Selección de roles
- `status_selection()` - Selección de estados
- `premium_role_duration()` - Selección de duración para roles premium

**Actualización:**
- Botón "👑 Plan VIP" → "🛒 Shop" en el menú de operaciones

---

### 7. **Nuevos Mensajes de Administración**

#### Archivo: `telegram_bot/messages/admin_messages.py`

Se agregaron mensajes para:
- Submenu de usuarios
- Lista de usuarios con detalles
- Información detallada de usuario
- Confirmación de bloqueo/desbloqueo
- Confirmación de eliminación
- Cambio de estado
- Asignación de roles

---

## 🔌 INTEGRACIÓN CON EL SISTEMA

### Para Integrar en `handler_initializer.py`:

```python
from telegram_bot.handlers.admin_users_callbacks import create_admin_users_callbacks
from telegram_bot.handlers.shop_handler import get_shop_handler

def initialize_handlers(...):
    # ... código existente ...
    
    # Agregar handlers de usuarios
    admin_users_callbacks = create_admin_users_callbacks(admin_service)
    application.add_handlers(admin_users_callbacks)
    
    # Agregar handlers de shop
    shop_callbacks = get_shop_handler(payment_service)
    application.add_handlers(shop_callbacks)
```

---

## 💾 ESTRUCTURA DE FLUJOS

### Flujo de Gestión de Usuarios:

```
Admin Panel
    ↓
👥 Submenu de Usuarios
    ↓
Opciones:
├─ 📋 Ver Usuarios (Paginado)
│  ├─ Seleccionar Usuario
│  └─ Acciones del Usuario
├─ 🎖️ Asignar Roles
│  ├─ Seleccionar Rol
│  └─ Confirmar (Premium: seleccionar duración)
├─ 📌 Cambiar Estado
│  ├─ Activo
│  ├─ Suspendido
│  ├─ Bloqueado
│  └─ Prueba Gratis
├─ 🔴 Bloquear Usuario
├─ 🟢 Desbloquear Usuario
└─ 🗑️ Eliminar Usuario (Confirmación)
```

### Flujo de Shop:

```
Operaciones
    ↓
🛒 SHOP uSipipo
    ↓
Categorías:
├─ 👑 Planes VIP
│  ├─ 1 Mes - 10⭐
│  ├─ 3 Meses - 27⭐
│  ├─ 6 Meses - 50⭐
│  └─ 12 Meses - 90⭐
├─ 📋 Roles Premium
│  ├─ Gestor de Tareas
│  ├─ Anunciante
│  └─ Ambos Roles
└─ 💾 Almacenamiento
   ├─ +10 GB - 5⭐
   ├─ +25 GB - 12⭐
   ├─ +50 GB - 25⭐
   └─ +200 GB - 100⭐
```

---

## 🔐 Permisos y Validaciones

- Solo el admin (ID en settings.ADMIN_ID) puede acceder al panel
- Los roles premium solo se pueden asignar a usuarios existentes
- Las compras se validan contra el balance de estrellas
- Los roles premium tienen fecha de expiración automática
- Los usuarios bloqueados no pueden acceder al sistema

---

## 📝 Próximos Pasos Recomendados

1. **Integración en handler_initializer.py**
   - Agregar imports de los nuevos handlers
   - Registrar los CallbackQueryHandlers

2. **Actualizar migraciones de BD**
   - Agregar campos de role, task_manager_expires_at, announcer_expires_at
   - Actualizar el campo status para incluir BLOCKED

3. **Implementar métodos faltantes en PaymentService**
   - `activate_vip(user_id, expires_at)`
   - `add_storage(user_id, gb)`
   - `deduct_balance(user_id, amount)`

4. **Crear interface de administración web** (Opcional)
   - Panel complementario en web
   - Reportes de compras
   - Estadísticas de usuarios

5. **Configurar límites en config.py**
   - Precios de roles premium
   - Límites de almacenamiento
   - Duración predeterminada de roles

---

## 📞 Soporte y Documentación

Para más información sobre:
- **Roles Premium**: Ver `AdminMessages.ROLE_DESCRIPTIONS`
- **Productos Shop**: Ver `ShopHandler._get_product_info()`
- **Estados de Usuario**: Ver `UserStatus` enum
- **Operaciones Admin**: Ver `AdminService` métodos CRUD

---

**Versión**: 1.0.0
**Último actualizado**: Enero 2026
