# services/lightning_payments.py

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
BTCPAY_URL = os.getenv("BTCPAY_URL")
BTCPAY_API_KEY = os.getenv("BTCPAY_API_KEY")
BTCPAY_STORE_ID = os.getenv("BTCPAY_STORE_ID")

OPENNODE_API_KEY = os.getenv("OPENNODE_API_KEY")
OPENNODE_URL = "https://api.opennode.com/v1"

# Fallback configuration
USE_BTCPAY = bool(BTCPAY_URL and BTCPAY_API_KEY and BTCPAY_STORE_ID)
USE_OPENNODE = bool(OPENNODE_API_KEY)

if not USE_BTCPAY and not USE_OPENNODE:
    logger.warning("Neither BTCPay nor OpenNode configured for Lightning payments")

class LightningPaymentError(Exception):
    """Custom exception for Lightning payment errors."""
    pass

async def create_lightning_invoice(
    session: AsyncSession,
    payment: models.Payment,
    description: str = "VPN Subscription"
) -> Tuple[str, str]:
    """
    Create a Lightning invoice for the given payment.
    Returns (invoice_id, payment_request) tuple.
    Tries BTCPay first, falls back to OpenNode.
    """
    amount_sats = payment.amount_sats
    if amount_sats <= 0:
        raise LightningPaymentError("Invalid amount for Lightning invoice")

    try:
        if USE_BTCPAY:
            return await _create_btcpay_invoice(payment, description)
        elif USE_OPENNODE:
            return await _create_opennode_invoice(payment, description)
        else:
            raise LightningPaymentError("No Lightning payment provider configured")
    except Exception as e:
        logger.exception(f"Error creating Lightning invoice for payment {payment.id}: {e}", extra={"user_id": payment.user_id, "payment_id": payment.id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=payment.user_id,
            action="lightning_invoice_creation_error",
            payload={"payment_id": payment.id, "error": str(e)},
            commit=False,
        )
        raise LightningPaymentError(f"Failed to create Lightning invoice: {e}")

async def _create_btcpay_invoice(payment: models.Payment, description: str) -> Tuple[str, str]:
    """Create invoice using BTCPay Server."""
    url = f"{BTCPAY_URL}/api/v1/stores/{BTCPAY_STORE_ID}/invoices"
    headers = {
        "Authorization": f"Bearer {BTCPAY_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "amount": str(payment.amount_usd),
        "currency": "USD",
        "metadata": {
            "payment_id": payment.id,
            "user_id": payment.user_id,
            "description": description,
        },
    }

    response = requests.post(url, headers=headers, json=data, timeout=30)
    response.raise_for_status()

    invoice_data = response.json()
    invoice_id = invoice_data["id"]
    payment_request = invoice_data["checkoutLink"]  # BTCPay returns checkout link

    logger.info(f"BTCPay invoice created: {invoice_id} for payment {payment.id}", extra={"user_id": payment.user_id, "payment_id": payment.id})
    return invoice_id, payment_request

async def _create_opennode_invoice(payment: models.Payment, description: str) -> Tuple[str, str]:
    """Create invoice using OpenNode as fallback."""
    url = f"{OPENNODE_URL}/charges"
    headers = {
        "Authorization": OPENNODE_API_KEY,
        "Content-Type": "application/json",
    }
    data = {
        "amount": str(payment.amount_sats),  # OpenNode expects sats
        "currency": "BTC",
        "description": description,
        "metadata": {
            "payment_id": payment.id,
            "user_id": payment.user_id,
        },
    }

    response = requests.post(url, headers=headers, json=data, timeout=30)
    response.raise_for_status()

    invoice_data = response.json()["data"]
    invoice_id = invoice_data["id"]
    payment_request = invoice_data["lightning_invoice"]["payreq"]

    logger.info(f"OpenNode invoice created: {invoice_id} for payment {payment.id}", extra={"user_id": payment.user_id, "payment_id": payment.id})
    return invoice_id, payment_request

async def check_payment_status(
    session: AsyncSession,
    payment: models.Payment,
    invoice_id: str
) -> Optional[str]:
    """
    Check the status of a Lightning payment.
    Returns status string or None if not found.
    """
    try:
        if USE_BTCPAY:
            return await _check_btcpay_status(invoice_id)
        elif USE_OPENNODE:
            return await _check_opennode_status(invoice_id)
        else:
            raise LightningPaymentError("No Lightning payment provider configured")
    except Exception as e:
        logger.exception(f"Error checking payment status for invoice {invoice_id}: {e}", extra={"user_id": payment.user_id, "payment_id": payment.id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=payment.user_id,
            action="lightning_status_check_error",
            payload={"payment_id": payment.id, "invoice_id": invoice_id, "error": str(e)},
            commit=False,
        )
        return None

async def _check_btcpay_status(invoice_id: str) -> Optional[str]:
    """Check payment status using BTCPay Server."""
    url = f"{BTCPAY_URL}/api/v1/stores/{BTCPAY_STORE_ID}/invoices/{invoice_id}"
    headers = {"Authorization": f"Bearer {BTCPAY_API_KEY}"}

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    invoice_data = response.json()
    status = invoice_data.get("status")

    # BTCPay status mapping
    if status == "Settled":
        return "paid"
    elif status == "Expired":
        return "expired"
    elif status == "Invalid":
        return "failed"
    else:
        return "pending"

async def _check_opennode_status(invoice_id: str) -> Optional[str]:
    """Check payment status using OpenNode."""
    url = f"{OPENNODE_URL}/charge/{invoice_id}"
    headers = {"Authorization": OPENNODE_API_KEY}

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    charge_data = response.json()["data"]
    status = charge_data.get("status")

    # OpenNode status mapping
    if status == "paid":
        return "paid"
    elif status == "expired":
        return "expired"
    elif status == "unpaid":
        return "pending"
    else:
        return "pending"

async def handle_webhook(
    session: AsyncSession,
    webhook_data: Dict[str, Any],
    provider: str = "btcpay"
) -> Optional[models.Payment]:
    """
    Handle webhook notifications from Lightning payment providers.
    Returns the updated Payment object if payment was successful.
    """
    try:
        if provider.lower() == "btcpay":
            return await _handle_btcpay_webhook(session, webhook_data)
        elif provider.lower() == "opennode":
            return await _handle_opennode_webhook(session, webhook_data)
        else:
            logger.error(f"Unknown webhook provider: {provider}")
            return None
    except Exception as e:
        logger.exception(f"Error handling {provider} webhook: {e}")
        return None

async def _handle_btcpay_webhook(session: AsyncSession, webhook_data: Dict[str, Any]) -> Optional[models.Payment]:
    """Handle BTCPay webhook."""
    invoice_id = webhook_data.get("invoiceId")
    status = webhook_data.get("status")

    if not invoice_id or status != "Settled":
        return None

    # Get payment from metadata
    metadata = webhook_data.get("metadata", {})
    payment_id = metadata.get("payment_id")

    if not payment_id:
        logger.error("BTCPay webhook missing payment_id in metadata")
        return None

    payment = await crud_payments.get_payment(session, payment_id)
    if not payment:
        logger.error(f"Payment {payment_id} not found for BTCPay webhook")
        return None

    if payment.status == "paid":
        return payment  # Already processed

    # Mark as paid
    updated_payment = await crud_payments.update_payment_status(session, payment_id, "paid", commit=False)

    await crud_logs.create_audit_log(
        session=session,
        user_id=payment.user_id,
        action="lightning_payment_received",
        payload={
            "payment_id": payment_id,
            "invoice_id": invoice_id,
            "provider": "btcpay",
            "amount_sats": payment.amount_sats,
        },
        commit=False,
    )

    logger.info(f"BTCPay payment received for payment {payment_id}", extra={"user_id": payment.user_id, "payment_id": payment_id})
    return updated_payment

async def _handle_opennode_webhook(session: AsyncSession, webhook_data: Dict[str, Any]) -> Optional[models.Payment]:
    """Handle OpenNode webhook."""
    invoice_id = webhook_data.get("id")
    status = webhook_data.get("status")

    if not invoice_id or status != "paid":
        return None

    # Get payment from metadata
    metadata = webhook_data.get("metadata", {})
    payment_id = metadata.get("payment_id")

    if not payment_id:
        logger.error("OpenNode webhook missing payment_id in metadata")
        return None

    payment = await crud_payments.get_payment(session, payment_id)
    if not payment:
        logger.error(f"Payment {payment_id} not found for OpenNode webhook")
        return None

    if payment.status == "paid":
        return payment  # Already processed

    # Mark as paid
    updated_payment = await crud_payments.update_payment_status(session, payment_id, "paid", commit=False)

    await crud_logs.create_audit_log(
        session=session,
        user_id=payment.user_id,
        action="lightning_payment_received",
        payload={
            "payment_id": payment_id,
            "invoice_id": invoice_id,
            "provider": "opennode",
            "amount_sats": payment.amount_sats,
        },
        commit=False,
    )

    logger.info(f"OpenNode payment received for payment {payment_id}", extra={"user_id": payment.user_id, "payment_id": payment_id})
    return updated_payment