# config/logger.py
import logging
import os
import sys
import platform
import gzip
import shutil
from typing import cast, BinaryIO
from logging.handlers import TimedRotatingFileHandler
import asyncio

# DB imports (async)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from database.db import AsyncSessionLocal as get_session
from database import models
from config.config import BOT_VERSION

LOG_DIR = "logs"
LOG_PATH = os.path.join(LOG_DIR, "usipipo.log")


# -------------------------
# Rotación con compresión
# -------------------------
def namer(name):
    return name + ".gz"


def rotator(source, dest):
    # gzip.open has overloaded return types (GzipFile | TextIOWrapper) which
    # confuses static type checkers. We know we open in binary mode, so cast
    # to BinaryIO to satisfy pylance/pyright for shutil.copyfileobj.
    with open(source, "rb") as fin, gzip.open(dest, "wb") as fout:
        shutil.copyfileobj(fin, cast(BinaryIO, fout))
    os.remove(source)


# -------------------------
# Handler que escribe en audit_logs (async task)
# -------------------------
class AuditLogHandler(logging.Handler):
    """
    Handler de logging que guarda los logs en la tabla audit_logs.
    - Usa el nivel como 'action' (info/warning/error/critical/debug).
    - Guarda el mensaje formateado completo en 'details'.
    - Permite asociar user_id si se pasa en extra={"user_id": int}.
    - Ejecuta el registro en un task async para no bloquear el loop.
    """

    level_action_map = {
        logging.DEBUG: "debug",
        logging.INFO: "info",
        logging.WARNING: "warning",
        logging.ERROR: "error",
        logging.CRITICAL: "critical",
    }

    def emit(self, record: logging.LogRecord):
        # Evita recursión si el handler genera logs propios
        if record.name == __name__:
            return

        # Ejecutar el registro async en un task separado
        asyncio.create_task(self._async_emit(record))

    async def _async_emit(self, record: logging.LogRecord):
        async with get_session() as session:
            try:
                action = self.level_action_map.get(record.levelno, "info")

                # Formatear mensaje con el formatter del handler si existe
                msg = self.format(record)

                # Si se pasa user_id en extra, lo asociamos; si no, None (log del sistema)
                user_id = getattr(record, "user_id", None)

                log = models.AuditLog(
                    user_id=user_id,
                    action=action,
                    details=msg,
                )

                session.add(log)
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
            except Exception:
                # Nunca levantar excepciones desde emit; el logger debe ser resiliente
                pass


# -------------------------
# Setup del logger raíz
# -------------------------
def setup_logger():
    os.makedirs(LOG_DIR, exist_ok=True)

    # Logger raíz
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(logging.INFO)

    # Rotación diaria con backup de 5 días
    file_handler = TimedRotatingFileHandler(
        LOG_PATH, when="midnight", interval=1, backupCount=5, encoding="utf-8"
    )
    file_handler.namer = namer
    file_handler.rotator = rotator

    # Salida a stdout
    stream_handler = logging.StreamHandler(sys.stdout)

    # Formato consistente con user_id
    formatter = logging.Formatter(
        "%(asctime)s | PID:%(process)d | %(levelname)s | [user_id=%(user_id)s] %(message)s"
    )
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Handler a DB (audit_logs)
    audit_handler = AuditLogHandler()
    audit_handler.setFormatter(formatter)

    # Añadir handlers
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.addHandler(audit_handler)

    # Silenciar librerías externas ruidosas
    noisy_loggers = [
        "telegram",
        "telegram.ext",
        "telegram.ext._application",
        "telegram.ext._httpx",
        "telegram.vendor.ptb_urllib3.urllib3.connectionpool",
        "httpx",
        "apscheduler",
    ]
    for name in noisy_loggers:
        third_party_logger = logging.getLogger(name)
        third_party_logger.handlers.clear()
        third_party_logger.propagate = False
        third_party_logger.setLevel(logging.CRITICAL)

    # Logs de arranque (se registran en archivo, stdout y audit_logs)
    logging.info(f"Bot uSipipo v{BOT_VERSION} iniciado", extra={"user_id": None})
    logging.info(f"Python version: {platform.python_version()}", extra={"user_id": None})
    logging.info("Status: RUNNING", extra={"user_id": None})


# -------------------------
# Compatibilidad y transición
# -------------------------
def get_last_logs(n=10):
    """
    Devuelve las últimas n líneas del archivo de logs.
    Mantenido por compatibilidad; se prefiere get_last_logs_db para DB.
    """
    try:
        with open(LOG_PATH, "r") as f:
            lines = f.readlines()
            return lines[-n:] if len(lines) >= n else lines
    except Exception as e:
        return [f"Error al leer logs: {e}"]


async def get_last_logs_db(n=10, user_id=None):
    """
    Devuelve las últimas n entradas desde audit_logs (async).
    Si se pasa user_id, filtra por ese usuario.
    """
    async with get_session() as session:
        try:
            q = select(models.AuditLog)
            if user_id is not None:
                q = q.filter(models.AuditLog.user_id == user_id)
            q = q.order_by(models.AuditLog.created_at.desc()).limit(n)
            result = await session.execute(q)
            logs = result.scalars().all()

            formatted = []
            for log in logs:
                who = (
                    f"@{log.user.username}"
                    if log.user and log.user.username
                    else (f"ID:{log.user_id}" if log.user_id else "SYSTEM")
                )
                formatted.append(
                    f"{log.created_at.strftime('%Y-%m-%d %H:%M:%S')} | {who} | "
                    f"{log.action} | {log.details or ''}"
                )
            return list(reversed(formatted))
        except SQLAlchemyError as e:
            return [f"Error al leer audit logs: {e}"]
