"""
Handlers para panel administrativo de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, CommandHandler
from application.services.admin_service import AdminService
from .messages_admin import AdminMessages
from .keyboards_admin import AdminKeyboards
from config import settings
from utils.logger import logger
from utils.spinner import admin_spinner_callback, SpinnerManager, with_spinner
from telegram_bot.common.base_handler import BaseConversationHandler
from datetime import datetime
from pathlib import Path

# Estados de la conversación de administración
ADMIN_MENU = 0
VIEWING_USERS = 1
VIEWING_KEYS = 2
DELETING_KEY = 3
CONFIRMING_DELETE = 4


class AdminHandler(BaseConversationHandler):
    """Handler para funciones administrativas."""

    def __init__(self, admin_service: AdminService):
        """
        Inicializa el handler administrativo.

        Args:
            admin_service: Servicio de administración
        """
        super().__init__(admin_service, "AdminService")
        logger.info("🔧 AdminHandler inicializado")

    async def admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú de administración."""
        user = update.effective_user
        admin_id = user.id

        # Verificar si es admin
        if admin_id != int(settings.ADMIN_ID):
            await self._reply_message(update, "⚠️ Acceso denegado. Función solo para administradores.", parse_mode="Markdown")
            return ConversationHandler.END

        await self._reply_message(
            update,
            text=AdminMessages.Menu.MAIN,
            reply_markup=AdminKeyboards.main_menu(),
            parse_mode="Markdown"
        )
        return ADMIN_MENU

    @admin_spinner_callback
    async def show_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE, spinner_message_id: int = None):
        """Muestra lista de usuarios."""
        query = update.callback_query
        await self._safe_answer_query(query)
        admin_id = update.effective_user.id

        try:
            users = await self.service.get_all_users(current_user_id=admin_id)

            if not users:
                message = AdminMessages.Users.NO_USERS
            else:
                message = AdminMessages.Users.HEADER
                for user in users[:20]:  # Limitar a 20 usuarios
                    status = "✅ Activo" if user.is_active else "❌ Inactivo"
                    message += f"\n👤 {user.full_name or user.username or 'N/A'} ({user.id})\n   {status}\n"

                if len(users) > 20:
                    message += f"\n... y {len(users) - 20} más usuarios"

            # Reemplazar spinner con el mensaje final
            await SpinnerManager.replace_spinner_with_message(
                update, context, spinner_message_id,
                text=message,
                reply_markup=AdminKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )
            return VIEWING_USERS

        except Exception as e:
            await self._handle_error(update, context, e, "show_users")
            return ADMIN_MENU

    @admin_spinner_callback
    async def show_keys(self, update: Update, context: ContextTypes.DEFAULT_TYPE, spinner_message_id: int = None):
        """Muestra lista de llaves VPN."""
        query = update.callback_query
        await self._safe_answer_query(query)
        admin_id = update.effective_user.id

        try:
            keys = await self.service.get_all_keys(current_user_id=admin_id)

            if not keys:
                message = AdminMessages.Keys.NO_KEYS
            else:
                message = AdminMessages.Keys.HEADER
                for key in keys[:20]:  # Limitar a 20 llaves
                    status = "✅ Activa" if key.is_active else "❌ Inactiva"
                    message += f"\n🔑 {key.key_name or 'N/A'} ({key.user_id})\n   {status}\n"

                if len(keys) > 20:
                    message += f"\n... y {len(keys) - 20} más llaves"

            # Reemplazar spinner con el mensaje final
            await SpinnerManager.replace_spinner_with_message(
                update, context, spinner_message_id,
                text=message,
                reply_markup=AdminKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )
            return VIEWING_KEYS

        except Exception as e:
            await self._handle_error(update, context, e, "show_keys")
            return ADMIN_MENU

    @admin_spinner_callback
    async def show_server_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE, spinner_message_id: int = None):
        """Muestra estado del servidor."""
        query = update.callback_query
        await self._safe_answer_query(query)
        admin_id = update.effective_user.id

        try:
            stats = await self.service.get_server_stats(current_user_id=admin_id)

            message = AdminMessages.Server.HEADER
            message += f"\n📊 **Usuarios Totales:** {stats.get('total_users', 0)}"
            message += f"\n✅ **Usuarios Activos:** {stats.get('active_users', 0)}"
            message += f"\n🔑 **Llaves Totales:** {stats.get('total_keys', 0)}"
            message += f"\n🟢 **Llaves Activas:** {stats.get('active_keys', 0)}"
            message += f"\n💾 **Uso de Storage:** {stats.get('storage_usage', 'N/A')}"
            message += f"\n📈 **CPU:** {stats.get('cpu_usage', 'N/A')}%"
            message += f"\n🌐 **Red:** {stats.get('network_usage', 'N/A')}"

            # Reemplazar spinner con el mensaje final
            await SpinnerManager.replace_spinner_with_message(
                update, context, spinner_message_id,
                text=message,
                reply_markup=AdminKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )
            return ADMIN_MENU

        except Exception as e:
            await self._handle_error(update, context, e, "show_server_status")
            return ADMIN_MENU

    @with_spinner()
    async def logs_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra los logs del sistema."""
        user = update.effective_user
        admin_id = user.id

        # Verificar si es admin
        if admin_id != int(settings.ADMIN_ID):
            await self._reply_message(update, AdminMessages.Error.ACCESS_DENIED, parse_mode="Markdown")
            return ConversationHandler.END

        try:
            # Obtener logs usando el logger
            logs_content = logger.get_last_logs(lines=20)
            
            # Si hay error o no hay logs
            if "Error leyendo logs:" in logs_content or "El archivo de log aún no existe" in logs_content:
                message = AdminMessages.Logs.NO_LOGS
            else:
                # Formatear logs para mostrar
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = AdminMessages.Logs.LOGS_DISPLAY.format(
                    logs_content=logs_content[-3000:],  # Limitar para evitar mensaje muy largo
                    timestamp=timestamp
                )

            if update.message:
                await self._reply_message(update, message, parse_mode="Markdown")
            elif update.callback_query:
                await self._safe_answer_query(update.callback_query)
                await self._safe_edit_message(
                    update.callback_query, context,
                    text=message,
                    reply_markup=AdminKeyboards.back_to_menu(),
                    parse_mode="Markdown"
                )
            return ADMIN_MENU

        except Exception as e:
            error_message = AdminMessages.Logs.LOGS_ERROR.format(error=str(e))
            if update.message:
                await self._reply_message(update, error_message, parse_mode="Markdown")
            elif update.callback_query:
                await self._safe_answer_query(update.callback_query)
                await self._safe_edit_message(
                    update.callback_query, context,
                    text=error_message,
                    reply_markup=AdminKeyboards.back_to_menu(),
                    parse_mode="Markdown"
                )
            return ADMIN_MENU

    async def back_to_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Vuelve al menú principal de administración."""
        query = update.callback_query
        await self._safe_answer_query(query)

        await self._safe_edit_message(
            query, context,
            text=AdminMessages.Menu.MAIN,
            reply_markup=AdminKeyboards.main_menu(),
            parse_mode="Markdown"
        )
        return ADMIN_MENU

    async def end_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Finaliza la sesión administrativa."""
        if update.message:
            await self._reply_message(update, "👋 Sesión administrativa finalizada.", reply_markup=AdminKeyboards.back_to_user_menu())
        elif update.callback_query:
            await self._handle_callback_query(update, context)
            await self._safe_edit_message(
                update.callback_query, context,
                text="👋 Sesión administrativa finalizada.",
                reply_markup=AdminKeyboards.back_to_user_menu()
            )
        return ConversationHandler.END


def get_admin_handlers(admin_service: AdminService):
    """
    Retorna los handlers administrativos.
    
    Args:
        admin_service: Servicio de administración
        
    Returns:
        list: Lista de handlers
    """
    handler = AdminHandler(admin_service)
    
    return [
        CommandHandler("admin", handler.admin_menu),
        CommandHandler("logs", handler.logs_handler),
    ]


def get_admin_callback_handlers(admin_service: AdminService):
    """
    Retorna los handlers de callbacks para administración.
    
    Args:
        admin_service: Servicio de administración
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = AdminHandler(admin_service)
    
    return [
        CallbackQueryHandler(handler.show_users, pattern="^show_users$"),
        CallbackQueryHandler(handler.show_keys, pattern="^show_keys$"),
        CallbackQueryHandler(handler.show_server_status, pattern="^server_status$"),
        CallbackQueryHandler(handler.logs_handler, pattern="^logs$"),
        CallbackQueryHandler(handler.back_to_menu, pattern="^admin$"),
        CallbackQueryHandler(handler.end_admin, pattern="^end_admin$"),
    ]


