"""
Interfaz del servicio de administración para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from domain.entities.vpn_key import VpnKey as Key

class IAdminService(ABC):
    """Interfaz del servicio de administración para gestión de usuarios y claves."""
    
    @abstractmethod
    async def get_all_users(self) -> List[Dict]:
        """Obtener lista de todos los usuarios registrados."""
        pass
    
    @abstractmethod
    async def get_user_keys(self, user_id: int) -> List[Key]:
        """Obtener todas las claves de un usuario específico."""
        pass
    
    @abstractmethod
    async def get_all_keys(self) -> List[Dict]:
        """Obtener todas las claves de todos los usuarios."""
        pass
    
    @abstractmethod
    async def delete_key_from_servers(self, key_id: str, key_type: str) -> bool:
        """Eliminar una clave de los servidores VPN (WireGuard y Outline)."""
        pass
    
    @abstractmethod
    async def delete_key_from_db(self, key_id: str) -> bool:
        """Eliminar una clave de la base de datos."""
        pass
    
    @abstractmethod
    async def delete_user_key_complete(self, key_id: str) -> Dict[str, bool]:
        """Eliminar completamente una clave (servidores + BD)."""
        pass
    
    @abstractmethod
    async def get_server_status(self) -> Dict[str, Dict]:
        """Obtener estado de los servidores VPN."""
        pass
    
    @abstractmethod
    async def get_key_usage_stats(self, key_id: str) -> Dict:
        """Obtener estadísticas de uso de una clave."""
        pass

    @abstractmethod
    async def get_dashboard_stats(self) -> Dict:
        """Genera estadísticas completas para el panel de control administrativo."""
        pass
