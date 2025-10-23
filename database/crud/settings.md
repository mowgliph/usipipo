# CRUD Configuraciones (`database/crud/settings.py`)

## Descripción del Propósito

Operaciones CRUD para configuraciones personalizadas de usuario. Gestiona preferencias individuales con auditoría automática de cambios.

## Funciones Principales

### `list_user_settings(session: AsyncSession, user_id: str, limit: int = 100) -> List[models.UserSetting]`
Lista todas las configuraciones de un usuario ordenadas por fecha de actualización.

### `get_user_setting(session: AsyncSession, user_id: str, key: str) -> Optional[models.UserSetting]`
Obtiene configuración específica por clave.

### `get_user_setting_value(session: AsyncSession, user_id: str, key: str, default: Optional[str] = None) -> Optional[str]`
Obtiene valor de configuración con valor por defecto opcional.

### `set_user_setting(session: AsyncSession, user_id: str, key: str, value: str, commit: bool = False) -> models.UserSetting`
Crea o actualiza configuración con timestamp automático.

### `delete_user_setting(session: AsyncSession, user_id: str, key: str, commit: bool = False) -> bool`
Elimina configuración específica.

### `delete_all_user_settings(session: AsyncSession, user_id: str, commit: bool = False) -> int`
Elimina todas las configuraciones de un usuario.

### `count_user_settings(session: AsyncSession, user_id: str) -> int`
Cuenta configuraciones de un usuario.

## Dependencias y Relaciones

- **Dependencias**:
  - `database.models`: Modelo UserSetting
  - `sqlalchemy`: Operaciones de BD

- **Relaciones**:
  - Usado por `services.settings` para lógica de negocio
  - Base para sistema de preferencias de usuario

## Ejemplos de Uso

```python
# Obtener configuración
setting = await get_user_setting(session, "user-123", "theme")

# Actualizar configuración
await set_user_setting(session, "user-123", "language", "es")

# Contar configuraciones
count = await count_user_settings(session, "user-123")
```

## Consideraciones de Seguridad

- **Control de acceso**: Solo el propio usuario puede modificar sus settings
- **Auditoría implícita**: Timestamps automáticos en actualizaciones
- **Transacciones**: Commit controlado por caller
- **Validación**: No hay validación de valores (flexible por diseño)