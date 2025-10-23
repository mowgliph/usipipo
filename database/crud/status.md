# CRUD Status (`database/crud/status.py`)

## Descripción del Propósito

Métricas y estadísticas del sistema para monitoreo y dashboards administrativos. Proporciona conteos eficientes de usuarios, VPNs, pagos y recursos del sistema.

## Funciones Principales

### Conteos de Usuarios:
- `count_users()`: Total de usuarios registrados
- `count_active_users()`: Usuarios activos
- `count_admins()`: Usuarios con rol admin
- `count_superadmins()`: Usuarios con rol superadmin

### Conteos de VPNs:
- `count_vpn_configs()`: Total de configuraciones VPN
- `count_vpn_configs_by_type(vpn_type)`: Por tipo (wireguard/outline)
- `count_active_vpn_configs()`: VPNs activas
- `count_trial_vpn_configs()`: VPNs de prueba
- `count_paid_vpn_configs()`: VPNs pagas

### Métricas de Recursos:
- `total_bandwidth_gb()`: Bandwidth total usado
- `count_payments()`: Total de pagos
- `count_pending_payments()`: Pagos pendientes
- `count_successful_payments()`: Pagos exitosos

### Gestión de IPs:
- `count_ips()`: Total de IPs en manager
- `count_available_ips()`: IPs disponibles
- `count_assigned_ips()`: IPs asignadas

### Dashboard Completo:
- `get_system_status()`: Resumen completo del sistema

## Dependencias y Relaciones

- **Dependencias**:
  - `database.models`: Todos los modelos del sistema
  - `sqlalchemy`: Funciones de agregación (func.count, func.sum)

- **Relaciones**:
  - Usado por `services.status` para comando /status
  - Base para dashboards administrativos
  - Métricas para monitoreo del sistema

## Ejemplos de Uso

```python
# Obtener métricas del sistema
status = await get_system_status(session)
# Retorna: {
#     "users": {"total": 150, "active": 120, "admins": 5},
#     "vpn": {"total": 200, "active": 180, "trials": 20},
#     "bandwidth_gb": 1250.5,
#     ...
# }

# Contar VPNs por tipo
wireguard_count = await count_vpn_configs_by_type(session, "wireguard")
```

## Consideraciones de Seguridad

- **Acceso administrativo**: Solo para admins y superadmins
- **Consultas eficientes**: Usa índices de BD para performance
- **Manejo de errores**: Logging detallado de fallos
- **Datos en tiempo real**: No cache, consultas directas