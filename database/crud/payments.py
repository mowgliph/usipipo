# database/crud/payments.py

from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

import logging

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

# Importamos calculate_price solo si se va a usar, o lo manejamos en el servicio
# from services.payments import calculate_price # Opcional: si se llama desde aquí
from database import models

logger = logging.getLogger("usipipo.crud.payments")


async def create_payment(
    session: AsyncSession,
    user_id: str,
    vpn_type: str,
    months: int,
    *,
    amount_usd: float,
    amount_stars: int,
    amount_ton: float,
    amount_sats: int = 0,
    payment_method: Optional[str] = None,
    status: str = "pending",
    extra_data: Optional[Dict[str, Any]] = None, # Campo extra_data del modelo Payment
    commit: bool = False,
) -> models.Payment:
    """
    Crea un nuevo registro de pago.
    Se espera que los montos hayan sido calculados previamente en el servicio.
    - session: AsyncSession
    - user_id: UUID string
    - vpn_type: 'wireguard' | 'outline' | 'none' (validar en services)
    - months: cantidad de meses
    - amount_usd: monto en USD
    - amount_stars: monto en estrellas (para pagos en Telegram)
    - amount_ton: monto en TON
    - status: estado inicial del pago (por defecto 'pending')
    - extra_data: datos adicionales como dict (opcional)
    - commit: si True hace commit() y refresh() antes de devolver el objeto
    """
    try:
        payment = models.Payment(
            user_id=user_id,
            vpn_type=vpn_type,
            months=months,
            amount_usd=amount_usd,
            amount_stars=amount_stars,
            amount_ton=amount_ton,
            amount_sats=amount_sats,
            payment_method=payment_method,
            status=status,
            extra_data=extra_data, # Asumiendo que el modelo Payment tiene este campo, si no, quitar
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
    - status: nuevo estado
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


# --- Nuevas funciones para integración con lógica de negocio ---
async def get_pending_payments(session: AsyncSession, limit: int = 100) -> List[models.Payment]:
    """Obtiene pagos con estado 'pending' para procesamiento."""
    try:
        stmt = select(models.Payment).where(
            models.Payment.status == "pending"
        ).order_by(models.Payment.created_at.asc()).limit(limit)
        res = await session.execute(stmt)
        return res.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo pagos pendientes", extra={"user_id": None})
        raise


async def get_successful_payments_for_user(session: AsyncSession, user_id: str) -> List[models.Payment]:
    """Obtiene pagos exitosos de un usuario específico."""
    try:
        stmt = select(models.Payment).where(
            models.Payment.user_id == user_id,
            models.Payment.status == "paid"
        ).order_by(models.Payment.created_at.desc())
        res = await session.execute(stmt)
        return res.scalars().all()
    except SQLAlchemyError:
        logger.exception("Error obteniendo pagos exitosos del usuario", extra={"user_id": user_id})
        raise
