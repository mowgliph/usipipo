from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

class UserStatus(str, Enum):
    """Estados posibles de un usuario en el sistema."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    FREE_TRIAL = "free_trial"

@dataclass
class User:
    """
    Entidad fundamental que representa a un usuario del bot/API.
    
    Esta clase es pura: no depende de ninguna base de datos ni librería externa.
    """
    telegram_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    status: UserStatus = UserStatus.ACTIVE
    max_keys: int = 5
    created_at: datetime = field(default_factory=datetime.now)
    
    # Esta lista se llenará con objetos VpnKey en el futuro
    keys: List = field(default_factory=list)

    def can_create_more_keys(self) -> bool:
        """
        Lógica de negocio: Verifica si el usuario tiene permiso 
        para generar una nueva llave según su límite.
        """
        # Contamos solo las llaves que no estén marcadas como eliminadas/inactivas
        active_keys = [k for k in self.keys if getattr(k, 'is_active', True)]
        return len(active_keys) < self.max_keys

    def __repr__(self):
        return f"<User(id={self.telegram_id}, username={self.username}, status={self.status})>"
