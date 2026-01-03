"""
Interfaz del servicio de logros para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from domain.entities.achievement import Achievement, UserAchievement, UserStats, AchievementType

class IAchievementService(ABC):
    """Interfaz del servicio de logros."""
    
    @abstractmethod
    async def initialize_user_achievements(self, user_id: int) -> None:
        """Inicializa todos los logros para un nuevo usuario."""
        pass
    
    @abstractmethod
    async def update_user_stats(self, user_id: int, stats_update: Dict) -> None:
        """Actualiza las estadísticas de un usuario y verifica logros."""
        pass
    
    @abstractmethod
    async def check_and_update_achievements(self, user_id: int, achievement_type: AchievementType, new_value: int) -> List[Achievement]:
        """Verifica y actualiza logros basados en un nuevo valor."""
        pass
    
    @abstractmethod
    async def claim_achievement_reward(self, user_id: int, achievement_id: str) -> bool:
        """Reclama la recompensa de un logro completado."""
        pass
    
    @abstractmethod
    async def get_user_achievements_progress(self, user_id: int) -> Dict[str, UserAchievement]:
        """Obtiene el progreso de todos los logros de un usuario."""
        pass
    
    @abstractmethod
    async def get_user_completed_achievements(self, user_id: int) -> List[UserAchievement]:
        """Obtiene los logros completados de un usuario."""
        pass
    
    @abstractmethod
    async def get_user_pending_rewards(self, user_id: int) -> List[UserAchievement]:
        """Obtiene las recompensas pendientes de un usuario."""
        pass
    
    @abstractmethod
    async def get_achievement_leaderboard(self, achievement_type: AchievementType, limit: int = 10) -> List[Dict]:
        """Obtiene el ranking de usuarios para un tipo de logro."""
        pass
    
    @abstractmethod
    async def get_user_summary(self, user_id: int) -> Dict:
        """Obtiene un resumen completo de logros del usuario."""
        pass
    
    @abstractmethod
    async def get_next_achievements(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Obtiene los próximos logros que el usuario puede completar."""
        pass
