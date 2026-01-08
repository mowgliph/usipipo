from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger
from config import settings

from application.services.vpn_service import VpnService
from telegram_bot.messages import UserMessages, CommonMessages
from telegram_bot.keyboard import UserKeyboards

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service: VpnService):
    """
    Muestra el estado general del usuario: 
    - Cantidad de llaves activas vs límite.
    - Consumo total acumulado de todas las llaves.
    - Estado de la suscripción/usuario.
    """
    telegram_id = update.effective_user.id
    user_name = update.effective_user.username or update.effective_user.first_name
    
    try:
        # Validar si es admin
        is_admin = str(telegram_id) == str(settings.ADMIN_ID)

        # Llamada al servicio para obtener el resumen del usuario
        status_data = await vpn_service.get_user_status(telegram_id)
        user_entity = status_data.get("user")
        
        # Formateamos el mensaje usando UserMessages.Status.USER_INFO 
        text = UserMessages.Status.HEADER + "\n\n" + UserMessages.Status.USER_INFO.format(
            name=user_name,
            user_id=telegram_id,
            join_date=user_entity.created_at.strftime("%Y-%m-%d") if user_entity and hasattr(user_entity, 'created_at') and user_entity.created_at else "N/A",
            status="Activo ✅" if user_entity and user_entity.is_active else "Inactivo ⚠️"
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
        except:
            is_admin = False
            
        await update.message.reply_text(
            text=CommonMessages.Errors.GENERIC.format(error="No se pudo recuperar la información de consumo."),
            reply_markup=UserKeyboards.main_menu(is_admin=is_admin)
        )
