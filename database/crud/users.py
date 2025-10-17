# database/crud/users.py
from __future__ import annotations
from typing import Optional, List, Dict, Any, AsyncGenerator

import logging
from datetime import datetime, timezone

from sqlalchemy import select, update, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database import models

logger = logging.getLogger("usipipo.crud.users")


async def get_user_by_pk(session: AsyncSession, user_id: str) -> Optional[models.User]:
    """Obtiene un usuario por la PK (UUID string)."""
    try:
        result = await session.execute(select(models.User).where(models.User.id == user_id))
        return result.scalars().one_or_none()
    except SQLAlchemyError:
        logger.exception("Error al obtener usuario por PK", extra={"user_id": None})
        raise


async def get_user(session: AsyncSession, user_id: int) -> Optional[models.User]:
    """Obtiene un usuario por su Telegram ID (telegram_id). Alias para get_user_by_telegram_id."""
    return await get_user_by_telegram_id(session, user_id)


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[models.User]:
    """Obtiene un usuario por su Telegram ID (telegram_id)."""
    try:
        result = await session.execute(select(models.User).where(models.User.telegram_id == telegram_id))
        user = result.scalars().one_or_none()
        logger.debug("get_user_by_telegram_id result", extra={"user_id": telegram_id})
        return user
    except SQLAlchemyError:
        logger.exception("Error al obtener usuario por telegram_id", extra={"user_id": None})
        raise


async def get_user_by_username(session: AsyncSession, username: str) -> Optional[models.User]:
    """Obtiene un usuario por su username de Telegram."""
    try:
        result = await session.execute(select(models.User).where(models.User.username == username))
        return result.scalars().one_or_none()
    except SQLAlchemyError:
        logger.exception("Error al obtener usuario por username", extra={"user_id": None})
        raise


async def create_user_from_telegram(
    session: AsyncSession,
    tg_payload: Dict[str, Any],
    commit: bool = False,
) -> models.User:
    """
    Crea un nuevo usuario desde el payload de Telegram.
    tg_payload esperado: {"id": int, "username": str|None, "first_name": str|None, "last_name": str|None}
    Nota: Telegram no proporciona email directamente, por lo que se omite para bots puros.
    commit: si True hace commit y refresh; por defecto False para permitir transacciones en services.
    """
    telegram_id = int(tg_payload["id"])
    username = tg_payload.get("username")
    first_name = tg_payload.get("first_name")
    last_name = tg_payload.get("last_name")
    # email = tg_payload.get("email")  # Removido: Telegram no lo proporciona

    try:
        user = models.User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            # email=email,  # Removido
        )
        session.add(user)
        if commit:
            try:
                await session.commit()
                await session.refresh(user)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al commitear user create", extra={"user_id": None})
                raise
        logger.info("Usuario creado desde Telegram", extra={"user_id": telegram_id})
        return user
    except SQLAlchemyError:
        logger.exception("Fallo al crear usuario desde Telegram", extra={"user_id": None})
        raise


async def ensure_user(
    session: AsyncSession,
    tg_payload: Dict[str, Any],
    commit: bool = False,
) -> models.User:
    """
    Asegura que exista un User para el tg_payload. Devuelve el objeto existente o creado.
    Actualiza username/first_name/last_name si cambian.
    Por defecto NO commitea para permitir composición transaccional en services.
    """
    telegram_id = int(tg_payload["id"])
    try:
        existing = await get_user_by_telegram_id(session, telegram_id)
        if existing:
            changed = False
            new_username = tg_payload.get("username")
            if new_username is not None and existing.username != new_username:
                existing.username = new_username
                changed = True

            new_first = tg_payload.get("first_name")
            if new_first is not None and existing.first_name != new_first:
                existing.first_name = new_first
                changed = True

            new_last = tg_payload.get("last_name")
            if new_last is not None and existing.last_name != new_last:
                existing.last_name = new_last
                changed = True

            # new_email = tg_payload.get("email")  # Removido: Telegram no proporciona email
            # if new_email is not None and existing.email != new_email:
            #     existing.email = new_email
            #     changed = True

            if changed and commit:
                try:
                    await session.commit()
                    await session.refresh(existing)
                except SQLAlchemyError:
                    await session.rollback()
                    logger.exception("Fallo al actualizar usuario existente", extra={"user_id": existing.telegram_id})
                    raise
            logger.info("Usuario existente retornado por ensure_user", extra={"user_id": existing.telegram_id})
            return existing

        # no existe -> crear
        user = await create_user_from_telegram(session, tg_payload, commit=commit)
        return user
    except Exception:
        logger.exception("Fallo en ensure_user", extra={"user_id": None})
        raise


