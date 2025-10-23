# Handler Start (`bot/handlers/start.py`)

## Descripción del Propósito

Maneja el comando /start del bot, proporcionando bienvenida y navegación inicial para nuevos usuarios.

## Funciones Principales

### `start_command(update: Update, context: ContextTypes) -> None`
Procesa comando de inicio del bot.
- **Comando**: `/start`
- **Funcionalidad**:
  - Mensaje de bienvenida personalizado
  - Teclado inline con comandos frecuentes
  - Registro automático en auditoría
- **Botones inline**:
  - ℹ️ Info
  - 📝 Registrarse
  - 🆕 Nueva VPN
  - 🔒 Proxy MTProto
  - 🆓 Trial WireGuard/Outline

## Dependencias y Relaciones

- **Dependencias**:
  - `services.user`: Consulta de usuario registrado
  - `utils.helpers`: Función de logging y notificación
  - `telegram.InlineKeyboardMarkup`: Creación de teclado

- **Relaciones**:
  - Primer punto de contacto con usuarios
  - Integra con sistema de registro de usuarios
  - Registra interacciones en audit logs

## Ejemplos de Uso

```python
# Usuario ejecuta comando
/start

# Respuesta:
# ¡Hola Juan! 👋 Bienvenido a uSipipo 🚀
# 
# Aquí podrás generar configuraciones de VPN Outline y WireGuard
# de forma sencilla, rápida y segura.
# 
# Usa /help para ver los comandos disponibles.
# 👉 Recuerda registrarte primero con /register.
# 
# [Teclado inline con botones]
```

## Consideraciones de Seguridad

- **Validación de update**: Verifica existencia de chat, message, user
- **Auditoría**: Registra todas las ejecuciones de /start
- **Manejo de errores**: Logging detallado de excepciones
- **Personalización**: Saludo con nombre del usuario
- **Navegación intuitiva**: Botones para acciones comunes