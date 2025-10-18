# services/ton_payments.py

from __future__ import annotations
from typing import Optional, Dict, Any, Tuple
import logging
import os
import json
from decimal import Decimal
import requests
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import payments as crud_payments
from database.crud import logs as crud_logs
from database import models

logger = logging.getLogger(__name__)

# Configuration from environment
TONAPI_URL = "https://tonapi.io/v2"
TONAPI_KEY = os.getenv("TONAPI_KEY")

# Fallback configuration
USE_TONAPI = bool(TONAPI_KEY)

if not USE_TONAPI:
    logger.warning("TONAPI_KEY not configured for TON payments")

class TonPaymentError(Exception):
    """Custom exception for TON payment errors."""
    pass

async def create_ton_invoice(
    session: AsyncSession,
    payment: models.Payment,
    description: str = "VPN Subscription"
) -> Tuple[str, str]:
    """
    Create a TON invoice (payment link).
    Returns (invoice_id, payment_link) tuple.
    Uses TONAPI as primary, ton.py as fallback.
    """
    amount_ton = payment.amount_ton
    if amount_ton <= 0:
        raise TonPaymentError("Invalid amount for TON invoice")

    try:
        if USE_TONAPI:
            return await _create_tonapi_invoice(payment, description)
        else:
            return await _create_tonpy_invoice(payment, description)
    except Exception as e:
        logger.exception(f"Error creating TON invoice for payment {payment.id}: {e}", extra={"user_id": payment.user_id, "payment_id": payment.id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=payment.user_id,
            action="ton_invoice_creation_error",
            payload={"payment_id": payment.id, "error": str(e)},
            commit=False,
        )
        raise TonPaymentError(f"Failed to create TON invoice: {e}")

async def _create_tonapi_invoice(payment: models.Payment, description: str) -> Tuple[str, str]:
    """Create invoice using TONAPI."""
    url = f"{TONAPI_URL}/wallet/send"
    headers = {
        "Authorization": f"Bearer {TONAPI_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "to": "your_wallet_address",  # Replace with actual wallet address
        "amount": str(payment.amount_ton),
        "comment": description,
        "metadata": {
            "payment_id": payment.id,
            "user_id": payment.user_id,
        },
    }

    response = requests.post(url, headers=headers, json=data, timeout=30)
    response.raise_for_status()

    invoice_data = response.json()
    invoice_id = invoice_data.get("id", payment.id)  # Adjust based on actual API response
    payment_link = f"ton://transfer/{invoice_data.get('to')}?amount={payment.amount_ton}&text={description}"

    logger.info(f"TONAPI invoice created: {invoice_id} for payment {payment.id}", extra={"user_id": payment.user_id, "payment_id": payment.id})
    return invoice_id, payment_link

async def _create_tonpy_invoice(payment: models.Payment, description: str) -> Tuple[str, str]:
    """Create invoice using ton.py as fallback."""
    try:
        import ton
        # Implement ton.py logic here
        # This is a placeholder - actual implementation depends on ton.py API
        invoice_id = payment.id
        payment_link = f"ton://transfer/wallet_address?amount={payment.amount_ton}&text={description}"
        logger.info(f"ton.py invoice created: {invoice_id} for payment {payment.id}", extra={"user_id": payment.user_id, "payment_id": payment.id})
        return invoice_id, payment_link
    except ImportError:
        raise TonPaymentError("ton.py library not available")

async def check_payment_status(
    session: AsyncSession,
    payment: models.Payment,
    invoice_id: str
) -> Optional[str]:
    """
    Check the status of a TON payment by querying transactions.
    Returns status string or None if not found.
    """
    try:
        if USE_TONAPI:
            return await _check_tonapi_status(invoice_id)
        else:
            return await _check_tonpy_status(invoice_id)
    except Exception as e:
        logger.exception(f"Error checking TON payment status for invoice {invoice_id}: {e}", extra={"user_id": payment.user_id, "payment_id": payment.id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=payment.user_id,
            action="ton_status_check_error",
            payload={"payment_id": payment.id, "invoice_id": invoice_id, "error": str(e)},
            commit=False,
        )
        return None

async def _check_tonapi_status(invoice_id: str) -> Optional[str]:
    """Check payment status using TONAPI."""
    url = f"{TONAPI_URL}/transactions/{invoice_id}"
    headers = {"Authorization": f"Bearer {TONAPI_KEY}"}

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    tx_data = response.json()
    status = tx_data.get("status")

    # TONAPI status mapping
    if status == "confirmed":
        return "paid"
    elif status == "failed":
        return "failed"
    elif status == "pending":
        return "pending"
    else:
        return "pending"

async def _check_tonpy_status(invoice_id: str) -> Optional[str]:
    """Check payment status using ton.py."""
    try:
        import ton
        # Implement ton.py status check logic
        # Placeholder
        return "pending"
    except ImportError:
        return None

async def handle_confirmation(
    session: AsyncSession,
    webhook_data: Dict[str, Any]
) -> Optional[models.Payment]:
    """
    Handle TON payment confirmations.
    Returns the updated Payment object if payment was successful.
    """
    try:
        return await _handle_tonapi_confirmation(session, webhook_data)
    except Exception as e:
        logger.exception(f"Error handling TON confirmation: {e}")
        return None

async def _handle_tonapi_confirmation(session: AsyncSession, webhook_data: Dict[str, Any]) -> Optional[models.Payment]:
    """Handle TONAPI webhook confirmation."""
    tx_hash = webhook_data.get("hash")
    status = webhook_data.get("status")

    if not tx_hash or status != "confirmed":
        return None

    # Extract payment_id from webhook data or transaction comment
    payment_id = webhook_data.get("payment_id")  # Adjust based on actual webhook structure

    if not payment_id:
        logger.error("TON confirmation missing payment_id")
        return None

    payment = await crud_payments.get_payment(session, payment_id)
    if not payment:
        logger.error(f"Payment {payment_id} not found for TON confirmation")
        return None

    if payment.status == "paid":
        return payment  # Already processed

    # Mark as paid
    updated_payment = await crud_payments.update_payment_status(session, payment_id, "paid", commit=False)

    await crud_logs.create_audit_log(
        session=session,
        user_id=payment.user_id,
        action="ton_payment_received",
        payload={
            "payment_id": payment_id,
            "tx_hash": tx_hash,
            "amount_ton": payment.amount_ton,
        },
        commit=False,
    )

    logger.info(f"TON payment received for payment {payment_id}", extra={"user_id": payment.user_id, "payment_id": payment_id})
    return updated_payment