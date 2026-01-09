"""
Handler para responder mensajes directos del usuario con IA Sip.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram_bot.messages import SipMessages
from telegram_bot.keyboard import CommonKeyboards
from utils.logger import logger


# Patrones de botones del menú que deben ser manejados por otros handlers
MENU_PATTERNS = [
    r"^🛡️ Mis Llaves$",
    r"^📊 Estado$",
    r"^💰 Operaciones$",
    r"^💰 Mi Balance$",
    r"^👑 Plan VIP$",
    r"^🎮 Juega y Gana$",
    r"^👥 Referidos$",
    r"^🔙 Atrás$",
    r"^🏆 Logros$",
    r"^⚙️ Ayuda$",
    r"^📋\s*Mostrar\s*Menú$",
    r"^🎫 Soporte$",
    r"^🌊 Sip$",
    r"^🤖 Asistente IA$",
    r"^➕ Crear Nueva$",
    r"^Finalizar$",
    r"^Salir$",
    r"^Exit$",
]


class DirectMessageHandler:
    """Handler para responder mensajes directos del usuario con IA."""
    
    def __init__(self, ai_support_service):
        """
        Inicializa el handler de mensajes directos.
        
        Args:
            ai_support_service: Servicio de soporte con IA
        """
        self.ai_support_service = ai_support_service
        logger.info("📨 DirectMessageHandler inicializado")
    
    def _is_menu_button(self, text: str) -> bool:
        """
        Verifica si el texto coincide con un botón del menú.
        
        Args:
            text: Texto del mensaje
            
        Returns:
            bool: True si es un botón del menú
        """
        import re
        for pattern in MENU_PATTERNS:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        return False
    
    async def handle_direct_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Procesa mensaje directo del usuario y responde con IA.
        
        Args:
            update: Update de Telegram
            context: Contexto de Telegram
        """
        user_message = update.message.text
        user_id = update.effective_user.id
        
        # Verificar si es un botón del menú
        if self._is_menu_button(user_message):
            logger.debug(f"📨 Mensaje '{user_message}' es un botón del menú, ignorando")
            return
        
        try:
            await update.message.chat.send_action(action="typing")
            
            # Verificar si hay una conversación activa
            conversation = await self.ai_support_service.get_active_conversation(user_id)
            
            if not conversation:
                # Si no hay conversación activa, iniciar una automáticamente
                logger.info(f"📨 Iniciando conversación automática para usuario {user_id}")
                await self.ai_support_service.start_conversation(
                    user_id=user_id,
                    user_name=update.effective_user.first_name
                )
            
            # Obtener respuesta de la IA
            ai_response = await self.ai_support_service.send_message(
                user_id=user_id,
                user_message=user_message
            )
            
            await update.message.reply_text(
                f"🌊 **Sip:**\n\n{ai_response}",
                parse_mode="Markdown"
            )
            
            logger.debug(f"📨 Respuesta enviada a usuario {user_id}")
            
        except ValueError as e:
            logger.warning(f"⚠️ Error de validación en mensaje directo: {e}")
            await update.message.reply_text(
                SipMessages.ERROR_NO_ACTIVE_CONVERSATION,
                reply_markup=CommonKeyboards.back_button(),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"❌ Error en mensaje directo: {e}")
            await update.message.reply_text(
                SipMessages.ERROR_PROCESSING_MESSAGE,
                parse_mode="Markdown"
            )


def get_direct_message_handler(ai_support_service):
    """
    Retorna el handler para mensajes directos del usuario.
    
    Args:
        ai_support_service: Servicio de soporte con IA
        
    Returns:
        MessageHandler: Handler configurado
    """
    handler = DirectMessageHandler(ai_support_service)
    
    return MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handler.handle_direct_message
    )
