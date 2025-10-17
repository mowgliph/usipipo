# database/crud/roles.py
from __future__ import annotations
from typing import Optional, List, Tuple
from datetime import datetime, timezone

import logging

from sqlalchemy import select, and_, func, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database import models

logger = logging.getLogger("usipipo.crud.roles")


async def get_role_by_name(
    session: AsyncSession,
    role_name: str,
) -> Optional[models.Role]:
    """
    Obtiene un rol por su nombre.
    Retorna None si no existe.
    """
    try:
        stmt = select(models.Role).where(models.Role.name == role_name)
        result = await session.execute(stmt)
        role = result.scalars().one_or_none()
        return role
    except SQLAlchemyError:
        logger.exception("Error en get_role_by_name", extra={"role_name": role_name})
        raise


async def create_role(
    session: AsyncSession,
    name: str,
    description: Optional[str] = None,
    *,
    commit: bool = False,
) -> models.Role:
    """
    Crea un nuevo rol.
    - Si ya existe, lanza IntegrityError (manejar en capa superior).
    - commit: si True hace commit() y refresh().
    """
    try:
        role = models.Role(name=name, description=description)
        session.add(role)
        if commit:
            await session.commit()
            await session.refresh(role)
        logger.info("Role creado", extra={"role_name": name})
        return role
    except SQLAlchemyError:
        logger.exception("Error en create_role", extra={"role_name": name})
        raise


async def get_all_roles(session: AsyncSession) -> List[models.Role]:
    """
    Obtiene todos los roles disponibles.
    """
    try:
        stmt = select(models.Role).order_by(models.Role.name)
        result = await session.execute(stmt)
        roles = result.scalars().all()
        return list(roles)
    except SQLAlchemyError:
        logger.exception("Error en get_all_roles")
        raise


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
        role = await get_role_by_name(session, role_name)
        if role is None:
            role = await create_role(session, role_name, f"Rol {role_name}", commit=False)
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
    Revoca un role dado por su nombre para un usuario (elimina todos los UserRole asociados).
    - Retorna True si se encontró y se eliminó al menos un UserRole.
    - No commitea por defecto; si commit=True hace commit().
    """
    try:
        # Buscar role
        role = await get_role_by_name(session, role_name)
        if role is None:
            logger.debug("revoke_role: role no existe", extra={"user_id": user_id, "role": role_name})
            return False

        # Eliminar user_roles relacionados (todos, sin considerar expiración)
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


async def get_user_roles(
    session: AsyncSession,
    user_id: str,
) -> List[models.UserRole]:
    """
    Obtiene todos los UserRole para un usuario (incluyendo expirados).
    """
    try:
        stmt = (
            select(models.UserRole)
            .where(models.UserRole.user_id == user_id)
            .order_by(models.UserRole.granted_at.desc())
        )
        result = await session.execute(stmt)
        user_roles = result.scalars().all()
        return list(user_roles)
    except SQLAlchemyError:
        logger.exception("Error en get_user_roles", extra={"user_id": user_id})
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


async def update_user_role_expires_at(
    session: AsyncSession,
    user_role_id: str,
    expires_at: Optional[datetime],
    *,
    commit: bool = False,
) -> bool:
    """
    Actualiza expires_at de un UserRole específico.
    - Retorna True si se actualizó (encontrado).
    - commit: si True hace commit().
    """
    try:
        stmt = (
            update(models.UserRole)
            .where(models.UserRole.id == user_role_id)
            .values(expires_at=expires_at)
        )
        result = await session.execute(stmt)
        updated = result.rowcount > 0
        if updated:
            logger.info("UserRole expires_at actualizado", extra={"user_role_id": user_role_id})
        if commit:
            await session.commit()
        return updated
    except SQLAlchemyError:
        logger.exception("Error en update_user_role_expires_at", extra={"user_role_id": user_role_id})
        raise


async def get_users_with_role(
    session: AsyncSession,
    role_name: str,
) -> List[models.User]:
    """
    Obtiene usuarios que tienen un rol activo (no expirado).
    """
    try:
        now = datetime.now(timezone.utc)
        stmt = (
            select(models.User)
            .join(models.UserRole, models.User.id == models.UserRole.user_id)
            .join(models.Role, models.UserRole.role_id == models.Role.id)
            .where(
                models.Role.name == role_name,
                (models.UserRole.expires_at.is_(None)) | (models.UserRole.expires_at > now),
            )
            .distinct()
        )
        result = await session.execute(stmt)
        users = result.scalars().all()
        return list(users)
    except SQLAlchemyError:
        logger.exception("Error en get_users_with_role", extra={"role_name": role_name})
        raise


async def delete_expired_user_roles(
    session: AsyncSession,
    *,
    commit: bool = False,
) -> int:
    """
    Elimina UserRole expirados (hard delete).
    - Retorna el número de registros eliminados.
    - commit: si True hace commit().
    - Usar con precaución; ideal para limpieza periódica.
    """
    try:
        now = datetime.now(timezone.utc)
        stmt = delete(models.UserRole).where(
            and_(models.UserRole.expires_at.isnot(None), models.UserRole.expires_at <= now)
        )
        result = await session.execute(stmt)
        deleted_count = result.rowcount
        logger.info("UserRole expirados eliminados", extra={"count": deleted_count})
        if commit:
            await session.commit()
        return deleted_count
    except SQLAlchemyError:
        logger.exception("Error en delete_expired_user_roles")
        raise