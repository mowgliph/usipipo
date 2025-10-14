# utils/permissions.py
from functools import wraps
from typing import Callable, Any
from telegram import Update
from telegram.ext import ContextTypes
import logging
import os

from database.db import get_session
from database.crud import users as crud_users
from utils.helpers import log_and_notify, log_error_and_notify, safe_chat_id_from_update
from config import superadmins as config_superadmins

logger = logging.getLogger("usipipo")


def _parse_ids_from_env(key: str) -> set[int]:
    raw = os.getenv(key, "")
    return {int(x.strip()) for x in raw.split(",") if x.strip()}


# Optional env-driven admin list (comma-separated TG IDs)
_ADMIN_IDS = _parse_ids_from_env("ADMIN_TG_IDS")


def require_admin(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Any:
        tg_user = update.effective_user
        async with get_session() as session:
            try:
                db_user = await crud_users.get_user_by_tg_id(session, tg_user.id)
                if db_user and await crud_users.is_user_admin(session, db_user.id):
                    return await func(update, context, *args, **kwargs)

                # Allow auto-registered admins from env list
                if tg_user.id in _ADMIN_IDS:
                    # auto-register and make admin
                    payload = {
                        "id": tg_user.id,
                        "username": getattr(tg_user, "username", None),
                        "first_name": getattr(tg_user, "first_name", None),
                        "last_name": getattr(tg_user, "last_name", None),
                    }
                    user_obj = await crud_users.create_user_from_tg(session, payload, commit=True)
                    await crud_users.set_user_admin(session, user_obj.id, True, commit=True)
                    await log_and_notify(session, context.bot, safe_chat_id_from_update(update), user_obj.id,
                                         "auto_register_admin", "Registro automático completado",
                                         "🧾 Registro automático completado. Ya puedes usar comandos administrativos.")
                    return await func(update, context, *args, **kwargs)

                await update.message.reply_text("⛔ Acceso denegado: se requiere permiso de administrador.")
                return
            except Exception as exc:
                logger.exception("require_admin_check_failed", extra={"tg_id": tg_user.id})
                await log_error_and_notify(session, context.bot, safe_chat_id_from_update(update), None,
                                           "require_admin_check_failed", exc,
                                           public_message="Error verificando permisos. Intenta más tarde.")
                return
    return wrapper


def require_superadmin(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Any:
        tg_user = update.effective_user
        async with get_session() as session:
            try:
                db_user = await crud_users.get_user_by_tg_id(session, tg_user.id)
                if db_user and await crud_users.is_user_superadmin(session, db_user.id):
                    return await func(update, context, *args, **kwargs)

                # Auto-register superadmin based on config/superadmins.py
                if config_superadmins.is_superadmin_tg(tg_user.id):
                    payload = {
                        "id": tg_user.id,
                        "username": getattr(tg_user, "username", None),
                        "first_name": getattr(tg_user, "first_name", None),
                        "last_name": getattr(tg_user, "last_name", None),
                    }
                    user_obj = await crud_users.create_user_from_tg(session, payload, commit=True)
                    await crud_users.set_user_superadmin(session, user_obj.id, True, commit=True)
                    await log_and_notify(session, context.bot, safe_chat_id_from_update(update), user_obj.id,
                                         "auto_register_superadmin", "Registro automático completado",
                                         "🧾 Registro automático completado. Ya puedes usar comandos de superadministración.")
                    return await func(update, context, *args, **kwargs)

                await update.message.reply_text("⛔ Acceso denegado: se requiere permiso de superadministrador.")
                return
            except Exception as exc:
                logger.exception("require_superadmin_check_failed", extra={"tg_id": tg_user.id})
                await log_error_and_notify(session, context.bot, safe_chat_id_from_update(update), None,
                                           "require_superadmin_check_failed", exc,
                                           public_message="Error verificando permisos. Intenta más tarde.")
                return
    return wrapper


def require_registered(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorador que asegura que el usuario esté registrado.
    Si no existe y aparece en config_superadmins.SUPERADMINS or _ADMIN_IDS,
    crea la cuenta automáticamente y asigna roles según corresponda.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Any:
        tg_user = update.effective_user
        bot = context.bot
        chat_id = safe_chat_id_from_update(update)

        async with get_session() as session:
            try:
                db_user = await crud_users.get_user_by_tg_id(session, tg_user.id)
                if db_user:
                    return await func(update, context, *args, **kwargs)

                # Detect admin/superadmin from config/env
                is_super = config_superadmins.is_superadmin_tg(tg_user.id)
                is_admin = (tg_user.id in _ADMIN_IDS) or is_super

                if is_admin or is_super:
                    payload = {
                        "id": tg_user.id,
                        "username": getattr(tg_user, "username", None),
                        "first_name": getattr(tg_user, "first_name", None),
                        "last_name": getattr(tg_user, "last_name", None),
                    }
                    user_obj = await crud_users.create_user_from_tg(session, payload, commit=True)
                    if is_admin:
                        await crud_users.set_user_admin(session, user_obj.id, True, commit=True)
                    if is_super:
                        await crud_users.set_user_superadmin(session, user_obj.id, True, commit=True)

                    await log_and_notify(session, bot, chat_id, user_obj.id,
                                         "auto_register_admin", "Registro automático completado",
                                         "🧾 Registro automático completado. Ya puedes usar comandos administrativos.")
                    return await func(update, context, *args, **kwargs)

                await update.message.reply_text(
                    "⚠️ No estás registrado aún.\nUsa /register para crear tu cuenta primero.",
                )
                return

            except Exception as exc:
                uid = getattr(db_user, "id", None) if 'db_user' in locals() and db_user else None
                logger.exception("require_registered_failed", extra={"tg_id": tg_user.id})
                await log_error_and_notify(session, bot, chat_id, uid,
                                           "require_registered", exc,
                                           public_message="Error verificando registro. Intenta más tarde.")
                return

    return wrapper
