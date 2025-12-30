import punq
from functools import lru_cache

from config import settings

# Interfaces
from domain.interfaces.iuser_repository import IUserRepository
from domain.interfaces.ikey_repository import IKeyRepository

# Implementaciones de Infraestructura (Nombres corregidos)
from infrastructure.persistence.supabase.user_repository import SupabaseUserRepository
from infrastructure.persistence.supabase.key_repository import SupabaseKeyRepository
from infrastructure.api_clients.client_outline import OutlineClient
from infrastructure.api_clients.client_wireguard import WireGuardClient

# Repositorios y Servicios adicionales
from infrastructure.persistence.supabase.ticket_repository import TicketRepository
from application.services.support_service import SupportService
from application.services.vpn_service import VpnService

@lru_cache()
def get_container() -> punq.Container:
    """Configura y retorna el contenedor de dependencias (Singleton)."""
    container = punq.Container()

    # 1. Registrar Clientes de Infraestructura (Singletons)
    container.register(OutlineClient, scope=punq.Scope.singleton)
    container.register(WireGuardClient, scope=punq.Scope.singleton)

    # 2. Registrar Repositorios (Mapeo de Interfaz -> Implementación Corregida)
    container.register(IUserRepository, SupabaseUserRepository)
    container.register(IKeyRepository, SupabaseKeyRepository)
    
    # Repositorios que no tienen interfaz (o registro directo)
    container.register(TicketRepository, scope=punq.Scope.singleton)

    # 3. Registrar Servicios de Aplicación
    container.register(VpnService)
    container.register(SupportService)

    return container
