# Servicio VPN (`services/vpn.py`)

## Descripción del Propósito

Este módulo proporciona una interfaz unificada para gestionar configuraciones VPN de diferentes tipos (WireGuard y Outline). Centraliza la lógica de creación, activación y revocación de VPNs, manejando errores y registrando auditorías.

## Funciones Principales

### `list_user_vpns(session: AsyncSession, user_id: str) -> list[models.VPNConfig]`
Lista todas las configuraciones VPN activas de un usuario.
- **Parámetros**: `session` (sesión DB), `user_id` (UUID del usuario)
- **Retorno**: Lista de objetos VPNConfig
- **Excepciones**: SQLAlchemyError si falla la consulta

### `activate_vpn_for_user(session: AsyncSession, user_id: str, vpn_type: Literal["wireguard", "outline"], months: int) -> Optional[models.VPNConfig]`
Crea o renueva una configuración VPN según el tipo especificado.
- **Parámetros**:
  - `session`: Sesión de base de datos
  - `user_id`: UUID del usuario
  - `vpn_type`: Tipo de VPN ('wireguard' o 'outline')
  - `months`: Duración en meses
- **Retorno**: VPNConfig creado o None si falla
- **Excepciones**: ValueError para tipos inválidos, SQLAlchemyError para errores de DB

### `revoke_vpn(session: AsyncSession, vpn_id: str, vpn_type: Literal["wireguard", "outline"]) -> Optional[models.VPNConfig]`
Revoca una configuración VPN existente.
- **Parámetros**: `session`, `vpn_id` (UUID de la VPN), `vpn_type`
- **Retorno**: VPNConfig actualizado o None si no existe
- **Excepciones**: ValueError para tipos inválidos, SQLAlchemyError

### `count_vpn_configs_by_user(session: AsyncSession, user_id: str) -> int`
Cuenta configuraciones VPN activas de un usuario.
- **Parámetros**: `session`, `user_id`
- **Retorno**: Número entero de configuraciones

### `last_vpn_config_by_user(session: AsyncSession, user_id: str) -> Optional[models.VPNConfig]`
Obtiene la configuración VPN más reciente de un usuario.
- **Parámetros**: `session`, `user_id`
- **Retorno**: VPNConfig más reciente o None

## Dependencias y Relaciones

- **Dependencias**:
  - `database.models`: Modelos de datos
  - `services.wireguard`: Servicio específico de WireGuard
  - `services.outline`: Servicio específico de Outline
  - `database.crud.vpn`: Operaciones CRUD para VPN
  - `database.crud.logs`: Registro de auditoría
  - `utils.helpers`: Utilidades de logging

- **Relaciones con otros módulos**:
  - Llama a `wireguard.create_peer()` y `outline.create_access()` para creación
  - Usa `crud_logs.create_audit_log()` para auditoría
  - Integrado con handlers de bot para comandos VPN

## Ejemplos de Uso

```python
# Crear VPN WireGuard por 3 meses
vpn = await activate_vpn_for_user(session, "user-123", "wireguard", 3)

# Listar VPNs de usuario
vpns = await list_user_vpns(session, "user-123")

# Revocar VPN
await revoke_vpn(session, vpn.id, "wireguard")
```

## Consideraciones de Seguridad

- **Validación de entrada**: Verifica tipos VPN permitidos
- **Auditoría completa**: Registra todas las operaciones en logs
- **Manejo de errores**: Captura y registra excepciones específicas
- **Control de transacciones**: Commit manejado por el caller para consistencia