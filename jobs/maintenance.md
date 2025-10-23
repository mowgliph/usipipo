# Job de Mantenimiento (`jobs/maintenance.py`)

## Descripción del Propósito

Tarea periódica que realiza limpieza automática del sistema: eliminación de logs antiguos y revocación de trials expirados.

## Funciones Principales

### `maintenance_job(context: ContextTypes.DEFAULT_TYPE) -> None`
Job principal de mantenimiento ejecutado periódicamente.
- **Limpieza de logs**: Elimina registros de auditoría >30 días
- **Revocación de trials**: Desactiva VPNs de prueba expiradas
- **Notificaciones**: Informa a admins solo si hubo cambios
- **Auditoría**: Registra todas las operaciones realizadas

## Operaciones Realizadas

1. **Eliminación de logs antiguos**:
   - Corta a 30 días atrás
   - Usa `crud_logs.delete_old_logs()`
   - Registra cantidad eliminada

2. **Revocación de trials expirados**:
   - Obtiene trials vencidos con `crud_vpn.get_expired_trials()`
   - Revoca en servicios WireGuard/Outline
   - Actualiza estado en BD
   - Registra auditoría por cada revocación

3. **Notificación condicional**:
   - Solo notifica admins si hubo cambios (logs eliminados o trials revocados)
   - Envía resumen con estadísticas
   - Usa `notify_admins()` con formato HTML

4. **Auditoría completa**:
   - Registra ejecución exitosa o errores
   - Payload con detalles de operaciones

## Dependencias y Relaciones

- **Dependencias**:
  - `database.crud.logs`: Eliminación de logs antiguos
  - `database.crud.vpn`: Consulta de trials expirados
  - `services.wireguard`: Revocación de peers WireGuard
  - `services.outline`: Revocación de access Outline
  - `utils.helpers`: Notificaciones a admins

- **Relaciones**:
  - Registrado en `register_jobs.py` para ejecución cada 24h
  - Integra con sistema de alertas y notificaciones
  - Complementa jobs de expiración y status

## Ejemplos de Ejecución

```python
# Se ejecuta automáticamente cada 24h a las 03:00 UTC
# Resultado típico:
🧹 Mantenimiento completado

🗑️ Logs eliminados: 1500
❌ Trials revocados: 5
⏱️ Fecha: 2025-10-23 03:00 UTC
```

## Consideraciones de Seguridad

- **Transacciones seguras**: Commit al final de todas las operaciones
- **Manejo de errores**: Rollback en caso de fallos
- **Auditoría detallada**: Registra cada operación individual
- **Notificación selectiva**: Solo informa cuando hay cambios
- **Separación de responsabilidades**: Una operación por tipo de mantenimiento