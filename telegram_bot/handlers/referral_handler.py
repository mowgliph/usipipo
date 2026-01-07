from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, CommandHandler,filters
from utils.logger import logger

from application.services.referral_service import ReferralService
from application.services.vpn_service import VpnService
from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard import OperationKeyboards, CommonKeyboards

# Estados de conversación para aplicar código de referido
APPLY_REFERRAL = range(1)

class ReferralHandler:
    def __init__(self, referral_service: ReferralService, vpn_service: VpnService):
        self.referral_service = referral_service
        self.vpn_service = vpn_service

    async def operations_menu_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú de operaciones."""
        query = update.callback_query
        await query.answer()

        await query.edit_message_text(
            text=Messages.Operations.MENU_TITLE,
            reply_markup=OperationKeyboards.operations_menu(),
            parse_mode="Markdown"
        )

    async def referrals_menu_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú de referidos desde el callback referrals_menu."""
        query = update.callback_query
        await query.answer()

        telegram_id = update.effective_user.id

        try:
            referral_code = await self.referral_service.get_referral_code(telegram_id)
            referrals = await self.referral_service.get_referrals(telegram_id)
            earnings = await self.referral_service.get_referral_earnings(telegram_id)

            text = Messages.Operations.REFERRAL_PROGRAM.format(
                bot_username="usipipo_bot",  # TODO: Get from config
                referral_code=referral_code,
                direct_referrals=len(referrals),
                total_earnings=earnings,
                commission=10
            )

            await query.edit_message_text(
                text=text,
                reply_markup=OperationKeyboards.referral_actions(),
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error in referrals_menu_handler: {e}")
            await query.edit_message_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=OperationKeyboards.operations_menu()
            )

    async def referral_program_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra información del programa de referidos."""
        query = update.callback_query
        await query.answer()

        telegram_id = update.effective_user.id

        try:
            referral_code = await self.referral_service.get_referral_code(telegram_id)
            referrals = await self.referral_service.get_referrals(telegram_id)
            earnings = await self.referral_service.get_referral_earnings(telegram_id)

            text = Messages.Operations.REFERRAL_PROGRAM.format(
                bot_username="usipipo_bot",  # TODO: Get from config
                referral_code=referral_code,
                direct_referrals=len(referrals),
                total_earnings=earnings,
                commission=10
            )

            await query.edit_message_text(
                text=text,
                reply_markup=OperationKeyboards.referral_actions(),
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error in referral_program_handler: {e}")
            await query.edit_message_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=OperationKeyboards.operations_menu()
            )

    async def my_referral_code_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el código de referido del usuario."""
        query = update.callback_query
        await query.answer()

        telegram_id = update.effective_user.id

        try:
            referral_code = await self.referral_service.get_referral_code(telegram_id)

            text = Messages.Operations.REFERRAL_CODE.format(referral_code=referral_code)

            await query.edit_message_text(
                text=text,
                reply_markup=OperationKeyboards.referral_actions(),
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error in my_referral_code_handler: {e}")
            await query.edit_message_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=OperationKeyboards.referral_actions()
            )

    async def my_referrals_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra la lista de referidos del usuario."""
        query = update.callback_query
        await query.answer()

        telegram_id = update.effective_user.id

        try:
            referrals = await self.referral_service.get_referrals(telegram_id)

            if not referrals:
                text = "📭 No tienes referidos todavía.\n\nComparte tu código de referido para ganar estrellas!"
            else:
                text = "👥 **Mis Referidos:**\n\n"
                for i, referral in enumerate(referrals, 1):
                    name = referral.get('full_name') or referral.get('username') or f"Usuario {referral['telegram_id']}"
                    date = referral['created_at'].strftime("%d/%m/%Y")
                    text += f"{i}. {name} - Registrado: {date}\n"

            await query.edit_message_text(
                text=text,
                reply_markup=OperationKeyboards.operations_menu(),
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error in my_referrals_handler: {e}")
            await query.edit_message_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=OperationKeyboards.referral_actions()
            )

    async def referral_earnings_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra las ganancias por referidos."""
        query = update.callback_query
        await query.answer()

        telegram_id = update.effective_user.id

        try:
            earnings = await self.referral_service.get_referral_earnings(telegram_id)
            referrals_count = len(await self.referral_service.get_referrals(telegram_id))

            text = f"💰 **Mis Ganancias por Referidos**\n\n"
            text += f"👥 Referidos totales: {referrals_count}\n"
            text += f"⭐ Estrellas ganadas: {earnings}\n\n"
            text += f"💡 *Ganas 10% de cada depósito de tus referidos de por vida.*"

            await query.edit_message_text(
                text=text,
                reply_markup=OperationKeyboards.referral_actions(),
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error in referral_earnings_handler: {e}")
            await query.edit_message_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=OperationKeyboards.referral_actions()
            )

    async def share_referral_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comparte el enlace de referido."""
        query = update.callback_query
        await query.answer()

        telegram_id = update.effective_user.id

        try:
            referral_code = await self.referral_service.get_referral_code(telegram_id)

            # Escape HTML special characters in referral_code
            escaped_referral_code = self._escape_html(referral_code)

            text = Messages.Operations.SHARE_REFERRAL.format(
                referral_code=escaped_referral_code,
                bot_username="usipipo_bot"  # TODO: Get from config
            )

            await query.edit_message_text(
                text=text,
                reply_markup=OperationKeyboards.referral_actions(),
                parse_mode="HTML"
            )

        except Exception as e:
            logger.error(f"Error in share_referral_handler: {e}")
            await query.edit_message_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=OperationKeyboards.referral_actions(),
                parse_mode="HTML"
            )

    async def apply_referral_start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el proceso de aplicar código de referido."""
        query = update.callback_query
        await query.answer()

        await query.edit_message_text(
            text="📋 Envía el código de referido que te dieron:",
            reply_markup=None
        )
        return APPLY_REFERRAL

    async def apply_referral_code_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa el código de referido enviado."""
        referral_code = update.message.text.strip().upper()
        telegram_id = update.effective_user.id

        try:
            success = await self.referral_service.apply_referral_code(telegram_id, referral_code)

            if success:
                await update.message.reply_text(
                    text="✅ ¡Código de referido aplicado exitosamente!\n\nAhora ganarás estrellas cuando hagas depósitos.",
                    reply_markup=CommonKeyboards.back_button()
                )
            else:
                await update.message.reply_text(
                    text=Messages.Errors.REFERRAL_CODE_INVALID.format(code=referral_code),
                    reply_markup=CommonKeyboards.back_button()
                )

        except Exception as e:
            logger.error(f"Error applying referral code: {e}")
            await update.message.reply_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=CommonKeyboards.back_button()
            )

        return ConversationHandler.END

    async def cancel_apply_referral_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancela la aplicación de código de referido."""
        await update.message.reply_text(
            "❌ Operación cancelada.",
            reply_markup=CommonKeyboards.back_button()
        )
        return ConversationHandler.END

    def _generate_referral_code(self) -> str:
        """Generate a unique referral code."""
        import uuid
        return str(uuid.uuid4())[:8].upper()

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

    def get_handlers(self):
        """Retorna la lista de handlers para el sistema de referidos."""
        return [
            # Handler para el menú de operaciones
            CallbackQueryHandler(
                lambda u, c: self.operations_menu_handler(u, c),
                pattern="^operations_menu$"
            ),

            # Handler para el menú de referidos desde operaciones
            CallbackQueryHandler(
                lambda u, c: self.referrals_menu_handler(u, c),
                pattern="^referrals_menu$"
            ),

            # Handlers para el programa de referidos
            CallbackQueryHandler(
                lambda u, c: self.referral_program_handler(u, c),
                pattern="^referral_program$"
            ),
            CallbackQueryHandler(
                lambda u, c: self.my_referral_code_handler(u, c),
                pattern="^my_referral_code$"
            ),
            CallbackQueryHandler(
                lambda u, c: self.my_referrals_handler(u, c),
                pattern="^my_referrals$"
            ),
            CallbackQueryHandler(
                lambda u, c: self.referral_earnings_handler(u, c),
                pattern="^referral_earnings$"
            ),
            CallbackQueryHandler(
                lambda u, c: self.share_referral_handler(u, c),
                pattern="^share_referral$"
            ),

            # Conversation handler para aplicar código de referido
            ConversationHandler(
                entry_points=[
                    CallbackQueryHandler(self.apply_referral_start_handler, pattern="^apply_referral_code$")
                ],
                states={
                    APPLY_REFERRAL: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.apply_referral_code_handler)
                    ]
                },
                fallbacks=[
                    CommandHandler("cancel", self.cancel_apply_referral_handler)
                ],
                per_message=True,
                per_chat=True,
                per_user=True,
                allow_reentry=True
            )
        ]


def get_referral_handlers(referral_service: ReferralService, vpn_service: VpnService):
    """Función para obtener los handlers de referidos."""
    handler = ReferralHandler(referral_service, vpn_service)
    return handler.get_handlers()