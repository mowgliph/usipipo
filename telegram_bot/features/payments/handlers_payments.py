"""
Handlers para sistema de procesamiento de pagos de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler, CommandHandler, ConversationHandler, PreCheckoutQueryHandler
from application.services.payment_service import PaymentService
from application.services.vpn_service import VpnService
from application.services.referral_service import ReferralService
from .messages_payments import PaymentsMessages
from .keyboards_payments import PaymentsKeyboards
from config import settings
from utils.logger import logger

# Estados de conversación para pagos
DEPOSIT_AMOUNT = range(1)
SELECTING_AMOUNT = 1
SELECTING_METHOD = 2
CONFIRMING_PAYMENT = 3


class PaymentsHandler:
    """Handler para sistema de procesamiento de pagos."""
    
    def __init__(self, payment_service: PaymentService, vpn_service: VpnService = None, referral_service: ReferralService = None):
        """
        Inicializa el handler de pagos.
        
        Args:
            payment_service: Servicio de pagos
            vpn_service: Servicio de VPN (opcional)
            referral_service: Servicio de referidos (opcional)
        """
        self.payment_service = payment_service
        self.vpn_service = vpn_service
        self.referral_service = referral_service
        logger.info("💳 PaymentsHandler inicializado")

    async def show_payment_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el menú principal de pagos.
        """
        query = update.callback_query
        
        if query:
            await query.answer()
            user_id = update.effective_user.id
        else:
            user_id = update.effective_user.id
        
        try:
            # Obtener balance del usuario
            balance = await self.payment_service.get_user_balance(user_id, current_user_id=user_id)
            balance = balance if balance is not None else 0
            
            message = PaymentsMessages.Menu.MAIN.format(balance=balance)
            keyboard = PaymentsKeyboards.main_menu()
            
            if query:
                await query.edit_message_text(
                    text=message,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    text=message,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            
            return DEPOSIT_AMOUNT
            
        except Exception as e:
            logger.error(f"Error en show_payment_menu: {e}")
            error_message = PaymentsMessages.Error.SYSTEM_ERROR
            
            if query:
                await query.edit_message_text(
                    text=error_message,
                    reply_markup=PaymentsKeyboards.back_to_operations(),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    text=error_message,
                    reply_markup=PaymentsKeyboards.back_to_operations(),
                    parse_mode="Markdown"
                )
            
            return ConversationHandler.END

    async def select_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra opciones de monto para depositar.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = PaymentsMessages.Deposit.AMOUNT_OPTIONS
            keyboard = PaymentsKeyboards.amount_options()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return SELECTING_AMOUNT
            
        except Exception as e:
            logger.error(f"Error en select_amount: {e}")
            await query.edit_message_text(
                text=PaymentsMessages.Error.SYSTEM_ERROR,
                reply_markup=PaymentsKeyboards.back_to_payments(),
                parse_mode="Markdown"
            )
            return DEPOSIT_AMOUNT

    async def custom_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja la entrada de monto personalizado.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = PaymentsMessages.Deposit.CUSTOM_AMOUNT
            keyboard = PaymentsKeyboards.back_to_amounts()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en custom_amount: {e}")
            await query.edit_message_text(
                text=PaymentsMessages.Error.SYSTEM_ERROR,
                reply_markup=PaymentsKeyboards.back_to_payments(),
                parse_mode="Markdown"
            )

    async def process_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Procesa el monto ingresado por el usuario.
        """
        query = update.callback_query
        await query.answer()
        
        # Extraer monto del callback_data
        amount = int(query.data.split("_")[-1])
        user_id = update.effective_user.id
        
        try:
            # Validar monto
            if amount <= 0:
                message = PaymentsMessages.Deposit.INVALID_AMOUNT
                keyboard = PaymentsKeyboards.back_to_amounts()
            elif amount > 10000:
                message = PaymentsMessages.Deposit.AMOUNT_TOO_HIGH.format(max_amount=10000)
                keyboard = PaymentsKeyboards.back_to_amounts()
            else:
                # Continuar con selección de método de pago
                message = PaymentsMessages.Payment.METHODS.format(amount=amount)
                keyboard = PaymentsKeyboards.payment_methods(amount)
                
                # Guardar monto en contexto
                context.user_data['deposit_amount'] = amount
                
                return SELECTING_METHOD
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except ValueError:
            message = PaymentsMessages.Deposit.INVALID_AMOUNT
            keyboard = PaymentsKeyboards.back_to_amounts()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error en process_amount: {e}")
            await query.edit_message_text(
                text=PaymentsMessages.Error.SYSTEM_ERROR,
                reply_markup=PaymentsKeyboards.back_to_payments(),
                parse_mode="Markdown"
            )
        
        return SELECTING_AMOUNT

    async def select_payment_method(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra métodos de pago disponibles.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            amount = context.user_data.get('deposit_amount', 0)
            
            message = PaymentsMessages.Payment.METHODS.format(amount=amount)
            keyboard = PaymentsKeyboards.payment_methods(amount)
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return CONFIRMING_PAYMENT
            
        except Exception as e:
            logger.error(f"Error en select_payment_method: {e}")
            await query.edit_message_text(
                text=PaymentsMessages.Error.SYSTEM_ERROR,
                reply_markup=PaymentsKeyboards.back_to_payments(),
                parse_mode="Markdown"
            )
            return SELECTING_AMOUNT

    async def confirm_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Confirma el pago.
        """
        query = update.callback_query
        await query.answer()
        
        # Extraer método de pago y monto
        callback_parts = query.data.split("_")
        payment_method = callback_parts[2]
        amount = context.user_data.get('deposit_amount', 0)
        user_id = update.effective_user.id
        
        try:
            message = PaymentsMessages.Payment.CONFIRMATION.format(
                amount=amount,
                payment_method=payment_method.title(),
                user_id=user_id
            )
            keyboard = PaymentsKeyboards.confirm_payment(payment_method, amount)
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return CONFIRMING_PAYMENT
            
        except Exception as e:
            logger.error(f"Error en confirm_payment: {e}")
            await query.edit_message_text(
                text=PaymentsMessages.Error.SYSTEM_ERROR,
                reply_markup=PaymentsKeyboards.back_to_payments(),
                parse_mode="Markdown"
            )
            return SELECTING_AMOUNT

    async def process_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Procesa el pago.
        """
        query = update.callback_query
        await query.answer()
        
        # Extraer información del pago
        callback_parts = query.data.split("_")
        payment_method = callback_parts[2]
        amount = context.user_data.get('deposit_amount', 0)
        user_id = update.effective_user.id
        
        try:
            # Procesar pago según el método
            if payment_method == "balance":
                success = await self._process_balance_payment(user_id, amount)
            elif payment_method == "card":
                success = await self._process_card_payment(user_id, amount)
            elif payment_method == "transfer":
                success = await self._process_transfer_payment(user_id, amount)
            elif payment_method == "crypto":
                success = await self._process_crypto_payment(user_id, amount)
            else:
                success = False
            
            if success:
                message = PaymentsMessages.Payment.SUCCESS.format(
                    amount=amount,
                    payment_method=payment_method.title(),
                    user_id=user_id
                )
                keyboard = PaymentsKeyboards.payment_success()
                
                # Limpiar contexto
                context.user_data.clear()
            else:
                message = PaymentsMessages.Payment.FAILED
                keyboard = PaymentsKeyboards.back_to_payments()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en process_payment: {e}")
            await query.edit_message_text(
                text=PaymentsMessages.Error.SYSTEM_ERROR,
                reply_markup=PaymentsKeyboards.back_to_payments(),
                parse_mode="Markdown"
            )
        
        return ConversationHandler.END

    async def show_payment_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el historial de pagos.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Aquí iría la lógica para obtener el historial de pagos
            # Por ahora, mostramos un mensaje placeholder
            
            message = PaymentsMessages.History.PAYMENTS.format(
                user_id=user_id,
                count=0  # Placeholder
            )
            
            keyboard = PaymentsKeyboards.back_to_payments()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_payment_history: {e}")
            await query.edit_message_text(
                text=PaymentsMessages.Error.SYSTEM_ERROR,
                reply_markup=PaymentsKeyboards.back_to_payments(),
                parse_mode="Markdown"
            )

    async def show_transaction_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra detalles de una transacción específica.
        """
        query = update.callback_query
        await query.answer()
        
        # Extraer ID de transacción
        transaction_id = query.data.split("_")[-1]
        user_id = update.effective_user.id
        
        try:
            # Aquí iría la lógica para obtener detalles de transacción
            # Por ahora, mostramos un mensaje placeholder
            
            message = PaymentsMessages.History.TRANSACTION_DETAIL.format(
                transaction_id=transaction_id,
                date="2024-01-01 12:00:00",  # Placeholder
                amount=10.00,  # Placeholder
                method="Balance",  # Placeholder
                status="Completado",  # Placeholder
                user_id=user_id
            )
            
            keyboard = PaymentsKeyboards.back_to_history()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_transaction_details: {e}")
            await query.edit_message_text(
                text=PaymentsMessages.Error.SYSTEM_ERROR,
                reply_markup=PaymentsKeyboards.back_to_history(),
                parse_mode="Markdown"
            )

    async def show_balance_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el estado del balance del usuario.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            balance = await self.payment_service.get_user_balance(user_id)
            balance = balance if balance is not None else 0
            
            # Obtener estadísticas del usuario
            user_status = await self.vpn_service.get_user_status(user_id, current_user_id=user_id) if self.vpn_service else {}
            user = user_status.get("user", {})
            
            total_deposited = getattr(user, 'total_deposited', 0)
            total_spent = getattr(user, 'total_spent', 0)
            
            message = PaymentsMessages.Balance.STATUS.format(
                balance=balance,
                total_deposited=total_deposited,
                total_spent=total_spent,
                available=balance
            )
            
            keyboard = PaymentsKeyboards.balance_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_balance_status: {e}")
            await query.edit_message_text(
                text=PaymentsMessages.Error.SYSTEM_ERROR,
                reply_markup=PaymentsKeyboards.back_to_payments(),
                parse_mode="Markdown"
            )

    # Métodos privados
    async def _process_balance_payment(self, user_id: int, amount: float) -> bool:
        """Procesa pago con balance."""
        try:
            # Aquí iría la lógica real de procesamiento
            # Por ahora, simulamos el proceso
            
            # Verificar si el usuario tiene suficiente balance
            current_balance = await self.payment_service.get_user_balance(user_id, current_user_id=user_id)
            
            if current_balance >= amount:
                # Descontar balance
                await self.payment_service.deduct_balance(user_id, amount, current_user_id=user_id)
                
                # Registrar transacción
                await self._register_transaction(user_id, amount, "balance", "completed")
                
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error procesando pago con balance: {e}")
            return False

    async def _process_card_payment(self, user_id: int, amount: float) -> bool:
        """Procesa pago con tarjeta."""
        try:
            # Aquí iría la integración con pasarelas de tarjeta
            # Por ahora, simulamos el proceso
            logger.info(f"Procesando pago con tarjeta para usuario {user_id}, amount: ${amount}")
            
            # Simular éxito
            await self._register_transaction(user_id, amount, "card", "completed")
            return True
        except Exception as e:
            logger.error(f"Error procesando pago con tarjeta: {e}")
            return False

    async def _process_transfer_payment(self, user_id: int, amount: float) -> bool:
        """Procesa pago por transferencia."""
        try:
            # Aquí iría la lógica para transferencias bancarias
            # Por ahora, simulamos el proceso
            logger.info(f"Procesando pago por transferencia para usuario {user_id}, amount: ${amount}")
            
            # Simular éxito
            await self._register_transaction(user_id, amount, "transfer", "pending")
            return True
        except Exception as e:
            logger.error(f"Error procesando pago por transferencia: {e}")
            return False

    async def _process_crypto_payment(self, user_id: int, amount: float) -> bool:
        """Procesa pago con criptomonedas."""
        try:
            # Aquí iría la integración con procesadores de crypto
            # Por ahora, simulamos el proceso
            logger.info(f"Procesando pago con crypto para usuario {user_id}, amount: ${amount}")
            
            # Simular éxito
            await self._register_transaction(user_id, amount, "crypto", "completed")
            return True
        except Exception as e:
            logger.error(f"Error procesando pago con crypto: {e}")
            return False

    async def _register_transaction(self, user_id: int, amount: float, method: str, status: str):
        """Registra una transacción en el sistema."""
        try:
            # Aquí iría la lógica para registrar en la base de datos
            # Por ahora, solo registramos el log
            logger.info(f"Transacción registrada: Usuario {user_id}, Monto: ${amount}, Método: {method}, Estado: {status}")
        except Exception as e:
            logger.error(f"Error registrando transacción: {e}")


def get_payments_handlers(payment_service: PaymentService, vpn_service: VpnService = None, referral_service: ReferralService = None):
    """
    Retorna los handlers de pagos.
    
    Args:
        payment_service: Servicio de pagos
        vpn_service: Servicio de VPN (opcional)
        referral_service: Servicio de referidos (opcional)
        
    Returns:
        list: Lista de handlers
    """
    handler = PaymentsHandler(payment_service, vpn_service, referral_service)
    
    return [
        MessageHandler(filters.Regex("^💳 Pagos$"), handler.show_payment_menu),
        CommandHandler("payment", handler.show_payment_menu),
        CommandHandler("deposit", handler.show_payment_menu),
    ]


def get_payments_callback_handlers(payment_service: PaymentService, vpn_service: VpnService = None, referral_service: ReferralService = None):
    """
    Retorna los handlers de callbacks de pagos.
    
    Args:
        payment_service: Servicio de pagos
        vpn_service: Servicio de VPN (opcional)
        referral_service: Servicio de referidos (opcional)
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = PaymentsHandler(payment_service, vpn_service, referral_service)
    
    return [
        CallbackQueryHandler(handler.show_balance_status, pattern="^balance_status$"),
        CallbackQueryHandler(handler.show_payment_history, pattern="^payment_history$"),
        CallbackQueryHandler(handler.show_transaction_details, pattern="^transaction_details_"),
    ]


def get_payments_conversation_handler(payment_service: PaymentService, vpn_service: VpnService = None, referral_service: ReferralService = None) -> ConversationHandler:
    """
    Retorna el ConversationHandler para pagos.
    
    Args:
        payment_service: Servicio de pagos
        vpn_service: Servicio de VPN (opcional)
        referral_service: Servicio de referidos (opcional)
        
    Returns:
        ConversationHandler: Handler configurado
    """
    handler = PaymentsHandler(payment_service, vpn_service, referral_service)
    
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^💳 Pagos$"), handler.show_payment_menu),
            CommandHandler("payment", handler.show_payment_menu),
            CommandHandler("deposit", handler.show_payment_menu),
        ],
        states={
            DEPOSIT_AMOUNT: [
                CallbackQueryHandler(handler.select_amount, pattern="^select_amount$"),
                CallbackQueryHandler(handler.custom_amount, pattern="^custom_amount$"),
                CallbackQueryHandler(handler.process_amount, pattern="^amount_"),
            ],
            SELECTING_AMOUNT: [
                CallbackQueryHandler(handler.select_payment_method, pattern="^payment_method_"),
                CallbackQueryHandler(handler.show_payment_menu, pattern="^payment_back$"),
            ],
            SELECTING_METHOD: [
                CallbackQueryHandler(handler.confirm_payment, pattern="^confirm_payment_"),
                CallbackQueryHandler(handler.show_payment_menu, pattern="^payment_back$"),
            ],
            CONFIRMING_PAYMENT: [
                CallbackQueryHandler(handler.process_payment, pattern="^process_payment_"),
                CallbackQueryHandler(handler.show_payment_menu, pattern="^payment_back$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handler.show_payment_menu),
            CallbackQueryHandler(handler.show_payment_menu, pattern="^payment_back$"),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )
