# Servicio de Usuario (`services/user.py`)

## Descripción del Propósito

Gestiona operaciones relacionadas con usuarios del sistema uSipipo. Maneja creación/actualización de usuarios, asignación de roles administrativos, configuración de preferencias y generación de mensajes de ayuda contextuales.

## Funciones Principales

### `ensure_user_exists(session: AsyncSession, tg_payload: Dict[str, Any]) -> models.User`
Asegura existencia de usuario en DB desde payload de Telegram.
- **Parámetros**: `session`, `tg_payload` (datos de Telegram)
- **Retorno**: Objeto User creado/actualizado

### `promote_to_admin(session: AsyncSession, user_id: str) -> Optional[models.User]`
Asigna permisos de administrador con auditoría.
- **Parámetros**: `session`, `user_id`
- **Retorno**: User actualizado o None

### `demote_from_admin(session: AsyncSession, user_id: str) -> Optional[models.User]`
Remueve permisos de administrador con auditoría.

### `list_all_users(session: AsyncSession, limit: int = 50) -> List[models.User]`
Lista usuarios con paginación.

### `get_user_settings(session: AsyncSession, user_id: str) -> List[models.UserSetting]`
Obtiene configuraciones de usuario.

### `update_user_setting(session: AsyncSession, user_id: str, key: str, value: str) -> Optional[models.UserSetting]`
Actualiza configuración de usuario con auditoría.

### `get_user_telegram_info(session: AsyncSession, tg_user: TelegramUser) -> str`
Genera información formateada de Telegram del usuario.
- **Retorno**: String HTML con ID, nombre, username

### `get_help_message(session: AsyncSession, user_id: Optional[str]) -> str`
Genera mensaje de ayuda contextual según rol del usuario.
- **Retorno**: String HTML con comandos disponibles

## Dependencias y Relaciones

- **Dependencias**:
  - `database.crud.users`: Operaciones CRUD de usuarios
  - `database.crud.settings`: Gestión de configuraciones
  - `database.crud.roles`: Gestión de roles
  - `database.crud.logs`: Auditoría
  - `telegram.User`: Tipos de Telegram
  - `html`: Sanitización HTML

- **Relaciones**:
  - Usado por handlers de bot para comandos de usuario
  - Integra con `services.admin` para gestión administrativa
  - Registra acciones en audit logs

## Ejemplos de Uso

```python
# Asegurar usuario existe
user = await ensure_user_exists(session, telegram_payload)

# Obtener info de Telegram
info = await get_user_telegram_info(session, telegram_user)
# Retorna: "<b>Tu información...</b>"

# Generar ayuda para admin
help_msg = await get_help_message(session, "user-123")
```

## Consideraciones de Seguridad

- **Sanitización HTML**: Usa `html.escape()` para prevenir XSS
- **Validación de permisos**: Verifica roles antes de operaciones admin
- **Auditoría completa**: Registra todas las operaciones administrativas
- **Prevención de auto-asignación**: Bloquea promoción/demotción propia
- **Control de acceso**: Mensajes de ayuda contextuales por rol