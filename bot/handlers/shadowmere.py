# bot/handlers/shadowmere.py

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from sqlalchemy.ext.asyncio import AsyncSession

from database.db import AsyncSessionLocal as get_session
from services.shadowmere import ShadowmereService
from utils.helpers import log_and_notify, log_error_and_notify

logger = logging.getLogger("usipipo.handlers.shadowmere")


async def shadowmere_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler asíncrono para comandos /shadowmere y /proxys.
    Muestra los últimos 10 proxies funcionando detectados por Shadowmere.
    """
    if not update.effective_chat or not update.message or not update.effective_user:
        return

    tg_user = update.effective_user
    chat_id = update.effective_chat.id
    bot = context.bot

    async with get_session() as session:
        try:
            await _handle_shadowmere_logic(session, update, bot, tg_user, chat_id)

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error en shadowmere_handler: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(
                session,
                bot,
                chat_id,
                None,  # No hay db_user específico
                action="command_shadowmere",
                error=e,
                public_message="Ha ocurrido un error obteniendo proxies de Shadowmere. Intenta más tarde.",
            )


async def _handle_shadowmere_logic(
    session: AsyncSession,
    update: Update,
    bot,
    tg_user,
    chat_id
) -> None:
    """Maneja la lógica principal del comando shadowmere."""
    try:
        # Obtener texto formateado de proxies
        proxies_text = await get_shadowmere_proxies_text(session, limit=10)

        # Enviar mensaje con proxies
        await update.message.reply_text(
            proxies_text,
            parse_mode="HTML"
        )

        # Log de éxito
        await log_and_notify(
            session,
            bot,
            chat_id,
            None,  # No hay db_user específico
            action="command_shadowmere",
            details="Proxies de Shadowmere mostrados exitosamente",
            message="Comando /shadowmere ejecutado",
            parse_mode="HTML",
        )

    except Exception as e:
        logger.exception("Error obteniendo proxies de Shadowmere", extra={"tg_id": tg_user.id})
        await update.message.reply_text(
            "❌ Error obteniendo proxies de Shadowmere. El servicio podría no estar disponible."
        )
        raise


async def get_shadowmere_proxies_text(session: AsyncSession, limit: int = 10) -> str:
    """
    Obtiene los proxies de Shadowmere y los formatea como texto HTML para Telegram.

    Args:
        session: Sesión async de SQLAlchemy
        limit: Número máximo de proxies a retornar (default: 10)

    Returns:
        Texto formateado en HTML con la lista de proxies

    Raises:
        RuntimeError: Si hay error obteniendo proxies
    """
    try:
        # Inicializar servicio Shadowmere (necesita configuración)
        # Nota: En producción, la configuración debería venir de settings
        shadowmere_service = ShadowmereService(
            shadowmere_api_url="http://localhost",  # Configuración por defecto
            shadowmere_port=8080
        )

        # Obtener top proxies funcionando
        proxies = await shadowmere_service.get_top_working_proxies(session, limit=limit)

        if not proxies:
            return (
                "🔍 <b>Proxies Shadowmere</b>\n\n"
                "❌ No hay proxies funcionando disponibles en este momento.\n"
                "El servicio Shadowmere podría no estar configurado o no tener datos."
            )

        # Construir mensaje HTML
        message_parts = [
            "🔍 <b>Proxies Shadowmere - Top 10 Funcionando</b>\n\n"
        ]

        for i, proxy in enumerate(proxies, 1):
            # Formatear información del proxy
            proxy_type = proxy.proxy_type.upper()
            proxy_address = proxy.proxy_address
            country = proxy.country or "Desconocido"
            response_time = ".1f" if proxy.response_time else "N/A"

            # Emoji según tipo
            type_emoji = {
                "SOCKS5": "🧦",
                "SOCKS4": "🧦",
                "HTTP": "🌐",
                "HTTPS": "🔒"
            }.get(proxy_type, "❓")

            message_parts.append(
                f"{i}. {type_emoji} <code>{proxy_address}</code>\n"
                f"   📍 País: {country}\n"
                f"   ⚡ Tiempo: {response_time} ms\n"
            )

        # Agregar estadísticas básicas
        try:
            stats = await shadowmere_service.get_proxy_stats(session)
            message_parts.append(
                f"\n📊 <b>Estadísticas:</b>\n"
                f"• Total: {stats['total']}\n"
                f"• Funcionando: {stats['working']}\n"
                f"• No funcionando: {stats['not_working']}\n"
            )
        except Exception as e:
            logger.warning("Error obteniendo estadísticas de proxies", extra={"error": str(e)})

        message_parts.append(
            "\n💡 <i>Estos proxies son detectados automáticamente por Shadowmere</i>"
        )

        return "".join(message_parts)

    except Exception as e:
        logger.exception("Error formateando texto de proxies Shadowmere")
        raise RuntimeError(f"Error obteniendo proxies: {e}") from e


# Alias para el comando /proxys
async def proxys_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Alias para shadowmere_handler con comando /proxys."""
    await shadowmere_handler(update, context)


__all__ = [
    "shadowmere_handler",
    "proxys_handler",
    "get_shadowmere_proxies_text",
]