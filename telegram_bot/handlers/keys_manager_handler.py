from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from loguru import logger

from application.services.vpn_service import VpnService
from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard.keyboard import Keyboards

async def list_keys_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service: VpnService):
    """
    Lista todas las llaves del usuario. 
    Envía un mensaje independiente por cada llave con su botón de gestión.
    """
    telegram_id = update.effective_user.id
    
    try:
        status = await vpn_service.get_user_status(telegram_id)
        keys = status.get("keys", [])

        if not keys:
            await update.message.reply_text(
                text=Messages.Keys.NO_KEYS,
                reply_markup=Keyboards.main_menu()
            )
            return

        await update.message.reply_text(
            text=Messages.Keys.LIST_HEADER, 
            parse_mode="Markdown"
        )

        for key in keys:
            # Formateamos el detalle de la llave usando nuestra clase Messages
            usage_str = f"{key.used_gb:.2f} GB / {key.data_limit_gb:.2f} GB"
            text = Messages.Keys.DETAIL.format(
                name=key.name,
                type=key.key_type.upper(),
                date=key.created_at.strftime("%d/%m/%Y"),
                usage=usage_str,
                id=key.id
            )
            
            await update.message.reply_text(
                text=text,
                reply_markup=Keyboards.key_management(str(key.id)),
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Error al listar llaves: {e}")
        await update.message.reply_text(Messages.Errors.GENERIC.format(error=str(e)))

async def delete_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service: VpnService):
    """
    Manejador central para las acciones de los botones Inline (Callback Queries).
    Gestiona la confirmación, ejecución y cancelación de borrado.
    """
    query = update.callback_query
    data = query.data
    await query.answer()

    # 1. Solicitar confirmación
    if data.startswith("delete_confirm_"):
        key_id = data.replace("delete_confirm_", "")
        await query.edit_message_reply_markup(
            reply_markup=Keyboards.confirm_delete(key_id)
        )

    # 2. Ejecutar la eliminación real
    elif data.startswith("delete_execute_"):
        key_id = data.replace("delete_execute_", "")
        
        try:
            # El VpnService se encarga de borrar en la API (Outline/WG) y en DB
            success = await vpn_service.revoke_key(key_id)
            
            if success:
                await query.edit_message_text(
                    text=f"{Messages.Keys.DELETED}\n\nLa configuración ha sido revocada del servidor.",
                    reply_markup=None # Quitamos los botones
                )
            else:
                await query.edit_message_text(text="❌ Error: La llave no pudo ser eliminada o ya no existe.")
        except Exception as e:
            logger.error(f"Error al ejecutar borrado: {e}")
            await query.edit_message_text(text=Messages.Errors.GENERIC.format(error="No se pudo contactar con el servidor VPN"))

    # 3. Cancelar la operación y volver al estado inicial del mensaje
    elif data == "cancel_delete":
        # Nota: Para restaurar el botón original necesitaríamos el ID de la llave.
        # Por simplicidad y UX, informamos que se canceló.
        await query.edit_message_text(
            text="✅ Acción cancelada. La llave permanece activa.",
            reply_markup=None
        )
