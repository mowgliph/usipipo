from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from utils.logger import logger

from application.services.vpn_service import VpnService
from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard import UserKeyboards
from utils.spinner import with_spinner, vpn_spinner

async def list_keys_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service: VpnService):
    """
    DEPRECATED: Lista todas las llaves del usuario.
    REDIRIGIDO AL SISTEMA DE SUBMENÚS para mejor organización por servidor.
    """
    # Redirigir al nuevo sistema de submenús
    from telegram_bot.handlers.key_submenu_handler import get_key_submenu_handler
    key_submenu_handler = get_key_submenu_handler(vpn_service)
    
    # Usar el handler directamente
    await key_submenu_handler.show_key_submenu(update, context)

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
            reply_markup=UserKeyboards.confirm_delete(key_id)
        )

    # 2. Ejecutar la eliminación real
    elif data.startswith("delete_execute_"):
        key_id = data.replace("delete_execute_", "")
        
        @vpn_spinner
        async def execute_delete():
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
        
        await execute_delete()

    # 3. Cancelar la operación y volver al estado inicial del mensaje
    elif data == "cancel_delete":
        # Nota: Para restaurar el botón original necesitaríamos el ID de la llave.
        # Por simplicidad y UX, informamos que se canceló.
        await query.edit_message_text(
            text="✅ Acción cancelada. La llave permanece activa.",
            reply_markup=None
        )
