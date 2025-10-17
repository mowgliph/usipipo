# utils/permissions.py
from functools import wraps
from typing import Callable, Any, Optional
from telegram import Update
from telegram.ext import ContextTypes
import logging
import os

from database.db import get_session
from database.crud import users as crud_users
from utils.helpers import log_and_notify, log_error_and_notify, safe_chat_id_from_update, send_permission_error, send_generic_error
from config import superadmins as config_superadmins
from config.config import ADMIN_TG_IDS

logger = logging.getLogger("usipipo.permissions")


async def _auto_register_admin(session, tg_user, update, context, is_super: bool = False) -> Optional[Any]:
    """
    Registra automáticamente un usuario como admin/superadmin desde env/config.
    Retorna el user_obj si se registra, None si falla.
    """
    try:
        payload = {
            "id": tg_user.id,
            "username": getattr(tg_user, "username", None),
            "first_name": getattr(tg_user, "first_name", None),
            "last_name": getattr(tg_user, "last_name", None),
        }
        user_obj = await crud_users.ensure_user(session, payload, commit=True)

        if is_super:
            await crud_users.set_user_superadmin(session, user_obj.id, True, commit=True)
            role_type = "superadmin"
            message = "🧾 Registro automático completado. Ya puedes usar comandos de superadministración."
        else:
            await crud_users.set_user_admin(session, user_obj.id, True, commit=True)
            role_type = "admin"
            message = "🧾 Registro automático completado. Ya puedes usar comandos administrativos."

        await log_and_notify(
            session, context.bot, safe_chat_id_from_update(update), user_obj.id,
            f"auto_register_{role_type}", "Registro automático completado",
            message
        )
        return user_obj
    except Exception as exc:
        logger.exception(f"auto_register_{'super' if is_super else ''}admin_failed", extra={"tg_id": tg_user.id})
        await log_error_and_notify(
            session, context.bot, safe_chat_id_from_update(update), None,
            f"auto_register_{'super' if is_super else ''}admin_failed", exc,
            public_message="Error en registro automático. Contacta a soporte."
        )
        return None


def require_admin(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorador que requiere permisos de administrador.
    Auto-registra admins desde variables de entorno si no existen.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Any:
        tg_user = update.effective_user
        if not tg_user:
            await send_generic_error(update, "No se pudo identificar al usuario")
            return

        async with get_session() as session:
            try:
                db_user = await crud_users.get_user_by_telegram_id(session, tg_user.id)
                if db_user and await crud_users.is_user_admin(session, db_user.id):
                    return await func(update, context, *args, **kwargs)

                # Verificar auto-registro desde config
                if tg_user.id in ADMIN_TG_IDS:
                    user_obj = await _auto_register_admin(session, tg_user, update, context, is_super=False)
                    if user_obj:
                        return await func(update, context, *args, **kwargs)

                await send_permission_error(update, "admin")
                return
            except Exception as exc:
                logger.exception("require_admin_check_failed", extra={"tg_id": tg_user.id})
                await log_error_and_notify(
                    session, context.bot, safe_chat_id_from_update(update), None,
                    "require_admin_check_failed", exc,
                    public_message="Error verificando permisos. Intenta más tarde."
                )
                return
    return wrapper


def require_superadmin(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorador que requiere permisos de superadministrador.
    Auto-registra superadmins desde config/superadmins.py si no existen.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Any:
        tg_user = update.effective_user
        if not tg_user:
            await send_generic_error(update, "No se pudo identificar al usuario")
            return

        async with get_session() as session:
            try:
                db_user = await crud_users.get_user_by_telegram_id(session, tg_user.id)
                if db_user and await crud_users.is_user_superadmin(session, db_user.id):
                    return await func(update, context, *args, **kwargs)

                # Verificar auto-registro desde config
                if config_superadmins.is_superadmin_tg(tg_user.id):
                    user_obj = await _auto_register_admin(session, tg_user, update, context, is_super=True)
                    if user_obj:
                        return await func(update, context, *args, **kwargs)

                await send_permission_error(update, "superadmin")
                return
            except Exception as exc:
                logger.exception("require_superadmin_check_failed", extra={"tg_id": tg_user.id})
                await log_error_and_notify(
                    session, context.bot, safe_chat_id_from_update(update), None,
                    "require_superadmin_check_failed", exc,
                    public_message="Error verificando permisos. Intenta más tarde."
                )
                return
    return wrapper


def require_registered(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorador que asegura que el usuario esté registrado.
    Auto-registra admins/superadmins desde config/env si no existen.
    Para usuarios normales, requiere registro manual.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Any:
        tg_user = update.effective_user
        if not tg_user:
            await send_generic_error(update, "No se pudo identificar al usuario")
            return

        bot = context.bot
        chat_id = safe_chat_id_from_update(update)

        async with get_session() as session:
            try:
                db_user = await crud_users.get_user_by_telegram_id(session, tg_user.id)
                if db_user:
                    return await func(update, context, *args, **kwargs)

                # Verificar si es admin/superadmin para auto-registro
                is_super = config_superadmins.is_superadmin_tg(tg_user.id)
                is_admin = (tg_user.id in ADMIN_TG_IDS) or is_super

                if is_admin or is_super:
                    user_obj = await _auto_register_admin(session, tg_user, update, context, is_super=is_super)
                    if user_obj:
                        return await func(update, context, *args, **kwargs)

                # Usuario normal no registrado
                await send_generic_error(
                    update,
                    "No estás registrado aún.\nUsa /register para crear tu cuenta primero."
                )
                return

            except Exception as exc:
                logger.exception("require_registered_failed", extra={"tg_id": tg_user.id})
                await log_error_and_notify(
                    session, bot, chat_id, None,
                    "require_registered_failed", exc,
                    public_message="Error verificando registro. Intenta más tarde."
                )
                return

    return wrapper
