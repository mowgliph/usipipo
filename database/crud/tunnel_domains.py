# database/crud/tunnel_domains.py

from __future__ import annotations
from typing import Optional, List, Dict, Any

from datetime import datetime, timezone
import logging

from sqlalchemy import select, update, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database import models

logger = logging.getLogger("usipipo.crud.tunnel_domains")


async def get_tunnel_domain_by_id(session: AsyncSession, domain_id: str) -> Optional[models.TunnelDomain]:
    """Obtiene un dominio de túnel por su ID (UUID string)."""
    try:
        result = await session.execute(select(models.TunnelDomain).where(models.TunnelDomain.id == domain_id))
        return result.scalars().one_or_none()
    except SQLAlchemyError:
        logger.exception("Error obteniendo TunnelDomain por id", extra={"user_id": None, "domain_id": domain_id})
        raise


async def get_tunnel_domain_by_name(session: AsyncSession, domain_name: str) -> Optional[models.TunnelDomain]:
    """Obtiene un dominio de túnel por su nombre de dominio."""
    try:
        result = await session.execute(select(models.TunnelDomain).where(models.TunnelDomain.domain_name == domain_name))
        return result.scalars().one_or_none()
    except SQLAlchemyError:
        logger.exception("Error obteniendo TunnelDomain por nombre", extra={"user_id": None, "domain_name": domain_name})
        raise


async def get_tunnel_domains_for_user(session: AsyncSession, user_id: str) -> List[models.TunnelDomain]:
    """Obtiene todos los dominios de túnel asociados a un usuario (user_id es UUID string)."""
    try:
        result = await session.execute(select(models.TunnelDomain).where(models.TunnelDomain.user_id == user_id))
        return result.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo TunnelDomains por usuario", extra={"user_id": None, "target_user_id": user_id})
        raise


