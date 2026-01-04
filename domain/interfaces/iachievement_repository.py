"""
Interfaces del repositorio de logros para el bot uSipipo.

Author: uSipipo Team
Version: 2.0.0
"""

from typing import Protocol, List, Optional, Dict
from domain.entities.achievement import Achievement, UserAchievement, UserStats, AchievementType


class IAchievementRepository(Protocol):
    """Interfaz del repositorio de logros (Protocol)."""
    
    async def get_all_achievements(self) -> List[Achievement]:
        """Obtiene todos los logros activos."""
        ...
    
    async def get_achievement_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """Obtiene un logro por su ID."""
        ...
    
    async def get_achievements_by_type(self, achievement_type: AchievementType) -> List[Achievement]:
        """Obtiene logros por tipo."""
        ...
    
    async def get_user_achievements(self, user_id: int) -> List[UserAchievement]:
        """Obtiene todos los logros de un usuario."""
        ...
    
    async def get_user_achievement(self, user_id: int, achievement_id: str) -> Optional[UserAchievement]:
        """Obtiene un logro específico de un usuario."""
        ...
    
    async def create_user_achievement(self, user_achievement: UserAchievement) -> UserAchievement:
        """Crea un nuevo registro de logro para usuario."""
        ...
    
    async def update_user_achievement(self, user_achievement: UserAchievement) -> UserAchievement:
        """Actualiza el progreso de un logro de usuario."""
        ...
    
    async def get_completed_achievements(self, user_id: int) -> List[UserAchievement]:
        """Obtiene logros completados por un usuario."""
        ...
    
    async def get_pending_rewards(self, user_id: int) -> List[UserAchievement]:
        """Obtiene logros completados con recompensas no reclamadas."""
        ...


class IUserStatsRepository(Protocol):
    """Interfaz del repositorio de estadísticas de usuarios (Protocol)."""
    
    async def get_user_stats(self, user_id: int) -> Optional[UserStats]:
        """Obtiene las estadísticas de un usuario."""
        ...
    
    async def create_user_stats(self, user_stats: UserStats) -> UserStats:
        """Crea estadísticas iniciales para un usuario."""
        ...
    
    async def update_user_stats(self, user_stats: UserStats) -> UserStats:
        """Actualiza las estadísticas de un usuario."""
        ...
    
    async def get_leaderboard_by_type(self, achievement_type: AchievementType, limit: int = 10) -> List[Dict]:
        """Obtiene ranking de usuarios por tipo de logro."""
        ...
    
    async def get_top_users_by_achievements(self, limit: int = 10) -> List[Dict]:
        """Obtiene usuarios con más logros completados."""
        ...
