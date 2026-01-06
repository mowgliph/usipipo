"""
Sistema de Broadcast para el bot uSipipo.
Permite al administrador enviar mensajes masivos a todos los usuarios con soporte para fotos y markdown.

Author: uSipipo Team
Version: 1.0.0
"""

import time
import re
from typing import List, Optional, Dict, Any
from telegram import Update, Message, PhotoSize
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from utils.logger import logger

from config import settings


# Estados de conversación para broadcast
AWAITING_MESSAGE = 1
AWAITING_CONFIRMATION = 2
AWAITING_PHOTO = 3

class BroadcastHandler:
    """Sistema de broadcast para mensajes masivos."""
    
    def __init__(self):

        self.pending_broadcast: Dict[int, Dict[str, Any]] = {}
        
    def is_admin(self, user_id: int) -> bool:
        """Verifica si el usuario es administrador."""
        return user_id == settings.ADMIN_ID
    
    async def start_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el proceso de broadcast."""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ Comando no autorizado")
            return ConversationHandler.END
        
        # Limpiar broadcast pendiente anterior si existe
        if user_id in self.pending_broadcast:
            del self.pending_broadcast[user_id]
        
        # Iniciar nueva conversación
        self.pending_broadcast[user_id] = {
            'message': None,
            'photo': None,
            'caption': None
        }
        
        await update.message.reply_text(
            "📢 **Sistema de Broadcast**\n\n"
            "Por favor, envíame el contenido del broadcast:\n\n"
            "• Puedes enviar texto con formato *Markdown*\n"
            "• Puedes enviar una foto con caption\n"
            "• Usa /cancel para cancelar\n\n"
            "¿Qué deseas enviar?",
            parse_mode="Markdown"
        )
        
        return AWAITING_MESSAGE
    
    async def receive_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Recibe el mensaje de texto para el broadcast."""
        user_id = update.effective_user.id
        
        if user_id not in self.pending_broadcast:
            return ConversationHandler.END
        
        message_text = update.message.text
        
        # Guardar mensaje
        self.pending_broadcast[user_id]['message'] = message_text
        self.pending_broadcast[user_id]['caption'] = message_text
        
        # Mostrar preview y confirmación
        preview = f"📋 **Preview del Broadcast:**\n\n{message_text}\n\n"
        preview += "📸 ¿Quieres añadir una foto? (Envía una foto o escribe 'no')"
        
        await update.message.reply_text(
            preview,
            parse_mode="Markdown"
        )
        
        return AWAITING_PHOTO
    
    async def receive_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Recibe la foto para el broadcast."""
        user_id = update.effective_user.id
        
        if user_id not in self.pending_broadcast:
            return ConversationHandler.END
        
        # Si el usuario dice "no", pasar directamente a confirmación
        if update.message.text and update.message.text.lower() == 'no':
            await self._show_confirmation(update, user_id)
            return AWAITING_CONFIRMATION
        
        # Procesar foto
        photo = update.message.photo
        if photo:
            # Obtener la foto de mayor resolución
            largest_photo = max(photo, key=lambda p: p.file_size)
            self.pending_broadcast[user_id]['photo'] = largest_photo
            
            # Si hay caption, usarlo como mensaje
            if update.message.caption:
                self.pending_broadcast[user_id]['caption'] = update.message.caption
            
            await self._show_confirmation(update, user_id)
            return AWAITING_CONFIRMATION
        
        # Si no es ni "no" ni una foto, pedir de nuevo
        await update.message.reply_text(
            "❌ Por favor envía una foto o escribe 'no' para continuar sin foto."
        )
        
        return AWAITING_PHOTO
    
    async def _show_confirmation(self, update: Update, user_id: int):
        """Muestra la confirmación del broadcast."""
        broadcast_data = self.pending_broadcast[user_id]
        
        if broadcast_data['photo']:
            # Enviar preview con foto
            await update.message.reply_photo(
                photo=broadcast_data['photo'],
                caption=f"📋 **Preview del Broadcast:**\n\n{broadcast_data['caption']}\n\n"
                        "✅ ¿Confirmar envío a todos los usuarios?\n"
                        "❌ Usa /cancel para cancelar",
                parse_mode="Markdown"
            )
        else:
            # Enviar preview de texto
            await update.message.reply_text(
                f"📋 **Preview del Broadcast:**\n\n{broadcast_data['message']}\n\n"
                "✅ ¿Confirmar envío a todos los usuarios?\n"
                "❌ Usa /cancel para cancelar",
                parse_mode="Markdown"
            )
    
    async def confirm_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirma y envía el broadcast a todos los usuarios."""
        user_id = update.effective_user.id
        
        if user_id not in self.pending_broadcast:
            return ConversationHandler.END
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ Comando no autorizado")
            return ConversationHandler.END
        
        broadcast_data = self.pending_broadcast[user_id]
        
        # Obtener lista de usuarios autorizados
        authorized_users = settings.AUTHORIZED_USERS
        
        if not authorized_users:
            await update.message.reply_text("⚠️ No hay usuarios registrados para enviar el broadcast.")
            del self.pending_broadcast[user_id]
            return ConversationHandler.END
        
        # Enviar broadcast
        await update.message.reply_text(
            f"🚀 **Enviando broadcast a {len(authorized_users)} usuarios...**\n"
            f"⏳ Por favor, espera...",
            parse_mode="Markdown"
        )
        
        success_count = 0
        error_count = 0
        
        for user_id_target in authorized_users:
            try:
                if broadcast_data['photo']:
                    # Enviar con foto
                    await context.bot.send_photo(
                        chat_id=user_id_target,
                        photo=broadcast_data['photo'],
                        caption=broadcast_data['caption'],
                        parse_mode="Markdown"
                    )
                else:
                    # Enviar solo texto
                    await context.bot.send_message(
                        chat_id=user_id_target,
                        text=broadcast_data['message'],
                        parse_mode="Markdown"
                    )
                success_count += 1
                
                # Pequeña pausa para evitar rate limiting
                
                time.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                self.bot_logger.log_error(e, f"Error enviando broadcast a usuario {user_id_target}")
        
        # Resumen del envío
        summary = f"""📊 **Resumen del Broadcast:**

✅ **Enviados exitosamente:** {success_count}
❌ **Errores:** {error_count}
👥 **Total usuarios:** {len(authorized_users)}

📝 **Mensaje:** {broadcast_data['caption'] if broadcast_data['photo'] else broadcast_data['message'][:50]}{'...' if len(broadcast_data['message']) > 50 else ''}"""
        
        await update.message.reply_text(summary, parse_mode="Markdown")
        
        # Limpiar datos
        del self.pending_broadcast[user_id]
        
        # Log del evento
        self.bot_logger.log_bot_event(
            "INFO", 
            f"Broadcast enviado: {success_count} exitosos, {error_count} errores",
            user_id
        )
        
        return ConversationHandler.END
    
    async def cancel_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancela el proceso de broadcast."""
        user_id = update.effective_user.id
        
        if user_id in self.pending_broadcast:
            del self.pending_broadcast[user_id]
        
        await update.message.reply_text("❌ **Broadcast cancelado**")
        
        return ConversationHandler.END
    
    def get_handlers(self):
        """Retorna los handlers de broadcast."""
        return ConversationHandler(
            entry_points=[CommandHandler("broadcast", self.start_broadcast)],
            states={
                AWAITING_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_message)
                ],
                AWAITING_PHOTO: [
                    MessageHandler(filters.PHOTO, self.receive_photo),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_photo)
                ],
                AWAITING_CONFIRMATION: [
                    MessageHandler(filters.Regex(r"^(✅|confirmar|si|ok|Confirmar|SI|OK)$"), self.confirm_broadcast),
                    CommandHandler("confirm", self.confirm_broadcast)
                ]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_broadcast)],
            per_message=False
        )


def get_broadcast_handler():
    """Función para obtener el handler de broadcast."""
    handler = BroadcastHandler()
    return handler.get_handlers()
