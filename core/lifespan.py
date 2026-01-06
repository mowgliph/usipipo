"""
Gestión del ciclo de vida de la aplicación FastAPI.
Maneja eventos de inicio y apagado de forma segura.
"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from utils.logger import logger
from config import settings
from infrastructure.persistence.database import close_database

# Configuración inicial de Loguru
logger.remove() # Quitar handler por defecto
logger.add(
    sys.stderr, 
    level=settings.LOG_LEVEL.upper(),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)
# Opcional: Log a archivo
# logger.add("logs/vpn_manager.log", rotation="10 MB", level="INFO")

def _setup_directories():
    """Crea los directorios necesarios definidos en config."""
    paths = [
        settings.TEMP_PATH,
        settings.QR_CODE_PATH,
        settings.CLIENT_CONFIGS_PATH
    ]
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            logger.info(f"📁 Directorio creado: {path}")

def _cleanup_temp():
    """Limpia archivos temporales al apagar."""
    if os.path.exists(settings.TEMP_PATH):
        try:
            for f in os.listdir(settings.TEMP_PATH):
                fp = os.path.join(settings.TEMP_PATH, f)
                if os.path.isfile(fp):
                    os.unlink(fp)
            logger.info("🧹 Archivos temporales limpiados.")
        except Exception as e:
            logger.error(f"Error limpiando temp: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ================= STARTUP =================
    logger.info(f"🚀 Iniciando {settings.PROJECT_NAME} en entorno {settings.APP_ENV}")
    
    _setup_directories()
    
    # Aquí inicializaremos el contenedor (Fase 6)
    # from core.container import container
    # container.wire(modules=[...])
    
    # Aquí verificamos conexiones (Fase 3 y 4)
    if not settings.SUPABASE_URL:
        logger.warning("⚠️ Supabase URL no configurada.")
    
    logger.success("✅ Sistema listo para recibir peticiones.")
    
    yield # La app corre aquí
    
    # ================= SHUTDOWN =================
    logger.info("🛑 Apagando sistema...")
    
    await close_database()
    _cleanup_temp()
    
    logger.info("👋 Hasta luego.")
