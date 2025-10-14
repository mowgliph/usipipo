# bot/main.py

import logging
from telegram.ext import ApplicationBuilder

# Configuraciones
from config.config import TELEGRAM_BOT_TOKEN
from routes.routes import register_handlers
from jobs.register_jobs import register_jobs
from config.logger import setup_logger

def main():
    setup_logger()

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Registro de comandos y tareas
    register_handlers(app)
    register_jobs(app)

    logging.info("🚀 Bot uSipipo ejecutándose...", extra={"user_id": None})
    app.run_polling()

if __name__ == "__main__":
    main()