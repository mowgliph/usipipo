# bot/handlers/perfil.py

from __future__ import annotations

import html
import logging

from telegram import Update
from telegram.ext import ContextTypes

from database.db import AsyncSessionLocal as get_session
from services import roles, user as user_service, vpn as vpn_service
from utils.helpers import (
    send_usage_error,
    send_warning,
    log_and_notify,
    log_error_and_notify,
)
from utils.permissions import require_admin, require_registered

logger = logging.getLogger("usipipo.handlers.perfil")


async def _get_user_profile_data(session, user_id: str):
    """Obtiene datos del perfil de usuario."""
    # Total de configuraciones
    total_configs = await vpn_service.count_vpn_configs_by_user(
        session, user_id
    )

    # Última configuración
    last_config = await vpn_service.last_vpn_config_by_user(session, user_id)
    last_info = (
        f"{last_config.vpn_type} — {last_config.created_at.strftime('%Y-%m-%d')}"
        if last_config else "N/A"
    )

    # Roles activos
    user_roles = await roles.get_user_roles(session, user_id)
    roles_text = (
        "\n".join(
            f"• <b>{html.escape(r[0])}</b> "
            f"(expira: {r[1].strftime('%Y-%m-%d') if r[1] else 'sin expiración'})"
            for r in user_roles
        )
        if user_roles else "Ninguno"
    )

    return total_configs, last_info, roles_text


async def _format_profile_message(
    db_user, total_configs: int, last_info: str, roles_text: str
) -> str:
    """Formatea el mensaje del perfil."""
    return (
        f"<b>👤 Perfil de usuario</b>\n\n"
        f"<b>Nombre:</b> {html.escape(db_user.first_name or '')} "
        f"{html.escape(db_user.last_name or '')}\n"
        f"<b>Usuario:</b> {html.escape('@'+db_user.username) if db_user.username else 'N/A'}\n"
        f"<b>ID:</b> <code>{db_user.id}</code>\n"
        f"<b>Registrado:</b> {db_user.created_at.strftime('%Y-%m-%d')}\n"
        f"<b>Total de configuraciones:</b> {total_configs}\n"
        f"<b>Última configuración:</b> {last_info}\n"
        f"<b>Roles activos:</b>\n{roles_text}"
    )


@require_registered
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    requester = update.effective_user
    user_id_for_log = str(requester.id)
    async with get_session() as db:
        try:
            # 1. Determinar si se consulta a otro usuario
            if context.args and context.args[0].isdigit():
                target_id = int(context.args[0])
            else:
                target_id = requester.id

            # 2. Obtener usuario
            db_user = await user_service.get_user_by_telegram_id(db, target_id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado en la base de datos.")
                return
            user_id_for_log = str(db_user.id)  # Usar el ID del usuario consultado para logs si existe

            # 3. Obtener datos del perfil
            total_configs, last_info, roles_text = await _get_user_profile_data(db, str(db_user.id))

            # 4. Formatear respuesta
            text = await _format_profile_message(db_user, total_configs, last_info, roles_text)

            # Enviar mensaje del perfil con botones
            await update.message.reply_text(
                text,
                parse_mode="HTML",
                reply_markup={
                    "inline_keyboard": [
                        [
                            {"text": "🔗 Nueva VPN", "callback_data": "newvpn"},
                            {"text": "🆓 Prueba Gratis", "callback_data": "trial"},
                            {"text": "📊 Mis Logs", "callback_data": "mylogs"},
                        ]
                    ]
                },
            )

            # Registrar en auditoría (sin enviar mensaje)
            await log_and_notify(
                session=db,
                bot=context.bot,
                chat_id=update.effective_chat.id,
                user_id=user_id_for_log,
                action="command_profile",
                details=f"Consultó perfil de ID:{target_id}",
                message=text,
            )

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in profile_command: %s", type(e).__name__, extra={"tg_id": requester.id})
            await log_error_and_notify(
                session=db,
                bot=context.bot,
                chat_id=update.effective_chat.id,
                user_id=user_id_for_log,
                action="command_profile",
                error=e,
            )


async def _format_whois_message(
    username: str, db_user, total_configs: int, last_info: str, roles_text: str
) -> str:
    """Formatea el mensaje del comando whois."""
    return (
        f"<b>🔍 Perfil de @{html.escape(username)}</b>\n\n"
        f"<b>Nombre:</b> {html.escape(db_user.first_name or '')} "
        f"{html.escape(db_user.last_name or '')}\n"
        f"<b>ID:</b> <code>{db_user.id}</code>\n"
        f"<b>Registrado:</b> {db_user.created_at.strftime('%Y-%m-%d')}\n"
        f"<b>Total de configuraciones:</b> {total_configs}\n"
        f"<b>Última configuración:</b> {last_info}\n"
        f"<b>Roles activos:</b>\n{roles_text}"
    )


@require_admin
async def whois_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    requester = update.effective_user
    user_id_for_log = str(requester.id)  # Default para logs
    async with get_session() as db:
        try:
            # 1. Validar argumentos
            if not context.args or not context.args[0].startswith("@"):
                await send_usage_error(update, "whois", "<@username>")
                return

            username = context.args[0][1:]  # quitar @

            # 2. Obtener usuario
            db_user = await user_service.get_user_by_username(db, username)
            if not db_user:
                await send_warning(update, "⚠️ Usuario no encontrado.")
                return
            user_id_for_log = str(db_user.id)  # Usar el ID del usuario consultado para logs si existe

            # 3. Obtener datos del perfil
            total_configs, last_info, roles_text = await _get_user_profile_data(db, str(db_user.id))

            # 4. Formatear respuesta
            text = await _format_whois_message(username, db_user, total_configs, last_info, roles_text)

            await update.message.reply_text(text, parse_mode="HTML")

            await log_and_notify(
                session=db,
                bot=context.bot,
                chat_id=update.effective_chat.id,
                user_id=user_id_for_log,
                action="command_whois",
                details=f"Consultó perfil de @{username}",
                message=text,
            )

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in whois_command: %s", type(e).__name__, extra={"tg_id": requester.id})
            await log_error_and_notify(
                session=db,
                bot=context.bot,
                chat_id=update.effective_chat.id,
                user_id=user_id_for_log,
                action="command_whois",
                error=e,
            )
