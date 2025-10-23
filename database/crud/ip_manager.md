# CRUD IP Manager (`database/crud/ip_manager.py`)

## Descripción del Propósito

Gestión de direcciones IP para asignación a usuarios. Maneja pool de IPs disponibles, asignación automática, revocación y reutilización de direcciones IP.

## Funciones Principales

### `get_available_ips_for_type(session: AsyncSession, ip_type: str) -> List[models.IPManager]`
Obtiene IPs disponibles de un tipo específico.

### `assign_ip_to_user(session: AsyncSession, ip_type: str, user_id: str, commit: bool = False) -> Optional[models.IPManager]`
Asigna IP disponible al usuario (con bloqueo para evitar race conditions).

### `revoke_ip(session: AsyncSession, ip_id: str, reason: str = "manual_revocation", commit: bool = False) -> bool`
Revoca IP asignada marcándola como no disponible.

### `release_ip(session: AsyncSession, ip_id: str, commit: bool = False) -> bool`
Libera IP revocada para reutilización.

### `get_assigned_ips_for_user(session: AsyncSession, user_id: str) -> List[models.IPManager]`
Lista IPs asignadas a usuario (no revocadas).

### `cleanup_revoked_ips(session: AsyncSession, commit: bool = False) -> int`
Limpia IPs revocadas sin usuario asignado, marcándolas disponibles.

### `create_ip_entry(session: AsyncSession, ip_address: str, ip_type: str, extra_data: Optional[Dict] = None, commit: bool = False) -> models.IPManager`
Crea nueva entrada de IP en el pool.

### `revoke_ips_by_user_and_type(session: AsyncSession, user_id: str, ip_type: str, reason: str = "vpn_revoked", commit: bool = False) -> int`
Revoca todas las IPs de un usuario de un tipo específico.

## Dependencias y Relaciones

- **Dependencias**:
  - `database.models`: Modelo IPManager
  - `sqlalchemy`: with_for_update para bloqueos

- **Relaciones**:
  - Usado por servicios VPN para asignación de IPs dedicadas
  - Integrado con revocación automática de VPNs
  - Base para gestión de recursos IP del sistema

## Ejemplos de Uso

```python
# Asignar IP WireGuard al usuario
ip = await assign_ip_to_user(session, "wireguard_paid", "user-123")

# Obtener IPs asignadas
ips = await get_assigned_ips_for_user(session, "user-123")

# Revocar IP
await revoke_ip(session, "ip-id-456", "vpn_expired")

# Limpiar IPs revocadas
cleaned = await cleanup_revoked_ips(session)
```

## Consideraciones de Seguridad

- **Prevención de race conditions**: with_for_update en asignaciones
- **Control de acceso**: Solo admins pueden gestionar IPs
- **Auditoría completa**: Registra asignaciones y revocaciones
- **Reutilización segura**: Limpieza automática de IPs revocadas
- **Validación de estado**: Verifica disponibilidad antes de asignar