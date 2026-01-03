from dataclasses import dataclass, field
from datetime import datetime
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
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    # Métricas de uso (sincronizadas desde los servidores VPN)
    used_bytes: int = 0               # Tráfico consumido en bytes
    last_seen_at: Optional[datetime] = None  # Última actividad del cliente

    def __post_init__(self):
        """
        Se ejecuta automáticamente después de la inicialización.
        Convierte strings ISO a objetos datetime si la BD los devuelve como texto.
        """
        if isinstance(self.created_at, str):
            try:
                # Intenta convertir formato ISO (ej: 2026-01-02T20:44:36)
                self.created_at = datetime.fromisoformat(self.created_at)
            except ValueError:
                # Si falla, intentamos manejar formatos sin T o con espacios si fuera necesario
                # o dejamos el valor tal cual para no romper la ejecución
                pass

        if isinstance(self.last_seen_at, str):
            try:
                self.last_seen_at = datetime.fromisoformat(self.last_seen_at)
            except ValueError:
                self.last_seen_at = None

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