async def update_last_login(session: AsyncSession, user_id: str, commit: bool = False) -> Optional[models.User]:
    """Actualiza last_login_at del usuario. Retorna el usuario actualizado o None."""
    try:
        user = await get_user_by_pk(session, user_id)
        if not user:
            return None
        user.last_login_at = datetime.now(tz=timezone.utc)
        if commit:
            try:
                await session.commit()
                await session.refresh(user)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al commitear update_last_login", extra={"user_id": user.telegram_id if user else None})
                raise
        logger.info("Updated last_login_at", extra={"user_id": user.telegram_id})
        return user
    except SQLAlchemyError:
        logger.exception("Error en update_last_login", extra={"user_id": None})
        raise


async def set_user_admin(session: AsyncSession, user_id: str, is_admin: bool, commit: bool = True) -> Optional[models.User]:
    """Asigna o revoca permisos de administrador. Por defecto commitea la operación."""
    try:
        user = await get_user_by_pk(session, user_id)
        if not user:
            return None
        user.is_admin = bool(is_admin)
        if commit:
            try:
                await session.commit()
                await session.refresh(user)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al setear is_admin", extra={"user_id": user.telegram_id})
                raise
        logger.info("Cambio is_admin", extra={"user_id": user.telegram_id})
        return user
    except SQLAlchemyError:
        logger.exception("Error en set_user_admin", extra={"user_id": None})
        raise


async def set_user_superadmin(session: AsyncSession, user_id: str, is_superadmin: bool, commit: bool = True) -> Optional[models.User]:
    """Asigna o revoca permisos de superadministrador y marca is_admin=True si se setea superadmin."""
    try:
        user = await get_user_by_pk(session, user_id)
        if not user:
            return None
        user.is_superadmin = bool(is_superadmin)
        if is_superadmin:
            user.is_admin = True
        if commit:
            try:
                await session.commit()
                await session.refresh(user)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al setear is_superadmin", extra={"user_id": user.telegram_id})
                raise
        logger.info("Cambio is_superadmin", extra={"user_id": user.telegram_id})
        return user
    except SQLAlchemyError:
        logger.exception("Error en set_user_superadmin", extra={"user_id": None})
        raise


async def is_user_admin(session: AsyncSession, user_id: str) -> bool:
    try:
        result = await session.execute(select(models.User.is_admin).where(models.User.id == user_id))
        value = result.scalars().one_or_none()
        return bool(value)
    except SQLAlchemyError:
        logger.exception("Error comprobando is_user_admin", extra={"user_id": None})
        raise


async def is_user_superadmin(session: AsyncSession, user_id: str) -> bool:
    try:
        result = await session.execute(select(models.User.is_superadmin).where(models.User.id == user_id))
        value = result.scalars().one_or_none()
        return bool(value)
    except SQLAlchemyError:
        logger.exception("Error comprobando is_user_superadmin", extra={"user_id": None})
        raise


async def get_admins(session: AsyncSession) -> List[models.User]:
    """Devuelve usuarios con is_admin o is_superadmin true."""
    try:
        stmt = select(models.User).where((models.User.is_admin.is_(True)) | (models.User.is_superadmin.is_(True)))
        result = await session.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo admins", extra={"user_id": None})
        raise


async def list_users(session: AsyncSession, limit: int = 50) -> List[models.User]:
    """Lista usuarios ordenados por created_at desc."""
    try:
        stmt = select(models.User).order_by(models.User.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error listando usuarios", extra={"user_id": None})
        raise


async def get_active_users(
    session: AsyncSession,
    batch_size: int = 100,
    offset: int = 0,
) -> AsyncGenerator[models.User, None]:
    """
    Generador async que devuelve usuarios activos (is_active=True) en lotes.
    Ideal para envíos masivos escalables.
    """
    try:
        stmt = (
            select(models.User)
            .where(models.User.is_active.is_(True))
            .order_by(models.User.created_at.desc())
            .offset(offset)
            .limit(batch_size)
        )
        result = await session.execute(stmt)
        for user in result.scalars():
            yield user
    except SQLAlchemyError:
        logger.exception("Error obteniendo usuarios activos", extra={"user_id": None})
        raise


# --- Nuevas funciones para integración con IPManager ---
async def get_assigned_ips_for_user(session: AsyncSession, user_id: str) -> List[models.IPManager]:
    """
    Obtiene todas las IPs asignadas actualmente a un usuario (no revocadas).
    """
    try:
        stmt = select(models.IPManager).where(
            models.IPManager.assigned_to_user_id == user_id,
            models.IPManager.is_revoked.is_(False) # Opcional: solo IPs no revocadas
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo IPs asignadas al usuario", extra={"user_id": user_id})
        raise


async def count_assigned_ips_for_user(session: AsyncSession, user_id: str) -> int:
    """
    Cuenta el número de IPs asignadas actualmente a un usuario (no revocadas).
    Útil para verificar límites.
    """
    try:
        stmt = select(func.count()).select_from(models.IPManager).where(
            models.IPManager.assigned_to_user_id == user_id,
            models.IPManager.is_revoked.is_(False)
        )
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)
    except SQLAlchemyError:
        logger.exception("Error contando IPs asignadas al usuario", extra={"user_id": user_id})
        raise