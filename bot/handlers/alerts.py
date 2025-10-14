# bot/handlers/alerts.py

from __future__ import annotations
from telegram.ext import ContextTypes
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_session
from services import alerts as alerts_service
from utils.helpers import log_and_notify, log_error_and_notify, notify_admins

async def expiration_alerts_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Job diario para enviar alertas de VPNs próximas a expirar.
    - Usa AsyncSession.
    - Delega a services.alerts.
    - Controla transacciones.
    """
    bot = context.bot

    async with get_session() as session:  # type: AsyncSession
        try:
            await alerts_service.send_expiration_alerts(session, bot, hours=24, limit=100)
            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=None,
                user_id=None,
                action="expiration_alerts_job",
                details="Ejecutado job de alertas de expiración",
                message=None,
            )
            await session.commit()
        except Exception as e:
            await log_error_and_notify(
                session=session,
                bot=bot,
                chat_id=None,
                user_id=None,
                action="expiration_alerts_job",
                error=e,
                public_message=None,
            )
            await notify_admins(
                session=session,
                bot=bot,
                message=f"Error en job de alertas de expiración: {str(e)}",
                action="job_error",
                details=str(e),
            )