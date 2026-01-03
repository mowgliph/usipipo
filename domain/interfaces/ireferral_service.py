from typing import Protocol, List, Dict
from domain.entities.user import User

class IReferralService(Protocol):
    """
    Interface for referral-related operations.
    """

    async def apply_referral_code(self, telegram_id: int, referral_code: str) -> bool:
        """Apply a referral code to a user."""
        ...

    async def get_referral_code(self, telegram_id: int) -> str:
        """Get or generate referral code for a user."""
        ...

    async def get_referrals(self, telegram_id: int) -> List[Dict]:
        """Get list of users referred by this user."""
        ...

    async def get_referral_earnings(self, telegram_id: int) -> int:
        """Get total referral earnings for a user."""
        ...

    async def process_referral_bonus(self, referred_user_id: int, deposit_amount: int) -> bool:
        """Process referral bonus when a referred user makes a deposit."""
        ...