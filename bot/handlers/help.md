# Handler Help (`bot/handlers/help.py`)

## Descripción del Propósito

Proporciona ayuda contextual según el rol del usuario, mostrando comandos disponibles de forma personalizada.

## Funciones Principales

### `help_command(update: Update, context: ContextTypes) -> None`
Muestra comandos disponibles según permisos del usuario.
- **Comando**: `/help`
- **Funcionalidad**:
  - Consulta rol del usuario en BD
  - Genera mensaje contextual con `user_service.get_help_message()`
  - Muestra comandos para usuarios normales, admins y superadmins

## Dependencias y Relaciones

- **Dependencias**:
  - `services.user`: Generación contextual de ayuda
  - `database.db`: Sesión para consulta de usuario
  - `utils.helpers`: Manejo de errores

- **Relaciones**:
  - Integra con sistema de roles y permisos
  - Complementa al handler /start
  - Usa servicio de usuarios para lógica de ayuda

## Ejemplos de Uso

```python
# Usuario normal
/help
# Muestra: Usuarios, VPN, Trial

# Administrador
/help  
# Muestra: Comandos admin adicionales (status, logs, promote, etc.)
```

## Consideraciones de Seguridad

- **Acceso universal**: Disponible para todos los usuarios
- **Información contextual**: Solo muestra comandos permitidos
- **Manejo de usuarios no registrados**: Funciona sin registro previo
- **Formato HTML**: Presentación clara y estructurada
- **Logging de errores**: Notificación al equipo en fallos