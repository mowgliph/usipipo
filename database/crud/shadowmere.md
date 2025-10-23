# CRUD Shadowmere (`database/crud/shadowmere.py`)

## Descripción del Propósito

Gestión de base de datos para el sistema Shadowmere de proxies. Maneja almacenamiento, consulta y mantenimiento de proxies SOCKS5/SOCKS4/HTTP detectados automáticamente.

## Funciones Principales

### `create_proxy(session: AsyncSession, proxy_address: str, proxy_type: str, country: Optional[str] = None, response_time: Optional[float] = None, commit: bool = False) -> models.ShadowmereProxy`
Crea nuevo registro de proxy Shadowmere.

### `get_proxy_by_address(session: AsyncSession, proxy_address: str) -> Optional[models.ShadowmereProxy]`
Obtiene proxy por dirección IP:puerto.

### `get_all_working_proxies(session: AsyncSession, limit: int = 10) -> List[models.ShadowmereProxy]`
Lista proxies funcionando ordenados por última verificación.

### `get_proxies_by_type(session: AsyncSession, proxy_type: str, limit: int = 10) -> List[models.ShadowmereProxy]`
Lista proxies filtrados por tipo (SOCKS5, HTTP, etc.).

### `update_proxy_status(session: AsyncSession, proxy_address: str, is_working: bool, response_time: Optional[float] = None, commit: bool = False) -> Optional[models.ShadowmereProxy]`
Actualiza estado de funcionamiento de proxy.

### `delete_proxy(session: AsyncSession, proxy_address: str, commit: bool = False) -> bool`
Elimina proxy de la base de datos.

### `delete_old_proxies(session: AsyncSession, days: int = 30, commit: bool = False) -> int`
Elimina proxies más antiguos que X días.

### `get_proxy_stats(session: AsyncSession) -> Dict[str, Any]`
Obtiene estadísticas completas: total, funcionando, por tipo, por país.

### `mark_all_as_not_working(session: AsyncSession, commit: bool = False) -> int`
Marca todos los proxies como no funcionando (reset masivo).

## Dependencias y Relaciones

- **Dependencias**:
  - `database.models`: Modelo ShadowmereProxy
  - `sqlalchemy`: Operaciones de BD con agregaciones

- **Relaciones**:
  - Usado por sistema Shadowmere de detección automática
  - Base de datos para proxies públicos encontrados
  - Estadísticas para monitoreo del sistema de proxies

## Ejemplos de Uso

```python
# Crear proxy detectado
proxy = await create_proxy(session, "192.168.1.1:8080", "SOCKS5", "US", 150.5)

# Obtener proxies funcionando
working = await get_all_working_proxies(session, limit=20)

# Actualizar estado
await update_proxy_status(session, "192.168.1.1:8080", False)

# Estadísticas
stats = await get_proxy_stats(session)
# Retorna: {"total": 1000, "working": 800, "by_type": {"SOCKS5": 500, ...}}
```

## Consideraciones de Seguridad

- **Validación de entrada**: Direcciones IP:puerto válidas
- **Prevención de duplicados**: Verificación antes de crear
- **Limpieza automática**: Eliminación de proxies antiguos
- **Auditoría de cambios**: Timestamps en actualizaciones
- **Control de acceso**: Funciones para mantenimiento del sistema