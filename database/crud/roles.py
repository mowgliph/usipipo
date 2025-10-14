# database/crud/roles.py
from __future__ import annotations
from typing import Optional, List, Tuple
from datetime import datetime, timezone

import logging

from sqlalchemy import select, and_, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database import models

logger = logging.getLogger("usipipo.crud.roles")


async def grant_role(
    session: AsyncSession,
    user_id: str,
    role_name: str,
    *,
    expires_at: Optional[datetime] = None,
    granted_by: Optional[str] = None,
    commit: bool = False,
) -> models.UserRole:
    """
    Crea Role si no existe y añade UserRole (no commitea por defecto).
    - user_id, granted_by: UUID string (granted_by puede ser None -> SYSTEM).
    - commit: si True hace commit() y refresh() antes de devolver.
    Retorna la instancia de UserRole.
    """
    try:
        # Buscar role existente
        q = await session.execute(select(models.Role).where(models.Role.name == role_name))
        role = q.scalars().one_or_none()

        if role is None:
            role = models.Role(name=role_name, description=f"Rol {role_name}")
            session.add(role)
            # flush para que role.id sea disponible sin commitear
            await session.flush()
            logger.info("Role creado", extra={"user_id": granted_by or None, "role": role_name})

        user_role = models.UserRole(
            user_id=user_id,
            role_id=role.id,
            granted_by=granted_by,
            granted_at=datetime.now(timezone.utc),
            expires_at=expires_at,
        )
        session.add(user_role)

        if commit:
            try:
                await session.commit()
                await session.refresh(user_role)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al commitear grant_role", extra={"user_id": user_id})
                raise

        logger.info("Role concedido", extra={"user_id": user_id, "role": role_name})
        return user_role
    except SQLAlchemyError:
        logger.exception("Error en grant_role", extra={"user_id": user_id})
        raise


async def revoke_role(
    session: AsyncSession,
    user_id: str,
    role_name: str,
    *,
    commit: bool = False,
) -> bool:
    """
    Revoca un role dado por su nombre para un usuario.
    - Retorna True si se encontró y se eliminó al menos un UserRole.
    - No commitea por defecto; si commit=True hace commit().
    """
    try:
        # Buscar role
        q = await session.execute(select(models.Role).where(models.Role.name == role_name))
        role = q.scalars().one_or_none()
        if role is None:
            logger.debug("revoke_role: role no existe", extra={"user_id": user_id, "role": role_name})
            return False

        # Eliminar user_roles relacionados
        stmt = select(models.UserRole).where(
            and_(models.UserRole.user_id == user_id, models.UserRole.role_id == role.id)
        )
        res = await session.execute(stmt)
        rows = res.scalars().all()
        if not rows:
            logger.debug("revoke_role: user_role no encontrado", extra={"user_id": user_id, "role": role_name})
            return False

        for ur in rows:
            await session.delete(ur)

        if commit:
            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al commitear revoke_role", extra={"user_id": user_id})
                raise

        logger.info("Role revocado", extra={"user_id": user_id, "role": role_name})
        return True
    except SQLAlchemyError:
        logger.exception("Error en revoke_role", extra={"user_id": user_id})
        raise


async def get_active_roles(
    session: AsyncSession,
    user_id: str,
) -> List[Tuple[str, Optional[datetime]]]:
    """
    Devuelve lista de tuplas (role_name, expires_at) para roles activos del usuario.
    - Considera activos los roles con expires_at IS NULL o expires_at > now (UTC).
    """
    try:
        now = datetime.now(timezone.utc)
        stmt = (
            select(models.Role.name, models.UserRole.expires_at)
            .join(models.UserRole, models.Role.id == models.UserRole.role_id)
            .where(
                models.UserRole.user_id == user_id,
                (models.UserRole.expires_at.is_(None)) | (models.UserRole.expires_at > now),
            )
        )
        res = await session.execute(stmt)
        rows = res.all()
        # rows son tuplas (name, expires_at)
        result: List[Tuple[str, Optional[datetime]]] = [(r[0], r[1]) for r in rows]
        logger.debug("get_active_roles result", extra={"user_id": user_id, "count": len(result)})
        return result
    except SQLAlchemyError:
        logger.exception("Error en get_active_roles", extra={"user_id": user_id})
        raise