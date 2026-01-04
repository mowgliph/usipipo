from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from loguru import logger

from application.services.referral_service import ReferralService
from application.services.vpn_service import VpnService
from application.services.payment_service import PaymentService
from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard.keyboard import Keyboards
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
            reply_markup=Keyboards.operations_menu_inline(),
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
                reply_markup=Keyboards.operations_menu_inline(),
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error in balance_display_handler: {e}")
            await query.edit_message_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=Keyboards.operations_menu_inline()
            )

    async def deposit_instructions_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra las instrucciones para recargar estrellas."""
        query = update.callback_query
        await query.answer()

        await query.edit_message_text(
            text=Messages.Operations.DEPOSIT_INSTRUCTIONS,
            reply_markup=Keyboards.operations_menu_inline(),
            parse_mode="Markdown"
        )

    async def star_payments_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja pagos exitosos con estrellas de Telegram."""
        # Este handler se activaría cuando Telegram confirme un pago
        # Por ahora, es un placeholder para futuras implementaciones
        query = update.callback_query
        await query.answer()

        await query.edit_message_text(
            text="💰 Función de pagos con estrellas próximamente disponible.",
            reply_markup=Keyboards.operations_menu_inline()
        )

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
            reply_markup=Keyboards.vip_plans(),
            parse_mode="Markdown"
        )

    async def vip_purchase_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa la compra de un plan VIP."""
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
                reply_markup=Keyboards.operations_menu_inline()
            )
            return

        try:
            user_status = await self.vpn_service.get_user_status(telegram_id)
            user = user_status["user"]
            if not user:
                raise Exception("Usuario no encontrado")

            await query.edit_message_text(
                text=Messages.Errors.INSUFFICIENT_BALANCE.format(
                    required=cost,
                    current=user.balance_stars
                ),
                reply_markup=Keyboards.operations_menu_inline()
            )

            # Upgrade to VIP first
            success = await self.vpn_service.upgrade_to_vip(user, months)
            if not success:
                raise Exception("Error al procesar el upgrade VIP")

            # Deduct balance and record transaction
            success = await self.payment_service.update_balance(
                telegram_id=telegram_id,
                amount=-cost,
                transaction_type="vip_purchase",
                description=f"Compra de plan VIP {months} meses",
                reference_id=f"vip_{months}m_{telegram_id}"
            )
            if not success:
                # If payment failed, we should ideally rollback VIP, but for now just log
                logger.error("Failed to deduct balance for VIP purchase")

            # Apply referral commission if applicable
            await self.payment_service.apply_referral_commission(telegram_id, cost)

            expiry_date = user.vip_expires_at.strftime("%d/%m/%Y") if user.vip_expires_at else "N/A"

            text = Messages.Operations.VIP_PURCHASE_SUCCESS.format(
                expiry_date=expiry_date,
                max_keys=settings.VIP_PLAN_MAX_KEYS,
                data_limit=settings.VIP_PLAN_DATA_LIMIT_GB
            )

            await query.edit_message_text(
                text=text,
                reply_markup=Keyboards.operations_menu_inline(),
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error in vip_purchase_handler: {e}")
            await query.edit_message_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=Keyboards.operations_menu_inline()
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
            CallbackQueryHandler(
                lambda u, c: self.deposit_instructions_handler(u, c),
                pattern="^deposit_stars$"
            ),

            # Handler para pagos con estrellas
            CallbackQueryHandler(
                lambda u, c: self.star_payments_handler(u, c),
                pattern="^star_payments$"
            ),

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