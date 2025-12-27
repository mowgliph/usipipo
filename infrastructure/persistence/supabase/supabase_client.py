from supabase import create_client, Client
from config import settings
from loguru import logger

# Variable global para guardar la conexión una vez creada
_supabase_instance: Client = None

def get_supabase() -> Client:
    """
    Crea y devuelve una única instancia del cliente de Supabase.
    Si ya existe una conexión, la reutiliza.
    """
    global _supabase_instance
    
    if _supabase_instance is None:
        try:
            # Usamos las variables que definimos en nuestro config.py
            _supabase_instance = create_client(
                settings.SUPABASE_URL, 
                settings.SUPABASE_SERVICE_KEY
            )
            logger.info("🔌 Conexión establecida con Supabase con éxito.")
        except Exception as e:
            logger.error(f"❌ Error al conectar con Supabase: {e}")
            raise e
            
    return _supabase_instance
