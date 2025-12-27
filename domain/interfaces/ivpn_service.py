from typing import Protocol
from domain.entities.vpn_key import VpnKey

class IVpnService(Protocol):
    """
    Contrato para los adaptadores de servidores VPN.
    Define qué debe hacer el código que habla con Outline o WireGuard.
    """

    async def create_key(self, name: str) -> VpnKey:
        """
        Ordena al servidor VPN crear una nueva conexión.
        Debe devolver un objeto VpnKey con los datos técnicos (config/URL).
        """
        ...

    async def delete_key(self, external_id: str) -> bool:
        """
        Ordena al servidor VPN que borre/revoque una llave específica.
        """
        ...
