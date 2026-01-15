"""
Base repository class for Supabase repositories with RLS support.

Author: uSipipo Team
Version: 2.0.0
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger


class BaseSupabaseRepository:
    """
    Base class for all Supabase repositories providing RLS session variable management.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session

    async def _set_current_user(self, user_id: int) -> None:
        """
        Set the current user ID in the database session for RLS policies.

        Args:
            user_id: The telegram_id of the current user.
        """
        try:
            await self.session.execute(
                text("SET app.current_user_id = :user_id"),
                {"user_id": user_id}
            )
        except Exception as e:
            logger.error(f"❌ Error setting current user {user_id}: {e}")
            raise