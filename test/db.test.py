import asyncio
from infrastructure.persistence.supabase.supabase_client import get_supabase
from domain.entities.user import User, UserStatus
from infrastructure.persistence.supabase.user_repository import SupabaseUserRepository
from loguru import logger

async def test_connection():
    logger.info("🔍 Iniciando prueba de conexión con Supabase...")
    
    try:
        # 1. Probar Cliente Básico
        client = get_supabase()
        logger.success("✅ Cliente de Supabase inicializado.")

        # 2. Probar Repositorio e Inserción
        repo = SupabaseUserRepository()
        test_user = User(
            telegram_id=123456789,
            username="test_user",
            full_name="Usuario de Prueba",
            status=UserStatus.ACTIVE
        )
        
        logger.info("💾 Intentando insertar un usuario de prueba...")
        await repo.save(test_user)
        logger.success("✅ Escritura en base de datos exitosa.")

        # 3. Probar Lectura
        fetched_user = await repo.get_by_id(123456789)
        if fetched_user:
            logger.success(f"✅ Lectura exitosa: {fetched_user.full_name}")
        
        logger.info("🚀 Todas las pruebas de DB pasaron correctamente.")

    except Exception as e:
        logger.error(f"❌ Error en la prueba: {e}")
        logger.error("Revisa tu DATABASE_URL y las API Keys en el .env")

if __name__ == "__main__":
    asyncio.run(test_connection())
