from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from config import settings
from utils.logger import logger

from application.services.support_service import SupportService
from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards

# Estado de la conversación
CHATTING = 1

async def start_support(update: Update, context: ContextTypes.DEFAULT_TYPE, support_service: SupportService):
    """Abre el canal de soporte y registra el ticket en la BD."""
    user = update.effective_user
    
    try:
        # Registrar o recuperar ticket abierto en Infraestructura
        await support_service.open_ticket(user_id=user.id, user_name=user.first_name)
        
        # Notificar al Admin con un mensaje que incluya el ID del usuario para facilitar el reply
        await context.bot.send_message(
            chat_id=settings.ADMIN_ID,
            text=Messages.Support.NEW_TICKET_ADMIN.format(name=user.first_name, user_id=user.id),
            parse_mode="HTML"
        )
        
        await update.message.reply_text(
            text=Messages.Support.OPEN_TICKET,
            reply_markup=InlineKeyboards.support_active(),
            parse_mode="Markdown"
        )
        return CHATTING
        
    except Exception as e:
        logger.error(f"Error al abrir ticket: {e}")
        await update.message.reply_text(Messages.Errors.GENERIC.format(error="No se pudo abrir el canal de soporte."))
        return ConversationHandler.END

async def relay_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, support_service: SupportService):
    """Reenvía mensajes al admin y actualiza la actividad del ticket."""
    user = update.effective_user
    text = update.message.text

    if text == "🔴 Finalizar Soporte":
        return await close_ticket(update, context, support_service)

    try:
        # Actualizar timestamp de actividad en la BD
        await support_service.update_activity(user.id)

        # Enviar al admin
        await context.bot.send_message(
            chat_id=settings.ADMIN_ID,
            text=Messages.Support.USER_MESSAGE_TO_ADMIN.format(name=user.first_name, text=text)
        )
    except Exception as e:
        logger.error(f"Error reenviando al admin: {e}")
        
    return CHATTING

async def close_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE, support_service: SupportService):
    """Cierra el ticket en la BD y notifica a ambas partes."""
    user_id = update.effective_user.id
    
    try:
        await support_service.close_ticket(user_id)
        
        await update.message.reply_text(
            text=Messages.Support.TICKET_CLOSED,
            reply_markup=InlineKeyboards.main_menu()
        )
        
        # Notificar al admin
        await context.bot.send_message(
            chat_id=settings.ADMIN_ID,
            text=f"🎫 Ticket del usuario {user_id} cerrado."
        )
    except Exception as e:
        logger.error(f"Error al cerrar ticket: {e}")
        
    return ConversationHandler.END

# --- LÓGICA PARA EL ADMINISTRADOR ---

async def admin_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, support_service: SupportService):
    """
    Permite al admin responder a un usuario. 
    Se activa si el mensaje del admin no es un comando y no está en una conversación propia.
    """
    # Validar que sea el admin
    if update.effective_user.id != int(settings.ADMIN_ID):
        return

    # Formato esperado para el admin: "ID_USUARIO Mensaje" o mediante Reply
    # Por ahora implementaremos por ID para mayor robustez
    try:
        parts = update.message.text.split(" ", 1)
        if len(parts) < 2: return

        target_user_id = int(parts[0])
        response_text = parts[1]

        # Enviar al usuario
        await context.bot.send_message(
            chat_id=target_user_id,
            text=Messages.Support.ADMIN_MESSAGE_TO_USER.format(text=response_text)
        )
        # Actualizar actividad del ticket
        await support_service.update_activity(target_user_id)
        
        await update.message.reply_text(f"✅ Respuesta enviada al usuario {target_user_id}")
    except (ValueError, IndexError):
        # Si no empieza con un ID, el admin quizás está hablando normal
        pass

def get_support_handler(support_service: SupportService) -> ConversationHandler:
    """Configuración del handler de soporte para main.py."""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎫 Soporte$"), lambda u, c: start_support(u, c, support_service))],
        states={
            CHATTING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               lambda u, c: relay_to_admin(u, c, support_service))
            ]
        },
        fallbacks=[
            MessageHandler(filters.Regex("^🔴 Finalizar Soporte$"),
                           lambda u, c: close_ticket(u, c, support_service)),
            MessageHandler(filters.Regex("^close_ticket$"),
                           lambda u, c: close_ticket(u, c, support_service))
        ],
    )


def get_support_callback_handler(support_service: SupportService):
    """Handler para callbacks de botones inline de soporte."""
    from telegram.ext import CallbackQueryHandler
    
    async def handle_support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "close_ticket":
            await close_ticket(update, context, support_service)
    
    return CallbackQueryHandler(handle_support_callback, pattern="^close_ticket$")
