# Servicio de Alertas (`services/alerts.py`)

## Descripción del Propósito

Gestiona notificaciones y alertas del sistema uSipipo. Envía mensajes broadcast a usuarios, alertas de expiración de VPN, y reportes diarios de status a superadministradores.

## Funciones Principales

### `send_broadcast_message(session: AsyncSession, bot: Bot, sender_user_id: str, message: str, batch_size: int = 100) -> tuple[int, List[str]]`
Envía mensaje a todos los usuarios activos con rate limiting.
- **Parámetros**: `session`, `bot`, `sender_user_id`, `message`, `batch_size`
- **Retorno**: Tupla (total_enviados, lista_errores)
- **Validaciones**: Solo admins/superadmins, límite 4096 caracteres

### `get_expiring_vpns(session: AsyncSession, hours: int = 24, limit: int = 100, offset: int = 0) -> List[models.VPNConfig]`
Obtiene VPNs que expiran pronto con paginación.
- **Parámetros**: `session`, `hours`, `limit`, `offset`
- **Retorno**: Lista de VPNConfig próximas a expirar

### `get_expired_vpns(session: AsyncSession, limit: int = 100, offset: int = 0) -> List[models.VPNConfig]`
Obtiene VPNs ya expiradas.

### `send_expiration_alerts(session: AsyncSession, bot: Bot, hours: int = 24, limit: int = 100) -> None`
Envía alertas de expiración a usuarios afectados.

### `send_daily_status_notification(bot: Bot, context: ContextTypes.DEFAULT_TYPE = None) -> None`
Envía reporte diario de status a superadministradores.
- **Métricas incluidas**: usuarios totales, VPNs por tipo, bandwidth, uptime, status DB

## Dependencias y Relaciones

- **Dependencias**:
  - `telegram.Bot`: Cliente de Telegram
  - `database.crud.logs`: Auditoría
  - `database.crud.vpn`: Consultas VPN
  - `database.crud.users`: Gestión usuarios
  - `services.status`: Métricas del sistema
  - `config.superadmins`: Lista de superadmins
  - `utils.helpers`: Utilidades de logging y notificaciones

- **Relaciones**:
  - Usado por jobs del sistema para notificaciones automáticas
  - Integra con handlers administrativos para broadcasts manuales
  - Registra todas las operaciones en audit logs

## Ejemplos de Uso

```python
# Enviar broadcast (solo admins)
total, errors = await send_broadcast_message(session, bot, "admin-123", "Mensaje importante")

# Obtener VPNs expirando en 24 horas
expiring = await get_expiring_vpns(session, hours=24)

# Enviar alertas de expiración
await send_expiration_alerts(session, bot)
```

## Consideraciones de Seguridad

- **Validación de permisos**: Solo admins/superadmins pueden enviar broadcasts
- **Rate limiting**: 35 mensajes/segundo para evitar spam
- **Sanitización**: Mensajes parseados como HTML
- **Auditoría completa**: Registra envíos, errores y métricas
- **Paginación**: Manejo eficiente de grandes volúmenes de usuarios
- **Manejo de errores**: Notificación a admins en caso de fallos críticos
- **Prevención de spam**: Evita alertas repetidas con flag 'alerted'