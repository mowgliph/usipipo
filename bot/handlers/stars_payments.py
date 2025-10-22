# bot/handlers/stars_payments.py

from __future__ import annotations
from typing import Optional

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from database.db import AsyncSessionLocal as get_session
from database.crud import users as crud_users, payments as crud_payments
from services import payments as payments_service, vpn as vpn_service
from services import stars_payments as stars_service
from utils.helpers import (
    log_and_notify,
    log_error_and_notify,
    send_success,
    send_usage_error,
    send_warning,
    safe_chat_id_from_update,
)
from utils.permissions import require_registered

logger = logging.getLogger("usipipo.handlers.stars_payments")


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


async def _get_db_user(session: AsyncSession, tg_user_id: int):
    """Obtiene el usuario de la base de datos por telegram_id."""
    return await crud_users.get_user_by_telegram_id(session, tg_user_id)


@require_registered
async def stars_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando principal para pagos con estrellas: /pay o /stars <wireguard|outline> <months>"""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    validation = _validate_payment_args(context.args)
    if not validation:
        await send_usage_error(update, "pay", "<wireguard|outline> <months>")
        return

    vpn_type, months = validation

    async with get_session() as session:
        try:
            db_user = await _get_db_user(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado. Usa /register primero.")
                return

            # Crear pago en BD
            payment = await payments_service.create_vpn_payment(session, db_user.id, vpn_type, months)  # type: ignore
            if not payment:
                await send_warning(update, "No se pudo crear el pago. Intenta más tarde.")
                return

            # Procesar pago con estrellas
            invoice_id, payment_url = await stars_service.process_star_payment(session, payment, tg_user.id, bot)

            # Actualizar método de pago
            payment.payment_method = "stars"

            msg = f"⭐ <b>Pago con Estrellas de Telegram</b>\n\n"
            msg += f"🔹 Tipo VPN: {vpn_type.capitalize()}\n"
            msg += f"🔹 Duración: {months} meses\n"
            msg += f"💰 Monto: {payment.amount_stars} estrellas\n\n"
            msg += f"Presiona el botón abajo para pagar:"

            # Crear botón inline para el pago
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Pagar con Estrellas", url=payment_url)]
            ])

            await log_and_notify(session, bot, chat_id, db_user.id, action="stars_payment_initiated",
                                details=f"{vpn_type} {months}m | PaymentID {payment.id}", message=msg)

            await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)

            await session.commit()

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in stars_payment_handler: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(session, bot, chat_id, None, action="stars_payment_handler", error=e)


async def stars_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback handler para procesar pagos exitosos/fallidos con estrellas."""
    query = update.callback_query
    await query.answer()

    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    # Extraer payment_id del callback_data (asumiendo formato "payment_success_{payment_id}")
    callback_data = query.data
    if not callback_data.startswith("payment_success_"):
        return

    payment_id = callback_data.replace("payment_success_", "")

    async with get_session() as session:
        try:
            # Obtener el pago
            payment = await crud_payments.get_payment(session, payment_id)
            if not payment:
                await send_warning(update, "Pago no encontrado.")
                return

            # Verificar que el usuario sea el propietario del pago
            if payment.user_id != tg_user.id:
                await send_warning(update, "No tienes permisos para este pago.")
                return

            # Verificar estado del pago (en producción, esto vendría de webhook)
            status = await stars_service.verify_payment(session, payment, payment.invoice_id or "")

            if status == "paid":
                # Activar VPN
                success = await vpn_service.activate_vpn_for_user(session, payment.user_id, payment.vpn_type, payment.months)
                if success:
                    msg = f"✅ <b>¡Pago exitoso!</b>\n\n"
                    msg += f"⭐ Estrellas pagadas: {payment.amount_stars}\n"
                    msg += f"🔹 VPN {payment.vpn_type.capitalize()} activado por {payment.months} meses\n\n"
                    msg += "¡Disfruta tu VPN!"
                else:
                    msg = "⚠️ Pago procesado pero hubo un error activando la VPN. Contacta al administrador."

                await send_success(update, msg)

                await log_and_notify(session, bot, chat_id, payment.user_id, action="stars_payment_completed",
                                    details=f"PaymentID {payment.id} | {payment.amount_stars} stars", message=msg)

            elif status == "failed":
                msg = "❌ El pago fue rechazado o falló."
                await send_warning(update, msg)

            else:
                msg = "⏳ El pago está pendiente de confirmación."
                await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

            await session.commit()

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in stars_payment_callback: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(session, bot, chat_id, None, action="stars_payment_callback", error=e)


def register_stars_payments_handlers(app):
    """Registra handlers de pagos con estrellas."""
    app.add_handler(CommandHandler(["pay", "stars"], stars_payment_handler))
    app.add_handler(CallbackQueryHandler(stars_payment_callback, pattern=r"^payment_success_"))