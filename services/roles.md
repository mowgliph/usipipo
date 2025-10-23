# Servicio de Roles (`services/roles.py`)

## Descripción del Propósito

Gestiona asignación y revocación de roles de usuario (normal, premium, vip) con expiración opcional. Asigna roles automáticamente según duración de compra y aplica bonuses por volumen.

## Funciones Principales

### `grant_role(session: AsyncSession, target_tg_id: str, role_name: str, days: Optional[int], granted_by: Optional[str]) -> Optional[models.UserRole]`
Asigna rol a usuario con validación y expiración opcional.
- **Parámetros**:
  - `target_tg_id`: Telegram ID del usuario objetivo
  - `role_name`: Nombre del rol ('normal', 'premium', 'vip')
  - `days`: Días de duración (opcional)
  - `granted_by`: UUID del administrador que otorga
- **Retorno**: UserRole creado o None si falla
- **Validaciones**: Rol permitido, usuario existe, no auto-asignación

### `revoke_role(session: AsyncSession, target_tg_id: str, role_name: str) -> bool`
Revoca rol activo de usuario.
- **Parámetros**: `target_tg_id`, `role_name`
- **Retorno**: True si revocado, False si no existía

### `get_user_roles(session: AsyncSession, user_id: str) -> List[Tuple[str, Optional[datetime]]]`
Obtiene roles activos (no expirados) del usuario.
- **Retorno**: Lista de tuplas (role_name, expires_at)

### `assign_role_on_purchase(session: AsyncSession, target_tg_id: str, duration_months: int, config_id: str, granted_by: Optional[str]) -> dict`
Asigna rol según duración de compra con bonuses.
- **Lógica de asignación**:
  - 24+ meses: VIP + 6 meses bonus
  - 12 meses: VIP + 2 meses bonus
  - 4-11 meses: Premium
  - 1-2 meses: Normal
- **Retorno**: Dict con rol, bonus y config_id

## Dependencias y Relaciones

- **Dependencias**:
  - `database.crud.roles`: Operaciones CRUD de roles
  - `database.crud.users`: Gestión de usuarios
  - `utils.helpers`: Notificaciones a admins
  - `datetime`: Manejo de expiraciones

- **Relaciones**:
  - Usado por `services.payments` al procesar compras
  - Integra con handlers administrativos para gestión manual
  - Registra errores críticos con notificaciones a admins

## Ejemplos de Uso

```python
# Asignar rol premium por 30 días
role = await grant_role(session, "123456789", "premium", days=30, granted_by="admin-123")

# Obtener roles activos de usuario
roles = await get_user_roles(session, "user-456")
# Retorna: [("premium", datetime(2025-11-22))]

# Asignar rol por compra de 6 meses
result = await assign_role_on_purchase(session, "123456789", 6, "config-789", "system")
# Retorna: {"role": "premium", "bonus_months": 0, "config_id": "config-789"}
```

## Consideraciones de Seguridad

- **Validación de roles**: Solo roles predefinidos permitidos
- **Prevención de abuso**: No auto-asignación de roles
- **Auditoría de errores**: Notificaciones a admins en fallos críticos
- **Control de expiración**: Roles temporales con fecha límite
- **Bonuses controlados**: Lógica clara de asignación por volumen