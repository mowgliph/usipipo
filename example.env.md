# .env.example - Plantilla de variables de entorno para uSipipo

# ========================================
# Telegram Bot
# ========================================
# Token del bot de Telegram obtenido de @BotFather
TELEGRAM_BOT_TOKEN=

# ========================================
# Base de Datos (MariaDB)
# ========================================
# URLs generadas por init_db.py
# URL síncrona (usada por herramientas CLI, migraciones)
DATABASE_URL=
# URL asíncrona (usada por la aplicación principal con SQLAlchemy async)
DATABASE_ASYNC_URL=
# URL síncrona duplicada (por compatibilidad, opcional)
DATABASE_SYNC_URL=

# Opciones de configuración del pool de conexiones (opcional)
DB_POOL_PRE_PING=true
DB_ECHO_SQL=false
DB_MAX_OVERFLOW=10
DB_POOL_SIZE=5
DB_POOL_TIMEOUT=30
DB_CHARSET=utf8mb4
# Opcional: Timeout de lectura/escritura para el driver (si es compatible)
# DB_READ_TIMEOUT=60
# DB_WRITE_TIMEOUT=60
# Opcional: Usar NullPool (útil para entornos serverless o tests)
# DB_POOL_CLASS=null

# ========================================
# Servidor WireGuard
# ========================================
# Variables generadas por wireguard-install.sh (refactorizado)
WG_INTERFACE=
WG_CONFIG_DIR=
WG_SERVER_PRIV_KEY=
WG_SERVER_PUB_KEY=
WG_SERVER_IP=
WG_PORT=
WG_SUBNET_BASE=
WG_DNS=
WG_ALLOWED_IPS=

# ========================================
# Servidor Outline
# ========================================
# Variables generadas por outline-install.sh (refactorizado)
OUTLINE_API_URL=
OUTLINE_CERT_SHA256=
OUTLINE_API_PORT=
OUTLINE_HOSTNAME=
OUTLINE_CONTAINER_NAME=
OUTLINE_IMAGE=

# ========================================
# Servidor MTProto
# ========================================
# Variables generadas por mtproto-install.sh (refactorizado)
MTPROXY_HOST=
MTPROXY_PORT=
MTPROXY_SECRET=
MTPROXY_DIR=
# TAG opcional, obtenido de @MTProxybot después de registrar el proxy
# MTPROXY_TAG=

# ========================================
# Otras Configuraciones (uSipipo App)
# ========================================
# Límites de IPs para trial (definidos en scripts y manejados por la app)
# wg_trial_ips: ["WG_SUBNET_BASE.2", ... "WG_SUBNET_BASE.26"] (Ej: 10.66.66.2 - 10.66.66.26)
# outline_trial_ips: [] (No se asignan IPs fijas, pero se puede definir un rango lógico)
# mtproxy_trial_ips: [] (No aplica)

# Opcional: Logging
LOG_LEVEL=INFO

# Opcional: Directorio para archivos temporales o logs
# LOG_DIR=/var/log/usipipo
# TEMP_DIR=/tmp/usipipo

# Opcional: Configuración de Jobs/CRON
# CLEANUP_JOB_INTERVAL=24h # Intervalo para el job de limpieza de IPs revocadas (si se implementa como string)

# Opcional: Otros
# MAX_CONCURRENT_USERS=100
# DEFAULT_VPN_DURATION_DAYS=7 # Para trial
# DEFAULT_VPN_DURATION_PAID_MONTHS=1