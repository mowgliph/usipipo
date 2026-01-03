"""
Interfaces del repositorio de logros para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from domain.entities.achievement import Achievement, UserAchievement, UserStats, AchievementType

class IAchievementRepository(ABC):
    """Interfaz del repositorio de logros."""
    
    @abstractmethod
    async def get_all_achievements(self) -> List[Achievement]:
        """Obtiene todos los logros activos."""
        pass
    
    @abstractmethod
    async def get_achievement_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """Obtiene un logro por su ID."""
        pass
    
    @abstractmethod
    async def get_achievements_by_type(self, achievement_type: AchievementType) -> List[Achievement]:
        """Obtiene logros por tipo."""
        pass
    
    @abstractmethod
    async def get_user_achievements(self, user_id: int) -> List[UserAchievement]:
        """Obtiene todos los logros de un usuario."""
        pass
    
    @abstractmethod
    async def get_user_achievement(self, user_id: int, achievement_id: str) -> Optional[UserAchievement]:
        """Obtiene un logro específico de un usuario."""
        pass
    
    @abstractmethod
    async def create_user_achievement(self, user_achievement: UserAchievement) -> UserAchievement:
        """Crea un nuevo registro de logro para usuario."""
        pass
    
    @abstractmethod
    async def update_user_achievement(self, user_achievement: UserAchievement) -> UserAchievement:
        """Actualiza el progreso de un logro de usuario."""
        pass
    
    @abstractmethod
    async def get_completed_achievements(self, user_id: int) -> List[UserAchievement]:
        """Obtiene logros completados por un usuario."""
        pass
    
    @abstractmethod
    async def get_pending_rewards(self, user_id: int) -> List[UserAchievement]:
        """Obtiene logros completados con recompensas no reclamadas."""
        pass

class IUserStatsRepository(ABC):
    """Interfaz del repositorio de estadísticas de usuarios."""
    
    @abstractmethod
    async def get_user_stats(self, user_id: int) -> Optional[UserStats]:
        """Obtiene las estadísticas de un usuario."""
        pass
    
    @abstractmethod
    async def create_user_stats(self, user_stats: UserStats) -> UserStats:
        """Crea estadísticas iniciales para un usuario."""
        pass
    
    @abstractmethod
    async def update_user_stats(self, user_stats: UserStats) -> UserStats:
        """Actualiza las estadísticas de un usuario."""
        pass
    
    @abstractmethod
    async def get_leaderboard_by_type(self, achievement_type: AchievementType, limit: int = 10) -> List[Dict]:
        """Obtiene ranking de usuarios por tipo de logro."""
        pass
    
    @abstractmethod
    async def get_top_users_by_achievements(self, limit: int = 10) -> List[Dict]:
        """Obtiene usuarios con más logros completados."""
        pass
