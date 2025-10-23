# Servicio de Auditoría (`services/audit.py`)

## Descripción del Propósito

Sistema centralizado de auditoría para uSipipo. Registra todas las operaciones del sistema con metadatos detallados, permite consultas históricas y limpieza automática de logs antiguos.

## Funciones Principales

### `create_audit_log(session: AsyncSession, user_id: Optional[str], action: str, payload: Optional[Dict[str, Any]] = None, commit: bool = True) -> models.AuditLog`
Crea entrada de auditoría usando CRUD.
- **Parámetros**: `session`, `user_id`, `action`, `payload`, `commit`
- **Retorno**: AuditLog creado

### `get_audit_logs(session: AsyncSession, limit: int = 20, offset: int = 0, user_id: Optional[str] = None, action: Optional[str] = None) -> List[models.AuditLog]`
Consulta logs con filtros y paginación.

### `count_audit_logs(session: AsyncSession, user_id: Optional[str] = None, action: Optional[str] = None) -> int`
Cuenta logs con filtros.

### `delete_old_logs(session: AsyncSession, cutoff: datetime, user_id: Optional[str] = None, commit: bool = True) -> int`
Elimina logs anteriores a fecha límite.
- **Retorno**: Número de logs eliminados

### `delete_logs_older_than(session: AsyncSession, days_old: int = 30, commit: bool = True) -> int`
Elimina logs más antiguos que X días.

### `format_logs(logs_list: List[models.AuditLog]) -> str`
Formatea lista de logs para presentación en mensajes.

### `log_action_auto_session()` / `audit_service`
Funciones de conveniencia con manejo automático de sesiones.

## Dependencias y Relaciones

- **Dependencias**:
  - `database.crud.logs`: Operaciones CRUD de auditoría
  - `database.db`: Sesiones de BD
  - `datetime`: Manejo de fechas y expiración

- **Relaciones**:
  - Usado por todos los servicios para registrar operaciones
  - Integrado con sistema de logs del bot
  - Consultas por handlers administrativos

## Ejemplos de Uso

```python
# Crear log de auditoría
log = await create_audit_log(session, "user-123", "vpn_created", {"vpn_type": "wireguard"})

# Consultar logs recientes
logs = await get_audit_logs(session, limit=10, user_id="user-123")

# Formatear para mensaje
formatted = format_logs(logs)
# Retorna: "🕒 2025-10-23 10:30:15 | @username | vpn_created | ..."

# Limpiar logs antiguos
deleted = await delete_logs_older_than(session, days_old=90)
```

## Consideraciones de Seguridad

- **Auditoría completa**: Registra todas las operaciones críticas
- **Filtros de consulta**: Control de acceso por user_id
- **Limpieza automática**: Evita crecimiento ilimitado de logs
- **Manejo de transacciones**: Commit controlado por caller
- **Validación de entrada**: user_id opcional (SYSTEM para operaciones automáticas)