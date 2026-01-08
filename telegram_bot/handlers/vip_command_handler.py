"""
Handler dedicado para el comando /vip.

Muestra directamente los planes VIP disponibles utilizando el sistema de tienda.
Este handler reemplaza la funcionalidad básica de plan_vip_handler con 
la interfaz completa de planes VIP del shop.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import settings
from utils.logger import logger
from application.services.payment_service import PaymentService
from telegram_bot.messages import ShopMessages, CommonMessages


class VipCommandHandler:
    """Handler dedicado para el comando /vip."""

    def __init__(self, payment_service: PaymentService):
        """
        Inicializar el handler con el servicio de pagos.
        
        Args:
            payment_service: Servicio para gestionar pagos y balances.
        """
        self.payment_service = payment_service

    async def show_vip_plans(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Mostrar planes VIP disponibles cuando se ejecuta el comando /vip.
        
        Este método muestra la interfaz completa de planes VIP del sistema
        de tienda, incluyendo precios, beneficios y opciones de compra.
        
        Args:
            update: Objeto de actualización de Telegram.
            context: Contexto de la conversación.
        """
        user_id = update.effective_user.id
        
        try:
            # Obtener balance del usuario para mostrarlo en la interfaz
            balance = await self.payment_service.get_user_balance(user_id)
            balance = balance if balance is not None else 0

            # Mensaje con planes VIP y balance del usuario
            message = f"""👑 **Planes VIP uSipipo**

Tu Balance: ⭐ {balance}

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
  • Ahorra 30 ⭐

💎 **Beneficios VIP:**
• Acceso a {settings.VIP_PLAN_MAX_KEYS} claves VPN simultáneas
• {settings.VIP_PLAN_DATA_LIMIT_GB} GB de datos por clave
• Soporte prioritario 24/7
• Sin anuncios en la interfaz
• Acceso anticipado a nuevas funciones"""

            # Teclado con opciones de planes VIP
            keyboard = [
                [InlineKeyboardButton("1 Mes - 10⭐", callback_data="shop_vip_1month")],
                [InlineKeyboardButton("3 Meses - 27⭐", callback_data="shop_vip_3months")],
                [InlineKeyboardButton("6 Meses - 50⭐", callback_data="shop_vip_6months")],
                [InlineKeyboardButton("12 Meses - 90⭐", callback_data="shop_vip_12months")],
                [InlineKeyboardButton("⭐ Recargar Estrellas", callback_data="deposit_stars")],
                [InlineKeyboardButton("🔙 Volver al Menú", callback_data="operations")]
            ]

            await update.message.reply_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            
            logger.info(f"Usuario {user_id} solicitó planes VIP via comando /vip")

        except Exception as e:
            logger.error(f"Error mostrando planes VIP para usuario {user_id}: {e}")
            await update.message.reply_text(
                text=CommonMessages.Errors.GENERIC.format(error=str(e)),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Volver", callback_data="operations")
                ]])
            )

    async def show_vip_plans_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Mostrar planes VIP cuando se invoca desde callback del menú de tienda.
        
        Args:
            update: Objeto de actualización de Telegram con callback query.
            context: Contexto de la conversación.
        """
        query = update.callback_query
        await query.answer()
        user_id = update.effective_user.id
        
        try:
            # Obtener balance del usuario para mostrarlo en la interfaz
            balance = await self.payment_service.get_user_balance(user_id)
            balance = balance if balance is not None else 0

            # Mensaje con planes VIP y balance del usuario
            message = f"""👑 **Planes VIP uSipipo**

Tu Balance: ⭐ {balance}

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
  • Ahorra 30 ⭐

💎 **Beneficios VIP:**
• Acceso a {settings.VIP_PLAN_MAX_KEYS} claves VPN simultáneas
• {settings.VIP_PLAN_DATA_LIMIT_GB} GB de datos por clave
• Soporte prioritario 24/7
• Sin anuncios en la interfaz
• Acceso anticipado a nuevas funciones"""

            # Teclado con opciones de planes VIP
            keyboard = [
                [InlineKeyboardButton("1 Mes - 10⭐", callback_data="shop_vip_1month")],
                [InlineKeyboardButton("3 Meses - 27⭐", callback_data="shop_vip_3months")],
                [InlineKeyboardButton("6 Meses - 50⭐", callback_data="shop_vip_6months")],
                [InlineKeyboardButton("12 Meses - 90⭐", callback_data="shop_vip_12months")],
                [InlineKeyboardButton("⭐ Recargar Estrellas", callback_data="deposit_stars")],
                [InlineKeyboardButton("🔙 Volver a Tienda", callback_data="shop_menu")]
            ]

            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            
            logger.info(f"Usuario {user_id} solicitó planes VIP via callback de tienda")

        except Exception as e:
            logger.error(f"Error mostrando planes VIP para usuario {user_id}: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)


def get_vip_command_handler(payment_service: PaymentService) -> tuple:
    """
    Factory para crear una instancia del handler de comando VIP y sus callbacks.
    
    Args:
        payment_service: Servicio de pagos para el handler.
        
    Returns:
        Tupla con (handler_instance, callback_handlers_list).
    """
    handler = VipCommandHandler(payment_service)
    
    # Callback handlers para integración con el menú de tienda
    callback_handlers = [
        CallbackQueryHandler(handler.show_vip_plans_callback, pattern="^vip_plans$")
    ]
    
    return handler, callback_handlers
