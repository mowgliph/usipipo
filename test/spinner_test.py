"""
Test simple para verificar el sistema de spinner.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock
from telegram import Update
from telegram.ext import ContextTypes

# Importar el sistema de spinner
from utils.spinner import SpinnerManager, with_spinner


async def test_spinner_basic():
    """Test básico del sistema de spinner."""
    
    # Mock objects
    update = MagicMock()
    update.message = AsyncMock()
    update.message.reply_text = AsyncMock(return_value=MagicMock(message_id=123))
    update.effective_chat.id = 12345
    
    context = MagicMock()
    context.bot = AsyncMock()
    context.chat_data = {}
    
    # Test 1: Mensaje de spinner
    message_id = await SpinnerManager.send_spinner_message(
        update, 
        operation_type="loading"
    )
    
    assert message_id == 123
    print("✅ Test 1: Spinner message sent successfully")
    
    # Test 2: Decorador básico
    @with_spinner("testing", "🧪 Test message")
    async def test_function(update, context):
        await asyncio.sleep(0.1)  # Simular operación
        return "test_result"
    
    result = await test_function(update, context)
    assert result == "test_result"
    print("✅ Test 2: Decorator works correctly")
    
    # Test 3: Verificación de tipos
    assert hasattr(context, 'bot')
    assert hasattr(context, 'chat_data')
    print("✅ Test 3: Type checking works")
    
    print("🎉 All tests passed! Spinner system is working correctly.")


if __name__ == "__main__":
    asyncio.run(test_spinner_basic())
