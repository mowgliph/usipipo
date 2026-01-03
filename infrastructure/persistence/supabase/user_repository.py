from typing import Optional, List
from datetime import datetime
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
                max_keys=data.get("max_keys", 2),
                balance_stars=data.get("balance_stars", 0),
                total_deposited=data.get("total_deposited", 0),
                referral_code=data.get("referral_code"),
                referred_by=data.get("referred_by"),
                total_referral_earnings=data.get("total_referral_earnings", 0),
                is_vip=data.get("is_vip", False),
                vip_expires_at=data.get("vip_expires_at")
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
            "max_keys": user.max_keys,
            "balance_stars": user.balance_stars,
            "total_deposited": user.total_deposited,
            "referral_code": user.referral_code,
            "referred_by": user.referred_by,
            "total_referral_earnings": user.total_referral_earnings,
            "is_vip": user.is_vip,
            "vip_expires_at": user.vip_expires_at
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
    
    async def get_by_referral_code(self, referral_code: str) -> Optional[User]:
        """Busca un usuario por su código de referido único."""
        try:
            response = self.client.table(self.table)\
                .select("*")\
                .eq("referral_code", referral_code)\
                .maybe_single()\
                .execute()
            
            if not response.data:
                return None
            
            data = response.data
            return User(
                telegram_id=data["telegram_id"],
                username=data.get("username"),
                full_name=data.get("full_name"),
                status=UserStatus(data.get("status", "active")),
                max_keys=data.get("max_keys", 2),
                balance_stars=data.get("balance_stars", 0),
                total_deposited=data.get("total_deposited", 0),
                referral_code=data.get("referral_code"),
                referred_by=data.get("referred_by"),
                total_referral_earnings=data.get("total_referral_earnings", 0),
                is_vip=data.get("is_vip", False),
                vip_expires_at=data.get("vip_expires_at")
            )
        except Exception as e:
            logger.error(f"❌ Error al buscar por referral_code {referral_code}: {e}")
            return None
    
    async def update_balance(self, telegram_id: int, new_balance: int) -> bool:
        """Actualiza el balance de estrellas del usuario."""
        try:
            self.client.table(self.table)\
                .update({"balance_stars": new_balance})\
                .eq("telegram_id", telegram_id)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"❌ Error al actualizar balance: {e}")
            return False
    
    async def get_referrals(self, referrer_id: int) -> list:
        """Obtiene todos los usuarios referidos por este usuario."""
        try:
            response = self.client.table(self.table)\
                .select("*")\
                .eq("referred_by", referrer_id)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Error al obtener referidos: {e}")
            return []
