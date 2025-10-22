# services/payments.py

"""
Servicio de pagos híbrido para uSipipo.

Maneja pagos con Telegram Stars y QvaPay, proporcionando una interfaz unificada
para procesar transacciones de VPN.

Funcionalidades principales:
- Cálculo de precios con descuentos
- Procesamiento de pagos con Telegram Stars
- Procesamiento de pagos con QvaPay
- Validación robusta de transacciones
- Manejo de errores específico por método de pago
"""

from __future__ import annotations
from typing import Optional, List, TypedDict, Literal, Dict, Any
from decimal import Decimal
import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from database.crud import payments as crud_payments
from database.crud import logs as crud_logs
from database import models
from services.market import get_market_snapshot
from services.qvapay_user_client import (
    QvaPayUserClient,
    QvaPayUserError,
    QvaPayUserAuthError,
    QvaPayUserBadRequestError,
    QvaPayUserNotFoundError,
    QvaPayUserServerError
)

logger = logging.getLogger(__name__)

class PriceResult(TypedDict):
    """
    Resultado del cálculo de precios para un plan VPN.

    Attributes:
        months (int): Número de meses del plan.
        usd (float): Precio en USD.
        stars (int): Precio en Telegram Stars.
        source (str): Fuente del precio (market.py, fallback).
        qvapay_balance_needed (Optional[float]): Balance requerido en QvaPay (None para pagos con Stars).
    """
    months: int
    usd: float
    stars: int
    source: str
    qvapay_balance_needed: Optional[float]

async def calculate_price(
    months: int,
    payment_method: Literal["stars", "qvapay"] = "stars",
    stars_amount: int = 100
) -> PriceResult:
    """
    Calcula el precio de un plan VPN en USD y Stars.

    Args:
        months (int): Número de meses del plan.
        payment_method (Literal["stars", "qvapay"]): Método de pago (afecta qvapay_balance_needed).
        stars_amount (int): Cantidad de estrellas para calcular el precio (por defecto 100).

    Returns:
        PriceResult: Diccionario con precios calculados y metadatos.

    Raises:
        ValueError: Si months es inválido.
    """
    if months < 1:
        raise ValueError("El número de meses debe ser mayor que 0")

    if payment_method not in ("stars", "qvapay"):
        raise ValueError(f"Método de pago no soportado: {payment_method}")
    base_price = Decimal("1.00")
    usd = base_price * months

    # Descuentos
    if months == 3:
        usd *= Decimal("0.95")
    elif months == 6:
        usd *= Decimal("0.85")
    elif months == 12:
        usd *= Decimal("0.75")

    usd = usd.quantize(Decimal("0.01"))

    try:
        market = get_market_snapshot(stars_amount)
        stars_usd = Decimal(str(market["stars_usd"])) / Decimal(str(market["stars_amount"]))

        stars = int(round(usd / stars_usd))

        result: PriceResult = {
            "months": months,
            "usd": float(usd),
            "stars": stars,
            "source": market.get("source", "market.py"),
            "qvapay_balance_needed": float(usd) if payment_method == "qvapay" else None,
        }
        logger.info(f"Precio calculado: {result}", extra={"user_id": None})
        return result
    except Exception as e:
        logger.warning(f"Error obteniendo precios del mercado: {e}. Usando fallback.", extra={"user_id": None})

        # Fallback: precio fijo basado en USD
        stars = int(round(float(usd) * 10))
        result: PriceResult = {
            "months": months,
            "usd": float(usd),
            "stars": stars,
            "source": "fallback",
            "qvapay_balance_needed": float(usd) if payment_method == "qvapay" else None,
        }
        logger.info(f"Precio calculado (fallback): {result}", extra={"user_id": None})
        return result

