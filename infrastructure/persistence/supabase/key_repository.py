from typing import List, Optional
from domain.entities.vpn_key import VpnKey, KeyType
from domain.interfaces.ikey_repository import IKeyRepository
from .supabase_client import get_supabase
from loguru import logger

class SupabaseKeyRepository(IKeyRepository):
    """Maneja las operaciones de las llaves VPN en Supabase."""

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
        
        # Si la llave ya tiene un ID, lo incluimos para que se actualice
        if key.id:
            key_data["id"] = key.id

        try:
            response = self.client.table(self.table).upsert(key_data).execute()
            # Actualizamos el objeto con el ID generado por la BD si es nueva
            if response.data:
                key.id = response.data[0]["id"]
            logger.info(f"🔑 Llave '{key.name}' guardada en BD.")
            return key
        except Exception as e:
            logger.error(f"❌ Error al guardar llave: {e}")
            raise e

    async def get_by_user(self, telegram_id: int) -> List[VpnKey]:
        try:
            response = self.client.table(self.table)\
                .select("*")\
                .eq("user_id", telegram_id)\
                .eq("is_active", True)\
                .execute()
            
            keys = []
            for item in response.data:
                keys.append(VpnKey(
                    id=item["id"],
                    user_id=item["user_id"],
                    key_type=KeyType(item["key_type"]),
                    name=item["name"],
                    key_data=item["key_data"],
                    external_id=item["external_id"],
                    is_active=item["is_active"]
                ))
            return keys
        except Exception as e:
            logger.error(f"❌ Error al listar llaves de {telegram_id}: {e}")
            return []

    async def delete(self, key_id: str) -> bool:
        try:
            # En lugar de borrar físicamente, la marcamos como inactiva (Soft Delete)
            self.client.table(self.table)\
                .update({"is_active": False})\
                .eq("id", key_id)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"❌ Error al desactivar llave {key_id}: {e}")
            return False
