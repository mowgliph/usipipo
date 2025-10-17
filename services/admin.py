# services/admin.py

from __future__ import annotations
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import models
from database.crud import users as crud_users
from database.crud import roles as crud_roles
from database.crud import logs as crud_logs
from database.crud import vpn as crud_vpn

logger = logging.getLogger("usipipo.services.admin")

async def list_users_paginated(
    session: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> List[models.User]:
    return await crud_users.list_users(session, limit=limit)

async def get_user_details(
    session: AsyncSession,
    user_id: str,
) -> Dict[str, Any]:
    """
    Recopila información relevante de un usuario:
    - user (models.User)
    - vpnconfigs (List[VPNConfig])
    - payments (List[Payment])
    - roles (List[(name, expires_at)])
    - recent_logs (List[AuditLog])
    """
    try:
        user = await crud_users.get_user_by_pk(session, user_id)
        if not user:
            return {"user": None}

        vpnconfigs = await crud_vpn.get_vpn_configs_for_user(session, user_id)
        payments = user.payments  # Usar relación directa
        roles = await crud_roles.get_active_roles(session, user_id)
        recent_logs = await crud_logs.get_audit_logs(session, user_id=user.id, limit=20)

        return {
            "user": user,
            "vpnconfigs": vpnconfigs,
            "payments": payments,
            "roles": roles,
            "recent_logs": recent_logs,
        }
    except SQLAlchemyError:
        logger.exception("Error en get_user_details", extra={"user_id": user_id})
        raise

async def promote_to_admin(
    session: AsyncSession,
    target_user_id: str,
    acting_user_id: Optional[str] = None,
    *,
    commit: bool = True,
) -> models.User:
    """
    Marca a target_user como is_admin=True y crea AuditLog.
    - acting_user_id: quien realizó la acción (puede ser None -> SYSTEM)
    - commit: si True hace commit() al finalizar (por defecto True)
    """
    try:
        user = await crud_users.get_user_by_pk(session, target_user_id)
        if not user:
            raise ValueError("user_not_found")

        user = await crud_users.set_user_admin(session, user_id=target_user_id, is_admin=True, commit=False)
        await crud_logs.create_audit_log(
            session,
            user_id=acting_user_id,
            action="admin.promote",
            payload={"target_user_id": target_user_id, "action": "promote", "by": acting_user_id},
            commit=False,
        )

        if commit:
            try:
                await session.commit()
                await session.refresh(user)
            except IntegrityError:
                await session.rollback()
                logger.exception("IntegrityError al promover a admin", extra={"user_id": acting_user_id})
                raise
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("DB error al promover a admin", extra={"user_id": acting_user_id})
                raise

        logger.info("Usuario promovido a admin", extra={"user_id": acting_user_id, "target_user_id": target_user_id})
        return user
    except Exception:
        logger.exception("Error en promote_to_admin", extra={"user_id": acting_user_id})
        raise

async def demote_from_admin(
    session: AsyncSession,
    target_user_id: str,
    acting_user_id: Optional[str] = None,
    *,
    commit: bool = True,
) -> models.User:
    try:
        user = await crud_users.get_user_by_pk(session, target_user_id)
        if not user:
            raise ValueError("user_not_found")

        user = await crud_users.set_user_admin(session, user_id=target_user_id, is_admin=False, commit=False)
        await crud_logs.create_audit_log(
            session,
            user_id=acting_user_id,
            action="admin.demote",
            payload={"target_user_id": target_user_id, "action": "demote", "by": acting_user_id},
            commit=False,
        )

        if commit:
            try:
                await session.commit()
                await session.refresh(user)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("DB error al despromover admin", extra={"user_id": acting_user_id})
                raise

        logger.info("Usuario despromovido de admin", extra={"user_id": acting_user_id, "target_user_id": target_user_id})
        return user
    except Exception:
        logger.exception("Error en demote_from_admin", extra={"user_id": acting_user_id})
        raise

async def set_superadmin(
    session: AsyncSession,
    target_user_id: str,
    acting_user_id: Optional[str] = None,
    *,
    commit: bool = True,
) -> models.User:
    """
    Marca a target_user como is_superadmin=True (y is_admin=True) y crea AuditLog.
    - acting_user_id: quien realizó la acción (puede ser None -> SYSTEM)
    - commit: si True hace commit() al finalizar (por defecto True)
    """
    try:
        user = await crud_users.get_user_by_pk(session, target_user_id)
        if not user:
            raise ValueError("user_not_found")

        user = await crud_users.set_user_superadmin(session, user_id=target_user_id, is_superadmin=True, commit=False)
        await crud_logs.create_audit_log(
            session,
            user_id=acting_user_id,
            action="admin.setsuper",
            payload={"target_user_id": target_user_id, "action": "setsuper", "by": acting_user_id},
            commit=False,
        )

        if commit:
            try:
                await session.commit()
                await session.refresh(user)
            except IntegrityError:
                await session.rollback()
                logger.exception("IntegrityError al asignar superadmin", extra={"user_id": acting_user_id})
                raise
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("DB error al asignar superadmin", extra={"user_id": acting_user_id})
                raise

        logger.info("Usuario asignado como superadmin", extra={"user_id": acting_user_id, "target_user_id": target_user_id})
        return user
    except Exception:
        logger.exception("Error en set_superadmin", extra={"user_id": acting_user_id})
        raise

async def assign_role_to_user(
    session: AsyncSession,
    target_user_id: str,
    role_name: str,
    acting_user_id: Optional[str] = None,
    *,
    expires_at: Optional[datetime] = None,
    commit: bool = True,
) -> models.UserRole:
    try:
        user_role = await crud_roles.grant_role(
            session,
            user_id=target_user_id,
            role_name=role_name,
            expires_at=expires_at,
            granted_by=acting_user_id,
            commit=False,
        )
        await crud_logs.create_audit_log(
            session,
            user_id=acting_user_id,
            action="role.grant",
            payload={"role": role_name, "target_user_id": target_user_id, "by": acting_user_id},
            commit=False,
        )
        if commit:
            try:
                await session.commit()
                await session.refresh(user_role)
            except IntegrityError:
                await session.rollback()
                logger.exception("IntegrityError en assign_role_to_user", extra={"user_id": acting_user_id})
                raise
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("DB error en assign_role_to_user", extra={"user_id": acting_user_id})
                raise

        logger.info("Role asignado", extra={"user_id": acting_user_id, "target_user_id": target_user_id, "role": role_name})
        return user_role
    except Exception:
        logger.exception("Error en assign_role_to_user", extra={"user_id": acting_user_id})
        raise

async def revoke_role_from_user(
    session: AsyncSession,
    target_user_id: str,
    role_name: str,
    acting_user_id: Optional[str] = None,
    *,
    commit: bool = True,
) -> bool:
    try:
        result = await crud_roles.revoke_role(session, user_id=target_user_id, role_name=role_name, commit=False)
        await crud_logs.create_audit_log(
            session,
            user_id=acting_user_id,
            action="role.revoke",
            payload={"role": role_name, "target_user_id": target_user_id, "by": acting_user_id},
            commit=False,
        )
        if commit:
            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("DB error en revoke_role_from_user", extra={"user_id": acting_user_id})
                raise

        logger.info("Role revocado", extra={"user_id": acting_user_id, "target_user_id": target_user_id, "role": role_name})
        return result
    except Exception:
        logger.exception("Error en revoke_role_from_user", extra={"user_id": acting_user_id})
        raise

async def list_admins(session: AsyncSession) -> List[models.User]:
    """
    Lista todos los usuarios que son administradores o superadministradores.
    """
    try:
        admins = await crud_users.get_admins(session)
        return admins
    except SQLAlchemyError:
        logger.exception("Error en list_admins", extra={"user_id": None})
        raise

