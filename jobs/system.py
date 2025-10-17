# jobs/system.py

from __future__ import annotations
import os
import platform
import logging
from telegram.ext import ContextTypes

from config.config import BOT_VERSION
from database.db import AsyncSessionLocal
from services.audit import log_action_auto_session

logger = logging.getLogger(__name__)

async def ping_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Tarea periódica para mantener el bot vivo y registrar estado (async).
    """
    pid = os.getpid()
    py_version = platform.python_version()
    msg = f"PID:{pid} | Bot v{BOT_VERSION} | Python v{py_version} | Status: RUNNING"

    # Log tradicional (archivo + stdout + DB vía AuditLogHandler)
    logger.info(msg, extra={"user_id": None})

    # Log explícito en audit_logs (async)
    await log_action_auto_session(
        user_id=None,
        action="system_ping",
        payload={"message": msg},
    )