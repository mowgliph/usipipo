from telegram import Update
from telegram.ext import ContextTypes
from application.services.vpn_service import VpnService
from application.services.achievement_service import AchievementService
from telegram_bot.messages import Messages
from telegram_bot.keyboard import InlineKeyboards, Keyboards
from config import settings
from loguru import logger
from telegram import ReplyKeyboardRemove
from utils.spinner import registration_spinner


@registration_spinner
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service: VpnService):
    """
    Maneja el comando /start y el registro de usuarios.
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    try:
        # Verificar si el usuario ya existe - usar get_by_id (método garantizado)
        existing_user = await vpn_service.user_repo.get_by_id(user.id)
        
        if not existing_user:
            # Construir full_name a partir de first_name y last_name
            full_name = user.first_name or ""
            if user.last_name:
                full_name = f"{full_name} {user.last_name}".strip()
            
            # Crear nuevo usuario con los parámetros CORRECTOS
            await vpn_service.user_repo.create_user(
                user_id=user.id,
                username=user.username,
                full_name=full_name  # CORREGIDO: era first_name y last_name
            )
            welcome_message = Messages.Welcome.NEW_USER.format(name=user.first_name)
            
            # Inicializar logros para nuevo usuario
            try:
                from application.services.common.container import get_container
                
                container = get_container()
                achievement_service = container.resolve(AchievementService)
                
                await achievement_service.initialize_user_achievements(user.id)
                logger.info(f"Logros inicializados para nuevo usuario {user.id}")
            except Exception as e:
                logger.error(f"Error inicializando logros para usuario {user.id}: {e}")
                # No fallar el registro si hay error en logros
        else:
            # Usuario existente - actualizar actividad diaria
            try:
                from application.services.common.container import get_container
                
                container = get_container()
                achievement_service = container.resolve(AchievementService)
                
                # CORREGIDO: user.id en lugar de user_id (variable no definida)
                await achievement_service.update_user_stats(user.id, {'daily_activity': True})
                logger.info(f"Actividad diaria actualizada para usuario {user.id}")
            except Exception as e:
                logger.error(f"Error actualizando actividad diaria para usuario {user.id}: {e}")
                # No fallar si hay error en logros
            
            welcome_message = Messages.Welcome.EXISTING_USER.format(name=user.first_name)
        
        # Enviar mensaje de bienvenida con botón de respaldo
        # Primero limpiar cualquier menú keyboard antiguo y luego mostrar el botón "📋 Mostrar Menú"
        await update.message.reply_text(
            text=welcome_message,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        
        # Enviar segundo mensaje con el botón de respaldo
        await update.message.reply_text(
            text="📋 Presiona el botón para mostrar el menú principal:",
            reply_markup=Keyboards.show_menu_button()
        )
        
            
    except Exception as e:
        logger.error(f"Error en start_handler: {e}")
        await update.message.reply_text(
            text=Messages.Errors.GENERIC.format(error="No se pudo procesar el registro. Intenta nuevamente.")
        )
