"""
Test de conexión a base de datos con SQLAlchemy Async.

Este script verifica que la conexión a PostgreSQL (Supabase) funciona correctamente.

Author: uSipipo Team
Version: 2.0.0
"""

import asyncio
from utils.logger import logger

from infrastructure.persistence.database import init_database, close_database, get_session_context
from infrastructure.persistence.supabase.models import UserModel
from infrastructure.persistence.supabase.user_repository import SupabaseUserRepository
from domain.entities.user import User, UserStatus
from sqlalchemy import select


async def test_connection():
    """Prueba la conexión a la base de datos."""
    logger.info("🔍 Iniciando prueba de conexión a PostgreSQL (Supabase)...")
    
    try:
        # 1. Inicializar base de datos
        logger.info("🔌 Inicializando conexión...")
        await init_database()
        logger.success("✅ Conexión a base de datos verificada.")

        # 2. Probar escritura con repositorio
        async with get_session_context() as session:
            repo = SupabaseUserRepository(session)
            
            test_user = User(
                telegram_id=123456789,
                username="test_user",
                full_name="Usuario de Prueba",
                status=UserStatus.ACTIVE
            )
            
            logger.info("💾 Intentando insertar un usuario de prueba...")
            await repo.save(test_user)
            logger.success("✅ Escritura en base de datos exitosa.")

            # 3. Probar lectura
            fetched_user = await repo.get_by_id(123456789)
            if fetched_user:
                logger.success(f"✅ Lectura exitosa: {fetched_user.full_name}")
            else:
                logger.warning("⚠️ Usuario no encontrado después de insertar")
        
        logger.info("🚀 Todas las pruebas de BD pasaron correctamente.")

    except Exception as e:
        logger.error(f"❌ Error en la prueba: {e}")
        logger.error("Revisa tu DATABASE_URL y las credenciales en el .env")
        import traceback
        traceback.print_exc()
    
    finally:
        # 4. Cerrar conexión
        await close_database()
        logger.info("🔌 Conexión cerrada.")


if __name__ == "__main__":
    asyncio.run(test_connection())
