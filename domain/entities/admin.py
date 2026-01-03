"""
Entidades de administración para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List

@dataclass
class AdminUserInfo:
    """Información de usuario para administración."""
    user_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    is_vip: bool
    vip_expiry: Optional[datetime]
    total_keys: int
    active_keys: int
    stars_balance: int
    registration_date: datetime
    last_activity: Optional[datetime]

@dataclass
class AdminKeyInfo:
    """Información de clave para administración."""
    key_id: str
    user_id: int
    user_name: str
    key_type: str  # 'wireguard' o 'outline'
    key_name: str
    access_url: Optional[str]
    created_at: datetime
    last_used: Optional[datetime]
    data_limit: int
    data_used: int
    is_active: bool
    server_status: str  # 'active', 'inactive', 'error'

@dataclass
class ServerStatus:
    """Estado del servidor VPN."""
    server_type: str  # 'wireguard' o 'outline'
    is_healthy: bool
    total_keys: int
    active_keys: int
    version: Optional[str]
    uptime: Optional[str]
    error_message: Optional[str]

@dataclass
class AdminOperationResult:
    """Resultado de operación administrativa."""
    success: bool
    operation: str
    target_id: str
    message: str
    details: Optional[Dict] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
