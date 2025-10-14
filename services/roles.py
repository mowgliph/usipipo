# services/roles.py

from __future__ import annotations
from typing import Optional, List, Tuple
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from database import models
from database.crud import roles as crud_roles
from database.crud import users as crud_users
from utils.helpers import notify_admins
import logging

logger = logging.getLogger("usipipo.services.roles")

ALLOWED_ROLES = {"normal", "premium", "vip"}  # Lista de roles permitidos


async def grant_role(
    session: AsyncSession,
    target_tg_id: str,
    role_name: str,
    days: Optional[int] = None,
    granted_by: Optional[str] = None,
) -> Optional[models.UserRole]:
    """
    Asigna un rol a un usuario. Crea el rol si no existe.
    - target_tg_id: Telegram ID del usuario objetivo.
    - role_name: Nombre del rol (valida contra ALLOWED_ROLES).
    - days: Si se proporciona, calcula expires_at.
    - granted_by: UUID del usuario que otorga (None para SYSTEM).
    Retorna UserRole creado o None si falla.
    """
    try:
        if role_name.lower() not in ALLOWED_ROLES:
            logger.warning(f"Intento de asignar rol no permitido: {role_name}", extra={"user_id": granted_by})
            return None

        # Obtener UUID del usuario objetivo
        target_user = await crud_users.get_user_by_telegram_id(session, int(target_tg_id))
        if not target_user:
            logger.warning(f"Usuario no encontrado: telegram_id={target_tg_id}", extra={"user_id": granted_by})
            return None

        # Evitar auto-asignación
        if granted_by and target_user.id == granted_by:
            logger.warning("Intento de auto-asignación de rol", extra={"user_id": granted_by})
            return None

        expires_at = datetime.utcnow() + timedelta(days=days) if days else None
        user_role = await crud_roles.grant_role(
            session,
            user_id=target_user.id,
            role_name=role_name.lower(),
            expires_at=expires_at,
            granted_by=granted_by,
            commit=False,
        )
        return user_role
    except SQLAlchemyError as e:
        logger.exception(f"Fallo al asignar rol {role_name} a telegram_id={target_tg_id}", extra={"user_id": granted_by})
        await notify_admins(
            session=session,
            bot=None,  # Bot debe ser pasado por el handler
            message=f"Error crítico al asignar rol {role_name} a telegram_id={target_tg_id}: {str(e)}",
            action="grant_role_error",
        )
        raise
    except ValueError:
        logger.warning(f"telegram_id inválido: {target_tg_id}", extra={"user_id": granted_by})
        return None


async def revoke_role(
    session: AsyncSession,
    target_tg_id: str,
    role_name: str,
) -> bool:
    """
    Revoca un rol activo de un usuario.
    - target_tg_id: Telegram ID del usuario objetivo.
    - role_name: Nombre del rol.
    Retorna True si se revocó, False si no existía.
    """
    try:
        target_user = await crud_users.get_user_by_telegram_id(session, int(target_tg_id))
        if not target_user:
            logger.warning(f"Usuario no encontrado: telegram_id={target_tg_id}", extra={"user_id": None})
            return False

        return await crud_roles.revoke_role(session, user_id=target_user.id, role_name=role_name.lower(), commit=False)
    except SQLAlchemyError as e:
        logger.exception(f"Fallo al revocar rol {role_name} de telegram_id={target_tg_id}", extra={"user_id": None})
        await notify_admins(
            session=session,
            bot=None,  # Bot debe ser pasado por el handler
            message=f"Error crítico al revocar rol {role_name} de telegram_id={target_tg_id}: {str(e)}",
            action="revoke_role_error",
        )
        raise
    except ValueError:
        logger.warning(f"telegram_id inválido: {target_tg_id}", extra={"user_id": None})
        return False


async def get_user_roles(session: AsyncSession, user_id: str) -> List[Tuple[str, Optional[datetime]]]:
    """
    Devuelve los roles activos (no expirados) del usuario.
    - user_id: UUID del usuario.
    Retorna lista de tuplas (role_name, expires_at).
    """
    try:
        return await crud_roles.get_active_roles(session, user_id)
    except SQLAlchemyError as e:
        logger.exception(f"No se pudieron obtener roles del usuario {user_id}", extra={"user_id": user_id})
        await notify_admins(
            session=session,
            bot=None,  # Bot debe ser pasado por el handler
            message=f"Error crítico al obtener roles del usuario {user_id}: {str(e)}",
            action="get_user_roles_error",
        )
        raise


async def assign_role_on_purchase(
    session: AsyncSession,
    target_tg_id: str,
    duration_months: int,
    config_id: str,
    granted_by: Optional[str] = None,
) -> dict:
    """
    Asigna un rol según la duración contratada y aplica bonus.
    - target_tg_id: Telegram ID del usuario.
    - duration_months: Duración de la suscripción.
    - config_id: ID de la configuración VPN.
    Retorna dict con rol asignado, bonus y config_id.
    """
    bonus_months = 0
    role = None

    if duration_months >= 24:
        role = "vip"
        bonus_months = 6
    elif duration_months == 12:
        role = "vip"
        bonus_months = 2
    elif 4 <= duration_months <= 11:
        role = "premium"
    elif 1 <= duration_months <= 2:
        role = "normal"

    if role:
        try:
            days = 30 * (duration_months + bonus_months)
            user_role = await grant_role(session, target_tg_id, role, days=days, granted_by=granted_by)
            if user_role:
                logger.info(
                    f"Asignado rol '{role}' a telegram_id={target_tg_id} por {duration_months}+{bonus_months} meses",
                    extra={"user_id": granted_by},
                )
        except SQLAlchemyError as e:
            logger.exception(f"No se pudo asignar rol {role} a telegram_id={target_tg_id}", extra={"user_id": granted_by})
            await notify_admins(
                session=session,
                bot=None,  # Bot debe ser pasado por el handler
                message=f"Error crítico al asignar rol por compra {role} a telegram_id={target_tg_id}: {str(e)}",
                action="assign_role_on_purchase_error",
            )
            raise

    return {
        "role": role,
        "bonus_months": bonus_months,
        "config_id": config_id,
    }