# Servicio de Proxy (`services/proxy.py`)

## Descripción del Propósito

Gestiona proxies MTProto gratuitos para usuarios. Crea configuraciones desde variables de entorno, genera cadenas de conexión y maneja ciclo de vida de proxies con expiración automática.

## Funciones Principales

### `create_free_proxy_for_user(session: AsyncSession, user_id: str, commit: bool = False) -> Optional[models.MTProtoProxy]`
Crea proxy MTProto gratuito para usuario (30 días).
- **Parámetros**: `session`, `user_id`, `commit`
- **Validaciones**: Usuario no tiene proxy activo
- **Retorno**: MTProtoProxy creado o None si falla

### `_generate_mtproto_config() -> Optional[Dict[str, Any]]`
Obtiene configuración MTProto desde variables de entorno.
- **Variables requeridas**: MTPROXY_HOST, MTPROXY_PORT, MTPROXY_SECRET
- **Retorno**: Dict con host, port, secret, tag

### `list_user_proxies(session: AsyncSession, user_id: str) -> list[models.MTProtoProxy]`
Lista todos los proxies MTProto del usuario.

### `revoke_proxy(session: AsyncSession, proxy_id: str, reason: str = "user_request") -> Optional[models.MTProtoProxy]`
Revoca proxy MTProto existente.
- **Parámetros**: `session`, `proxy_id`, `reason`
- **Retorno**: Proxy actualizado o None si no existe

### `get_proxy_connection_string(proxy: models.MTProtoProxy) -> str`
Genera cadena de conexión tg:// para Telegram.
- **Formato**: `tg://proxy?server={host}&port={port}&secret={secret}`

### `get_proxy_info(proxy: models.MTProtoProxy) -> Dict[str, Any]`
Retorna información completa del proxy para usuario.

## Dependencias y Relaciones

- **Dependencias**:
  - `database.crud.proxy`: Operaciones CRUD de proxies
  - `database.crud.logs`: Auditoría
  - `utils.helpers`: Utilidades de logging
  - `config`: Variables de entorno MTProto

- **Relaciones**:
  - Usado por handlers de bot para comandos de proxy
  - Comparte lógica de auditoría con otros servicios VPN
  - Integrado con sistema de expiración automática

## Ejemplos de Uso

```python
# Crear proxy gratuito
proxy = await create_free_proxy_for_user(session, "user-123")

# Generar cadena de conexión
if proxy:
    connection_string = await get_proxy_connection_string(proxy)
    # Retorna: "tg://proxy?server=example.com&port=443&secret=..."

# Listar proxies del usuario
proxies = await list_user_proxies(session, "user-123")
```

## Consideraciones de Seguridad

- **Validación de configuración**: Verifica variables de entorno críticas
- **Prevención de duplicados**: Un proxy activo por usuario
- **Auditoría completa**: Registra creación y revocación
- **Configuración compartida**: Misma config para todos los usuarios (gratuito)
- **Expiración automática**: Proxies temporales con fecha límite