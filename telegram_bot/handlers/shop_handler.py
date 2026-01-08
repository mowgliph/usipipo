"""
Handler para planes especiales y tienda (Shop) del bot uSipipo.

Integra planes de suscripción VIP, roles premium (Gestor de Tareas, Anunciante),
y paquetes adicionales como GB de conexión.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram_bot.messages import ShopMessages, CommonMessages
from telegram_bot.keyboard import ShopKeyboards
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from utils.logger import logger

from application.services.payment_service import PaymentService
from utils.spinner import with_spinner

# Estados de conversación
SHOP_MENU = 0
SHOP_VIP_PLANS = 1
SHOP_PREMIUM_ROLES = 2
SHOP_STORAGE_PLANS = 3
SELECTING_PAYMENT = 4
CONFIRMING_PURCHASE = 5


class ShopHandler:
    """Handler para la tienda y planes del sistema."""

    def __init__(self, payment_service: PaymentService):
        self.payment_service = payment_service

    # ============================================
    # ROLES PREMIUM
    # ============================================

    async def show_premium_roles(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar roles premium disponibles."""
        query = update.callback_query
        await query.answer()

        try:
            message = f"""{ShopMessages.PremiumRoles.HEADER}

{ShopMessages.PremiumRoles.TASK_MANAGER}

{ShopMessages.PremiumRoles.ANNOUNCER}

{ShopMessages.PremiumRoles.BOTH_ROLES}"""

            keyboard = ShopKeyboards.premium_roles()

            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return SHOP_PREMIUM_ROLES

        except Exception as e:
            logger.error(f"Error mostrando roles premium: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return SHOP_MENU

    # ============================================
    # PAQUETES DE ALMACENAMIENTO
    # ============================================

    async def show_storage_plans(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar paquetes de almacenamiento/datos."""
        query = update.callback_query
        await query.answer()

        try:
            message = f"""{ShopMessages.StoragePlans.HEADER}

{ShopMessages.StoragePlans.BASIC}

{ShopMessages.StoragePlans.STANDARD}

{ShopMessages.StoragePlans.PREMIUM}

{ShopMessages.StoragePlans.UNLIMITED}"""

            keyboard = ShopKeyboards.storage_plans()

            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return SHOP_STORAGE_PLANS

        except Exception as e:
            logger.error(f"Error mostrando paquetes de almacenamiento: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return SHOP_MENU

    # ============================================
    # MENU PRINCIPAL DE TIENDA
    # ============================================

    async def shop_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar menú principal de la tienda."""
        query = update.callback_query
        await query.answer()

        try:
            user = update.effective_user
            balance = await self.payment_service.get_user_balance(user.id)
            balance = balance if balance is not None else 0

            message = f"""{ShopMessages.Menu.HEADER}

{ShopMessages.Menu.BALANCE.format(balance=balance)}

{ShopMessages.Menu.CATEGORIES}

{ShopMessages.Menu.VIP_DESCRIPTION}

{ShopMessages.Menu.ROLES_DESCRIPTION}

{ShopMessages.Menu.STORAGE_DESCRIPTION}

{ShopMessages.Menu.RECHARGE_DESCRIPTION}"""

            keyboard = ShopKeyboards.main_menu()

            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return SHOP_MENU

        except Exception as e:
            logger.error(f"Error mostrando menú de tienda: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)

    async def shop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar el comando /shop para mostrar el menú principal de la tienda."""
        try:
            user = update.effective_user
            balance = await self.payment_service.get_user_balance(user.id)
            balance = balance if balance is not None else 0

            message = f"""{ShopMessages.Menu.HEADER}

{ShopMessages.Menu.BALANCE.format(balance=balance)}

{ShopMessages.Menu.CATEGORIES}

{ShopMessages.Menu.VIP_DESCRIPTION}

{ShopMessages.Menu.ROLES_DESCRIPTION}

{ShopMessages.Menu.STORAGE_DESCRIPTION}

{ShopMessages.Menu.RECHARGE_DESCRIPTION}"""

            keyboard = ShopKeyboards.main_menu_command()

            await update.message.reply_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return SHOP_MENU

        except Exception as e:
            logger.error(f"Error mostrando menú de tienda desde comando /shop: {e}")
            await update.message.reply_text(
                CommonMessages.Errors.GENERIC.format(error=str(e)),
                parse_mode="Markdown"
            )

    # ============================================
    # CONFIRMAR COMPRA
    # ============================================

    async def confirm_purchase(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirmar compra de un producto."""
        query = update.callback_query
        callback_data = query.data

        try:
            await query.answer()

            # Parsear callback_data
            parts = callback_data.split("_")
            product_type = parts[1]  # vip, role, storage
            product_id = "_".join(parts[2:])  # Resto del identificador

            # Obtener información del producto
            product_info = self._get_product_info(product_type, product_id)

            if not product_info:
                await query.answer("❌ Producto no encontrado", show_alert=True)
                return SHOP_MENU

            context.user_data['pending_purchase'] = {
                'type': product_type,
                'id': product_id,
                'cost': product_info['cost'],
                'name': product_info['name']
            }

            message = ShopMessages.Purchase.CONFIRM_HEADER.format(
                product_name=product_info['name'],
                cost=product_info['cost']
            )

            keyboard = ShopKeyboards.confirm_purchase(product_type, product_id)

            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return CONFIRMING_PURCHASE

        except Exception as e:
            logger.error(f"Error confirmando compra: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return SHOP_MENU

    @with_spinner
    async def execute_purchase(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ejecutar la compra."""
        query = update.callback_query
        await query.answer()

        try:
            user_id = update.effective_user.id
            purchase_data = context.user_data.get('pending_purchase')

            if not purchase_data:
                await query.answer("❌ Compra no válida", show_alert=True)
                return SHOP_MENU

            cost = purchase_data['cost']
            product_name = purchase_data['name']

            # Verificar balance
            current_balance = await self.payment_service.get_user_balance(user_id)
            current_balance = current_balance if current_balance is not None else 0

            if current_balance < cost:
                message = ShopMessages.Purchase.INSUFFICIENT_BALANCE.format(
                    current_balance=current_balance,
                    cost=cost,
                    needed=cost - current_balance
                )

                keyboard = ShopKeyboards.insufficient_balance()

                await query.edit_message_text(
                    text=message,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
                return SHOP_MENU

            # Procesar la compra
            result = await self._process_purchase(
                user_id,
                purchase_data['type'],
                purchase_data['id'],
                cost,
                product_name
            )

            if result['success']:
                message = ShopMessages.Purchase.SUCCESS_HEADER.format(
                    product_name=product_name,
                    cost=cost,
                    old_balance=current_balance,
                    new_balance=current_balance - cost,
                    additional_message=result.get('message', '')
                )

                keyboard = ShopKeyboards.purchase_success()
            else:
                message = ShopMessages.Purchase.ERROR_HEADER.format(
                    error_message=result.get('message', 'Error desconocido')
                )
                keyboard = ShopKeyboards.purchase_error()

            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return SHOP_MENU

        except Exception as e:
            logger.error(f"Error ejecutando compra: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return SHOP_MENU

    # ============================================
    # MÉTODOS AUXILIARES
    # ============================================

    def _get_product_info(self, product_type: str, product_id: str) -> dict:
        """Obtener información de un producto."""
        
        # Planes VIP
        vip_plans = {
            '1month': {'name': 'Plan VIP 1 Mes', 'cost': 10, 'duration_days': 30},
            '3months': {'name': 'Plan VIP 3 Meses', 'cost': 27, 'duration_days': 90},
            '6months': {'name': 'Plan VIP 6 Meses', 'cost': 50, 'duration_days': 180},
            '12months': {'name': 'Plan VIP 12 Meses', 'cost': 90, 'duration_days': 365}
        }
        
        # Roles Premium
        premium_roles = {
            'task_manager_1month': {'name': 'Gestor de Tareas 1 Mes', 'cost': 50, 'duration_days': 30},
            'task_manager_3months': {'name': 'Gestor de Tareas 3 Meses', 'cost': 120, 'duration_days': 90},
            'task_manager_6months': {'name': 'Gestor de Tareas 6 Meses', 'cost': 220, 'duration_days': 180},
            'task_manager_1year': {'name': 'Gestor de Tareas 1 Año', 'cost': 400, 'duration_days': 365},
            'announcer_1month': {'name': 'Anunciante 1 Mes', 'cost': 80, 'duration_days': 30},
            'announcer_3months': {'name': 'Anunciante 3 Meses', 'cost': 200, 'duration_days': 90},
            'announcer_6months': {'name': 'Anunciante 6 Meses', 'cost': 350, 'duration_days': 180},
            'announcer_1year': {'name': 'Anunciante 1 Año', 'cost': 650, 'duration_days': 365},
            'both_1month': {'name': 'Ambos Roles 1 Mes', 'cost': 120, 'duration_days': 30},
            'both_3months': {'name': 'Ambos Roles 3 Meses', 'cost': 300, 'duration_days': 90},
            'both_6months': {'name': 'Ambos Roles 6 Meses', 'cost': 550, 'duration_days': 180},
            'both_1year': {'name': 'Ambos Roles 1 Año', 'cost': 1000, 'duration_days': 365}
        }
        
        # Paquetes de Almacenamiento
        storage_plans = {
            '10gb': {'name': 'Paquete +10 GB', 'cost': 5, 'gb': 10},
            '25gb': {'name': 'Paquete +25 GB', 'cost': 12, 'gb': 25},
            '50gb': {'name': 'Paquete +50 GB', 'cost': 25, 'gb': 50},
            '200gb': {'name': 'Paquete +200 GB', 'cost': 100, 'gb': 200}
        }
        
        if product_type == 'vip':
            return vip_plans.get(product_id)
        elif product_type == 'role':
            return premium_roles.get(product_id)
        elif product_type == 'storage':
            return storage_plans.get(product_id)
        
        return None

    @with_spinner
    async def _process_purchase(self, user_id: int, product_type: str, product_id: str, cost: int, product_name: str) -> dict:
        """Procesar la compra de un producto."""
        try:
            # Descontar del balance
            payment_result = await self.payment_service.deduct_balance(user_id, cost)
            
            if not payment_result:
                return {
                    'success': False,
                    'message': 'Error al procesar el pago'
                }
            
            # Aplicar el producto según el tipo
            if product_type == 'vip':
                # Activar VIP
                product_info = self._get_product_info(product_type, product_id)
                duration_days = product_info['duration_days']
                
                await self.payment_service.activate_vip(user_id, duration_days)
                
                return {
                    'success': True,
                    'message': f'Tu VIP ha sido activado por {duration_days} días'
                }
            
            elif product_type == 'role':
                # Asignar rol
                # Esta función debería conectar con admin_service
                # Por ahora, retornar mensaje de éxito
                return {
                    'success': True,
                    'message': f'Rol premium adquirido. Contacta al soporte para activarlo.'
                }
            
            elif product_type == 'storage':
                # Agregar almacenamiento
                product_info = self._get_product_info(product_type, product_id)
                gb = product_info['gb']
                
                await self.payment_service.add_storage(user_id, gb)
                
                return {
                    'success': True,
                    'message': f'{gb} GB han sido agregados a tu cuenta'
                }
            
            return {
                'success': False,
                'message': 'Tipo de producto no reconocido'
            }
            
        except Exception as e:
            logger.error(f"Error procesando compra: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }


def get_shop_handler(payment_service: PaymentService) -> list:
    """Retorna los handlers para la tienda."""
    handler = ShopHandler(payment_service)
    callbacks = []
    
    # Comando /shop
    callbacks.append(
        CommandHandler("shop", handler.shop_command)
    )
    
    # Menú principal
    callbacks.append(
        CallbackQueryHandler(handler.shop_menu, pattern="^shop_menu$|^shop$")
    )
    
    # Planes VIP - Solo callbacks de compra (show_vip_plans eliminado)
    callbacks.append(
        CallbackQueryHandler(handler.confirm_purchase, pattern="^shop_vip_")
    )
    
    # Roles Premium
    callbacks.append(
        CallbackQueryHandler(handler.show_premium_roles, pattern="^shop_roles$")
    )
    
    callbacks.append(
        CallbackQueryHandler(handler.confirm_purchase, pattern="^shop_role_")
    )
    
    # Almacenamiento
    callbacks.append(
        CallbackQueryHandler(handler.show_storage_plans, pattern="^shop_storage$")
    )
    
    callbacks.append(
        CallbackQueryHandler(handler.confirm_purchase, pattern="^shop_storage_")
    )
    
    # Ejecutar compra
    callbacks.append(
        CallbackQueryHandler(handler.execute_purchase, pattern="^shop_buy_")
    )
    
    return callbacks
