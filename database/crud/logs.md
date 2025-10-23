# CRUD Logs (`database/crud/logs.py`)

## Descripción del Propósito

Sistema de auditoría centralizado para uSipipo. Maneja creación, consulta y limpieza de registros de auditoría con soporte para metadatos JSON.

## Funciones Principales

### `create_audit_log(session: AsyncSession, user_id: Optional[str], action: str, payload: Optional[Dict[str, Any]] = None, commit: bool = False) -> models.AuditLog`
Crea nuevo registro de auditoría.
- **Parámetros**: `session`, `user_id`, `action`, `payload`, `commit`
- **Retorno**: AuditLog creado

### `get_audit_logs(session: AsyncSession, user_id: Optional[str] = None, action: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[models.AuditLog]`
Consulta logs con filtros y paginación.
- **Parámetros**: `session`, `user_id`, `action`, `limit`, `offset`
- **Retorno**: Lista de AuditLog con relación User cargada

### `count_audit_logs(session: AsyncSession, user_id: Optional[str] = None, action: Optional[str] = None) -> int`
Cuenta logs con filtros.

### `delete_old_logs(session: AsyncSession, cutoff: datetime, user_id: Optional[str] = None, commit: bool = False) -> int`
Elimina logs anteriores a fecha límite.
- **Parámetros**: `session`, `cutoff`, `user_id`, `commit`
- **Retorno**: Número de logs eliminados

## Dependencias y Relaciones

- **Dependencias**:
  - `database.models`: Modelo AuditLog
  - `sqlalchemy`: Operaciones de BD con selectinload

- **Relaciones**:
  - Usado por `services.audit` para operaciones de negocio
  - Base para todo el sistema de auditoría de uSipipo

## Ejemplos de Uso

```python
# Crear log de auditoría
log = await create_audit_log(session, "user-123", "vpn_created", {"vpn_type": "wireguard"})

# Consultar logs recientes
logs = await get_audit_logs(session, limit=10, user_id="user-123")

# Limpiar logs antiguos
deleted = await delete_old_logs(session, cutoff_date, user_id="user-123")
```

## Consideraciones de Seguridad

- **Filtrado por usuario**: Control de acceso a logs
- **Paginación**: Manejo eficiente de grandes volúmenes
- **Limpieza automática**: Prevención de crecimiento ilimitado
- **Metadatos JSON**: Almacenamiento flexible de información
- **Timestamps UTC**: Consistencia temporal