# Servicio de Pagos (`services/payments.py`)

## Descripción del Propósito

Servicio híbrido de pagos que maneja transacciones con Telegram Stars y QvaPay. Proporciona una interfaz unificada para calcular precios, procesar pagos y validar transacciones, con soporte para descuentos por volumen y manejo robusto de errores.

## Funciones Principales

### `calculate_price(months: int, payment_method: Literal["stars", "qvapay"], stars_amount: int = 100) -> PriceResult`
Calcula precios de planes VPN con descuentos.
- **Parámetros**:
  - `months`: Número de meses
  - `payment_method`: Método de pago
  - `stars_amount`: Cantidad de estrellas para conversión
- **Retorno**: TypedDict con precios en USD, Stars y balance QvaPay requerido
- **Descuentos**: 5% (3 meses), 15% (6 meses), 25% (12 meses)

### `create_vpn_payment(session: AsyncSession, user_id: str, vpn_type: str, months: int) -> Optional[models.Payment]`
Crea pago pendiente para VPN con precios calculados.
- **Parámetros**: `session`, `user_id`, `vpn_type`, `months`
- **Retorno**: Objeto Payment creado o None

### `mark_as_paid(session: AsyncSession, payment_id: str) -> Optional[models.Payment]`
Marca pago como completado y registra auditoría.
- **Parámetros**: `session`, `payment_id`
- **Retorno**: Payment actualizado

### `process_payment(session: AsyncSession, user_id: str, vpn_type: str, months: int, payment_method: str, app_id: Optional[str]) -> Optional[models.Payment]`
Procesa pago según método seleccionado (Stars o QvaPay).
- **Parámetros**: `session`, `user_id`, `vpn_type`, `months`, `payment_method`, `app_id`
- **Retorno**: Payment procesado

### Funciones QvaPay específicas:
- `get_user_qvapay_balance()`: Obtiene balance del usuario
- `process_qvapay_payment()`: Procesa pago desde balance
- `validate_qvapay_payment()`: Valida transacción completada
- `create_qvapay_vpn_payment()`: Crea pago con QvaPay y activa VPN

## Dependencias y Relaciones

- **Dependencias**:
  - `services.market`: Obtención de precios del mercado
  - `services.qvapay_user_client`: Cliente API de QvaPay
  - `database.crud.payments`: Operaciones CRUD de pagos
  - `database.crud.logs`: Auditoría de transacciones
  - `decimal`: Cálculos precisos de precios

- **Relaciones**:
  - Integrado con handlers de bot para comandos de pago
  - Usa `market.get_market_snapshot()` para conversiones USD-Stars
  - Registra todas las operaciones en audit logs

## Ejemplos de Uso

```python
# Calcular precio para 6 meses con QvaPay
price = await calculate_price(6, "qvapay")
# Resultado: {"months": 6, "usd": 4.05, "stars": 405, "qvapay_balance_needed": 4.05}

# Procesar pago con QvaPay
payment = await process_payment(session, "user-123", "wireguard", 3, "qvapay", "app-456")

# Crear pago pendiente con Stars
payment = await create_vpn_payment(session, "user-123", "outline", 1)
```

## Consideraciones de Seguridad

- **Validación de entrada**: Verifica métodos de pago y montos
- **Manejo de errores específico**: Diferentes excepciones por tipo de error QvaPay
- **Auditoría completa**: Registra todas las transacciones y errores
- **Validación de pagos**: Verifica integridad de transacciones QvaPay
- **Rate limiting**: Implementado en handlers que llaman este servicio
- **Balance verification**: Verifica fondos suficientes antes de procesar