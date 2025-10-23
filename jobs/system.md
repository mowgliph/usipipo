# Job del Sistema (`jobs/system.py`)

## Descripción del Propósito

Tarea básica del sistema que mantiene el bot activo y registra el estado de funcionamiento periódico.

## Funciones Principales

### `ping_job(context: ContextTypes.DEFAULT_TYPE) -> None`
Job de ping que se ejecuta cada 60 segundos.
- **Propósito**: Mantener el bot vivo y registrar estado del sistema
- **Información registrada**:
  - PID del proceso
  - Versión del bot (`BOT_VERSION`)
  - Versión de Python
  - Estado: RUNNING

## Operaciones Realizadas

1. **Registro en logs tradicionales**:
   - Logger central registra mensaje con PID y versiones
   - Incluye `user_id: None` para identificar como sistema

2. **Registro en audit logs**:
   - Usa `log_action_auto_session()` para auditoría asíncrona
   - Payload con mensaje completo
   - Acción: "system_ping"

## Dependencias y Relaciones

- **Dependencias**:
  - `os`: Obtener PID del proceso
  - `platform`: Versión de Python
  - `config.config`: Versión del bot
  - `services.audit`: Logging de auditoría

- **Relaciones**:
  - Registrado en `register_jobs.py` para ejecución cada 60s
  - Complementa jobs de mantenimiento y alertas
  - Base para monitoreo de salud del sistema

## Ejemplos de Ejecución

```python
# Se ejecuta automáticamente cada 60 segundos
# Log generado:
# INFO - PID:1234 | Bot v1.0.0 | Python v3.11.0 | Status: RUNNING

# Audit log creado:
# {
#   "action": "system_ping",
#   "payload": {
#     "message": "PID:1234 | Bot v1.0.0 | Python v3.11.0 | Status: RUNNING"
#   }
# }
```

## Consideraciones de Seguridad

- **Información no sensible**: Solo expone versiones y PID
- **Frecuencia apropiada**: 60s no genera spam pero mantiene actividad
- **Auditoría ligera**: Payload mínimo para no sobrecargar BD
- **Disponibilidad**: Job simple que no puede fallar
- **Monitoreo**: Permite verificar que el bot sigue ejecutándose