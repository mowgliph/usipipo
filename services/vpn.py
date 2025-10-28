# services/vpn.py

from __future__ import annotations
from typing import Optional, Literal, List
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from database import models
from services import wireguard as wireguard_service, outline as outline_service
from database.crud import logs as crud_logs, vpn as crud_vpn, tunnel_domains as crud_tunnel_domains
from utils.helpers import log_error_and_notify

logger = logging.getLogger(__name__)

async def list_user_vpns(session: AsyncSession, user_id: str) -> list[models.VPNConfig]:
    """Lista todas las VPNs de un usuario."""
    try:
        vpns = await crud_vpn.get_vpn_configs_for_user(session, user_id)
        return vpns
    except SQLAlchemyError:
        logger.exception("Error listando VPNs para usuario", extra={"user_id": user_id})
        raise

async def activate_vpn_for_user(
    session: AsyncSession,
    user_id: str,
    vpn_type: Literal["wireguard", "outline"],
    months: int,
    bypass_domains: Optional[List[str]] = None,
) -> Optional[models.VPNConfig]:
    """
    Crea o renueva una VPN según el tipo especificado.
    - user_id: UUID str
    - vpn_type: 'wireguard' | 'outline'
    - months: duración
    - bypass_domains: Lista opcional de dominios para bypass (dual tunnel)
    Retorna VPNConfig creado o None si falla.
    Nota: El commit de la transacción debe manejarse en el handler.
    """
    try:
        if vpn_type == "wireguard":
            result = await wireguard_service.create_peer(session, user_id=user_id, duration_months=months, bypass_domains=bypass_domains, commit=False)
            vpn_obj = result.get("vpn")
        elif vpn_type == "outline":
            result = await outline_service.create_access(session, user_id=user_id, duration_months=months, bypass_domains=bypass_domains)
            vpn_obj = result.get("vpn") or result.get("vpn_obj")
        else:
            raise ValueError(f"Tipo VPN no soportado: {vpn_type}")

        if vpn_obj:
            logger.info(f"✅ VPN {vpn_type} activada para usuario {user_id}", extra={"user_id": user_id})
        else:
            logger.error(f"❌ No se creó VPN {vpn_type} para usuario {user_id}", extra={"user_id": user_id})
            await crud_logs.create_audit_log(
                session=session,
                user_id=user_id,
                action="vpn_activation_failed",
                payload={"vpn_type": vpn_type, "months": months, "bypass_domains": bypass_domains, "reason": "No se creó VPN"},
                commit=False,
            )
        return vpn_obj
    except ValueError:
        logger.exception(f"❌ Tipo VPN no soportado: {vpn_type}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="vpn_activation_error",
            payload={"vpn_type": vpn_type, "months": months, "bypass_domains": bypass_domains, "error": "Tipo VPN no soportado"},
            commit=False,
        )
        raise
    except SQLAlchemyError:
        logger.exception(f"❌ Error de base de datos activando VPN {vpn_type}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="vpn_activation_error",
            payload={"vpn_type": vpn_type, "months": months, "bypass_domains": bypass_domains, "error": "Error de base de datos"},
            commit=False,
        )
        raise
    except Exception as e:
        logger.exception(f"❌ Error inesperado activando VPN {vpn_type}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="vpn_activation_error",
            payload={"vpn_type": vpn_type, "months": months, "bypass_domains": bypass_domains, "error": str(e)},
            commit=False,
        )
        raise

async def revoke_vpn(
    session: AsyncSession,
    vpn_id: str,
    vpn_type: Literal["wireguard", "outline"],
) -> Optional[models.VPNConfig]:
    """
    Revoca una VPN existente según su tipo.
    Retorna VPNConfig actualizado o None si no se encuentra.
    Nota: El commit de la transacción debe manejarse en el handler.
    """
    try:
        if vpn_type == "wireguard":
            vpn_obj = await wireguard_service.revoke_peer(session, vpn_id=vpn_id, commit=False)
        elif vpn_type == "outline":
            vpn_obj = await outline_service.revoke_access(session, vpn_id=vpn_id)
        else:
            raise ValueError(f"Tipo VPN no soportado: {vpn_type}")

        if vpn_obj:
            logger.info(f"🧹 VPN {vpn_type} revocada (ID: {vpn_id})", extra={"user_id": None, "vpn_id": vpn_id})
            await crud_logs.create_audit_log(
                session=session,
                user_id=None,
                action="vpn_revoked",
                payload={"vpn_id": vpn_id, "vpn_type": vpn_type, "status": "revoked"},
                commit=False,
            )
        else:
            logger.error(f"❌ No se encontró VPN {vpn_type} ID {vpn_id}", extra={"user_id": None, "vpn_id": vpn_id})
            await crud_logs.create_audit_log(
                session=session,
                user_id=None,
                action="vpn_revoke_failed",
                payload={"vpn_id": vpn_id, "vpn_type": vpn_type, "reason": "VPN not found"},
                commit=False,
            )
        return vpn_obj
    except ValueError:
        logger.exception(f"❌ Tipo VPN no soportado: {vpn_type}", extra={"user_id": None, "vpn_id": vpn_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=None,
            action="vpn_revoke_error",
            payload={"vpn_id": vpn_id, "vpn_type": vpn_type, "error": "Tipo VPN no soportado"},
            commit=False,
        )
        raise
    except SQLAlchemyError:
        logger.exception(f"❌ Error de base de datos revocando VPN {vpn_type}", extra={"user_id": None, "vpn_id": vpn_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=None,
            action="vpn_revoke_error",
            payload={"vpn_id": vpn_id, "vpn_type": vpn_type, "error": "Error de base de datos"},
            commit=False,
        )
        raise
    except Exception as e:
        logger.exception(f"❌ Error inesperado revocando VPN {vpn_type}", extra={"user_id": None, "vpn_id": vpn_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=None,
            action="vpn_revoke_error",
            payload={"vpn_id": vpn_id, "vpn_type": vpn_type, "error": str(e)},
            commit=False,
        )
        raise


async def count_vpn_configs_by_user(session: AsyncSession, user_id: str) -> int:
    """Cuenta el número de configuraciones VPN para un usuario dado."""
    try:
        return await crud_vpn.count_vpn_configs_by_user(session, user_id)
    except SQLAlchemyError:
        logger.exception("Error counting VPN configs for user", extra={"user_id": user_id})
        return 0


async def last_vpn_config_by_user(session: AsyncSession, user_id: str) -> Optional[models.VPNConfig]:
    """Obtiene la última configuración VPN creada para un usuario dado."""
    try:
        return await crud_vpn.last_vpn_config_by_user(session, user_id)
    except SQLAlchemyError:
        logger.exception("Error getting last VPN config for user", extra={"user_id": user_id})
        return None