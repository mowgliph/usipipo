# services/stars_payments.py

from __future__ import annotations
from typing import Optional, Dict, Any, Tuple
import logging
import os
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import payments as crud_payments
from database.crud import logs as crud_logs
from database import models

logger = logging.getLogger(__name__)

# Configuration from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

class StarsPaymentError(Exception):
    """Custom exception for Telegram Stars payment errors."""
    pass

async def process_star_payment(
    session: AsyncSession,
    payment: models.Payment,
    telegram_user_id: int,
    bot
) -> Tuple[str, str]:
    """
    Procesa un pago con estrellas de Telegram.
    Retorna (invoice_id, payment_url) tuple.
    """
    if payment.amount_stars <= 0:
        raise StarsPaymentError("Invalid amount for Stars payment")

    try:
        # Crear invoice usando Telegram Payments API
        invoice_id, payment_url = await _create_stars_invoice(payment, telegram_user_id, bot)

        logger.info(f"Stars payment processed: {invoice_id} for payment {payment.id}", extra={"user_id": payment.user_id, "payment_id": payment.id})
        return invoice_id, payment_url

    except Exception as e:
        logger.exception(f"Error processing Stars payment for payment {payment.id}: {e}", extra={"user_id": payment.user_id, "payment_id": payment.id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=payment.user_id,
            action="stars_payment_creation_error",
            payload={"payment_id": payment.id, "error": str(e)},
            commit=False,
        )
        raise StarsPaymentError(f"Failed to process Stars payment: {e}")

async def _create_stars_invoice(payment: models.Payment, telegram_user_id: int, bot) -> Tuple[str, str]:
    """Crear invoice usando Telegram Stars API."""
    from telegram import LabeledPrice

    # Preparar los precios con estrellas (XTR)
    prices = [LabeledPrice(label=f"VPN {payment.vpn_type.capitalize()} {payment.months} meses", amount=payment.amount_stars)]

    # Crear invoice
    invoice = await bot.create_invoice(
        chat_id=telegram_user_id,
        title=f"VPN Subscription - {payment.vpn_type.capitalize()}",
        description=f"Acceso VPN por {payment.months} meses",
        payload=f"payment_{payment.id}",
        provider_token="",  # Para Telegram Stars, dejar vacío
        currency="XTR",  # Telegram Stars
        prices=prices,
        start_parameter=f"vpn_payment_{payment.id}"
    )

    invoice_id = invoice.invoice.id if hasattr(invoice, 'invoice') else str(payment.id)
    payment_url = f"https://t.me/{bot.username}?start=pay_{payment.id}"

    return invoice_id, payment_url

async def verify_payment(
    session: AsyncSession,
    payment: models.Payment,
    invoice_id: str
) -> Optional[str]:
    """
    Verifica el estado de un pago con estrellas.
    Retorna status string o None si no se encuentra.
    """
    try:
        # En Telegram Stars, la verificación se hace a través de webhooks
        # o consultando el estado del pago
        status = await _check_stars_payment_status(invoice_id)

        if status == "paid":
            # Marcar como pagado
            updated_payment = await crud_payments.update_payment_status(session, payment.id, "paid", commit=False)
            await crud_logs.create_audit_log(
                session=session,
                user_id=payment.user_id,
                action="stars_payment_received",
                payload={
                    "payment_id": payment.id,
                    "invoice_id": invoice_id,
                    "amount_stars": payment.amount_stars,
                },
                commit=False,
            )
            logger.info(f"Stars payment verified and marked as paid: {payment.id}", extra={"user_id": payment.user_id, "payment_id": payment.id})
            return "paid"
        elif status == "failed":
            return "failed"
        else:
            return "pending"

    except Exception as e:
        logger.exception(f"Error verifying Stars payment for invoice {invoice_id}: {e}", extra={"user_id": payment.user_id, "payment_id": payment.id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=payment.user_id,
            action="stars_payment_verification_error",
            payload={"payment_id": payment.id, "invoice_id": invoice_id, "error": str(e)},
            commit=False,
        )
        return None

async def _check_stars_payment_status(invoice_id: str) -> Optional[str]:
    """Verificar estado del pago con Telegram Stars."""
    # En una implementación real, esto se haría consultando la API de Telegram
    # o manejando webhooks. Para simplificar, asumimos que se verifica externamente.
    # En producción, implementar lógica para consultar el estado del invoice
    return "pending"  # Placeholder

async def refund_stars(
    session: AsyncSession,
    payment: models.Payment,
    reason: str = "Refund requested"
) -> bool:
    """
    Reembolsa estrellas si es necesario.
    Retorna True si el reembolso fue exitoso.
    """
    try:
        # Implementar lógica de reembolso con Telegram Stars
        # Nota: Telegram Stars no soporta reembolsos directos como otras criptos
        # Esto podría requerir lógica personalizada

        await crud_logs.create_audit_log(
            session=session,
            user_id=payment.user_id,
            action="stars_refund_attempted",
            payload={
                "payment_id": payment.id,
                "amount_stars": payment.amount_stars,
                "reason": reason,
            },
            commit=False,
        )

        logger.info(f"Stars refund processed for payment {payment.id}", extra={"user_id": payment.user_id, "payment_id": payment.id})
        return True

    except Exception as e:
        logger.exception(f"Error processing Stars refund for payment {payment.id}: {e}", extra={"user_id": payment.user_id, "payment_id": payment.id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=payment.user_id,
            action="stars_refund_error",
            payload={"payment_id": payment.id, "error": str(e)},
            commit=False,
        )
        return False

async def get_payment_history(
    session: AsyncSession,
    user_id: str
) -> list[Dict[str, Any]]:
    """
    Obtiene el historial de pagos con estrellas para un usuario.
    """
    try:
        payments = await crud_payments.get_user_payments(session, user_id)
        stars_payments = [
            {
                "payment_id": p.id,
                "amount_stars": p.amount_stars,
                "status": p.status,
                "created_at": p.created_at.isoformat(),
                "vpn_type": p.vpn_type,
                "months": p.months,
            }
            for p in payments
            if p.payment_method == "stars"
        ]

        logger.info(f"Retrieved {len(stars_payments)} Stars payments for user {user_id}", extra={"user_id": user_id})
        return stars_payments

    except Exception as e:
        logger.exception(f"Error getting Stars payment history for user {user_id}: {e}", extra={"user_id": user_id})
        return []

async def handle_stars_webhook(
    session: AsyncSession,
    webhook_data: Dict[str, Any]
) -> Optional[models.Payment]:
    """
    Maneja webhooks de pagos con estrellas de Telegram.
    Retorna el Payment object si el pago fue exitoso.
    """
    try:
        # Extraer datos del webhook
        payment_id = webhook_data.get("payment_id")
        status = webhook_data.get("status")
        invoice_id = webhook_data.get("invoice_id")

        if not payment_id or status != "paid":
            return None

        # Obtener el pago
        payment = await crud_payments.get_payment(session, payment_id)
        if not payment:
            logger.error(f"Payment {payment_id} not found for Stars webhook")
            return None

        if payment.status == "paid":
            return payment  # Ya procesado

        # Marcar como pagado
        updated_payment = await crud_payments.update_payment_status(session, payment_id, "paid", commit=False)

        await crud_logs.create_audit_log(
            session=session,
            user_id=payment.user_id,
            action="stars_payment_webhook_received",
            payload={
                "payment_id": payment_id,
                "invoice_id": invoice_id,
                "amount_stars": payment.amount_stars,
            },
            commit=False,
        )

        logger.info(f"Stars payment webhook processed for payment {payment_id}", extra={"user_id": payment.user_id, "payment_id": payment_id})
        return updated_payment

    except Exception as e:
        logger.exception(f"Error handling Stars webhook: {e}")
        return None