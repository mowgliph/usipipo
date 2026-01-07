from dataclasses import dataclass, field
from datetime import datetime
import uuid
from utils.datetime_utils import now_utc

@dataclass
class Ticket:
    id: uuid.UUID
    user_id: int
    user_name: str
    status: str = "open"  # "open" o "closed"
    created_at: datetime = field(default_factory=now_utc)
    last_message_at: datetime = field(default_factory=now_utc)

    def is_stale(self, hours: int = 48) -> bool:
        """Verifica si el ticket debe cerrarse por inactividad."""
        delta = now_utc() - self.last_message_at
        return delta.total_seconds() > (hours * 3600)
