 # bot/handlers/vpn.py

from __future__ import annotations
from typing import Optional, Dict, Any

import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler, PreCheckoutQueryHandler, MessageHandler, filters, CallbackQueryHandler

from database.crud import payments as crud_payments, users as crud_users, vpn as crud_vpn
from database.db import AsyncSessionLocal as get_session
from services import payments as payments_service, trial as trial_service, vpn as vpn_service, \
    wireguard as wireguard_service, qvapay_user_client as qvapay_client
from utils.helpers import (
    format_vpn_list,
    log_and_notify,
    log_error_and_notify,
    notify_admins,
    safe_chat_id_from_update,
    send_success,
    send_usage_error,
    send_vpn_config,
    send_warning,
)
from utils.permissions import require_registered

logger = logging.getLogger("usipipo.handlers.vpn")


async def _validate_vpn_type_and_months(args: list[str]) -> tuple[str, int] | None:
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


@require_registered
async def newvpn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Crea una nueva VPN: /newvpn <wireguard|outline> <months>"""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    validation = _validate_vpn_type_and_months(context.args)
    if not validation:
        await send_usage_error(update, "newvpn", "<wireguard|outline> <months>")
        return

    vpn_type, months = validation

    async with get_session() as session:
        try:
            db_user = await _get_db_user(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado. Usa /register primero.")
                return

            # Calcular precio
            price = await payments_service.calculate_price(months)

            # Verificar si usuario tiene QvaPay vinculado
            has_qvapay = db_user.qvapay_user_id is not None and db_user.qvapay_app_id is not None

            # Crear botones del menú
            keyboard = []
            if has_qvapay:
                keyboard.append([
                    InlineKeyboardButton("💳 Pagar con QvaPay", callback_data=f"vpn_pay_qvapay:{vpn_type}:{months}:{price['usd']}"),
                    InlineKeyboardButton("⭐ Pagar con Estrellas", callback_data=f"vpn_pay_stars:{vpn_type}:{months}")
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton("⭐ Pagar con Estrellas", callback_data=f"vpn_pay_stars:{vpn_type}:{months}")
                ])

            reply_markup = InlineKeyboardMarkup(keyboard)

            msg = f"🔐 **Nueva VPN {vpn_type.capitalize()}**\n\n"
            msg += f"📅 Duración: {months} meses\n"
            msg += f"💰 Precio: ${price['usd']:.2f} USD / {price['stars']} ⭐\n\n"
            msg += "Selecciona tu método de pago:"

            await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

            await log_and_notify(session, bot, chat_id, db_user.id, action="newvpn_menu_shown",
                                details=f"{vpn_type} {months}m | QvaPay: {has_qvapay}", message=msg)

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in newvpn_command: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(session, bot, chat_id, None, action="newvpn_command", error=e)
            await notify_admins(session, bot, message=f"Error en /newvpn para {tg_user.id}: {str(e)}")


@require_registered
async def myvpns_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lista VPNs del usuario: /myvpns"""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    async with get_session() as session:
        try:
            db_user = await _get_db_user(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado.")
                return

            vpns = await vpn_service.list_user_vpns(session, db_user.id)
            msg = await format_vpn_list(vpns)
            await log_and_notify(session, bot, chat_id, db_user.id, action="command_myvpns",
                                details="Consultó VPNs", message=msg)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in myvpns_command: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(session, bot, chat_id, None, action="myvpns_command", error=e)


async def _check_vpn_ownership_or_admin(session: AsyncSession, vpn: object, db_user: object) -> bool:
    """Verifica si el usuario es propietario de la VPN o es admin."""
    if vpn.user_id == db_user.id:
        return True
    return await crud_users.is_user_admin(session, db_user.id)


@require_registered
async def revokevpn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Revoca VPN: /revokevpn <vpn_id>"""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    if len(context.args) < 1:
        await send_usage_error(update, "revokevpn", "<vpn_id>")
        return

    vpn_id = context.args[0]

    async with get_session() as session:
        try:
            db_user = await _get_db_user(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado.")
                return

            vpn = await crud_vpn.get_vpn_config(session, vpn_id)
            if not vpn:
                await send_warning(update, "VPN no encontrada.")
                return

            if not await _check_vpn_ownership_or_admin(session, vpn, db_user):
                await send_warning(update, "No tienes permisos para revocar esta VPN.")
                return

            success = await vpn_service.revoke_vpn(session, vpn_id, vpn.vpn_type)
            if not success:
                await send_warning(update, "VPN no encontrada o ya revocada.")
                return

            msg = f"✅ VPN <code>{vpn_id}</code> revocada."
            await log_and_notify(session, bot, chat_id, db_user.id, action="command_revokevpn",
                                details=f"Revocó VPN {vpn_id}", message=msg)
            await session.commit()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in revokevpn_command: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(session, bot, chat_id, None, action="revokevpn_command", error=e)


async def _build_tg_payload(tg_user: object, update: Update) -> Dict[str, Any]:
    """Construye el payload de Telegram para el servicio de trial."""
    return {
        "id": tg_user.id,
        "username": tg_user.username,
        "first_name": tg_user.first_name,
        "last_name": tg_user.last_name,
        "_update": update,
    }


@require_registered
async def trialvpn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Crea trial: /trialvpn <wireguard|outline>"""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    if len(context.args) < 1:
        await send_usage_error(update, "trialvpn", "<wireguard|outline>")
        return

    vpn_type = context.args[0].lower()
    if vpn_type not in ("wireguard", "outline"):
        await send_warning(update, "Tipo de VPN inválido.")
        return

    async with get_session() as session:
        try:
            tg_payload = _build_tg_payload(tg_user, update)
            result = await trial_service.start_trial(session, bot, tg_payload, vpn_type, duration_days=7)
            if not result["ok"]:
                await send_warning(update, result["message"])
                return

            vpn = result["vpn"]
            await send_success(update, "Trial creado exitosamente.")
            qr_bytes = await wireguard_service.generate_qr(vpn.config_data) if vpn.vpn_type == "wireguard" else None
            await send_vpn_config(update, vpn, qr_bytes=qr_bytes)
            await log_and_notify(session, bot, chat_id, vpn.user_id, action="command_trialvpn",
                                details=f"Trial {vpn_type} creado ID:{vpn.id}", message=result["message"])
            await session.commit()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in trialvpn_command: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(session, bot, chat_id, None, action="trialvpn_command", error=e)


async def precheckout_vpn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler unificado para precheckout VPN."""
    query = update.pre_checkout_query
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    async with get_session() as session:
        try:
            payment_id = query.invoice_payload
            payment = await crud_payments.get_payment(session, payment_id)
            if not payment:
                await query.answer(ok=False, error_message="Pago no encontrado.")
                return

            db_user = await crud_users.get_user_by_telegram_id(session, query.from_user.id)
            uid = db_user.id if db_user else None

            msg = "📡 Procesando pre-checkout..."
            await log_and_notify(session, bot, chat_id, uid, action="pre_checkout",
                                details=f"PaymentID {payment_id}", message=msg)

            await query.answer(ok=True)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in precheckout_vpn_handler: %s", type(e).__name__, extra={"tg_id": query.from_user.id if query.from_user else None})
            await log_error_and_notify(session, bot, chat_id, None, action="precheckout_vpn_handler", error=e)
            await query.answer(ok=False, error_message="Error procesando el pago.")


async def vpn_payment_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para callbacks de pago VPN (estrellas y QvaPay)."""
    query = update.callback_query
    await query.answer()

    tg_user = query.from_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    data = query.data
    if not data.startswith("vpn_pay_"):
        return

    # Parse callback data: vpn_pay_stars:wireguard:3 or vpn_pay_qvapay:wireguard:3:5.00
    parts = data.split(":")
    if len(parts) < 4:
        await send_warning(update, "Datos de pago inválidos.")
        return

    payment_method = parts[1]  # stars or qvapay
    vpn_type = parts[2]
    months = int(parts[3])
    amount_usd = float(parts[4]) if len(parts) > 4 else None

    async with get_session() as session:
        try:
            db_user = await _get_db_user(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado.")
                return

            if payment_method == "stars":
                # Flujo existente de estrellas
                payment = await payments_service.create_vpn_payment(session, str(db_user.id), vpn_type, months)
                if not payment:
                    await send_warning(update, "No se pudo crear el pago. Intenta más tarde.")
                    return

                msg = f"📡 Generando invoice para {vpn_type.capitalize()} por {months} meses..."
                await log_and_notify(session, bot, chat_id, db_user.id, action="payment_created",
                                    details=f"{vpn_type} {months}m | PaymentID {payment.id}", message=msg)

                await query.message.reply_invoice(
                    title=f"Suscripción VPN {vpn_type.capitalize()}",
                    description=f"{months} meses de servicio VPN {vpn_type.capitalize()}",
                    payload=str(payment.id),
                    provider_token=os.getenv("TELEGRAM_PROVIDER_TOKEN", ""),
                    currency="XTR",
                    prices=[LabeledPrice(f"VPN {vpn_type.capitalize()}", payment.amount_stars)],
                    parse_mode=ParseMode.HTML,
                )
                await session.commit()

            elif payment_method == "qvapay":
                # Nuevo flujo con QvaPay
                if not amount_usd:
                    await send_warning(update, "Monto USD requerido para pago con QvaPay.")
                    return

                if not db_user.qvapay_user_id or not db_user.qvapay_app_id:
                    await send_warning(update, "QvaPay no vinculado. Usa /qvapay para vincular tu cuenta.")
                    return

                # Verificar balance
                try:
                    balance_info = await qvapay_client.QvaPayUserClient().async_get_user_balance(
                        db_user.qvapay_app_id, db_user.qvapay_user_id
                    )
                    usd_balance = balance_info.get("balances", {}).get("USD", 0)

                    if usd_balance < amount_usd:
                        await send_warning(update, f"Balance insuficiente. Tienes ${usd_balance:.2f} USD, necesitas ${amount_usd:.2f} USD.")
                        return

                except Exception as e:
                    logger.exception("Error verificando balance QvaPay: %s", str(e))
                    await send_warning(update, "Error verificando balance QvaPay. Intenta más tarde.")
                    return

                # Procesar pago
                try:
                    payment_result = await qvapay_client.QvaPayUserClient().async_process_payment(
                        db_user.qvapay_app_id, db_user.qvapay_user_id, amount_usd
                    )

                    msg = f"💰 Pago procesado con QvaPay: ${amount_usd:.2f} USD"
                    await log_and_notify(session, bot, chat_id, db_user.id, action="qvapay_payment_processed",
                                        details=f"{vpn_type} {months}m | Amount: ${amount_usd}", message=msg)

                    # Crear VPN inmediatamente
                    vpn = await vpn_service.activate_vpn_for_user(session, db_user.id, vpn_type, months)
                    if not vpn:
                        await send_warning(update, "No se pudo crear la VPN. Contacta soporte.")
                        return

                    qr_bytes = await wireguard_service.generate_qr(vpn.config_data) if vpn.vpn_type == "wireguard" else None
                    await send_vpn_config(update, vpn, qr_bytes=qr_bytes)
                    msg = f"🔐 VPN {vpn_type.capitalize()} creada exitosamente con QvaPay."
                    await log_and_notify(session, bot, chat_id, db_user.id, action="vpn_created_qvapay",
                                        details=f"VPNID {vpn.id}", message=msg)
                    await session.commit()

                except Exception as e:
                    logger.exception("Error procesando pago QvaPay: %s", str(e))
                    await send_warning(update, "Error procesando pago con QvaPay. Intenta más tarde.")
                    return

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in vpn_payment_callback_handler: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(session, bot, chat_id, None, action="vpn_payment_callback_handler", error=e)
            await notify_admins(session, bot, message=f"Error en callback de pago VPN para {tg_user.id}: {str(e)}")


async def successful_payment_vpn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler unificado para pago exitoso VPN."""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    success = update.message.successful_payment
    if not success:
        return

    async with get_session() as session:
        try:
            db_user = await crud_users.get_user_by_telegram_id(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado.")
                return

            payment_id = success.invoice_payload
            payment = await payments_service.mark_as_paid(session, payment_id)
            if not payment:
                await send_warning(update, "Pago no encontrado.")
                return

            msg = "💰 Pago recibido correctamente."
            await log_and_notify(session, bot, chat_id, db_user.id, action="payment_paid",
                                details=f"PaymentID {payment_id}", message=msg)

            vpn = await vpn_service.activate_vpn_for_user(session, db_user.id, payment.vpn_type, payment.months)
            if not vpn:
                await send_warning(update, "No se pudo activar la VPN. Contacta soporte.")
                return

            qr_bytes = await wireguard_service.generate_qr(vpn.config_data) if vpn.vpn_type == "wireguard" else None
            await send_vpn_config(update, vpn, qr_bytes=qr_bytes)
            msg = f"🔐 VPN {payment.vpn_type.capitalize()} creada exitosamente."
            await log_and_notify(session, bot, chat_id, db_user.id, action="vpn_created",
                                details=f"VPNID {vpn.id}", message=msg)
            await session.commit()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in successful_payment_vpn_handler: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(session, bot, chat_id, None, action="successful_payment_vpn_handler", error=e)
            await notify_admins(session, bot, message=f"Error en pago exitoso para {tg_user.id}: {str(e)}")


def register_vpn_handlers(app):
    """Registra handlers VPN."""
    app.add_handler(CommandHandler("newvpn", newvpn_command))
    app.add_handler(CommandHandler("myvpns", myvpns_command))
    app.add_handler(CommandHandler("revokevpn", revokevpn_command))
    app.add_handler(CommandHandler("trialvpn", trialvpn_command))
    app.add_handler(CallbackQueryHandler(vpn_payment_callback_handler, pattern=r"^vpn_pay_"))
    app.add_handler(PreCheckoutQueryHandler(precheckout_vpn_handler))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_vpn_handler))