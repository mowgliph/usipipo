# database/crud/proxy.py

from __future__ import annotations
from typing import Optional, List, Dict, Any

from datetime import datetime, timedelta, timezone
import logging

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database import models

logger = logging.getLogger("usipipo.crud.proxy")


async def get_proxy_by_id(session: AsyncSession, proxy_id: str) -> Optional[models.MTProtoProxy]:
    """Obtiene un proxy MTProto por su ID (UUID string)."""
    try:
        res = await session.execute(select(models.MTProtoProxy).where(models.MTProtoProxy.id == proxy_id))
        return res.scalars().one_or_none()
    except SQLAlchemyError:
        logger.exception("Error obteniendo MTProtoProxy por id", extra={"user_id": None, "proxy_id": proxy_id})
        raise


async def get_proxies_for_user(session: AsyncSession, user_id: str) -> List[models.MTProtoProxy]:
    """Obtiene todos los proxies MTProto asociados a un usuario (user_id es UUID string)."""
    try:
        res = await session.execute(select(models.MTProtoProxy).where(models.MTProtoProxy.user_id == user_id))
        return res.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo MTProtoProxies por usuario", extra={"user_id": None, "target_user_id": user_id})
        raise


async def get_active_proxy_for_user(session: AsyncSession, user_id: str) -> Optional[models.MTProtoProxy]:
    """
    Devuelve el proxy activo del usuario si existe.
    Condiciones: status='active', expires_at is null or > now (UTC).
    """
    try:
        now = datetime.now(timezone.utc)
        stmt = select(models.MTProtoProxy).where(
            models.MTProtoProxy.user_id == user_id,
            models.MTProtoProxy.status == "active",
            (models.MTProtoProxy.expires_at.is_(None) | (models.MTProtoProxy.expires_at > now)),
        ).order_by(models.MTProtoProxy.created_at.desc()).limit(1)
        res = await session.execute(stmt)
        return res.scalars().one_or_none()
    except SQLAlchemyError:
        logger.exception("Error comprobando proxy activo", extra={"user_id": None, "target_user_id": user_id})
        raise


async def create_proxy(
    session: AsyncSession,
    user_id: str,
    host: str,
    port: int,
    secret: str,
    *,
    tag: Optional[str] = None,
    expires_at: Optional[datetime] = None,
    extra_data: Optional[Dict[str, Any]] = None,
    commit: bool = False,
) -> models.MTProtoProxy:
    """
    Crea un registro MTProtoProxy en estado active. No realiza validaciones de negocio.
    - user_id: UUID string
    - host: IP o hostname
    - port: puerto del proxy
    - secret: secreto del proxy
    - tag: opcional, para registro con @MTProxybot
    - commit: por defecto False para permitir transacciones en services.
    """
    try:
        proxy = models.MTProtoProxy(
            user_id=user_id,
            host=host,
            port=port,
            secret=secret,
            tag=tag,
            expires_at=expires_at,
            extra_data=extra_data or {},
            status="active",
            created_at=datetime.now(timezone.utc),
        )
        session.add(proxy)
        if commit:
            try:
                await session.commit()
                await session.refresh(proxy)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error commiteando create_proxy", extra={"user_id": user_id})
                raise
        logger.info("MTProtoProxy creado", extra={"user_id": user_id, "proxy_id": getattr(proxy, "id", None)})
        return proxy
    except SQLAlchemyError:
        logger.exception("Error creando MTProtoProxy", extra={"user_id": user_id})
        raise


async def create_free_proxy(
    session: AsyncSession,
    user_id: str,
    host: str,
    port: int,
    secret: str,
    *,
    tag: Optional[str] = None,
    duration_days: int = 30,
    extra_data: Optional[Dict[str, Any]] = None,
    commit: bool = False,
) -> models.MTProtoProxy:
    """
    Crea un proxy gratuito con duración `duration_days`.
    Previene la creación de más de un proxy activo por usuario.
    """
    try:
        existing = await get_active_proxy_for_user(session, user_id)
        if existing:
            logger.info("Intento de crear proxy cuando ya existe uno activo", extra={"user_id": user_id, "proxy_id": existing.id})
            raise ValueError("user_has_active_proxy")

        expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)
        proxy = await create_proxy(
            session,
            user_id=user_id,
            host=host,
            port=port,
            secret=secret,
            tag=tag,
            expires_at=expires_at,
            extra_data=extra_data,
            commit=commit,
        )
        return proxy
    except ValueError:
        raise
    except SQLAlchemyError:
        logger.exception("Error creando proxy gratuito", extra={"user_id": user_id})
        raise


async def has_active_proxy(session: AsyncSession, user_id: str) -> bool:
    """Verifica si el usuario tiene un proxy activo (sin devolver el objeto)."""
    try:
        now = datetime.now(timezone.utc)
        stmt = select(func.count()).select_from(models.MTProtoProxy).where(
            models.MTProtoProxy.user_id == user_id,
            models.MTProtoProxy.status == "active",
            (models.MTProtoProxy.expires_at.is_(None) | (models.MTProtoProxy.expires_at > now)),
        )
        res = await session.execute(stmt)
        count = res.scalar_one()
        return int(count) > 0
    except SQLAlchemyError:
        logger.exception("Error comprobando existencia de proxy activo", extra={"user_id": user_id})
        raise


