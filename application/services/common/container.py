"""
Contenedor de Inyección de Dependencias.

Este módulo configura todas las dependencias de la aplicación
usando el patrón de inyección de dependencias con punq.

Author: uSipipo Team
Version: 2.0.0
"""

import punq
from functools import lru_cache
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger

from config import settings

# Database
from infrastructure.persistence.database import get_session_factory

# Interfaces
from domain.interfaces.iuser_repository import IUserRepository
from domain.interfaces.ikey_repository import IKeyRepository
from domain.interfaces.itransaction_repository import ITransactionRepository
from domain.interfaces.iachievement_repository import IAchievementRepository, IUserStatsRepository

# Implementaciones de Repositorios
from infrastructure.persistence.supabase.user_repository import SupabaseUserRepository
from infrastructure.persistence.supabase.key_repository import SupabaseKeyRepository
from infrastructure.persistence.supabase.transaction_repository import SupabaseTransactionRepository
from infrastructure.persistence.supabase.achievement_repository import AchievementRepository, UserStatsRepository
from infrastructure.persistence.supabase.ticket_repository import TicketRepository
from infrastructure.persistence.supabase.task_repository import TaskRepository

# Clientes de Infraestructura
from infrastructure.api_clients.client_outline import OutlineClient
from infrastructure.api_clients.client_wireguard import WireGuardClient

# Servicios de Aplicación
from application.services.vpn_service import VpnService
from application.services.support_service import SupportService
from application.services.referral_service import ReferralService
from application.services.payment_service import PaymentService
from application.services.achievement_service import AchievementService
from application.services.admin_service import AdminService
from application.services.task_service import TaskService


class SessionManager:
    """
    Gestiona la creación de sesiones de base de datos.
    
    Esta clase permite obtener sesiones de forma lazy y
    compartir la misma sesión durante una operación.
    """
    
    def __init__(self):
        self._session: AsyncSession | None = None
        self._factory = get_session_factory()
    
    async def get_session(self) -> AsyncSession:
        """Obtiene o crea una sesión de base de datos."""
        if self._session is None or not self._session.is_active:
            self._session = self._factory()
        return self._session
    
    async def close(self):
        """Cierra la sesión actual si existe."""
        if self._session is not None:
            await self._session.close()
            self._session = None


@lru_cache()
def get_container() -> punq.Container:
    """
    Configura y retorna el contenedor de dependencias (Singleton).
    
    Returns:
        Container con todas las dependencias configuradas.
    """
    container = punq.Container()
    
    logger.debug("🔧 Configurando contenedor de dependencias...")

    # =========================================================================
    # 1. SESIÓN DE BASE DE DATOS
    # =========================================================================
    session_manager = SessionManager()
    container.register(SessionManager, instance=session_manager)
    
    # Factory para obtener sesiones
    session_factory = get_session_factory()
    container.register(AsyncSession, factory=lambda: session_factory())

    # =========================================================================
    # 2. CLIENTES DE INFRAESTRUCTURA VPN (Singletons)
    # =========================================================================
    container.register(OutlineClient, scope=punq.Scope.singleton)
    container.register(WireGuardClient, scope=punq.Scope.singleton)

    # =========================================================================
    # 3. REPOSITORIOS (Requieren AsyncSession)
    # =========================================================================
    
    # Registrar factories que crean repositorios con la sesión
    def create_user_repo() -> SupabaseUserRepository:
        session = session_factory()
        return SupabaseUserRepository(session)
    
    def create_key_repo() -> SupabaseKeyRepository:
        session = session_factory()
        return SupabaseKeyRepository(session)
    
    def create_transaction_repo() -> SupabaseTransactionRepository:
        session = session_factory()
        return SupabaseTransactionRepository(session)
    
    def create_achievement_repo() -> AchievementRepository:
        session = session_factory()
        return AchievementRepository(session)
    
    def create_user_stats_repo() -> UserStatsRepository:
        session = session_factory()
        return UserStatsRepository(session)
    
    def create_ticket_repo() -> TicketRepository:
        session = session_factory()
        return TicketRepository(session)
    
    def create_task_repo() -> TaskRepository:
        session = session_factory()
        return TaskRepository(session)
    
    container.register(IUserRepository, factory=create_user_repo)
    container.register(IKeyRepository, factory=create_key_repo)
    container.register(ITransactionRepository, factory=create_transaction_repo)
    container.register(IAchievementRepository, factory=create_achievement_repo)
    container.register(IUserStatsRepository, factory=create_user_stats_repo)
    container.register(TicketRepository, factory=create_ticket_repo)
    container.register(TaskRepository, factory=create_task_repo)

    # =========================================================================
    # 4. SERVICIOS DE APLICACIÓN
    # =========================================================================
    
    def create_vpn_service() -> VpnService:
        return VpnService(
            user_repo=create_user_repo(),
            key_repo=create_key_repo(),
            outline_client=container.resolve(OutlineClient),
            wireguard_client=container.resolve(WireGuardClient)
        )
    
    def create_support_service() -> SupportService:
        return SupportService(
            ticket_repo=create_ticket_repo()
        )
    
    def create_referral_service() -> ReferralService:
        return ReferralService(
            user_repo=create_user_repo()
        )
    
    def create_payment_service() -> PaymentService:
        return PaymentService(
            user_repo=create_user_repo(),
            transaction_repo=create_transaction_repo()
        )
    
    def create_achievement_service() -> AchievementService:
        return AchievementService(
            achievement_repository=create_achievement_repo(),
            user_stats_repository=create_user_stats_repo()
        )
    
    def create_admin_service() -> AdminService:
        return AdminService(
            key_repository=create_key_repo(),
            user_repository=create_user_repo(),
            payment_repository=create_transaction_repo()
        )
    
    def create_task_service() -> TaskService:
        return TaskService(
            task_repo=create_task_repo(),
            payment_service=create_payment_service()
        )
    
    container.register(VpnService, factory=create_vpn_service)
    container.register(SupportService, factory=create_support_service)
    container.register(ReferralService, factory=create_referral_service)
    container.register(PaymentService, factory=create_payment_service)
    container.register(AchievementService, factory=create_achievement_service)
    container.register(AdminService, factory=create_admin_service)
    container.register(TaskService, factory=create_task_service)

    logger.debug("✅ Contenedor de dependencias configurado")
    
    return container


def get_service(service_class):
    """
    Helper para obtener un servicio del contenedor.
    
    Args:
        service_class: Clase del servicio a resolver.
    
    Returns:
        Instancia del servicio configurado.
    """
    container = get_container()
    return container.resolve(service_class)
