# bot/handlers/roles.py

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from database.db import AsyncSessionLocal as get_session
from services import roles as roles_service
from services import user as user_service
from utils.helpers import (
    send_usage_error,
    send_warning,
    log_and_notify,
    log_error_and_notify,
    safe_chat_id_from_update,
    format_roles_list,
)
from utils.permissions import require_admin, require_registered

logger = logging.getLogger("usipipo.handlers.roles")


@require_registered
async def myroles_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra los roles activos del usuario."""
    tg_user = update.effective_user
    chat_id = safe_chat_id_from_update(update)

    async with get_session() as session:
        try:
            db_user = await user_service.ensure_user_exists(session, {
                "id": tg_user.id,
                "username": tg_user.username,
                "first_name": tg_user.first_name,
                "last_name": tg_user.last_name,
            })
            user_roles = await roles_service.get_user_roles(session, db_user.id)
            if not user_roles:
                await send_warning(update, "No tienes roles activos.")
                return

            msg = await format_roles_list(user_roles)
            await log_and_notify(
                session=session,
                bot=context.bot,
                chat_id=chat_id,
                user_id=db_user.id,
                action="command_myroles",
                details="Usuario consultó sus roles activos",
                message=msg,
            )
        except Exception as e:
            logger.exception("Error in myroles_command: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(
                session=session,
                bot=context.bot,
                chat_id=chat_id,
                user_id=None,
                action="command_myroles",
                error=e,
            )


@require_admin
async def grantrole_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Otorga un rol a un usuario: /grantrole <telegram_id> <role> [days]"""
    requester = update.effective_user
    chat_id = safe_chat_id_from_update(update)

    async with get_session() as session:
        try:
            if len(context.args) < 2:
                await send_usage_error(update, "grantrole", "<telegram_id> <role> [days]")
                return

            try:
                target_tg_id = int(context.args[0])
            except ValueError:
                await send_usage_error(update, "grantrole", "<telegram_id> <role> [days]")
                return

            role_name = context.args[1]
            days = int(context.args[2]) if len(context.args) >= 3 and context.args[2].isdigit() else None

            requester_user = await user_service.ensure_user_exists(session, {
                "id": requester.id,
                "username": requester.username,
                "first_name": requester.first_name,
                "last_name": requester.last_name,
            })
            user_role = await roles_service.grant_role(
                session,
                target_tg_id=str(target_tg_id),
                role_name=role_name,
                days=days,
                granted_by=requester_user.id,
            )
            if not user_role:
                await send_warning(update, f"No se pudo otorgar el rol '{role_name}' al usuario {target_tg_id}.")
                return

            msg = (
                f"✅ Rol <b>{role_name}</b> otorgado a <code>{target_tg_id}</code> "
                f"hasta {user_role.expires_at.strftime('%Y-%m-%d') if user_role.expires_at else 'sin expiración'}."
            )
            await log_and_notify(
                session=session,
                bot=context.bot,
                chat_id=chat_id,
                user_id=requester_user.id,
                action="grant_role",
                details=f"Otorgó rol '{role_name}' a telegram_id:{target_tg_id} expira:{user_role.expires_at}",
                message=msg,
            )
            await session.commit()
        except Exception as e:
            logger.exception("Error in grantrole_command: %s", type(e).__name__, extra={"tg_id": requester.id})
            await log_error_and_notify(
                session=session,
                bot=context.bot,
                chat_id=chat_id,
                user_id=None,
                action="grant_role",
                error=e,
            )


@require_admin
async def revokerole_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Revoca un rol de un usuario: /revokerole <telegram_id> <role>"""
    requester = update.effective_user
    chat_id = safe_chat_id_from_update(update)

    async with get_session() as session:
        try:
            if len(context.args) < 2:
                await send_usage_error(update, "revokerole", "<telegram_id> <role>")
                return

            try:
                target_tg_id = int(context.args[0])
            except ValueError:
                await send_usage_error(update, "revokerole", "<telegram_id> <role>")
                return

            role_name = context.args[1]

            requester_user = await user_service.ensure_user_exists(session, {
                "id": requester.id,
                "username": requester.username,
                "first_name": requester.first_name,
                "last_name": requester.last_name,
            })
            success = await roles_service.revoke_role(session, target_tg_id=str(target_tg_id), role_name=role_name)
            if not success:
                await send_warning(update, f"Rol '{role_name}' no encontrado para el usuario {target_tg_id}.")
                return

            msg = f"❌ Rol <b>{role_name}</b> revocado de <code>{target_tg_id}</code>."
            await log_and_notify(
                session=session,
                bot=context.bot,
                chat_id=chat_id,
                user_id=requester_user.id,
                action="revoke_role",
                details=f"Revocó rol '{role_name}' de telegram_id:{target_tg_id}",
                message=msg,
            )
            await session.commit()
        except Exception as e:
            logger.exception("Error in revokerole_command: %s", type(e).__name__, extra={"tg_id": requester.id})
            await log_error_and_notify(
                session=session,
                bot=context.bot,
                chat_id=chat_id,
                user_id=None,
                action="revoke_role",
                error=e,
            )


def register_roles_handlers(app):
    """Registra los handlers de roles en la aplicación."""
    app.add_handler(CommandHandler("myroles", myroles_command))
    app.add_handler(CommandHandler("grantrole", grantrole_command))
    app.add_handler(CommandHandler("revokerole", revokerole_command))