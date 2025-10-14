from telegram import Update
from telegram.ext import ContextTypes
from database.db import SessionLocal
from database import crud
from services import roles
from utils.permissions import require_admin, require_registered
from utils.helpers import (
    send_usage_error,
    send_warning,
    log_and_notify,
    log_error_and_notify,
)
import html


@require_registered
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    requester = update.effective_user
    db = SessionLocal()
    try:
        # 1. Determinar si se consulta a otro usuario
        if context.args and context.args[0].isdigit():
            target_id = int(context.args[0])
        else:
            target_id = requester.id

        # 2. Obtener usuario
        db_user = crud.get_user(db, target_id)
        if not db_user:
            await send_warning(update, "Usuario no encontrado en la base de datos.")
            return

        # 3. Total de configuraciones
        total_configs = crud.count_vpn_configs_by_user(db, target_id)

        # 4. Última configuración
        last_config = crud.last_vpn_config_by_user(db, target_id)
        last_info = (
            f"{last_config.vpn_type} — {last_config.created_at.strftime('%Y-%m-%d')}"
            if last_config else "N/A"
        )

        # 5. Roles activos
        user_roles = roles.get_user_roles(db, target_id)
        roles_text = (
            "\n".join(
                f"• <b>{html.escape(r[0])}</b> "
                f"(expira: {r[1].strftime('%Y-%m-%d') if r[1] else 'sin expiración'})"
                for r in user_roles
            )
            if user_roles else "Ninguno"
        )

        # 6. Formatear respuesta
        text = (
            f"<b>👤 Perfil de usuario</b>\n\n"
            f"<b>Nombre:</b> {html.escape(db_user.first_name or '')} {html.escape(db_user.last_name or '')}\n"
            f"<b>Usuario:</b> {html.escape('@'+db_user.username) if db_user.username else 'N/A'}\n"
            f"<b>ID:</b> <code>{db_user.id}</code>\n"
            f"<b>Registrado:</b> {db_user.created_at.strftime('%Y-%m-%d')}\n"
            f"<b>Total de configuraciones:</b> {total_configs}\n"
            f"<b>Última configuración:</b> {last_info}\n"
            f"<b>Roles activos:</b>\n{roles_text}"
        )

        await log_and_notify(
            db,
            update,
            requester.id,
            "command_profile",
            f"Consultó perfil de ID:{target_id}",
            text,
        )

    except Exception as e:
        uid = db_user.id if 'db_user' in locals() and db_user else None
        await log_error_and_notify(update, uid, "command_profile", e)
    finally:
        db.close()


@require_admin
async def whois_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        # 1. Validar argumentos
        if not context.args or not context.args[0].startswith("@"):
            await send_usage_error(update, "whois", "<@username>")
            return

        username = context.args[0][1:]  # quitar @

        # 2. Obtener usuario
        db_user = crud.get_user_by_username(db, username)
        if not db_user:
            await send_warning(update, "⚠️ Usuario no encontrado.")
            return

        # 3. Total de configuraciones
        total_configs = crud.count_vpn_configs_by_user(db, db_user.id)

        # 4. Última configuración
        last_config = crud.last_vpn_config_by_user(db, db_user.id)
        last_info = (
            f"{last_config.vpn_type} — {last_config.created_at.strftime('%Y-%m-%d')}"
            if last_config else "N/A"
        )

        # 5. Roles activos
        user_roles = roles.get_user_roles(db, db_user.id)
        roles_text = (
            "\n".join(
                f"• <b>{html.escape(r[0])}</b> "
                f"(expira: {r[1].strftime('%Y-%m-%d') if r[1] else 'sin expiración'})"
                for r in user_roles
            )
            if user_roles else "Ninguno"
        )

        # 6. Formatear respuesta
        text = (
            f"<b>🔍 Perfil de @{html.escape(username)}</b>\n\n"
            f"<b>Nombre:</b> {html.escape(db_user.first_name or '')} {html.escape(db_user.last_name or '')}\n"
            f"<b>ID:</b> <code>{db_user.id}</code>\n"
            f"<b>Registrado:</b> {db_user.created_at.strftime('%Y-%m-%d')}\n"
            f"<b>Total de configuraciones:</b> {total_configs}\n"
            f"<b>Última configuración:</b> {last_info}\n"
            f"<b>Roles activos:</b>\n{roles_text}"
        )

        await log_and_notify(
            db,
            update,
            None,
            "command_whois",
            f"Consultó perfil de @{username}",
            text,
        )

    except Exception as e:
        uid = db_user.id if 'db_user' in locals() and db_user else None
        await log_error_and_notify(update, uid, "command_whois", e)
    finally:
        db.close()