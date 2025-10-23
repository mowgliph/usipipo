# Registro de Jobs (`jobs/register_jobs.py`)

## Descripción del Propósito

Centraliza el registro de todas las tareas periódicas del sistema en la cola de jobs de Telegram.

## Funciones Principales

### `register_jobs(app: Application) -> None`
Registra todas las tareas programadas en la aplicación Telegram.

## Jobs Registrados

### 1. Ping Job
- **Función**: `ping_job` desde `jobs.system`
- **Intervalo**: Cada 60 segundos
- **Propósito**: Mantener bot vivo y registrar estado del sistema

### 2. Maintenance Job
- **Función**: `maintenance_job` desde `jobs.maintenance`
- **Intervalo**: Cada 24 horas (86400 segundos)
- **Inicio**: Primera ejecución a las 3:00 UTC
- **Propósito**: Limpieza de logs antiguos y revocación de trials expirados

### 3. Expiration Alerts Job
- **Función**: `expiration_alerts_job` desde `bot.handlers.alerts`
- **Horario**: Diariamente a las 9:00 UTC
- **Días**: Todos los días de la semana (0-6)
- **Propósito**: Enviar alertas de VPNs próximas a expirar

### 4. Daily Status Notification
- **Función**: `send_daily_status_notification` desde `services.alerts`
- **Horario**: Diariamente a medianoche UTC (00:00)
- **Días**: Todos los días de la semana
- **Propósito**: Enviar reporte diario de status a superadministradores

## Dependencias y Relaciones

- **Dependencias**:
  - `telegram.ext.Application`: Cola de jobs de Telegram
  - `datetime.time`: Configuración de horarios
  - `zoneinfo.ZoneInfo`: Zonas horarias UTC

- **Relaciones**:
  - Punto de entrada único para configuración de jobs
  - Importa funciones desde módulos específicos
  - Ejecutado durante inicialización del bot

## Ejemplos de Configuración

```python
# En main.py o app.py
from jobs.register_jobs import register_jobs

app = Application.builder().token(TOKEN).build()
register_jobs(app)  # Registra todos los jobs
```

## Consideraciones de Seguridad

- **Horarios UTC**: Todos los jobs usan zona horaria UTC para consistencia
- **Intervalos apropiados**: Jobs de mantenimiento no interfieren con operaciones normales
- **Ejecución asíncrona**: Todos los jobs son async para no bloquear el bot
- **Logging integrado**: Cada job registra su ejecución en logs
- **Configuración centralizada**: Fácil de modificar intervalos y horarios