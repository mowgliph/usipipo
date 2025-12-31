import sys
from loguru import logger
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config import settings
from application.services.common.container import get_container
from application.services.vpn_service import VpnService
from application.services.support_service import SupportService

# Importación de Handlers
from telegram_bot.handlers.start_handler import start_handler
from telegram_bot.handlers.crear_llave_handler import get_creation_handler
from telegram_bot.handlers.keys_manager_handler import list_keys_handler, delete_callback_handler
from telegram_bot.handlers.status_handler import status_handler
from telegram_bot.handlers.ayuda_handler import ayuda_handler
from telegram_bot.handlers.support_handler import get_support_handler, admin_reply_handler

# Importación de Jobs
from infrastructure.jobs.ticket_cleaner import close_stale_tickets_job
from infrastructure.jobs.usage_sync import sync_vpn_usage_job

# Configuración de Loguru para un rastreo claro
logger.add("logs/bot.log", rotation="10 MB", retention="10 days", level="INFO")

def main():
    logger.info("🚀 Iniciando uSipipo VPN Manager Bot...")

    # 1. Inicializar Contenedor de Dependencias
    try:
        container = get_container()
        vpn_service = container.resolve(VpnService)
        support_service = container.resolve(SupportService)
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

    # 4. Registro de Handlers Principales
    
    # Comando /start y botón de registro
    application.add_handler(CommandHandler("start", lambda u, c: start_handler(u, c, vpn_service)))
    
    # Flujo de Creación de Llaves (ConversationHandler)
    application.add_handler(get_creation_handler(vpn_service))
    
    # Gestión de Llaves (Listar y Botones Inline de borrado)
    application.add_handler(MessageHandler(filters.Regex("^🛡️ Mis Llaves$"), 
                                         lambda u, c: list_keys_handler(u, c, vpn_service)))
    application.add_handler(CallbackQueryHandler(lambda u, c: delete_callback_handler(u, c, vpn_service), 
                                                pattern="^(delete_|cancel_delete)"))

    # Estado y Métricas
    application.add_handler(MessageHandler(filters.Regex("^📊 Estado$"), 
                                         lambda u, c: status_handler(u, c, vpn_service)))
    
    # Ayuda General
    application.add_handler(MessageHandler(filters.Regex("^⚙️ Ayuda$"), ayuda_handler))

    # Soporte Directo Chat-to-Admin (ConversationHandler)
    application.add_handler(get_support_handler(support_service))
    
    # Handler especial para que el Admin responda
    application.add_handler(MessageHandler(filters.Chat(chat_id=int(settings.ADMIN_ID)) & ~filters.COMMAND, 
                                         lambda u, c: admin_reply_handler(u, c, support_service)))

    # 5. Encender el Bot
    logger.info("🤖 Bot en línea y escuchando mensajes...")
    application.run_polling()

if __name__ == "__main__":
    main()
