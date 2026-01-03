"""
Interfaz del servicio de juegos para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.game import GameSession, UserBalance, GameStats, GameType, GameResult

class IGameService(ABC):
    """Interfaz del servicio de juegos."""
    
    @abstractmethod
    async def get_user_balance(self, user_id: int) -> UserBalance:
        """Obtener balance de estrellas de un usuario."""
        pass
    
    @abstractmethod
    async def update_balance(self, user_id: int, stars: int) -> UserBalance:
        """Actualizar balance de estrellas de un usuario."""
        pass
    
    @abstractmethod
    async def get_game_stats(self, user_id: int) -> GameStats:
        """Obtener estadísticas de juegos de un usuario."""
        pass
    
    @abstractmethod
    async def can_play_today(self, user_id: int) -> bool:
        """Verificar si el usuario puede jugar hoy."""
        pass
    
    @abstractmethod
    async def can_win_this_week(self, user_id: int) -> bool:
        """Verificar si el usuario puede ganar esta semana."""
        pass
    
    @abstractmethod
    async def play_game(self, user_id: int, game_type: GameType) -> tuple[GameResult, int]:
        """Jugar un juego y retornar resultado y estrellas ganadas."""
        pass
    
    @abstractmethod
    async def get_recent_games(self, user_id: int, limit: int = 10) -> List[GameSession]:
        """Obtener juegos recientes de un usuario."""
        pass
    
    @abstractmethod
    async def use_stars_for_plan(self, user_id: int, plan_cost: int) -> bool:
        """Usar estrellas para comprar un plan."""
        pass