def get_admin_conversation_handler(admin_service: AdminService) -> ConversationHandler:
    """
    Retorna el ConversationHandler para administración.
    
    Args:
        admin_service: Servicio de administración
        
    Returns:
        ConversationHandler: Handler configurado
    """
    handler = AdminHandler(admin_service)
    
    return ConversationHandler(
        entry_points=[CommandHandler("admin", handler.admin_menu)],
        states={
            ADMIN_MENU: [
                CallbackQueryHandler(handler.show_users, pattern="^show_users$"),
                CallbackQueryHandler(handler.show_keys, pattern="^show_keys$"),
                CallbackQueryHandler(handler.show_server_status, pattern="^server_status$"),
                CallbackQueryHandler(handler.logs_handler, pattern="^logs$"),
                CallbackQueryHandler(handler.end_admin, pattern="^end_admin$"),
            ],
            VIEWING_USERS: [
                CallbackQueryHandler(handler.back_to_menu, pattern="^admin$"),
                CallbackQueryHandler(handler.end_admin, pattern="^end_admin$"),
            ],
            VIEWING_KEYS: [
                CallbackQueryHandler(handler.back_to_menu, pattern="^admin$"),
                CallbackQueryHandler(handler.end_admin, pattern="^end_admin$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handler.end_admin),
            CallbackQueryHandler(handler.end_admin, pattern="^end_admin$"),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )
