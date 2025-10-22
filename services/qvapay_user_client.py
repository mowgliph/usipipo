# services/qvapay_user_client.py

import os
import logging
from typing import Dict, List, Optional, Any, Literal
from decimal import Decimal
import requests
import asyncio

logger = logging.getLogger(__name__)

class QvaPayUserError(Exception):
    """Excepción base para errores de QvaPay User API."""
    pass

class QvaPayUserAuthError(QvaPayUserError):
    """Excepción para errores de autenticación."""
    pass

class QvaPayUserBadRequestError(QvaPayUserError):
    """Excepción para solicitudes incorrectas (400)."""
    pass

class QvaPayUserNotFoundError(QvaPayUserError):
    """Excepción para recursos no encontrados (404)."""
    pass

class QvaPayUserServerError(QvaPayUserError):
    """Excepción para errores del servidor (5xx)."""
    pass

class QvaPayUserClient:
    """Cliente para interactuar con la API de QvaPay user-based."""

    BASE_URL = "https://qvapay.com/api/v1"

    SUPPORTED_CURRENCIES = ["USD", "BTC", "LTC", "DASH"]

    def __init__(self, app_id: Optional[str] = None, api_key: Optional[str] = None):
        """
        Inicializa el cliente QvaPay user-based.

        Args:
            app_id (Optional[str]): ID de la aplicación QvaPay. Si no se proporciona,
                                    se obtiene de la variable de entorno QVAPAY_APP_ID.
            api_key (Optional[str]): Clave API de QvaPay. Si no se proporciona,
                                    se obtiene de la variable de entorno QVAPAY_API_KEY.

        Raises:
            ValueError: Si no se proporcionan app_id o api_key.
        """
        self.app_id = app_id or os.getenv("QVAPAY_APP_ID")
        if not self.app_id:
            raise ValueError("Se requiere un APP_ID de QvaPay. Proporciónalo o configura la variable de entorno QVAPAY_APP_ID.")

        self.api_key = api_key or os.getenv("QVAPAY_API_KEY")
        if not self.api_key:
            raise ValueError("Se requiere una API key de QvaPay. Proporciónala o configura la variable de entorno QVAPAY_API_KEY.")

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Maneja la respuesta de la API y lanza excepciones apropiadas.

        Args:
            response (requests.Response): La respuesta de la solicitud.

        Returns:
            Dict[str, Any]: Los datos JSON de la respuesta.

        Raises:
            QvaPayUserAuthError: Para errores de autenticación (401).
            QvaPayUserBadRequestError: Para solicitudes incorrectas (400).
            QvaPayUserNotFoundError: Para recursos no encontrados (404).
            QvaPayUserServerError: Para errores del servidor (5xx).
            QvaPayUserError: Para otros errores.
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise QvaPayUserAuthError("Error de autenticación: Verifica tu APP_ID y API key.") from e
            elif response.status_code == 400:
                raise QvaPayUserBadRequestError(f"Solicitud incorrecta: {response.text}") from e
            elif response.status_code == 404:
                raise QvaPayUserNotFoundError("Recurso no encontrado.") from e
            elif response.status_code >= 500:
                raise QvaPayUserServerError(f"Error del servidor: {response.text}") from e
            else:
                raise QvaPayUserError(f"Error HTTP {response.status_code}: {response.text}") from e
        except requests.exceptions.RequestException as e:
            raise QvaPayUserError(f"Error de conexión: {str(e)}") from e

    def get_user_balance(self, app_id: str, user_id: str) -> Dict[str, Any]:
        """
        Obtiene el balance del usuario en QvaPay.

        Args:
            app_id (str): ID de la aplicación.
            user_id (str): ID del usuario.

        Returns:
            Dict[str, Any]: Información del balance del usuario, incluyendo balances por moneda.

        Raises:
            QvaPayUserAuthError: Si las credenciales son inválidas.
            QvaPayUserBadRequestError: Si los parámetros son inválidos.
            QvaPayUserServerError: Si hay un error del servidor.
            QvaPayUserError: Para otros errores de la API.
        """
        if not app_id or not user_id:
            raise ValueError("app_id y user_id son requeridos.")

        url = f"{self.BASE_URL}/user/balance"
        data = {
            "app_id": app_id,
            "user_id": user_id
        }
        response = self.session.post(url, json=data)
        result = self._handle_response(response)

        logger.info(f"Balance obtenido para user {user_id} en app {app_id}: {result}", extra={"user_id": user_id, "app_id": app_id})
        return result

    def process_payment(
        self,
        app_id: str,
        user_id: str,
        amount: float,
        currency: Literal["USD", "BTC", "LTC", "DASH"] = "USD"
    ) -> Dict[str, Any]:
        """
        Procesa un pago desde el balance del usuario.

        Args:
            app_id (str): ID de la aplicación.
            user_id (str): ID del usuario.
            amount (float): Monto a procesar.
            currency (str): Moneda del pago (USD, BTC, LTC, DASH).

        Returns:
            Dict[str, Any]: Detalles del pago procesado.

        Raises:
            QvaPayUserAuthError: Si las credenciales son inválidas.
            QvaPayUserBadRequestError: Si los parámetros son inválidos o no hay suficiente balance.
            QvaPayUserServerError: Si hay un error del servidor.
            QvaPayUserError: Para otros errores de la API.
        """
        if not app_id or not user_id:
            raise ValueError("app_id y user_id son requeridos.")

        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Moneda no soportada: {currency}. Monedas soportadas: {self.SUPPORTED_CURRENCIES}")

        if amount <= 0:
            raise ValueError("El monto debe ser mayor que cero.")

        url = f"{self.BASE_URL}/user/pay"
        data = {
            "app_id": app_id,
            "user_id": user_id,
            "amount": amount,
            "currency": currency
        }
        response = self.session.post(url, json=data)
        result = self._handle_response(response)

        logger.info(
            f"Pago procesado: user {user_id}, app {app_id}, amount {amount} {currency}",
            extra={"user_id": user_id, "app_id": app_id, "amount": amount, "currency": currency}
        )
        return result

    def get_supported_currencies(self) -> List[str]:
        """
        Retorna la lista de monedas soportadas.

        Returns:
            List[str]: Lista de monedas soportadas.
        """
        return self.SUPPORTED_CURRENCIES.copy()

    async def async_get_user_balance(self, app_id: str, user_id: str) -> Dict[str, Any]:
        """
        Versión asíncrona de get_user_balance.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_user_balance, app_id, user_id)

    async def async_process_payment(
        self,
        app_id: str,
        user_id: str,
        amount: float,
        currency: Literal["USD", "BTC", "LTC", "DASH"] = "USD"
    ) -> Dict[str, Any]:
        """
        Versión asíncrona de process_payment.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process_payment, app_id, user_id, amount, currency)