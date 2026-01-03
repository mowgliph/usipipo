from telegram import Update
from telegram.ext import ContextTypes
from application.services.vpn_service import VpnService
from telegram_bot.messages import Messages
from telegram_bot.keyboard import Keyboards
from config import settings
import logging

logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service):
    """
    Maneja el comando /start y el registro de usuarios.
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    try:
        # Verificar si el usuario ya existe
        existing_user = await vpn_service.user_repository.get_user(user.id)
        
        if not existing_user:
            # Crear nuevo usuario
            await vpn_service.user_repository.create_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            welcome_message = Messages.Welcome.NEW_USER.format(name=user.first_name)
        else:
            # Usuario existente
            welcome_message = Messages.Welcome.EXISTING_USER.format(name=user.first_name)
        
        # Enviar mensaje de bienvenida con menú principal
        # Si es admin, mostrar menú con acceso de administración
        if user.id == int(settings.ADMIN_ID):
            await update.message.reply_text(
                text=welcome_message,
                reply_markup=Keyboards.admin_main_menu(),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                text=welcome_message,
                reply_markup=Keyboards.main_menu(),
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Error en start_handler: {e}")
        await update.message.reply_text(
            text=Messages.Errors.GENERIC.format(error="No se pudo procesar el registro. Intenta nuevamente.")
        )
