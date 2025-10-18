# utils/helpers.py

"""
Utilitarios generales para el bot uSipipo.

Este módulo contiene funciones auxiliares para manejo de mensajes,
logging estructurado, notificaciones, formateo de datos y validaciones.
Todas las funciones siguen la arquitectura async del proyecto.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List, Tuple, Union
import traceback
import logging
import html
import io
from datetime import datetime, timezone
from telegram import Update, Bot, InputFile, InlineKeyboardMarkup
from telegram.constants import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import AsyncSessionLocal
from database.crud import users as crud_users, logs as crud_logs
from database import models

logger = logging.getLogger("usipipo.helpers")


# -------------------------
# Mensajes de respuesta (siempre HTML)
# -------------------------
async def send_usage_error(update: Update, command: str, usage: str) -> None:
    """
    Envía un mensaje de error de uso incorrecto del comando.

    Args:
        update: Objeto Update de Telegram.
        command: Nombre del comando sin barra.
        usage: Ejemplo de uso correcto.

    Returns:
        None

    Example:
        await send_usage_error(update, "vpn", "<tipo> [meses]")
    """
    if not update.message:
        return
    await update.message.reply_text(
        f"⚠️ Uso incorrecto de /{command}\n\n"
        f"Ejemplo correcto:\n<code>/{command} {usage}</code>",
        parse_mode=ParseMode.HTML,
    )


async def send_permission_error(update: Update, required_role: str = "admin") -> None:
    """
    Envía un mensaje de error de permisos insuficientes.

    Args:
        update: Objeto Update de Telegram.
        required_role: Rol requerido para la operación.

    Returns:
        None

    Example:
        await send_permission_error(update, "superadmin")
    """
    if not update.message:
        return
    await update.message.reply_text(
        f"⛔ No tienes permisos suficientes. Se requiere rol: <b>{required_role}</b>",
        parse_mode=ParseMode.HTML,
    )


async def send_generic_error(update: Update, public_message: str = "Ha ocurrido un error inesperado") -> None:
    """
    Envía un mensaje de error genérico al usuario.

    Args:
        update: Objeto Update de Telegram.
        public_message: Mensaje público a mostrar (sin detalles técnicos).

    Returns:
        None

    Example:
        await send_generic_error(update, "Error al procesar la solicitud")
    """
    if not update.message:
        return
    await update.message.reply_text(f"⚠️ {public_message}", parse_mode=ParseMode.HTML)


async def send_warning(update: Update, message: str) -> None:
    """
    Envía un mensaje de advertencia al usuario.

    Args:
        update: Objeto Update de Telegram.
        message: Mensaje de advertencia.

    Returns:
        None

    Example:
        await send_warning(update, "Tu VPN expira pronto")
    """
    if not update.message:
        return
    await update.message.reply_text(f"⚠️ {message}", parse_mode=ParseMode.HTML)


async def send_success(update: Update, message: str) -> None:
    """
    Envía un mensaje de éxito al usuario.

    Args:
        update: Objeto Update de Telegram.
        message: Mensaje de confirmación.

    Returns:
        None

    Example:
        await send_success(update, "VPN creada exitosamente")
    """
    if not update.message:
        return
    await update.message.reply_text(f"✅ {message}", parse_mode=ParseMode.HTML)


async def send_info(update: Update, message: str) -> None:
    """
    Envía un mensaje informativo al usuario.

    Args:
        update: Objeto Update de Telegram.
        message: Mensaje informativo.

    Returns:
        None

    Example:
        await send_info(update, "Tu perfil ha sido actualizado")
    """
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
    *,
    action: str,
    details: str,
    message: str,
    parse_mode: Union[str, ParseMode] = ParseMode.HTML,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> None:
    """
    Registra auditoría unificada: DB, logger y notificación al usuario.

    Args:
        session: Sesión de base de datos async (opcional).
        bot: Instancia del bot de Telegram (opcional).
        chat_id: ID del chat para notificación (opcional).
        user_id: ID del usuario como string UUID (opcional).
        action: Acción realizada para auditoría.
        details: Detalles descriptivos de la acción.
        message: Mensaje a enviar al usuario.
        parse_mode: Modo de parseo del mensaje (HTML por defecto).

    Returns:
        None

    Note:
        - Registra en DB si session provista (commit=False).
        - Siempre registra en logger central.
        - Envía mensaje si bot y chat_id provistos.

    Example:
        await log_and_notify(
            session=session,
            bot=bot,
            chat_id=chat_id,
            user_id=user_id,
            action="vpn_created",
            details="VPN WireGuard creada",
            message="✅ VPN creada exitosamente"
        )
    """
    # 1) Audit DB
    if session is not None:
        try:
            payload = {"details": details, "timestamp": datetime.now(timezone.utc).isoformat()}
            await crud_logs.create_audit_log(session=session, user_id=user_id, action=action, payload=payload, commit=False)
        except Exception:
            logger.exception("audit_log_failed", extra={"user_id": user_id})

    # 2) Logger central
    extra_uid = user_id if user_id is not None else None
    logger.info("%s | %s", action, details, extra={"user_id": extra_uid})

    # 3) Enviar mensaje
    if bot is not None and chat_id is not None:
        try:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode, reply_markup=reply_markup)
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
    *,
    action: str,
    error: Exception,
    public_message: str = "Ha ocurrido un error inesperado. El equipo ha sido notificado.",
    notify_user: bool = True,
) -> None:
    """
    Registra errores de forma estructurada con notificación limitada al usuario.

    Args:
        session: Sesión de base de datos async (opcional).
        bot: Instancia del bot de Telegram (opcional).
        chat_id: ID del chat para notificación (opcional).
        user_id: ID del usuario como string UUID (opcional).
        action: Acción que causó el error.
        error: Excepción capturada.
        public_message: Mensaje público para el usuario (sin detalles técnicos).
        notify_user: Si enviar notificación al usuario.

    Returns:
        None

    Note:
        - Registra en DB con payload truncado si session provista.
        - Logger incluye stacktrace completo.
        - Usuario recibe mensaje público sin detalles técnicos.

    Example:
        try:
            # código que puede fallar
            pass
        except Exception as e:
            await log_error_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=user_id,
                action="vpn_creation",
                error=e
            )
    """
    # Prepare details (limit size for DB)
    tb = traceback.format_exc()
    details = f"{str(error)}\n{tb}"
    truncated = details if len(details) <= 2000 else details[:2000] + " ... [truncated]"
    payload = {
        "details": details,
        "error": str(error),
        "trace": truncated,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # 1) Audit DB
    if session is not None:
        try:
            await crud_logs.create_audit_log(session=session, user_id=user_id, action=f"{action}_error", payload=payload, commit=False)
        except Exception:
            logger.exception("audit_log_failed_on_error", extra={"user_id": user_id})

    # 2) Logger central (full stacktrace)
    extra_uid = user_id if user_id is not None else None
    logger.exception("%s_error | %s", action, error, extra={"user_id": extra_uid})

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
    *,
    message: str,
    action: str = "notify_admins",
    details: Optional[str] = None,
    parse_mode: Union[str, ParseMode] = ParseMode.HTML,
) -> None:
    """
    Envía notificación a todos los administradores y superadministradores.

    Args:
        session: Sesión de base de datos async (opcional).
        bot: Instancia del bot de Telegram.
        message: Mensaje a enviar a los admins.
        action: Acción para auditoría.
        details: Detalles adicionales para auditoría.
        parse_mode: Modo de parseo del mensaje.

    Returns:
        None

    Note:
        Registra la acción en auditoría si session provista.
        Envía mensaje a todos los admins encontrados.
        Ignora fallos individuales de envío.

    Example:
        await notify_admins(
            session=session,
            bot=bot,
            message="🚨 Sistema requiere atención",
            action="system_alert",
            details="Error crítico en VPN service"
        )
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
            payload = {
                "details": details or message,
                "admin_count": len(admins),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await crud_logs.create_audit_log(session=session, user_id=None, action=action, payload=payload, commit=False)
        except Exception:
            logger.exception("audit_log_failed_on_notify_admins", extra={"user_id": None})

    logger.info("%s | notifying %d admins", action, len(admins), extra={"user_id": None})

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
    """
    Formatea cantidad de días en singular o plural.

    Args:
        days: Número de días.

    Returns:
        str: Texto formateado.

    Example:
        format_days(1)  # "1 día"
        format_days(5)  # "5 días"
    """
    return f"{days} día" if days == 1 else f"{days} días"


def safe_chat_id_from_update(update: Update) -> Optional[int]:
    """
    Extrae el chat_id de forma segura desde un Update de Telegram.

    Args:
        update: Objeto Update de Telegram.

    Returns:
        Optional[int]: ID del chat o None si no disponible.

    Example:
        chat_id = safe_chat_id_from_update(update)
        if chat_id:
            await bot.send_message(chat_id=chat_id, text="Hola")
    """
    if update.effective_chat:
        return update.effective_chat.id
    return None


async def format_roles_list(roles: List[Tuple[str, Optional[datetime]]]) -> str:
    """
    Formatea una lista de roles activos en HTML para mostrar al usuario.

    Args:
        roles: Lista de tuplas (role_name, expires_at).

    Returns:
        str: Texto formateado en HTML.

    Example:
        roles = [("admin", None), ("premium", datetime(2024, 12, 31))]
        html_text = await format_roles_list(roles)
    """
    if not roles:
        return "<b>No tienes roles activos.</b>"

    lines = [
        f"• <b>{html.escape(role_name)}</b> "
        f"(expira: {expires_at.strftime('%Y-%m-%d') if expires_at else 'sin expiración'})"
        for role_name, expires_at in roles
    ]
    return "<b>Tus roles activos:</b>\n" + "\n".join(lines)


async def format_vpn_list(vpns: List[models.VPNConfig]) -> str:
    """
    Formatea lista de configuraciones VPN en HTML para mostrar al usuario.

    Args:
        vpns: Lista de objetos VPNConfig.

    Returns:
        str: Texto formateado en HTML.

    Example:
        vpns = await vpn_service.list_user_vpns(session, user_id)
        html_text = await format_vpn_list(vpns)
    """
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


# Send VPN config

async def send_vpn_config(
    update: Update,
    vpn: models.VPNConfig,
    qr_bytes: Optional[bytes] = None,
    conf_file: Optional[InputFile] = None,
) -> None:
    """
    Envía la configuración de VPN al usuario según el tipo soportado.

    Args:
        update: Objeto Update de Telegram.
        vpn: Instancia de VPNConfig con los datos de configuración.
        qr_bytes: Bytes de la imagen QR (solo para WireGuard).
        conf_file: Archivo .conf como InputFile (solo para WireGuard).

    Returns:
        None

    Raises:
        Exception: Si hay error en el envío de mensajes/documentos.

    Note:
        Soporta tipos: wireguard, outline.
        Para WireGuard envía QR y archivo .conf.
        Para Outline envía la URL de acceso.

    Example:
        qr_bytes, conf_file = await wireguard_service.generate_config_files(vpn)
        await send_vpn_config(update, vpn, qr_bytes, conf_file)
    """
    if not update.message:
        return

    chat_id = safe_chat_id_from_update(update)
    bot = update.message.bot

    expires_str = vpn.expires_at.strftime("%Y-%m-%d %H:%M UTC") if vpn.expires_at else "N/A"

    if vpn.vpn_type == "wireguard":

        # MENSAJE DE INTRODUCCIÓN PARA WIREGUARD
        msg = (
            f"🚀 ¡Tu VPN WireGuard está lista! Expira el <code>{expires_str}</code>.\n\n"
            f"1. Descarga la app <b>WireGuard</b>.\n"
            f"2. Escanea el <b>código QR</b> o descarga el archivo <b>.conf</b> adjunto.\n"
            f"3. ¡Conéctate!"
        )
        await bot.send_message(chat_id, msg, parse_mode=ParseMode.HTML)

        # ENVÍO DEL ARCHIVO .CONF
        if conf_file:
            await bot.send_document(
                chat_id,
                document=conf_file,
                caption="Archivo de configuración WireGuard (.conf)"
            )

        # ENVÍO DEL CÓDIGO QR
        if qr_bytes:
            await bot.send_photo(
                chat_id,
                photo=InputFile(io.BytesIO(qr_bytes), filename=f"{vpn.config_name}.png"),
                caption="Código QR (para escanear directamente con la app WireGuard)"
            )

    elif vpn.vpn_type == "outline":

        # MENSAJE Y ENVÍO DE KEY PARA OUTLINE
        access_url = vpn.config_data
        if access_url:
            msg = (
                f"🚀 ¡Tu VPN Outline está lista! Expira el <code>{expires_str}</code>.\n\n"
                f"1. Descarga la app <b>Outline</b>.\n"
                f"2. Copia la clave de acceso que se muestra a continuación:\n\n"
                f"🔑 <code>{html.escape(access_url)}</code>\n\n"
                f"3. Abre la app Outline y añade la clave."
            )
            await bot.send_message(chat_id, msg, parse_mode=ParseMode.HTML)
        else:
            await bot.send_message(
                chat_id,
                "⚠️ Error: No se encontró la URL de acceso de Outline.",
                parse_mode=ParseMode.HTML
            )

    else:
        # TIPO NO SOPORTADO
        await bot.send_message(
            chat_id,
            "⚠️ No se puede entregar la configuración. Tipo de VPN no reconocido.",
            parse_mode=ParseMode.HTML
        )

    await bot.send_message(
        chat_id,
        f"💡 Usa /myvpns para ver tus configuraciones.",
        parse_mode=ParseMode.HTML
    )


async def format_expiration_message(vpn: models.VPNConfig) -> str:
    """
    Formatea mensaje de expiración de VPN en HTML.

    Args:
        vpn: Instancia de VPNConfig que está expirando.

    Returns:
        str: Mensaje formateado en HTML.

    Example:
        message = await format_expiration_message(vpn)
        await bot.send_message(chat_id, message, parse_mode=ParseMode.HTML)
    """
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
    Formatea una entrada de log para mostrarla en el chat de Telegram.

    Args:
        log: Objeto de log con campos created_at, user, user_id, action, payload.

    Returns:
        str: Cadena formateada con emojis y HTML.

    Example:
        logs = await audit_service.get_logs(limit=10)
        for log in logs:
            message = format_log_entry(log)
            await update.message.reply_text(message, parse_mode=ParseMode.HTML)
    """
    timestamp = log.created_at.strftime("%Y-%m-%d %H:%M")
    user_info = (
        f"@{log.user.username}" if log.user and log.user.username
        else f"ID:{log.user_id}" if log.user_id
        else "SYSTEM"
    )

    # Extraer detalles del payload si existen
    details = ""
    if log.payload and isinstance(log.payload, dict):
        details = log.payload.get("details", "")
        if details and len(details) > 50:
            details = details[:47] + "..."

    entry = (
        f"⏰ <b>{timestamp} UTC</b>\n"
        f"👤 {user_info}\n"
        f"🔹 <code>{html.escape(log.action)}</code>"
    )

    if details:
        entry += f"\n📝 {html.escape(details)}"

    return entry




def format_file_size(bytes_size: int) -> str:
    """
    Formatea tamaño en bytes a formato legible (KB, MB, GB).

    Args:
        bytes_size: Tamaño en bytes.

    Returns:
        str: Tamaño formateado con unidad apropiada.

    Example:
        format_file_size(1024)      # "1.0 KB"
        format_file_size(1048576)   # "1.0 MB"
    """
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"


def validate_vpn_type(vpn_type: str) -> bool:
    """
    Valida que el tipo de VPN sea uno de los soportados por el sistema.

    Args:
        vpn_type: Tipo de VPN a validar.

    Returns:
        bool: True si es válido, False en caso contrario.

    Example:
        if validate_vpn_type("wireguard"):
            # crear VPN WireGuard
            pass
    """
    from database.models import VPN_TYPES
    return vpn_type in VPN_TYPES


def validate_ip_type(ip_type: str) -> bool:
    """
    Valida que el tipo de IP sea uno de los soportados por el sistema.

    Args:
        ip_type: Tipo de IP a validar.

    Returns:
        bool: True si es válido, False en caso contrario.

    Example:
        if validate_ip_type("wireguard_trial"):
            # asignar IP para trial WireGuard
            pass
    """
    from database.models import IP_TYPES
    return ip_type in IP_TYPES