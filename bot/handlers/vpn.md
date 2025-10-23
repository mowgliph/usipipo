# Handler VPN (`bot/handlers/vpn.py`)

## Descripción del Propósito

Maneja todos los comandos y callbacks relacionados con VPNs: creación, listado, revocación, trials y pagos. Integra servicios de pagos con Telegram Stars y QvaPay.

## Funciones Principales

### `newvpn_command(update: Update, context: ContextTypes) -> None`
Crea nueva VPN con menú de selección de método de pago.
- **Comando**: `/newvpn <wireguard|outline> <months>`
- **Funcionalidad**: Muestra botones inline para Stars/QvaPay
- **Validaciones**: Usuario registrado, tipos válidos

### `myvpns_command(update: Update, context: ContextTypes) -> None`
Lista VPNs del usuario.
- **Comando**: `/myvpns`
- **Funcionalidad**: Usa `format_vpn_list()` para mostrar configs

### `revokevpn_command(update: Update, context: ContextTypes) -> None`
Revoca VPN existente.
- **Comando**: `/revokevpn <vpn_id>`
- **Funcionalidad**: Verifica permisos y revoca

### `trialvpn_command(update: Update, context: ContextTypes) -> None`
Crea VPN de prueba (7 días).
- **Comando**: `/trialvpn <wireguard|outline>`
- **Funcionalidad**: Llama a `trial_service.start_trial()`

### `vpn_payment_callback_handler(update: Update, context: ContextTypes) -> None`
Maneja callbacks de pago VPN.
- **Callbacks**: `vpn_pay_stars:wireguard:3`, `vpn_pay_qvapay:wireguard:3:5.00`
- **Funcionalidad**: Crea invoices o procesa pagos QvaPay

### `precheckout_vpn_handler(update: Update, context: ContextTypes) -> None`
Valida pre-checkout de pagos con estrellas.

### `successful_payment_vpn_handler(update: Update, context: ContextTypes) -> None`
Procesa pagos exitosos y crea VPNs.

## Dependencias y Relaciones

- **Dependencias**:
  - `services.payments`: Lógica de pagos
  - `services.vpn_crud`: CRUD unificado de VPNs
  - `services.wireguard`: Generación de QR
  - `database.crud.payments`: Gestión de pagos
  - `utils.helpers`: Funciones de respuesta

- **Relaciones**:
  - Integra con handlers de pagos de Telegram
  - Usa servicios de validación de permisos
  - Registra todas las operaciones en audit logs

## Ejemplos de Uso

```python
# Comando para nueva VPN
/newvpn wireguard 3
# Muestra menú: [💳 Pagar con QvaPay] [⭐ Pagar con Estrellas]

# Callback de pago con estrellas
# vpn_pay_stars:wireguard:3
# Crea invoice de Telegram

# Pago exitoso
# Procesa automáticamente y envía config VPN
```

## Consideraciones de Seguridad

- **Validación de entrada**: Tipos VPN, meses, IDs válidos
- **Permisos**: Solo usuarios registrados
- **Rate limiting**: Implícito en handlers de Telegram
- **Auditoría completa**: Registra creación, pagos, revocaciones
- **Manejo de errores**: Notificación a admins en fallos críticos
- **Transacciones**: Commit controlado para consistencia