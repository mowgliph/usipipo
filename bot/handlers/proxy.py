# bot/handlers/proxy.py

from __future__ import annotations

import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from sqlalchemy.ext.asyncio import AsyncSession

from database.db import AsyncSessionLocal as get_session
from services import proxy as proxy_service
from services.user import get_user_by_telegram_id
from utils.helpers import log_and_notify, log_error_and_notify
from utils.permissions import require_registered

logger = logging.getLogger("usipipo.handlers.proxy")


@require_registered
async def proxy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /proxy handler asíncrono.
    Envia configuracion de proxy MTProto gratuito para usuarios registrados.
    Verifica que el usuario esté registrado usando el decorador @require_registered.
    """
    if not update.effective_chat or not update.message or not update.effective_user:
        return

    tg_user = update.effective_user
    chat_id = update.effective_chat.id
    bot = context.bot

    async with get_session() as session:
        try:
            # Obtener usuario de DB (ya verificado por decorador)
            db_user = await get_user_by_telegram_id(session, tg_user.id)
            if not db_user:
                await update.message.reply_text(
                    "❌ Error interno. No se pudo encontrar tu usuario en la base de datos."
                )
                return

            await _handle_proxy_logic(
                session=session,
                update=update,
                bot=bot,
                db_user=db_user,
                tg_user=tg_user,
                chat_id=chat_id
            )

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error en proxy_command: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(
                session,
                bot,
                chat_id,
                db_user.id if 'db_user' in locals() and db_user else None,
                action="command_proxy",
                error=e,
                public_message="Ha ocurrido un error procesando /proxy. Intenta más tarde.",
            )


async def _handle_proxy_logic(
    session: AsyncSession,
    update: Update,
    bot,
    db_user,
    tg_user,
    chat_id
) -> None:
    """Maneja la lógica principal del comando proxy."""
    # Verificar si ya tiene un proxy activo
    existing_proxy = await proxy_service.list_user_proxies(session, db_user.id)
    active_proxies = [p for p in existing_proxy if p.status == "active"]

    if active_proxies:
        await _show_existing_proxy(update, active_proxies[0])
    else:
        await _create_new_proxy(
            session=session,
            update=update,
            bot=bot,
            db_user=db_user,
            tg_user=tg_user,
            chat_id=chat_id
        )


async def _show_existing_proxy(update: Update, proxy) -> None:
    """Muestra información del proxy existente."""
    proxy_info = await proxy_service.get_proxy_info(proxy)
    connection_string = proxy_info["connection_string"]

    keyboard = [
        [
            InlineKeyboardButton("🔄 Renovar Proxy", callback_data=f"renew_proxy_{proxy.id}"),
            InlineKeyboardButton("🗑️ Revocar Proxy", callback_data=f"revoke_proxy_{proxy.id}")
        ],
        [
            InlineKeyboardButton("📋 Mis Proxies", callback_data="list_proxies"),
            InlineKeyboardButton("❓ Ayuda", callback_data="help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🔒 <b>Ya tienes un proxy MTProto activo</b>\n\n"
        f"📍 <b>Host:</b> <code>{proxy.host}</code>\n"
        f"🔌 <b>Puerto:</b> <code>{proxy.port}</code>\n"
        f"🔑 <b>Secreto:</b> <code>{proxy.secret}</code>\n"
        f"📅 <b>Expira:</b> {proxy.expires_at.strftime('%Y-%m-%d %H:%M') if proxy.expires_at else 'Nunca'}\n\n"
        f"🔗 <b>Enlace de conexión:</b>\n<code>{connection_string}</code>\n\n"
        f"💡 <b>¿Qué deseas hacer?</b>",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def _create_new_proxy(
    session: AsyncSession,
    update: Update,
    bot,
    db_user,
    tg_user,
    chat_id
) -> None:
    """Crea un nuevo proxy gratuito."""
    try:
        new_proxy = await proxy_service.create_free_proxy_for_user(session, db_user.id, commit=True)
        if new_proxy:
            await _show_new_proxy_success(update, new_proxy)
            await _log_proxy_creation(session, bot, chat_id, db_user, new_proxy)
        else:
            await update.message.reply_text(
                "❌ No se pudo crear el proxy. Inténtalo más tarde o contacta a soporte."
            )

    except ValueError as ve:
        if str(ve) == "user_has_active_proxy":
            await update.message.reply_text(
                "❌ Ya tienes un proxy activo. Usa /proxy para verlo o revocar el existente."
            )
        else:
            await update.message.reply_text(
                "❌ Error al crear proxy. Inténtalo más tarde."
            )
    except Exception:  # pylint: disable=broad-except
        logger.exception("Error creando proxy gratuito", extra={"user_id": db_user.id, "tg_id": tg_user.id})
        await update.message.reply_text(
            "❌ Error interno al crear proxy. Inténtalo más tarde."
        )


async def _show_new_proxy_success(update: Update, new_proxy) -> None:
    """Muestra mensaje de éxito al crear nuevo proxy."""
    proxy_info = await proxy_service.get_proxy_info(new_proxy)
    connection_string = proxy_info["connection_string"]

    keyboard = [
        [
            InlineKeyboardButton("📋 Mis Proxies", callback_data="list_proxies"),
            InlineKeyboardButton("❓ Ayuda", callback_data="help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"✅ <b>¡Proxy MTProto gratuito creado!</b>\n\n"
        f"📍 <b>Host:</b> <code>{new_proxy.host}</code>\n"
        f"🔌 <b>Puerto:</b> <code>{new_proxy.port}</code>\n"
        f"🔑 <b>Secreto:</b> <code>{new_proxy.secret}</code>\n"
        f"📅 <b>Expira:</b> {new_proxy.expires_at.strftime('%Y-%m-%d %H:%M') if new_proxy.expires_at else 'Nunca'}\n\n"
        f"🔗 <b>Enlace de conexión:</b>\n<code>{connection_string}</code>\n\n"
        f"📱 <b>Instrucciones:</b>\n"
        f"1. Copia el enlace de arriba\n"
        f"2. Ábrelo en Telegram o comparte\n"
        f"3. El proxy se conectará automáticamente\n\n"
        f"⚠️ <b>Nota:</b> Este proxy es gratuito y expira en 30 días.",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def _log_proxy_creation(
    session: AsyncSession,
    bot,
    chat_id,
    db_user,
    new_proxy
) -> None:
    """Registra la creación exitosa del proxy."""
    await log_and_notify(
        session,
        bot,
        chat_id,
        db_user.id,
        action="command_proxy",
        details=f"Proxy creado: {new_proxy.id} - Host: {new_proxy.host}:{new_proxy.port}",
        message="Proxy MTProto gratuito creado",
        parse_mode="HTML",
    )