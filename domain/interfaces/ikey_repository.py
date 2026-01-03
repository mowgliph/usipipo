from typing import Protocol, List, Optional
from domain.entities.vpn_key import VpnKey
import uuid

class IKeyRepository(Protocol):
    """
    Contrato para la persistencia de llaves VPN.
    Define cómo interactuamos con la tabla de llaves en la BD.
    """

    async def save(self, key: VpnKey) -> VpnKey:
        """Guarda una nueva llave o actualiza una existente."""
        ...

    async def get_by_user(self, telegram_id: int) -> List[VpnKey]:
        """Recupera todas las llaves que le pertenecen a un usuario."""
        ...

    async def get_by_user_id(self, telegram_id: int) -> List[VpnKey]:
        """Recupera todas las llaves que le pertenecen a un usuario (alias)."""
        ...

    async def get_by_id(self, key_id: str) -> Optional[VpnKey]:
        """Busca una llave específica por su ID interno."""
        ...

    async def get_by_id(self, key_id: uuid.UUID) -> Optional[VpnKey]:
        """Busca una llave específica por su ID interno (UUID)."""
        ...

    async def delete(self, key_id: str) -> bool:
        """Elimina una llave de la base de datos."""
        ...

    async def delete(self, key_id: uuid.UUID) -> bool:
        """Elimina una llave de la base de datos (UUID)."""
        ...

    async def get_all_active(self) -> List[VpnKey]:
        """Obtiene todas las llaves activas del sistema."""
        ...

    async def update_usage(self, key_id: uuid.UUID, used_bytes: int) -> bool:
        """Actualiza el uso de datos de una llave."""
        ...

    async def reset_data_usage(self, key_id: uuid.UUID) -> bool:
        """Resetea el uso de datos de una llave."""
        ...
