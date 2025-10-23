# Sistema de Permisos (`utils/permissions.py`)

## Descripción del Propósito

Decoradores para control de acceso basado en roles. Gestiona permisos de administrador, superadministrador y registro obligatorio con auto-registro automático.

## Decoradores Principales

### `@require_admin`
Requiere permisos de administrador. Auto-registra usuarios desde `ADMIN_TG_IDS` si no existen.

### `@require_superadmin`
Requiere permisos de superadministrador. Auto-registra usuarios desde `config/superadmins.py`.

### `@require_registered`
Asegura que el usuario esté registrado. Auto-registra admins/superadmins, requiere registro manual para usuarios normales.

## Funciones Auxiliares

### `_auto_register_admin()`
Registra automáticamente usuarios como admin/superadmin desde configuración.
- Crea usuario en BD si no existe
- Asigna permisos correspondientes
- Registra auditoría de registro automático

## Dependencias y Relaciones

- **Dependencias**:
  - `database.crud.users`: Operaciones de usuarios y permisos
  - `config.superadmins`: Lista de superadministradores
  - `config.config`: Lista de administradores
  - `utils.helpers`: Funciones de logging y respuesta

- **Relaciones**:
  - Usado por todos los handlers que requieren permisos
  - Integra con sistema de registro automático
  - Base para control de acceso en todo el bot

## Ejemplos de Uso

```python
# Comando solo para admins
@require_admin
async def status_command(update: Update, context: ContextTypes) -> None:
    # Solo accesible para administradores
    pass

# Comando solo para superadmins
@require_superadmin
async def promote_command(update: Update, context: ContextTypes) -> None:
    # Solo accesible para superadministradores
    pass

# Comando que requiere registro
@require_registered
async def newvpn_command(update: Update, context: ContextTypes) -> None:
    # Requiere usuario registrado
    pass
```

## Consideraciones de Seguridad

- **Auto-registro controlado**: Solo para IDs predefinidos en config
- **Validación de permisos**: Verificación en BD antes de ejecutar
- **Auditoría completa**: Registra intentos de acceso y registros automáticos
- **Manejo de errores**: Logging detallado de fallos de verificación
- **Mensajes informativos**: Errores claros para usuarios no autorizados
- **Transacciones seguras**: Commit automático en registros