import sys
from loguru import logger
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

from config import settings
from application.services.common.container import get_container
from application.services.vpn_service import VpnService
from application.services.support_service import SupportService
from application.services.payment_service import PaymentService
from application.services.referral_service import ReferralService

# Importación de Inicializador de Handlers
from telegram_bot.handlers.handler_initializer import initialize_handlers

# Importación de Jobs
from infrastructure.jobs.ticket_cleaner import close_stale_tickets_job
from infrastructure.jobs.usage_sync import sync_vpn_usage_job
from infrastructure.jobs.key_cleanup_job import key_cleanup_job

# Configuración de Loguru para un rastreo claro
logger.add("logs/bot.log", rotation="10 MB", retention="10 days", level="INFO")

def main():
    logger.info("🚀 Iniciando uSipipo VPN Manager Bot...")

    # 1. Inicializar Contenedor de Dependencias
    try:
        container = get_container()
        vpn_service = container.resolve(VpnService)
        support_service = container.resolve(SupportService)
        referral_service = container.resolve(ReferralService)
        payment_service = container.resolve(PaymentService)
        logger.info("✅ Contenedor de dependencias configurado correctamente.")
    except Exception as e:
        logger.critical(f"❌ Error al inicializar el contenedor: {e}")
        sys.exit(1)

    # 2. Configurar la Aplicación de Telegram
    if not settings.TELEGRAM_TOKEN:
        logger.error("❌ No se encontró el TELEGRAM_TOKEN en el archivo .env")
        sys.exit(1)

    application = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()

    # 3. Registrar JobQueue para automatización (Cierre de tickets 48h)
    job_queue = application.job_queue
    job_queue.run_repeating(
        close_stale_tickets_job,
        interval=3600,  # Se ejecuta cada hora
        first=10,       # Primera ejecución a los 10 segundos
        data={'support_service': support_service}
    )
    logger.info("⏰ Job de limpieza de tickets programado (cada 1h).")
    
    job_queue.run_repeating(
        sync_vpn_usage_job,
        interval=1800,  # 30 minutos
        first=60,       # Primera ejecución tras 1 minuto de encendido
        data={'vpn_service': vpn_service}
    )
    logger.info("⏰ Job de  cuota programado.")

    job_queue.run_repeating(
        key_cleanup_job,
        interval=3600,  # Se ejecuta cada hora
        first=30,       # Primera ejecución a los 30 segundos
        data={'vpn_service': vpn_service}
    )
    logger.info("⏰ Job de limpieza de llaves programado.")

    # 4. Registro de Handlers Principales
    handlers = initialize_handlers(vpn_service, support_service, referral_service, payment_service)
    for handler in handlers:
        application.add_handler(handler)

    # 5. Encender el Bot
    logger.info("🤖 Bot en línea y escuchando mensajes...")
    application.run_polling()

if __name__ == "__main__":
    main()
