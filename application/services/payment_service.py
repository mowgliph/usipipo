from typing import Optional
from loguru import logger

from domain.entities.user import User
from domain.interfaces.iuser_repository import IUserRepository
from domain.interfaces.itransaction_repository import ITransactionRepository

class PaymentService:
    def __init__(self, user_repo: IUserRepository, transaction_repo: ITransactionRepository):
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo

    async def update_balance(self, telegram_id: int, amount: int, transaction_type: str,
                           description: str, reference_id: str = None,
                           telegram_payment_id: str = None) -> bool:
        """Actualiza el balance del usuario y registra la transacción."""
        try:
            user = await self.user_repo.get_by_id(telegram_id)
            if not user:
                raise Exception("Usuario no encontrado")

            old_balance = user.balance_stars
            user.balance_stars += amount

            # Update total deposited if it's a deposit
            if amount > 0 and transaction_type == "deposit":
                user.total_deposited += amount

            await self.user_repo.save(user)

            # Record transaction
            await self.transaction_repo.record_transaction(
                user_id=telegram_id,
                transaction_type=transaction_type,
                amount=amount,
                balance_after=user.balance_stars,
                description=description,
                reference_id=reference_id,
                telegram_payment_id=telegram_payment_id
            )

            logger.info(f"💰 Balance updated for user {telegram_id}: {old_balance} -> {user.balance_stars}")
            return True

        except Exception as e:
            logger.error(f"Error updating balance: {e}")
            return False

    async def apply_referral_commission(self, telegram_id: int, amount: int) -> bool:
        """Aplica comisión de referido al usuario que refirió a este."""
        try:
            user = await self.user_repo.get_by_id(telegram_id)
            if not user or not user.referred_by:
                return True  # No referrer, not an error

            referrer = await self.user_repo.get_by_id(user.referred_by)
            if not referrer:
                return True  # Referrer not found, not an error

            commission = int(amount * 0.10)  # 10% commission

            # Update referrer's balance and earnings
            referrer.balance_stars += commission
            referrer.total_referral_earnings += commission
            await self.user_repo.save(referrer)

            # Record commission transaction
            await self.transaction_repo.record_transaction(
                user_id=user.referred_by,
                transaction_type="referral_commission",
                amount=commission,
                balance_after=referrer.balance_stars,
                description=f"Comisión por referido: {user.telegram_id}",
                reference_id=f"ref_comm_{telegram_id}_{amount}"
            )

            logger.info(f"🎉 Referral commission applied: {commission} stars to {user.referred_by}")
            return True

        except Exception as e:
            logger.error(f"Error applying referral commission: {e}")
            return False