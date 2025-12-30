import punq
from functools import lru_cache

from config import settings

# Interfaces
from domain.interfaces.iuser_repository import IUserRepository
from domain.interfaces.ikey_repository import IKeyRepository

# Implementaciones de Infraestructura
from infrastructure.persistence.supabase.user_repository import UserRepository
from infrastructure.persistence.supabase.key_repository import KeyRepository
from infrastructure.api_clients.client_outline import OutlineClient
from infrastructure.api_clients.client_wireguard import WireGuardClient

from infrastructure.persistence.supabase.ticket_repository import TicketRepository
from application.services.support_service import SupportService

# Servicio de Aplicación
from application.services.vpn_service import VpnService

@lru_cache()
def get_container() -> punq.Container:
    """Configura y retorna el contenedor de dependencias (Singleton)."""
    container = punq.Container()

    # 1. Registrar Clientes de Infraestructura (Singletons)
    container.register(OutlineClient, scope=punq.Scope.singleton)
    container.register(WireGuardClient, scope=punq.Scope.singleton)

    # 2. Registrar Repositorios (Mapeo de Interfaz -> Implementación)
    # Esto permite que el Service pida 'IUserRepository' y reciba 'UserRepository'
    container.register(IUserRepository, UserRepository)
    container.register(IKeyRepository, KeyRepository)

    # 3. Registrar el Servicio Principal (VpnService)
    # Punq inyectará automáticamente los repositorios y clientes necesarios
    container.register(VpnService)
    
    container.register(TicketRepository, scope=punq.Scope.singleton)
    container.register(SupportService)

    return container