async def create_vpn_payment(
    session: AsyncSession,
    user_id: str,
    vpn_type: Literal["wireguard", "outline"],
    months: int,
) -> Optional[models.Payment]:
    """
    Crea un pago pendiente para VPN con precios calculados.

    Args:
        session (AsyncSession): Sesión de base de datos.
        user_id (str): ID del usuario.
        vpn_type (Literal["wireguard", "outline"]): Tipo de VPN.
        months (int): Número de meses del plan.

    Returns:
        Optional[models.Payment]: El pago creado o None si falla.

    Note:
        El commit de la transacción debe manejarse en el handler que llama a esta función.
    """
    if vpn_type not in ("wireguard", "outline"):
        logger.error(f"Tipo VPN no soportado: {vpn_type}", extra={"user_id": user_id})
        raise ValueError(f"Tipo VPN no soportado: {vpn_type}")

    try:
        price = await calculate_price(months, "stars")
        # Generar un ID único para el pago
        import uuid
        payment_id = str(uuid.uuid4())
        
        payment = await crud_payments.create_payment(
            session,
            payment_id=payment_id,
            user_id=user_id,
            vpn_type=vpn_type,
            months=months,
            amount_usd=price["usd"],
            amount_stars=price["stars"],
            commit=False,
        )
        logger.info(
            f"Pago creado: PaymentID {payment_id} para user {user_id}, {vpn_type}, {months} meses",
            extra={"user_id": user_id, "payment_id": payment_id},
        )
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="payment_created",
            payload={"payment_id": payment_id, "vpn_type": vpn_type, "months": months, "amount_stars": price["stars"]},
            commit=False,
        )
        return payment
    except (SQLAlchemyError, ValueError) as e:
        logger.exception(f"Error creando pago para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="payment_creation_error",
            payload={"vpn_type": vpn_type, "months": months, "error": str(e)},
            commit=False,
        )
        raise

