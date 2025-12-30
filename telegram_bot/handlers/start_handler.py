from telegram import Update
from telegram.ext import ContextTypes
from application.services.vpn_service import VpnService
from telegram_bot.messages import Messages
from telegram_bot.keyboard import Keyboards

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service: VpnService):
    """Maneja el comando /start y asegura que el usuario exista en la BD."""
    user_tg = update.effective_user
    
    try:
        # El servicio se encarga de crear al usuario si no existe
        await vpn_service.get_user_status(user_tg.id)
        
        await update.message.reply_text(
            text=Messages.Welcome.START,
            reply_markup=Keyboards.main_menu(),
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(
            text=Messages.Errors.GENERIC.format(error=str(e))
        )
