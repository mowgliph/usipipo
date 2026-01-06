"""
Servicio de juegos Play and Earn para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

import random
from datetime import datetime, date
from typing import List, Optional, Dict

from domain.interfaces.igame_service import IGameService
from domain.entities.game import GameSession, UserBalance, GameStats, GameType, GameResult
from utils.logger import get_logger

class GameService(IGameService):
    """Implementación del servicio de juegos."""
    
    def __init__(self):
        self.bot_logger = get_logger()
        # Simulación de base de datos en memoria
        self._balances: Dict[int, UserBalance] = {}
        self._game_stats: Dict[int, GameStats] = {}
        self._game_sessions: List[GameSession] = []
        
        # Probabilidades de ganar según el juego
        self._win_probabilities = {
            GameType.BOWLING: 0.4,  # 40% de ganar
            GameType.DARTS: 0.35,   # 35% de ganar
            GameType.DICE: 0.45     # 45% de ganar
        }
    
    async def get_user_balance(self, user_id: int) -> UserBalance:
        """Obtener balance de estrellas de un usuario."""
        if user_id not in self._balances:
            self._balances[user_id] = UserBalance(user_id=user_id)
        return self._balances[user_id]
    
    async def update_balance(self, user_id: int, stars: int) -> UserBalance:
        """Actualizar balance de estrellas de un usuario."""
        balance = await self.get_user_balance(user_id)
        if stars > 0:
            balance.add_stars(stars)
            self.bot_logger.log_bot_event("INFO", f"User {user_id} earned {stars} stars")
        else:
            balance.deduct_stars(abs(stars))
            self.bot_logger.log_bot_event("INFO", f"User {user_id} spent {abs(stars)} stars")
        return balance
    
    async def get_game_stats(self, user_id: int) -> GameStats:
        """Obtener estadísticas de juegos de un usuario."""
        if user_id not in self._game_stats:
            self._game_stats[user_id] = GameStats(user_id=user_id)
        return self._game_stats[user_id]
    
    async def can_play_today(self, user_id: int) -> bool:
        """Verificar si el usuario puede jugar hoy."""
        stats = await self.get_game_stats(user_id)
        return stats.can_play_today()
    
    async def can_win_this_week(self, user_id: int) -> bool:
        """Verificar si el usuario puede ganar esta semana."""
        stats = await self.get_game_stats(user_id)
        return stats.can_win_this_week()
    
    async def play_game(self, user_id: int, game_type: GameType) -> tuple[GameResult, int]:
        """Jugar un juego y retornar resultado y estrellas ganadas."""
        # Verificar si puede jugar hoy
        if not await self.can_play_today(user_id):
            raise ValueError("Ya has jugado hoy. Vuelve mañana!")
        
        # Obtener estadísticas
        stats = await self.get_game_stats(user_id)
        
        # Determinar resultado basado en probabilidades y límite semanal
        can_win = await self.can_win_this_week(user_id)
        win_probability = self._win_probabilities[game_type]
        
        if can_win and random.random() < win_probability:
            # Gana
            result = GameResult.WIN
            stars_earned = 1  # 1 estrella por victoria
        else:
            # Pierde
            result = GameResult.LOSE
            stars_earned = 0
        
        # Crear sesión de juego
        session = GameSession(
            user_id=user_id,
            game_type=game_type,
            result=result,
            played_at=datetime.now(),
            reward_earned=stars_earned
        )
        
        # Guardar sesión
        self._game_sessions.append(session)
        
        # Actualizar estadísticas
        stats.record_game(result)
        
        # Actualizar balance si ganó
        if result == GameResult.WIN:
            await self.update_balance(user_id, stars_earned)
        
        # Log del evento
        self.bot_logger.log_bot_event(
            "INFO",
            f"Game played: User {user_id}, Type {game_type.value}, Result {result.value}, Stars {stars_earned}"
        )
        
        return result, stars_earned
    
    async def get_recent_games(self, user_id: int, limit: int = 10) -> List[GameSession]:
        """Obtener juegos recientes de un usuario."""
        user_games = [session for session in self._game_sessions if session.user_id == user_id]
        user_games.sort(key=lambda x: x.played_at, reverse=True)
        return user_games[:limit]
    
    async def use_stars_for_plan(self, user_id: int, plan_cost: int) -> bool:
        """Usar estrellas para comprar un plan."""
        try:
            balance = await self.get_user_balance(user_id)
            balance.deduct_stars(plan_cost)
            self.bot_logger.log_bot_event("INFO", f"User {user_id} used {plan_cost} stars for plan")
            return True
        except ValueError:
            return False
    
    def _cleanup_old_sessions(self) -> None:
        """Limpiar sesiones antiguas (mantener solo último mes)."""
        cutoff_date = datetime.now().replace(day=1)  # Primer día del mes actual
        self._game_sessions = [
            session for session in self._game_sessions 
            if session.played_at >= cutoff_date
        ]
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Obtener tabla de líderes por estrellas."""
        sorted_balances = sorted(
            self._balances.values(), 
            key=lambda x: x.stars_balance, 
            reverse=True
        )
        
        return [
            {
                'user_id': balance.user_id,
                'stars_balance': balance.stars_balance,
                'last_updated': balance.last_updated
            }
            for balance in sorted_balances[:limit]
        ]
