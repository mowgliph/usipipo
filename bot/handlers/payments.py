# bot/handlers/payments.py

from __future__ import annotations
from typing import Optional

import logging
import qrcode
import io

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler

from database.db import AsyncSessionLocal as get_session
from database.crud import users as crud_users
from services import payments as payments_service, vpn as vpn_service
from services import lightning_payments, ton_payments
from services import wireguard as wireguard_service
from utils.helpers import (
    log_and_notify,
    log_error_and_notify,
    send_success,
    send_usage_error,
    send_warning,
    safe_chat_id_from_update,
)
from utils.permissions import require_registered

logger = logging.getLogger("usipipo.handlers.payments")


async def _validate_payment_args(args: list[str]) -> tuple[str, int] | None:
    """Valida y extrae vpn_type y months de los argumentos."""
    if len(args) < 2:
        return None

    vpn_type = args[0].lower()
    if vpn_type not in ("wireguard", "outline"):
        return None

    try:
        months = int(args[1])
        if months < 1:
            return None
    except ValueError:
        return None

    return vpn_type, months


async def _get_db_user(session: AsyncSession, tg_user_id: int) -> Optional[object]:
    """Obtiene el usuario de la base de datos por telegram_id."""
    return await crud_users.get_user_by_telegram_id(session, tg_user_id)


async def _send_qr_code(update: Update, qr_data: str, caption: str) -> None:
    """Envía un código QR generado desde texto."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)

    await update.message.reply_photo(
        photo=bio,
        caption=caption,
        parse_mode=ParseMode.HTML
    )


@require_registered
async def paylightning_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Crea pago con Lightning: /paylightning <wireguard|outline> <months>"""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    validation = _validate_payment_args(context.args)
    if not validation:
        await send_usage_error(update, "paylightning", "<wireguard|outline> <months>")
        return

    vpn_type, months = validation

    async with get_session() as session:
        try:
            db_user = await _get_db_user(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado. Usa /register primero.")
                return

            # Crear pago en BD
            payment = await payments_service.create_vpn_payment(session, db_user.id, vpn_type, months)
            if not payment:
                await send_warning(update, "No se pudo crear el pago. Intenta más tarde.")
                return

            # Crear invoice Lightning
            invoice_id, payment_request = await lightning_payments.create_lightning_invoice(
                session, payment, f"VPN {vpn_type.capitalize()} {months} meses"
            )

            # Actualizar método de pago
            payment.payment_method = "lightning"
            # await crud_payments.update_payment_method(session, payment.id, "lightning")

            msg = f"⚡ Invoice Lightning creado para {vpn_type.capitalize()} por {months} meses.\n\n"
            msg += f"💰 Monto: {payment.amount_sats} sats\n"
            msg += f"🔗 Paga aquí: {payment_request}"

            await log_and_notify(session, bot, chat_id, db_user.id, action="lightning_invoice_created",
                                details=f"{vpn_type} {months}m | PaymentID {payment.id}", message=msg)

            # Enviar QR si es lightning invoice (bech32)
            if payment_request.startswith("lnbc"):
                await _send_qr_code(update, payment_request,
                                   f"📱 Escanea para pagar {payment.amount_sats} sats")

            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

            # Verificar pago periódicamente (simulado, en producción usar webhooks)
            # En un entorno real, configurar webhooks para manejar pagos automáticamente

            await session.commit()

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in paylightning_command: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(session, bot, chat_id, None, action="paylightning_command", error=e)


@require_registered
async def payton_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Crea pago con TON: /payton <wireguard|outline> <months>"""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    validation = _validate_payment_args(context.args)
    if not validation:
        await send_usage_error(update, "payton", "<wireguard|outline> <months>")
        return

    vpn_type, months = validation

    async with get_session() as session:
        try:
            db_user = await _get_db_user(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado. Usa /register primero.")
                return

            # Crear pago en BD
            payment = await payments_service.create_vpn_payment(session, db_user.id, vpn_type, months)
            if not payment:
                await send_warning(update, "No se pudo crear el pago. Intenta más tarde.")
                return

            # Crear invoice TON
            invoice_id, payment_link = await ton_payments.create_ton_invoice(
                session, payment, f"VPN {vpn_type.capitalize()} {months} meses"
            )

            # Actualizar método de pago
            payment.payment_method = "ton"
            # await crud_payments.update_payment_method(session, payment.id, "ton")

            msg = f"💎 Invoice TON creado para {vpn_type.capitalize()} por {months} meses.\n\n"
            msg += f"💰 Monto: {payment.amount_ton} TON\n"
            msg += f"🔗 Paga aquí: {payment_link}"

            await log_and_notify(session, bot, chat_id, db_user.id, action="ton_invoice_created",
                                details=f"{vpn_type} {months}m | PaymentID {payment.id}", message=msg)

            # Enviar QR para el link de pago TON
            await _send_qr_code(update, payment_link,
                               f"📱 Escanea para pagar {payment.amount_ton} TON")

            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

            # Verificar pago periódicamente (simulado, en producción usar webhooks)
            # En un entorno real, configurar webhooks para manejar pagos automáticamente

            await session.commit()

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in payton_command: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(session, bot, chat_id, None, action="payton_command", error=e)


def register_payments_handlers(app):
    """Registra handlers de pagos."""
    app.add_handler(CommandHandler("paylightning", paylightning_command))
    app.add_handler(CommandHandler("payton", payton_command))