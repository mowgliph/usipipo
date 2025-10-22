# database/crud/payments.py

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from database import models


async def create_payment(
    session: AsyncSession,
    payment_id: str,
    user_id: str,
    vpn_type: str,
    months: int,
    amount_usd: float,
    amount_stars: int,
    commit: bool = True,
) -> Optional[models.Payment]:
    """
    Crea un nuevo pago pendiente.

    Args:
        session (AsyncSession): Sesión de base de datos.
        payment_id (str): ID del pago.
        user_id (str): ID del usuario.
        vpn_type (str): Tipo de VPN ('wireguard' o 'outline').
        months (int): Número de meses del plan.
        amount_usd (float): Monto en USD.
        amount_stars (int): Monto en Stars.
        commit (bool): Si hacer commit automáticamente.

    Returns:
        Optional[models.Payment]: El pago creado o None si falla.
    """
    try:
        payment = models.Payment(
            id=payment_id,
            user_id=user_id,
            vpn_type=vpn_type,
            months=months,
            amount_usd=amount_usd,
            amount_stars=amount_stars,
            status="pending",
        )
        session.add(payment)
        if commit:
            await session.commit()
            await session.refresh(payment)
        return payment
    except SQLAlchemyError:
        if commit:
            await session.rollback()
        raise


async def update_payment_status(
    session: AsyncSession,
    payment_id: str,
    status: str,
    commit: bool = True,
) -> Optional[models.Payment]:
    """
    Actualiza el estado de un pago.

    Args:
        session (AsyncSession): Sesión de base de datos.
        payment_id (str): ID del pago.
        status (str): Nuevo estado ('paid', 'failed', etc.).
        commit (bool): Si hacer commit automáticamente.

    Returns:
        Optional[models.Payment]: El pago actualizado o None si no se encuentra.
    """
    try:
        stmt = (
            update(models.Payment)
            .where(models.Payment.id == payment_id)
            .values(status=status)
            .returning(models.Payment)
        )
        result = await session.execute(stmt)
        payment = result.scalar_one_or_none()
        if payment and commit:
            await session.commit()
        return payment
    except SQLAlchemyError:
        if commit:
            await session.rollback()
        raise


async def get_user_payments(session: AsyncSession, user_id: str) -> List[models.Payment]:
    """
    Obtiene todos los pagos de un usuario.

    Args:
        session (AsyncSession): Sesión de base de datos.
        user_id (str): ID del usuario.

    Returns:
        List[models.Payment]: Lista de pagos del usuario.
    """
    try:
        stmt = select(models.Payment).where(models.Payment.user_id == user_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())
    except SQLAlchemyError:
        raise


async def get_payment_by_id(session: AsyncSession, payment_id: str) -> Optional[models.Payment]:
    """
    Obtiene un pago por su ID.

    Args:
        session (AsyncSession): Sesión de base de datos.
        payment_id (str): ID del pago.

    Returns:
        Optional[models.Payment]: El pago encontrado o None.
    """
    try:
        stmt = select(models.Payment).where(models.Payment.id == payment_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    except SQLAlchemyError:
        raise