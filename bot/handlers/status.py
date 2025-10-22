# bot/handlers/status.py

import logging

from telegram import Update
from telegram.ext import ContextTypes

from database.db import AsyncSessionLocal as get_session
from services.status import get_status_metrics
from utils.helpers import send_success, send_generic_error
from utils.permissions import require_admin

logger = logging.getLogger("usipipo.handlers.status")

@require_admin
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Responde al comando /status mostrando métricas globales y estado del sistema.
    Uso: /status
    Solo accesible para admins. Registra la acción en AuditLog.
    """
    user = update.effective_user
    async with get_session() as session:
        try:
            # Obtener métricas desde el servicio
            metrics = await get_status_metrics(session)
            
            # Construir mensaje de estado (HTML)
            status_msg = (
                "<b>📊 Estado de uSipipo Bot</b>\n\n"
                f"👥 Usuarios registrados: <b>{metrics['total_users']}</b>\n"
                f"🌐 Configs WireGuard: <b>{metrics['total_wireguard']}</b>\n"
                f"🌐 Configs Outline: <b>{metrics['total_outline']}</b>\n"
                f"📡 Consumo total: <b>{metrics['total_bandwidth']:.2f} GB</b>\n"
                f"⏱️ Uptime: <b>{metrics['uptime']}</b>\n"
                f"🗄️ Base de datos: <b>{metrics['db_status']}</b>\n\n"
                "⚡ <b>uSipipo INFO RUNNING</b>"
            )

            await send_success(update, status_msg)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error en status_command: %s", type(e).__name__, extra={"tg_id": user.id})
            await send_generic_error(update, "Error obteniendo el estado del sistema. El equipo ha sido notificado.")