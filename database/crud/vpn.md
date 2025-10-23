# CRUD VPN (`database/crud/vpn.py`)

## Descripción del Propósito

Operaciones CRUD para configuraciones VPN. Maneja creación, consulta, actualización y eliminación de VPNs con soporte para trials, expiración y métricas.

## Funciones Principales

### `get_vpn_config(session: AsyncSession, vpn_id: str) -> Optional[models.VPNConfig]`
Obtiene configuración VPN por ID.
- **Parámetros**: `session`, `vpn_id` (UUID)
- **Retorno**: VPNConfig o None

### `get_vpn_configs_for_user(session: AsyncSession, user_id: str) -> List[models.VPNConfig]`
Lista todas las VPNs de un usuario.
- **Parámetros**: `session`, `user_id`
- **Retorno**: Lista de VPNConfig

### `create_vpn_config(session: AsyncSession, user_id: str, vpn_type: str, config_name: Optional[str], config_data: Dict | str, expires_at: Optional[datetime], extra_data: Optional[Dict], is_trial: bool = False, commit: bool = False) -> models.VPNConfig`
Crea nueva configuración VPN.
- **Parámetros**: `session`, `user_id`, `vpn_type`, `config_name`, `config_data`, `expires_at`, `extra_data`, `is_trial`, `commit`
- **Retorno**: VPNConfig creado

### `create_trial_vpn(session: AsyncSession, user_id: str, vpn_type: str, config_name: Optional[str], config_data: Dict | str, duration_days: int = 7, extra_data: Optional[Dict], commit: bool = False) -> models.VPNConfig`
Crea VPN de prueba con duración limitada.
- **Validación**: Previene múltiples trials activos por usuario

### `update_vpn_status(session: AsyncSession, vpn_id: str, status: str, commit: bool = False) -> Optional[models.VPNConfig]`
Actualiza estado de VPN (active/revoked/expired).

### `revoke_vpn(session: AsyncSession, vpn_id: str, reason: str, commit: bool = False) -> bool`
Revoca VPN y registra razón.

### `get_active_trial_for_user(session: AsyncSession, user_id: str) -> Optional[models.VPNConfig]`
Obtiene trial activo de usuario.

### `get_expired_trials(session: AsyncSession) -> List[models.VPNConfig]`
Lista trials expirados para mantenimiento.

### Métricas:
- `count_vpn_configs_by_type()`: Cuenta por tipo
- `total_bandwidth_gb()`: Bandwidth total
- `count_vpn_configs_by_user()`: Cuenta por usuario
- `last_vpn_config_by_user()`: Última configuración

## Dependencias y Relaciones

- **Dependencias**:
  - `database.models`: Modelo VPNConfig
  - `sqlalchemy`: Operaciones de BD

- **Relaciones**:
  - Usado por `services.vpn` para operaciones de negocio
  - Base para `services.wireguard` y `services.outline`

## Ejemplos de Uso

```python
# Crear VPN WireGuard
vpn = await create_vpn_config(
    session, "user-123", "wireguard", "config1", 
    config_data, expires_at, extra_data
)

# Obtener VPNs de usuario
vpns = await get_vpn_configs_for_user(session, "user-123")

# Revocar VPN
await revoke_vpn(session, "vpn-id-456", "user_request")
```

## Consideraciones de Seguridad

- **Validación de tipos**: Verifica vpn_type válido
- **Prevención de trials múltiples**: Un trial activo por usuario
- **Control de expiración**: Manejo de fechas UTC
- **Transacciones**: Commit controlado por caller
- **Auditoría implícita**: Registra operaciones en BD