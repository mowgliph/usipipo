# Servicio de Status (`services/status.py`)

## Descripción del Propósito

Proporciona métricas del sistema para el comando /status del bot. Calcula uptime, cuenta usuarios activos, configuraciones VPN y bandwidth total, verificando también el estado de la conexión a base de datos.

## Funciones Principales

### `format_uptime(seconds: float) -> str`
Convierte segundos en formato legible (días, horas, minutos, segundos).
- **Parámetros**: `seconds` (tiempo en segundos)
- **Retorno**: String formateado (ej: "1d 2h 30m 45s")

### `get_status_metrics(session: AsyncSession) -> Dict[str, Any]`
Obtiene métricas globales del sistema para /status.
- **Métricas incluidas**:
  - `total_users`: Número total de usuarios
  - `total_wireguard`: Configuraciones WireGuard activas
  - `total_outline`: Configuraciones Outline activas
  - `total_bandwidth`: Bandwidth total en GB
  - `uptime`: Tiempo de actividad formateado
  - `db_status`: Estado de conexión a BD ("✅ Conectada" o "❌ Error")
- **Retorno**: Dict con todas las métricas
- **Auditoría**: Registra la consulta en AuditLog

## Dependencias y Relaciones

- **Dependencias**:
  - `database.crud.status`: Funciones CRUD para métricas
  - `services.audit`: Servicio de auditoría
  - `config.runtime`: Tiempo de inicio del bot
  - `datetime`: Manejo de fechas y timezone

- **Relaciones**:
  - Usado por handlers del bot para comando /status
  - Integra con `database.crud.status` para consultas eficientes
  - Registra acciones en audit logs

## Ejemplos de Uso

```python
# Obtener métricas del sistema
metrics = await get_status_metrics(session)
# Retorna: {
#     "total_users": 150,
#     "total_wireguard": 45,
#     "total_outline": 23,
#     "total_bandwidth": 1250.5,
#     "uptime": "2d 5h 30m 15s",
#     "db_status": "✅ Conectada"
# }
```

## Consideraciones de Seguridad

- **Auditoría completa**: Registra todas las consultas de status
- **Validación de estado**: Verifica conectividad a BD
- **Acceso controlado**: Solo disponible para administradores
- **Manejo de errores**: Captura excepciones y registra en logs