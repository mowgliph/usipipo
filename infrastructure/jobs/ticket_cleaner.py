from application.services.support_service import SupportService
from telegram.ext import ContextTypes
from loguru import logger
from telegram_bot.messages.messages import Messages

async def close_stale_tickets_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Tarea programada que revisa y cierra tickets inactivos.
    Se ejecuta cada hora.
    """
    # Obtenemos el servicio desde el contenedor de dependencias (inyectado en main)
    support_service: SupportService = context.job.context['support_service']
    
    try:
        closed_users = await support_service.check_and_close_stale_tickets()
        
        for user_id in closed_users:
            try:
                # Avisar al usuario que su ticket se cerró por tiempo
                await context.bot.send_message(
                    chat_id=user_id,
                    text="⏰ **Ticket cerrado automáticamente** debido a 48h de inactividad.\nSi aún necesitas ayuda, abre uno nuevo."
                )
                logger.info(f"Ticket del usuario {user_id} cerrado por inactividad (48h).")
            except Exception:
                # El usuario pudo bloquear al bot
                pass
                
    except Exception as e:
        logger.error(f"Error en el Job de limpieza de tickets: {e}")
