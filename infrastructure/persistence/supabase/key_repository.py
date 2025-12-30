from typing import List, Optional
import uuid
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
            "is_active": key.is_active
        }
        if key.id: key_data["id"] = str(key.id)

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
        except Exception: return False
