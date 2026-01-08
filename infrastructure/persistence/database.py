"""
Módulo de conexión a base de datos con SQLAlchemy Async.

Este módulo centraliza la conexión a PostgreSQL (Supabase) usando
SQLAlchemy 2.0 con soporte asíncrono completo.

Author: uSipipo Team
Version: 1.0.0
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text
from utils.logger import logger

from config import settings


# Variable global para el engine
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _build_async_database_url(url: str) -> str:
    """
    Convierte la URL de PostgreSQL a formato asyncpg.
    
    Maneja múltiples formatos:
    - postgres://... → postgresql+asyncpg://...
    - postgresql://... → postgresql+asyncpg://...
    - postgresql+psycopg2://... → postgresql+asyncpg://...
    
    Args:
        url: URL de base de datos original.
    
    Returns:
        URL convertida para asyncpg.
    """
    # Caso 1: postgres:// → postgresql+asyncpg://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    # Caso 2: postgresql+psycopg2:// → postgresql+asyncpg://
    elif url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    # Caso 3: postgresql:// (sin driver) → postgresql+asyncpg://
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    return url


def _configure_sqlalchemy_logging():
    """
    Configura SQLAlchemy para usar el logger personalizado en lugar de stdout.
    
    Redirige los logs de SQLAlchemy al sistema de logging personalizado.
    """
    # Obtener el logger de SQLAlchemy
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    
    # Remover handlers existentes para evitar duplicación
    for handler in sqlalchemy_logger.handlers[:]:
        sqlalchemy_logger.removeHandler(handler)
    
    # Configurar nivel de logging basado en el entorno
    if settings.is_development:
        sqlalchemy_logger.setLevel(logging.WARNING)  # Solo WARNING y ERROR en desarrollo
    else:
        sqlalchemy_logger.setLevel(logging.ERROR)  # Solo ERROR en producción
    
    # Crear un handler personalizado que redirija a nuestro logger
    class CustomSQLAlchemyHandler(logging.Handler):
        def emit(self, record):
            # Solo procesar WARNING y ERROR para reducir ruido
            if record.levelno < logging.WARNING:
                return
                
            # Mapear niveles de logging estándar a métodos de nuestro logger
            level_map = {
                logging.WARNING: logger.warning,
                logging.ERROR: logger.error,
                logging.CRITICAL: logger.critical
            }
            
            # Obtener el método de logging apropiado
            log_method = level_map.get(record.levelno, logger.warning)
            
            # Formatear el mensaje
            msg = self.format(record)
            
            # Simplificar mensaje para SQL queries
            if "SELECT" in msg or "INSERT" in msg or "UPDATE" in msg or "DELETE" in msg:
                # Extraer solo la operación principal, no los parámetros
                if "SELECT" in msg:
                    msg = "🔍 Consulta SELECT ejecutada"
                elif "INSERT" in msg:
                    msg = "➕ Registro INSERT ejecutado"
                elif "UPDATE" in msg:
                    msg = "✏️ Registro UPDATE ejecutado"
                elif "DELETE" in msg:
                    msg = "🗑️ Registro DELETE ejecutado"
            else:
                # Agregar prefijo para otros logs de SQLAlchemy
                msg = f"🗃️ SQL: {msg}"
            
            # Enviar al logger personalizado
            log_method(msg)
    
    # Configurar el handler
    handler = CustomSQLAlchemyHandler()
    handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    
    # Añadir el handler al logger de SQLAlchemy
    sqlalchemy_logger.addHandler(handler)
    
    logger.info("🔧 Configuración de logging de SQLAlchemy aplicada")


def get_engine() -> AsyncEngine:
    """
    Obtiene o crea el engine de SQLAlchemy (Singleton).
    
    Returns:
        AsyncEngine configurado para la base de datos.
    """
    global _engine
    
    if _engine is None:
        # Configurar logging de SQLAlchemy antes de crear el engine
        _configure_sqlalchemy_logging()
        
        database_url = _build_async_database_url(settings.DATABASE_URL)
        
        _engine = create_async_engine(
            database_url,
            echo=False,  # Desactivar echo ya que usamos nuestro propio logging
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=10,
            pool_timeout=settings.DB_TIMEOUT,
            pool_pre_ping=True,  # Verificar conexiones antes de usar
            # Para Supabase en producción, considera NullPool si hay problemas
            # poolclass=NullPool,
        )
        
        logger.info("🔌 Engine SQLAlchemy async creado exitosamente")
    
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Obtiene o crea el factory de sesiones (Singleton).
    
    Returns:
        Factory configurado para crear AsyncSessions.
    """
    global _session_factory
    
    if _session_factory is None:
        engine = get_engine()
        
        _session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Evitar lazy loading después de commit
            autocommit=False,
            autoflush=False,
        )
        
        logger.debug("📦 Session factory SQLAlchemy creado")
    
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Generador de sesiones para inyección de dependencias.
    
    Uso con FastAPI:
        @app.get("/users")
        async def get_users(session: AsyncSession = Depends(get_session)):
            ...
    
    Uso manual:
        async for session in get_session():
            result = await session.execute(query)
    
    Yields:
        AsyncSession configurada y lista para usar.
    """
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager para sesiones (uso en servicios y jobs).
    
    Uso:
        async with get_session_context() as session:
            result = await session.execute(query)
            await session.commit()
    
    Yields:
        AsyncSession con manejo automático de transacciones.
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database() -> None:
    """
    Inicializa la conexión a la base de datos.
    
    Llama esto al inicio de la aplicación para verificar
    que la conexión funciona correctamente.
    """
    try:
        engine = get_engine()
        
        # Verificar conexión
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        logger.info("✅ Conexión a PostgreSQL verificada correctamente")
        
    except Exception as e:
        logger.critical(f"❌ Error conectando a la base de datos: {e}")
        raise


async def close_database() -> None:
    """
    Cierra el engine y libera todas las conexiones.
    
    Llama esto al cerrar la aplicación.
    """
    global _engine, _session_factory
    
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("🔌 Conexión a base de datos cerrada")
