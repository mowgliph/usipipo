# utils/helpers.py

from __future__ import annotations
from typing import Optional, Dict, Any, Sequence, Callable, List
import traceback
import logging
import html
import io
from datetime import datetime
from telegram import Update, Bot, InputFile
from telegram.constants import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import users as crud_users
from database.crud import logs as crud_logs
from database import models

logger = logging.getLogger("usipipo.helpers")


# -------------------------
# Mensajes de respuesta (siempre HTML)
# -------------------------
async def send_usage_error(update: Update, command: str, usage: str) -> None:
    if not update.message:
        return
    await update.message.reply_text(
        f"⚠️ Uso incorrecto de /{command}\n\n"
        f"Ejemplo correcto:\n<code>/{command} {usage}</code>",
        parse_mode=ParseMode.HTML,
    )


async def send_permission_error(update: Update, required_role: str = "admin") -> None:
    if not update.message:
        return
    await update.message.reply_text(
        f"⛔ No tienes permisos suficientes. Se requiere rol: <b>{required_role}</b>",
        parse_mode=ParseMode.HTML,
    )


async def send_generic_error(update: Update, public_message: str = "Ha ocurrido un error inesperado") -> None:
    if not update.message:
        return
    await update.message.reply_text(f"⚠️ {public_message}", parse_mode=ParseMode.HTML)


async def send_warning(update: Update, message: str) -> None:
    if not update.message:
        return
    await update.message.reply_text(f"⚠️ {message}", parse_mode=ParseMode.HTML)


async def send_success(update: Update, message: str) -> None:
    if not update.message:
        return
    await update.message.reply_text(f"✅ {message}", parse_mode=ParseMode.HTML)


async def send_info(update: Update, message: str) -> None:
    if not update.message:
        return
    await update.message.reply_text(f"ℹ️ {message}", parse_mode=ParseMode.HTML)


# -------------------------
# Log + Notificación unificada (DB audit + logger + respuesta al usuario)
# -------------------------
async def log_and_notify(
    session: Optional[AsyncSession],
    bot: Optional[Bot],
    chat_id: Optional[int],
    user_id: Optional[str],
    action: str,
    details: str,
    message: str,
    parse_mode: str = ParseMode.HTML,
) -> None:
    """
    1) Registra auditoría en DB si session provisto (payload + commit=False).
    2) Registra en logger central con extra={"user_id": ...}.
    3) Envía mensaje al chat_id si bot y chat_id provistos.
    """
    # 1) Audit DB
    if session is not None:
        try:
            payload = {"details": details}
            await crud_logs.create_audit_log(session=session, user_id=user_id, action=action, details=None, payload=payload, commit=False)
        except Exception:
            logger.exception("audit_log_failed", extra={"user_id": user_id})

    # 2) Logger central
    extra_uid = user_id if user_id is not None else None
    logger.info(f"{action} | {details}", extra={"user_id": extra_uid})

    # 3) Enviar mensaje
    if bot is not None and chat_id is not None:
        try:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode)
        except Exception:
            logger.exception("notify_user_failed", extra={"user_id": extra_uid})


# -------------------------
# Log de error + notificación (DB + logger + respuesta limitada)
# -------------------------
async def log_error_and_notify(
    session: Optional[AsyncSession],
    bot: Optional[Bot],
    chat_id: Optional[int],
    user_id: Optional[str],
    action: str,
    error: Exception,
    public_message: str = "Ha ocurrido un error inesperado. El equipo ha sido notificado.",
    notify_user: bool = True,
) -> None:
    """
    1) Registra audit_log con detalles del error (truncado payload) si session provisto.
    2) Logger con stacktrace completo.
    3) Envía mensaje público al usuario (sin mostrar stacktrace).
    """
    # Prepare details (limit size for DB)
    tb = traceback.format_exc()
    details = f"{str(error)}\n{tb}"
    truncated = details if len(details) <= 2000 else details[:2000] + " ... [truncated]"
    payload = {"error": str(error), "trace": truncated}

    # 1) Audit DB
    if session is not None:
        try:
            await crud_logs.create_audit_log(session=session, user_id=user_id, action=f"{action}_error", details=None, payload=payload, commit=False)
        except Exception:
            logger.exception("audit_log_failed_on_error", extra={"user_id": user_id})

    # 2) Logger central (full stacktrace)
    extra_uid = user_id if user_id is not None else None
    logger.exception(f"{action}_error | {error}", extra={"user_id": extra_uid})

    # 3) Notify user (public message only)
    if notify_user and bot is not None and chat_id is not None:
        try:
            await bot.send_message(chat_id=chat_id, text=f"⚠️ {public_message}", parse_mode=ParseMode.HTML)
        except Exception:
            logger.exception("notify_user_failed_in_error_path", extra={"user_id": extra_uid})


# -------------------------
# Notificación a admins/superadmins
# -------------------------
async def notify_admins(
    session: Optional[AsyncSession],
    bot: Bot,
    message: str,
    action: str = "notify_admins",
    details: Optional[str] = None,
    parse_mode: str = ParseMode.HTML,
) -> None:
    """
    Envía un mensaje a todos los admins/superadmins.
    Registra la acción en auditoría (si session provisto) y logs.
    """
    admins: List[models.User] = []
    if session is not None:
        try:
            admins = await crud_users.get_admins(session)
        except Exception:
            logger.exception("failed_fetching_admins", extra={"user_id": None})
            admins = []

    # Registrar acción en audit (session opcional)
    if session is not None:
        try:
            await crud_logs.create_audit_log(session=session, user_id=None, action=action, details=details or message, payload={"details": details or message}, commit=False)
        except Exception:
            logger.exception("audit_log_failed_on_notify_admins", extra={"user_id": None})

    logger.info(f"{action} | notifying {len(admins)} admins", extra={"user_id": None})

    # Enviar mensaje a cada admin (ignorar fallos individuales)
    for admin in admins:
        tg = getattr(admin, "telegram_id", None)
        try:
            if tg is None:
                logger.debug("admin missing telegram_id", extra={"user_id": admin.id})
                continue
            await bot.send_message(chat_id=tg, text=message, parse_mode=parse_mode)
        except Exception:
            logger.exception("failed_sending_notify_to_admin", extra={"user_id": admin.id})


