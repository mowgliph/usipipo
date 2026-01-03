from typing import Protocol
import uuid

class ITransactionRepository(Protocol):
    """
    Este es el 'contrato' para el manejo de transacciones.
    Cualquier base de datos que usemos (Supabase, SQL, etc.)
    DEBE cumplir con estos métodos.
    """

    async def record_transaction(self, user_id: int, transaction_type: str, amount: int,
                               balance_after: int, description: str, reference_id: str = None,
                               telegram_payment_id: str = None) -> uuid.UUID:
        """Registra una nueva transacción."""
        ...