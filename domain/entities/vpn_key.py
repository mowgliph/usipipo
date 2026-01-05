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

    def __post_init__(self):
        """
        Se ejecuta automáticamente después de la inicialización.
        Convierte strings ISO a objetos datetime si la BD los devuelve como texto.
        """
        if isinstance(self.created_at, str):
            try:
                self.created_at = datetime.fromisoformat(self.created_at)
            except ValueError:
                pass

        if isinstance(self.last_seen_at, str):
            try:
                self.last_seen_at = datetime.fromisoformat(self.last_seen_at)
            except ValueError:
                self.last_seen_at = None
        
        if isinstance(self.billing_reset_at, str):
            try:
                self.billing_reset_at = datetime.fromisoformat(self.billing_reset_at)
            except ValueError:
                self.billing_reset_at = datetime.now()

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
        from datetime import timezone
        
        # Normalizar ambas fechas a naive UTC para comparación segura
        now = datetime.utcnow()
        
        billing_reset = self.billing_reset_at
        if billing_reset is None:
            return False
        
        # Si billing_reset_at tiene timezone, convertir a naive UTC
        if billing_reset.tzinfo is not None:
            billing_reset = billing_reset.astimezone(timezone.utc).replace(tzinfo=None)
        
        result = now > billing_reset + timedelta(days=30)
        return result