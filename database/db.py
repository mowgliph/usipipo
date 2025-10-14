# database/db.py
from typing import AsyncGenerator, Optional
import os
import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger("usipipo")

# Configuración desde entorno
# DATABASE_ASYNC_URL debe usar el driver async de Python para MariaDB:
# - recomendado: mysql+asyncmy://user:pass@host:port/dbname
# - alternativa: mysql+aiomysql://user:pass@host:port/dbname
DATABASE_ASYNC_URL = os.getenv("DATABASE_ASYNC_URL")
DATABASE_SYNC_URL = os.getenv("DATABASE_SYNC_URL")  # opcional, usado para migraciones/CLI

# Parámetros por defecto y flags
POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "true").lower() in ("1", "true", "yes")
ECHO_SQL = os.getenv("DB_ECHO_SQL", "false").lower() in ("1", "true", "yes")
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_CLASS_ENV = os.getenv("DB_POOL_CLASS", "").strip().lower()  # "null" -> NullPool

# Base declarativa (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    pass

if not DATABASE_ASYNC_URL:
    logger.error("DATABASE_ASYNC_URL no está definido en el entorno.", extra={"user_id": None})
    raise RuntimeError("Missing DATABASE_ASYNC_URL")

# Connect args recomendados para MariaDB / MySQL drivers async
connect_args: dict = {
    "charset": os.getenv("DB_CHARSET", "utf8mb4"),
}

# Permitir timeout de lectura/escritura si el driver/connector lo soporta
read_timeout = os.getenv("DB_READ_TIMEOUT")
write_timeout = os.getenv("DB_WRITE_TIMEOUT")
if read_timeout:
    connect_args["read_timeout"] = int(read_timeout)
if write_timeout:
    connect_args["write_timeout"] = int(write_timeout)

# Pool kwargs configurables (usar NullPool en serverless/tests)
pool_kwargs: dict = {}
if POOL_CLASS_ENV == "null":
    pool_kwargs["poolclass"] = NullPool
else:
    pool_kwargs.update(
        {
            "pool_size": POOL_SIZE,
            "max_overflow": MAX_OVERFLOW,
            "pool_timeout": POOL_TIMEOUT,
            "pool_pre_ping": POOL_PRE_PING,
        }
    )

logger.info("Creando AsyncEngine (driver async recomendado: asyncmy/aiomysql).", extra={"user_id": None})

async_engine: AsyncEngine = create_async_engine(
    DATABASE_ASYNC_URL,
    echo=ECHO_SQL,
    future=True,
    connect_args=connect_args,
    **pool_kwargs,
)

# async_sessionmaker con comportamiento seguro para servicios
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Proveedor de sesiones asíncronas (usar con `async with`)
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager que provee una AsyncSession.
    Uso:
        async with get_session() as session:
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session

# Helper para inicializar esquema (solo dev / semi-prod; en prod usar Alembic)
async def init_db(create: bool = True) -> None:
    """
    Crea tablas definidas en Base.metadata si create=True.
    En producción usar Alembic para migraciones.
    """
    if not create:
        return
    async with async_engine.begin() as conn:
        logger.info("Inicializando esquema de la base de datos", extra={"user_id": None})
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Esquema inicializado", extra={"user_id": None})

# Utilidad opcional para obtener la URL sync (para herramientas que no soportan async)
def get_sync_database_url() -> Optional[str]:
    return DATABASE_SYNC_URL

__all__ = [
    "Base",
    "async_engine",
    "AsyncSessionLocal",
    "get_session",
    "init_db",
    "get_sync_database_url",
]