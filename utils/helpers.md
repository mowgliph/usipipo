# Utilitarios Helpers (`utils/helpers.py`)

## Descripción del Propósito

Colección de funciones auxiliares para el bot uSipipo. Maneja mensajes de respuesta, logging estructurado, notificaciones, formateo de datos y validaciones comunes.

## Funciones Principales

### Mensajes de Respuesta (siempre HTML):
- `send_usage_error()`: Errores de uso incorrecto de comandos
- `send_permission_error()`: Errores de permisos insuficientes
- `send_generic_error()`: Errores genéricos al usuario
- `send_warning()`: Advertencias al usuario
- `send_success()`: Confirmaciones de éxito
- `send_info()`: Mensajes informativos

### Logging y Notificación Unificada:
- `log_and_notify()`: Registra auditoría DB, logger y notifica usuario
- `log_error_and_notify()`: Manejo estructurado de errores con notificación limitada
- `notify_admins()`: Envía notificaciones a todos los administradores

### Utilitarios Adicionales:
- `format_days()`: Formatea cantidad de días (singular/plural)
- `safe_chat_id_from_update()`: Extrae chat_id de forma segura
- `format_roles_list()`: Formatea lista de roles activos en HTML
- `format_vpn_list()`: Formatea lista de VPNs en HTML

### Envío de Configuraciones VPN:
- `send_vpn_config()`: Envía config VPN según tipo (WireGuard: QR + .conf, Outline: URL)

### Formateo de Datos:
- `format_expiration_message()`: Mensajes de expiración de VPN
- `format_log_entry()`: Formatea entradas de log para Telegram
- `format_file_size()`: Convierte bytes a KB/MB/GB

### Validaciones:
- `validate_vpn_type()`: Verifica tipos VPN soportados
- `validate_ip_type()`: Verifica tipos IP soportados

## Dependencias y Relaciones

- **Dependencias**:
  - `telegram`: Tipos y envío de mensajes
  - `database.crud`: Operaciones de auditoría
  - `html`: Sanitización HTML
  - `io`, `traceback`: Manejo de archivos y errores

- **Relaciones**:
  - Usado por todos los handlers del bot
  - Base para logging consistente en todo el sistema
  - Integra con servicios de auditoría y notificaciones

## Ejemplos de Uso

```python
# Enviar error de uso
await send_usage_error(update, "newvpn", "<wireguard|outline> <months>")

# Logging unificado
await log_and_notify(
    session, bot, chat_id, user_id,
    action="vpn_created",
    details="VPN WireGuard creada",
    message="✅ VPN creada exitosamente"
)

# Enviar configuración VPN
await send_vpn_config(update, vpn, qr_bytes=qr, conf_file=conf)
```

## Consideraciones de Seguridad

- **Sanitización HTML**: Usa `html.escape()` para prevenir XSS
- **Validación de tipos**: Verifica tipos VPN/IP soportados
- **Manejo de errores**: Logging completo sin exponer detalles técnicos
- **Control de acceso**: Funciones de notificación solo para admins
- **Rate limiting**: No implementado (delegado a Telegram)