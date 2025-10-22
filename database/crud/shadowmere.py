# database/crud/shadowmere.py

from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
import logging

from sqlalchemy import select, func, and_, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database import models

logger = logging.getLogger("usipipo.crud.shadowmere")


async def create_proxy(
    session: AsyncSession,
    proxy_address: str,
    proxy_type: str,
    *,
    country: Optional[str] = None,
    response_time: Optional[float] = None,
    commit: bool = False,
) -> models.ShadowmereProxy:
    """
    Crea un nuevo registro de proxy Shadowmere.
    
    Args:
        session: Sesión async de SQLAlchemy
        proxy_address: Dirección del proxy (IP:puerto)
        proxy_type: Tipo de proxy (SOCKS5, SOCKS4, HTTP, HTTPS)
        country: País del proxy (opcional)
        response_time: Tiempo de respuesta en ms (opcional)
        commit: Si True, realiza commit automático
    
    Returns:
        Instancia de ShadowmereProxy creada
    
    Raises:
        ValueError: Si proxy_address está vacío
        SQLAlchemyError: Si hay error en la base de datos
    """
    if not proxy_address or not proxy_address.strip():
        raise ValueError("proxy_address no puede estar vacío")
    
    try:
        proxy = models.ShadowmereProxy(
            proxy_address=proxy_address.strip(),
            proxy_type=proxy_type,
            country=country,
            response_time=response_time,
            is_working=True,
            detection_source="shadowmere",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(proxy)
        if commit:
            try:
                await session.commit()
                await session.refresh(proxy)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error commiteando create_proxy", extra={"proxy_address": proxy_address})
                raise
        logger.info("Proxy Shadowmere creado", extra={"proxy_address": proxy_address, "proxy_type": proxy_type})
        return proxy
    except SQLAlchemyError:
        logger.exception("Error creando proxy Shadowmere", extra={"proxy_address": proxy_address})
        raise


async def get_proxy_by_address(
    session: AsyncSession,
    proxy_address: str,
) -> Optional[models.ShadowmereProxy]:
    """
    Obtiene un proxy por su dirección (IP:puerto).
    
    Args:
        session: Sesión async de SQLAlchemy
        proxy_address: Dirección del proxy (IP:puerto)
    
    Returns:
        Instancia de ShadowmereProxy o None si no existe
    
    Raises:
        SQLAlchemyError: Si hay error en la base de datos
    """
    if not proxy_address or not proxy_address.strip():
        raise ValueError("proxy_address no puede estar vacío")
    
    try:
        stmt = select(models.ShadowmereProxy).where(
            models.ShadowmereProxy.proxy_address == proxy_address.strip()
        )
        res = await session.execute(stmt)
        return res.scalars().one_or_none()
    except SQLAlchemyError:
        logger.exception("Error obteniendo proxy por dirección", extra={"proxy_address": proxy_address})
        raise


async def get_all_working_proxies(
    session: AsyncSession,
    limit: int = 10,
) -> List[models.ShadowmereProxy]:
    """
    Obtiene los últimos proxys que están funcionando.
    
    Args:
        session: Sesión async de SQLAlchemy
        limit: Número máximo de proxys a retornar (default: 10)
    
    Returns:
        Lista de instancias de ShadowmereProxy funcionando
    
    Raises:
        SQLAlchemyError: Si hay error en la base de datos
    """
    try:
        stmt = select(models.ShadowmereProxy).where(
            models.ShadowmereProxy.is_working == True
        ).order_by(
            desc(models.ShadowmereProxy.last_checked)
        ).limit(limit)
        res = await session.execute(stmt)
        return res.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo proxys funcionando", extra={"limit": limit})
        raise


async def get_proxies_by_type(
    session: AsyncSession,
    proxy_type: str,
    limit: int = 10,
) -> List[models.ShadowmereProxy]:
    """
    Obtiene proxys filtrados por tipo.
    
    Args:
        session: Sesión async de SQLAlchemy
        proxy_type: Tipo de proxy (SOCKS5, SOCKS4, HTTP, HTTPS)
        limit: Número máximo de proxys a retornar (default: 10)
    
    Returns:
        Lista de instancias de ShadowmereProxy del tipo especificado
    
    Raises:
        SQLAlchemyError: Si hay error en la base de datos
    """
    if not proxy_type or not proxy_type.strip():
        raise ValueError("proxy_type no puede estar vacío")
    
    try:
        stmt = select(models.ShadowmereProxy).where(
            models.ShadowmereProxy.proxy_type == proxy_type.strip()
        ).order_by(
            desc(models.ShadowmereProxy.last_checked)
        ).limit(limit)
        res = await session.execute(stmt)
        return res.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo proxys por tipo", extra={"proxy_type": proxy_type, "limit": limit})
        raise


async def update_proxy_status(
    session: AsyncSession,
    proxy_address: str,
    is_working: bool,
    response_time: Optional[float] = None,
    commit: bool = False,
) -> Optional[models.ShadowmereProxy]:
    """
    Actualiza el estado de un proxy (funcionando/no funcionando).
    
    Args:
        session: Sesión async de SQLAlchemy
        proxy_address: Dirección del proxy (IP:puerto)
        is_working: Si el proxy está funcionando
        response_time: Tiempo de respuesta en ms (opcional)
        commit: Si True, realiza commit automático
    
    Returns:
        Instancia de ShadowmereProxy actualizada o None si no existe
    
    Raises:
        ValueError: Si proxy_address está vacío
        SQLAlchemyError: Si hay error en la base de datos
    """
    if not proxy_address or not proxy_address.strip():
        raise ValueError("proxy_address no puede estar vacío")
    
    try:
        proxy = await get_proxy_by_address(session, proxy_address)
        if not proxy:
            logger.warning("Proxy no encontrado para actualizar", extra={"proxy_address": proxy_address})
            return None
        
        proxy.is_working = is_working
        proxy.last_checked = datetime.now(timezone.utc)
        if response_time is not None:
            proxy.response_time = response_time
        proxy.updated_at = datetime.now(timezone.utc)
        
        session.add(proxy)
        if commit:
            try:
                await session.commit()
                await session.refresh(proxy)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error commiteando update_proxy_status", extra={"proxy_address": proxy_address})
                raise
        
        logger.info("Estado de proxy actualizado", extra={"proxy_address": proxy_address, "is_working": is_working})
        return proxy
    except SQLAlchemyError:
        logger.exception("Error actualizando estado del proxy", extra={"proxy_address": proxy_address})
        raise


async def delete_proxy(
    session: AsyncSession,
    proxy_address: str,
    commit: bool = False,
) -> bool:
    """
    Elimina un proxy de la base de datos.
    
    Args:
        session: Sesión async de SQLAlchemy
        proxy_address: Dirección del proxy (IP:puerto)
        commit: Si True, realiza commit automático
    
    Returns:
        True si se eliminó, False si no existía
    
    Raises:
        ValueError: Si proxy_address está vacío
        SQLAlchemyError: Si hay error en la base de datos
    """
    if not proxy_address or not proxy_address.strip():
        raise ValueError("proxy_address no puede estar vacío")
    
    try:
        proxy = await get_proxy_by_address(session, proxy_address)
        if not proxy:
            logger.warning("Proxy no encontrado para eliminar", extra={"proxy_address": proxy_address})
            return False
        
        await session.delete(proxy)
        if commit:
            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error commiteando delete_proxy", extra={"proxy_address": proxy_address})
                raise
        
        logger.info("Proxy eliminado", extra={"proxy_address": proxy_address})
        return True
    except SQLAlchemyError:
        logger.exception("Error eliminando proxy", extra={"proxy_address": proxy_address})
        raise


async def delete_old_proxies(
    session: AsyncSession,
    days: int = 30,
    commit: bool = False,
) -> int:
    """
    Elimina proxys más antiguos que el número de días especificado.
    
    Args:
        session: Sesión async de SQLAlchemy
        days: Número de días (default: 30)
        commit: Si True, realiza commit automático
    
    Returns:
        Número de proxys eliminados
    
    Raises:
        SQLAlchemyError: Si hay error en la base de datos
    """
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Primero obtener los proxys a eliminar para logging
        stmt_select = select(models.ShadowmereProxy).where(
            models.ShadowmereProxy.created_at < cutoff_date
        )
        res = await session.execute(stmt_select)
        proxies_to_delete = res.scalars().all()
        count = len(proxies_to_delete)
        
        # Eliminar los proxys
        for proxy in proxies_to_delete:
            await session.delete(proxy)
        
        if commit:
            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error commiteando delete_old_proxies", extra={"days": days, "count": count})
                raise
        
        logger.info("Proxys antiguos eliminados", extra={"days": days, "count": count})
        return count
    except SQLAlchemyError:
        logger.exception("Error eliminando proxys antiguos", extra={"days": days})
        raise


async def get_proxy_stats(
    session: AsyncSession,
) -> Dict[str, Any]:
    """
    Obtiene estadísticas de proxys (total, funcionando, por tipo).
    
    Args:
        session: Sesión async de SQLAlchemy
    
    Returns:
        Diccionario con estadísticas:
        {
            "total": int,
            "working": int,
            "not_working": int,
            "by_type": {
                "SOCKS5": int,
                "SOCKS4": int,
                "HTTP": int,
                "HTTPS": int,
            },
            "by_country": {
                "country_name": int,
                ...
            }
        }
    
    Raises:
        SQLAlchemyError: Si hay error en la base de datos
    """
    try:
        # Total de proxys
        stmt_total = select(func.count(models.ShadowmereProxy.id))
        res_total = await session.execute(stmt_total)
        total = res_total.scalar() or 0
        
        # Proxys funcionando
        stmt_working = select(func.count(models.ShadowmereProxy.id)).where(
            models.ShadowmereProxy.is_working == True
        )
        res_working = await session.execute(stmt_working)
        working = res_working.scalar() or 0
        
        # Proxys no funcionando
        stmt_not_working = select(func.count(models.ShadowmereProxy.id)).where(
            models.ShadowmereProxy.is_working == False
        )
        res_not_working = await session.execute(stmt_not_working)
        not_working = res_not_working.scalar() or 0
        
        # Por tipo
        stmt_by_type = select(
            models.ShadowmereProxy.proxy_type,
            func.count(models.ShadowmereProxy.id).label("count")
        ).group_by(models.ShadowmereProxy.proxy_type)
        res_by_type = await session.execute(stmt_by_type)
        by_type = {row[0]: row[1] for row in res_by_type.all()}
        
        # Por país
        stmt_by_country = select(
            models.ShadowmereProxy.country,
            func.count(models.ShadowmereProxy.id).label("count")
        ).where(
            models.ShadowmereProxy.country.isnot(None)
        ).group_by(models.ShadowmereProxy.country)
        res_by_country = await session.execute(stmt_by_country)
        by_country = {row[0]: row[1] for row in res_by_country.all() if row[0]}
        
        stats = {
            "total": total,
            "working": working,
            "not_working": not_working,
            "by_type": by_type,
            "by_country": by_country,
        }
        
        logger.info("Estadísticas de proxys obtenidas", extra={"stats": stats})
        return stats
    except SQLAlchemyError:
        logger.exception("Error obteniendo estadísticas de proxys")
        raise


async def mark_all_as_not_working(
    session: AsyncSession,
    commit: bool = False,
) -> int:
    """
    Marca todos los proxys como no funcionando.
    
    Args:
        session: Sesión async de SQLAlchemy
        commit: Si True, realiza commit automático
    
    Returns:
        Número de proxys actualizados
    
    Raises:
        SQLAlchemyError: Si hay error en la base de datos
    """
    try:
        # Obtener todos los proxys funcionando
        stmt = select(models.ShadowmereProxy).where(
            models.ShadowmereProxy.is_working == True
        )
        res = await session.execute(stmt)
        proxies = res.scalars().all()
        count = len(proxies)
        
        # Actualizar todos
        now = datetime.now(timezone.utc)
        for proxy in proxies:
            proxy.is_working = False
            proxy.last_checked = now
            proxy.updated_at = now
            session.add(proxy)
        
        if commit:
            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error commiteando mark_all_as_not_working", extra={"count": count})
                raise
        
        logger.info("Todos los proxys marcados como no funcionando", extra={"count": count})
        return count
    except SQLAlchemyError:
        logger.exception("Error marcando proxys como no funcionando")
        raise


__all__ = [
    "create_proxy",
    "get_proxy_by_address",
    "get_all_working_proxies",
    "get_proxies_by_type",
    "update_proxy_status",
    "delete_proxy",
    "delete_old_proxies",
    "get_proxy_stats",
    "mark_all_as_not_working",
]
