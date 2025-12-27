from typing import Protocol, Optional
from domain.entities.user import User

class IUserRepository(Protocol):
    """
    Este es el 'contrato' para el manejo de usuarios.
    Cualquier base de datos que usemos (Supabase, SQL, etc.) 
    DEBE cumplir con estos métodos.
    """

    async def get_by_id(self, telegram_id: int) -> Optional[User]:
        """Busca un usuario por su ID de Telegram."""
        ...

    async def save(self, user: User) -> User:
        """Guarda un usuario nuevo o actualiza uno existente."""
        ...

    async def exists(self, telegram_id: int) -> bool:
        """Verifica si el usuario ya está registrado."""
        ...
