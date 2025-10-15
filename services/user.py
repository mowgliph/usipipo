# services/user.py
from typing import Optional, List, Dict, Any
import logging
import html

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import User as TelegramUser

from database import models
from database.crud import users as crud_users, logs as crud_logs, settings as crud_settings
from utils.helpers import log_and_notify

logger = logging.getLogger("usipipo")

async def ensure_user_exists(session: AsyncSession, tg_payload: Dict[str, Any]) -> models.User:
    """
    Asegura que exista un User para el payload de Telegram.
    - Usa crud_users.ensure_user (ya async) o create_user_from_tg as needed.
    - Devuelve el objeto User (refrescado si fue creado).
    """
    # crud_users.ensure_user updates existing or creates new (commit behavior controlled there)
    user = await crud_users.ensure_user(session, tg_payload, commit=True)
    return user

async def promote_to_admin(session: AsyncSession, user_id: int) -> Optional[models.User]:
    """
    Asigna permisos de administrador a un usuario y registra la auditoría.
    Hace commit dentro de los CRUD helpers.
    """
    user = await crud_users.set_user_admin(session, str(user_id), True, commit=True)
    if not user:
        return None
    try:
        await crud_logs.create_audit_log(session, str(user_id), "promote_admin", "Usuario promovido a administrador")
        await session.commit()
    except Exception:
        logger.exception("failed_audit_promote_admin", extra={"user_id": user_id})
        try:
            await session.rollback()
        except Exception:
            logger.exception("rollback_failed_after_promote", extra={"user_id": user_id})
    await session.refresh(user)
    return user

async def demote_from_admin(session: AsyncSession, user_id: int) -> Optional[models.User]:
    user = await crud_users.set_user_admin(session, str(user_id), False, commit=True)
    if not user:
        return None
    try:
        await crud_logs.create_audit_log(session, str(user_id), "demote_admin", "Usuario degradado de administrador")
        await session.commit()
    except Exception:
        logger.exception("failed_audit_demote_admin", extra={"user_id": user_id})
        try:
            await session.rollback()
        except Exception:
            logger.exception("rollback_failed_after_demote", extra={"user_id": user_id})
    await session.refresh(user)
    return user

async def list_all_users(session: AsyncSession, limit: int = 50) -> List[models.User]:
    return await crud_users.list_users(session, limit=limit)

async def get_user_settings(session: AsyncSession, user_id: int):
    return await crud_settings.list_user_settings(session, str(user_id))

async def update_user_setting(session: AsyncSession, user_id: int, key: str, value: str):
    setting = await crud_settings.set_user_setting(session, str(user_id), key, value)
    try:
        await crud_logs.create_audit_log(session, str(user_id), "update_setting", f"{key}={value}")
        await session.commit()
    except Exception:
        logger.exception("failed_audit_update_setting", extra={"user_id": user_id})
        try:
            await session.rollback()
        except Exception:
            logger.exception("rollback_failed_after_update_setting", extra={"user_id": user_id})
    return setting

async def get_user_by_username(session: AsyncSession, username: str) -> Optional[models.User]:
    return await crud_users.get_user_by_username(session, username)

async def get_user(session: AsyncSession, user_id: int) -> Optional[models.User]:
    return await crud_users.get_user(session, user_id)

async def get_user_telegram_info(session: AsyncSession, tg_user: TelegramUser) -> str:
    """
    Obtiene y formatea la información de Telegram del usuario (ID, nombre, username).
    Registra la acción en AuditLog.
    Devuelve el texto formateado en HTML.
    """
    try:
        # Buscar usuario en DB (opcional, para registrar user_id en AuditLog)
        db_user = await crud_users.get_user_by_telegram_id(session, tg_user.id)
        user_id = db_user.id if db_user else None

        # Formatear respuesta en HTML
        text = (
            f"<b>Tu información de Telegram</b>\n\n"
            f"<b>Nombre:</b> {html.escape(tg_user.full_name or 'N/A')}\n"
            f"<b>Usuario:</b> {html.escape('@' + tg_user.username) if tg_user.username else 'N/A'}\n"
            f"<b>ID:</b> <code>{tg_user.id}</code>\n"
        )

        # Registrar en AuditLog
        await log_and_notify(
            session=session,
            bot=None,  # No enviar mensaje aquí, se envía en el handler
            chat_id=None,
            user_id=user_id,
            action="command_myid",
            details="Usuario consultó su ID de Telegram",
            message=text,
        )

        return text
    except Exception as e:
        logger.exception("Error en get_user_telegram_info", extra={"tg_id": tg_user.id})
        raise