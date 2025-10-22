# config/config.py

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Set
from dotenv import load_dotenv

load_dotenv()

# Variables de entorno principales
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_VERSION = os.getenv("BOT_VERSION", "1.0.0")

# Base de Datos
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_ASYNC_URL = os.getenv("DATABASE_ASYNC_URL")
DATABASE_SYNC_URL = os.getenv("DATABASE_SYNC_URL", DATABASE_URL)  # Fallback

# Opciones de pool de BD
DB_POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
DB_ECHO_SQL = os.getenv("DB_ECHO_SQL", "false").lower() == "true"
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

# Servidores VPN
# WireGuard (generado por wireguard-install.sh)
WG_INTERFACE = os.getenv("WG_INTERFACE")
WG_CONFIG_DIR = os.getenv("WG_CONFIG_DIR")
WG_SERVER_PRIV_KEY = os.getenv("WG_SERVER_PRIV_KEY")
WG_SERVER_PUB_KEY = os.getenv("WG_SERVER_PUB_KEY")
WG_SERVER_IP = os.getenv("WG_SERVER_IP")
WG_PORT = os.getenv("WG_PORT", "51820")
WG_SUBNET_BASE = os.getenv("WG_SUBNET_BASE")
WG_DNS = os.getenv("WG_DNS", "1.1.1.1")
WG_ALLOWED_IPS = os.getenv("WG_ALLOWED_IPS", "0.0.0.0/0")

# Outline (generado por outline-install.sh)
OUTLINE_API_URL = os.getenv("OUTLINE_API_URL")
OUTLINE_CERT_SHA256 = os.getenv("OUTLINE_CERT_SHA256")
OUTLINE_API_PORT = os.getenv("OUTLINE_API_PORT")
OUTLINE_HOSTNAME = os.getenv("OUTLINE_HOSTNAME")
OUTLINE_CONTAINER_NAME = os.getenv("OUTLINE_CONTAINER_NAME")
OUTLINE_IMAGE = os.getenv("OUTLINE_IMAGE")

# MTProto (generado por mtproto-install.sh)
MTPROXY_HOST = os.getenv("MTPROXY_HOST")
MTPROXY_PORT = os.getenv("MTPROXY_PORT")
MTPROXY_SECRET = os.getenv("MTPROXY_SECRET")
MTPROXY_DIR = os.getenv("MTPROXY_DIR")
MTPROXY_TAG = os.getenv("MTPROXY_TAG")  # Opcional, de @MTProxybot

# Configuración de permisos (admins desde env para flexibilidad)
ADMIN_TG_IDS_RAW = os.getenv("ADMIN_TG_IDS", "")
ADMIN_TG_IDS: Set[int] = set()
if ADMIN_TG_IDS_RAW.strip():
    try:
        ADMIN_TG_IDS = {int(x.strip()) for x in ADMIN_TG_IDS_RAW.split(",") if x.strip()}
    except ValueError as e:
        logging.warning(f"Error parseando ADMIN_TG_IDS: {e}. Usando set vacío.")

# Configuración de límites y aplicación
MAX_VPN_PER_USER = int(os.getenv("MAX_VPN_PER_USER", "5"))
TRIAL_DURATION_DAYS = int(os.getenv("TRIAL_DURATION_DAYS", "7"))
BANDWIDTH_LIMIT_MB = int(os.getenv("BANDWIDTH_LIMIT_MB", "1000"))
MAX_CONCURRENT_USERS = int(os.getenv("MAX_CONCURRENT_USERS", "100"))

# Configuración de pagos
PAYMENT_CURRENCY = os.getenv("PAYMENT_CURRENCY", "USD")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

# Logging y archivos
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "/var/log/usipipo")
TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/usipipo")

# Jobs/CRON
CLEANUP_JOB_INTERVAL = os.getenv("CLEANUP_JOB_INTERVAL", "24h")

# Validaciones críticas
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN no está definido")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está definido")


# Configuración de logging centralizado
logger = logging.getLogger("usipipo")
logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

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

# Función helper para validar configuración
def validate_config() -> bool:
    """
    Valida que la configuración crítica esté presente.
    Retorna True si todo está OK, False si hay problemas.
    """
    issues = []

    if not TELEGRAM_BOT_TOKEN:
        issues.append("TELEGRAM_BOT_TOKEN")
    if not DATABASE_URL:
        issues.append("DATABASE_URL")

    if issues:
        logging.error(f"Configuración inválida. Variables faltantes: {', '.join(issues)}")
        return False

    # Warnings para servicios opcionales
    optional_warnings = []
    if not OUTLINE_API_URL:
        optional_warnings.append("Outline (funcionalidad limitada)")
    if not WG_INTERFACE:
        optional_warnings.append("WireGuard (funcionalidad limitada)")
    if not MTPROXY_HOST:
        optional_warnings.append("MTProto (funcionalidad limitada)")

    if optional_warnings:
        logging.warning(f"Servicios opcionales no configurados: {', '.join(optional_warnings)}")

    logging.info("Configuración validada correctamente")
    return True


# Función helper para obtener configuración de BD
def get_database_config() -> dict:
    """
    Retorna configuración de base de datos para SQLAlchemy.
    """
    return {
        "url": DATABASE_URL,
        "async_url": DATABASE_ASYNC_URL,
        "sync_url": DATABASE_SYNC_URL,
        "pool_pre_ping": DB_POOL_PRE_PING,
        "echo": DB_ECHO_SQL,
        "max_overflow": DB_MAX_OVERFLOW,
        "pool_size": DB_POOL_SIZE,
        "pool_timeout": DB_POOL_TIMEOUT,
        "charset": DB_CHARSET,
    }