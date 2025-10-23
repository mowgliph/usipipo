# CRUD Roles (`database/crud/roles.py`)

## Descripción del Propósito

Gestión de roles y permisos de usuario. Maneja creación de roles, asignación/revocación a usuarios con soporte para expiración temporal.

## Funciones Principales

### `get_role_by_name(session: AsyncSession, role_name: str) -> Optional[models.Role]`
Obtiene rol por nombre.

### `create_role(session: AsyncSession, name: str, description: Optional[str] = None, commit: bool = False) -> models.Role`
Crea nuevo rol si no existe.

### `grant_role(session: AsyncSession, user_id: str, role_name: str, expires_at: Optional[datetime] = None, granted_by: Optional[str] = None, commit: bool = False) -> models.UserRole`
Asigna rol a usuario con expiración opcional.
- **Crea rol automáticamente** si no existe

### `revoke_role(session: AsyncSession, user_id: str, role_name: str, commit: bool = False) -> bool`
Revoca rol de usuario.

### `get_user_roles(session: AsyncSession, user_id: str) -> List[models.UserRole]`
Obtiene todos los roles de usuario (incluyendo expirados).

### `get_active_roles(session: AsyncSession, user_id: str) -> List[Tuple[str, Optional[datetime]]]`
Obtiene roles activos (no expirados) como tuplas (name, expires_at).

### `get_users_with_role(session: AsyncSession, role_name: str) -> List[models.User]`
Lista usuarios con rol activo específico.

### `delete_expired_user_roles(session: AsyncSession, commit: bool = False) -> int`
Elimina roles expirados (hard delete).

## Dependencias y Relaciones

- **Dependencias**:
  - `database.models`: Modelos Role y UserRole
  - `sqlalchemy`: Joins y operaciones complejas

- **Relaciones**:
  - Usado por `services.roles` para lógica de negocio
  - Base para sistema de permisos de uSipipo

## Ejemplos de Uso

```python
# Asignar rol con expiración
user_role = await grant_role(session, "user-123", "premium", expires_at, "admin-456")

# Obtener roles activos
active_roles = await get_active_roles(session, "user-123")
# Retorna: [("premium", datetime), ("vip", None)]

# Revocar rol
await revoke_role(session, "user-123", "premium")
```

## Consideraciones de Seguridad

- **Expiración automática**: Roles temporales con fecha límite
- **Auditoría**: Registra granted_by para trazabilidad
- **Validación**: Verifica existencia de roles antes de operaciones
- **Hard delete**: Limpieza de roles expirados
- **Joins eficientes**: Consultas optimizadas con índices