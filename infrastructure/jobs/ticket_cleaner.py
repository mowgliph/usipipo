from application.services.support_service import SupportService
from telegram.ext import ContextTypes
from utils.logger import logger

async def close_stale_tickets_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Tarea programada que revisa y cierra tickets inactivos.
    Se ejecuta cada hora.
    """
    # CORRECCIÓN: Usar context.job.data en lugar de context.job.context
    support_service: SupportService = context.job.data['support_service']
    
    try:
        closed_users = await support_service.check_and_close_stale_tickets()
        
        for user_id in closed_users:
            try:
                # Avisar al usuario que su ticket se cerró por tiempo
                await context.bot.send_message(
                    chat_id=user_id,
                    text="⏰ **Ticket cerrado automáticamente** debido a 48h de inactividad.\n\nSi aún necesitas ayuda, abre uno nuevo.",
                    parse_mode="Markdown"
                )
                logger.info(f"✅ Ticket del usuario {user_id} cerrado por inactividad (48h).")
            except Exception as e:
                # El usuario pudo bloquear al bot
                logger.warning(f"⚠️ No se pudo notificar al usuario {user_id}: {e}")
                
        logger.info(f"✅ Job completado. {len(closed_users)} tickets cerrados.")
                
    except Exception as e:
        logger.error(f"❌ Error en el Job de limpieza de tickets: {e}")