async def mark_as_paid(
    session: AsyncSession,
    payment_id: str,
) -> Optional[models.Payment]:
    """
    Marca un pago como pagado y registra el evento.

    Args:
        session (AsyncSession): Sesión de base de datos.
        payment_id (str): ID del pago a marcar como pagado.

    Returns:
        Optional[models.Payment]: El pago actualizado o None si no se encuentra.

    Note:
        El commit de la transacción debe manejarse en el handler que llama a esta función.
    """
    try:
        payment = await crud_payments.update_payment_status(session, payment_id, "paid", commit=False)
        if payment:
            logger.info(f"Pago {payment_id} marcado como paid", extra={"user_id": None, "payment_id": payment_id})
            await crud_logs.create_audit_log(
                session=session,
                user_id=None,
                action="payment_marked_paid",
                payload={"payment_id": payment_id, "status": "paid"},
                commit=False,
            )
        else:
            logger.error(f"Pago {payment_id} no encontrado", extra={"user_id": None, "payment_id": payment_id})
            await crud_logs.create_audit_log(
                session=session,
                user_id=None,
                action="payment_mark_failed",
                payload={"payment_id": payment_id, "reason": "payment_not_found"},
                commit=False,
            )
        return payment
    except SQLAlchemyError as e:
        logger.exception(f"Error marcando pago {payment_id} como paid: {e}", extra={"user_id": None, "payment_id": payment_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=None,
            action="payment_mark_error",
            payload={"payment_id": payment_id, "error": str(e)},
            commit=False,
        )
        raise

async def get_user_payments(session: AsyncSession, user_id: str) -> List[models.Payment]:
    """
    Obtiene todos los pagos de un usuario.

    Args:
        session (AsyncSession): Sesión de base de datos.
        user_id (str): ID del usuario.

    Returns:
        List[models.Payment]: Lista de pagos del usuario.
    """
    try:
        payments = await crud_payments.get_user_payments(session, user_id)
        logger.info(f"Obtenidos {len(payments)} pagos para user {user_id}", extra={"user_id": user_id})
        return payments
    except SQLAlchemyError as e:
        logger.exception(f"Error obteniendo pagos de user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="get_payments_error",
            payload={"user_id": user_id, "error": str(e)},
            commit=False,
        )
        raise

async def get_user_qvapay_balance(app_id: str, user_id: str) -> Dict[str, Any]:
    """
    Obtiene el balance del usuario en QvaPay.

    Args:
        app_id (str): ID de la aplicación QvaPay.
        user_id (str): ID del usuario en QvaPay.

    Returns:
        Dict[str, Any]: Información del balance del usuario, incluyendo balances por moneda.

    Raises:
        ValueError: Si las credenciales son inválidas o hay errores específicos.
        QvaPayUserError: Para errores generales de la API.
    """
    try:
        client = QvaPayUserClient()
        balance = await client.async_get_user_balance(app_id, user_id)
        logger.info(f"Balance QvaPay obtenido para user {user_id}: {balance}", extra={"user_id": user_id})
        return balance
    except QvaPayUserAuthError as e:
        logger.error(f"Error de autenticación QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        raise ValueError("Credenciales QvaPay inválidas. Verifica tu configuración.")
    except QvaPayUserBadRequestError as e:
        logger.error(f"Error de solicitud QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        raise ValueError("Error en la solicitud a QvaPay. Verifica los parámetros.")
    except QvaPayUserNotFoundError as e:
        logger.error(f"Recurso no encontrado en QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        raise ValueError("Recurso no encontrado en QvaPay.")
    except QvaPayUserServerError as e:
        logger.error(f"Error del servidor QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        raise ValueError("Error temporal en QvaPay. Intenta más tarde.")
    except QvaPayUserError as e:
        logger.exception(f"Error obteniendo balance QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        raise ValueError("Error en QvaPay. Intenta más tarde.")

async def process_qvapay_payment(
    app_id: str,
    user_id: str,
    amount: float,
    currency: Literal["USD", "BTC", "LTC", "DASH"] = "USD"
) -> Dict[str, Any]:
    """
    Procesa un pago desde el balance del usuario en QvaPay.

    Args:
        app_id (str): ID de la aplicación QvaPay.
        user_id (str): ID del usuario en QvaPay.
        amount (float): Monto a procesar.
        currency (str): Moneda del pago (USD, BTC, LTC, DASH).

    Returns:
        Dict[str, Any]: Detalles del pago procesado.

    Raises:
        ValueError: Si las credenciales son inválidas o hay errores específicos.
        QvaPayUserError: Para errores generales de la API.
    """
    try:
        client = QvaPayUserClient()
        payment = await client.async_process_payment(app_id, user_id, amount, currency)
        logger.info(
            f"Pago QvaPay procesado: user {user_id}, app {app_id}, amount {amount} {currency}",
            extra={"user_id": user_id, "app_id": app_id, "amount": amount, "currency": currency}
        )
        return payment
    except QvaPayUserAuthError as e:
        logger.error(f"Error de autenticación QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        raise ValueError("Credenciales QvaPay inválidas. Verifica tu configuración.")
    except QvaPayUserBadRequestError as e:
        logger.error(f"Error de solicitud QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        raise ValueError("Error en la solicitud a QvaPay. Verifica los parámetros.")
    except QvaPayUserNotFoundError as e:
        logger.error(f"Recurso no encontrado en QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        raise ValueError("Recurso no encontrado en QvaPay.")
    except QvaPayUserServerError as e:
        logger.error(f"Error del servidor QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        raise ValueError("Error temporal en QvaPay. Intenta más tarde.")
    except QvaPayUserError as e:
        logger.exception(f"Error procesando pago QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        raise ValueError("Error en QvaPay. Intenta más tarde.")

async def validate_qvapay_payment(payment_result: Dict[str, Any]) -> bool:
    """
    Valida que el pago se procesó correctamente en QvaPay.

    Args:
        payment_result (Dict[str, Any]): Resultado del pago procesado por QvaPay.

    Returns:
        bool: True si el pago es válido, False en caso contrario.
    """
    # Verificar que el resultado contiene los campos necesarios
    if not isinstance(payment_result, dict):
        logger.error("Resultado de pago QvaPay inválido: no es un diccionario", extra={"payment_result": payment_result})
        return False

    # Verificar que el pago fue exitoso
    if payment_result.get("success") is not True:
        logger.error("Pago QvaPay no fue exitoso", extra={"payment_result": payment_result})
        return False

    # Verificar que se proporcionó un ID de transacción
    if not payment_result.get("transaction_id"):
        logger.error("Pago QvaPay no contiene ID de transacción", extra={"payment_result": payment_result})
        return False

    logger.info("Pago QvaPay validado correctamente", extra={"transaction_id": payment_result.get("transaction_id")})
    return True

async def create_qvapay_vpn_payment(
    session: AsyncSession,
    user_id: str,
    vpn_type: Literal["wireguard", "outline"],
    months: int,
    app_id: str,
) -> Optional[models.Payment]:
    """
    Crea un pago con QvaPay y activa la VPN.

    Args:
        session (AsyncSession): Sesión de base de datos.
        user_id (str): ID del usuario.
        vpn_type (Literal["wireguard", "outline"]): Tipo de VPN.
        months (int): Número de meses.
        app_id (str): ID de la aplicación QvaPay.

    Returns:
        Optional[models.Payment]: El pago creado o None si falla.
    """
    if vpn_type not in ("wireguard", "outline"):
        logger.error(f"Tipo VPN no soportado: {vpn_type}", extra={"user_id": user_id})
        raise ValueError(f"Tipo VPN no soportado: {vpn_type}")

    try:
        # Calcular precio
        price = await calculate_price(months, "qvapay")
        
        # Verificar balance del usuario
        balance_info = await get_user_qvapay_balance(app_id, user_id)
        user_balance = balance_info.get("balance", {}).get("USD", 0)

        if price["qvapay_balance_needed"] and user_balance < price["qvapay_balance_needed"]:
            logger.error(
                f"Balance insuficiente para user {user_id}: necesita {price['qvapay_balance_needed']}, tiene {user_balance}",
                extra={"user_id": user_id, "needed": price['qvapay_balance_needed'], "available": user_balance}
            )
            raise ValueError("Balance QvaPay insuficiente")
        
        # Procesar pago
        if not price["qvapay_balance_needed"]:
            raise ValueError("Monto requerido para pago QvaPay no disponible")

        payment_result = await process_qvapay_payment(
            app_id, user_id, price["qvapay_balance_needed"], "USD"
        )
        
        # Validar pago
        if not await validate_qvapay_payment(payment_result):
            logger.error(f"Pago QvaPay inválido para user {user_id}", extra={"user_id": user_id, "payment_result": payment_result})
            raise ValueError("Pago QvaPay inválido")
        
        # Generar un ID único para el pago
        import uuid
        payment_id = str(uuid.uuid4())
        
        # Crear registro de pago
        payment = await crud_payments.create_payment(
            session,
            payment_id=payment_id,
            user_id=user_id,
            vpn_type=vpn_type,
            months=months,
            amount_usd=price["usd"],
            amount_stars=0,  # No se usan estrellas en este caso
            commit=False,
        )
        
        logger.info(
            f"Pago QvaPay creado: PaymentID {payment_id} para user {user_id}, {vpn_type}, {months} meses",
            extra={"user_id": user_id, "payment_id": payment_id}
        )
        
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="qvapay_payment_created",
            payload={
                "payment_id": payment_id,
                "vpn_type": vpn_type,
                "months": months,
                "amount_usd": price["usd"],
                "qvapay_transaction_id": payment_result.get("transaction_id")
            },
            commit=False,
        )
        
        return payment
    except QvaPayUserAuthError as e:
        logger.error(f"Error de autenticación QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="qvapay_payment_auth_error",
            payload={
                "vpn_type": vpn_type,
                "months": months,
                "error": str(e)
            },
            commit=False,
        )
        raise ValueError("Credenciales QvaPay inválidas. Verifica tu configuración.")
    except QvaPayUserBadRequestError as e:
        logger.error(f"Error de solicitud QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="qvapay_payment_bad_request_error",
            payload={
                "vpn_type": vpn_type,
                "months": months,
                "error": str(e)
            },
            commit=False,
        )
        raise ValueError("Error en la solicitud a QvaPay. Verifica los parámetros.")
    except QvaPayUserNotFoundError as e:
        logger.error(f"Recurso no encontrado en QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="qvapay_payment_not_found_error",
            payload={
                "vpn_type": vpn_type,
                "months": months,
                "error": str(e)
            },
            commit=False,
        )
        raise ValueError("Recurso no encontrado en QvaPay.")
    except QvaPayUserServerError as e:
        logger.error(f"Error del servidor QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="qvapay_payment_server_error",
            payload={
                "vpn_type": vpn_type,
                "months": months,
                "error": str(e)
            },
            commit=False,
        )
        raise ValueError("Error temporal en QvaPay. Intenta más tarde.")
    except QvaPayUserError as e:
        logger.error(f"Error general QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="qvapay_payment_general_error",
            payload={
                "vpn_type": vpn_type,
                "months": months,
                "error": str(e)
            },
            commit=False,
        )
        raise ValueError("Error en QvaPay. Intenta más tarde.")
    except (SQLAlchemyError, ValueError) as e:
        logger.exception(f"Error creando pago QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="qvapay_payment_creation_error",
            payload={
                "vpn_type": vpn_type,
                "months": months,
                "error": str(e)
            },
            commit=False,
        )
        raise

async def process_payment(
    session: AsyncSession,
    user_id: str,
    vpn_type: Literal["wireguard", "outline"],
    months: int,
    payment_method: Literal["stars", "qvapay"],
    app_id: Optional[str] = None,
) -> Optional[models.Payment]:
    """
    Procesa un pago según el método seleccionado.

    Args:
        session (AsyncSession): Sesión de base de datos.
        user_id (str): ID del usuario.
        vpn_type (Literal["wireguard", "outline"]): Tipo de VPN.
        months (int): Número de meses.
        payment_method (Literal["stars", "qvapay"]): Método de pago.
        app_id (Optional[str]): ID de la aplicación QvaPay (requerido para pagos QvaPay).

    Returns:
        Optional[models.Payment]: El pago procesado o None si falla.
    """
    try:
        if payment_method == "qvapay":
            if not app_id:
                logger.error("APP ID requerido para pagos QvaPay", extra={"user_id": user_id})
                raise ValueError("APP ID requerido para pagos QvaPay")

            payment = await create_qvapay_vpn_payment(session, user_id, vpn_type, months, app_id)
            if payment:
                payment.payment_method = "qvapay"
                await session.commit()
            return payment

        elif payment_method == "stars":
            payment = await create_vpn_payment(session, user_id, vpn_type, months)
            if payment:
                payment.payment_method = "stars"
                await session.commit()
            return payment

        else:
            logger.error(f"Método de pago no soportado: {payment_method}", extra={"user_id": user_id})
            raise ValueError(f"Método de pago no soportado: {payment_method}")

    except QvaPayUserAuthError as e:
        logger.error(f"Error de autenticación QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="qvapay_payment_auth_error",
            payload={
                "vpn_type": vpn_type,
                "months": months,
                "payment_method": payment_method,
                "error": str(e)
            },
            commit=False,
        )
        raise ValueError("Credenciales QvaPay inválidas. Verifica tu configuración.")
    except QvaPayUserBadRequestError as e:
        logger.error(f"Error de solicitud QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="qvapay_payment_bad_request_error",
            payload={
                "vpn_type": vpn_type,
                "months": months,
                "payment_method": payment_method,
                "error": str(e)
            },
            commit=False,
        )
        raise ValueError("Error en la solicitud a QvaPay. Verifica los parámetros.")
    except QvaPayUserNotFoundError as e:
        logger.error(f"Recurso no encontrado en QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="qvapay_payment_not_found_error",
            payload={
                "vpn_type": vpn_type,
                "months": months,
                "payment_method": payment_method,
                "error": str(e)
            },
            commit=False,
        )
        raise ValueError("Recurso no encontrado en QvaPay.")
    except QvaPayUserServerError as e:
        logger.error(f"Error del servidor QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="qvapay_payment_server_error",
            payload={
                "vpn_type": vpn_type,
                "months": months,
                "payment_method": payment_method,
                "error": str(e)
            },
            commit=False,
        )
        raise ValueError("Error temporal en QvaPay. Intenta más tarde.")
    except QvaPayUserError as e:
        logger.error(f"Error general QvaPay para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="qvapay_payment_general_error",
            payload={
                "vpn_type": vpn_type,
                "months": months,
                "payment_method": payment_method,
                "error": str(e)
            },
            commit=False,
        )
        raise ValueError("Error en QvaPay. Intenta más tarde.")
    except (SQLAlchemyError, ValueError) as e:
        logger.exception(f"Error procesando pago para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="payment_processing_error",
            payload={
                "vpn_type": vpn_type,
                "months": months,
                "payment_method": payment_method,
                "error": str(e)
            },
            commit=False,
        )
        raise