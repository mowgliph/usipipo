# services/status.py
from typing import Dict, Any
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.crud import status as crud_status
from services.audit import audit_service
from config.runtime import BOT_START_TIME

logger = logging.getLogger("usipipo.status")

async def format_uptime(seconds: float) -> str:
    """Convierte segundos en formato legible (días, horas, minutos)."""
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)

async def get_status_metrics(session: AsyncSession) -> Dict[str, Any]:
    """
    Obtiene métricas globales del sistema para el comando /status.
    Registra la acción en AuditLog.
    """
    try:
        # Obtener métricas
        total_users = await crud_status.count_users(session)
        total_wireguard = await crud_status.count_vpn_configs_by_type(session, "wireguard")
        total_outline = await crud_status.count_vpn_configs_by_type(session, "outline")
        total_bandwidth = await crud_status.total_bandwidth_gb(session)

        # Calcular uptime
        uptime_seconds = (datetime.now(timezone.utc) - BOT_START_TIME).total_seconds()
        uptime_str = await format_uptime(uptime_seconds)

        # Verificar estado de la conexión
        db_status = "✅ Conectada" if (await session.execute(select(1))).scalar() else "❌ Error de conexión"

        metrics = {
            "total_users": total_users,
            "total_wireguard": total_wireguard,
            "total_outline": total_outline,
            "total_bandwidth": total_bandwidth,
            "uptime": uptime_str,
            "db_status": db_status,
        }

        # Registrar en AuditLog
        await audit_service.log_action(
            user_id=None,  # Sistema, no usuario específico
            action="command_status",
            details="Métricas del sistema consultadas",
            session=session,
            metrics=metrics
        )

        return metrics
    except Exception as e:
        logger.exception("Error en get_status_metrics", extra={"user_id": None})
        raise