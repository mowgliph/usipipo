"""
Handlers para sistema VIP de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from application.services.payment_service import PaymentService
from application.services.vpn_service import VpnService
from .messages_vip import VipMessages
from .keyboards_vip import VipKeyboards
from config import settings
from utils.logger import logger


class VipHandler:
    """Handler para sistema VIP."""
    
    def __init__(self, payment_service: PaymentService, vpn_service: VpnService = None):
        """
        Inicializa el handler VIP.
        
        Args:
            payment_service: Servicio de pagos
            vpn_service: Servicio de VPN (opcional)
        """
        self.payment_service = payment_service
        self.vpn_service = vpn_service
        logger.info("👑 VipHandler inicializado")

    async def show_vip_plans(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra los planes VIP disponibles.
        """
        user_id = update.effective_user.id
        
        try:
            # Obtener balance del usuario para mostrarlo en la interfaz
            balance = await self.payment_service.get_user_balance(user_id)
            balance = balance if balance is not None else 0
            
            # Verificar si ya es VIP
            is_vip = await self._check_vip_status(user_id)
            
            if is_vip:
                # Mostrar estado VIP actual
                vip_info = await self._get_vip_info(user_id)
                message = VipMessages.Status.ALREADY_VIP.format(
                    plan_name=vip_info.get('plan_name', 'VIP'),
                    expiry_date=vip_info.get('expiry_date', 'N/A'),
                    benefits=vip_info.get('benefits', [])
                )
                keyboard = VipKeyboards.vip_status_actions()
            else:
                # Mostrar planes disponibles
                message = VipMessages.Plans.MAIN.format(balance=balance)
                keyboard = VipKeyboards.vip_plans()
            
            await update.message.reply_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_vip_plans: {e}")
            await update.message.reply_text(
                text=VipMessages.Error.SYSTEM_ERROR,
                reply_markup=VipKeyboards.back_to_operations(),
                parse_mode="Markdown"
            )

    async def show_plan_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra detalles de un plan específico.
        """
        query = update.callback_query
        await query.answer()
        
        # Extraer plan del callback_data
        plan = query.data.replace("vip_plan_", "")
        user_id = update.effective_user.id
        
        try:
            # Obtener información del plan
            plan_info = await self._get_plan_info(plan)
            
            if not plan_info:
                message = VipMessages.Error.PLAN_NOT_FOUND
                keyboard = VipKeyboards.back_to_plans()
            else:
                message = VipMessages.Plans.DETAILS.format(
                    plan_name=plan_info['name'],
                    price=plan_info['price'],
                    duration=plan_info['duration'],
                    features='\n'.join(f"• {feature}" for feature in plan_info['features']),
                    benefits='\n'.join(f"🎁 {benefit}" for benefit in plan_info['benefits'])
                )
                keyboard = VipKeyboards.plan_actions(plan, plan_info['price'])
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_plan_details: {e}")
            await query.edit_message_text(
                text=VipMessages.Error.SYSTEM_ERROR,
                reply_markup=VipKeyboards.back_to_plans(),
                parse_mode="Markdown"
            )

    async def process_vip_purchase(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Procesa la compra de un plan VIP.
        """
        query = update.callback_query
        await query.answer()
        
        # Extraer plan y precio del callback_data
        callback_parts = query.data.split("_")
        plan = callback_parts[2]
        price = float(callback_parts[3])
        user_id = update.effective_user.id
        
        try:
            # Verificar balance
            balance = await self.payment_service.get_user_balance(user_id)
            
            if balance < price:
                message = VipMessages.Payment.INSUFFICIENT_BALANCE.format(
                    current_balance=balance,
                    required=price,
                    missing=price - balance
                )
                keyboard = VipKeyboards.payment_options(plan, price)
            else:
                # Procesar pago
                success = await self._process_vip_payment(user_id, plan, price)
                
                if success:
                    message = VipMessages.Payment.SUCCESS.format(
                        plan_name=plan.title(),
                        price=price,
                        new_balance=balance - price
                    )
                    keyboard = VipKeyboards.vip_activated()
                else:
                    message = VipMessages.Payment.FAILED
                    keyboard = VipKeyboards.back_to_plans()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en process_vip_purchase: {e}")
            await query.edit_message_text(
                text=VipMessages.Error.SYSTEM_ERROR,
                reply_markup=VipKeyboards.back_to_plans(),
                parse_mode="Markdown"
            )

    async def show_vip_benefits(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra los beneficios VIP del usuario.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            vip_info = await self._get_vip_info(user_id)
            
            if not vip_info:
                message = VipMessages.Status.NOT_VIP
                keyboard = VipKeyboards.upgrade_to_vip()
            else:
                message = VipMessages.Benefits.ACTIVE.format(
                    plan_name=vip_info.get('plan_name', 'VIP'),
                    remaining_days=vip_info.get('remaining_days', 0),
                    benefits='\n'.join(f"🎁 {benefit}" for benefit in vip_info.get('benefits', [])),
                    usage_stats=vip_info.get('usage_stats', {})
                )
                keyboard = VipKeyboards.vip_benefits_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_vip_benefits: {e}")
            await query.edit_message_text(
                text=VipMessages.Error.SYSTEM_ERROR,
                reply_markup=VipKeyboards.back_to_operations(),
                parse_mode="Markdown"
            )

    async def extend_vip_membership(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Extiende la membresía VIP.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Mostrar opciones de extensión
            message = VipMessages.Extension.EXTENSION_OPTIONS
            keyboard = VipKeyboards.extension_options()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en extend_vip_membership: {e}")
            await query.edit_message_text(
                text=VipMessages.Error.SYSTEM_ERROR,
                reply_markup=VipKeyboards.back_to_operations(),
                parse_mode="Markdown"
            )

    # Métodos privados
    async def _check_vip_status(self, user_id: int) -> bool:
        """Verifica si el usuario es VIP."""
        try:
            if self.vpn_service:
                user_status = await self.vpn_service.get_user_status(user_id)
                user = user_status.get("user")
                return user.is_vip if user else False
            return False
        except Exception:
            return False

    async def _get_vip_info(self, user_id: int) -> dict:
        """Obtiene información VIP del usuario."""
        try:
            if self.vpn_service:
                user_status = await self.vpn_service.get_user_status(user_id)
                user = user_status.get("user")
                if user and user.is_vip:
                    return {
                        'plan_name': getattr(user, 'vip_plan', 'VIP'),
                        'expiry_date': getattr(user, 'vip_expiry', 'N/A'),
                        'benefits': getattr(user, 'vip_benefits', []),
                        'remaining_days': getattr(user, 'vip_days_left', 0),
                        'usage_stats': {}
                    }
            return {}
        except Exception:
            return {}

    async def _get_plan_info(self, plan: str) -> dict:
        """Obtiene información de un plan."""
        plans = {
            'basic': {
                'name': 'Plan Básico',
                'price': 9.99,
                'duration': '1 mes',
                'features': ['Llaves VPN ilimitadas', '100 GB por llave', 'Soporte prioritario'],
                'benefits': ['Acceso a servidores básicos', 'Sin límites de velocidad', 'Backup automático']
            },
            'premium': {
                'name': 'Plan Premium',
                'price': 19.99,
                'duration': '1 mes',
                'features': ['Todo Básico +', '500 GB por llave', 'Servidores dedicados', 'Sin límites de velocidad'],
                'benefits': ['Acceso a todos los servidores', 'Soporte 24/7', 'Backup en la nube', 'Prioridad máxima']
            },
            'elite': {
                'name': 'Plan Elite',
                'price': 39.99,
                'duration': '1 mes',
                'features': ['Todo Premium +', 'Datos ilimitados', 'Todos los servidores', 'Soporte exclusivo'],
                'benefits': ['Cuenta personal dedicada', 'Acceso beta features', 'Eventos exclusivos', 'Regalos mensuales']
            }
        }
        return plans.get(plan.lower())

    async def _process_vip_payment(self, user_id: int, plan: str, price: float) -> bool:
        """Procesa el pago VIP."""
        try:
            # Aquí iría la lógica real de procesamiento de pago
            # Por ahora, simulamos el proceso
            balance = await self.payment_service.get_user_balance(user_id)
            
            if balance >= price:
                # Descontar balance
                await self.payment_service.deduct_balance(user_id, price)
                
                # Activar VIP (simulado)
                await self._activate_vip(user_id, plan)
                
                return True
            return False
        except Exception as e:
            logger.error(f"Error procesando pago VIP: {e}")
            return False

    async def _activate_vip(self, user_id: int, plan: str):
        """Activa la membresía VIP."""
        # Aquí iría la lógica real de activación VIP
        # Por ahora, solo registramos el log
        logger.info(f"VIP activado para usuario {user_id}, plan: {plan}")


def get_vip_handlers(payment_service: PaymentService, vpn_service: VpnService = None):
    """
    Retorna los handlers VIP.
    
    Args:
        payment_service: Servicio de pagos
        vpn_service: Servicio de VPN (opcional)
        
    Returns:
        list: Lista de handlers
    """
    handler = VipHandler(payment_service, vpn_service)
    
    return [
        MessageHandler(filters.Regex("^👑 Plan VIP$"), handler.show_vip_plans),
        CommandHandler("vip", handler.show_vip_plans),
    ]


def get_vip_callback_handlers(payment_service: PaymentService, vpn_service: VpnService = None):
    """
    Retorna los handlers de callbacks VIP.
    
    Args:
        payment_service: Servicio de pagos
        vpn_service: Servicio de VPN (opcional)
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = VipHandler(payment_service, vpn_service)
    
    return [
        CallbackQueryHandler(handler.show_plan_details, pattern="^vip_plan_"),
        CallbackQueryHandler(handler.process_vip_purchase, pattern="^vip_buy_"),
        CallbackQueryHandler(handler.show_vip_benefits, pattern="^vip_benefits$"),
        CallbackQueryHandler(handler.extend_vip_membership, pattern="^vip_extend$"),
    ]
