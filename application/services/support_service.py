from datetime import datetime
import uuid
from typing import List  # <--- FALTABA ESTA LÍNEA
from domain.entities.ticket import Ticket
from infrastructure.persistence.supabase.ticket_repository import TicketRepository
from utils.datetime_utils import now_utc

class SupportService:
    def __init__(self, ticket_repo: TicketRepository):
        self.ticket_repo = ticket_repo

    async def open_ticket(self, user_id: int, user_name: str) -> Ticket:
        existing = await self.ticket_repo.get_open_by_user(user_id)
        if existing:
            return existing
        
        new_ticket = Ticket(id=uuid.uuid4(), user_id=user_id, user_name=user_name)
        await self.ticket_repo.save(new_ticket)
        return new_ticket

    async def update_activity(self, user_id: int):
        ticket = await self.ticket_repo.get_open_by_user(user_id)
        if ticket:
            ticket.last_message_at = now_utc()
            await self.ticket_repo.save(ticket)

    async def close_ticket(self, user_id: int):
        ticket = await self.ticket_repo.get_open_by_user(user_id)
        if ticket:
            ticket.status = "closed"
            await self.ticket_repo.save(ticket)

    async def check_and_close_stale_tickets(self) -> List[int]:
        """Retorna una lista de IDs de usuarios cuyos tickets fueron cerrados por inactividad."""
        open_tickets = await self.ticket_repo.get_all_open()
        closed_users = []
        for ticket in open_tickets:
            # Asumiendo que el método is_stale existe en la entidad Ticket
            if ticket.is_stale(48):
                ticket.status = "closed"
                await self.ticket_repo.save(ticket)
                closed_users.append(ticket.user_id)
        return closed_users
