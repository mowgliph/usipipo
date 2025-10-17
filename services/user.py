# services/user.py

from __future__ import annotations
from typing import Optional, List, Dict, Any
import logging
import html

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import User as TelegramUser

from database import models
from database.crud import users as crud_users, logs as crud_logs, settings as crud_settings
from utils.helpers import log_and_notify

logger = logging.getLogger("usipipo.services.user")

async def ensure_user_exists(session: AsyncSession, tg_payload: Dict[str, Any]) -> models.User:
    """
    Asegura que exista un User para el payload de Telegram.
    - Usa crud_users.ensure_user (ya async) o create_user_from_tg as needed.
    - Devuelve el objeto User (refrescado si fue creado).
    """
    # crud_users.ensure_user updates existing or creates new (commit behavior controlled there)
    user = await crud_users.ensure_user(session, tg_payload, commit=True)
    return user

async def promote_to_admin(session: AsyncSession, user_id: str) -> Optional[models.User]:
    """
    Asigna permisos de administrador a un usuario y registra la auditoría.
    Hace commit dentro de los CRUD helpers.
    """
    user = await crud_users.set_user_admin(session, user_id, True, commit=True)
    if not user:
        return None
    try:
        await crud_logs.create_audit_log(session, user_id, "promote_admin", payload={"action": "promote_to_admin"}, commit=False)
        await session.commit()
    except Exception:
        logger.exception("failed_audit_promote_admin", extra={"user_id": user_id})
        try:
            await session.rollback()
        except Exception:
            logger.exception("rollback_failed_after_promote", extra={"user_id": user_id})
    await session.refresh(user)
    return user

async def demote_from_admin(session: AsyncSession, user_id: str) -> Optional[models.User]:
    user = await crud_users.set_user_admin(session, user_id, False, commit=True)
    if not user:
        return None
    try:
        await crud_logs.create_audit_log(session, user_id, "demote_admin", payload={"action": "demote_from_admin"}, commit=False)
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
    try:
        return await crud_users.list_users(session, limit=limit)
    except Exception as e:
        logger.exception("Error listando usuarios", extra={"user_id": None})
        return []

async def get_user_settings(session: AsyncSession, user_id: str) -> List[models.UserSetting]:
    try:
        return await crud_settings.list_user_settings(session, user_id)
    except Exception as e:
        logger.exception("Error obteniendo settings de usuario", extra={"user_id": user_id})
        return []

async def update_user_setting(session: AsyncSession, user_id: str, key: str, value: str) -> Optional[models.UserSetting]:
    setting = await crud_settings.set_user_setting(session, user_id, key, value, commit=False)
    try:
        await crud_logs.create_audit_log(session, user_id, "update_setting", payload={"key": key, "value": value}, commit=False)
        await session.commit()
        await session.refresh(setting)
    except Exception:
        logger.exception("failed_audit_update_setting", extra={"user_id": user_id})
        try:
            await session.rollback()
        except Exception:
            logger.exception("rollback_failed_after_update_setting", extra={"user_id": user_id})
        return None
    return setting

async def get_user_by_username(session: AsyncSession, username: str) -> Optional[models.User]:
    try:
        return await crud_users.get_user_by_username(session, username)
    except Exception as e:
        logger.exception("Error obteniendo usuario por username", extra={"username": username})
        return None

async def get_user(session: AsyncSession, user_id: str) -> Optional[models.User]:
    try:
        return await crud_users.get_user_by_pk(session, user_id)
    except Exception as e:
        logger.exception("Error obteniendo usuario por ID", extra={"user_id": user_id})
        return None

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
        return "Error obteniendo información de Telegram."
async def get_help_message(session: AsyncSession, user_id: Optional[str]) -> str:
    """
    Genera el mensaje de ayuda según el rol del usuario.
    Devuelve el mensaje formateado en HTML.
    """
    try:
        # Verificar si es admin o superadmin
        is_admin = await crud_users.is_user_admin(session, user_id) if user_id else False
        is_superadmin = await crud_users.is_user_superadmin(session, user_id) if user_id else False

        # Base para todos los usuarios
        help_msg = (
            "📖 <b>Comandos disponibles en uSipipo Bot:</b>\n\n"
            "👤 <b>Usuarios</b>\n"
            "  • /start – Iniciar el bot y ver bienvenida\n"
            "  • /register – Registrarte en la base de datos\n"
            "  • /help – Mostrar este menú de ayuda\n"
            "  • /myid – Ver tu ID de Telegram\n"
            "  • /profile – Ver tu perfil\n"
            "  • /whois &lt;@usuario|id&gt; – Consultar perfil de otro usuario\n\n"
            "🌐 <b>VPN</b>\n"
            "  • /trialvpn &lt;wireguard|outline&gt; – Solicitar un VPN de prueba (7 días)\n"
            "  • /newvpn &lt;wireguard|outline&gt; &lt;meses&gt; – Crear nueva VPN\n"
            "  • /myvpns – Listar tus configuraciones VPN\n"
            "  • /revokevpn &lt;id&gt; – Revocar una configuración VPN\n"
        )

        # Extensión para admins/superadmins
        if is_admin or is_superadmin:
            help_msg += (
                "\n🛠️ <b>Administración</b>\n"
                "  • /status – Ver estado del bot\n"
                "  • /logs – Ver acciones recientes\n"
                "  • /mylogs – Ver tus acciones registradas\n"
                "  • /promote &lt;id&gt; – Asignar admin\n"
                "  • /demote &lt;id&gt; – Quitar admin\n"
                "  • /setsuper &lt;id&gt; – Asignar superadmin\n"
                "  • /listadmins – Listar administradores\n"
                "  • /grantrole &lt;id&gt; &lt;rol&gt; – Asignar rol\n"
                "  • /revokerole &lt;id&gt; &lt;rol&gt; – Revocar rol\n"
            )

        return help_msg
    except Exception as e:
        logger.exception("Error generando mensaje de ayuda", extra={"user_id": user_id})
        raise
        raise