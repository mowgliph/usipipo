# Servicio de Pagos con Stars (`services/stars_payments.py`)

## Descripción del Propósito

Maneja pagos con Telegram Stars. Crea invoices, verifica pagos y maneja webhooks para transacciones con estrellas de Telegram.

## Funciones Principales

### `process_star_payment(session: AsyncSession, payment: models.Payment, telegram_user_id: int, bot) -> Tuple[str, str]`
Procesa pago creando invoice de Telegram.
- **Parámetros**: `session`, `payment`, `telegram_user_id`, `bot`
- **Retorno**: (invoice_id, payment_url)
- **Validación**: Monto de estrellas > 0

### `_create_stars_invoice(payment: models.Payment, telegram_user_id: int, bot) -> Tuple[str, str]`
Crea invoice usando Telegram Payments API.
- **Detalles**: Título, descripción, precios en XTR (Stars)
- **Retorno**: invoice_id y URL de pago

### `verify_payment(session: AsyncSession, payment: models.Payment, invoice_id: str) -> Optional[str]`
Verifica estado del pago (placeholder para implementación real).
- **Retorno**: "paid", "failed" o "pending"

### `refund_stars(session: AsyncSession, payment: models.Payment, reason: str = "Refund requested") -> bool`
Procesa reembolso de estrellas (lógica placeholder).
- **Nota**: Telegram Stars no soporta reembolsos directos

### `get_payment_history(session: AsyncSession, user_id: str) -> list[Dict[str, Any]]`
Obtiene historial de pagos con estrellas del usuario.

### `handle_stars_webhook(session: AsyncSession, webhook_data: Dict[str, Any]) -> Optional[models.Payment]`
Maneja webhooks de pagos con estrellas.

## Dependencias y Relaciones

- **Dependencias**:
  - `telegram.LabeledPrice`: Para precios en invoices
  - `database.crud.payments`: Operaciones de pagos
  - `database.crud.logs`: Auditoría

- **Relaciones**:
  - Integrado con `services.payments` para interfaz unificada
  - Usa BOT_TOKEN de entorno para autenticación
  - Registra todas las operaciones en audit logs

## Ejemplos de Uso

```python
# Procesar pago con stars
invoice_id, payment_url = await process_star_payment(session, payment_obj, 123456789, bot)

# Verificar pago
status = await verify_payment(session, payment_obj, invoice_id)
# Retorna: "paid" | "failed" | "pending"

# Obtener historial
history = await get_payment_history(session, "user-123")
```

## Consideraciones de Seguridad

- **Validación de montos**: Verifica cantidades positivas
- **Auditoría completa**: Registra creación, verificación y errores
- **Manejo de webhooks**: Valida datos de entrada
- **Control de estado**: Evita procesamiento duplicado
- **Logging detallado**: Registra user_id en todas las operaciones