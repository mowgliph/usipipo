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
from utils.telegram_utils import TelegramHandlerUtils
from utils.spinner import with_spinner

# Estados de la conversación de administración
ADMIN_MENU = 0
VIEWING_USERS = 1
VIEWING_KEYS = 2
DELETING_KEY = 3
CONFIRMING_DELETE = 4


class AdminHandler:
    """Handler para funciones administrativas."""
    
    def __init__(self, admin_service: AdminService):
        """
        Inicializa el handler administrativo.
        
        Args:
            admin_service: Servicio de administración
        """
        self.admin_service = admin_service
        logger.info("🔧 AdminHandler inicializado")

    async def admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú de administración."""
        user = update.effective_user
        
        # Verificar si es admin
        if user.id != int(settings.ADMIN_ID):
            await update.message.reply_text("⚠️ Acceso denegado. Función solo para administradores.")
            return ConversationHandler.END
        
        await update.message.reply_text(
            text=AdminMessages.Menu.MAIN,
            reply_markup=AdminKeyboards.main_menu(),
            parse_mode="Markdown"
        )
        return ADMIN_MENU

    @with_spinner
    async def show_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra lista de usuarios."""
        query = update.callback_query
        await TelegramHandlerUtils.safe_answer_query(query)
        
        try:
            users = await self.admin_service.get_all_users()
            
            if not users:
                message = AdminMessages.Users.NO_USERS
            else:
                message = AdminMessages.Users.HEADER
                for user in users[:20]:  # Limitar a 20 usuarios
                    status = "✅ Activo" if user.is_active else "❌ Inactivo"
                    message += f"\n👤 {user.full_name or user.username or 'N/A'} ({user.id})\n   {status}\n"
                
                if len(users) > 20:
                    message += f"\n... y {len(users) - 20} más usuarios"
            
            await TelegramHandlerUtils.safe_edit_message(
                query, context,
                text=message,
                reply_markup=AdminKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )
            return VIEWING_USERS
            
        except Exception as e:
            logger.error(f"Error en show_users: {e}")
            await TelegramHandlerUtils.safe_edit_message(
                query, context,
                text=AdminMessages.Error.SYSTEM_ERROR,
                reply_markup=AdminKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )
            return ADMIN_MENU

    @with_spinner
    async def show_keys(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra lista de llaves VPN."""
        query = update.callback_query
        await TelegramHandlerUtils.safe_answer_query(query)
        
        try:
            keys = await self.admin_service.get_all_keys()
            
            if not keys:
                message = AdminMessages.Keys.NO_KEYS
            else:
                message = AdminMessages.Keys.HEADER
                for key in keys[:20]:  # Limitar a 20 llaves
                    status = "🟢 Activa" if key.is_active else "🔴 Inactiva"
                    message += f"\n🔑 {key.name} ({key.type.upper()}) - {key.user_id}\n   {status}\n"
                
                if len(keys) > 20:
                    message += f"\n... y {len(keys) - 20} más llaves"
            
            await TelegramHandlerUtils.safe_edit_message(
                query, context,
                text=message,
                reply_markup=AdminKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )
            return VIEWING_KEYS
            
        except Exception as e:
            logger.error(f"Error en show_keys: {e}")
            await TelegramHandlerUtils.safe_edit_message(
                query, context,
                text=AdminMessages.Error.SYSTEM_ERROR,
                reply_markup=AdminKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )
            return ADMIN_MENU

    @with_spinner
    async def show_server_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra estado del servidor."""
        query = update.callback_query
        await TelegramHandlerUtils.safe_answer_query(query)
        
        try:
            stats = await self.admin_service.get_server_stats()
            
            message = AdminMessages.Server.HEADER
            message += f"\n📊 **Usuarios Totales:** {stats.get('total_users', 0)}"
            message += f"\n✅ **Usuarios Activos:** {stats.get('active_users', 0)}"
            message += f"\n🔑 **Llaves Totales:** {stats.get('total_keys', 0)}"
            message += f"\n🟢 **Llaves Activas:** {stats.get('active_keys', 0)}"
            message += f"\n💾 **Uso de Storage:** {stats.get('storage_usage', 'N/A')}"
            message += f"\n📈 **CPU:** {stats.get('cpu_usage', 'N/A')}%"
            message += f"\n🌐 **Red:** {stats.get('network_usage', 'N/A')}"
            
            await TelegramHandlerUtils.safe_edit_message(
                query, context,
                text=message,
                reply_markup=AdminKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )
            return ADMIN_MENU
            
        except Exception as e:
            logger.error(f"Error en show_server_status: {e}")
            await TelegramHandlerUtils.safe_edit_message(
                query, context,
                text=AdminMessages.Error.SYSTEM_ERROR,
                reply_markup=AdminKeyboards.back_to_menu(),
                parse_mode="Markdown"
            )
            return ADMIN_MENU

    async def back_to_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Vuelve al menú principal de administración."""
        query = update.callback_query
        await TelegramHandlerUtils.safe_answer_query(query)
        
        await TelegramHandlerUtils.safe_edit_message(
            query, context,
            text=AdminMessages.Menu.MAIN,
            reply_markup=AdminKeyboards.main_menu(),
            parse_mode="Markdown"
        )
        return ADMIN_MENU

    async def end_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Finaliza la sesión administrativa."""
        if update.message:
            await update.message.reply_text(
                "👋 Sesión administrativa finalizada.",
                reply_markup=AdminKeyboards.back_to_user_menu()
            )
        elif update.callback_query:
            await TelegramHandlerUtils.safe_answer_query(update.callback_query)
            await TelegramHandlerUtils.safe_edit_message(
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
