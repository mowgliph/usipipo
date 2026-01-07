"""
Handler para planes especiales y tienda (Shop) del bot uSipipo.

Integra planes de suscripción VIP, roles premium (Gestor de Tareas, Anunciante),
y paquetes adicionales como GB de conexión.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from config import settings
from utils.logger import logger
from datetime import datetime, timedelta, timezone

from application.services.payment_service import PaymentService
from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards
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
    # PLANES VIP
    # ============================================

    async def show_vip_plans(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar planes VIP disponibles."""
        query = update.callback_query
        await query.answer()

        try:
            message = """👑 **Planes VIP**

Disfruta de beneficios exclusivos con nuestros planes VIP:

🟢 **Plan VIP 1 Mes** - 10 ⭐
  • 10 claves VPN simultáneas
  • 50 GB de datos por clave
  • Soporte prioritario
  • Sin anuncios

🟡 **Plan VIP 3 Meses** - 27 ⭐
  • 10 claves VPN simultáneas
  • 50 GB de datos por clave
  • Soporte prioritario
  • Sin anuncios
  • Ahorra 3 ⭐

🔵 **Plan VIP 6 Meses** - 50 ⭐
  • 10 claves VPN simultáneas
  • 50 GB de datos por clave
  • Soporte prioritario
  • Sin anuncios
  • Ahorra 10 ⭐

🔴 **Plan VIP 12 Meses** - 90 ⭐
  • 10 claves VPN simultáneas
  • 50 GB de datos por clave
  • Soporte prioritario
  • Sin anuncios
  • Ahorra 30 ⭐"""

            keyboard = [
                [InlineKeyboardButton("1 Mes - 10⭐", callback_data="shop_vip_1month")],
                [InlineKeyboardButton("3 Meses - 27⭐", callback_data="shop_vip_3months")],
                [InlineKeyboardButton("6 Meses - 50⭐", callback_data="shop_vip_6months")],
                [InlineKeyboardButton("12 Meses - 90⭐", callback_data="shop_vip_12months")],
                [InlineKeyboardButton("🔙 Volver", callback_data="shop_menu")]
            ]

            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return SHOP_VIP_PLANS

        except Exception as e:
            logger.error(f"Error mostrando planes VIP: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return SHOP_MENU

    # ============================================
    # ROLES PREMIUM
    # ============================================

    async def show_premium_roles(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar roles premium disponibles."""
        query = update.callback_query
        await query.answer()

        try:
            message = """📋 **Roles Premium**

Obtén roles especiales para funcionalidades exclusivas:

📋 **GESTOR DE TAREAS** - 50 ⭐ / mes
  Crea y gestiona tareas para otros usuarios
  • Crear tareas públicas/privadas
  • Ver participación de usuarios
  • Recompensas por tareas completadas
  • Estadísticas detalladas
  
  Planes: 1 mes | 3 meses | 6 meses | 1 año

📣 **ANUNCIANTE** - 80 ⭐ / mes
  Envía anuncios y promociones a otros usuarios
  • Crear campañas de anuncios
  • Targeting por región/tipo de usuario
  • Estadísticas de visualización
  • Hasta 100 anuncios por mes
  
  Planes: 1 mes | 3 meses | 6 meses | 1 año

✨ **Ambos Roles** - 120 ⭐ / mes
  Obtén acceso a ambos roles premium
  • Todas las funciones de Gestor de Tareas
  • Todas las funciones de Anunciante
  • Descuento especial en paquetes
  
  Planes: 1 mes | 3 meses | 6 meses | 1 año"""

            keyboard = [
                [InlineKeyboardButton("📋 Gestor de Tareas", callback_data="shop_role_task_manager")],
                [InlineKeyboardButton("📣 Anunciante", callback_data="shop_role_announcer")],
                [InlineKeyboardButton("✨ Ambos Roles", callback_data="shop_role_both")],
                [InlineKeyboardButton("🔙 Volver", callback_data="shop_menu")]
            ]

            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
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
            message = """💾 **Paquetes de Almacenamiento**

Amplía tu límite de datos mensuales:

🟢 **Paquete Básico** - 5 ⭐
  • +10 GB de datos
  • Válido por 30 días
  • Aplicable a todas tus claves

🟡 **Paquete Estándar** - 12 ⭐
  • +25 GB de datos
  • Válido por 30 días
  • Aplicable a todas tus claves
  • Ahorra 3 ⭐ vs Paquete Básico x3

🔵 **Paquete Premium** - 25 ⭐
  • +50 GB de datos
  • Válido por 30 días
  • Aplicable a todas tus claves
  • Ahorra 5 ⭐ vs Paquete Estándar x2

🔴 **Paquete Ilimitado** - 100 ⭐
  • +200 GB de datos
  • Válido por 30 días
  • Aplicable a todas tus claves
  • Mejor ahorro"""

            keyboard = [
                [InlineKeyboardButton("+10 GB - 5⭐", callback_data="shop_storage_10gb")],
                [InlineKeyboardButton("+25 GB - 12⭐", callback_data="shop_storage_25gb")],
                [InlineKeyboardButton("+50 GB - 25⭐", callback_data="shop_storage_50gb")],
                [InlineKeyboardButton("+200 GB - 100⭐", callback_data="shop_storage_200gb")],
                [InlineKeyboardButton("🔙 Volver", callback_data="shop_menu")]
            ]

            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
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
            user_info = await self.payment_service.get_user_balance(user.id)
            balance = user_info.get('balance_stars', 0) if user_info else 0

            message = f"""🛒 **SHOP uSipipo**

Tu Balance: ⭐ {balance}

Selecciona una categoría:

👑 **Planes VIP**
  Obtén acceso a más claves y GB

📋 **Roles Premium**
  Sé Gestor de Tareas o Anunciante

💾 **Almacenamiento Adicional**
  Amplía tus GB de conexión

⭐ **Recargar Estrellas**
  Compra más estrellas con Telegram Stars"""

            keyboard = [
                [InlineKeyboardButton("👑 Planes VIP", callback_data="shop_vip")],
                [InlineKeyboardButton("📋 Roles Premium", callback_data="shop_roles")],
                [InlineKeyboardButton("💾 Almacenamiento", callback_data="shop_storage")],
                [InlineKeyboardButton("⭐ Recargar Estrellas", callback_data="deposit_stars")],
                [InlineKeyboardButton("🔙 Volver", callback_data="operations")]
            ]

            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return SHOP_MENU

        except Exception as e:
            logger.error(f"Error mostrando menú de tienda: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)

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

            message = f"""✅ **Confirmar Compra**

Producto: {product_info['name']}
Costo: ⭐ {product_info['cost']}

¿Deseas proceder con la compra?"""

            keyboard = [
                [
                    InlineKeyboardButton("✅ Comprar", callback_data=f"shop_buy_{product_type}_{product_id}"),
                    InlineKeyboardButton("❌ Cancelar", callback_data="shop_menu")
                ]
            ]

            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return CONFIRMING_PURCHASE

        except Exception as e:
            logger.error(f"Error confirmando compra: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return SHOP_MENU

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
            user_info = await self.payment_service.get_user_balance(user_id)
            current_balance = user_info.get('balance_stars', 0) if user_info else 0

            if current_balance < cost:
                message = f"""❌ **Balance Insuficiente**

Balance actual: ⭐ {current_balance}
Costo del producto: ⭐ {cost}
Necesitas: ⭐ {cost - current_balance} más

Recargar estrellas con el botón de abajo."""

                keyboard = [
                    [InlineKeyboardButton("⭐ Recargar Estrellas", callback_data="deposit_stars")],
                    [InlineKeyboardButton("🔙 Volver", callback_data="shop_menu")]
                ]

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
                message = f"""✅ **Compra Exitosa**

Producto: {product_name}
Costo: ⭐ {cost}
Balance anterior: ⭐ {current_balance}
Balance nuevo: ⭐ {current_balance - cost}

{result.get('message', '')}"""

                keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="operations")]]
            else:
                message = f"""❌ **Error en la Compra**

{result.get('message', 'Error desconocido')}"""
                keyboard = [[InlineKeyboardButton("🔙 Reintentar", callback_data="shop_menu")]]

            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
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
                expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)
                
                await self.payment_service.activate_vip(user_id, expires_at)
                
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
    
    # Menú principal
    callbacks.append(
        CallbackQueryHandler(handler.shop_menu, pattern="^shop_menu$|^plan_vip$|^shop$")
    )
    
    # Planes VIP
    callbacks.append(
        CallbackQueryHandler(handler.show_vip_plans, pattern="^shop_vip$")
    )
    
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
