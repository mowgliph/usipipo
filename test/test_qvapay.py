import os
import sys
import asyncio
import logging

# Añadir el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configurar variables de entorno mínimas para evitar errores de DB
os.environ.setdefault("DATABASE_ASYNC_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("QVAPAY_API_KEY", "test_key_placeholder")  # Placeholder, será verificado

# Importar solo el cliente QvaPay directamente para evitar dependencias de DB
from services.qvapay_client import QvaPayClient, QvaPayError

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_qvapay():
    # Verificar API Key
    api_key = os.getenv("QVAPAY_API_KEY")
    if not api_key:
        logger.error("QVAPAY_API_KEY no está configurada en el entorno.")
        return

    logger.info("Iniciando pruebas de QvaPay...")

    # Prueba 1: Crear transacción
    try:
        client = QvaPayClient()
        logger.info("Intentando crear transacción con API key: %s", api_key[:10] + "...")
        logger.info("URL base del cliente: %s", client.BASE_URL)
        logger.info("Endpoint de transacción: %s", f"{client.BASE_URL}/transaction")
        transaction = await asyncio.get_event_loop().run_in_executor(
            None, client.create_transaction, 10.0, "Prueba de transacción", "test123"
        )
        logger.info(f"Transacción creada exitosamente: {transaction}")
        transaction_id = transaction.get("id")
    except QvaPayError as e:
        logger.error(f"Error creando transacción: {e}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        return
    except Exception as e:
        logger.error(f"Error inesperado creando transacción: {e}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        return

    # Prueba 2: Verificar transacción
    if transaction_id:
        try:
            client = QvaPayClient()
            verified = await asyncio.get_event_loop().run_in_executor(
                None, client.get_transaction, transaction_id
            )
            logger.info(f"Transacción verificada: {verified}")
        except QvaPayError as e:
            logger.error(f"Error verificando transacción: {e}")
        except Exception as e:
            logger.error(f"Error inesperado verificando transacción: {e}")

    # Prueba 3: Obtener balance
    try:
        client = QvaPayClient()
        balance = await asyncio.get_event_loop().run_in_executor(
            None, client.get_account
        )
        logger.info(f"Balance obtenido: {balance}")
    except QvaPayError as e:
        logger.error(f"Error obteniendo balance: {e}")
    except Exception as e:
        logger.error(f"Error inesperado obteniendo balance: {e}")

    logger.info("Pruebas completadas.")

if __name__ == "__main__":
    asyncio.run(test_qvapay())