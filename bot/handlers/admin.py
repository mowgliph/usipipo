# bot/handlers/admin.py

from __future__ import annotations
from typing import Optional

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from database.crud import users as crud_users
from database.db import AsyncSessionLocal as get_session
from services import admin as admin_service, user as user_service, vpn as vpn_service, roles as role_service
from services.audit import get_audit_logs, format_logs
from utils.helpers import log_and_notify, log_error_and_notify, safe_chat_id_from_update, send_usage_error, send_generic_error
from utils.permissions import require_superadmin

logger = logging.getLogger("usipipo.handlers.admin")

@require_superadmin
async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /users [limit] - Lista usuarios recientes.
    """
    bot = context.bot
    chat_id = safe_chat_id_from_update(update)
    if not chat_id:
        logger.error("No chat_id en update", extra={"user_id": None})
        return

    args = context.args or []
    if args and not args[0].isdigit():
        await send_usage_error(update, "users", "[limit]")
        return
    limit = int(args[0]) if args and args[0].isdigit() else 50

    async with get_session() as session:
        try:
            users = await admin_service.list_users_paginated(session, limit=limit, offset=0)
            if not users:
                msg = "No hay usuarios registrados."
            else:
                lines = []
                for u in users:
                    lines.append(
                        f"• <b>{u.first_name or u.username or '—'}</b> <code>{u.id}</code>\n"
                        f"  tg: <code>{u.telegram_id}</code> admin: {'✔️' if u.is_admin else '—'} super: {'✔️' if u.is_superadmin else '—'}\n"
                        f"  created: {u.created_at.strftime('%Y-%m-%d %H:%M UTC')}"
                    )
                msg = "<b>Usuarios recientes</b>\n\n" + "\n\n".join(lines)

            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=None,
                action="admin.users",
                details="Listado de usuarios",
                message=msg,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.exception("Error in users_command: %s", type(e).__name__, extra={"tg_id": None})
            await send_generic_error(update, "Error listando usuarios. El equipo ha sido notificado.")

@require_superadmin
async def promote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /promote <user_id|telegram_id> - Promueve a admin.
    """
    bot = context.bot
    chat_id = safe_chat_id_from_update(update)
    if not chat_id:
        logger.error("No chat_id en update", extra={"user_id": None})
        return

    args = context.args or []
    if not args or len(args) != 1:
        await send_usage_error(update, "promote", "<user_id|telegram_id>")
        return

    target = args[0]
    acting_tg = update.effective_user.id if update.effective_user else None

    async with get_session() as session:
        try:
            # Soporta UUID (user_id) o telegram_id numérico
            if target.isdigit():
                target_user = await crud_users.get_user_by_telegram_id(session, int(target))
                if not target_user:
                    await log_and_notify(
                        session=session,
                        bot=bot,
                        chat_id=chat_id,
                        user_id=str(acting_tg),
                        action="admin.promote_failed",
                        details=f"Usuario no encontrado por telegram_id: {target}",
                        message="Usuario no encontrado por telegram_id.",
                        parse_mode="HTML",
                    )
                    return
                target_user_id = target_user.id
            else:
                target_user_id = target

            user = await admin_service.promote_to_admin(session, target_user_id, acting_user_id=str(acting_tg))
            text = f"✅ Usuario promovido a admin: <code>{user.id}</code>"
            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=str(acting_tg),
                action="admin.promote",
                details=f"Promovido {target}",
                message=text,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.exception("Error in promote_command: %s", type(e).__name__, extra={"tg_id": acting_tg})
            await send_generic_error(update, "Error promoviendo usuario. El equipo ha sido notificado.")

@require_superadmin
async def demote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /demote <user_id|telegram_id> - Revoca estado de admin.
    """
    bot = context.bot
    chat_id = safe_chat_id_from_update(update)
    if not chat_id:
        logger.error("No chat_id en update", extra={"user_id": None})
        return

    args = context.args or []
    if not args or len(args) != 1:
        await send_usage_error(update, "demote", "<user_id|telegram_id>")
        return

    target = args[0]
    acting_tg = update.effective_user.id if update.effective_user else None

    async with get_session() as session:
        try:
            if target.isdigit():
                target_user = await crud_users.get_user_by_telegram_id(session, int(target))
                if not target_user:
                    await log_and_notify(
                        session=session,
                        bot=bot,
                        chat_id=chat_id,
                        user_id=str(acting_tg),
                        action="admin.demote_failed",
                        details=f"Usuario no encontrado por telegram_id: {target}",
                        message="Usuario no encontrado por telegram_id.",
                        parse_mode="HTML",
                    )
                    return
                target_user_id = target_user.id
            else:
                target_user_id = target

            user = await admin_service.demote_from_admin(session, target_user_id, acting_user_id=str(acting_tg))
            text = f"✅ Usuario revocado de admin: <code>{user.id}</code>"
            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=str(acting_tg),
                action="admin.demote",
                details=f"Despromovido {target}",
                message=text,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.exception("Error in demote_command: %s", type(e).__name__, extra={"tg_id": acting_tg})
            await send_generic_error(update, "Error despromoviendo usuario. El equipo ha sido notificado.")

@require_superadmin
async def setsuper_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /setsuper <user_id|telegram_id> - Asigna rol de superadmin.
    """
    bot = context.bot
    chat_id = safe_chat_id_from_update(update)
    if not chat_id:
        logger.error("No chat_id en update", extra={"user_id": None})
        return

    args = context.args or []
    if not args or len(args) != 1:
        await send_usage_error(update, "setsuper", "<user_id|telegram_id>")
        return

    target = args[0]
    acting_tg = update.effective_user.id if update.effective_user else None

    async with get_session() as session:
        try:
            if target.isdigit():
                target_user = await crud_users.get_user_by_telegram_id(session, int(target))
                if not target_user:
                    await log_and_notify(
                        session=session,
                        bot=bot,
                        chat_id=chat_id,
                        user_id=str(acting_tg),
                        action="admin.setsuper_failed",
                        details=f"Usuario no encontrado por telegram_id: {target}",
                        message="Usuario no encontrado por telegram_id.",
                        parse_mode="HTML",
                    )
                    return
                target_user_id = target_user.id
            else:
                target_user_id = target

            user = await admin_service.set_superadmin(session, target_user_id, acting_user_id=str(acting_tg))
            text = f"✅ Usuario asignado como superadmin: <code>{user.id}</code>"
            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=str(acting_tg),
                action="admin.setsuper",
                details=f"Asignado superadmin {target}",
                message=text,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.exception("Error in setsuper_command: %s", type(e).__name__, extra={"tg_id": acting_tg})
            await send_generic_error(update, "Error asignando superadmin. El equipo ha sido notificado.")

