from telegram import Update, LabeledPrice
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, PreCheckoutQueryHandler
from utils.logger import logger

from application.services.referral_service import ReferralService
from application.services.vpn_service import VpnService
from application.services.payment_service import PaymentService
from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard.keyboard import Keyboards
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards
from config import settings

# Estados de conversación para pagos con estrellas
DEPOSIT_AMOUNT = range(1)

class PaymentHandler:
    def __init__(self, referral_service: ReferralService, vpn_service: VpnService, payment_service: PaymentService):
        self.referral_service = referral_service
        self.vpn_service = vpn_service
        self.payment_service = payment_service

    async def operations_menu_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú de operaciones."""
        query = update.callback_query
        await query.answer()

        await query.edit_message_text(
            text=Messages.Operations.MENU_TITLE,
            reply_markup=InlineKeyboards.operations_menu(),
            parse_mode="Markdown"
        )

    async def balance_display_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el balance de estrellas del usuario."""
        query = update.callback_query
        await query.answer()

        telegram_id = update.effective_user.id

        try:
            user_status = await self.vpn_service.get_user_status(telegram_id)
            user = user_status["user"]

            text = Messages.Operations.BALANCE_INFO.format(
                name=user.full_name or user.username or f"Usuario {user.telegram_id}",
                balance=user.balance_stars,
                total_deposited=user.total_deposited,
                referral_earnings=user.total_referral_earnings
            )

            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboards.operations_menu(),
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error in balance_display_handler: {e}")
            await query.edit_message_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=InlineKeyboards.operations_menu()
            )

    async def deposit_instructions_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el proceso de recarga de estrellas."""
        query = update.callback_query
        await query.answer()

        await query.edit_message_text(
            text="⭐ **Recargar Saldo**\n\n¿Cuántas estrellas deseas recargar?\n\nEnvía un número entre 1 y 1000.",
            reply_markup=None,
            parse_mode="Markdown"
        )
        return DEPOSIT_AMOUNT

    async def deposit_amount_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa la cantidad de estrellas a recargar y crea la factura."""
        try:
            amount = int(update.message.text.strip())
            if amount < 1 or amount > 1000:
                await update.message.reply_text(
                    "❌ Cantidad inválida. Debe ser entre 1 y 1000 estrellas.\n\nIntenta de nuevo:",
                    parse_mode="Markdown"
                )
                return DEPOSIT_AMOUNT

            telegram_id = update.effective_user.id

            # Crear la factura usando Telegram Stars
            prices = [LabeledPrice(label=f"Recarga de {amount} estrellas", amount=amount)]
            await update.message.reply_invoice(
                title=f"Recarga de {amount} Estrellas",
                description=f"Recarga tu saldo con {amount} estrellas de Telegram.",
                payload=f"deposit_{telegram_id}_{amount}",
                provider_token="",  # Para Telegram Stars, dejar vacío
                currency="XTR",  # Moneda para estrellas
                prices=prices,
                start_parameter="deposit"
            )

            return ConversationHandler.END

        except ValueError:
            await update.message.reply_text(
                "❌ Por favor, envía un número válido.\n\nIntenta de nuevo:",
                parse_mode="Markdown"
            )
            return DEPOSIT_AMOUNT
        except Exception as e:
            logger.error(f"Error in deposit_amount_handler: {e}")
            await update.message.reply_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                parse_mode="Markdown"
            )
            return ConversationHandler.END

    async def pre_checkout_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja la consulta de pre-checkout para aprobar el pago."""
        query = update.pre_checkout_query
        await query.answer(ok=True)

    async def successful_payment_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja pagos exitosos con estrellas y actualiza el balance o activa VIP."""
        payment = update.message.successful_payment

        # Extraer información del payload
        payload_parts = payment.invoice_payload.split('_')
        if len(payload_parts) == 3 and payload_parts[0] == 'deposit':
            telegram_id = int(payload_parts[1])
            amount = int(payload_parts[2])

            try:
                # Actualizar balance del usuario
                success = await self.payment_service.update_balance(
                    telegram_id=telegram_id,
                    amount=amount,
                    transaction_type="deposit",
                    description=f"Recarga de {amount} estrellas",
                    telegram_payment_id=payment.telegram_payment_charge_id
                )

                if success:
                    # Aplicar comisión de referido si aplica
                    await self.payment_service.apply_referral_commission(telegram_id, amount)

                    await update.message.reply_text(
                        f"✅ **Pago exitoso**\n\nTu saldo ha sido recargado con **{amount}** ⭐\n\nSaldo actualizado al instante.",
                        parse_mode="Markdown"
                    )
                else:
                    logger.error(f"Failed to update balance for user {telegram_id} after payment")
                    await update.message.reply_text(
                        "❌ Error al procesar el pago. Contacta a soporte.",
                        parse_mode="Markdown"
                    )

            except Exception as e:
                logger.error(f"Error processing successful payment: {e}")
                await update.message.reply_text(
                    text=Messages.Errors.GENERIC.format(error=str(e)),
                    parse_mode="Markdown"
                )
        elif len(payload_parts) == 3 and payload_parts[0] == 'vip':
            telegram_id = int(payload_parts[1])
            months = int(payload_parts[2])

            # Determine cost based on months
            if months == 1:
                cost = 10
            elif months == 3:
                cost = 27
            elif months == 6:
                cost = 50
            elif months == 12:
                cost = 90
            else:
                logger.warning(f"Invalid months in VIP payment payload: {payment.invoice_payload}")
                await update.message.reply_text(
                    "❌ Error en el pago VIP. Contacta a soporte.",
                    parse_mode="Markdown"
                )
                return

            try:
                user_status = await self.vpn_service.get_user_status(telegram_id)
                user = user_status["user"]
                if not user:
                    raise Exception("Usuario no encontrado")

                # Upgrade to VIP
                success = await self.vpn_service.upgrade_to_vip(user, months)
                if not success:
                    raise Exception("Error al procesar el upgrade VIP")

                # Record transaction (no balance deduction since paid via invoice)
                success = await self.payment_service.update_balance(
                    telegram_id=telegram_id,
                    amount=-cost,
                    transaction_type="vip_purchase",
                    description=f"Compra de plan VIP {months} meses",
                    reference_id=f"vip_{months}m_{telegram_id}",
                    telegram_payment_id=payment.telegram_payment_charge_id
                )
                if not success:
                    logger.error("Failed to record VIP purchase transaction")

                # Apply referral commission if applicable
                await self.payment_service.apply_referral_commission(telegram_id, cost)

                expiry_date = user.vip_expires_at.strftime("%d/%m/%Y") if user.vip_expires_at else "N/A"

                text = Messages.Operations.VIP_PURCHASE_SUCCESS.format(
                    expiry_date=expiry_date,
                    max_keys=settings.VIP_PLAN_MAX_KEYS,
                    data_limit=settings.VIP_PLAN_DATA_LIMIT_GB
                )

                await update.message.reply_text(
                    text=text,
                    parse_mode="Markdown"
                )

            except Exception as e:
                logger.error(f"Error processing VIP payment: {e}")
                await update.message.reply_text(
                    text=Messages.Errors.GENERIC.format(error=str(e)),
                    parse_mode="Markdown"
                )
        else:
            logger.warning(f"Invalid payment payload: {payment.invoice_payload}")


    async def vip_plans_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra los planes VIP disponibles."""
        query = update.callback_query
        await query.answer()

        text = Messages.Operations.VIP_PLAN_INFO.format(
            max_keys=settings.VIP_PLAN_MAX_KEYS,
            data_limit=settings.VIP_PLAN_DATA_LIMIT_GB,
            cost="10 estrellas por mes"
        )

        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboards.vip_plans(),
            parse_mode="Markdown"
        )

    async def vip_purchase_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa la compra de un plan VIP creando una factura de estrellas."""
        query = update.callback_query
        await query.answer()

        telegram_id = update.effective_user.id
        callback_data = query.data

        # Extraer la duración del callback
        if callback_data == "vip_1_month":
            months = 1
            cost = 10
        elif callback_data == "vip_3_months":
            months = 3
            cost = 27
        elif callback_data == "vip_6_months":
            months = 6
            cost = 50
        elif callback_data == "vip_12_months":
            months = 12
            cost = 90
        else:
            await query.edit_message_text(
                text="❌ Opción inválida.",
                reply_markup=InlineKeyboards.operations_menu()
            )
            return

        try:
            # Crear la factura usando Telegram Stars
            prices = [LabeledPrice(label=f"Plan VIP {months} meses", amount=cost)]
            await query.message.reply_invoice(
                title=f"Plan VIP {months} Meses",
                description=f"Activa tu plan VIP por {months} meses con {cost} estrellas.",
                payload=f"vip_{telegram_id}_{months}",
                provider_token="",  # Para Telegram Stars, dejar vacío
                currency="XTR",  # Moneda para estrellas
                prices=prices,
                start_parameter="vip_purchase"
            )

        except Exception as e:
            logger.error(f"Error in vip_purchase_handler: {e}")
            await query.edit_message_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=InlineKeyboards.operations_menu()
            )


    def get_handlers(self):
        """Retorna la lista de handlers para el sistema de pagos."""
        return [
            # Handler para el menú de operaciones
            CallbackQueryHandler(
                lambda u, c: self.operations_menu_handler(u, c),
                pattern="^operations_menu$"
            ),

            # Handlers para balance y depósitos
            CallbackQueryHandler(
                lambda u, c: self.balance_display_handler(u, c),
                pattern="^my_balance$"
            ),

            # Conversation handler para depósito de estrellas
            ConversationHandler(
                entry_points=[
                    CallbackQueryHandler(
                        lambda u, c: self.deposit_instructions_handler(u, c),
                        pattern="^deposit_stars$"
                    )
                ],
                states={
                    DEPOSIT_AMOUNT: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.deposit_amount_handler)
                    ]
                },
                fallbacks=[]
            ),

            # Handler para pre-checkout
            PreCheckoutQueryHandler(self.pre_checkout_handler),

            # Handler para pagos exitosos
            MessageHandler(filters.SUCCESSFUL_PAYMENT, self.successful_payment_handler),

            # Handlers para planes VIP
            CallbackQueryHandler(
                lambda u, c: self.vip_plans_handler(u, c),
                pattern="^vip_plan$"
            ),
            CallbackQueryHandler(
                lambda u, c: self.vip_purchase_handler(u, c),
                pattern="^vip_1_month$|^vip_3_months$|^vip_6_months$|^vip_12_months$"
            )
        ]


def get_payment_handlers(referral_service: ReferralService, vpn_service: VpnService, payment_service: PaymentService):
    """Función para obtener los handlers de pagos."""
    handler = PaymentHandler(referral_service, vpn_service, payment_service)
    return handler.get_handlers()