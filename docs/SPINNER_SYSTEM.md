# Sistema de Spinner para uSipipo Bot

## Overview

El sistema de spinner mejora la experiencia del usuario (UX) durante operaciones asíncronas que pueden tomar tiempo, como conexiones a base de datos, operaciones VPN o procesos de registro.

**Última actualización:** Corregido error de TypeError con Python 3.13 usando verificación de atributos en lugar de `isinstance()`.

## Características

- **Decoradores fáciles de usar**: Solo añade un decorador a tu función
- **Mensajes predefinidos**: Para diferentes tipos de operaciones
- **Animación opcional**: Spinners animados que se actualizan periódicamente
- **Manejo automático de errores**: Elimina el spinner y muestra mensajes de error
- **Tipos específicos**: Spinners especializados para VPN, base de datos, pagos, etc.
- **Compatible con Python 3.13**: Usa verificación robusta de tipos sin `isinstance()` genéricos

## Uso Básico

### 1. Importar los decoradores

```python
from utils.spinner import with_spinner, vpn_spinner, database_spinner
```

### 2. Aplicar a handlers

```python
@database_spinner
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service: VpnService):
    # Tu código existente
    user = await vpn_service.user_repo.get_by_id(user.id)
    # ... resto del código
```

### 3. Spinners específicos

```python
@vpn_spinner
async def create_vpn_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Operación VPN lenta
    new_key = await vpn_service.create_key(telegram_id, key_type, key_name)

@payment_spinner
async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Operación de pago
    result = await payment_service.process_charge(user_id, amount)
```

## Decoradores Disponibles

### `with_spinner(operation_type, custom_message, show_duration)`
Decorador genérico con opciones personalizadas.

**Parámetros:**
- `operation_type`: Tipo de operación predefinida ("loading", "processing", "connecting", etc.)
- `custom_message`: Mensaje personalizado (opcional)
- `show_duration`: Muestra tiempo de ejecución (default: False)

**Ejemplo:**
```python
@with_spinner("creating", "🔨 Creando tu llave VPN...", show_duration=True)
async def create_key():
    # Tu código
```

### `with_animated_spinner(operation_type, custom_message, update_interval)`
Spinner animado que se actualiza periódicamente.

**Parámetros:**
- `operation_type`: Tipo de operación
- `custom_message`: Mensaje personalizado (opcional)
- `update_interval`: Intervalo de actualización en segundos (default: 0.5)

### Spinners Especializados

- `@database_spinner`: Para operaciones de base de datos
- `@vpn_spinner`: Para operaciones VPN
- `@registration_spinner`: Para registro de usuarios
- `@payment_spinner`: Para operaciones de pago

## Mensajes Predefinidos

- `"loading"`: "🔄 Cargando..."
- `"processing"`: "⚙️ Procesando..."
- `"connecting"`: "🔌 Conectando..."
- `"creating"`: "🔨 Creando..."
- `"updating"`: "📝 Actualizando..."
- `"deleting"`: "🗑️ Eliminando..."
- `"searching"`: "🔍 Buscando..."
- `"validating"`: "✅ Validando..."
- `"database"`: "💾 Accediendo a la base de datos..."
- `"vpn"`: "🌐 Configurando VPN..."
- `"payment"`: "💳 Procesando pago..."
- `"register"`: "👤 Registrando usuario..."
- `"default"`: "⏳ Procesando solicitud..."

## Uso Avanzado

### SpinnerManager para control manual

```python
from utils.spinner import SpinnerManager

# Enviar spinner manualmente
spinner_id = await SpinnerManager.send_spinner_message(
    update, 
    operation_type="vpn",
    custom_message="🌐 Conectando al servidor VPN..."
)

# Actualizar spinner
await SpinnerManager.update_spinner_message(
    context, chat_id, spinner_id,
    operation_type="processing"
)

# Eliminar spinner
await SpinnerManager.delete_spinner_message(context, chat_id, spinner_id)
```

## Handlers Actualizados

Los siguientes handlers ya incluyen spinners:

1. **start_handler.py**: `@registration_spinner`
   - Operaciones de registro y verificación de usuarios
   - Conexión a base de datos Supabase

2. **crear_llave_handler.py**: `@vpn_spinner`
   - Creación de llaves VPN (Outline/WireGuard)
   - Generación de QR y archivos de configuración

3. **keys_manager_handler.py**: `@vpn_spinner` en eliminación
   - Revocación de llaves en servidores VPN
   - Eliminación de base de datos

4. **achievement_handler.py**: `@database_spinner`
   - Consultas de logros y estadísticas
   - Operaciones de base de datos de logros

## Beneficios

- **Mejor UX**: Los usuarios ven feedback inmediato
- **Reducción de percepción de lentitud**: La espera parece más corta
- **Profesionalismo**: Muestra que el bot está trabajando
- **Transparencia**: Usuarios saben qué está sucediendo
- **Manejo de errores**: Mensajes claros cuando algo falla

## Consideraciones

- Los spinners se eliminan automáticamente cuando la función termina
- En caso de error, el spinner se elimina y se muestra mensaje de error
- No afecta el flujo normal del programa
- Compatible con todos los handlers existentes

## Ejemplo Completo

```python
from utils.spinner import vpn_spinner
from telegram import Update
from telegram.ext import ContextTypes

@vpn_spinner
async def create_vpn_key_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service: VpnService):
    """Handler con spinner automático para creación de llaves VPN."""
    
    user_id = update.effective_user.id
    key_name = update.message.text
    
    try:
        # El spinner se muestra automáticamente aquí
        new_key = await vpn_service.create_key(user_id, "outline", key_name)
        
        # Cuando termina, el spinner se elimina automáticamente
        await update.message.reply_text(
            f"✅ Llave '{new_key.name}' creada exitosamente"
        )
        
    except Exception as e:
        # Si hay error, el spinner se elimina y se muestra error
        await update.message.reply_text(
            f"❌ Error: {str(e)}"
        )
```

El sistema está listo para producción y mejora significativamente la experiencia del usuario durante operaciones lentas.
