# config/config.py

from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

# Variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_VERSION = os.getenv("BOT_VERSION")
OUTLINE_API_URL = os.getenv("OUTLINE_API_URL")
OUTLINE_CERT_SHA256 = os.getenv("OUTLINE_CERT_SHA256")
DATABASE_URL = os.getenv("DATABASE_URL")

# Validaciones
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN no está definido")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está definido")
if not OUTLINE_API_URL:
    raise ValueError("OUTLINE_API_URL no está definido")
if not BOT_VERSION:
    raise ValueError("BOT_VERSION no está definido")

# Configuración de logging centralizado
logger = logging.getLogger("usipipo")
logger.setLevel(logging.INFO)

# Formato con user_id
formatter = logging.Formatter(
    "%(asctime)s [%(name)s] [%(levelname)s] [user_id=%(user_id)s] %(message)s",
    defaults={"user_id": None}  # Default para SYSTEM
)

# Handlers
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
file_handler = RotatingFileHandler("usipipo.log", maxBytes=10_000_000, backupCount=5)
file_handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(stream_handler)
logger.addHandler(file_handler)