@require_superadmin
async def listadmins_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /listadmins - Lista usuarios con rol admin o superadmin.
    """
    bot = context.bot
    chat_id = safe_chat_id_from_update(update)
    if not chat_id:
        logger.error("No chat_id en update", extra={"user_id": None})
        return

    async with get_session() as session:
        try:
            admins = await admin_service.list_admins(session)
            if not admins:
                msg = "No hay administradores registrados."
            else:
                lines = []
                for u in admins:
                    lines.append(
                        f"• <b>{u.first_name or u.username or '—'}</b> <code>{u.id}</code>\n"
                        f"  tg: <code>{u.telegram_id}</code> admin: {'✔️' if u.is_admin else '—'} super: {'✔️' if u.is_superadmin else '—'}"
                    )
                msg = "<b>Administradores</b>\n\n" + "\n\n".join(lines)

            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=None,
                action="admin.listadmins",
                details="Listado de administradores",
                message=msg,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.exception("Error in listadmins_command: %s", type(e).__name__, extra={"tg_id": None})
            await send_generic_error(update, "Error listando administradores. El equipo ha sido notificado.")

@require_superadmin
async def roles_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /roles <user_id|telegram_id> - Muestra roles activos de un usuario.
    """
    bot = context.bot
    chat_id = safe_chat_id_from_update(update)
    if not chat_id:
        logger.error("No chat_id en update", extra={"user_id": None})
        return

    args = context.args or []
    if not args or len(args) != 1:
        await send_usage_error(update, "roles", "<user_id|telegram_id>")
        return

    target = args[0]
    acting_tg = update.effective_user.id if update.effective_user else None

    async with get_session() as session:
        try:
            if target.isdigit():
                target_user = await crud_users.get_user_by_telegram_id(session, int(target))
                if not target_user:
                    await log_and_notify(
                        session=session,
                        bot=bot,
                        chat_id=chat_id,
                        user_id=str(acting_tg),
                        action="admin.roles_failed",
                        details=f"Usuario no encontrado: {target}",
                        message="Usuario no encontrado.",
                        parse_mode="HTML",
                    )
                    return
                target_user_id = target_user.id
            else:
                target_user_id = target

            roles = await admin_service.get_user_details(session, target_user_id)
            role_lines = []
            for name, expires in roles.get("roles", []):
                expires_str = expires.strftime("%Y-%m-%d %H:%M UTC") if expires else "sin expiración"
                role_lines.append(f"• <b>{name}</b> (expira: {expires_str})")
            text = "<b>Roles activos</b>\n\n" + ("\n".join(role_lines) if role_lines else "No hay roles activos.")
            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=str(acting_tg),
                action="admin.roles",
                details=f"Roles consultados {target}",
                message=text,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.exception("Error in roles_command: %s", type(e).__name__, extra={"tg_id": acting_tg})
            await send_generic_error(update, "Error consultando roles. El equipo ha sido notificado.")

@require_superadmin
async def audit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /audit [limit] - Muestra logs de auditoría recientes.
    """
    bot = context.bot
    chat_id = safe_chat_id_from_update(update)
    if not chat_id:
        logger.error("No chat_id en update", extra={"user_id": None})
        return

    args = context.args or []
    if args and not args[0].isdigit():
        await send_usage_error(update, "audit", "[limit]")
        return
    limit = int(args[0]) if args and args[0].isdigit() else 25

    async with get_session() as session:
        try:
            logs = await get_audit_logs(session=session, limit=limit, offset=0)
            if not logs:
                text = "No hay logs de auditoría."
            else:
                # Usar la función de formato exportada por services.audit
                text = format_logs(logs)

            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=None,
                action="admin.audit",
                details="Consulta de audit logs",
                message=text,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.exception("Error in audit_command: %s", type(e).__name__, extra={"tg_id": None})
            await send_generic_error(update, "Error consultando audit logs. El equipo ha sido notificado.")

def register_admin_handlers(app):
    """
    Registra todos los handlers de comandos administrativos.
    """
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("promote", promote_command))
    app.add_handler(CommandHandler("demote", demote_command))
    app.add_handler(CommandHandler("setsuper", setsuper_command))
    app.add_handler(CommandHandler("listadmins", listadmins_command))
    app.add_handler(CommandHandler("roles", roles_command))
    app.add_handler(CommandHandler("audit", audit_command))