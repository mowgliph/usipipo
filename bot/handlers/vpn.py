# bot/handlers/vpn.py

from __future__ import annotations
from typing import Optional, Dict, Any
 
import logging
import os
 
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton, PreCheckoutQuery, CallbackQuery, Message
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler, PreCheckoutQueryHandler, MessageHandler, filters, CallbackQueryHandler

from database.db import AsyncSessionLocal as get_session
from database.crud import payments as crud_payments
from database.models import User
from services import payments as payments_service, trial as trial_service, user as user_service
from services.vpn_crud import VPNCrudService
from services import wireguard as wireguard_service
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
    if not args or len(args) < 2:
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


async def _get_db_user(session: AsyncSession, tg_user_id: int) -> Optional[User]:
    """Obtiene el usuario de la base de datos por telegram_id."""
    return await user_service.get_user_by_telegram_id(session, tg_user_id)


@require_registered
async def newvpn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Crea una nueva VPN: /newvpn <wireguard|outline> <months>"""
    tg_user = update.effective_user
    if not tg_user:
        logger.warning("update.effective_user is None in newvpn_command")
        await send_warning(update, "Error: Usuario no identificado.")
        return
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    if not context.args or len(context.args) < 2:
        await send_usage_error(update, "newvpn", "<wireguard|outline> <months>")
        return

    validation = await _validate_vpn_type_and_months(context.args)
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

            # Calcular precio usando el servicio CRUD
            price_info = await VPNCrudService.calculate_vpn_price(months, "stars")

            # Verificar si usuario tiene QvaPay vinculado
            has_qvapay = db_user.qvapay_user_id is not None and db_user.qvapay_app_id is not None

            # Crear botones del menú
            keyboard = []
            if has_qvapay:
                keyboard.append([
                    InlineKeyboardButton(
                        "💳 Pagar con QvaPay",
                        callback_data=f"vpn_pay_qvapay:{vpn_type}:{months}:{price_info['usd']:.2f}"
                    ),
                    InlineKeyboardButton(
                        "⭐ Pagar con Estrellas",
                        callback_data=f"vpn_pay_stars:{vpn_type}:{months}"
                    )
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(
                        "⭐ Pagar con Estrellas",
                        callback_data=f"vpn_pay_stars:{vpn_type}:{months}"
                    )
                ])

            reply_markup = InlineKeyboardMarkup(keyboard)

            msg = (
                f"🔐 **Nueva VPN {vpn_type.capitalize()}**\n\n"
                f"📅 Duración: {months} meses\n"
                f"💰 Precio: ${price_info['usd']:.2f} USD / {price_info['stars']} ⭐\n\n"
                "Selecciona tu método de pago:"
            )

            # Verificar que update.message existe antes de usar reply_text
            if update.message:
                await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            else:
                if update.effective_chat:
                    logger.warning("update.message is None in newvpn_command, using effective_chat.send_message")
                    await update.effective_chat.send_message(
                        msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    logger.error("Both update.message and update.effective_chat are None in newvpn_command")

            await log_and_notify(session, bot, chat_id, str(db_user.id), action="newvpn_menu_shown",
                                  details=f"{vpn_type} {months}m | QvaPay: {has_qvapay}", message=msg)

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in newvpn_command: %s", type(e).__name__, extra={"tg_id": str(tg_user.id)})
            await log_error_and_notify(session, bot, chat_id, None, action="newvpn_command", error=e)
            await notify_admins(session, bot, message=f"Error en /newvpn para {str(tg_user.id)}: {str(e)}")


@require_registered
async def myvpns_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lista VPNs del usuario: /myvpns"""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    if not tg_user:
        logger.warning("update.effective_user is None in myvpns_command")
        await send_warning(update, "Error: Usuario no identificado.")
        return

    async with get_session() as session:
        try:
            db_user = await _get_db_user(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado.")
                return

            vpns = await VPNCrudService.list_user_vpns(session, str(db_user.id))
            msg = await format_vpn_list(vpns)
            await log_and_notify(session, bot, chat_id, str(db_user.id), action="command_myvpns",
                                  details="Consultó VPNs", message=msg)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in myvpns_command: %s", type(e).__name__, extra={"tg_id": str(tg_user.id)})
            await log_error_and_notify(session, bot, chat_id, None, action="myvpns_command", error=e)


# Función removida - ahora está en VPNCrudService


@require_registered
async def revokevpn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Revoca VPN: /revokevpn <vpn_id>"""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    if not tg_user:
        logger.warning("update.effective_user is None in trialvpn_command")
        await send_warning(update, "Error: Usuario no identificado.")
        return

    if not context.args or len(context.args) < 1:
        await send_usage_error(update, "revokevpn", "<vpn_id>")
        return

    vpn_id = context.args[0]

    async with get_session() as session:
        try:
            db_user = await _get_db_user(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado.")
                return

            # Usar el servicio CRUD para revocar VPN
            revoked_vpn = await VPNCrudService.revoke_vpn(session, vpn_id, str(db_user.id))
            if not revoked_vpn:
                await send_warning(update, "VPN no encontrada o no tienes permisos para revocarla.")
                return

            msg = f"✅ VPN <code>{vpn_id}</code> revocada."
            await log_and_notify(session, bot, chat_id, str(db_user.id), action="command_revokevpn",
                                  details=f"Revocó VPN {vpn_id}", message=msg)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in revokevpn_command: %s", type(e).__name__, extra={"tg_id": str(tg_user.id)})
            await log_error_and_notify(session, bot, chat_id, None, action="revokevpn_command", error=e)


# Función removida - ahora se construye inline


@require_registered
async def trialvpn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Crea trial: /trialvpn <wireguard|outline>"""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    if not tg_user:
        logger.warning("update.effective_user is None in revokevpn_command")
        await send_warning(update, "Error: Usuario no identificado.")
        return

    if not context.args or len(context.args) < 1:
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
            qr_bytes = await wireguard_service.generate_qr(vpn.config_data) if vpn.vpn_type == "wireguard" else None
            await send_vpn_config(update, vpn, qr_bytes=qr_bytes)
            await log_and_notify(session, bot, chat_id, str(vpn.user_id), action="command_trialvpn",
                                details=f"Trial {vpn_type} creado ID:{vpn.id}", message=result["message"])
            await session.commit()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in trialvpn_command: %s", type(e).__name__, extra={"tg_id": str(tg_user.id)})
            await log_error_and_notify(session, bot, chat_id, None, action="trialvpn_command", error=e)


async def precheckout_vpn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler unificado para precheckout VPN."""
    query: Optional[PreCheckoutQuery] = update.pre_checkout_query
    if not query:
        logger.warning("pre_checkout_query is None in precheckout_vpn_handler")
        return
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    async with get_session() as session:
        try:
            payment_id = query.invoice_payload
            payment = await crud_payments.get_payment_by_id(session, payment_id)
            if not payment:
                await query.answer(ok=False, error_message="Pago no encontrado.")
                return

            db_user = await user_service.get_user_by_telegram_id(session, query.from_user.id)
            uid = db_user.id if db_user else None

            msg = "📡 Procesando pre-checkout..."
            await log_and_notify(
                session, bot, chat_id, str(uid), action="pre_checkout",
                details=f"PaymentID {payment_id}", message=msg
            )

            await query.answer(ok=True)
        except Exception as e:  # pylint: disable=broad-except
            tg_id = str(query.from_user.id) if query.from_user else None
            logger.exception(
                "Error in precheckout_vpn_handler: %s", type(e).__name__,
                extra={"tg_id": tg_id}
            )
            await log_error_and_notify(
                session, bot, chat_id, None, action="precheckout_vpn_handler", error=e
            )
            await query.answer(ok=False, error_message="Error procesando el pago.")


async def vpn_payment_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para callbacks de pago VPN (estrellas y QvaPay)."""
    query: Optional[CallbackQuery] = update.callback_query
    if not query:
        logger.warning("callback_query is None in vpn_payment_callback_handler")
        return
    await query.answer()

    tg_user = query.from_user
    if not tg_user:
        logger.warning("query.from_user is None in vpn_payment_callback_handler")
        return
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    data = query.data
    if not data or not data.startswith("vpn_pay_"):
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
                # Flujo de estrellas usando servicio de pagos
                payment = await payments_service.create_vpn_payment(session, str(db_user.id), vpn_type, months)  # type: ignore
                if not payment:
                    await send_warning(update, "No se pudo crear el pago. Intenta más tarde.")
                    return

                msg = f"📡 Generando invoice para {vpn_type.capitalize()} por {months} meses..."
                await log_and_notify(session, bot, chat_id, str(db_user.id), action="payment_created",
                                      details=f"{vpn_type} {months}m | PaymentID {payment.id}", message=msg)

                if query.message and isinstance(query.message, Message):
                    await query.message.reply_invoice(
                        title=f"Suscripción VPN {vpn_type.capitalize()}",
                        description=f"{months} meses de servicio VPN {vpn_type.capitalize()}",
                        payload=str(payment.id),
                        provider_token=os.getenv("TELEGRAM_PROVIDER_TOKEN", ""),
                        currency="XTR",
                        prices=[LabeledPrice(f"VPN {vpn_type.capitalize()}", payment.amount_stars)],
                    )
                else:
                    logger.warning("query.message is None or not a Message in vpn_payment_callback_handler")
                await session.commit()

            elif payment_method == "qvapay":
                # Flujo con QvaPay usando servicio CRUD
                if not amount_usd:
                    await send_warning(update, "Monto USD requerido para pago con QvaPay.")
                    return

                if not db_user.qvapay_user_id or not db_user.qvapay_app_id:
                    await send_warning(update, "QvaPay no vinculado. Usa /qvapay para vincular tu cuenta.")
                    return

                # Verificar balance usando servicio CRUD
                try:
                    balance_check = await VPNCrudService.check_qvapay_balance(
                        session, str(db_user.id), amount_usd
                    )

                    if not balance_check["has_sufficient_balance"]:
                        await send_warning(update,
                            f"Balance insuficiente. Tienes ${balance_check['current_balance']:.2f} USD, "
                            f"necesitas ${balance_check['required_amount']:.2f} USD."
                        )
                        return

                except Exception as e:
                    logger.exception("Error verificando balance QvaPay: %s", str(e))
                    await send_warning(update, "Error verificando balance QvaPay. Intenta más tarde.")
                    return

                # Procesar pago completo usando servicio CRUD
                try:
                    vpn = await VPNCrudService.process_qvapay_payment(
                        session, str(db_user.id), vpn_type, months  # type: ignore
                    )

                    if not vpn:
                        await send_warning(update, "No se pudo crear la VPN. Contacta soporte.")
                        return

                    # Enviar configuración VPN
                    config_str = vpn.config_data.get("content", "") if isinstance(vpn.config_data, dict) else str(vpn.config_data)
                    qr_bytes = await wireguard_service.generate_qr(config_str) if vpn.vpn_type == "wireguard" else None
                    await send_vpn_config(update, vpn, qr_bytes=qr_bytes)

                    msg = f"🔐 VPN {vpn_type.capitalize()} creada exitosamente con QvaPay."
                    await log_and_notify(session, bot, chat_id, str(db_user.id), action="vpn_created_qvapay",
                                          details=f"VPNID {getattr(vpn, 'id', 'unknown')}", message=msg)

                except Exception as e:
                    logger.exception("Error procesando pago QvaPay: %s", str(e))
                    await send_warning(update, "Error procesando pago con QvaPay. Intenta más tarde.")
                    return

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in vpn_payment_callback_handler: %s", type(e).__name__, extra={"tg_id": str(tg_user.id)})
            await log_error_and_notify(session, bot, chat_id, None, action="vpn_payment_callback_handler", error=e)
            await notify_admins(session, bot, message=f"Error en callback de pago VPN para {str(tg_user.id)}: {str(e)}")


async def successful_payment_vpn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler unificado para pago exitoso VPN."""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    if not tg_user:
        logger.warning("update.effective_user is None in successful_payment_vpn_handler")
        return

    if not update.message:
        logger.warning("update.message is None in successful_payment_vpn_handler")
        return

    success = update.message.successful_payment
    if not success:
        return

    async with get_session() as session:
        try:
            db_user = await user_service.get_user_by_telegram_id(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado.")
                return

            payment_id = success.invoice_payload
            payment = await payments_service.mark_as_paid(session, payment_id)
            if not payment:
                await send_warning(update, "Pago no encontrado.")
                return

            msg = "💰 Pago recibido correctamente."
            await log_and_notify(session, bot, chat_id, str(db_user.id), action="payment_paid",
                                  details=f"PaymentID {payment_id}", message=msg)

            # Crear VPN usando servicio CRUD
            vpn = await VPNCrudService.create_vpn(
                session=session,
                user_id=str(db_user.id),
                vpn_type=payment.vpn_type,  # type: ignore
                months=payment.months,
                payment_method="stars",
                is_trial=False,
                commit=True
            )

            if not vpn:
                await send_warning(update, "No se pudo activar la VPN. Contacta soporte.")
                return

            # Enviar configuración VPN
            config_str = vpn.config_data.get("content", "") if isinstance(vpn.config_data, dict) else str(vpn.config_data)
            qr_bytes = await wireguard_service.generate_qr(config_str) if vpn.vpn_type == "wireguard" else None
            await send_vpn_config(update, vpn, qr_bytes=qr_bytes)

            msg = f"🔐 VPN {payment.vpn_type.capitalize()} creada exitosamente."
            await log_and_notify(session, bot, chat_id, str(db_user.id), action="vpn_created",
                                  details=f"VPNID {vpn.id}", message=msg)

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in successful_payment_vpn_handler: %s", type(e).__name__, extra={"tg_id": str(tg_user.id)})
            await log_error_and_notify(session, bot, chat_id, None, action="successful_payment_vpn_handler", error=e)
            await notify_admins(session, bot, message=f"Error en pago exitoso para {str(tg_user.id)}: {str(e)}")


def register_vpn_handlers(app):
    """Registra handlers VPN."""
    app.add_handler(CommandHandler("newvpn", newvpn_command))
    app.add_handler(CommandHandler("myvpns", myvpns_command))
    app.add_handler(CommandHandler("revokevpn", revokevpn_command))
    app.add_handler(CommandHandler("trialvpn", trialvpn_command))
    app.add_handler(CallbackQueryHandler(vpn_payment_callback_handler, pattern=r"^vpn_pay_"))
    app.add_handler(PreCheckoutQueryHandler(precheckout_vpn_handler))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_vpn_handler))