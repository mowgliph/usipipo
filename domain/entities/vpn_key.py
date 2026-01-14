from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

class KeyType(str, Enum):
    """Define los tipos de VPN que soporta el sistema."""
    OUTLINE = "outline"
    WIREGUARD = "wireguard"

@dataclass
class VpnKey:
    """
    Entidad que representa una credencial de acceso a la VPN.
    
    Guarda la información técnica necesaria para que el usuario se conecte.
    """
    id: Optional[str] = None          # ID interno en nuestra base de datos
    user_id: Optional[int] = None     # El telegram_id del dueño de la llave
    key_type: KeyType = KeyType.OUTLINE
    name: str = "Nueva Clave"         # Nombre descriptivo (ej: "Mi iPhone")
    
    # Datos técnicos
    key_data: str = ""                # Aquí va el "ss://..." o el config de WireGuard
    external_id: str = ""             # El ID que le asigna el servidor (Outline/WG)
    
    # Estado y fechas
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    
    # Métricas de uso (sincronizadas desde los servidores VPN)
    used_bytes: int = 0               # Tráfico consumido en bytes
    last_seen_at: Optional[datetime] = None  # Última actividad del cliente
    
    data_limit_bytes: int = 10 * 1024**3  # 10 GB por defecto
    billing_reset_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None  # Fecha de expiración de la clave

    def __post_init__(self):
        """
        Se ejecuta automáticamente después de la inicialización.
        Convierte strings ISO a objetos datetime si la BD los devuelve como texto.
        Normaliza todos los datetimes para que sean aware (con timezone UTC).
        """
        if isinstance(self.created_at, str):
            try:
                self.created_at = datetime.fromisoformat(self.created_at)
            except ValueError:
                self.created_at = datetime.now(timezone.utc)
        
        # Normalizar created_at a UTC aware
        if self.created_at and self.created_at.tzinfo is None:
            self.created_at = self.created_at.replace(tzinfo=timezone.utc)
        elif self.created_at:
            self.created_at = self.created_at.astimezone(timezone.utc)

        if isinstance(self.last_seen_at, str):
            try:
                self.last_seen_at = datetime.fromisoformat(self.last_seen_at)
            except ValueError:
                self.last_seen_at = None
        
        # Normalizar last_seen_at a UTC aware si existe
        if self.last_seen_at and self.last_seen_at.tzinfo is None:
            self.last_seen_at = self.last_seen_at.replace(tzinfo=timezone.utc)
        elif self.last_seen_at:
            self.last_seen_at = self.last_seen_at.astimezone(timezone.utc)
        
        if isinstance(self.billing_reset_at, str):
            try:
                self.billing_reset_at = datetime.fromisoformat(self.billing_reset_at)
            except ValueError:
                self.billing_reset_at = datetime.now(timezone.utc)
        
        # Normalizar billing_reset_at a UTC aware
        if self.billing_reset_at and self.billing_reset_at.tzinfo is None:
            self.billing_reset_at = self.billing_reset_at.replace(tzinfo=timezone.utc)
        elif self.billing_reset_at:
            self.billing_reset_at = self.billing_reset_at.astimezone(timezone.utc)
        
        if isinstance(self.expires_at, str):
            try:
                self.expires_at = datetime.fromisoformat(self.expires_at)
            except ValueError:
                self.expires_at = None
        
        # Normalizar expires_at a UTC aware si existe
        if self.expires_at and self.expires_at.tzinfo is None:
            self.expires_at = self.expires_at.replace(tzinfo=timezone.utc)
        elif self.expires_at:
            self.expires_at = self.expires_at.astimezone(timezone.utc)

    def __repr__(self):
        return f"<VpnKey(name={self.name}, type={self.key_type}, active={self.is_active})>"
    
    @property
    def used_mb(self) -> float:
        """Retorna el consumo en megabytes."""
        return self.used_bytes / (1024 * 1024)
    
    @property
    def used_gb(self) -> float:
        """Retorna el consumo en gigabytes."""
        return self.used_bytes / (1024 * 1024 * 1024)
    
    @property
    def data_limit_gb(self) -> float:
        """Retorna el límite de datos en gigabytes."""
        return self.data_limit_bytes / (1024 * 1024 * 1024)
    
    @property
    def remaining_bytes(self) -> int:
        """Bytes restantes en el ciclo de facturación."""
        return max(0, self.data_limit_bytes - self.used_bytes)
    
    @property
    def is_over_limit(self) -> bool:
        """True si se excedió el límite de datos."""
        return self.used_bytes > self.data_limit_bytes
    
    def needs_reset(self) -> bool:
        """True si necesita reset mensual (ha pasado 30 días)."""
        # Usar datetime con timezone UTC para consistencia
        now = datetime.now(timezone.utc)
        
        billing_reset = self.billing_reset_at
        if billing_reset is None:
            return False
        
        # Asegurar que billing_reset tenga timezone UTC
        if billing_reset.tzinfo is None:
            billing_reset = billing_reset.replace(tzinfo=timezone.utc)
        else:
            billing_reset = billing_reset.astimezone(timezone.utc)
        
        # Ambas fechas ahora tienen timezone, comparación directa
        result = now > billing_reset + timedelta(days=30)
        return result
    
    @property
    def server(self) -> str:
        """
        Retorna el nombre del servidor basado en el tipo de clave.
        Proporciona una forma consistente de obtener información del servidor.
        """
        if self.key_type == KeyType.OUTLINE:
            return "Outline Server"
        elif self.key_type == KeyType.WIREGUARD:
            return "WireGuard Server"
        else:
            return "Unknown Server"