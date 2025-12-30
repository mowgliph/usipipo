from typing import Optional, List
import uuid
from datetime import datetime
from domain.entities.ticket import Ticket
from infrastructure.persistence.supabase.supabase_client import get_supabase

class TicketRepository:
    def __init__(self):
        self.client = get_supabase()
        self.table = "tickets"

    async def get_open_by_user(self, user_id: int) -> Optional[Ticket]:
        res = self.client.table(self.table).select("*").eq("user_id", user_id).eq("status", "open").execute()
        if not res.data: return None
        data = res.data[0]
        return Ticket(**data)

    async def save(self, ticket: Ticket):
        data = {
            "id": str(ticket.id),
            "user_id": ticket.user_id,
            "user_name": ticket.user_name,
            "status": ticket.status,
            "last_message_at": ticket.last_message_at.isoformat()
        }
        self.client.table(self.table).upsert(data).execute()

    async def get_all_open(self) -> List[Ticket]:
        res = self.client.table(self.table).select("*").eq("status", "open").execute()
        return [Ticket(**item) for item in res.data]
