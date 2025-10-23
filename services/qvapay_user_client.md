# Cliente QvaPay (`services/qvapay_user_client.py`)

## Descripción del Propósito

Cliente Python para la API user-based de QvaPay. Maneja autenticación, consultas de balance, procesamiento de pagos y manejo robusto de errores específicos de la plataforma.

## Funciones Principales

### `__init__(app_id: Optional[str] = None, api_key: Optional[str] = None)`
Inicializa cliente con credenciales.
- **Parámetros**: `app_id`, `api_key` (de env si no proporcionados)
- **Validación**: APP_ID y API_KEY requeridos
- **Sesión**: Configura headers de autenticación

### `_handle_response(response: requests.Response) -> Dict[str, Any]`
Maneja respuestas HTTP con excepciones específicas.
- **Excepciones**:
  - `QvaPayUserAuthError`: 401 (credenciales inválidas)
  - `QvaPayUserBadRequestError`: 400 (parámetros inválidos)
  - `QvaPayUserNotFoundError`: 404 (recurso no encontrado)
  - `QvaPayUserServerError`: 5xx (errores del servidor)
  - `QvaPayUserError`: Otros errores

### `get_user_balance(app_id: str, user_id: str) -> Dict[str, Any]`
Obtiene balance del usuario en QvaPay.
- **Parámetros**: `app_id`, `user_id`
- **Retorno**: Dict con balances por moneda

### `process_payment(app_id: str, user_id: str, amount: float, currency: str = "USD") -> Dict[str, Any]`
Procesa pago desde balance del usuario.
- **Parámetros**: `app_id`, `user_id`, `amount`, `currency`
- **Monedas soportadas**: USD, BTC, LTC, DASH
- **Validaciones**: Monto > 0, moneda válida

### `async_get_user_balance()` / `async_process_payment()`
Versiones asíncronas usando `asyncio.run_in_executor`.

## Dependencias y Relaciones

- **Dependencias**:
  - `requests`: Cliente HTTP síncrono
  - `asyncio`: Para versiones asíncronas
  - `decimal`: Manejo preciso de montos

- **Relaciones**:
  - Usado por `services.payments` para pagos QvaPay
  - Variables de entorno: QVAPAY_APP_ID, QVAPAY_API_KEY
  - Excepciones específicas integradas con manejo de errores

## Ejemplos de Uso

```python
# Inicializar cliente
client = QvaPayUserClient()

# Obtener balance
balance = client.get_user_balance("app-123", "user-456")
# Retorna: {"balance": {"USD": 50.0, "BTC": 0.001}}

# Procesar pago
payment = client.process_payment("app-123", "user-456", 10.0, "USD")
# Retorna: {"success": True, "transaction_id": "tx-789"}

# Versión asíncrona
balance = await client.async_get_user_balance("app-123", "user-456")
```

## Consideraciones de Seguridad

- **Autenticación**: Bearer token en headers
- **Validación de entrada**: APP_ID, user_id requeridos
- **Manejo de errores específico**: Excepciones por tipo de error HTTP
- **Timeouts implícitos**: requests con timeouts por defecto
- **Sesión reutilizable**: Mantiene conexión HTTP
- **Logging**: Registra operaciones exitosas