# bot/handlers/logs.py

from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import AsyncSessionLocal
from database.crud import logs as crud_logs, users as crud_users
from utils.helpers import (
    log_error_and_notify,
    log_and_notify,
    safe_chat_id_from_update,
    send_usage_error,
    notify_admins,
    format_log_entry
)
from utils.permissions import require_superadmin, require_registered

logger = logging.getLogger("usipipo.handlers.logs")

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
    async with AsyncSessionLocal() as session:
        try:
            user = await crud_users.get_user_by_telegram_id(session, update.effective_user.id) if update.effective_user else None
            if not user:
                await update.message.reply_text(
                    "🔐 Para ver tus registros de actividad, primero debes registrarte.\n\n"
                    "Usa el comando /register para crear tu cuenta y luego podrás ver tus registros con /mylogs"
                )
                return
                
            # Verificar si es superadmin
            if not user.is_superadmin:
                await update.message.reply_text(
                    "⚠️ Solo los administradores pueden ver los registros globales.\n\n"
                    f"Puedes ver tus propios registros con /mylogs"
                )
                return
                
        except Exception as e:
            await log_error_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=update.effective_user.id if update.effective_user else None,
                action="logs_command_auth_check",
                error=e,
                public_message="❌ Error al verificar permisos."
            )
            return

    # Procesar argumentos
    try:
        limit = min(int(context.args[0]) if len(context.args) > 0 and context.args[0].isdigit() else 10, 50)
        page = max(1, int(context.args[1])) if len(context.args) > 1 and context.args[1].isdigit() else 1
    except (ValueError, IndexError):
        await send_usage_error(update, "logs", "[limit=10] [page=1]")
        return

    async with AsyncSessionLocal() as session:
        try:
            # Obtener logs
            logs = await crud_logs.get_audit_logs(
                session=session,
                limit=limit,
                offset=(page - 1) * limit
            )
            
            total = await crud_logs.count_audit_logs(session)
            
            if not logs:
                await update.message.reply_text(
                    "📭 No hay registros de auditoría disponibles.",
                    parse_mode="HTML"
                )
                return
            
            # Formatear logs
            log_entries = [format_log_entry(log) for log in logs]
            
            # Enviar en chunks para evitar mensajes demasiado largos
            chunk_size = 5
            for i in range(0, len(log_entries), chunk_size):
                chunk = log_entries[i:i + chunk_size]
                message = (
                    "📜 <b>Registros de Auditoría</b>\n\n" +
                    "\n\n".join(chunk) +
                    f"\n\n📊 Página {page} | Mostrando {len(log_entries)} de {total} registros"
                )
                await update.message.reply_text(
                    message,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
            
            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=update.effective_user.id if update.effective_user else None,
                action="admin.logs",
                details=f"Consultó {len(log_entries)} registros de auditoría (página {page})",
                message=f"✅ Se han consultado {len(log_entries)} registros de auditoría."
            )
            
        except Exception as e:
            await log_error_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=update.effective_user.id if update.effective_user else None,
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

    # Procesar argumentos
    try:
        limit = min(int(context.args[0]) if len(context.args) > 0 and context.args[0].isdigit() else 10, 20)
        page = max(1, int(context.args[1])) if len(context.args) > 1 and context.args[1].isdigit() else 1
    except (ValueError, IndexError):
        await send_usage_error(update, "mylogs", "[limit=10] [page=1]")
        return

    async with AsyncSessionLocal() as session:
        try:
            # Obtener usuario
            user = await crud_users.get_user_by_telegram_id(session, update.effective_user.id)
            if not user:
                await update.message.reply_text(
                    "❌ Usuario no encontrado. Por favor, regístrate primero.",
                    parse_mode="HTML"
                )
                return
            
            # Obtener logs del usuario
            logs = await crud_logs.get_audit_logs(
                session=session,
                user_id=user.id,
                limit=limit,
                offset=(page - 1) * limit
            )
            
            total = await crud_logs.count_audit_logs(session, user_id=user.id)
            
            if not logs:
                await update.message.reply_text(
                    "📭 No tienes registros de auditoría.",
                    parse_mode="HTML"
                )
                return
            
            # Formatear logs
            log_entries = [format_log_entry(log) for log in logs]
            
            # Enviar en chunks para evitar mensajes demasiado largos
            chunk_size = 5
            for i in range(0, len(log_entries), chunk_size):
                chunk = log_entries[i:i + chunk_size]
                message = (
                    "📋 <b>Tus Registros de Actividad</b>\n\n" +
                    "\n\n".join(chunk) +
                    f"\n\n📊 Página {page} | Mostrando {len(log_entries)} de {total} registros"
                )
                await update.message.reply_text(
                    message,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
            
            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=user.id,
                action="user.mylogs",
                details=f"Consultó sus registros de auditoría (página {page})",
                message=f"✅ Se han consultado tus registros de auditoría."
            )
            
        except Exception as e:
            await log_error_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=update.effective_user.id if update.effective_user else None,
                action="user.mylogs_error",
                error=e,
                public_message="❌ Error al obtener tus registros de actividad."
            )

def register_logs_handlers(app) -> None:
    """Registra los manejadores de comandos de logs."""
    app.add_handler(CommandHandler("logs", logs_command))
    app.add_handler(CommandHandler("mylogs", mylogs_command))
