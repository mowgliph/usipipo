import uuid
from domain.interfaces.itransaction_repository import ITransactionRepository
from .supabase_client import get_supabase
from loguru import logger

class SupabaseTransactionRepository(ITransactionRepository):
    """
    Implementación real del manejo de transacciones usando Supabase.
    """

    def __init__(self):
        self.client = get_supabase()
        self.table = "transactions"

    async def record_transaction(self, user_id: int, transaction_type: str, amount: int,
                               balance_after: int, description: str, reference_id: str = None,
                               telegram_payment_id: str = None) -> uuid.UUID:
        """Registra una nueva transacción."""
        try:
            transaction_data = {
                "user_id": user_id,
                "transaction_type": transaction_type,
                "amount": amount,
                "balance_after": balance_after,
                "reference_id": reference_id,
                "description": description,
                "telegram_payment_id": telegram_payment_id
            }

            response = self.client.table(self.table).insert(transaction_data).execute()

            if response.data and len(response.data) > 0:
                transaction_id = response.data[0]["id"]
                logger.info(f"💾 Transacción registrada: {transaction_id}")
                return transaction_id
            else:
                raise Exception("No se pudo registrar la transacción")

        except Exception as e:
            logger.error(f"❌ Error al registrar transacción: {e}")
            raise e