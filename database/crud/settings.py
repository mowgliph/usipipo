# database/crud/settings.py
from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timezone

import logging

from sqlalchemy import select, delete, update, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database import models

logger = logging.getLogger("usipipo.crud.settings")


async def list_user_settings(session: AsyncSession, user_id: str, limit: int = 100) -> List[models.UserSetting]:
    """
    Devuelve todas las configuraciones de un usuario ordenadas por updated_at desc.
    - user_id: UUID string
    """
    try:
        stmt = select(models.UserSetting).where(models.UserSetting.user_id == user_id).order_by(models.UserSetting.updated_at.desc()).limit(limit)
        res = await session.execute(stmt)
        settings = res.scalars().all()
        logger.debug("Listado de settings obtenido", extra={"user_id": user_id, "count": len(settings)})
        return settings
    except SQLAlchemyError:
        logger.exception("Error listando settings del usuario", extra={"user_id": user_id})
        raise


async def get_user_setting(session: AsyncSession, user_id: str, key: str) -> Optional[models.UserSetting]:
    """
    Obtiene un setting específico de un usuario.
    - No hace commit; quien llame controla la transacción.
    """
    try:
        stmt = select(models.UserSetting).where(models.UserSetting.user_id == user_id, models.UserSetting.setting_key == key)
        res = await session.execute(stmt)
        setting = res.scalars().one_or_none()
        logger.debug("Obtenido user setting", extra={"user_id": user_id, "key": key})
        return setting
    except SQLAlchemyError:
        logger.exception("Error obteniendo user setting", extra={"user_id": user_id, "key": key})
        raise


async def get_user_setting_value(session: AsyncSession, user_id: str, key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Obtiene el valor de un setting específico de un usuario.
    - Retorna el valor o default si no existe.
    """
    try:
        setting = await get_user_setting(session, user_id, key)
        return setting.setting_value if setting else default
    except SQLAlchemyError:
        logger.exception("Error obteniendo valor de user setting", extra={"user_id": user_id, "key": key})
        raise


async def set_user_setting(session: AsyncSession, user_id: str, key: str, value: str, *, commit: bool = False) -> models.UserSetting:
    """
    Crea o actualiza una configuración de usuario.
    - commit: si True hace commit() y refresh() antes de devolver el objeto.
    - Retorna la instancia UserSetting (pendiente de commit si commit=False).
    """
    try:
        existing = await get_user_setting(session, user_id, key)
        now = datetime.now(timezone.utc)

        if existing:
            existing.setting_value = value
            existing.updated_at = now
            setting = existing
            logger.info("Actualizando setting de usuario", extra={"user_id": user_id, "key": key})
        else:
            setting = models.UserSetting(
                user_id=user_id,
                setting_key=key,
                setting_value=value,
                updated_at=now,
            )
            session.add(setting)
            # flush so caller can see PK if needed without full commit
            await session.flush()
            logger.info("Creando nuevo setting de usuario", extra={"user_id": user_id, "key": key})

        if commit:
            try:
                await session.commit()
                await session.refresh(setting)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al commitear set_user_setting", extra={"user_id": user_id, "key": key})
                raise

        return setting
    except SQLAlchemyError:
        logger.exception("Error en set_user_setting", extra={"user_id": user_id, "key": key})
        raise


async def delete_user_setting(session: AsyncSession, user_id: str, key: str, *, commit: bool = False) -> bool:
    """
    Elimina una configuración específica del usuario.
    - Retorna True si se eliminó, False si no existía.
    - commit: si True hace commit() tras la eliminación.
    """
    try:
        setting = await get_user_setting(session, user_id, key)
        if not setting:
            logger.debug("Intento de borrar setting inexistente", extra={"user_id": user_id, "key": key})
            return False

        await session.delete(setting)

        if commit:
            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al commitear delete_user_setting", extra={"user_id": user_id, "key": key})
                raise

        logger.info("Setting eliminado", extra={"user_id": user_id, "key": key})
        return True
    except SQLAlchemyError:
        logger.exception("Error eliminando user setting", extra={"user_id": user_id, "key": key})
        raise


async def delete_all_user_settings(session: AsyncSession, user_id: str, *, commit: bool = False) -> int:
    """
    Elimina todas las configuraciones del usuario.
    - Retorna la cantidad de registros eliminados.
    - commit: si True hace commit() al finalizar.
    """
    try:
        stmt = delete(models.UserSetting).where(models.UserSetting.user_id == user_id)
        res = await session.execute(stmt)
        deleted = int(res.rowcount or 0)

        if commit:
            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al commitear delete_all_user_settings", extra={"user_id": user_id})
                raise

        logger.info("Eliminadas settings del usuario", extra={"user_id": user_id, "deleted": deleted})
        return deleted
    except SQLAlchemyError:
        logger.exception("Error eliminando todos los settings del usuario", extra={"user_id": user_id})
        raise


async def count_user_settings(session: AsyncSession, user_id: str) -> int:
    """
    Cuenta el número de configuraciones que tiene un usuario.
    """
    try:
        stmt = select(func.count()).select_from(models.UserSetting).where(models.UserSetting.user_id == user_id)
        res = await session.execute(stmt)
        count = int(res.scalar_one() or 0)
        return count
    except SQLAlchemyError:
        logger.exception("Error contando settings del usuario", extra={"user_id": user_id})
        raise