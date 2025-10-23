# Servicio WireGuard (`services/wireguard.py`)

## Descripción del Propósito

Cliente completo para gestión de VPN WireGuard. Maneja generación de claves, asignación de IPs, configuración de peers en el servidor y creación de archivos de configuración cliente.

## Funciones Principales

### `generate_keys() -> Tuple[str, str]`
Genera par de claves WireGuard usando comandos del sistema.
- **Comandos**: `wg genkey | wg pubkey`
- **Retorno**: (private_key, public_key)

### `get_next_ip(session: AsyncSession) -> str`
Asigna siguiente IP disponible en el rango configurado.
- **Rango**: IP_RANGE_START a IP_RANGE_END
- **Formato**: CIDR (ej: "10.10.0.3/32")
- **Validación**: Evita colisiones consultando DB

### `_wg_add_peer(public_key: str, address: str) -> None`
Añade peer al interfaz WireGuard del servidor.
- **Comando**: `wg set WG_INTERFACE peer {public_key} allowed-ips {address}`

### `_wg_remove_peer(public_key: str) -> None`
Remueve peer del interfaz WireGuard.

### `create_peer(session: AsyncSession, user_id: str, duration_months: int = 1, dns: Optional[str] = None, config_name: Optional[str] = None, commit: bool = False) -> Dict[str, Any]`
Crea peer completo con configuración cliente.
- **Flujo**:
  1. Generar claves y reservar IP
  2. Escribir archivo .conf atómicamente
  3. Crear registro DB con status 'creating'
  4. Añadir peer al servidor
  5. Actualizar status a 'active'
- **Retorno**: Dict con config_data, extra_data, vpn_obj

### `revoke_peer(session: AsyncSession, vpn_id: str, commit: bool = False) -> Optional[models.VPNConfig]`
Revoca peer: remueve del servidor y marca como revoked en DB.

### `list_user_peers(session: AsyncSession, user_id: str) -> List[models.VPNConfig]`
Lista peers WireGuard activos del usuario.

### `generate_qr(config_data: str) -> bytes`
Genera código QR de configuración usando qrencode.
- **Retorno**: Bytes PNG del QR

## Dependencias y Relaciones

- **Dependencias**:
  - `asyncio.subprocess`: Ejecución de comandos wg y qrencode
  - `aiofiles`: Escritura atómica de archivos
  - `tempfile`: Archivos temporales para escritura segura
  - `database.crud.vpn`: Operaciones DB

- **Relaciones**:
  - Variables de entorno requeridas: WG_INTERFACE, WG_CONFIG_DIR, etc.
  - Integrado con `services.vpn` para interfaz unificada
  - Usa `database.crud.vpn` para persistencia

## Ejemplos de Uso

```python
# Crear peer de 6 meses
result = await create_peer(session, "user-123", duration_months=6)
config = result["config_data"]  # Configuración cliente
qr_bytes = await generate_qr(config)  # Generar QR

# Revocar peer
await revoke_peer(session, "vpn-id-456")
```

## Consideraciones de Seguridad

- **Validación de configuración**: Variables de entorno críticas requeridas
- **Escritura atómica**: Usa archivos temporales para evitar corrupción
- **Asignación de IP**: Evita colisiones consultando DB existente
- **Manejo de errores**: Rollback en fallos parciales
- **Comandos del sistema**: Ejecuta wg con permisos apropiados
- **Timeouts**: Control de tiempo en operaciones del servidor