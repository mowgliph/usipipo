# bot/handlers/vpn.py

from __future__ import annotations
from typing import Optional, Dict
from io import BytesIO
from telegram import Update, LabeledPrice, InputFile
from telegram.ext import ContextTypes, CommandHandler, PreCheckoutQueryHandler, MessageHandler, filters
from telegram.constants import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
import os

from database.db import AsyncSessionLocal as get_session
from database.crud import users as crud_users, vpn as crud_vpn, payments as crud_payments
from services import vpn as vpn_service, payments as payments_service, trial as trial_service, wireguard as wireguard_service
from utils.permissions import require_registered, require_admin
from utils.helpers import (
    send_usage_error,
    send_warning,
    send_success,
    log_and_notify,
    log_error_and_notify,
    safe_chat_id_from_update,
    format_vpn_list,
    send_vpn_config,
    notify_admins,
)


@require_registered
async def newvpn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Crea una nueva VPN: /newvpn <wireguard|outline> <months>"""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    if len(context.args) < 2:
        await send_usage_error(update, "newvpn", "<wireguard|outline> <months>")
        return

    vpn_type = context.args[0].lower()
    if vpn_type not in ("wireguard", "outline"):
        await send_warning(update, "Tipo de VPN inválido. Usa wireguard u outline.")
        return

    try:
        months = int(context.args[1])
        if months < 1:
            await send_warning(update, "La duración debe ser al menos 1 mes.")
            return
    except ValueError:
        await send_usage_error(update, "newvpn", "<wireguard|outline> <months>")
        return

    async with get_session() as session:
        try:
            db_user = await crud_users.get_user_by_telegram_id(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado. Usa /register primero.")
                return

            payment = await payments_service.create_vpn_payment(session, db_user.id, vpn_type, months)
            if not payment:
                await send_warning(update, "No se pudo crear el pago. Intenta más tarde.")
                return

            msg = f"📡 Generando invoice para {vpn_type.capitalize()} por {months} meses..."
            await log_and_notify(session, bot, chat_id, db_user.id, action="payment_created", details=f"{vpn_type} {months}m | PaymentID {payment.id}", message=msg)

            await update.message.reply_invoice(
                title=f"Suscripción VPN {vpn_type.capitalize()}",
                description=f"{months} meses de servicio VPN {vpn_type.capitalize()}",
                payload=str(payment.id),
                provider_token=os.getenv("TELEGRAM_PROVIDER_TOKEN", ""),
                currency="XTR",
                prices=[LabeledPrice(f"VPN {vpn_type.capitalize()}", payment.amount_stars)],
                parse_mode=ParseMode.HTML,
            )
            await session.commit()
        except Exception as e:
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
            db_user = await crud_users.get_user_by_telegram_id(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado.")
                return

            vpns = await vpn_service.list_user_vpns(session, db_user.id)
            msg = await format_vpn_list(vpns)
            await log_and_notify(session, bot, chat_id, db_user.id, action="command_myvpns", details="Consultó VPNs", message=msg)
        except Exception as e:
            await log_error_and_notify(session, bot, chat_id, None, action="myvpns_command", error=e)


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
            db_user = await crud_users.get_user_by_telegram_id(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado.")
                return

            vpn = await crud_vpn.get_vpn_config(session, vpn_id)
            if not vpn:
                await send_warning(update, "VPN no encontrada.")
                return

            if vpn.user_id != db_user.id:
                if not await crud_users.is_user_admin(session, db_user.id):
                    await send_warning(update, "No tienes permisos para revocar esta VPN.")
                    return

            success = await vpn_service.revoke_vpn(session, vpn_id, vpn.vpn_type)
            if not success:
                await send_warning(update, "VPN no encontrada o ya revocada.")
                return

            msg = f"✅ VPN <code>{vpn_id}</code> revocada."
            await log_and_notify(session, bot, chat_id, db_user.id, action="command_revokevpn", details=f"Revocó VPN {vpn_id}", message=msg)
            await session.commit()
        except Exception as e:
            await log_error_and_notify(session, bot, chat_id, None, action="revokevpn_command", error=e)


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
            tg_payload = {
                "id": tg_user.id,
                "username": tg_user.username,
                "first_name": tg_user.first_name,
                "last_name": tg_user.last_name,
                "_update": update,
            }
            result = await trial_service.start_trial(session, bot, tg_payload, vpn_type, duration_days=7)
            if not result["ok"]:
                await send_warning(update, result["message"])
                return

            vpn = result["vpn"]
            await send_success(update, "Trial creado exitosamente.")
            await send_vpn_config(update, vpn, qr_bytes=await wireguard_service.generate_qr(vpn.config_data) if vpn.vpn_type == "wireguard" else None)
            await log_and_notify(session, bot, chat_id, vpn.user_id, action="command_trialvpn", details=f"Trial {vpn_type} creado ID:{vpn.id}", message=result["message"])
            await session.commit()
        except Exception as e:
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
            await log_and_notify(session, bot, chat_id, uid, action="pre_checkout", details=f"PaymentID {payment_id}", message=msg)

            await query.answer(ok=True)
        except Exception as e:
            await log_error_and_notify(session, bot, chat_id, None, action="precheckout_vpn_handler", error=e)
            await query.answer(ok=False, error_message="Error procesando el pago.")


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
            await log_and_notify(session, bot, chat_id, db_user.id, action="payment_paid", details=f"PaymentID {payment_id}", message=msg)

            vpn = await vpn_service.activate_vpn_for_user(session, db_user.id, payment.vpn_type, payment.months)
            if not vpn:
                await send_warning(update, "No se pudo activar la VPN. Contacta soporte.")
                return

            await send_vpn_config(update, vpn, qr_bytes=await wireguard_service.generate_qr(vpn.config_data) if vpn.vpn_type == "wireguard" else None)
            msg = f"🔐 VPN {payment.vpn_type.capitalize()} creada exitosamente."
            await log_and_notify(session, bot, chat_id, db_user.id, action="vpn_created", details=f"VPNID {vpn.id}", message=msg)
            await session.commit()
        except Exception as e:
            await log_error_and_notify(session, bot, chat_id, None, action="successful_payment_vpn_handler", error=e)
            await notify_admins(session, bot, message=f"Error en pago exitoso para {tg_user.id}: {str(e)}")


def register_vpn_handlers(app):
    """Registra handlers VPN."""
    app.add_handler(CommandHandler("newvpn", newvpn_command))
    app.add_handler(CommandHandler("myvpns", myvpns_command))
    app.add_handler(CommandHandler("revokevpn", revokevpn_command))
    app.add_handler(CommandHandler("trialvpn", trialvpn_command))
    app.add_handler(PreCheckoutQueryHandler(precheckout_vpn_handler))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_vpn_handler))