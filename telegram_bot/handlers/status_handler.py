from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger
from config import settings
from datetime import datetime

from application.services.vpn_service import VpnService
from application.services.admin_service import AdminService
from telegram_bot.messages import UserMessages, CommonMessages, AdminMessages
from telegram_bot.keyboard import UserKeyboards

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service: VpnService, admin_service: Optional[AdminService] = None):
    """
    Muestra el estado general del usuario o estadísticas administrativas:
    - Para usuarios regulares: estado de llaves y consumo.
    - Para administradores: panel de control con estadísticas completas.
    """
    telegram_id = update.effective_user.id
    user_name = update.effective_user.username or update.effective_user.first_name
    
    try:
        # Validar si es admin
        is_admin = str(telegram_id) == str(settings.ADMIN_ID)
        
        if is_admin and admin_service:
            # Mostrar panel de control administrativo usando el servicio inyectado
            stats = await admin_service.get_dashboard_stats()
            text = _format_admin_dashboard(user_name, stats)
        else:
            # Mostrar estado de usuario regular
            status_data = await vpn_service.get_user_status(telegram_id)
            user_entity = status_data.get("user")
            
            # Formatear fecha de unión
            join_date = "N/A"
            if user_entity and hasattr(user_entity, 'created_at') and user_entity.created_at:
                join_date = user_entity.created_at.strftime("%Y-%m-%d")
                
            # Determinar estado
            status_text = "Inactivo ⚠️"
            if user_entity and (getattr(user_entity, 'is_active', False) or getattr(user_entity, 'status', None) == 'active'):
                status_text = "Activo ✅"
            
            text = UserMessages.Status.HEADER + "\n\n" + UserMessages.Status.USER_INFO.format(
                name=user_name,
                user_id=telegram_id,
                join_date=join_date,
                status=status_text
            )
        
        await update.message.reply_text(
            text=text,
            reply_markup=UserKeyboards.main_menu(is_admin=is_admin),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en status_handler: {e}")
        # Intentamos obtener is_admin de forma segura en caso de error
        try:
            is_admin = str(telegram_id) == str(settings.ADMIN_ID)
        except (ValueError, TypeError):
            is_admin = False
         
        await update.message.reply_text(
            text=CommonMessages.Errors.GENERIC.format(error="No se pudo recuperar la información."),
            reply_markup=UserKeyboards.main_menu(is_admin=is_admin)
        )

def _format_admin_dashboard(admin_name: str, stats: dict) -> str:
    """
    Formatea los datos del dashboard administrativo usando la plantilla de mensajes.
    """
    try:
        return AdminMessages.Statistics.ADMIN_DASHBOARD.format(
            admin_name=admin_name,
            current_date=stats.get('generated_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            total_users=stats.get('total_users', 0),
            active_users=stats.get('active_users', 0),
            vip_users=stats.get('vip_users', 0),
            active_keys=stats.get('active_keys', 0),
            total_usage=stats.get('total_usage_gb', 0),
            total_revenue=stats.get('total_revenue', "0.00"),
            avg_usage=stats.get('avg_usage_gb', 0),
            new_users_today=stats.get('new_users_today', 0),
            keys_created_today=stats.get('keys_created_today', 0),
            wireguard_keys=stats.get('wireguard_keys', 0),
            wireguard_pct=stats.get('wireguard_pct', 0),
            outline_keys=stats.get('outline_keys', 0),
            outline_pct=stats.get('outline_pct', 0),
            response_time="150",  # Placeholder
            uptime="99.9",  # Placeholder
            server_status=stats.get('server_status_text', "Desconocido")
        )
    except Exception as e:
        logger.error(f"Error formateando dashboard: {e}")
        return f"❌ Error al generar visualización: {str(e)}"
