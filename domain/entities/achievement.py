"""
Entidades del sistema de logros y badges para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from datetime import datetime, date
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

class AchievementType(str, Enum):
    """Tipos de logros disponibles."""
    DATA_CONSUMED = "data_consumed"
    DAYS_ACTIVE = "days_active"
    REFERRALS_COUNT = "referrals_count"
    STARS_DEPOSITED = "stars_deposited"
    KEYS_CREATED = "keys_created"
    GAMES_WON = "games_won"
    VIP_MONTHS = "vip_months"

class AchievementTier(str, Enum):
    """Niveles de logros."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

@dataclass
class Achievement:
    """Definición de un logro."""
    id: str
    name: str
    description: str
    type: AchievementType
    tier: AchievementTier
    requirement_value: int
    reward_stars: int
    icon: str
    is_active: bool = True
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario para persistencia."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type.value,
            'tier': self.tier.value,
            'requirement_value': self.requirement_value,
            'reward_stars': self.reward_stars,
            'icon': self.icon,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Achievement':
        """Crear desde diccionario."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            type=AchievementType(data['type']),
            tier=AchievementTier(data['tier']),
            requirement_value=data['requirement_value'],
            reward_stars=data['reward_stars'],
            icon=data['icon'],
            is_active=data.get('is_active', True)
        )

@dataclass
class UserAchievement:
    """Progreso de un usuario en un logro específico."""
    user_id: int
    achievement_id: str
    current_value: int = 0
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    reward_claimed: bool = False
    reward_claimed_at: Optional[datetime] = None
    
    def update_progress(self, new_value: int) -> bool:
        """Actualiza el progreso y retorna si se completó."""
        self.current_value = new_value
        if not self.is_completed and self.current_value >= self.get_requirement_value():
            self.is_completed = True
            self.completed_at = datetime.now()
            return True
        return False
    
    def get_requirement_value(self) -> int:
        """Obtiene el valor requerido (debe ser cargado desde Achievement)."""
        # Este valor será establecido por el servicio de logros
        return 0
    
    def claim_reward(self) -> bool:
        """Reclama la recompensa del logro."""
        if self.is_completed and not self.reward_claimed:
            self.reward_claimed = True
            self.reward_claimed_at = datetime.now()
            return True
        return False
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario."""
        return {
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'current_value': self.current_value,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'reward_claimed': self.reward_claimed,
            'reward_claimed_at': self.reward_claimed_at.isoformat() if self.reward_claimed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserAchievement':
        """Crear desde diccionario."""
        return cls(
            user_id=data['user_id'],
            achievement_id=data['achievement_id'],
            current_value=data.get('current_value', 0),
            is_completed=data.get('is_completed', False),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            reward_claimed=data.get('reward_claimed', False),
            reward_claimed_at=datetime.fromisoformat(data['reward_claimed_at']) if data.get('reward_claimed_at') else None
        )

@dataclass
class UserStats:
    """Estadísticas generales del usuario para seguimiento de logros."""
    user_id: int
    total_data_consumed_gb: float = 0.0
    days_active: int = 0
    total_referrals: int = 0
    total_stars_deposited: int = 0
    total_keys_created: int = 0
    total_games_won: int = 0
    vip_months_purchased: int = 0
    last_active_date: Optional[date] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_active_date is None:
            self.last_active_date = date.today()
    
    def update_data_consumed(self, additional_gb: float):
        """Actualiza el consumo de datos."""
        self.total_data_consumed_gb += additional_gb
    
    def update_daily_activity(self):
        """Actualiza los días de actividad."""
        today = date.today()
        if self.last_active_date != today:
            self.days_active += 1
            self.last_active_date = today
    
    def increment_referrals(self):
        """Incrementa el contador de referidos."""
        self.total_referrals += 1
    
    def add_stars_deposited(self, amount: int):
        """Añade estrellas depositadas."""
        self.total_stars_deposited += amount
    
    def increment_keys_created(self):
        """Incrementa el contador de claves creadas."""
        self.total_keys_created += 1
    
    def increment_games_won(self):
        """Incrementa el contador de juegos ganados."""
        self.total_games_won += 1
    
    def add_vip_months(self, months: int):
        """Añade meses VIP comprados."""
        self.vip_months_purchased += months
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario."""
        return {
            'user_id': self.user_id,
            'total_data_consumed_gb': self.total_data_consumed_gb,
            'days_active': self.days_active,
            'total_referrals': self.total_referrals,
            'total_stars_deposited': self.total_stars_deposited,
            'total_keys_created': self.total_keys_created,
            'total_games_won': self.total_games_won,
            'vip_months_purchased': self.vip_months_purchased,
            'last_active_date': self.last_active_date.isoformat() if self.last_active_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserStats':
        """Crear desde diccionario."""
        return cls(
            user_id=data['user_id'],
            total_data_consumed_gb=data.get('total_data_consumed_gb', 0.0),
            days_active=data.get('days_active', 0),
            total_referrals=data.get('total_referrals', 0),
            total_stars_deposited=data.get('total_stars_deposited', 0),
            total_keys_created=data.get('total_keys_created', 0),
            total_games_won=data.get('total_games_won', 0),
            vip_months_purchased=data.get('vip_months_purchased', 0),
            last_active_date=datetime.fromisoformat(data['last_active_date']).date() if data.get('last_active_date') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )

# Definiciones de logros predefinidos
ACHIEVEMENTS_DEFINITIONS = [
    # Logros de consumo de datos
    Achievement("data_bronze_1", "Primeros Pasos", "Consume 1 GB de datos", AchievementType.DATA_CONSUMED, AchievementTier.BRONZE, 1, 5, "🥉"),
    Achievement("data_bronze_2", "Navegante", "Consume 5 GB de datos", AchievementType.DATA_CONSUMED, AchievementTier.BRONZE, 5, 10, "🥉"),
    Achievement("data_silver_1", "Explorador", "Consume 10 GB de datos", AchievementType.DATA_CONSUMED, AchievementTier.SILVER, 10, 25, "🥈"),
    Achievement("data_silver_2", "Viajero Frecuente", "Consume 25 GB de datos", AchievementType.DATA_CONSUMED, AchievementTier.SILVER, 25, 50, "🥈"),
    Achievement("data_gold_1", "Conquistador", "Consume 50 GB de datos", AchievementType.DATA_CONSUMED, AchievementTier.GOLD, 50, 100, "🥇"),
    Achievement("data_gold_2", "Maestro de Datos", "Consume 100 GB de datos", AchievementType.DATA_CONSUMED, AchievementTier.GOLD, 100, 200, "🥇"),
    Achievement("data_platinum_1", "Leyenda Digital", "Consume 250 GB de datos", AchievementType.DATA_CONSUMED, AchievementTier.PLATINUM, 250, 500, "💎"),
    Achievement("data_diamond_1", "Titán de la Red", "Consume 500 GB de datos", AchievementType.DATA_CONSUMED, AchievementTier.DIAMOND, 500, 1000, "💍"),
    
    # Logros de días activos
    Achievement("days_bronze_1", "Novato", "Usa el bot por 1 día", AchievementType.DAYS_ACTIVE, AchievementTier.BRONZE, 1, 3, "🥉"),
    Achievement("days_bronze_2", "Regular", "Usa el bot por 7 días", AchievementType.DAYS_ACTIVE, AchievementTier.BRONZE, 7, 15, "🥉"),
    Achievement("days_silver_1", "Dedicado", "Usa el bot por 30 días", AchievementType.DAYS_ACTIVE, AchievementTier.SILVER, 30, 50, "🥈"),
    Achievement("days_silver_2", "Constante", "Usa el bot por 90 días", AchievementType.DAYS_ACTIVE, AchievementTier.SILVER, 90, 100, "🥈"),
    Achievement("days_gold_1", "Veterano", "Usa el bot por 180 días", AchievementType.DAYS_ACTIVE, AchievementTier.GOLD, 180, 200, "🥇"),
    Achievement("days_gold_2", "Experto", "Usa el bot por 365 días", AchievementType.DAYS_ACTIVE, AchievementTier.GOLD, 365, 500, "🥇"),
    Achievement("days_platinum_1", "Maestro", "Usa el bot por 730 días", AchievementType.DAYS_ACTIVE, AchievementTier.PLATINUM, 730, 1000, "💎"),
    Achievement("days_diamond_1", "Leyenda", "Usa el bot por 1000 días", AchievementType.DAYS_ACTIVE, AchievementTier.DIAMOND, 1000, 2000, "💍"),
    
    # Logros de referidos
    Achievement("ref_bronze_1", "Amigos", "Refiere 1 usuario", AchievementType.REFERRALS_COUNT, AchievementTier.BRONZE, 1, 10, "🥉"),
    Achievement("ref_bronze_2", "Conector", "Refiere 3 usuarios", AchievementType.REFERRALS_COUNT, AchievementTier.BRONZE, 3, 30, "🥉"),
    Achievement("ref_silver_1", "Influencer", "Refiere 5 usuarios", AchievementType.REFERRALS_COUNT, AchievementTier.SILVER, 5, 75, "🥈"),
    Achievement("ref_silver_2", "Líder", "Refiere 10 usuarios", AchievementType.REFERRALS_COUNT, AchievementTier.SILVER, 10, 150, "🥈"),
    Achievement("ref_gold_1", "Mentor", "Refiere 25 usuarios", AchievementType.REFERRALS_COUNT, AchievementTier.GOLD, 25, 400, "🥇"),
    Achievement("ref_gold_2", "Gurú", "Refiere 50 usuarios", AchievementType.REFERRALS_COUNT, AchievementTier.GOLD, 50, 1000, "🥇"),
    Achievement("ref_platinum_1", "Estrella", "Refiere 100 usuarios", AchievementType.REFERRALS_COUNT, AchievementTier.PLATINUM, 100, 2500, "💎"),
    Achievement("ref_diamond_1", "Leyenda", "Refiere 250 usuarios", AchievementType.REFERRALS_COUNT, AchievementTier.DIAMOND, 250, 5000, "💍"),
    
    # Logros de estrellas depositadas
    Achievement("stars_bronze_1", "Inversor", "Deposita 10 estrellas", AchievementType.STARS_DEPOSITED, AchievementTier.BRONZE, 10, 5, "🥉"),
    Achievement("stars_bronze_2", "Ahorrista", "Deposita 50 estrellas", AchievementType.STARS_DEPOSITED, AchievementTier.BRONZE, 50, 25, "🥉"),
    Achievement("stars_silver_1", "Banquero", "Deposita 100 estrellas", AchievementType.STARS_DEPOSITED, AchievementTier.SILVER, 100, 60, "🥈"),
    Achievement("stars_silver_2", "Financiero", "Deposita 250 estrellas", AchievementType.STARS_DEPOSITED, AchievementTier.SILVER, 250, 150, "🥈"),
    Achievement("stars_gold_1", "Magnate", "Deposita 500 estrellas", AchievementType.STARS_DEPOSITED, AchievementTier.GOLD, 500, 350, "🥇"),
    Achievement("stars_gold_2", "Titán", "Deposita 1000 estrellas", AchievementType.STARS_DEPOSITED, AchievementTier.GOLD, 1000, 800, "🥇"),
    Achievement("stars_platinum_1", "Mogul", "Deposita 2500 estrellas", AchievementType.STARS_DEPOSITED, AchievementTier.PLATINUM, 2500, 2000, "💎"),
    Achievement("stars_diamond_1", "Legendario", "Deposita 5000 estrellas", AchievementType.STARS_DEPOSITED, AchievementTier.DIAMOND, 5000, 5000, "💍"),
    
    # Logros de claves creadas
    Achievement("keys_bronze_1", "Principiante", "Crea 1 clave", AchievementType.KEYS_CREATED, AchievementTier.BRONZE, 1, 2, "🥉"),
    Achievement("keys_bronze_2", "Práctico", "Crea 5 claves", AchievementType.KEYS_CREATED, AchievementTier.BRONZE, 5, 10, "🥉"),
    Achievement("keys_silver_1", "Experto en Claves", "Crea 10 claves", AchievementType.KEYS_CREATED, AchievementTier.SILVER, 10, 25, "🥈"),
    Achievement("keys_silver_2", "Coleccionista", "Crea 25 claves", AchievementType.KEYS_CREATED, AchievementTier.SILVER, 25, 60, "🥈"),
    Achievement("keys_gold_1", "Maestro de Claves", "Crea 50 claves", AchievementType.KEYS_CREATED, AchievementTier.GOLD, 50, 150, "🥇"),
    Achievement("keys_gold_2", "Generador", "Crea 100 claves", AchievementType.KEYS_CREATED, AchievementTier.GOLD, 100, 300, "🥇"),
    Achievement("keys_platinum_1", "Factory", "Crea 250 claves", AchievementType.KEYS_CREATED, AchievementTier.PLATINUM, 250, 800, "💎"),
    Achievement("keys_diamond_1", "Infinity", "Crea 500 claves", AchievementType.KEYS_CREATED, AchievementTier.DIAMOND, 500, 1500, "💍"),
    
    # Logros de juegos ganados
    Achievement("games_bronze_1", "Jugador", "Gana 1 juego", AchievementType.GAMES_WON, AchievementTier.BRONZE, 1, 3, "🥉"),
    Achievement("games_bronze_2", "Competidor", "Gana 5 juegos", AchievementType.GAMES_WON, AchievementTier.BRONZE, 5, 15, "🥉"),
    Achievement("games_silver_1", "Campeón", "Gana 10 juegos", AchievementType.GAMES_WON, AchievementTier.SILVER, 10, 35, "🥈"),
    Achievement("games_silver_2", "Ganador", "Gana 25 juegos", AchievementType.GAMES_WON, AchievementTier.SILVER, 25, 80, "🥈"),
    Achievement("games_gold_1", "Maestro", "Gana 50 juegos", AchievementType.GAMES_WON, AchievementTier.GOLD, 50, 180, "🥇"),
    Achievement("games_gold_2", "Leyenda", "Gana 100 juegos", AchievementType.GAMES_WON, AchievementTier.GOLD, 100, 400, "🥇"),
    Achievement("games_platinum_1", "Inmortal", "Gana 250 juegos", AchievementType.GAMES_WON, AchievementTier.PLATINUM, 250, 1000, "💎"),
    Achievement("games_diamond_1", "Dios", "Gana 500 juegos", AchievementType.GAMES_WON, AchievementTier.DIAMOND, 500, 2000, "💍"),
    
    # Logros VIP
    Achievement("vip_bronze_1", "VIP Novato", "Compra 1 mes VIP", AchievementType.VIP_MONTHS, AchievementTier.BRONZE, 1, 5, "🥉"),
    Achievement("vip_bronze_2", "VIP Regular", "Compra 3 meses VIP", AchievementType.VIP_MONTHS, AchievementTier.BRONZE, 3, 20, "🥉"),
    Achievement("vip_silver_1", "VIP Dedicado", "Compra 6 meses VIP", AchievementType.VIP_MONTHS, AchievementTier.SILVER, 6, 50, "🥈"),
    Achievement("vip_silver_2", "VIP Leal", "Compra 12 meses VIP", AchievementType.VIP_MONTHS, AchievementTier.SILVER, 12, 100, "🥈"),
    Achievement("vip_gold_1", "VIP Elite", "Compra 24 meses VIP", AchievementType.VIP_MONTHS, AchievementTier.GOLD, 24, 250, "🥇"),
    Achievement("vip_gold_2", "VIP Supremo", "Compra 36 meses VIP", AchievementType.VIP_MONTHS, AchievementTier.GOLD, 36, 500, "🥇"),
    Achievement("vip_platinum_1", "VIP Leyenda", "Compra 60 meses VIP", AchievementType.VIP_MONTHS, AchievementTier.PLATINUM, 60, 1000, "💎"),
    Achievement("vip_diamond_1", "VIP Eterno", "Compra 120 meses VIP", AchievementType.VIP_MONTHS, AchievementTier.DIAMOND, 120, 2500, "💍"),
]

def get_achievements_by_type(achievement_type: AchievementType) -> List[Achievement]:
    """Obtiene todos los logros de un tipo específico."""
    return [a for a in ACHIEVEMENTS_DEFINITIONS if a.type == achievement_type]

def get_achievement_by_id(achievement_id: str) -> Optional[Achievement]:
    """Obtiene un logro por su ID."""
    for achievement in ACHIEVEMENTS_DEFINITIONS:
        if achievement.id == achievement_id:
            return achievement
    return None