async def get_active_tunnel_domains_for_user(session: AsyncSession, user_id: str) -> List[models.TunnelDomain]:
    """
    Obtiene los dominios de túnel activos para un usuario.
    Condiciones: status='active', expires_at is null or > now (UTC).
    """
    try:
        now = datetime.now(timezone.utc)
        stmt = select(models.TunnelDomain).where(
            models.TunnelDomain.user_id == user_id,
            models.TunnelDomain.status == "active",
            (models.TunnelDomain.expires_at.is_(None) | (models.TunnelDomain.expires_at > now)),
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo dominios activos por usuario", extra={"user_id": None, "target_user_id": user_id})
        raise


async def create_tunnel_domain(
    session: AsyncSession,
    user_id: str,
    domain_name: str,
    *,
    vpn_config_id: Optional[str] = None,
    expires_at: Optional[datetime] = None,
    extra_data: Optional[Dict[str, Any]] = None,
    commit: bool = False,
) -> models.TunnelDomain:
    """
    Crea un registro TunnelDomain en estado active. No realiza validaciones de negocio.
    - user_id: UUID string
    - domain_name: nombre del dominio (FQDN)
    - vpn_config_id: opcional, ID de la VPN config asociada
    - commit: por defecto False para permitir transacciones en services.
    """
    try:
        # Verificar unicidad del dominio
        existing = await get_tunnel_domain_by_name(session, domain_name)
        if existing:
            raise ValueError("domain_already_exists")

        domain = models.TunnelDomain(
            user_id=user_id,
            domain_name=domain_name,
            vpn_config_id=vpn_config_id,
            expires_at=expires_at,
            extra_data=extra_data or {},
            status="active",
            assigned_at=datetime.now(timezone.utc),
        )
        session.add(domain)
        if commit:
            try:
                await session.commit()
                await session.refresh(domain)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error commiteando create_tunnel_domain", extra={"user_id": user_id})
                raise
        logger.info("TunnelDomain creado", extra={"user_id": user_id, "domain_id": getattr(domain, "id", None), "domain_name": domain_name})
        return domain
    except ValueError:
        raise
    except SQLAlchemyError:
        logger.exception("Error creando TunnelDomain", extra={"user_id": user_id})
        raise


async def update_tunnel_domain(
    session: AsyncSession,
    domain_id: str,
    *,
    domain_name: Optional[str] = None,
    vpn_config_id: Optional[str] = None,
    status: Optional[str] = None,
    expires_at: Optional[datetime] = None,
    extra_data: Optional[Dict[str, Any]] = None,
    commit: bool = False,
) -> Optional[models.TunnelDomain]:
    """
    Actualiza un dominio de túnel. Solo actualiza campos proporcionados.
    """
    try:
        domain = await get_tunnel_domain_by_id(session, domain_id)
        if not domain:
            return None

        if domain_name is not None:
            # Verificar unicidad si cambia el nombre
            if domain_name != domain.domain_name:
                existing = await get_tunnel_domain_by_name(session, domain_name)
                if existing:
                    raise ValueError("domain_already_exists")
            domain.domain_name = domain_name

        if vpn_config_id is not None:
            domain.vpn_config_id = vpn_config_id

        if status is not None:
            domain.status = status

        if expires_at is not None:
            domain.expires_at = expires_at

        if extra_data is not None:
            domain.extra_data = extra_data

        if commit:
            try:
                await session.commit()
                await session.refresh(domain)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error guardando TunnelDomain", extra={"user_id": domain.user_id, "domain_id": domain_id})
                raise
        logger.info("TunnelDomain actualizado", extra={"user_id": domain.user_id, "domain_id": domain_id})
        return domain
    except ValueError:
        raise
    except SQLAlchemyError:
        logger.exception("Error en update_tunnel_domain", extra={"user_id": None, "domain_id": domain_id})
        raise


async def delete_tunnel_domain(session: AsyncSession, domain_id: str, *, commit: bool = False) -> bool:
    """Elimina un dominio de túnel por ID."""
    try:
        domain = await get_tunnel_domain_by_id(session, domain_id)
        if not domain:
            return False
        await session.delete(domain)
        if commit:
            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error borrando TunnelDomain", extra={"user_id": domain.user_id, "domain_id": domain_id})
                raise
        logger.info("TunnelDomain eliminada", extra={"user_id": domain.user_id, "domain_id": domain_id})
        return True
    except SQLAlchemyError:
        logger.exception("Error en delete_tunnel_domain", extra={"user_id": None, "domain_id": domain_id})
        raise


async def verify_tunnel_domain(session: AsyncSession, domain_id: str, *, commit: bool = False) -> Optional[models.TunnelDomain]:
    """
    Marca un dominio como verificado y actualiza last_verified.
    """
    try:
        domain = await get_tunnel_domain_by_id(session, domain_id)
        if not domain:
            return None

        domain.is_verified = True
        domain.last_verified = datetime.now(timezone.utc)

        if commit:
            try:
                await session.commit()
                await session.refresh(domain)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error verificando TunnelDomain", extra={"user_id": domain.user_id, "domain_id": domain_id})
                raise
        logger.info("TunnelDomain verificado", extra={"user_id": domain.user_id, "domain_id": domain_id})
        return domain
    except SQLAlchemyError:
        logger.exception("Error en verify_tunnel_domain", extra={"user_id": None, "domain_id": domain_id})
        raise


async def unverify_tunnel_domain(session: AsyncSession, domain_id: str, *, commit: bool = False) -> Optional[models.TunnelDomain]:
    """
    Marca un dominio como no verificado.
    """
    try:
        domain = await get_tunnel_domain_by_id(session, domain_id)
        if not domain:
            return None

        domain.is_verified = False
        domain.last_verified = None

        if commit:
            try:
                await session.commit()
                await session.refresh(domain)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error desverficando TunnelDomain", extra={"user_id": domain.user_id, "domain_id": domain_id})
                raise
        logger.info("TunnelDomain desverificado", extra={"user_id": domain.user_id, "domain_id": domain_id})
        return domain
    except SQLAlchemyError:
        logger.exception("Error en unverify_tunnel_domain", extra={"user_id": None, "domain_id": domain_id})
        raise


async def assign_domain_to_vpn_config(
    session: AsyncSession,
    domain_id: str,
    vpn_config_id: str,
    *,
    commit: bool = False,
) -> Optional[models.TunnelDomain]:
    """
    Asigna un dominio a una configuración VPN.
    """
    try:
        domain = await get_tunnel_domain_by_id(session, domain_id)
        if not domain:
            return None

        # Verificar que la VPN config existe
        vpn_config = await session.execute(select(models.VPNConfig).where(models.VPNConfig.id == vpn_config_id))
        if not vpn_config.scalars().one_or_none():
            raise ValueError("vpn_config_not_found")

        domain.vpn_config_id = vpn_config_id

        if commit:
            try:
                await session.commit()
                await session.refresh(domain)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error asignando dominio a VPN", extra={"user_id": domain.user_id, "domain_id": domain_id, "vpn_config_id": vpn_config_id})
                raise
        logger.info("Dominio asignado a VPN", extra={"user_id": domain.user_id, "domain_id": domain_id, "vpn_config_id": vpn_config_id})
        return domain
    except ValueError:
        raise
    except SQLAlchemyError:
        logger.exception("Error en assign_domain_to_vpn_config", extra={"user_id": None, "domain_id": domain_id})
        raise


async def unassign_domain_from_vpn_config(session: AsyncSession, domain_id: str, *, commit: bool = False) -> Optional[models.TunnelDomain]:
    """
    Desasigna un dominio de cualquier configuración VPN.
    """
    try:
        domain = await get_tunnel_domain_by_id(session, domain_id)
        if not domain:
            return None

        domain.vpn_config_id = None

        if commit:
            try:
                await session.commit()
                await session.refresh(domain)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error desasignando dominio de VPN", extra={"user_id": domain.user_id, "domain_id": domain_id})
                raise
        logger.info("Dominio desasignado de VPN", extra={"user_id": domain.user_id, "domain_id": domain_id})
        return domain
    except SQLAlchemyError:
        logger.exception("Error en unassign_domain_from_vpn_config", extra={"user_id": None, "domain_id": domain_id})
        raise


async def get_domains_assigned_to_vpn_config(session: AsyncSession, vpn_config_id: str) -> List[models.TunnelDomain]:
    """
    Obtiene todos los dominios asignados a una configuración VPN específica.
    """
    try:
        result = await session.execute(select(models.TunnelDomain).where(models.TunnelDomain.vpn_config_id == vpn_config_id))
        return result.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo dominios por VPN config", extra={"user_id": None, "vpn_config_id": vpn_config_id})
        raise


async def list_tunnel_domains(
    session: AsyncSession,
    *,
    status: Optional[str] = None,
    is_verified: Optional[bool] = None,
    limit: int = 50,
) -> List[models.TunnelDomain]:
    """
    Lista dominios de túnel con filtros opcionales.
    """
    try:
        stmt = select(models.TunnelDomain)

        if status is not None:
            stmt = stmt.where(models.TunnelDomain.status == status)

        if is_verified is not None:
            stmt = stmt.where(models.TunnelDomain.is_verified == is_verified)

        stmt = stmt.order_by(models.TunnelDomain.assigned_at.desc()).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error listando TunnelDomains", extra={"user_id": None})
        raise


async def get_expired_tunnel_domains(session: AsyncSession) -> List[models.TunnelDomain]:
    """
    Devuelve todos los dominios de túnel vencidos y aún activos.
    Útil para jobs de mantenimiento.
    """
    try:
        now = datetime.now(timezone.utc)
        stmt = select(models.TunnelDomain).where(
            models.TunnelDomain.status == "active",
            models.TunnelDomain.expires_at < now,
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error listando dominios vencidos", extra={"user_id": None})
        raise


async def count_tunnel_domains_for_user(session: AsyncSession, user_id: str) -> int:
    """Cuenta el número de dominios de túnel para un usuario dado."""
    try:
        stmt = select(func.count()).select_from(models.TunnelDomain).where(models.TunnelDomain.user_id == user_id)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)
    except SQLAlchemyError:
        logger.exception("Error contando dominios por usuario", extra={"user_id": None, "target_user_id": user_id})
        raise


async def count_verified_domains_for_user(session: AsyncSession, user_id: str) -> int:
    """Cuenta el número de dominios verificados para un usuario dado."""
    try:
        stmt = select(func.count()).select_from(models.TunnelDomain).where(
            models.TunnelDomain.user_id == user_id,
            models.TunnelDomain.is_verified.is_(True)
        )
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)
    except SQLAlchemyError:
        logger.exception("Error contando dominios verificados por usuario", extra={"user_id": None, "target_user_id": user_id})
        raise