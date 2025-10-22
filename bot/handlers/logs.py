# bot/handlers/logs.py

from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from database.db import AsyncSessionLocal as get_session
from database.crud import logs as crud_logs, users as crud_users
from services.audit import audit_service
from utils.helpers import (
    log_error_and_notify,
    log_and_notify,
    safe_chat_id_from_update,
    send_usage_error,
    format_log_entry
)
from utils.permissions import require_registered, require_superadmin

logger = logging.getLogger("usipipo.handlers.logs")


async def parse_limit_page(context: ContextTypes.DEFAULT_TYPE, default_limit: int = 10, max_limit: int = 50) -> tuple[int, int]:
    """Parse limit and page from context args."""
    try:
        limit = min(int(context.args[0]) if len(context.args) > 0 and context.args[0].isdigit() else default_limit, max_limit)
        page = max(1, int(context.args[1])) if len(context.args) > 1 and context.args[1].isdigit() else 1
    except (ValueError, IndexError):
        raise ValueError("Invalid arguments")
    return limit, page

@require_superadmin
async def get_user_id_for_command(update: Update, session: AsyncSession) -> Optional[str]:
    """Get user ID and check permissions."""
    user = await get_user_by_telegram_id(session, update.effective_user.id) if update.effective_user else None
    if not user:
        await update.message.reply_text(
            "🔐 Para ver tus registros de actividad, primero debes registrarte.\n\n"
            "Usa el comando /register para crear tu cuenta y luego podrás ver tus registros con /mylogs",
            parse_mode="HTML"
        )
        return None
    if not user.is_superadmin:
        await update.message.reply_text(
            "⚠️ Solo los administradores pueden ver los registros globales.\n\n"
            "Puedes ver tus propios registros con /mylogs",
            parse_mode="HTML"
        )
        return None
    return user.id


async def get_formatted_logs(limit: int, page: int, user_id: Optional[str] = None) -> tuple[Optional[List[str]], int]:
    """Get and format logs."""
    logs_result = await audit_service.get_logs(limit=limit, offset=(page - 1) * limit, user_id=user_id)
    if not logs_result["ok"]:
        raise Exception("Error obteniendo logs desde service")
    logs = logs_result["data"]["items"]
    total = logs_result["data"]["total"]
    if not logs:
        return None, total
    log_entries = [format_log_entry(log) for log in logs]
    return log_entries, total


async def send_logs_in_chunks(update: Update, log_entries: List[str], total: int, page: int, title: str):
    """Send logs in chunks to avoid long messages."""
    chunk_size = 5
    for i in range(0, len(log_entries), chunk_size):
        chunk = log_entries[i:i + chunk_size]
        message = (
            f"{title}\n\n" +
            "\n\n".join(chunk) +
            f"\n\n📊 Página {page} | Mostrando {len(log_entries)} de {total} registros"
        )
        await update.message.reply_text(
            message,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Muestra los registros de auditoría globales.
    Si el usuario no está registrado, le indica cómo registrarse.
    Uso: /logs [limit=10] [page=1]
    """
    bot = context.bot
    chat_id = safe_chat_id_from_update(update)
    if not chat_id:
        logger.error("No chat_id en update", extra={"user_id": None})
        return
    
    # Verificar si el usuario está registrado
    async with get_session() as session:
        try:
            user_id_str = await get_user_id_for_command(update, session)
            if not user_id_str:
                return
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in logs_command auth check: %s", type(e).__name__, extra={"tg_id": update.effective_user.id if update.effective_user else None})
            await log_error_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=user_id_str,
                action="logs_command_auth_check",
                error=e,
                public_message="❌ Error al verificar permisos."
            )
            return

    # Procesar argumentos
    try:
        limit, page = await parse_limit_page(context, default_limit=10, max_limit=50)
    except ValueError:
        await send_usage_error(update, "logs", "[limit=10] [page=1]")
        return

    async with AsyncSessionLocal() as session:
        try:
            log_entries, total = await get_formatted_logs(limit, page)
            if log_entries is None:
                await update.message.reply_text(
                    "📭 No hay registros de auditoría disponibles.",
                    parse_mode="HTML"
                )
                return

            await send_logs_in_chunks(update, log_entries, total, page, "📜 <b>Registros de Auditoría</b>")

            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=user_id_str,
                action="admin.logs",
                details=f"Consultó {len(log_entries)} registros de auditoría (página {page})",
                message=f"✅ Se han consultado {len(log_entries)} registros de auditoría."
            )

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in logs_command: %s", type(e).__name__, extra={"tg_id": update.effective_user.id if update.effective_user else None})
            await log_error_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=user_id_str,
                action="admin.logs_error",
                error=e,
                public_message="❌ Error al obtener los registros de auditoría."
            )

@require_registered
async def mylogs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Muestra los registros de auditoría del usuario actual.
    Uso: /mylogs [limit=10] [page=1]
    """
    bot = context.bot
    chat_id = safe_chat_id_from_update(update)
    if not chat_id:
        logger.error("No chat_id en update", extra={"user_id": None})
        return

    user_id_str = str(update.effective_user.id) if update.effective_user else None

    # Procesar argumentos
    try:
        limit, page = await parse_limit_page(context, default_limit=10, max_limit=20)
    except ValueError:
        await send_usage_error(update, "mylogs", "[limit=10] [page=1]")
        return

    async with AsyncSessionLocal() as session:
        try:
            # Obtener usuario
            user = await get_user_by_telegram_id(session, update.effective_user.id)
            if not user:
                await update.message.reply_text(
                    "❌ Usuario no encontrado. Por favor, regístrate primero.",
                    parse_mode="HTML"
                )
                return

            user_id_str = user.id

            log_entries, total = await get_formatted_logs(limit, page, user_id_str)
            if log_entries is None:
                await update.message.reply_text(
                    "📭 No tienes registros de auditoría.",
                    parse_mode="HTML"
                )
                return

            await send_logs_in_chunks(update, log_entries, total, page, "📋 <b>Tus Registros de Actividad</b>")

            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=user_id_str,
                action="user.mylogs",
                details=f"Consultó sus registros de auditoría (página {page})",
                message=f"✅ Se han consultado tus registros de auditoría."
            )

        except Exception as e:
            logger.exception("Error in mylogs_command: %s", type(e).__name__, extra={"tg_id": update.effective_user.id if update.effective_user else None})
            await log_error_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=user_id_str,
                action="user.mylogs_error",
                error=e,
                public_message="❌ Error al obtener tus registros de actividad."
            )

def register_logs_handlers(app) -> None:
    """Registra los manejadores de comandos de logs."""
    app.add_handler(CommandHandler("logs", logs_command))
    app.add_handler(CommandHandler("mylogs", mylogs_command))