# -------------------------
# Utilitarios adicionales
# -------------------------
def format_days(days: int) -> str:
    return f"{days} día" if days == 1 else f"{days} días"


def safe_chat_id_from_update(update: Update) -> Optional[int]:
    if update.effective_chat:
        return update.effective_chat.id
    return None


async def format_roles_list(roles: List[Tuple[str, Optional[datetime]]]) -> str:
    """Formatea una lista de roles activos en HTML."""
    if not roles:
        return "<b>No tienes roles activos.</b>"

    lines = [
        f"• <b>{html.escape(role_name)}</b> "
        f"(expira: {expires_at.strftime('%Y-%m-%d') if expires_at else 'sin expiración'})"
        for role_name, expires_at in roles
    ]
    return "<b>Tus roles activos:</b>\n" + "\n".join(lines)


async def format_vpn_list(vpns: List[models.VPNConfig]) -> str:
    """Formatea lista de VPNs en HTML."""
    if not vpns:
        return "<b>No tienes configuraciones VPN activas.</b>"

    lines = []
    for vpn in vpns:
        status = vpn.status or "active"
        expires = vpn.expires_at.strftime("%Y-%m-%d") if vpn.expires_at else "sin expiración"
        lines.append(
            f"• <b>ID:</b> <code>{vpn.id}</code>\n"
            f"   Tipo: {vpn.vpn_type.upper()} — {html.escape(vpn.config_name or 'N/A')}\n"
            f"   Estado: {status}\n"
            f"   Creado: {vpn.created_at.strftime('%Y-%m-%d')}\n"
            f"   Expira: {expires}\n"
        )
    return "<b>Tus configuraciones VPN:</b>\n" + "\n".join(lines)


async def send_vpn_config(update: Update, vpn: models.VPNConfig, qr_bytes: Optional[bytes] = None) -> None:
    """Envía config VPN según tipo (file/QR para wireguard, text para outline)."""
    if not update.message:
        logger.error("No message in update for send_vpn_config", extra={"user_id": None})
        return

    if vpn.vpn_type == "wireguard":
        conf_bytes = io.BytesIO(vpn.config_data.encode("utf-8"))
        conf_bytes.name = f"{vpn.config_name}.conf"
        await update.message.reply_document(
            document=InputFile(conf_bytes),
            filename=conf_bytes.name,
            caption="✅ Aquí está tu configuración WireGuard (.conf)",
            parse_mode=ParseMode.HTML,
        )
        if qr_bytes:
            await update.message.reply_photo(
                photo=io.BytesIO(qr_bytes),
                caption="Escanea este QR en tu app WireGuard 📱",
                parse_mode=ParseMode.HTML,
            )
    elif vpn.vpn_type == "outline":
        await update.message.reply_text(
            f"✅ Tu configuración Outline ha sido creada.\n\n"
            f"<b>Access Key:</b>\n<code>{html.escape(vpn.config_data)}</code>",
            parse_mode=ParseMode.HTML,
        )


async def format_expiration_message(vpn: models.VPNConfig) -> str:
    """Formatea mensaje de expiración en HTML."""
    expires_str = vpn.expires_at.strftime("%Y-%m-%d %H:%M UTC") if vpn.expires_at else "N/A"
    if vpn.is_trial:
        return (
            f"⚠️ Tu <b>trial</b> de <b>{html.escape(vpn.vpn_type.upper())}</b> "
            f"expira el <code>{expires_str}</code>.\n\n"
            f"👉 Contrata un plan con <code>/newvpn {vpn.vpn_type} 1</code>"
        )
    return (
        f"⚠️ Tu VPN <code>{vpn.id}</code> ({vpn.vpn_type.upper()}) "
        f"expira el <code>{expires_str}</code>.\n\n"
        f"👉 Renueva con <code>/newvpn {vpn.vpn_type} 1</code>"
    )


def format_log_entry(log: Any) -> str:
    """
    Formatea una entrada de log para mostrarla en el chat.
    
    Args:
        log: Objeto de log con los campos created_at, user, user_id, action y payload
        
    Returns:
        str: Cadena formateada con emojis y HTML
    """
    timestamp = log.created_at.strftime("%Y-%m-%d %H:%M")
    user_info = f"@{log.user.username}" if log.user and log.user.username else f"ID:{log.user_id}" if log.user_id else "SYSTEM"
    
    # Extraer detalles del payload si existen
    details = ""
    if log.payload and isinstance(log.payload, dict):
        details = log.payload.get("details", "")
        if details and len(details) > 50:
            details = details[:47] + "..."
    
    entry = (
        f"⏰ <b>{timestamp} UTC</b>\n"
        f"👤 {user_info}\n"
        f"🔹 <code>{log.action}</code>"
    )
    
    if details:
        entry += f"\n📝 {details}"
    
    return entry