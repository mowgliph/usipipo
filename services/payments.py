# services/payments.py

from __future__ import annotations
from typing import Optional, List, TypedDict, Literal
from decimal import Decimal
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from database.crud import payments as crud_payments
from database.crud import logs as crud_logs
from database import models
from services.market import get_market_snapshot

logger = logging.getLogger(__name__)

class PriceResult(TypedDict):
    months: int
    usd: float
    stars: int
    ton: float
    ton_usd: float
    sats: int
    source: str

async def calculate_price(months: int, stars_amount: int = 100) -> PriceResult:
    """
    Calcula el precio de un plan en USD, Stars y TON.
    Retorna un diccionario con los valores calculados.
    """
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
        ton_usd = Decimal(str(market["ton_usd"]))
        btc_usd = Decimal(str(market["btc_usd"]))

        stars = int(round(usd / stars_usd))
        ton = float((usd / ton_usd).quantize(Decimal("0.01")))
        sats = int(round(usd / btc_usd * 100000000))  # 1 BTC = 100,000,000 sats

        result: PriceResult = {
            "months": months,
            "usd": float(usd),
            "stars": stars,
            "ton": ton,
            "ton_usd": float(ton_usd),
            "sats": sats,
            "source": market.get("source", "market.py"),
        }
        logger.info(f"Precio calculado: {result}", extra={"user_id": None})
        return result
    except Exception as e:
        logger.exception(f"Error obteniendo precios reales: {e}", extra={"user_id": None})
        async with AsyncSession() as session:
            await crud_logs.create_audit_log(
                session=session,
                user_id=None,
                action="calculate_price_error",
                payload={"months": months, "stars_amount": stars_amount, "error": str(e)},
                commit=False,
            )

        # Fallback
        stars = int(round(float(usd) * 10))
        ton = round(float(usd) * 0.5, 2)
        sats = int(round(float(usd) / 50000 * 100000000))  # Approximate BTC price fallback
        result: PriceResult = {
            "months": months,
            "usd": float(usd),
            "stars": stars,
            "ton": ton,
            "ton_usd": 0.5,
            "sats": sats,
            "source": "fallback",
        }
        logger.info(f"Precio fallback: {result}", extra={"user_id": None})
        return result

async def create_vpn_payment(
    session: AsyncSession,
    user_id: str,
    vpn_type: Literal["wireguard", "outline"],
    months: int,
) -> Optional[models.Payment]:
    """
    Crea un pago pendiente con precios calculados.
    Retorna Payment o None si falla.
    Nota: El commit de la transacción debe manejarse en el handler.
    """
    if vpn_type not in ("wireguard", "outline"):
        logger.error(f"Tipo VPN no soportado: {vpn_type}", extra={"user_id": user_id})
        raise ValueError(f"Tipo VPN no soportado: {vpn_type}")

    try:
        price = await calculate_price(months)
        payment = await crud_payments.create_payment(
            session,
            user_id=user_id,
            vpn_type=vpn_type,
            months=months,
            amount_usd=price["usd"],
            amount_stars=price["stars"],
            amount_ton=price["ton"],
            amount_sats=price["sats"],
            commit=False,
        )
        logger.info(
            f"Pago creado: PaymentID {payment.id} para user {user_id}, {vpn_type}, {months} meses",
            extra={"user_id": user_id, "payment_id": payment.id},
        )
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="payment_created",
            payload={"payment_id": payment.id, "vpn_type": vpn_type, "months": months, "amount_stars": price["stars"]},
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
    Marca un pago como pagado.
    Retorna Payment actualizado o None si no se encuentra.
    Nota: El commit de la transacción debe manejarse en el handler.
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
    Lista los pagos de un usuario.
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