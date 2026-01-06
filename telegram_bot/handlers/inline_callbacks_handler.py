"""
Handlers para callbacks de teclados inline del bot uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Sistema de teclados inline
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards, InlineAdminKeyboards, get_main_menu_for_user
from telegram_bot.handlers.admin_handler import AdminHandler
from application.services.admin_service import AdminService
from telegram_bot.messages.messages import Messages
from telegram_bot.messages.admin_messages import AdminMessages
from telegram_bot.handlers.key_submenu_handler import get_key_submenu_handler
from config import settings
from utils.logger import logger
from application.services.support_service import SupportService
from application.services.common.container import get_container


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para volver al menú principal."""
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    
    # Determinar si es admin
    is_admin = user.id == int(settings.ADMIN_ID)
    
    await query.edit_message_text(
        text="👇 Menú Principal",
        reply_markup=InlineKeyboards.main_menu(is_admin=is_admin),
        parse_mode="Markdown"
    )

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
            text += f"👑 **Estado VIP:** Activo hasta {user.vip_expires_at.strftime('%d/%m/%Y')}\n"    
        await query.edit_message_text(
            text=text,
            reply_markup=get_main_menu_for_user(user_id),
            parse_mode="Markdown"
        )     
    except Exception as e:
        logger.error(f"Error en status_handler: {e}")
        await query.edit_message_text(
            text=Messages.Errors.GENERIC.format(error=str(e)),
            reply_markup=get_main_menu_for_user(user_id)
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
            reply_markup=get_main_menu_for_user(update.effective_user.id)
        )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mostrar el menú de ayuda."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text=Messages.Help.MENU_TITLE,
        reply_markup=InlineKeyboards.help_menu(),
        parse_mode="Markdown"
    )


async def usage_guide_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mostrar la guía de uso."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text=Messages.Help.USAGE_GUIDE,
        reply_markup=InlineKeyboards.back_button("help"),
        parse_mode="Markdown"
    )


async def configuration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mostrar la guía de configuración."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text=Messages.Help.CONFIGURATION,
        reply_markup=InlineKeyboards.back_button("help"),
        parse_mode="Markdown"
    )


async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mostrar las preguntas frecuentes."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text=Messages.Help.FAQ,
        reply_markup=InlineKeyboards.back_button("help"),
        parse_mode="Markdown"
    )


async def support_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mostrar el menú de soporte desde el centro de ayuda."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🎫 Crear Ticket", callback_data="create_ticket"),
            InlineKeyboardButton("📋 Mis Tickets", callback_data="my_tickets")
        ],
        [
            InlineKeyboardButton("❓ FAQ", callback_data="faq"),
            InlineKeyboardButton("🔙 Volver", callback_data="help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=Messages.Support.MENU_TITLE,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def create_ticket_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, support_service: SupportService):
    """Handler para crear un ticket de soporte desde callback."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    try:
        # Abrir ticket
        await support_service.open_ticket(user_id=user.id, user_name=user.first_name)
        
        # Notificar al Admin
        await context.bot.send_message(
            chat_id=settings.ADMIN_ID,
            text=Messages.Support.NEW_TICKET_ADMIN.format(name=user.first_name, user_id=user.id),
            parse_mode="HTML"
        )
        
        await query.edit_message_text(
            text=Messages.Support.OPEN_TICKET,
            reply_markup=InlineKeyboards.support_active(),
            parse_mode="Markdown"
        )
        
        # Notificar al usuario que puede escribir
        await context.bot.send_message(
            chat_id=user.id,
            text="💬 Ahora puedes escribir tu mensaje y será enviado al equipo de soporte."
        )
        
    except Exception as e:
        logger.error(f"Error al crear ticket desde callback: {e}")
        await query.edit_message_text(
            text=Messages.Errors.GENERIC.format(error="No se pudo abrir el canal de soporte."),
            reply_markup=InlineKeyboards.back_button("support_menu")
        )


async def my_tickets_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, support_service: SupportService):
    """Handler para mostrar los tickets del usuario."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    try:
        # Obtener ticket abierto si existe usando el repositorio del servicio
        open_ticket = await support_service.ticket_repo.get_open_by_user(user_id)
        
        if open_ticket:
            text = "📋 **Mis Tickets**\n"
            text += "━━━━━━━━━━━━\n\n"
            text += f"🎫 **Ticket Activo**\n\n"
            text += f"📅 Creado: {open_ticket.created_at.strftime('%d/%m/%Y %H:%M')}\n"
            if open_ticket.last_message_at:
                text += f"💬 Último mensaje: {open_ticket.last_message_at.strftime('%d/%m/%Y %H:%M')}\n"
            text += f"📊 Estado: {'Abierto' if open_ticket.status == 'open' else 'Cerrado'}\n\n"
            text += "💡 Escribe un mensaje para continuar la conversación."
        else:
            text = "📋 **Mis Tickets**\n"
            text += "━━━━━━━━━━━━\n\n"
            text += "📭 No tienes tickets activos.\n\n"
            text += "💡 Toca **🎫 Crear Ticket** para iniciar una conversación con soporte."
        
        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboards.back_button("support_menu"),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error al obtener tickets: {e}")
        await query.edit_message_text(
            text=Messages.Errors.GENERIC.format(error=str(e)),
            reply_markup=InlineKeyboards.back_button("support_menu")
        )


async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para el menú de administración."""
    query = update.callback_query
    await query.answer()
    
    # Verificar si es admin
    if update.effective_user.id != int(settings.ADMIN_ID):
        await query.edit_message_text(
            text="🚫 **Acceso Denegado**\n\nNo tienes permisos de administración.",
            reply_markup=get_main_menu_for_user(update.effective_user.id)
        )
        return
    
    text = AdminMessages.MAIN_MENU
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineAdminKeyboards.main_menu(),
        parse_mode="Markdown"
    )


async def close_ticket_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, support_service: SupportService):
    """Handler para cerrar un ticket de soporte desde callback."""
    query = update.callback_query
    await query.answer()
     
    user_id = update.effective_user.id
    
    try:
        # Cerrar ticket usando el servicio
        await support_service.close_ticket(user_id)
         
        await query.edit_message_text(
            text=Messages.Support.TICKET_CLOSED,
            reply_markup=InlineKeyboards.main_menu(),
            parse_mode="Markdown"
        )
         
        # Notificar al admin
        await context.bot.send_message(
            chat_id=settings.ADMIN_ID,
            text=f"🎫 Ticket del usuario {user_id} cerrado."
        )
         
    except Exception as e:
        logger.error(f"Error al cerrar ticket desde callback: {e}")
        await query.edit_message_text(
            text=Messages.Errors.GENERIC.format(error="No se pudo cerrar el ticket."),
            reply_markup=InlineKeyboards.support_active()
        )

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para cancelar cualquier operación y volver al menú principal."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Determinar si es admin
    is_admin = user.id == int(settings.ADMIN_ID)
    
    await query.edit_message_text(
        text=Messages.Cancel.CANCEL_MESSAGE,
        reply_markup=InlineKeyboards.main_menu(is_admin=is_admin),
        parse_mode="Markdown"
    )
     
    # Cancelar cualquier conversación en curso
    if context.user_data:
        context.user_data.clear()
        logger.log_bot_event("INFO", f"Datos de usuario limpiados para usuario {user.id}")


# Función para registrar todos los handlers de callbacks inline
def get_inline_callback_handlers(vpn_service=None, achievement_service=None, support_service=None, admin_service=None):
    """Retorna una lista de handlers para callbacks inline."""
    handlers = []
    
    # Obtener support_service del contenedor si no se proporciona
    if support_service is None:
        container = get_container()
        support_service = container.resolve(SupportService)

    # Obtener admin_service si no se proporciona y crear instancia del AdminHandler
    if admin_service is None:
        container = get_container()
        admin_service = container.resolve(AdminService)

    admin_handler_instance = AdminHandler(admin_service)

    # Registrar handlers de administración (para usar desde menús inline)
    handlers.append(CallbackQueryHandler(admin_handler_instance.show_users, pattern="^show_users$"))
    handlers.append(CallbackQueryHandler(admin_handler_instance.show_keys, pattern="^show_keys$"))
    handlers.append(CallbackQueryHandler(admin_handler_instance.confirm_delete_key, pattern="^delete_key_"))
    handlers.append(CallbackQueryHandler(admin_handler_instance.execute_delete_key, pattern="^confirm_delete_"))
    handlers.append(CallbackQueryHandler(admin_handler_instance.show_server_status, pattern="^server_status$"))
    handlers.append(CallbackQueryHandler(admin_handler_instance.back_to_menu, pattern="^admin$"))
    
    # Navegación principal
    handlers.append(CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"))
    # Usar el nuevo sistema de submenús para "my_keys"
    key_submenu_handler = get_key_submenu_handler(vpn_service)
    handlers.append(CallbackQueryHandler(
        lambda u, c: key_submenu_handler.show_key_submenu(u, c), 
        pattern="^my_keys$"
    ))

    handlers.append(CallbackQueryHandler(lambda u, c: status_handler(u, c, vpn_service), pattern="^status$"))
    handlers.append(CallbackQueryHandler(operations_handler, pattern="^operations$"))
    handlers.append(CallbackQueryHandler(lambda u, c: achievements_handler(u, c, achievement_service), pattern="^achievements$"))
    handlers.append(CallbackQueryHandler(help_handler, pattern="^help$"))
       
    # Handlers del centro de ayuda
    handlers.append(CallbackQueryHandler(usage_guide_handler, pattern="^usage_guide$"))
    handlers.append(CallbackQueryHandler(configuration_handler, pattern="^configuration$"))
    handlers.append(CallbackQueryHandler(faq_handler, pattern="^faq$"))
    handlers.append(CallbackQueryHandler(support_menu_handler, pattern="^support_menu$"))
    
    # Handlers de soporte
    handlers.append(CallbackQueryHandler(lambda u, c: create_ticket_handler(u, c, support_service), pattern="^create_ticket$"))
    handlers.append(CallbackQueryHandler(lambda u, c: my_tickets_handler(u, c, support_service), pattern="^my_tickets$"))
    
    handlers.append(CallbackQueryHandler(admin_handler, pattern="^admin$"))
    
    # Añadir handler para cerrar ticket
    handlers.append(CallbackQueryHandler(lambda u, c: close_ticket_handler(u, c, support_service), pattern="^close_ticket$"))
    
    # Añadir handler para cancelar operaciones
    handlers.append(CallbackQueryHandler(cancel_handler, pattern="^cancel$"))
     
    return handlers
