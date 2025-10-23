# Servicio de Mercado (`services/market.py`)

## Descripción del Propósito

Proporciona datos de precios de criptomonedas para cálculos de conversiones. Obtiene precios de TON, BTC y Stars desde múltiples APIs con fallbacks automáticos.

## Funciones Principales

### `get_ton_price_usd() -> float`
Obtiene precio de TON en USD.
- **APIs**: TONAPI.io → CoinGecko (fallback)
- **Retorno**: Precio USD de 1 TON

### `get_btc_price_usd() -> float`
Obtiene precio de BTC en USD desde CoinGecko.

### `get_stars_price(amount: int = 100) -> dict | None`
Obtiene precio de Telegram Stars usando fragment-api-lib.
- **Parámetros**: `amount` (cantidad de stars)
- **Retorno**: Dict con amount, ton, usd, source o None si falla

### `get_market_snapshot(amount: int = 100) -> dict`
Snapshot completo de mercado con TON/USD, BTC/USD y Stars.
- **Fallback**: Si fragment-api-lib falla, usa cálculo aproximado
- **Retorno**: Dict con precios y fuente

## Dependencias y Relaciones

- **Dependencias**:
  - `requests`: Cliente HTTP para APIs
  - `fragment_api_lib`: Cliente específico para Stars

- **Relaciones**:
  - Usado por `services.payments` para calcular precios
  - Proporciona datos para conversiones USD ↔ Stars
  - Integrado con lógica de descuentos por volumen

## Ejemplos de Uso

```python
# Obtener precios actuales
snapshot = get_market_snapshot(100)
# Retorna: {
#     "ton_usd": 5.67,
#     "btc_usd": 45000.0,
#     "stars_amount": 100,
#     "stars_ton": 0.1,
#     "stars_usd": 0.567,
#     "source": "fragment-api-lib"
# }

# Precio directo de TON
ton_price = get_ton_price_usd()
```

## Consideraciones de Seguridad

- **Timeouts**: 5 segundos por petición
- **Fallbacks**: Múltiples fuentes para evitar fallos
- **Validación**: Manejo de respuestas HTTP
- **Rate limiting**: Implícito por timeouts