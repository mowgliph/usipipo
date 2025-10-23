# Servicio de Configuraciones (`services/settings.py`)

## Descripción del Propósito

Gestiona configuraciones personalizadas de usuario con auditoría completa. Permite crear, actualizar y consultar preferencias individuales de cada usuario del sistema.

## Funciones Principales

### `get_settings(session: AsyncSession, user_id: str) -> List[models.UserSetting]`
Obtiene todas las configuraciones de un usuario.
- **Parámetros**: `session`, `user_id`
- **Retorno**: Lista de UserSetting o lista vacía si error

### `get_setting(session: AsyncSession, user_id: str, key: str) -> Optional[models.UserSetting]`
Obtiene configuración específica por clave.
- **Parámetros**: `session`, `user_id`, `key`
- **Retorno**: UserSetting o None si no existe/error

### `update_setting(session: AsyncSession, user_id: str, key: str, value: str) -> Optional[models.UserSetting]`
Crea o actualiza configuración con auditoría.
- **Parámetros**: `session`, `user_id`, `key`, `value`
- **Retorno**: UserSetting actualizado o None si error
- **Transacción**: Commit automático para consistencia

## Dependencias y Relaciones

- **Dependencias**:
  - `database.crud.settings`: Operaciones CRUD de configuraciones
  - `database.crud.logs`: Auditoría de cambios
  - `database.models`: Modelo UserSetting

- **Relaciones**:
  - Usado por handlers de usuario para preferencias
  - Integra con sistema de auditoría para tracking de cambios
  - Complementa `services.user` para gestión completa de usuarios

## Ejemplos de Uso

```python
# Obtener todas las configuraciones
settings = await get_settings(session, "user-123")

# Obtener configuración específica
theme = await get_setting(session, "user-123", "theme")
if theme:
    print(f"Tema: {theme.value}")

# Actualizar configuración
updated = await update_setting(session, "user-123", "language", "es")
```

## Consideraciones de Seguridad

- **Auditoría completa**: Registra todos los cambios de configuración
- **Manejo de errores**: Rollback automático en fallos
- **Validación de acceso**: Solo el propio usuario puede modificar sus settings
- **Consistencia**: Transacciones atómicas para cambios y auditoría