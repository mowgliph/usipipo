# services/trial_service.py

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from telegram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from database import models
from database.crud import users as crud_users, vpn as crud_vpn, logs as crud_logs
from utils import helpers
from services import wireguard, outline

logger = logging.getLogger("usipipo")


async def build_vpn_config_payload(tg_user: Dict[str, Any], vpntype: str) -> Dict[str, Any]:
    """
    Construye un payload básico para la creación de la configuración VPN.
    No contiene secretos reales; wireguard/outline service deben generar claves reales.
    Devuelve: {"config_name": str, "config_data": str, "extra_data": dict}
    """
    username = tg_user.get("username") or f"{tg_user.get('first_name','user')}_{tg_user.get('id')}"
    config_name = f"{username}_{vpntype}_trial_{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    config_data = f"placeholder-config-for-{username}-{vpntype}"
    extra_data = {
        "created_by_tg_id": tg_user.get("id"),
        "created_by_username": tg_user.get("username"),
        "purpose": "trial",
    }
    return {"config_name": config_name, "config_data": config_data, "extra_data": extra_data}


async def start_trial(
    session: AsyncSession,
    bot: Bot,
    tg_user: Dict[str, Any],
    vpntype: str = "wireguard",
    duration_days: int = 7,
) -> Dict[str, Any]:
    """
    Inicia un trial VPN para tg_user.
    Flujo:
      - Asegura User en DB
      - Verifica trial activo
      - Construye payload y crea recursos específicos (wireguard/outline)
      - Crea VPNConfig mediante crud_vpn.create_vpn_config (commit controlable)
      - Registra AuditLog y notifica usuario y admins
    Retorno mínimo:
      {"ok": bool, "reason": Optional[str], "vpn": Optional[models.VPNConfig], "message": str}
    """
    chat_id = helpers.safe_chat_id_from_update(tg_user.get("_update")) if isinstance(tg_user.get("_update"), dict) else None
    # Normalmente tg_user proviene de Telegram update: aseguramos keys mínimas
    try:
        # 1) Asegurar usuario en DB
        # tg_user dict esperado: {"id": int, "username": str|None, "first_name": str|None, "last_name": str|None}
        user = await crud_users.ensure_user(session, tg_user, commit=True)
        user_id = user.id

        # 2) Comprobar trial activo
        if await crud_vpn.has_trial(session, user_id):
            # auditar intento y notificar al usuario (sin crear)
            await crud_logs.create_audit_log(session=session, user_id=user_id, action="trial_denied", payload={"vpntype": vpntype, "reason": "active_trial_exists"})
            await helpers.log_and_notify(session=session, bot=bot, chat_id=chat_id, user_id=user_id,
                                         action="trial_denied",
                                         details=f"user has active trial",
                                         message=f"⚠️ Ya tienes un trial activo. No puedes crear otro hasta que expire.")
            return {"ok": False, "reason": "user_has_active_trial", "vpn": None, "message": "Ya tienes un trial activo."}

        # 3) Construir payload
        payload = await build_vpn_config_payload(tg_user, vpntype)
        expires_at = datetime.utcnow() + timedelta(days=duration_days)

        # 4) Crear recursos específicos de VPN dentro de una transacción
        async with session.begin():
            # generar recursos externos según tipo
            if vpntype == "wireguard":
                # wireguard.create_peer debe ser async y devolver data necesaria
                wg_result = await wireguard.create_peer(session, user_id=int(user_id), config_name=payload["config_name"])
                config_data = wg_result.get("config_data") or payload["config_data"]
                extra_data = {**payload["extra_data"], **wg_result.get("extra_data", {})}
            elif vpntype == "outline":
                ol_result = await outline.create_access(session, user_id=user_id)
                config_data = ol_result.get("config_data") or payload["config_data"]
                extra_data = {**payload["extra_data"], **ol_result.get("extra_data", {})}
            else:
                raise ValueError("invalid_vpntype")

            # 5) Crear registro VPNConfig en DB usando CRUD (commit al salir del session.begin)
            vpn_obj = await crud_vpn.create_vpn_config(
                session=session,
                user_id=user_id,
                vpn_type=vpntype,
                config_name=payload["config_name"],
                config_data=config_data,
                expires_at=expires_at,
                extra_data=extra_data,
                is_trial=True,
                commit=False,  # commit controlado por session.begin
            )

            # 6) Crear audit log asociado
            await crud_logs.create_audit_log(session=session, user_id=user_id, action="trial_created",
                                            payload={"vpntype": vpntype, "vpn_id": getattr(vpn_obj,'id', 'pending')})
            # Al salir del async with session.begin() se hará commit automático

        # 7) Post-commit notifications: log central y user notification
        await helpers.log_and_notify(session=session, bot=bot, chat_id=chat_id, user_id=user_id,
                                     action="trial_created",
                                     details=f"{vpntype} trial created for user",
                                     message=f"✅ Tu trial de {vpntype} está activo hasta {expires_at.date()}.")
        # Notificar admins si es necesario (ejemplo: nueva creación)
        await helpers.notify_admins(session=session, bot=bot,
                                    message=f"🔔 Nuevo trial {vpntype} para @{user.username or user_id}",
                                    action="notify_new_trial",
                                    details=f"user_id={user_id}; vpntype={vpntype}")

        return {"ok": True, "reason": None, "vpn": vpn_obj, "message": "Trial creado correctamente."}

    except ValueError as ve:
        # errores previstos: tipo de VPN inválido
        msg_map = {"invalid_vpntype": "Tipo de VPN no válido. Usa wireguard u outline."}
        public_msg = msg_map.get(str(ve), "Entrada inválida.")
        await crud_logs.create_audit_log(session=session, user_id=None, action="trial_failed_input", payload={"error": str(ve)})
        await helpers.log_error_and_notify(session=session, bot=bot, chat_id=chat_id, user_id=None,
                                           action="trial_failed_input", error=ve,
                                           public_message=public_msg)
        return {"ok": False, "reason": "invalid_input", "vpn": None, "message": public_msg}

    except Exception as exc:
        # errores inesperados: registrar, notificar admins y devolver mensaje genérico al usuario
        logger.exception("unexpected_error_starting_trial", extra={"user_id": None})
        await crud_logs.create_audit_log(session=session, user_id=None, action="trial_failed", payload={"error": str(exc)[:2000]})
        await helpers.log_error_and_notify(session=session, bot=bot, chat_id=chat_id, user_id=None,
                                           action="trial_failed", error=exc,
                                           public_message="Ha ocurrido un error creando tu trial. Intenta más tarde.")
        return {"ok": False, "reason": "internal_error", "vpn": None, "message": "Error interno al crear trial."}