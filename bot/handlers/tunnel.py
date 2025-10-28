# bot/handlers/tunnel.py

from __future__ import annotations
from typing import Optional, List
import logging
import re

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from database.db import AsyncSessionLocal as get_session
from database.crud import tunnel_domains as crud_tunnel_domains
from database.models import User
from services import user as user_service
from utils.helpers import (
    log_and_notify,
    log_error_and_notify,
    notify_admins,
    safe_chat_id_from_update,
    send_success,
    send_usage_error,
    send_warning,
)
from utils.permissions import require_registered

logger = logging.getLogger("usipipo.handlers.tunnel")


def _validate_domain_name(domain: str) -> bool:
    """
    Valida que el dominio sea un FQDN válido.
    """
    # Patrón básico para FQDN: letras, números, guiones, puntos
    # Debe tener al menos un punto, no empezar/terminar con punto o guión
    pattern = r'^(?!-)([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain)) and len(domain) <= 253


async def _get_db_user(session: AsyncSession, tg_user_id: int) -> Optional[User]:
    """Obtiene el usuario de la base de datos por telegram_id."""
    return await user_service.get_user_by_telegram_id(session, tg_user_id)


@require_registered
async def tunnel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja el comando /tunnel para gestión de dominios de bypass VPN.

    Subcomandos:
    - /tunnel add <domain> - Agrega un dominio de bypass
    - /tunnel list - Lista dominios del usuario
    - /tunnel remove <domain> - Remueve un dominio de bypass
    """
    tg_user = update.effective_user
    if not tg_user:
        logger.warning("update.effective_user is None in tunnel_command")
        await send_warning(update, "Error: Usuario no identificado.")
        return

    chat_id = safe_chat_id_from_update(update)
    bot = context.bot

    if not context.args or len(context.args) < 1:
        await send_usage_error(update, "tunnel", "add <domain> | list | remove <domain>")
        return

    subcommand = context.args[0].lower()

    async with get_session() as session:
        try:
            db_user = await _get_db_user(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado. Usa /register primero.")
                return

            if subcommand == "add":
                await _handle_tunnel_add(session, update, context, db_user, bot, chat_id)

            elif subcommand == "list":
                await _handle_tunnel_list(session, update, db_user, bot, chat_id)

            elif subcommand == "remove":
                await _handle_tunnel_remove(session, update, context, db_user, bot, chat_id)

            else:
                await send_usage_error(update, "tunnel", "add <domain> | list | remove <domain>")

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error in tunnel_command: %s", type(e).__name__, extra={"tg_id": str(tg_user.id)})
            await log_error_and_notify(session, bot, chat_id, None, action="tunnel_command", error=e)
            await notify_admins(session, bot, message=f"Error en /tunnel para {str(tg_user.id)}: {str(e)}")


async def _handle_tunnel_add(
    session: AsyncSession,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    db_user: User,
    bot,
    chat_id: Optional[int]
) -> None:
    """Maneja subcomando add."""
    if len(context.args) < 2:
        await send_usage_error(update, "tunnel add", "<domain>")
        return

    domain_name = context.args[1].lower().strip()

    # Validar formato del dominio
    if not _validate_domain_name(domain_name):
        await send_warning(update, "Formato de dominio inválido. Ejemplo: example.com")
        return

    try:
        # Intentar crear el dominio
        domain = await crud_tunnel_domains.create_tunnel_domain(
            session=session,
            user_id=str(db_user.id),
            domain_name=domain_name,
            commit=True
        )

        msg = f"✅ Dominio <code>{domain_name}</code> agregado exitosamente."
        await log_and_notify(session, bot, chat_id, str(db_user.id), action="tunnel_add",
                           details=f"Dominio {domain_name} agregado", message=msg)

    except ValueError as e:
        if "domain_already_exists" in str(e):
            await send_warning(update, f"El dominio <code>{domain_name}</code> ya está registrado.")
        else:
            await send_warning(update, "Error al agregar dominio.")
    except Exception as e:
        logger.exception("Error creando dominio de túnel", extra={"user_id": str(db_user.id), "domain": domain_name})
        await send_warning(update, "Error al agregar dominio. Intenta más tarde.")


async def _handle_tunnel_list(
    session: AsyncSession,
    update: Update,
    db_user: User,
    bot,
    chat_id: Optional[int]
) -> None:
    """Maneja subcomando list."""
    try:
        domains = await crud_tunnel_domains.get_tunnel_domains_for_user(session, str(db_user.id))

        if not domains:
            msg = "📋 No tienes dominios de bypass configurados."
        else:
            domain_list = "\n".join([
                f"• <code>{domain.domain_name}</code> "
                f"({'verificado' if domain.is_verified else 'pendiente'})"
                for domain in domains
            ])
            msg = f"📋 Tus dominios de bypass:\n{domain_list}"

        await log_and_notify(session, bot, chat_id, str(db_user.id), action="tunnel_list",
                           details="Listó dominios de bypass", message=msg)

    except Exception as e:
        logger.exception("Error listando dominios de túnel", extra={"user_id": str(db_user.id)})
        await send_warning(update, "Error al listar dominios. Intenta más tarde.")


async def _handle_tunnel_remove(
    session: AsyncSession,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    db_user: User,
    bot,
    chat_id: Optional[int]
) -> None:
    """Maneja subcomando remove."""
    if len(context.args) < 2:
        await send_usage_error(update, "tunnel remove", "<domain>")
        return

    domain_name = context.args[1].lower().strip()

    try:
        # Verificar que el dominio existe y pertenece al usuario
        domain = await crud_tunnel_domains.get_tunnel_domain_by_name(session, domain_name)
        if not domain or str(domain.user_id) != str(db_user.id):
            await send_warning(update, f"Dominio <code>{domain_name}</code> no encontrado o no tienes permisos.")
            return

        # Eliminar el dominio
        deleted = await crud_tunnel_domains.delete_tunnel_domain(session, str(domain.id), commit=True)
        if deleted:
            msg = f"✅ Dominio <code>{domain_name}</code> removido exitosamente."
            await log_and_notify(session, bot, chat_id, str(db_user.id), action="tunnel_remove",
                               details=f"Dominio {domain_name} removido", message=msg)
        else:
            await send_warning(update, "Error al remover dominio.")

    except Exception as e:
        logger.exception("Error removiendo dominio de túnel", extra={"user_id": str(db_user.id), "domain": domain_name})
        await send_warning(update, "Error al remover dominio. Intenta más tarde.")


def register_tunnel_handlers(app):
    """Registra handlers del comando tunnel."""
    app.add_handler(CommandHandler("tunnel", tunnel_command))