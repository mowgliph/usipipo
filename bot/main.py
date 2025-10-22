# bot/main.py

import logging
import asyncio
from telegram.ext import ApplicationBuilder

# Configuraciones
from config.config import TELEGRAM_BOT_TOKEN
from routes.routes import register_handlers
from jobs.register_jobs import register_jobs
from config.logger import setup_logger
from services.alerts import send_daily_status_notification

async def send_startup_notification(app):
    """Envía notificación de status al iniciar el bot."""
    try:
        await send_daily_status_notification(bot=app.bot)
        logging.info("Notificación de inicio enviada a superadmins", extra={"user_id": None})
    except Exception as e:
        logging.error("Error enviando notificación de inicio", extra={"user_id": None, "error": str(e)})

def main():
    setup_logger()

    if TELEGRAM_BOT_TOKEN is None:
        logging.error("TELEGRAM_BOT_TOKEN is not set. Please check your configuration.", extra={"user_id": None})
        raise SystemExit(1)

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Registro de comandos y tareas
    register_handlers(app)
    register_jobs(app)

    # Enviar notificación de status al iniciar
    asyncio.run(send_startup_notification(app))

    logging.info("🚀 Bot uSipipo ejecutándose...", extra={"user_id": None})
    app.run_polling()

if __name__ == "__main__":
    main()