# jobs/register_jobs.py

from __future__ import annotations
from telegram.ext import Application
from datetime import datetime
from zoneinfo import ZoneInfo

from jobs.system import ping_job
from jobs.maintenance import maintenance_job
from bot.handlers.alerts import expiration_alerts_job

def register_jobs(app: Application) -> None:
    """
    Registra todas las tareas periódicas en la aplicación Telegram.
    """
    # Tarea de ping cada 60s
    app.job_queue.run_repeating(ping_job, interval=60, first=0)

    # Tarea de mantenimiento cada 24h a las 03:00 UTC
    app.job_queue.run_repeating(maintenance_job, interval=86400, first=60*60*3)

    # Job diario para alertas de expiración a las 9 AM UTC
    app.job_queue.run_daily(
        callback=expiration_alerts_job,
        time=datetime.time(hour=9, minute=0, tzinfo=ZoneInfo("UTC")),
        days=(0, 1, 2, 3, 4, 5, 6),
    )