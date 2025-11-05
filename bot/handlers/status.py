# bot/handlers/status.py

import logging

from telegram import Update
from telegram.ext import ContextTypes

from database.db import AsyncSessionLocal as get_session
from services.status import get_status_metrics, get_server_status, format_server_status_for_telegram
from utils.helpers import send_success, send_generic_error
from utils.permissions import require_admin

logger = logging.getLogger("usipipo.handlers.status")

@require_admin
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Responde al comando /status mostrando métricas globales, estado del sistema y estado de servidores VPN.
    Uso: /status
    Solo accesible para admins. Registra la acción en AuditLog.
    """
    user = update.effective_user
    async with get_session() as session:
        try:
            # Obtener métricas del bot
            metrics = await get_status_metrics(session)
            
            # Obtener estado de los servidores VPN
            server_status = await get_server_status()
            
            # Construir mensaje de estado del bot (HTML)
            bot_status_msg = (
                "<b>📊 Estado de uSipipo Bot</b>\n\n"
                f"👥 Usuarios registrados: <b>{metrics['total_users']}</b>\n"
                f"🌐 Configs WireGuard: <b>{metrics['total_wireguard']}</b>\n"
                f"🌐 Configs Outline: <b>{metrics['total_outline']}</b>\n"
                f"📡 Consumo total: <b>{metrics['total_bandwidth']:.2f} GB</b>\n"
                f"⏱️ Uptime: <b>{metrics['uptime']}</b>\n"
                f"🗄️ Base de datos: <b>{metrics['db_status']}</b>\n\n"
            )
            
            # Construir mensaje de estado de servidores VPN
            servers_status_msg = format_server_status_for_telegram(server_status)
            
            # Combinar ambos mensajes
            full_status_msg = bot_status_msg + servers_status_msg + "\n\n⚡ <b>uSipipo INFO RUNNING</b>"

            await send_success(update, full_status_msg)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error en status_command: %s", type(e).__name__, extra={"tg_id": user.id})
            await send_generic_error(update, "Error obteniendo el estado del sistema. El equipo ha sido notificado.")