from typing import List, Optional
import uuid
from datetime import datetime
from domain.entities.vpn_key import VpnKey, KeyType
from domain.interfaces.ikey_repository import IKeyRepository
from .supabase_client import get_supabase
from loguru import logger

class SupabaseKeyRepository(IKeyRepository):
    def __init__(self):
        self.client = get_supabase()
        self.table = "vpn_keys"

    async def save(self, key: VpnKey) -> VpnKey:
        key_data = {
            "user_id": key.user_id,
            "key_type": key.key_type,
            "name": key.name,
            "key_data": key.key_data,
            "external_id": key.external_id,
            "is_active": key.is_active,
            "data_limit_bytes": key.data_limit_bytes,
            "billing_reset_at": key.billing_reset_at.isoformat() if key.billing_reset_at else None,
            "used_bytes": key.used_bytes,
            "last_seen_at": key.last_seen_at.isoformat() if key.last_seen_at else None
        }
        if key.id: 
            key_data["id"] = str(key.id)

        try:
            response = self.client.table(self.table).upsert(key_data).execute()
            if response.data and not key.id:
                key.id = uuid.UUID(response.data[0]["id"])
            return key
        except Exception as e:
            logger.error(f"❌ Error al guardar llave: {e}")
            raise e

    async def get_by_user_id(self, telegram_id: int) -> List[VpnKey]:
        try:
            response = self.client.table(self.table).select("*").eq("user_id", telegram_id).eq("is_active", True).execute()
            return [VpnKey(**item) for item in response.data]
        except Exception as e:
            logger.error(f"❌ Error al listar llaves: {e}")
            return []

    async def get_by_user(self, telegram_id: int) -> List[VpnKey]:
        """Alias para get_by_user_id para compatibilidad."""
        return await self.get_by_user_id(telegram_id)

    async def get_all_active(self) -> List[VpnKey]:
        res = self.client.table(self.table).select("*").eq("is_active", True).execute()
        return [VpnKey(**item) for item in res.data]

    async def update_usage(self, key_id: uuid.UUID, used_bytes: int):
        self.client.table(self.table).update({"used_bytes": used_bytes}).eq("id", str(key_id)).execute()

    async def get_by_id(self, key_id: uuid.UUID) -> Optional[VpnKey]:
        res = self.client.table(self.table).select("*").eq("id", str(key_id)).maybe_single().execute()
        return VpnKey(**res.data) if res.data else None

    async def delete(self, key_id: uuid.UUID) -> bool:
        try:
            self.client.table(self.table).update({"is_active": False}).eq("id", str(key_id)).execute()
            return True
        except Exception as e:
            logger.error(f"Error al eliminar llave: {e}")
            return False
    
    async def update_data_limit(self, key_id: uuid.UUID, data_limit_bytes: int):
        try:
            self.client.table(self.table)\
                .update({"data_limit_bytes": data_limit_bytes})\
                .eq("id", str(key_id))\
                .execute()
            return True
        except Exception as e:
            logger.error(f"Error al actualizar límite de datos: {e}")
            return False
    
    async def reset_data_usage(self, key_id: uuid.UUID):
        try:
            now = datetime.now().isoformat()
            self.client.table(self.table)\
                .update({"used_bytes": 0, "billing_reset_at": now})\
                .eq("id", str(key_id))\
                .execute()
            return True
        except Exception as e:
            logger.error(f"Error al resetear uso de datos: {e}")
            return False
    
    async def get_keys_needing_reset(self) -> List[VpnKey]:
        try:
            from datetime import datetime, timedelta
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            
            response = self.client.table(self.table)\
                .select("*")\
                .lt("billing_reset_at", thirty_days_ago)\
                .eq("is_active", True)\
                .execute()
            
            return [VpnKey(**item) for item in response.data] if response.data else []
        except Exception as e:
            logger.error(f"Error al obtener llaves para reset: {e}")
            return []
