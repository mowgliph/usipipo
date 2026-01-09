"""
Punto de entrada principal del bot uSipipo VPN Manager.

Author: uSipipo Team
Version: 2.0.0
"""

import sys
import asyncio
from utils.logger import logger
from telegram.ext import ApplicationBuilder

from config import settings
from application.services.common.container import get_container
from application.services.vpn_service import VpnService
from application.services.support_service import SupportService
from application.services.payment_service import PaymentService
from application.services.referral_service import ReferralService
from application.services.achievement_service import AchievementService
from application.services.ai_support_service import AiSupportService

# Importación de Database
from infrastructure.persistence.database import init_database, close_database

# Importación de Inicializador de Handlers
from telegram_bot.handlers.handler_initializer import initialize_handlers

# Importación de Jobs
from infrastructure.jobs.ticket_cleaner import close_stale_tickets_job
from infrastructure.jobs.usage_sync import sync_vpn_usage_job
from infrastructure.jobs.key_cleanup_job import key_cleanup_job
from infrastructure.jobs.conversation_cleanup_job import cleanup_stale_conversations_job

# Logging configurado desde utils.logger (centralizado en settings)


async def startup():
    """Inicialización de la aplicación."""
    logger.info("🔌 Inicializando conexión a base de datos...")
    await init_database()


async def shutdown():
    """Limpieza al cerrar la aplicación."""
    logger.info("🔌 Cerrando conexión a base de datos...")
    await close_database()


def main():
    """Función principal del bot."""
    logger.info("🚀 Iniciando uSipipo VPN Manager Bot...")

    # 1. Inicializar Contenedor de Dependencias
    try:
        container = get_container()
        vpn_service = container.resolve(VpnService)
        support_service = container.resolve(SupportService)
        referral_service = container.resolve(ReferralService)
        payment_service = container.resolve(PaymentService)
        achievement_service = container.resolve(AchievementService)
        ai_support_service = container.resolve(AiSupportService)
        logger.info("✅ Contenedor de dependencias configurado correctamente.")
        logger.info("🌊 Servicio de IA Sip inicializado correctamente.")
    except Exception as e:
        logger.critical(f"❌ Error al inicializar el contenedor: {e}")
        sys.exit(1)

    # 2. Configurar la Aplicación de Telegram
    if not settings.TELEGRAM_TOKEN:
        logger.error("❌ No se encontró el TELEGRAM_TOKEN en el archivo .env")
        sys.exit(1)

    async def post_init_callback(app):
        """Callback ejecutado después de inicializar la aplicación."""
        await startup()

    async def post_shutdown_callback(app):
        """Callback ejecutado después de cerrar la aplicación."""
        await shutdown()

    application = (
        ApplicationBuilder()
        .token(settings.TELEGRAM_TOKEN)
        .post_init(post_init_callback)
        .post_shutdown(post_shutdown_callback)
        .build()
    )

    # 3. Registrar JobQueue para automatización
    job_queue = application.job_queue
    
    # Job de limpieza de tickets (cada hora)
    job_queue.run_repeating(
        close_stale_tickets_job,
        interval=3600,
        first=10,
        data={'support_service': support_service}
    )
    logger.info("⏰ Job de limpieza de tickets programado (cada 1h).")
    
    # Job de sincronización de uso (cada 30 min)
    job_queue.run_repeating(
        sync_vpn_usage_job,
        interval=1800,
        first=60,
        data={'vpn_service': vpn_service}
    )
    logger.info("⏰ Job de cuota programado.")

    # Job de limpieza de llaves (cada hora)
    job_queue.run_repeating(
        key_cleanup_job,
        interval=3600,
        first=30,
        data={'vpn_service': vpn_service}
    )
    logger.info("⏰ Job de limpieza de llaves programado.")
    
    # Job de limpieza de conversaciones IA (cada 6 horas)
    job_queue.run_repeating(
        cleanup_stale_conversations_job,
        interval=21600,
        first=300,
        data={'ai_support_service': ai_support_service}
    )
    logger.info("🌊 Job de limpieza de conversaciones IA programado (cada 6h).")

    # 4. Registro de Handlers Principales
    handlers = initialize_handlers(
        vpn_service,
        support_service,
        referral_service,
        payment_service,
        achievement_service
    )
    for handler in handlers:
        application.add_handler(handler)

    # 5. Encender el Bot
    logger.info("🤖 Bot en línea y escuchando mensajes...")
    application.run_polling()


if __name__ == "__main__":
    main()
