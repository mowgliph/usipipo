# bot/handlers/proxy.py

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from sqlalchemy.ext.asyncio import AsyncSession

from database.db import AsyncSessionLocal as get_session
from services import proxy as proxy_service
from services.user import get_user_by_telegram_id
from utils.helpers import log_error_and_notify
from utils.permissions import require_registered

logger = logging.getLogger("usipipo.handlers.proxy")


@require_registered
async def proxy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /proxy handler asíncrono.
    Placeholder for future proxy implementations.
    Currently redirects to MTProto via /mtproto command.
    """
    if not update.effective_chat or not update.message or not update.effective_user:
        return

    tg_user = update.effective_user
    chat_id = update.effective_chat.id
    bot = context.bot

    async with get_session() as session:
        db_user = None
        try:
            # Obtener usuario de DB (ya verificado por decorador)
            db_user = await get_user_by_telegram_id(session, tg_user.id)
            if not db_user:
                await update.message.reply_text(
                    "❌ Error interno. No se pudo encontrar tu usuario en la base de datos."
                )
                return

            # For now, redirect to MTProto handler
            await update.message.reply_text(
                "🔄 Los proxies MTProto ahora se manejan con el comando /mtproto.\n\n"
                "Usa /mtproto para obtener la configuración del proxy MTProto compartido."
            )

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error en proxy_command: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(
                session,
                bot,
                chat_id,
                db_user.id if db_user else None,
                action="command_proxy",
                error=e,
                public_message="Ha ocurrido un error procesando /proxy. Inténtalo más tarde.",
            )


