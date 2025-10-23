# CRUD Proxy (`database/crud/proxy.py`)

## Descripción del Propósito

Operaciones CRUD para proxies MTProto. Gestiona creación, consulta y revocación de proxies gratuitos con expiración automática.

## Funciones Principales

### `get_proxy_by_id(session: AsyncSession, proxy_id: str) -> Optional[models.MTProtoProxy]`
Obtiene proxy por ID.

### `get_proxies_for_user(session: AsyncSession, user_id: str) -> List[models.MTProtoProxy]`
Lista todos los proxies de un usuario.

### `get_active_proxy_for_user(session: AsyncSession, user_id: str) -> Optional[models.MTProtoProxy]`
Obtiene proxy activo de usuario (no expirado).

### `create_proxy(session: AsyncSession, user_id: str, host: str, port: int, secret: str, tag: Optional[str], expires_at: Optional[datetime], extra_data: Optional[Dict], commit: bool = False) -> models.MTProtoProxy`
Crea nuevo proxy MTProto.

### `create_free_proxy(session: AsyncSession, user_id: str, host: str, port: int, secret: str, tag: Optional[str], duration_days: int = 30, extra_data: Optional[Dict], commit: bool = False) -> models.MTProtoProxy`
Crea proxy gratuito con duración específica.

### `update_proxy_status(session: AsyncSession, proxy_id: str, status: str, commit: bool = False) -> Optional[models.MTProtoProxy]`
Actualiza estado del proxy.

### `revoke_proxy(session: AsyncSession, proxy_id: str, reason: str, commit: bool = False) -> Optional[models.MTProtoProxy]`
Revoca proxy y registra razón.

### `get_expired_proxies(session: AsyncSession) -> List[models.MTProtoProxy]`
Lista proxies expirados para limpieza.

### Métricas:
- `count_proxies_by_status()`: Conteo por estado
- `count_proxies_for_user()`: Conteo por usuario
- `last_proxy_for_user()`: Último proxy creado

## Dependencias y Relaciones

- **Dependencias**:
  - `database.models`: Modelo MTProtoProxy
  - `sqlalchemy`: Operaciones de BD

- **Relaciones**:
  - Usado por `services.proxy` para lógica de negocio
  - Integrado con sistema de expiración automática
  - Similar a VPN CRUD pero para proxies MTProto

## Ejemplos de Uso

```python
# Crear proxy gratuito
proxy = await create_free_proxy(session, "user-123", "host.com", 443, "secret123")

# Obtener proxy activo
active = await get_active_proxy_for_user(session, "user-123")

# Revocar proxy
await revoke_proxy(session, "proxy-id-456", "user_request")
```

## Consideraciones de Seguridad

- **Un proxy activo por usuario**: Previene duplicados
- **Expiración automática**: Proxies temporales
- **Auditoría de revocación**: Registra razones
- **Transacciones**: Commit controlado por caller
- **Validación de unicidad**: Un solo proxy activo por usuario