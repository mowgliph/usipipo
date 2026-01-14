"""
Handler para responder mensajes directos con IA Sip.

Este handler solo actúa cuando NO hay una conversación activa
en el ConversationHandler.

Author: uSipipo Team
Version: 1.1.0
"""

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from telegram_bot.common.base_handler import BaseHandler
from utils.logger import logger


# Patrones de botones del menú que NO deben ser procesados por IA
MENU_BUTTON_PATTERNS = [
    r"^🛡️\s*Mis\s*Llaves$",
    r"^📊\s*Estado$",
    r"^💰\s*Operaciones$",
    r"^💰\s*Mi\s*Balance$",
    r"^🏆\s*Logros$",
    r"^👥\s*Referidos$",
    r"^🎮\s*Juega\s*y\s*Gana$",
    r"^👑\s*Plan\s*VIP$",
    r"^🎫\s*Soporte$",
    r"^🌊\s*Sip$",
    r"^🤖\s*Asistente\s*IA$",
    r"^➕\s*Crear\s*Nueva$",
    r"^Finalizar$",
    r"^Salir$",
    r"^Exit$",
    r"^Fin$",
    r"^Terminar$",
    r"^🔙\s*Atrás$",
    r"^📋\s*Mostrar\s*Menú$",
    r"^⚙️\s*Ayuda$",
    r"^🛒\s*Shop$",
    r"^🎧\s*Centro\s*de\s*Ayuda$",
    r"^📞\s*Contactar\s*Soporte$",
    r"^❓\s*FAQ$",
    r"^📝\s*Tutoriales$",
    r"^🔧\s*Admin$",
    r"^👤\s*Mi\s*Perfil$",
    r"^⭐\s*VIP$",
    r"^🎯\s*Tareas$",
    r"^📢\s*Anuncios$",
    r"^📣\s*Broadcast$",
]

# Clave para verificar si hay conversación IA activa
AI_CHAT_KEY = 'in_ai_conversation'


class DirectMessageHandler(BaseHandler):
    """Handler para responder mensajes directos del usuario con IA."""

    def __init__(self, ai_support_service):
        """
        Inicializa el handler de mensajes directos.

        Args:
            ai_support_service: Servicio de soporte con IA
        """
        super().__init__(ai_support_service, "AiSupportService")
        self._menu_patterns_compiled = None
        logger.info("📨 DirectMessageHandler inicializado")

    def _compile_patterns(self):
        """Compila los patrones de menú una sola vez."""
        if self._menu_patterns_compiled is None:
            import re
            self._menu_patterns_compiled = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in MENU_BUTTON_PATTERNS
            ]
        return self._menu_patterns_compiled

    def _is_menu_button(self, text: str) -> bool:
        """Verifica si el texto es un botón del menú."""
        patterns = self._compile_patterns()
        return any(pattern.match(text) for pattern in patterns)

    async def handle_direct_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Procesa mensaje directo del usuario.

        Solo responde si:
        1. No es un botón del menú
        2. No hay conversación IA activa en el ConversationHandler
        """
        user_message = update.message.text
        user_id = update.effective_user.id

        # 1. Ignorar botones del menú
        if self._is_menu_button(user_message):
            logger.debug(f"📨 Ignorando botón de menú: '{user_message}'")
            return

        # 2. Verificar si hay conversación IA activa (gestionada por ConversationHandler)
        if context.user_data.get(AI_CHAT_KEY, False):
            logger.debug(f"📨 Usuario {user_id} tiene conversación IA activa, delegando al ConversationHandler")
            return

        logger.info(f"📨 Mensaje directo de usuario {user_id}: '{user_message[:30]}...'")

        try:
            # Mostrar indicador de escritura
            await update.message.chat.send_action(action="typing")

            # Verificar si hay conversación en BD
            conversation = await self.service.get_active_conversation(user_id)

            if not conversation:
                # Iniciar conversación automática
                logger.info(f"📨 Iniciando conversación automática para usuario {user_id}")
                await self.service.start_conversation(
                    user_id=user_id,
                    user_name=update.effective_user.first_name
                )

            # Obtener respuesta de IA
            ai_response = await self.service.send_message(
                user_id=user_id,
                user_message=user_message
            )

            # Enviar respuesta con instrucciones
            await update.message.reply_text(
                f"🌊 **Sip:**\n\n{ai_response}\n\n"
                f"_💡 Escribe 'Finalizar' para terminar o usa /sipai para modo completo_",
                reply_markup=None,  # No mostrar teclado para evitar confusión
                parse_mode="Markdown"
            )

            logger.debug(f"📨 Respuesta automática enviada a usuario {user_id}")

        except ValueError as e:
            logger.warning(f"⚠️ Error en mensaje directo de {user_id}: {e}")
            await update.message.reply_text(
                f"⚠️ {str(e)}",
                reply_markup=None,
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"❌ Error en mensaje directo de {user_id}: {e}")
            await update.message.reply_text(
                "❌ Tuve un problema procesando tu mensaje. Usa /sipai para iniciar el asistente.",
                parse_mode="Markdown"
            )


def get_direct_message_handler(ai_support_service):
    """
    Retorna el handler para mensajes directos.

    IMPORTANTE: Este handler debe registrarse DESPUÉS del ai_support_handler
    para que el ConversationHandler tenga prioridad.
    """
    handler = DirectMessageHandler(ai_support_service)

    return MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handler.handle_direct_message
    )