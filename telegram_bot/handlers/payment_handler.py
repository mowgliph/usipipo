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
            text="⭐ **Recargar Saldo**\n\n¿Cuántas estrellas deseas recargar?\n\nEnvía un número entero entre 1 y 10000 (sin decimales ni texto).",
            reply_markup=None,
            parse_mode="Markdown"
        )
        return DEPOSIT_AMOUNT

    async def deposit_amount_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa la cantidad de estrellas a recargar y crea la factura."""
        logger.info(f"💰 deposit_amount_handler llamado con texto: '{update.message.text}'")
        
        try:
            # Validar que sea un número entero (sin decimales)
            amount_text = update.message.text.strip()
            logger.info(f"🔢 Procesando cantidad: '{amount_text}'")
            
            # Verificar que no contenga puntos ni comas (decimales)
            if '.' in amount_text or ',' in amount_text:
                logger.warning(f"❌ Decimales detectados en: '{amount_text}'")
                await update.message.reply_text(
                    "❌ Solo se permiten números enteros (sin decimales).\n\nEnvía un número entero entre 1 y 10000:",
                    parse_mode="Markdown"
                )
                return DEPOSIT_AMOUNT
            
            amount = int(amount_text)
            logger.info(f"✅ Cantidad válida: {amount}")
            
            # Validar rango (1 a 10000)
            if amount < 1 or amount > 10000:
                logger.warning(f"❌ Cantidad fuera de rango: {amount}")
                await update.message.reply_text(
                    "❌ Cantidad inválida. Debe ser un número entero entre 1 y 10000 estrellas.\n\nIntenta de nuevo:",
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
        """Procesa la compra de un plan VIP con validación de balance y opciones de pago."""
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
            # Verificar balance del usuario
            user_status = await self.vpn_service.get_user_status(telegram_id)
            user = user_status["user"]
            current_balance = user.balance_stars

            # Validar que el usuario tenga saldo suficiente para pagar con balance
            if current_balance >= cost:
                # Mostrar opciones de pago
                await query.edit_message_text(
                    text=f"👑 **Compra de Plan VIP {months} Meses**\n\n"
                         f"💰 **Costo:** {cost} ⭐\n\n"
                         f"📊 **Tu saldo actual:** {current_balance} ⭐\n\n"
                         f"💡 **Elige tu método de pago:**",
                    reply_markup=self._get_vip_payment_options(telegram_id, months, cost),
                    parse_mode="Markdown"
                )
            else:
                # Solo permitir pago con factura si no tiene saldo suficiente
                await query.edit_message_text(
                    text=f"👑 **Compra de Plan VIP {months} Meses**\n\n"
                         f"💰 **Costo:** {cost} ⭐\n\n"
                         f"📊 **Tu saldo actual:** {current_balance} ⭐\n"
                         f"⚠️ **Saldo insuficiente** para pagar con balance.\n\n"
                         f"💡 **Se generará una factura para pagar con Telegram Stars:**",
                    parse_mode="Markdown"
                )

                # Crear la factura usando Telegram Stars
                prices = [LabeledPrice(label=f"Plan VIP {months} meses", amount=cost)]
                await query.message.reply_invoice(
                    title=f"Plan VIP {months} Meses",
                    description=f"Activa tu plan VIP por {months} meses con {cost} estrellas de Telegram.",
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


    async def vip_payment_method_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja la selección del método de pago para VIP."""
        query = update.callback_query
        await query.answer()

        callback_data = query.data
        
        try:
            if callback_data == "cancel_vip_purchase":
                await query.edit_message_text(
                    text="❌ **Compra cancelada**\n\nPuedes elegir otro plan VIP cuando quieras.",
                    reply_markup=InlineKeyboards.vip_plans(),
                    parse_mode="Markdown"
                )
                return

            # Parsear datos del callback
            parts = callback_data.split('_')
            if len(parts) == 5 and parts[0] == 'vip' and parts[1] == 'pay':
                payment_method = parts[2]  # 'balance' o 'invoice'
                telegram_id = int(parts[3])
                months = int(parts[4])
                cost = int(parts[5])
                
                if payment_method == 'balance':
                    # Pagar con balance existente
                    success = await self.payment_service.update_balance(
                        telegram_id=telegram_id,
                        amount=-cost,
                        transaction_type="vip_purchase",
                        description=f"Compra de plan VIP {months} meses con balance",
                        reference_id=f"vip_balance_{months}m_{telegram_id}"
                    )
                    
                    if success:
                        # Actualizar a VIP
                        user_status = await self.vpn_service.get_user_status(telegram_id)
                        user = user_status["user"]
                        success = await self.vpn_service.upgrade_to_vip(user, months)
                        
                        if success:
                            # Aplicar comisión de referido
                            await self.payment_service.apply_referral_commission(telegram_id, cost)
                            
                            expiry_date = user.vip_expires_at.strftime("%d/%m/%Y") if user.vip_expires_at else "N/A"
                            
                            text = Messages.Operations.VIP_PURCHASE_SUCCESS.format(
                                expiry_date=expiry_date,
                                max_keys=settings.VIP_PLAN_MAX_KEYS,
                                data_limit=settings.VIP_PLAN_DATA_LIMIT_GB
                            )
                            
                            await query.edit_message_text(
                                text=f"✅ **¡Plan VIP Activado!**\n\n{text}",
                                parse_mode="Markdown"
                            )
                        else:
                            # Revertir el cargo si falla el upgrade
                            await self.payment_service.update_balance(
                                telegram_id=telegram_id,
                                amount=cost,
                                transaction_type="vip_refund",
                                description=f"Reembolso por fallo en VIP {months} meses"
                            )
                            await query.edit_message_text(
                                text="❌ Error al activar el plan VIP. Se ha reembolsado tu saldo.",
                                parse_mode="Markdown"
                            )
                    else:
                        await query.edit_message_text(
                            text="❌ Error al procesar el pago con balance. Intenta con factura.",
                            parse_mode="Markdown"
                        )
                
                elif payment_method == 'invoice':
                    # Pagar con factura de Telegram Stars
                    prices = [LabeledPrice(label=f"Plan VIP {months} meses", amount=cost)]
                    await query.message.reply_invoice(
                        title=f"Plan VIP {months} Meses",
                        description=f"Activa tu plan VIP por {months} meses con {cost} estrellas de Telegram.",
                        payload=f"vip_{telegram_id}_{months}",
                        provider_token="",  # Para Telegram Stars, dejar vacío
                        currency="XTR",  # Moneda para estrellas
                        prices=prices,
                        start_parameter="vip_purchase"
                    )
                    
                    await query.edit_message_text(
                        text=f"📋 **Factura generada**\n\nPor favor, completa el pago de {cost} ⭐ usando el botón arriba.",
                        parse_mode="Markdown"
                    )

        except Exception as e:
            logger.error(f"Error in vip_payment_method_handler: {e}")
            await query.edit_message_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                parse_mode="Markdown"
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
                fallbacks=[],
                per_message=True,
                per_chat=True,
                per_user=True,
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
            ),
            CallbackQueryHandler(
                lambda u, c: self.vip_payment_method_handler(u, c),
                pattern="^vip_pay_|^cancel_vip_purchase$"
            )
        ]


def get_payment_handlers(referral_service: ReferralService, vpn_service: VpnService, payment_service: PaymentService):
    """Función para obtener los handlers de pagos."""
    handler = PaymentHandler(referral_service, vpn_service, payment_service)
    return handler.get_handlers()