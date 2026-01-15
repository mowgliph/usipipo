from typing import Protocol, List, Optional
from domain.entities.vpn_key import VpnKey
import uuid

class IKeyRepository(Protocol):
    """
    Contrato para la persistencia de llaves VPN.
    Define cómo interactuamos con la tabla de llaves en la BD.
    """

    async def save(self, key: VpnKey, current_user_id: int) -> VpnKey:
        """Guarda una nueva llave o actualiza una existente."""
        ...

    async def get_by_user(self, telegram_id: int, current_user_id: int) -> List[VpnKey]:
        """Recupera todas las llaves que le pertenecen a un usuario."""
        ...

    async def get_by_user_id(self, telegram_id: int, current_user_id: int) -> List[VpnKey]:
        """Recupera todas las llaves que le pertenecen a un usuario (alias)."""
        ...

    async def get_by_id(self, key_id: uuid.UUID, current_user_id: int) -> Optional[VpnKey]:
        """Busca una llave específica por su ID interno (UUID)."""
        ...

    async def delete(self, key_id: uuid.UUID, current_user_id: int) -> bool:
        """Elimina una llave de la base de datos (UUID)."""
        ...

    async def get_all_active(self, current_user_id: int) -> List[VpnKey]:
        """Obtiene todas las llaves activas del sistema."""
        ...

    async def get_all_keys(self, current_user_id: int) -> List[VpnKey]:
        """Obtiene todas las llaves del sistema (activas e inactivas)."""
        ...

    async def update_usage(self, key_id: uuid.UUID, used_bytes: int, current_user_id: int) -> bool:
        """Actualiza el uso de datos de una llave."""
        ...

    async def reset_data_usage(self, key_id: uuid.UUID, current_user_id: int) -> bool:
        """Resetea el uso de datos de una llave."""
        ...

    async def update_data_limit(self, key_id: uuid.UUID, data_limit_bytes: int, current_user_id: int) -> bool:
        """Actualiza el límite de datos de una llave."""
        ...

    async def get_keys_needing_reset(self, current_user_id: int) -> List[VpnKey]:
        """Obtiene llaves que necesitan reset de ciclo de facturación."""
        ...
