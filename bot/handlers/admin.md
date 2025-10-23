# Handler Administrativo (`bot/handlers/admin.py`)

## Descripción del Propósito

Proporciona comandos administrativos para gestión de usuarios, roles y auditoría del sistema. Solo accesible para superadministradores.

## Funciones Principales

### `users_command(update: Update, context: ContextTypes) -> None`
Lista usuarios recientes con paginación.
- **Comando**: `/users [limit]`
- **Permisos**: Superadmin requerido
- **Formato**: HTML con ID, nombre, roles, fecha creación

### `promote_command(update: Update, context: ContextTypes) -> None`
Promueve usuario a administrador.
- **Comando**: `/promote <user_id|telegram_id>`
- **Funcionalidad**: Soporta UUID o Telegram ID
- **Auditoría**: Registra acción con acting_user_id

### `demote_command(update: Update, context: ContextTypes) -> None`
Revoca permisos de administrador.

### `setsuper_command(update: Update, context: ContextTypes) -> None`
Asigna rol de superadministrador.

### `listadmins_command(update: Update, context: ContextTypes) -> None`
Lista todos los administradores y superadministradores.

### `roles_command(update: Update, context: ContextTypes) -> None`
Muestra roles activos de un usuario específico.

### `audit_command(update: Update, context: ContextTypes) -> None`
Muestra logs de auditoría recientes.
- **Comando**: `/audit [limit]`
- **Funcionalidad**: Usa `format_logs()` para presentación

## Dependencias y Relaciones

- **Dependencias**:
  - `services.admin`: Lógica de gestión administrativa
  - `services.audit`: Consultas de auditoría
  - `database.crud.users`: Operaciones de usuarios
  - `utils.permissions`: Decorador require_superadmin

- **Relaciones**:
  - Solo accesible para superadministradores
  - Registra todas las operaciones administrativas
  - Integra con sistema de notificaciones a admins

## Ejemplos de Uso

```python
# Listar usuarios recientes
/users 20

# Promover usuario
/promote 1234567890

# Ver logs de auditoría
/audit 50
```

## Consideraciones de Seguridad

- **Permisos estrictos**: Solo superadministradores
- **Validación de entrada**: IDs válidos, límites numéricos
- **Auditoría completa**: Registra todas las acciones admin
- **Manejo de errores**: Notificación a admins en fallos
- **Soporte flexible**: Acepta tanto UUID como Telegram ID
- **Paginación**: Control de volumen de datos