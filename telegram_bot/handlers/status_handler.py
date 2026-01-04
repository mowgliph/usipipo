from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from application.services.vpn_service import VpnService
from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard.keyboard import Keyboards

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service: VpnService):
    """
    Muestra el estado general del usuario: 
    - Cantidad de llaves activas vs límite.
    - Consumo total acumulado de todas las llaves.
    - Estado de la suscripción/usuario.
    """
    telegram_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    try:
        # Llamada al servicio para obtener el resumen del usuario
        status_data = await vpn_service.get_user_status(telegram_id)
        user_entity = status_data.get("user")
        keys = status_data.get("keys", [])
        
        # Calculamos el consumo total (esto asume que las entidades VpnKey 
        total_bytes = sum(getattr(key, 'used_bytes', 0) for key in keys)
        total_mb = total_bytes / (1024 * 1024) # Conversión de Bytes a Megabytes
        
        
        # Formateamos el mensaje usando Messages.Status.INFO 
        text = Messages.Status.HEADER + "\n\n" + Messages.Status.INFO.format(
            name=user_name,
            count=len(keys),
            max=user_entity.max_keys if user_entity else 5,
            usage=round(total_mb, 2),
            stars=user_entity.balance_stars if user_entity else 0,
            status="Activo ✅" if user_entity and user_entity.is_active else "Inactivo ⚠️"
        )
        
        await update.message.reply_text(
            text=text,
            reply_markup=Keyboards.main_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en status_handler: {e}")
        await update.message.reply_text(
            text=Messages.Errors.GENERIC.format(error="No se pudo recuperar la información de consumo."),
            reply_markup=Keyboards.main_menu()
        )
