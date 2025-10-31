# 🗄️ Base de Datos

Este directorio contiene los modelos y operaciones CRUD de la base de datos.

## 📋 Modelos Principales (`models.py`)

### User
- Información del usuario
- Roles y permisos
- Estado y configuración

### VPNConfig
- Configuraciones VPN activas
- Tipo (WireGuard/Outline)
- Datos de config en JSON
- Fechas de expiración

### Payment
- Registro de pagos
- Método (Stars/QvaPay)
- Estado y detalles
- Referencias cruzadas

### IPManager
- Gestión de IPs
- Asignación y liberación
- Datos extra en JSON

## 📦 Operaciones CRUD

### Users (`crud/users.py`)
- Registro/actualización
- Consultas por TG ID
- Gestión de roles

### VPN (`crud/vpn.py`)
- Creación de configs
- Listado por usuario
- Revocación y cleanup

### Payments (`crud/payments.py`)
- Registro de transacciones
- Validación de pagos
- Histórico por usuario

### Status (`crud/status.py`)
- Métricas del sistema
- Conteos agregados
- Estado de recursos

## 🛠️ Utilidades BD (`db.py`)

### Sesiones
```python
async with get_session() as session:
    # Operaciones DB
    await session.commit()
```

### Inicialización
```python
# Desarrollo
await init_db()

# Producción
# Usar Alembic migrations
```

## 🔒 Consideraciones

### Seguridad
- Validación de tipos
- Sanitización de input
- Control de acceso
- Auditoría de cambios

### Rendimiento
- Índices optimizados
- Consultas eficientes
- Caching donde aplique

### Consistencia
- Transacciones atómicas
- Foreign keys
- Constraints únicos

## 📝 Notas Operativas

- `DATABASE_ASYNC_URL` requerido
- Driver async: `asyncmy`/`aiomysql`
- Sin migraciones Alembic (usa `init_db()` en dev)
- Mantener compatibilidad JSON en campos extra

## 🔍 Ejemplos de Uso

### Crear Usuario
```python
async with get_session() as session:
    user = await create_user(
        session,
        telegram_id="123456789",
        username="example"
    )
    await session.commit()
```

### Listar VPNs
```python
async with get_session() as session:
    vpns = await list_user_vpns(
        session,
        user_id="123456789"
    )
```

### Métricas
```python
async with get_session() as session:
    stats = await get_system_metrics(session)
    # Total usuarios, VPNs activas, etc.
```