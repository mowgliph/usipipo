# bot/handlers/perfil.py

from __future__ import annotations

import html
import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from sqlalchemy.ext.asyncio import AsyncSession

from database.db import AsyncSessionLocal
from services import roles, user as user_service, vpn as vpn_service
from database.crud import tunnel_domains as crud_tunnel_domains
from utils.helpers import (
    send_usage_error,
    send_warning,
    send_generic_error,
    log_and_notify,
    log_error_and_notify,
)
from utils.permissions import require_admin, require_registered

logger = logging.getLogger("usipipo.handlers.perfil")


async def _get_user_profile_data(session: AsyncSession, user_id: str):
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

    # Tunnel domains (dual tunnel status)
    tunnel_domains = await crud_tunnel_domains.get_active_tunnel_domains_for_user(session, user_id)
    tunnel_info = ""
    if tunnel_domains:
        tunnel_info = f"<b>Dual Tunnel Activo:</b> ✅ Sí\n<b>Dominios bypass:</b>\n" + "\n".join(
            f"• <code>{html.escape(d.domain_name)}</code> ({'✅ Verificado' if d.is_verified else '⏳ Pendiente'})"
            for d in tunnel_domains
        )
    else:
        tunnel_info = "<b>Dual Tunnel Activo:</b> ❌ No"

    return total_configs, last_info, roles_text, tunnel_info


async def _format_profile_message(
    db_user, total_configs: int, last_info: str, roles_text: str, tunnel_info: str
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
        f"<b>Roles activos:</b>\n{roles_text}\n\n"
        f"{tunnel_info}"
    )


@require_registered
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mostrar el perfil propio o de otro usuario (por ID Telegram).

    - Si se pasa un argumento numérico, se interpreta como telegram_id.
    - Las IDs internas de usuario se manejan como UUID strings.
    """
    requester = update.effective_user
    requester_id = getattr(requester, "id", None)
    user_id_for_log: Optional[str] = None

    async with AsyncSessionLocal() as db:
        try:
            # 1. Determinar si se consulta a otro usuario (por telegram id)
            if context.args and context.args[0].isdigit():
                target_tg_id = int(context.args[0])
            else:
                target_tg_id = requester_id

            # 2. Obtener usuario por Telegram ID (service se encarga del CRUD)
            if target_tg_id is None:
                await send_generic_error(update, "No se pudo identificar al usuario solicitante")
                return
            db_user = await user_service.get_user_by_telegram_id(db, int(target_tg_id))
            if not db_user:
                await send_warning(update, "Usuario no encontrado en la base de datos.")
                return
            user_id_for_log = str(db_user.id)

            # 3. Obtener datos del perfil (usar UUID string)
            total_configs, last_info, roles_text, tunnel_info = await _get_user_profile_data(db, str(db_user.id))

            # 4. Formatear respuesta
            text = await _format_profile_message(db_user, total_configs, last_info, roles_text, tunnel_info)

            # Determinar texto del botón QvaPay basado en vinculación
            qvapay_button_text = "💳 Ver QvaPay" if getattr(db_user, "qvapay_user_id", None) else "💳 Agregar QvaPay"

            # Construir teclado inline de forma correcta
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="🔗 Nueva VPN", callback_data="newvpn"),
                        InlineKeyboardButton(text="🆓 Prueba Gratis", callback_data="trial"),
                        InlineKeyboardButton(text="📊 Mis Logs", callback_data="mylogs"),
                    ],
                    [InlineKeyboardButton(text=qvapay_button_text, callback_data="qvapay")],
                ]
            )

            # Enviar mensaje del perfil
            if update.message:
                await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
            else:
                # enviar mediante bot si message no está disponible
                chat_id = update.effective_chat.id if update.effective_chat else None
                if chat_id:
                    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=keyboard)

            # Registrar en auditoría (sin enviar mensaje adicional)
            chat_id = update.effective_chat.id if update.effective_chat else None
            await log_and_notify(
                session=db,
                bot=context.bot,
                chat_id=chat_id,
                user_id=user_id_for_log,
                action="command_profile",
                details=f"Consultó perfil de telegram_id:{target_tg_id}",
                message=text,
            )

        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Error en profile_command", extra={"user_id": user_id_for_log, "tg_id": requester_id})
            chat_id = update.effective_chat.id if update.effective_chat else None
            await log_error_and_notify(
                session=db,
                bot=context.bot,
                chat_id=chat_id,
                user_id=user_id_for_log,
                action="command_profile",
                error=exc,
            )


async def _format_whois_message(
    username: str, db_user, total_configs: int, last_info: str, roles_text: str, tunnel_info: str
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
        f"<b>Roles activos:</b>\n{roles_text}\n\n"
        f"{tunnel_info}"
    )


@require_admin
async def whois_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    requester = update.effective_user
    requester_id = getattr(requester, "id", None)
    user_id_for_log: Optional[str] = None

    async with AsyncSessionLocal() as db:
        try:
            # 1. Validar argumentos (espera @username)
            if not context.args or not context.args[0].startswith("@"):
                await send_usage_error(update, "whois", "<@username>")
                return

            username = context.args[0][1:]

            # 2. Obtener usuario por username
            db_user = await user_service.get_user_by_username(db, username)
            if not db_user:
                await send_warning(update, "⚠️ Usuario no encontrado.")
                return
            user_id_for_log = str(db_user.id)

            # 3. Obtener datos del perfil
            total_configs, last_info, roles_text, tunnel_info = await _get_user_profile_data(db, str(db_user.id))

            # 4. Formatear respuesta
            text = await _format_whois_message(username, db_user, total_configs, last_info, roles_text, tunnel_info)

            if update.message:
                await update.message.reply_text(text, parse_mode="HTML")
            else:
                chat_id = update.effective_chat.id if update.effective_chat else None
                if chat_id:
                    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")

            chat_id = update.effective_chat.id if update.effective_chat else None
            await log_and_notify(
                session=db,
                bot=context.bot,
                chat_id=chat_id,
                user_id=user_id_for_log,
                action="command_whois",
                details=f"Consultó perfil de @{username}",
                message=text,
            )

        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Error en whois_command", extra={"user_id": user_id_for_log, "tg_id": requester_id})
            chat_id = update.effective_chat.id if update.effective_chat else None
            await log_error_and_notify(
                session=db,
                bot=context.bot,
                chat_id=chat_id,
                user_id=user_id_for_log,
                action="command_whois",
                error=exc,
            )
