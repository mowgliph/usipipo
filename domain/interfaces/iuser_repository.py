from typing import Protocol, Optional, List
from domain.entities.user import User

class IUserRepository(Protocol):
    """
    Este es el 'contrato' para el manejo de usuarios.
    Cualquier base de datos que usemos (Supabase, SQL, etc.) 
    DEBE cumplir con estos métodos.
    """

    async def get_by_id(self, telegram_id: int, current_user_id: int) -> Optional[User]:
        """Busca un usuario por su ID de Telegram."""
        ...

    async def save(self, user: User, current_user_id: int) -> User:
        """Guarda un usuario nuevo o actualiza uno existente."""
        ...

    async def exists(self, telegram_id: int, current_user_id: int) -> bool:
        """Verifica si el usuario ya está registrado."""
        ...

    async def get_by_referral_code(self, referral_code: str, current_user_id: int) -> Optional[User]:
        """Busca un usuario por su código de referido."""
        ...

    async def get_referrals_by_user(self, telegram_id: int, current_user_id: int) -> List[User]:
        """Obtiene la lista de usuarios referidos por un usuario."""
        ...

    async def get_referrals(self, referrer_id: int, current_user_id: int) -> List[User]:
        """Obtiene todos los usuarios referidos por este usuario."""
        ...

    async def update_balance(self, telegram_id: int, new_balance: int, current_user_id: int) -> bool:
        """Actualiza el balance de estrellas del usuario."""
        ...

    async def get_user(self, telegram_id: int, current_user_id: int) -> Optional[User]:
        """Busca un usuario por su ID de Telegram (alias de get_by_id)."""
        ...

    async def create_user(self, user_id: int, username: str = None, full_name: str = None, referral_code: str = None, referred_by: int = None, current_user_id: int = None) -> User:
        """Crea un nuevo usuario."""
        ...

    async def get_all_users(self, current_user_id: int) -> List[User]:
        """Obtiene todos los usuarios registrados."""
        ...
