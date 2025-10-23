# Servicio Outline (`services/outline.py`)

## Descripción del Propósito

Cliente para la API de Outline VPN. Gestiona creación y revocación de access keys, verificación de certificados TLS y comunicación segura con el servidor Outline.

## Funciones Principales

### `_verify_outline_cert() -> bool`
Verifica fingerprint SHA256 del certificado TLS de Outline.
- **Verificación**: Compara hash remoto con OUTLINE_CERT_SHA256
- **Ejecuta en thread**: Usa asyncio.run_in_executor para socket operations
- **Retorno**: True si coincide, False si no

### `_outline_request(method: str, path: str, json: Optional[Dict] = None, timeout: int = 10) -> Optional[Dict]`
Realiza petición HTTP a API de Outline con verificación de certificado.
- **Parámetros**: `method`, `path`, `json`, `timeout`
- **Flujo**: Verifica cert → petición con ssl=False → parse JSON
- **Retorno**: Dict de respuesta o None

### `create_access(session: AsyncSession, user_id: str, duration_months: int = 1, commit: bool = False) -> Dict[str, Any]`
Crea access key en Outline y registra en DB.
- **Parámetros**: `session`, `user_id`, `duration_months`, `commit`
- **Retorno**: Dict con config_data, extra_data, vpn_obj
- **Expiración**: Calcula fecha fin basada en meses

### `revoke_access(session: AsyncSession, vpn_id: str, commit: bool = False) -> Optional[models.VPNConfig]`
Revoca access key en Outline y actualiza DB.
- **Parámetros**: `session`, `vpn_id`, `commit`
- **Flujo**: DELETE a API → update status a 'revoked'

### `list_user_accesses(session: AsyncSession, user_id: str) -> List[models.VPNConfig]`
Lista access keys Outline de un usuario.

## Dependencias y Relaciones

- **Dependencias**:
  - `aiohttp`: Cliente HTTP asíncrono
  - `ssl, socket, hashlib`: Verificación de certificados
  - `urllib.parse`: Parsing de URLs
  - `database.crud.vpn`: Operaciones DB

- **Relaciones**:
  - Integrado con `services.vpn` para interfaz unificada
  - Usa variables de entorno: OUTLINE_API_URL, OUTLINE_CERT_SHA256
  - Comparte lógica de expiración con otros servicios VPN

## Ejemplos de Uso

```python
# Crear access key de 3 meses
result = await create_access(session, "user-123", duration_months=3)
config_url = result["config_data"]  # ss://...

# Revocar access key
await revoke_access(session, "vpn-id-456")

# Listar accesos del usuario
accesses = await list_user_accesses(session, "user-123")
```

## Consideraciones de Seguridad

- **Verificación de certificado**: Fingerprint SHA256 obligatorio
- **Validación de URL**: Parsing seguro de OUTLINE_API_URL
- **Timeouts**: Límite de 10 segundos por defecto
- **Manejo de errores**: RuntimeError para fallos críticos
- **Configuración requerida**: Variables de entorno críticas validadas
- **Auditoría implícita**: Registra operaciones en DB