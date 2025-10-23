# CRUD Usuarios (`database/crud/users.py`)

## Descripción del Propósito

Operaciones CRUD básicas para gestión de usuarios del sistema uSipipo. Maneja creación, consulta y actualización de usuarios desde Telegram, incluyendo permisos administrativos.

## Funciones Principales

### `get_user_by_pk(session: AsyncSession, user_id: str) -> Optional[models.User]`
Obtiene usuario por UUID.
- **Parámetros**: `session`, `user_id` (UUID string)
- **Retorno**: User o None

### `get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[models.User]`
Obtiene usuario por Telegram ID.
- **Parámetros**: `session`, `telegram_id`
- **Retorno**: User o None

### `ensure_user(session: AsyncSession, tg_payload: Dict[str, Any], commit: bool = False) -> models.User`
Asegura existencia de usuario, crea si no existe, actualiza datos si cambiaron.
- **Parámetros**: `session`, `tg_payload`, `commit`
- **Retorno**: User existente o creado

### `create_user_from_telegram(session: AsyncSession, tg_payload: Dict[str, Any], commit: bool = False) -> models.User`
Crea nuevo usuario desde payload de Telegram.
- **Parámetros**: `session`, `tg_payload`, `commit`
- **Retorno**: User creado

### `set_user_admin(session: AsyncSession, user_id: str, is_admin: bool, commit: bool = True) -> Optional[models.User]`
Asigna/revoca permisos de administrador.
- **Parámetros**: `session`, `user_id`, `is_admin`, `commit`
- **Retorno**: User actualizado o None

### `set_user_superadmin(session: AsyncSession, user_id: str, is_superadmin: bool, commit: bool = True) -> Optional[models.User]`
Asigna/revoca permisos de superadministrador.

### `is_user_admin(session: AsyncSession, user_id: str) -> bool`
Verifica si usuario es administrador.

### `is_user_superadmin(session: AsyncSession, user_id: str) -> bool`
Verifica si usuario es superadministrador.

### `get_admins(session: AsyncSession) -> List[models.User]`
Lista todos los administradores y superadministradores.

### `list_users(session: AsyncSession, limit: int = 50) -> List[models.User]`
Lista usuarios con paginación.

### `get_active_users(session: AsyncSession, batch_size: int = 100, offset: int = 0) -> AsyncGenerator[models.User, None]`
Generador asíncrono de usuarios activos para envíos masivos.

## Dependencias y Relaciones

- **Dependencias**:
  - `database.models`: Modelo User
  - `sqlalchemy`: Operaciones de BD

- **Relaciones**:
  - Usado por `services.user` para operaciones de negocio
  - Base para gestión administrativa en `services.admin`

## Ejemplos de Uso

```python
# Obtener usuario por Telegram ID
user = await get_user_by_telegram_id(session, 123456789)

# Asegurar usuario existe
user = await ensure_user(session, telegram_payload)

# Promover a admin
await set_user_admin(session, "user-123", True)
```

## Consideraciones de Seguridad

- **Validación de entrada**: Verifica telegram_id válido
- **Prevención de duplicados**: ensure_user evita usuarios duplicados
- **Control de permisos**: Funciones separadas para admin/superadmin
- **Transacciones**: Commit controlado por caller