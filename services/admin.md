# Servicio de Administración (`services/admin.py`)

## Descripción del Propósito

Proporciona funcionalidades administrativas para gestión de usuarios, roles y permisos. Permite promover/demover administradores, asignar/revocar roles, y gestionar usuarios del sistema con auditoría completa.

## Funciones Principales

### `list_users_paginated(session: AsyncSession, limit: int = 50, offset: int = 0) -> List[models.User]`
Lista usuarios con paginación.
- **Parámetros**: `session`, `limit`, `offset`
- **Retorno**: Lista de usuarios

### `get_user_details(session: AsyncSession, user_id: str) -> Dict[str, Any]`
Obtiene información completa de usuario incluyendo VPNs, pagos, roles y logs.
- **Retorno**: Dict con user, vpnconfigs, payments, roles, recent_logs

### `promote_to_admin(session: AsyncSession, target_user_id: str, acting_user_id: Optional[str], commit: bool = True) -> models.User`
Promueve usuario a administrador con auditoría.
- **Parámetros**: `session`, `target_user_id`, `acting_user_id`, `commit`
- **Retorno**: Usuario promovido

### `demote_from_admin(session: AsyncSession, target_user_id: str, acting_user_id: Optional[str], commit: bool = True) -> models.User`
Remueve permisos de administrador.

### `set_superadmin(session: AsyncSession, target_user_id: str, acting_user_id: Optional[str], commit: bool = True) -> models.User`
Asigna permisos de superadministrador.

### `assign_role_to_user(session: AsyncSession, target_user_id: str, role_name: str, acting_user_id: Optional[str], expires_at: Optional[datetime], commit: bool = True) -> models.UserRole`
Asigna rol a usuario con expiración opcional.

### `revoke_role_from_user(session: AsyncSession, target_user_id: str, role_name: str, acting_user_id: Optional[str], commit: bool = True) -> bool`
Revoca rol de usuario.

### `list_admins(session: AsyncSession) -> List[models.User]`
Lista todos los administradores y superadministradores.

## Dependencias y Relaciones

- **Dependencias**:
  - `database.crud.users`: Operaciones CRUD de usuarios
  - `database.crud.roles`: Gestión de roles
  - `database.crud.logs`: Auditoría
  - `database.crud.vpn`: Consultas de VPN
  - `datetime`: Manejo de fechas

- **Relaciones**:
  - Usado por handlers administrativos del bot
  - Integra con `services.user` para operaciones básicas
  - Registra todas las acciones en audit logs

## Ejemplos de Uso

```python
# Obtener detalles completos de usuario
details = await get_user_details(session, "user-123")
# Retorna: {"user": User, "vpnconfigs": [...], "payments": [...], ...}

# Promover a admin
await promote_to_admin(session, "user-456", "admin-789")

# Asignar rol con expiración
from datetime import timedelta
expires = datetime.utcnow() + timedelta(days=30)
await assign_role_to_user(session, "user-123", "premium", "admin-789", expires)
```

## Consideraciones de Seguridad

- **Validación de permisos**: Verifica existencia de usuarios objetivo
- **Auditoría completa**: Registra todas las operaciones administrativas
- **Prevención de errores**: Manejo de transacciones con rollback
- **Control de acceso**: Solo administradores pueden usar estas funciones
- **Validación de roles**: Verifica roles permitidos antes de asignar
- **Integrity constraints**: Maneja errores de integridad de BD