# services/activation_vpn.py

from __future__ import annotations
from typing import Optional, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from database import models
from services import wireguard as wireguard_service, outline as outline_service
from database.crud import logs as crud_logs

logger = logging.getLogger(__name__)

async def list_user_vpns(session: AsyncSession, user_id: str) -> list[models.VPNConfig]:
    """Lista todas las VPNs de un usuario."""
    try:
        from database.crud import vpn as crud_vpn
        vpns = await crud_vpn.get_vpn_configs_for_user(session, user_id)
        return vpns
    except SQLAlchemyError as e:
        logger.exception(f"Error listando VPNs para user {user_id}", extra={"user_id": user_id})
        raise

async def activate_vpn_for_user(
    session: AsyncSession,
    user_id: str,
    vpn_type: Literal["wireguard", "outline"],
    months: int,
) -> Optional[models.VPNConfig]:
    """
    Crea o renueva una VPN según el tipo especificado.
    - user_id: UUID str
    - vpn_type: 'wireguard' | 'outline'
    - months: duración
    Retorna VPNConfig creado o None si falla.
    Nota: El commit de la transacción debe manejarse en el handler.
    """
    try:
        if vpn_type == "wireguard":
            result = await wireguard_service.create_peer(session, user_id=user_id, duration_months=months, commit=False)
            vpn_obj = result.get("vpn")  # Estandarizado a clave "vpn"
        elif vpn_type == "outline":
            result = await outline_service.create_access(session, user_id=user_id, duration_months=months)
            vpn_obj = result.get("vpn") or result.get("vpn_obj")  # Soporta ambas claves por compatibilidad
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
                details=f"No se creó VPN {vpn_type}",
                payload={"vpn_type": vpn_type, "months": months},
                commit=False,
            )
        return vpn_obj
    except (SQLAlchemyError, ValueError) as e:
        logger.exception(f"❌ Error activando VPN ({vpn_type}) para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="vpn_activation_error",
            details=str(e),
            payload={"vpn_type": vpn_type, "months": months},
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
                details=f"VPN {vpn_type} ID {vpn_id} revocada",
                payload={"vpn_id": vpn_id, "vpn_type": vpn_type},
                commit=False,
            )
        else:
            logger.error(f"❌ No se encontró VPN {vpn_type} ID {vpn_id}", extra={"user_id": None, "vpn_id": vpn_id})
            await crud_logs.create_audit_log(
                session=session,
                user_id=None,
                action="vpn_revoke_failed",
                details=f"No se encontró VPN {vpn_type} ID {vpn_id}",
                payload={"vpn_id": vpn_id, "vpn_type": vpn_type},
                commit=False,
            )
        return vpn_obj
    except (SQLAlchemyError, ValueError) as e:
        logger.exception(f"❌ Error revocando VPN ({vpn_type}) ID {vpn_id}: {e}", extra={"user_id": None, "vpn_id": vpn_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=None,
            action="vpn_revoke_error",
            details=str(e),
            payload={"vpn_id": vpn_id, "vpn_type": vpn_type},
            commit=False,
        )
        raise