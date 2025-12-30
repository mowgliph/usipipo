from typing import List, Optional, Dict
import uuid
from loguru import logger

from domain.entities.user import User
from domain.entities.vpn_key import VpnKey
from domain.interfaces.iuser_repository import IUserRepository
from domain.interfaces.ikey_repository import IKeyRepository
from infrastructure.api_clients.client_outline import OutlineClient
from infrastructure.api_clients.client_wireguard import WireGuardClient

class VpnService:
    def __init__(
        self,
        user_repo: IUserRepository,
        key_repo: IKeyRepository,
        outline_client: OutlineClient,
        wireguard_client: WireGuardClient
    ):
        self.user_repo = user_repo
        self.key_repo = key_repo
        self.outline_client = outline_client
        self.wireguard_client = wireguard_client

    async def create_key(self, telegram_id: int, key_type: str, key_name: str) -> VpnKey:
        """Orquesta la creación de una llave VPN."""
        user = await self.user_repo.get_by_id(telegram_id)
        if not user:
            user = User(telegram_id=telegram_id)
            await self.user_repo.save(user)

        existing_keys = await self.key_repo.get_by_user_id(telegram_id)
        if len(existing_keys) >= user.max_keys:
            raise Exception(f"Límite de llaves alcanzado ({user.max_keys})")

        if key_type.lower() == "outline":
            infra_data = await self.outline_client.create_key(name=key_name)
            external_id = str(infra_data["id"])
            access_data = infra_data["accessUrl"]
        elif key_type.lower() == "wireguard":
            infra_data = await self.wireguard_client.create_peer(user_id=telegram_id, name=key_name)
            external_id = infra_data["id"] 
            access_data = infra_data["config"]
        else:
            raise ValueError(f"Tipo de VPN no soportado: {key_type}")

        new_key = VpnKey(
            id=uuid.uuid4(),
            user_id=telegram_id,
            key_type=key_type,
            name=key_name,
            key_data=access_data,
            external_id=external_id
        )
        
        await self.key_repo.save(new_key)
        return new_key

    async def get_all_active_keys(self) -> List[VpnKey]:
        """
        Recupera todas las llaves activas de la base de datos para la sincronización.
        """
        return await self.key_repo.get_all_active()

    async def fetch_real_usage(self, key: VpnKey) -> int:
        """
        Consulta el consumo de datos (en bytes) directamente a las APIs de los servidores.
        """
        try:
            if key.key_type == "outline":
                # Consultar uso a Outline (devuelve el uso total de todas las llaves)
                usage_data = await self.outline_client.get_metrics()
                return usage_data.get(str(key.external_id), 0)
            
            elif key.key_type == "wireguard":
                # Consultar uso a WireGuard para el peer específico
                peer_data = await self.wireguard_client.get_peer_metrics(key.external_id)
                return peer_data.get("transfer_total", 0)
            
            return 0
        except Exception as e:
            logger.error(f"Error consultando métricas para llave {key.id}: {e}")
            return 0

    async def update_key_usage(self, key_id: uuid.UUID, used_bytes: int):
        """
        Persiste el consumo actualizado en la base de datos local.
        """
        await self.key_repo.update_usage(key_id, used_bytes)

    async def get_user_status(self, telegram_id: int) -> dict:
        """Obtiene un resumen del estado del usuario y sus llaves."""
        user = await self.user_repo.get_by_id(telegram_id)
        keys = await self.key_repo.get_by_user_id(telegram_id)
        
        return {
            "user": user,
            "keys": keys
        }

    async def revoke_key(self, key_id: uuid.UUID) -> bool:
        """Elimina una llave de la infraestructura y de la BD."""
        key = await self.key_repo.get_by_id(key_id)
        if not key:
            return False

        if key.key_type == "outline":
            await self.outline_client.delete_key(key.external_id)
        elif key.key_type == "wireguard":
            client_name = f"tg_{key.user_id}"
            await self.wireguard_client.delete_peer(key.external_id, client_name)

        return await self.key_repo.delete(key_id)
