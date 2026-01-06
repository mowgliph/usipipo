import uuid
from typing import List, Dict
from utils.logger import logger

from domain.entities.user import User
from domain.interfaces.iuser_repository import IUserRepository
from domain.interfaces.ireferral_service import IReferralService

class ReferralService(IReferralService):
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def apply_referral_code(self, telegram_id: int, referral_code: str) -> bool:
        """Apply a referral code to a user."""
        try:
            # Get the user
            user = await self.user_repo.get_by_id(telegram_id)
            if not user:
                return False

            # Check if user already has a referrer
            if user.referred_by is not None:
                return False

            # Find the referrer by referral code
            referrer = await self._get_user_by_referral_code(referral_code)
            if not referrer:
                return False

            # Prevent self-referral
            if referrer.telegram_id == telegram_id:
                return False

            # Update user with referrer
            user.referred_by = referrer.telegram_id
            await self.user_repo.save(user)

            logger.info(f"Referral code {referral_code} applied to user {telegram_id}")
            return True

        except Exception as e:
            logger.error(f"Error applying referral code: {e}")
            return False

    async def get_referral_code(self, telegram_id: int) -> str:
        """Get or generate referral code for a user."""
        user = await self.user_repo.get_by_id(telegram_id)
        if not user:
            return ""

        if user.referral_code:
            return user.referral_code

        # Generate new referral code
        referral_code = self._generate_referral_code()
        user.referral_code = referral_code
        await self.user_repo.save(user)

        return referral_code

    async def get_referrals(self, telegram_id: int) -> List[Dict]:
        """Get list of users referred by this user."""
        referrals = await self.user_repo.get_referrals_by_user(telegram_id)
        return [
            {
                "telegram_id": user.telegram_id,
                "username": user.username,
                "full_name": user.full_name,
                "created_at": user.created_at
            }
            for user in referrals
        ]

    async def get_referral_earnings(self, telegram_id: int) -> int:
        """Get total referral earnings for a user."""
        user = await self.user_repo.get_by_id(telegram_id)
        if not user:
            return 0
        return user.total_referral_earnings

    async def get_user_referral_data(self, telegram_id: int) -> Dict:
        """Get complete referral data for a user including code, referrals count, and earnings."""
        try:
            user = await self.user_repo.get_by_id(telegram_id)
            if not user:
                return {
                    "code": "",
                    "direct_referrals": 0,
                    "total_earnings": 0
                }
            
            # Get referral code
            code = await self.get_referral_code(telegram_id)
            
            # Get referrals count
            referrals = await self.get_referrals(telegram_id)
            referrals_count = len(referrals)
            
            # Get earnings
            earnings = await self.get_referral_earnings(telegram_id)
            
            return {
                "code": code,
                "direct_referrals": referrals_count,
                "total_earnings": earnings
            }
        except Exception as e:
            logger.error(f"Error getting referral data for user {telegram_id}: {e}")
            return {
                "code": "",
                "direct_referrals": 0,
                "total_earnings": 0
            }

    async def process_referral_bonus(self, referred_user_id: int, deposit_amount: int) -> bool:
        """Process referral bonus when a referred user makes a deposit."""
        try:
            referred_user = await self.user_repo.get_by_id(referred_user_id)
            if not referred_user or not referred_user.referred_by:
                return False

            referrer = await self.user_repo.get_by_id(referred_user.referred_by)
            if not referrer:
                return False

            # Calculate 10% bonus
            bonus = int(deposit_amount * 0.1)

            # Update referrer's balance and earnings
            referrer.balance_stars += bonus
            referrer.total_referral_earnings += bonus
            await self.user_repo.save(referrer)

            logger.info(f"Referral bonus {bonus} stars credited to user {referrer.telegram_id}")
            return True

        except Exception as e:
            logger.error(f"Error processing referral bonus: {e}")
            return False

    async def _get_user_by_referral_code(self, referral_code: str) -> User:
        """Helper method to find user by referral code."""
        return await self.user_repo.get_by_referral_code(referral_code)

    def _generate_referral_code(self) -> str:
        """Generate a unique referral code."""
        return str(uuid.uuid4())[:8].upper()