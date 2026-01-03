from typing import List, Optional, Dict
import uuid
from datetime import datetime, timedelta
from loguru import logger

from domain.entities.user import User
from domain.entities.vpn_key import VpnKey
from domain.interfaces.iuser_repository import IUserRepository
from domain.interfaces.ikey_repository import IKeyRepository
from infrastructure.api_clients.client_outline import OutlineClient
from infrastructure.api_clients.client_wireguard import WireGuardClient
from config import settings

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
            infra_data = await self.outline_client.create_key(key_name)
            access_data = infra_data["access_url"]
            external_id = infra_data["id"]
        elif key_type.lower() == "wireguard":
            infra_data = await self.wireguard_client.create_peer(telegram_id, key_name)
            access_data = infra_data["config"]
            # create_peer devuelve 'client_name' en su diccionario de respuesta
            external_id = infra_data["client_name"] 
        else:
            raise ValueError("Tipo de llave no soportado")

        # Determinar límite de datos según plan
        data_limit_bytes = self._get_user_data_limit(user)
        
        new_key = VpnKey(
            id=uuid.uuid4(),
            user_id=telegram_id,
            key_type=key_type.lower(),
            name=key_name,
            key_data=access_data,
            external_id=external_id,
            data_limit_bytes=data_limit_bytes,
            billing_reset_at=datetime.now()
        )
        
        await self.key_repo.save(new_key)
        logger.info(f"🔑 Llave {key_type} creada para el usuario {telegram_id}")
        return new_key

    async def get_all_active_keys(self) -> List[VpnKey]:
        """Obtiene todas las llaves activas de todos los usuarios para sincronizar."""
        return await self.key_repo.get_all_active()
    
    async def fetch_real_usage(self, key: VpnKey) -> int:
        """Abstrae la consulta de consumo según el tipo de llave."""
        try:
            if key.key_type == "outline":
                metrics = await self.outline_client.get_metrics()
                return metrics.get(str(key.external_id), 0)
            
            elif key.key_type == "wireguard":
                peer_data = await self.wireguard_client.get_peer_metrics(key.external_id)
                return peer_data.get("transfer_total", 0)
            
            return 0
        except Exception as e:
            logger.error(f"Error consultando métricas reales para llave {key.id}: {e}")
            return 0

    async def update_key_usage(self, key_id: uuid.UUID, used_bytes: int):
        """Persiste el consumo actualizado en la base de datos."""
        await self.key_repo.update_usage(key_id, used_bytes)

    def _get_user_data_limit(self, user: User) -> int:
        """Retorna el límite de datos en bytes según el plan del usuario."""
        if user.is_vip_active():
            return settings.VIP_PLAN_DATA_LIMIT_GB * (1024**3)
        else:
            return settings.FREE_PLAN_DATA_LIMIT_GB * (1024**3)

    async def can_user_create_key(self, user: User) -> tuple[bool, str]:
        """Verifica si el usuario puede crear una nueva llave."""
        keys = await self.key_repo.get_by_user_id(user.telegram_id)
        if len(keys) >= user.max_keys:
            return False, f"Has alcanzado el límite de {user.max_keys} llaves."
        
        return True, ""

    async def get_user_status(self, telegram_id: int) -> dict:
        """Obtiene un resumen del estado del usuario y sus llaves."""
        user = await self.user_repo.get_by_id(telegram_id)
        keys = await self.key_repo.get_by_user_id(telegram_id)
        
        # Calcular consumo total
        total_used_bytes = sum(k.used_bytes for k in keys)
        total_data_limit = sum(k.data_limit_bytes for k in keys)
        
        return {
            "user": user,
            "keys_count": len(keys),
            "keys": keys,
            "total_used_gb": total_used_bytes / (1024**3),
            "total_limit_gb": total_data_limit / (1024**3),
            "remaining_gb": max(0, total_data_limit - total_used_bytes) / (1024**3)
        }

    async def check_and_reset_billing_cycle(self, key: VpnKey) -> bool:
        """Verifica si el ciclo de facturación debe resetearse y lo hace si es necesario."""
        if key.needs_reset():
            await self.key_repo.reset_data_usage(key.id)
            return True
        return False

    async def get_user_keys(self, telegram_id: int) -> List[VpnKey]:
      """Obtiene todas las llaves activas de un usuario."""
      return await self.key_repo.get_by_user_id(telegram_id)

    async def revoke_key(self, key_id: uuid.UUID) -> bool:
        """Elimina una llave de la infraestructura y la marca como inactiva en BD."""
        key = await self.key_repo.get_by_id(key_id)
        if not key:
            logger.warning(f"Intentando revocar llave inexistente: {key_id}")
            return False

        # Verificar si el usuario puede eliminar (ha depositado)
        user = await self.user_repo.get_by_id(key.user_id)
        if not user.can_delete_keys():
            raise Exception("Debes realizar al menos un depósito para eliminar claves.")

        try:
            # 1. Eliminar de la infraestructura real
            if key.key_type == "outline":
                await self.outline_client.delete_key(key.external_id)
            elif key.key_type == "wireguard":
                await self.wireguard_client.delete_client(key.external_id)

            # 2. Marcar como inactiva en Repositorio (Soft Delete)
            return await self.key_repo.delete(key_id)
            
        except Exception as e:
            logger.error(f"❌ Error al revocar llave {key_id}: {e}")
            return False

    async def upgrade_to_vip(self, user: User, months: int = 1) -> bool:
        """Actualiza un usuario a VIP por la cantidad de meses especificada."""
        if user.is_vip_active():
            # Extender la fecha de expiración
            new_expiry = user.vip_expires_at + timedelta(days=30*months)
        else:
            new_expiry = datetime.now() + timedelta(days=30*months)

        user.is_vip = True
        user.vip_expires_at = new_expiry
        user.max_keys = settings.VIP_PLAN_MAX_KEYS

        # Actualizar límites de datos de las llaves existentes
        keys = await self.key_repo.get_by_user_id(user.telegram_id)
        for key in keys:
            key.data_limit_bytes = settings.VIP_PLAN_DATA_LIMIT_GB * (1024**3)
            await self.key_repo.save(key)

        await self.user_repo.save(user)
        return True

    async def deactivate_inactive_key(self, key_id: uuid.UUID) -> bool:
        """Desactiva una llave por inactividad (soft delete)."""
        try:
            key = await self.key_repo.get_by_id(key_id)
            if not key:
                return False
            key.is_active = False
            await self.key_repo.save(key)
            return True
        except Exception as e:
            logger.error(f"Error al desactivar llave {key_id}: {e}")
            return False
