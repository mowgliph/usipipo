"""
Entidades de dominio para el sistema de tareas.

Author: uSipipo Team
Version: 1.0.0
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid
from utils.datetime_utils import now_utc


@dataclass
class Task:
    """Entidad que representa una tarea creada por un administrador."""
    id: uuid.UUID
    title: str
    description: str
    reward_stars: int
    guide_text: Optional[str] = None
    is_active: bool = True
    created_by: Optional[int] = None
    created_at: datetime = field(default_factory=now_utc)
    expires_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Verifica si la tarea ha expirado."""
        if self.expires_at is None:
            return False
        return now_utc() > (self.expires_at if self.expires_at.tzinfo is not None else self.expires_at.replace(tzinfo=timezone.utc))
    
    def is_available(self) -> bool:
        """Verifica si la tarea está disponible para completar."""
        return self.is_active and not self.is_expired()


@dataclass
class UserTask:
    """Entidad que representa el progreso de un usuario en una tarea."""
    user_id: int
    task_id: uuid.UUID
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    reward_claimed: bool = False
    reward_claimed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def can_claim_reward(self) -> bool:
        """Verifica si el usuario puede reclamar la recompensa."""
        return self.is_completed and not self.reward_claimed
    
    def claim_reward(self) -> None:
        """Marca la recompensa como reclamada."""
        if not self.is_completed:
            raise ValueError("No se puede reclamar recompensa de una tarea no completada")
        self.reward_claimed = True
        self.reward_claimed_at = datetime.now()

