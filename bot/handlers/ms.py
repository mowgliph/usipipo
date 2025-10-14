# bot/handlers/ms.py
from telegram import Update
from telegram.ext import ContextTypes
import logging

from database.db import get_session
from database.crud import users as crud_users
from services.notification import send_broadcast_message
from utils.permissions import require_admin
from utils.helpers import send_success, send_usage_error, send_generic_error, send_info

logger = logging.getLogger("usipipo.handlers.ms")

@require_admin
async def ms_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para /ms <mensaje>. Envía un mensaje a todos los usuarios activos.
    Uso: /ms Hola, este es un mensaje para todos.
    Registra la acción en AuditLog y notifica errores a admins.
    """
    if not context.args:
        await send_usage_error(update, "ms", "Hola, este es un mensaje")
        return

    message = " ".join(context.args)
    user = update.effective_user
    async with get_session() as session:
        try:
            # Obtener el ID del usuario en la DB
            db_user = await crud_users.get_user_by_telegram_id(session, user.id)
            if not db_user:
                await send_generic_error(update, "Usuario no encontrado en la base de datos.")
                return

            total_sent, errors = await send_broadcast_message(
                session=session,
                bot=context.bot,
                sender_user_id=db_user.id,
                message=message,
            )
            await send_success(
                update,
                f"Mensaje enviado a {total_sent} usuarios. Errores: {len(errors)}",
            )
            if errors:
                await send_info(update, f"Errores en envío: {len(errors)}. Revisa logs.")
        except ValueError as ve:
            await send_generic_error(update, str(ve))
        except Exception as e:
            logger.exception("Error en ms_handler", extra={"tg_id": user.id})
            await send_generic_error(update, "Error enviando mensaje. El equipo ha sido notificado.")