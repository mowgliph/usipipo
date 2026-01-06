from application.services.vpn_service import VpnService
from telegram.ext import ContextTypes
from datetime import datetime, timedelta, timezone
from typing import List
from domain.entities.vpn_key import VpnKey
from utils.logger import logger

def _normalize_datetime(dt: datetime) -> datetime:
    """
    Normaliza un datetime a naive (sin timezone) para comparaciones consistentes.
    Si tiene timezone, convierte a UTC y quita el tzinfo.
    """
    if dt is None:
        return None
    if dt.tzinfo is not None:
        # Convertir a UTC y luego quitar timezone
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


async def key_cleanup_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Tarea programada que realiza limpieza de llaves inactivas,
    resetea el uso de datos cuando corresponde, y notifica límites de datos.
    Se ejecuta periódicamente.
    """
    vpn_service: VpnService = context.job.data['vpn_service']

    try:
        logger.info("🧹 Iniciando limpieza de llaves y verificación de límites...")

        # Obtener todas las llaves activas
        active_keys = await vpn_service.get_all_active_keys()

        if not active_keys:
            logger.info("ℹ️ No hay llaves activas para procesar.")
            return

        # Ejecutar las tareas de limpieza
        await cleanup_inactive_keys(vpn_service, active_keys)
        await reset_data_usage(vpn_service, active_keys)
        await check_and_notify_data_limits(context, vpn_service, active_keys)

        logger.info("✅ Limpieza completada exitosamente.")

    except Exception as e:
        logger.error(f"❌ Error en key_cleanup_job: {e}")


async def cleanup_inactive_keys(vpn_service: VpnService, keys: List[VpnKey]):
    """
    Desactiva llaves que no han sido usadas en los últimos 90 días.
    """
    # Usar datetime.utcnow() para consistencia (siempre naive UTC)
    now_naive = datetime.utcnow()
    inactive_threshold = now_naive - timedelta(days=90)
    deactivated_count = 0

    for key in keys:
        if key.last_seen_at:
            # Normalizar la fecha de la llave antes de comparar
            last_seen_naive = _normalize_datetime(key.last_seen_at)
            if last_seen_naive and last_seen_naive < inactive_threshold:
                # Desactivar la llave
                if await vpn_service.deactivate_inactive_key(key.id):
                    deactivated_count += 1
                    logger.info(f"🔒 Llave {key.id} desactivada por inactividad (última actividad: {key.last_seen_at})")

    logger.info(f"🗑️ {deactivated_count} llaves desactivadas por inactividad.")


async def reset_data_usage(vpn_service: VpnService, keys: List[VpnKey]):
    """
    Resetea el uso de datos para llaves que han completado su ciclo de facturación.
    """
    reset_count = 0

    for key in keys:
        if await vpn_service.check_and_reset_billing_cycle(key):
            reset_count += 1
            logger.info(f"🔄 Uso de datos reseteado para llave {key.id}")

    logger.info(f"📊 {reset_count} ciclos de facturación reseteados.")


async def check_and_notify_data_limits(context: ContextTypes.DEFAULT_TYPE, vpn_service: VpnService, keys: List[VpnKey]):
    """
    Verifica si alguna llave ha excedido su límite de datos y notifica al usuario.
    """
    notified_users = set()

    for key in keys:
        if key.is_over_limit and key.user_id not in notified_users:
            try:
                await context.bot.send_message(
                    chat_id=key.user_id,
                    text=f"⚠️ **Límite de datos excedido**\n\n"
                         f"Tu llave '{key.name}' ha consumido {key.used_gb:.2f} GB de {key.data_limit_gb:.2f} GB permitidos.\n\n"
                         f"Considera actualizar tu plan o esperar al próximo ciclo de facturación.",
                    parse_mode="Markdown"
                )
                notified_users.add(key.user_id)
                logger.info(f"📢 Notificación enviada a usuario {key.user_id} por exceder límite de datos.")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo notificar al usuario {key.user_id}: {e}")

    logger.info(f"📢 {len(notified_users)} usuarios notificados por límites de datos.")