async def update_proxy_status(session: AsyncSession, proxy_id: str, status: str, *, commit: bool = False) -> Optional[models.MTProtoProxy]:
    """Actualiza el estado de un proxy MTProto (active/revoked/expired)."""
    try:
        proxy = await get_proxy_by_id(session, proxy_id)
        if not proxy:
            return None
        proxy.status = status
        if commit:
            try:
                await session.commit()
                await session.refresh(proxy)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error guardando status de MTProtoProxy", extra={"user_id": proxy.user_id, "proxy_id": proxy_id})
                raise
        logger.info("Status proxy actualizado", extra={"user_id": proxy.user_id, "proxy_id": proxy_id, "status": status})
        return proxy
    except SQLAlchemyError:
        logger.exception("Error en update_proxy_status", extra={"user_id": None, "proxy_id": proxy_id})
        raise


async def revoke_proxy(session: AsyncSession, proxy_id: str, reason: str, *, commit: bool = False) -> Optional[models.MTProtoProxy]:
    """
    Marca un proxy como 'revoked' y añade un campo 'extra_data.revoked_reason' si procede.
    Devuelve el proxy actualizado si existía y fue modificado, None si no se encontró.
    """
    try:
        proxy = await get_proxy_by_id(session, proxy_id)
        if not proxy:
            return None

        proxy.status = "revoked"
        extra = dict(proxy.extra_data or {})
        extra["revoked_reason"] = reason
        extra["revoked_at"] = datetime.now(timezone.utc).isoformat()
        proxy.extra_data = extra
        if commit:
            try:
                await session.commit()
                await session.refresh(proxy)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error revocando MTProtoProxy", extra={"user_id": proxy.user_id, "proxy_id": proxy_id})
                raise
        logger.info("Proxy revocado", extra={"user_id": proxy.user_id, "proxy_id": proxy_id, "reason": reason})
        return proxy
    except SQLAlchemyError:
        logger.exception("Error en revoke_proxy", extra={"user_id": None, "proxy_id": proxy_id})
        raise


async def delete_proxy(session: AsyncSession, proxy_id: str, *, commit: bool = False) -> bool:
    """Elimina un proxy MTProto por ID."""
    try:
        proxy = await get_proxy_by_id(session, proxy_id)
        if not proxy:
            return False
        await session.delete(proxy)
        if commit:
            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error borrando MTProtoProxy", extra={"user_id": proxy.user_id, "proxy_id": proxy_id})
                raise
        logger.info("MTProtoProxy eliminada", extra={"user_id": proxy.user_id, "proxy_id": proxy_id})
        return True
    except SQLAlchemyError:
        logger.exception("Error en delete_proxy", extra={"user_id": None, "proxy_id": proxy_id})
        raise


async def get_expired_proxies(session: AsyncSession) -> List[models.MTProtoProxy]:
    """
    Devuelve todos los proxies MTProto vencidos y aún activos.
    Útil para jobs de mantenimiento.
    """
    try:
        now = datetime.now(timezone.utc)
        stmt = select(models.MTProtoProxy).where(
            models.MTProtoProxy.status == "active",
            models.MTProtoProxy.expires_at < now,
        )
        res = await session.execute(stmt)
        return res.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error listando proxies vencidos", extra={"user_id": None})
        raise


# =========================
# Métricas / helpers simples
# =========================

async def count_proxies_by_status(session: AsyncSession, status: str) -> int:
    try:
        stmt = select(func.count()).select_from(models.MTProtoProxy).where(models.MTProtoProxy.status == status)
        res = await session.execute(stmt)
        return int(res.scalar_one() or 0)
    except SQLAlchemyError:
        logger.exception("Error contando proxies por status", extra={"user_id": None})
        raise


async def count_proxies_for_user(session: AsyncSession, user_id: str) -> int:
    """Cuenta el número de proxies MTProto para un usuario dado."""
    try:
        stmt = select(func.count()).select_from(models.MTProtoProxy).where(models.MTProtoProxy.user_id == user_id)
        res = await session.execute(stmt)
        return int(res.scalar_one() or 0)
    except SQLAlchemyError:
        logger.exception("Error contando proxies por usuario", extra={"user_id": None, "target_user_id": user_id})
        raise


async def last_proxy_for_user(session: AsyncSession, user_id: str) -> Optional[models.MTProtoProxy]:
    """Obtiene el último proxy MTProto creado para un usuario dado."""
    try:
        stmt = select(models.MTProtoProxy).where(models.MTProtoProxy.user_id == user_id).order_by(models.MTProtoProxy.created_at.desc()).limit(1)
        res = await session.execute(stmt)
        return res.scalars().one_or_none()
    except SQLAlchemyError:
        logger.exception("Error obteniendo último proxy por usuario", extra={"user_id": None, "target_user_id": user_id})
        raise