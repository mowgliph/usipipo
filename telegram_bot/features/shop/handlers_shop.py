"""
Handlers para sistema de comercio electrónico de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler, CommandHandler, ConversationHandler
from application.services.payment_service import PaymentService
from application.services.vpn_service import VpnService
from .messages_shop import ShopMessages
from .keyboards_shop import ShopKeyboards
from utils.logger import logger
from utils.spinner import shop_spinner_callback

# Estados de conversación
SHOP_MENU = 0
SHOP_VIP_PLANS = 1
SHOP_PREMIUM_ROLES = 2
SHOP_STORAGE_PLANS = 3
SELECTING_PAYMENT = 4
CONFIRMING_PURCHASE = 5


class ShopHandler:
    """Handler para sistema de comercio electrónico."""
    
    def __init__(self, payment_service: PaymentService, vpn_service: VpnService = None):
        """
        Inicializa el handler de shop.
        
        Args:
            payment_service: Servicio de pagos
            vpn_service: Servicio de VPN (opcional)
        """
        self.payment_service = payment_service
        self.vpn_service = vpn_service
        logger.info("🛍️ ShopHandler inicializado")

    @shop_spinner_callback
    async def show_shop_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, spinner_message_id: int = None):
        """
        Muestra el menú principal de la tienda.
        """
        query = update.callback_query
        
        if query:
            await query.answer()
            user_id = update.effective_user.id
        else:
            user_id = update.effective_user.id
        
        try:
            # Obtener balance del usuario
            balance = await self.payment_service.get_user_balance(user_id)
            balance = balance if balance is not None else 0
            
            message = ShopMessages.Menu.MAIN.format(balance=balance)
            keyboard = ShopKeyboards.main_menu()
            
            if query:
                # Para callbacks, usar el nuevo método de reemplazo
                await SpinnerManager.replace_spinner_with_message(
                    update, context, spinner_message_id,
                    text=message,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                # Para mensajes normales, responder normalmente
                await update.message.reply_text(
                    text=message,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                
        except Exception as e:
            logger.error(f"Error en show_shop_menu: {e}")
            if query:
                await query.edit_message_text(
                    text="❌ Error cargando el menú. Por favor, intenta nuevamente.",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    text="❌ Error cargando el menú. Por favor, intenta nuevamente.",
                    parse_mode="Markdown"
                )

    async def show_vip_plans(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra los planes VIP disponibles.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = ShopMessages.VipPlans.HEADER
            keyboard = ShopKeyboards.vip_plans()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return SHOP_VIP_PLANS
            
        except Exception as e:
            logger.error(f"Error en show_vip_plans: {e}")
            await query.edit_message_text(
                text=ShopMessages.Error.SYSTEM_ERROR,
                reply_markup=ShopKeyboards.back_to_shop(),
                parse_mode="Markdown"
            )
            return SHOP_MENU

    async def show_premium_roles(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra los roles premium disponibles.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = ShopMessages.PremiumRoles.HEADER
            
            # Agregar información de roles
            message += f"\n\n{ShopMessages.PremiumRoles.TASK_MANAGER}"
            message += f"\n\n{ShopMessages.PremiumRoles.ANNOUNCER}"
            
            keyboard = ShopKeyboards.premium_roles()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return SHOP_PREMIUM_ROLES
            
        except Exception as e:
            logger.error(f"Error en show_premium_roles: {e}")
            await query.edit_message_text(
                text=ShopMessages.Error.SYSTEM_ERROR,
                reply_markup=ShopKeyboards.back_to_shop(),
                parse_mode="Markdown"
            )
            return SHOP_MENU

    async def show_storage_plans(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra los planes de almacenamiento.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = ShopMessages.StoragePlans.HEADER
            
            # Agregar planes de almacenamiento
            message += f"\n\n{ShopMessages.StoragePlans.PLAN_100GB}"
            message += f"\n\n{ShopMessages.StoragePlans.PLAN_500GB}"
            message += f"\n\n{ShopMessages.StoragePlans.PLAN_1TB}"
            
            keyboard = ShopKeyboards.storage_plans()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return SHOP_STORAGE_PLANS
            
        except Exception as e:
            logger.error(f"Error en show_storage_plans: {e}")
            await query.edit_message_text(
                text=ShopMessages.Error.SYSTEM_ERROR,
                reply_markup=ShopKeyboards.back_to_shop(),
                parse_mode="Markdown"
            )
            return SHOP_MENU

    async def show_product_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra detalles de un producto específico.
        """
        query = update.callback_query
        await query.answer()
        
        # Extraer tipo y producto del callback_data
        callback_parts = query.data.split("_")
        product_type = callback_parts[1]
        product_id = callback_parts[2]
        
        try:
            product_info = await self._get_product_info(product_type, product_id)
            
            if not product_info:
                message = ShopMessages.Error.PRODUCT_NOT_FOUND
                keyboard = ShopKeyboards.back_to_shop()
            else:
                message = ShopMessages.Products.DETAILS.format(
                    name=product_info['name'],
                    price=product_info['price'],
                    description=product_info['description'],
                    features='\n'.join(f"• {feature}" for feature in product_info['features']),
                    benefits='\n'.join(f"🎁 {benefit}" for benefit in product_info['benefits'])
                )
                keyboard = ShopKeyboards.product_actions(product_type, product_id, product_info['price'])
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_product_details: {e}")
            await query.edit_message_text(
                text=ShopMessages.Error.SYSTEM_ERROR,
                reply_markup=ShopKeyboards.back_to_shop(),
                parse_mode="Markdown"
            )

    async def select_payment_method(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra métodos de pago disponibles.
        """
        query = update.callback_query
        await query.answer()
        
        # Extraer información del producto
        callback_parts = query.data.split("_")
        product_type = callback_parts[2]
        product_id = callback_parts[3]
        
        try:
            product_info = await self._get_product_info(product_type, product_id)
            
            if not product_info:
                message = ShopMessages.Error.PRODUCT_NOT_FOUND
                keyboard = ShopKeyboards.back_to_shop()
            else:
                message = ShopMessages.Payment.METHODS.format(
                    product_name=product_info['name'],
                    price=product_info['price']
                )
                keyboard = ShopKeyboards.payment_methods(product_type, product_id, product_info['price'])
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return SELECTING_PAYMENT
            
        except Exception as e:
            logger.error(f"Error en select_payment_method: {e}")
            await query.edit_message_text(
                text=ShopMessages.Error.SYSTEM_ERROR,
                reply_markup=ShopKeyboards.back_to_shop(),
                parse_mode="Markdown"
            )
            return SHOP_MENU

    async def confirm_purchase(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Confirma la compra de un producto.
        """
        query = update.callback_query
        await query.answer()
        
        # Extraer información del callback
        callback_parts = query.data.split("_")
        payment_method = callback_parts[2]
        product_type = callback_parts[3]
        product_id = callback_parts[4]
        
        try:
            product_info = await self._get_product_info(product_type, product_id)
            
            if not product_info:
                message = ShopMessages.Error.PRODUCT_NOT_FOUND
                keyboard = ShopKeyboards.back_to_shop()
            else:
                message = ShopMessages.Payment.CONFIRMATION.format(
                    product_name=product_info['name'],
                    price=product_info['price'],
                    payment_method=payment_method.title()
                )
                keyboard = ShopKeyboards.confirm_purchase(product_type, product_id, payment_method)
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return CONFIRMING_PURCHASE
            
        except Exception as e:
            logger.error(f"Error en confirm_purchase: {e}")
            await query.edit_message_text(
                text=ShopMessages.Error.SYSTEM_ERROR,
                reply_markup=ShopKeyboards.back_to_shop(),
                parse_mode="Markdown"
            )
            return SHOP_MENU

    async def process_purchase(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Procesa la compra de un producto.
        """
        query = update.callback_query
        await query.answer()
        
        # Extraer información del callback
        callback_parts = query.data.split("_")
        product_type = callback_parts[2]
        product_id = callback_parts[3]
        payment_method = callback_parts[4]
        user_id = update.effective_user.id
        
        try:
            product_info = await self._get_product_info(product_type, product_id)
            
            if not product_info:
                message = ShopMessages.Error.PRODUCT_NOT_FOUND
                keyboard = ShopKeyboards.back_to_shop()
            else:
                # Procesar pago
                success = await self._process_payment(user_id, product_type, product_id, payment_method)
                
                if success:
                    message = ShopMessages.Payment.SUCCESS.format(
                        product_name=product_info['name'],
                        price=product_info['price'],
                        payment_method=payment_method.title()
                    )
                    keyboard = ShopKeyboards.purchase_success()
                else:
                    message = ShopMessages.Payment.FAILED
                    keyboard = ShopKeyboards.back_to_shop()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en process_purchase: {e}")
            await query.edit_message_text(
                text=ShopMessages.Error.SYSTEM_ERROR,
                reply_markup=ShopKeyboards.back_to_shop(),
                parse_mode="Markdown"
            )

    async def show_purchase_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el historial de compras.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Aquí iría la lógica para obtener el historial de compras
            # Por ahora, mostramos un mensaje placeholder
            
            message = ShopMessages.History.PURCHASES.format(
                user_id=user_id,
                count=0  # Placeholder
            )
            
            keyboard = ShopKeyboards.back_to_shop()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_purchase_history: {e}")
            await query.edit_message_text(
                text=ShopMessages.Error.SYSTEM_ERROR,
                reply_markup=ShopKeyboards.back_to_shop(),
                parse_mode="Markdown"
            )

    # Métodos privados
    async def _get_product_info(self, product_type: str, product_id: str) -> dict:
        """Obtiene información de un producto."""
        try:
            if product_type == "vip":
                plans = {
                    "basic": {
                        "name": "Plan VIP Básico",
                        "price": 9.99,
                        "description": "Acceso básico a funciones premium",
                        "features": ["Llaves VPN ilimitadas", "100 GB por llave", "Soporte prioritario"],
                        "benefits": ["Servidores básicos", "Sin límites de velocidad", "Backup automático"]
                    },
                    "premium": {
                        "name": "Plan VIP Premium",
                        "price": 19.99,
                        "description": "Acceso premium con beneficios adicionales",
                        "features": ["Todo Básico +", "500 GB por llave", "Servidores dedicados"],
                        "benefits": ["Todos los servidores", "Soporte 24/7", "Backup en la nube"]
                    },
                    "elite": {
                        "name": "Plan VIP Elite",
                        "price": 39.99,
                        "description": "Acceso elite con beneficios máximos",
                        "features": ["Todo Premium +", "Datos ilimitados", "Soporte exclusivo"],
                        "benefits": ["Cuenta dedicada", "Acceso beta features", "Eventos exclusivos"]
                    }
                }
                return plans.get(product_id)
            
            elif product_type == "role":
                roles = {
                    "task_manager": {
                        "name": "Gestor de Tareas",
                        "price": 29.99,
                        "description": "Acceso completo a gestión de tareas",
                        "features": ["Crear tareas", "Asignar tareas", "Seguimiento avanzado"],
                        "benefits": ["Panel administrativo", "Estadísticas detalladas", "Soporte prioritario"]
                    },
                    "announcer": {
                        "name": "Anunciante",
                        "price": 49.99,
                        "description": "Acceso a sistema de anuncios",
                        "features": ["Crear anuncios", "Segmentación avanzada", "Estadísticas"],
                        "benefits": ["Alcance masivo", "Analytics completo", "Soporte dedicado"]
                    }
                }
                return roles.get(product_id)
            
            elif product_type == "storage":
                storage = {
                    "100gb": {
                        "name": "100 GB Adicionales",
                        "price": 4.99,
                        "description": "Espacio de almacenamiento extra",
                        "features": ["100 GB extra", "Compartible entre llaves", "Backup automático"],
                        "benefits": ["Más espacio para datos", "Flexibilidad total", "Seguridad mejorada"]
                    },
                    "500gb": {
                        "name": "500 GB Adicionales",
                        "price": 19.99,
                        "description": "Espacio de almacenamiento premium",
                        "features": ["500 GB extra", "Compartible entre llaves", "Backup automático"],
                        "benefits": ["Gran capacidad", "Ideal para empresas", "Seguridad enterprise"]
                    },
                    "1tb": {
                        "name": "1 TB Adicional",
                        "price": 34.99,
                        "description": "Espacio de almacenamiento ilimitado",
                        "features": ["1 TB extra", "Compartible entre llaves", "Backup automático"],
                        "benefits": ["Capacidad máxima", "Sin restricciones", "Seguridad total"]
                    }
                }
                return storage.get(product_id)
            
            return {}
        except Exception as e:
            logger.error(f"Error obteniendo información del producto: {e}")
            return {}

    async def _process_payment(self, user_id: int, product_type: str, product_id: str, payment_method: str) -> bool:
        """Procesa el pago de un producto."""
        try:
            # Aquí iría la lógica real de procesamiento de pago
            # Por ahora, simulamos el proceso
            product_info = await self._get_product_info(product_type, product_id)
            
            if product_info:
                balance = await self.payment_service.get_user_balance(user_id)
                
                if balance >= product_info['price']:
                    # Descontar balance
                    await self.payment_service.deduct_balance(user_id, product_info['price'])
                    
                    # Activar producto (simulado)
                    await self._activate_product(user_id, product_type, product_id)
                    
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error procesando pago: {e}")
            return False

    async def _activate_product(self, user_id: int, product_type: str, product_id: str):
        """Activa un producto para el usuario."""
        # Aquí iría la lógica real de activación
        # Por ahora, solo registramos el log
        logger.info(f"Producto activado para usuario {user_id}: {product_type} - {product_id}")


def get_shop_handlers(payment_service: PaymentService, vpn_service: VpnService = None):
    """
    Retorna los handlers de shop.
    
    Args:
        payment_service: Servicio de pagos
        vpn_service: Servicio de VPN (opcional)
        
    Returns:
        list: Lista de handlers
    """
    handler = ShopHandler(payment_service, vpn_service)
    
    return [
        MessageHandler(filters.Regex("^🛍️ Tienda$"), handler.show_shop_menu),
        CommandHandler("shop", handler.show_shop_menu),
    ]


def get_shop_callback_handlers(payment_service: PaymentService, vpn_service: VpnService = None):
    """
    Retorna los handlers de callbacks de shop.
    
    Args:
        payment_service: Servicio de pagos
        vpn_service: Servicio de VPN (opcional)
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = ShopHandler(payment_service, vpn_service)
    
    return [
        CallbackQueryHandler(handler.show_vip_plans, pattern="^shop_vip$"),
        CallbackQueryHandler(handler.show_premium_roles, pattern="^shop_roles$"),
        CallbackQueryHandler(handler.show_storage_plans, pattern="^shop_storage$"),
        CallbackQueryHandler(handler.show_product_details, pattern="^shop_details_"),
        CallbackQueryHandler(handler.select_payment_method, pattern="^shop_payment_"),
        CallbackQueryHandler(handler.confirm_purchase, pattern="^shop_confirm_"),
        CallbackQueryHandler(handler.process_purchase, pattern="^shop_buy_"),
        CallbackQueryHandler(handler.show_purchase_history, pattern="^shop_history$"),
    ]


def get_shop_conversation_handler(payment_service: PaymentService, vpn_service: VpnService = None) -> ConversationHandler:
    """
    Retorna el ConversationHandler para shop.
    
    Args:
        payment_service: Servicio de pagos
        vpn_service: Servicio de VPN (opcional)
        
    Returns:
        ConversationHandler: Handler configurado
    """
    handler = ShopHandler(payment_service, vpn_service)
    
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🛍️ Tienda$"), handler.show_shop_menu),
            CommandHandler("shop", handler.show_shop_menu),
        ],
        states={
            SHOP_MENU: [
                CallbackQueryHandler(handler.show_vip_plans, pattern="^shop_vip$"),
                CallbackQueryHandler(handler.show_premium_roles, pattern="^shop_roles$"),
                CallbackQueryHandler(handler.show_storage_plans, pattern="^shop_storage$"),
                CallbackQueryHandler(handler.show_purchase_history, pattern="^shop_history$"),
            ],
            SHOP_VIP_PLANS: [
                CallbackQueryHandler(handler.show_product_details, pattern="^shop_details_"),
                CallbackQueryHandler(handler.show_shop_menu, pattern="^shop_back$"),
            ],
            SHOP_PREMIUM_ROLES: [
                CallbackQueryHandler(handler.show_product_details, pattern="^shop_details_"),
                CallbackQueryHandler(handler.show_shop_menu, pattern="^shop_back$"),
            ],
            SHOP_STORAGE_PLANS: [
                CallbackQueryHandler(handler.show_product_details, pattern="^shop_details_"),
                CallbackQueryHandler(handler.show_shop_menu, pattern="^shop_back$"),
            ],
            SELECTING_PAYMENT: [
                CallbackQueryHandler(handler.confirm_purchase, pattern="^shop_confirm_"),
                CallbackQueryHandler(handler.show_shop_menu, pattern="^shop_back$"),
            ],
            CONFIRMING_PURCHASE: [
                CallbackQueryHandler(handler.process_purchase, pattern="^shop_buy_"),
                CallbackQueryHandler(handler.show_shop_menu, pattern="^shop_back$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handler.show_shop_menu),
            CallbackQueryHandler(handler.show_shop_menu, pattern="^shop_back$"),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )
