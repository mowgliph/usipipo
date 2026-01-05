"""
Handlers para callbacks de teclados inline del bot uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Sistema de teclados inline
"""

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards, InlineAdminKeyboards
from telegram_bot.messages import Messages
from loguru import logger


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para volver al menú principal."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="👇 Menú Principal",
        reply_markup=InlineKeyboards.main_menu(),
        parse_mode="Markdown"
    )





async def create_key_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler DEPRECATED para iniciar el proceso de creación de llave.
    Ahora manejado por el ConversationHandler en crear_llave_handler.py
    """
    # Este handler está obsoleto. El ConversationHandler maneja create_key directamente.
    pass


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service):
    """Handler para mostrar el estado del usuario."""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        user_status = await vpn_service.get_user_status(user_id)
        user = user_status["user"]
        
        text = f"📊 **Estado de tu Cuenta:**\n\n"
        text += f"👤 **Usuario:** {user.full_name or user.username or 'N/A'}\n"
        text += f"⭐ **Balance:** {user.balance_stars} estrellas\n"
        text += f"🔑 **Llaves Activas:** {user_status['keys_count']}\n"
        text += f"📅 **Miembro desde:** {user.created_at.strftime('%d/%m/%Y')}\n"
        
        if user.is_vip:
            text += f"👑 **Estado VIP:** Activo hasta {user.vip_expires.strftime('%d/%m/%Y')}\n"
        
        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboards.main_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en status_handler: {e}")
        await query.edit_message_text(
            text=Messages.Errors.GENERIC.format(error=str(e)),
            reply_markup=InlineKeyboards.main_menu()
        )


async def operations_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mostrar el menú de operaciones."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text=Messages.Operations.MENU_TITLE,
        reply_markup=InlineKeyboards.operations_menu(),
        parse_mode="Markdown"
    )


async def achievements_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, achievement_service):
    """Handler para mostrar el menú de logros."""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        user_achievements = await achievement_service.get_user_summary(user_id)
        
        text = "🏆 **Sistema de Logros**\n\n"
        text += f"📊 **Progreso General:** {user_achievements['completed_achievements']}/{user_achievements['total_achievements']} logros desbloqueados\n"
        text += f"⭐ **Puntos de Logro:** {user_achievements['total_reward_stars']}\n"
        text += f"🎁 **Recompensas Pendientes:** {user_achievements['pending_rewards']}\n\n"
        text += "Selecciona una opción para ver más detalles:"
        
        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboards.achievements_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en achievements_handler: {e}")
        await query.edit_message_text(
            text=Messages.Errors.GENERIC.format(error=str(e)),
            reply_markup=InlineKeyboards.main_menu()
        )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mostrar el menú de ayuda."""
    query = update.callback_query
    await query.answer()
    
    text = "⚙️ **Centro de Ayuda**\n\n"
    text += "¿En qué podemos ayudarte?\n\n"
    text += "Selecciona una opción:"
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboards.help_menu(),
        parse_mode="Markdown"
    )


async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para el menú de administración."""
    query = update.callback_query
    await query.answer()
    
    # Verificar si es admin
    from config import settings
    if update.effective_user.id != int(settings.ADMIN_ID):
        await query.edit_message_text(
            text="🚫 **Acceso Denegado**\n\nNo tienes permisos de administración.",
            reply_markup=InlineKeyboards.main_menu()
        )
        return
    
    text = "🔧 **Panel de Administración**\n\n"
    text += "Selecciona una opción para gestionar el sistema:"
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineAdminKeyboards.main_menu(),
        parse_mode="Markdown"
    )


# Función para registrar todos los handlers de callbacks inline
def get_inline_callback_handlers(vpn_service=None, achievement_service=None):
    """Retorna una lista de handlers para callbacks inline."""
    handlers = []
    
    # Navegación principal
    handlers.append(CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"))
    # DEPRECATED: Handler de llaves básico reemplazado por sistema de submenús
    # handlers.append(CallbackQueryHandler(lambda u, c: my_keys_handler(u, c, vpn_service), pattern="^my_keys$"))
    
    # Usar el nuevo sistema de submenús para "my_keys"
    from telegram_bot.handlers.key_submenu_handler import get_key_submenu_handler
    key_submenu_handler = get_key_submenu_handler(vpn_service)
    handlers.append(CallbackQueryHandler(
        lambda u, c: key_submenu_handler.show_key_submenu(u, c), 
        pattern="^my_keys$"
    ))
    # DEPRECATED: create_key ahora manejado por ConversationHandler en crear_llave_handler.py
    # handlers.append(CallbackQueryHandler(create_key_handler, pattern="^create_key$"))
    handlers.append(CallbackQueryHandler(lambda u, c: status_handler(u, c, vpn_service), pattern="^status$"))
    handlers.append(CallbackQueryHandler(operations_handler, pattern="^operations$"))
    handlers.append(CallbackQueryHandler(lambda u, c: achievements_handler(u, c, achievement_service), pattern="^achievements$"))
    handlers.append(CallbackQueryHandler(help_handler, pattern="^help$"))
    handlers.append(CallbackQueryHandler(admin_handler, pattern="^admin$"))
    
    return handlers
