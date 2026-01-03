"""
Entidades del sistema de juegos y balance para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from datetime import datetime, date
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

class GameType(Enum):
    """Tipos de juegos disponibles."""
    BOWLING = "bowling"
    DARTS = "darts"
    DICE = "dice"

class GameResult(Enum):
    """Resultados posibles de un juego."""
    WIN = "win"
    LOSE = "lose"

@dataclass
class GameSession:
    """Sesión de juego de un usuario."""
    user_id: int
    game_type: GameType
    result: GameResult
    played_at: datetime
    reward_earned: int = 0  # Estrellas ganadas
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario para persistencia."""
        return {
            'user_id': self.user_id,
            'game_type': self.game_type.value,
            'result': self.result.value,
            'played_at': self.played_at.isoformat(),
            'reward_earned': self.reward_earned
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GameSession':
        """Crear desde diccionario."""
        return cls(
            user_id=data['user_id'],
            game_type=GameType(data['game_type']),
            result=GameResult(data['result']),
            played_at=datetime.fromisoformat(data['played_at']),
            reward_earned=data.get('reward_earned', 0)
        )

@dataclass
class UserBalance:
    """Balance de estrellas de un usuario."""
    user_id: int
    stars_balance: int = 0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    def add_stars(self, amount: int) -> int:
        """Añadir estrellas al balance."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.stars_balance += amount
        self.last_updated = datetime.now()
        return self.stars_balance
    
    def deduct_stars(self, amount: int) -> int:
        """Deducir estrellas del balance."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if self.stars_balance < amount:
            raise ValueError("Insufficient balance")
        self.stars_balance -= amount
        self.last_updated = datetime.now()
        return self.stars_balance
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario."""
        return {
            'user_id': self.user_id,
            'stars_balance': self.stars_balance,
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserBalance':
        """Crear desde diccionario."""
        return cls(
            user_id=data['user_id'],
            stars_balance=data.get('stars_balance', 0),
            last_updated=datetime.fromisoformat(data['last_updated']) if 'last_updated' in data else datetime.now()
        )

@dataclass
class GameStats:
    """Estadísticas de juegos de un usuario."""
    user_id: int
    total_games: int = 0
    total_wins: int = 0
    weekly_wins: int = 0
    last_play_date: Optional[date] = None
    current_week_wins: List[date] = None
    
    def __post_init__(self):
        if self.current_week_wins is None:
            self.current_week_wins = []
    
    def can_play_today(self) -> bool:
        """Verificar si puede jugar hoy."""
        today = date.today()
        return self.last_play_date != today
    
    def can_win_this_week(self) -> bool:
        """Verificar si puede ganar esta semana (máximo 3)."""
        return len(self.current_week_wins) < 3
    
    def record_game(self, game_result: GameResult) -> None:
        """Registrar un juego."""
        self.total_games += 1
        self.last_play_date = date.today()
        
        if game_result == GameResult.WIN:
            self.total_wins += 1
            if date.today() not in self.current_week_wins:
                self.current_week_wins.append(date.today())
    
    def reset_weekly_wins(self) -> None:
        """Resetear victorias semanales."""
        self.current_week_wins = []
        self.weekly_wins = 0
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario."""
        return {
            'user_id': self.user_id,
            'total_games': self.total_games,
            'total_wins': self.total_wins,
            'weekly_wins': self.weekly_wins,
            'last_play_date': self.last_play_date.isoformat() if self.last_play_date else None,
            'current_week_wins': [d.isoformat() for d in self.current_week_wins]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GameStats':
        """Crear desde diccionario."""
        return cls(
            user_id=data['user_id'],
            total_games=data.get('total_games', 0),
            total_wins=data.get('total_wins', 0),
            weekly_wins=data.get('weekly_wins', 0),
            last_play_date=datetime.fromisoformat(data['last_play_date']).date() if data.get('last_play_date') else None,
            current_week_wins=[datetime.fromisoformat(d).date() for d in data.get('current_week_wins', [])]
        )
