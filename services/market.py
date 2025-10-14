# services/market.py 
import requests

# Cliente de fragment-api-lib (PyPI)
from fragment_api_lib.client import FragmentAPIClient

# Endpoints oficiales para TON
TONAPI_URL = "https://tonapi.io/v2/rates?tokens=ton&currencies=usd"
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd"

# Inicializar cliente
fragment_client_pypi = FragmentAPIClient()


def get_ton_price_usd() -> float:
    """Precio de TON en USD desde TONAPI, con fallback a CoinGecko."""
    try:
        resp = requests.get(TONAPI_URL, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data["rates"]["TON"]["prices"]["USD"]
    except Exception:
        resp = requests.get(COINGECKO_URL, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data["the-open-network"]["usd"]


def get_stars_price(amount: int = 100) -> dict:
    """
    Obtiene precio de Stars en TON y USD usando fragment-api-lib (PyPI).
    Si falla, retorna None.
    """
    try:
        res = fragment_client_pypi.get_stars_price(amount=amount)
        return {
            "amount": res["amount"],
            "ton": res["price_ton"],
            "usd": res["price_usd"],
            "source": "fragment-api-lib"
        }
    except Exception:
        return None


def get_market_snapshot(amount: int = 100) -> dict:
    """Snapshot de mercado con TON/USD y Stars/TON/USD."""
    ton_usd = get_ton_price_usd()
    stars = get_stars_price(amount)

    if stars:
        return {
            "ton_usd": ton_usd,
            "stars_amount": stars["amount"],
            "stars_ton": stars["ton"],
            "stars_usd": stars["usd"],
            "source": stars["source"]
        }
    else:
        # Fallback: cálculo aproximado si fragment-api-lib falla
        fallback_star_to_ton = 0.1
        return {
            "ton_usd": ton_usd,
            "stars_amount": amount,
            "stars_ton": amount * fallback_star_to_ton,
            "stars_usd": round(amount * fallback_star_to_ton * ton_usd, 2),
            "source": "fallback"
        }