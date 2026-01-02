from typing import Optional
from domain.entities.user import User, UserStatus
from domain.interfaces.iuser_repository import IUserRepository
from .supabase_client import get_supabase
from loguru import logger

class SupabaseUserRepository(IUserRepository):
    """
    Implementación real del manejo de usuarios usando Supabase.
    """

    def __init__(self):
        # Obtenemos nuestra conexión central
        self.client = get_supabase()
        self.table = "users"

    async def get_by_id(self, telegram_id: int) -> Optional[User]:
        """Busca un usuario en la tabla 'users' de Supabase."""
        try:
            response = self.client.table(self.table)\
                .select("*")\
                .eq("telegram_id", telegram_id)\
                .maybe_single()\
                .execute()

            if response is None or not response.data:
                return None

            data = response.data
            return User(
                telegram_id=data["telegram_id"],
                username=data.get("username"),
                full_name=data.get("full_name"),
                status=UserStatus(data.get("status", "active")),
                max_keys=data.get("max_keys", 5)
            )
        except Exception as e:
            logger.error(f"❌ Error al obtener usuario {telegram_id}: {e}")
            return None

    async def save(self, user: User) -> User:
        """Guarda o actualiza los datos del usuario."""
        user_data = {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "full_name": user.full_name,
            "status": user.status,
            "max_keys": user.max_keys
        }
        
        try:
            # .upsert significa: "Si existe actualiza, si no existe inserta"
            self.client.table(self.table).upsert(user_data).execute()
            logger.info(f"💾 Usuario {user.telegram_id} guardado correctamente.")
            return user
        except Exception as e:
            logger.error(f"❌ Error al guardar usuario: {e}")
            raise e

    async def exists(self, telegram_id: int) -> bool:
        """Chequeo rápido de existencia."""
        response = self.client.table(self.table)\
            .select("telegram_id", count="exact")\
            .eq("telegram_id", telegram_id)\
            .execute()
        return (response.count or 0) > 0
