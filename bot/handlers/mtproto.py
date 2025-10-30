# bot/handlers/mtproto.py

from __future__ import annotations

import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from sqlalchemy.ext.asyncio import AsyncSession

from database.db import AsyncSessionLocal as get_session
from services.user import get_user_by_telegram_id
from utils.helpers import log_and_notify, log_error_and_notify
from utils.permissions import require_registered
from config import config

logger = logging.getLogger("usipipo.handlers.mtproto")


@require_registered
async def mtproto_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /mtproto handler asíncrono.
    Envia configuracion de proxy MTProto compartido para usuarios registrados.
    Verifica que el usuario esté registrado usando el decorador @require_registered.
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

            await _handle_mtproto_logic(
                session=session,
                update=update,
                bot=bot,
                db_user=db_user,
                tg_user=tg_user,
                chat_id=chat_id
            )

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error en mtproto_command: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(
                session,
                bot,
                chat_id,
                db_user.id if db_user else None,
                action="command_mtproto",
                error=e,
                public_message="Ha ocurrido un error procesando /mtproto. Inténtalo más tarde.",
            )


async def _handle_mtproto_logic(
    session: AsyncSession,
    update: Update,
    bot,
    db_user,
    tg_user,
    chat_id
) -> None:
    """Maneja la lógica principal del comando MTProto."""
    # MTProto usa configuración compartida, no proxies por usuario
    # Mostrar siempre la configuración MTProto compartida
    await _show_mtproto_config(update, session, db_user, bot, chat_id)


async def _show_mtproto_config(update: Update, session: AsyncSession, db_user, bot, chat_id) -> None:
    """Muestra la configuración MTProto compartida."""
    if not update.message:
        return

    try:

        if not config.MTPROXY_HOST or not config.MTPROXY_PORT or not config.MTPROXY_SECRET:
            await update.message.reply_text(
                "❌ El servicio MTProto no está configurado correctamente. Contacta a soporte."
            )
            return

        # Generar enlace de conexión
        connection_string = f"tg://proxy?server={config.MTPROXY_HOST}&port={config.MTPROXY_PORT}&secret={config.MTPROXY_SECRET}"

        keyboard = [
            [
                InlineKeyboardButton("📋 Mis Proxys", callback_data="list_proxys"),
                InlineKeyboardButton("❓ Ayuda", callback_data="help")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = (
            f"🔒 <b>Proxy MTProto Compartido</b>\n\n"
            f"📍 <b>Host:</b> <code>{config.MTPROXY_HOST}</code>\n"
            f"🔌 <b>Puerto:</b> <code>{config.MTPROXY_PORT}</code>\n"
            f"🔑 <b>Secreto:</b> <code>{config.MTPROXY_SECRET}</code>\n\n"
            f"🔗 <b>Enlace de conexión:</b>\n<code>{connection_string}</code>\n\n"
            f"📱 <b>Instrucciones:</b>\n"
            f"1. Copia el enlace de arriba\n"
            f"2. Ábrelo en Telegram o comparte\n"
            f"3. El proxy se conectará automáticamente\n\n"
            f"⚠️ <b>Nota:</b> Este proxy es compartido por todos los usuarios registrados."
        )

        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

        # Log del acceso al proxy
        await log_and_notify(
            session,
            bot,
            chat_id,
            db_user.id,
            action="command_mtproto",
            details=f"MTProto config accessed - Host: {config.MTPROXY_HOST}:{config.MTPROXY_PORT}",
            message="Configuración MTProto compartida accedida",
            parse_mode="HTML",
        )

    except Exception as e:
        logger.exception("Error mostrando configuración MTProto", extra={"user_id": db_user.id})
        await update.message.reply_text(
            "❌ Error interno al obtener configuración MTProto. Inténtalo más tarde."
        )


__all__ = [
    "mtproto_command",
    "_handle_mtproto_logic",
    "_show_mtproto_config",
]