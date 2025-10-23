# Handler Status (`bot/handlers/status.py`)

## Descripción del Propósito

Proporciona comando /status para administradores, mostrando métricas del sistema en tiempo real.

## Funciones Principales

### `status_command(update: Update, context: ContextTypes) -> None`
Muestra estado completo del sistema.
- **Comando**: `/status`
- **Permisos**: Admin requerido
- **Métricas mostradas**:
  - Usuarios registrados
  - Configuraciones WireGuard/Outline activas
  - Consumo total de bandwidth
  - Uptime del bot
  - Estado de conexión a BD

## Dependencias y Relaciones

- **Dependencias**:
  - `services.status`: Obtención de métricas
  - `utils.permissions`: Decorador require_admin
  - `utils.helpers`: Funciones de respuesta

- **Relaciones**:
  - Solo accesible para administradores
  - Integra con servicio de métricas del sistema
  - Registra consulta en audit logs

## Ejemplos de Uso

```python
# Ver estado del sistema
/status
# Respuesta:
# 📊 Estado de uSipipo Bot
# 👥 Usuarios registrados: 150
# 🌐 Configs WireGuard: 45
# 🌐 Configs Outline: 23
# 📡 Consumo total: 1250.50 GB
# ⏱️ Uptime: 2d 5h 30m 15s
# 🗄️ Base de datos: ✅ Conectada
```

## Consideraciones de Seguridad

- **Permisos**: Solo administradores
- **Auditoría**: Registra consultas de status
- **Manejo de errores**: Notificación a equipo en fallos
- **Formato HTML**: Presentación clara de métricas