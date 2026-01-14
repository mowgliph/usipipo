from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

class UserStatus(str, Enum):
    """Estados posibles de un usuario en el sistema."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"
    FREE_TRIAL = "free_trial"

class UserRole(str, Enum):
    """Roles disponibles en el sistema."""
    USER = "user"  # Usuario regular
    ADMIN = "admin"  # Administrador del sistema
    TASK_MANAGER = "task_manager"  # Gestor de tareas - Rol especial de pago
    ANNOUNCER = "announcer"  # Anunciante - Rol especial de pago

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
    role: UserRole = UserRole.USER
    max_keys: int = 2
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    balance_stars: int = 0
    total_deposited: int = 0
    referral_code: Optional[str] = None
    referred_by: Optional[int] = None
    total_referral_earnings: int = 0
    is_vip: bool = False
    vip_expires_at: Optional[datetime] = None
    
    # Atributos para roles especiales
    task_manager_expires_at: Optional[datetime] = None
    announcer_expires_at: Optional[datetime] = None
    
    keys: List = field(default_factory=list)

    @property
    def is_active(self) -> bool:
        """Verifica si el usuario está activo."""
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_blocked(self) -> bool:
        """Verifica si el usuario está bloqueado."""
        return self.status == UserStatus.BLOCKED
    
    def is_task_manager_active(self) -> bool:
        """Verifica si el usuario tiene rol de Gestor de Tareas activo."""
        if self.role != UserRole.TASK_MANAGER or not self.task_manager_expires_at:
            return False
        
        now = datetime.now(timezone.utc)
        exp = self.task_manager_expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        else:
            exp = exp.astimezone(timezone.utc)
        return now < exp
    
    def is_announcer_active(self) -> bool:
        """Verifica si el usuario tiene rol de Anunciante activo."""
        if self.role != UserRole.ANNOUNCER or not self.announcer_expires_at:
            return False
        
        now = datetime.now(timezone.utc)
        exp = self.announcer_expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        else:
            exp = exp.astimezone(timezone.utc)
        return now < exp
    
    def can_create_more_keys(self) -> bool:
        """
        Lógica de negocio: Verifica si el usuario tiene permiso 
        para generar una nueva llave según su límite.
        Los administradores pueden crear ilimitadas.
        """
        # Los administradores pueden crear ilimitadas
        if self.role == UserRole.ADMIN:
            return True
            
        active_keys = [k for k in self.keys if getattr(k, 'is_active', True)]
        return len(active_keys) < self.max_keys
    
    def can_delete_keys(self) -> bool:
        """
        Lógica de negocio: Solo usuarios que han recargado pueden eliminar claves.
        Los administradores pueden eliminar sin restricciones.
        """
        # Los administradores pueden eliminar sin restricciones
        if self.role == UserRole.ADMIN:
            return True
            
        return self.total_deposited > 0
    
    def is_vip_active(self) -> bool:
        """
        Verifica si el usuario tiene VIP activo (pagado y no expirado).
        Maneja datetimes naive y aware convirtiendo a UTC para comparar.
        """
        if not self.is_vip or not self.vip_expires_at:
            return False
        
        now = datetime.now(timezone.utc)
        vip_exp = self.vip_expires_at
        if vip_exp.tzinfo is None:
            vip_exp = vip_exp.replace(tzinfo=timezone.utc)
        else:
            vip_exp = vip_exp.astimezone(timezone.utc)
        return now < vip_exp

    def __repr__(self):
        return f"<User(id={self.telegram_id}, username={self.username}, status={self.status})>"
