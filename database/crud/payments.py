# database/crud/payments.py

from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

import logging

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from services.payments import calculate_price
from database import models

logger = logging.getLogger("usipipo.crud.payments")


async def create_payment(
    session: AsyncSession,
    user_id: str,
    vpn_type: str,
    months: int,
    *,
    commit: bool = False,
) -> models.Payment:
    """
    Crea un nuevo registro de pago usando la lógica de precios de services.payments.
    - session: AsyncSession
    - user_id: UUID string
    - vpn_type: 'wireguard' | 'outline' (validar en services)
    - months: cantidad de meses
    - commit: si True hace commit() y refresh() antes de devolver el objeto
    """
    try:
        price = calculate_price(months)  # espera dict con keys: usd, stars, ton

        payment = models.Payment(
            user_id=user_id,
            vpn_type=vpn_type,
            months=months,
            amount_usd=float(price.get("usd", 0.0)),
            amount_stars=int(price.get("stars", 0)),
            amount_ton=float(price.get("ton", 0.0)),
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        session.add(payment)

        if commit:
            try:
                await session.commit()
                await session.refresh(payment)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al commitear create_payment", extra={"user_id": user_id})
                raise

        logger.info("Payment creado", extra={"user_id": user_id, "payment_id": getattr(payment, "id", None)})
        return payment
    except Exception:
        logger.exception("Error creando payment", extra={"user_id": user_id})
        raise


async def update_payment_status(
    session: AsyncSession,
    payment_id: str,
    status: str,
    *,
    commit: bool = False,
) -> Optional[models.Payment]:
    """
    Actualiza el estado de un pago: 'pending' -> 'paid'|'failed'.
    - payment_id: UUID string
    - commit: si True hace commit() y refresh()
    """
    try:
        stmt = select(models.Payment).where(models.Payment.id == payment_id)
        res = await session.execute(stmt)
        payment = res.scalars().one_or_none()
        if not payment:
            return None

        payment.status = status
        if commit:
            try:
                await session.commit()
                await session.refresh(payment)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al commitear update_payment_status", extra={"user_id": payment.user_id, "payment_id": payment_id})
                raise

        logger.info("Payment status actualizado", extra={"user_id": payment.user_id, "payment_id": payment_id, "status": status})
        return payment
    except SQLAlchemyError:
        logger.exception("Error en update_payment_status", extra={"user_id": None, "payment_id": payment_id})
        raise


async def get_payment(session: AsyncSession, payment_id: str) -> Optional[models.Payment]:
    """Obtiene un pago por ID (UUID string)."""
    try:
        stmt = select(models.Payment).where(models.Payment.id == payment_id)
        res = await session.execute(stmt)
        return res.scalars().one_or_none()
    except SQLAlchemyError:
        logger.exception("Error obteniendo payment", extra={"user_id": None, "payment_id": payment_id})
        raise


async def get_user_payments(session: AsyncSession, user_id: str, limit: int = 50) -> List[models.Payment]:
    """Devuelve los pagos de un usuario ordenados por created_at desc."""
    try:
        stmt = (
            select(models.Payment)
            .where(models.Payment.user_id == user_id)
            .order_by(models.Payment.created_at.desc())
            .limit(limit)
        )
        res = await session.execute(stmt)
        return res.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo pagos de usuario", extra={"user_id": user_id})
        raise


async def list_payments(session: AsyncSession, limit: int = 100) -> List[models.Payment]:
    """Devuelve los pagos recientes (para admins)."""
    try:
        stmt = select(models.Payment).order_by(models.Payment.created_at.desc()).limit(limit)
        res = await session.execute(stmt)
        return res.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error listando payments", extra={"user_id": None})
        raise


async def count_payments(session: AsyncSession) -> int:
    """Cuenta la cantidad total de pagos registrados."""
    try:
        stmt = select(func.count()).select_from(models.Payment)
        res = await session.execute(stmt)
        return int(res.scalar_one() or 0)
    except SQLAlchemyError:
        logger.exception("Error contando payments", extra={"user_id": None})
        raise