"""
Handlers para callbacks de teclados inline del bot uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Sistema de teclados inline
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes
from telegram_bot.keyboard import UserKeyboards, AdminKeyboards, OperationKeyboards, SupportKeyboards, CommonKeyboards
from telegram_bot.handlers.admin_handler import AdminHandler
from application.services.admin_service import AdminService
from telegram_bot.messages import UserMessages, CommonMessages, OperationMessages, SupportMessages
from telegram_bot.messages.admin_messages import AdminMessages
from telegram_bot.handlers.key_submenu_handler import get_key_submenu_handler
from telegram_bot.handlers.user_task_manager_handler import get_user_task_manager_handlers
from telegram_bot.handlers.user_announcer_handler import get_user_announcer_handlers
from config import settings
from utils.logger import logger
from utils.telegram_utils import TelegramHandlerUtils
from application.services.support_service import SupportService


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para volver al menú principal."""
    query = update.callback_query
    
    # Validar que query no sea None
    if not await TelegramHandlerUtils.validate_callback_query(query, context, update):
        return
        
    await TelegramHandlerUtils.safe_answer_query(query)
    user = update.effective_user
    
    # Determinar si es admin
    is_admin = user.id == int(settings.ADMIN_ID)
    
    await TelegramHandlerUtils.safe_edit_message(
        query,
        context,
        text="👇 Menú Principal",
        reply_markup=UserKeyboards.main_menu(is_admin=is_admin),
        parse_mode="Markdown"
    )

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service):
    """Handler para mostrar el estado del usuario."""
    query = update.callback_query
    
    # Validar que query no sea None
    if not await TelegramHandlerUtils.validate_callback_query(query, context, update):
        return
        
    await TelegramHandlerUtils.safe_answer_query(query)
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
        is_admin = user_id == int(settings.ADMIN_ID)
        await TelegramHandlerUtils.safe_edit_message(
            query,
            context,
            text=text,
            reply_markup=UserKeyboards.main_menu(is_admin=is_admin),
            parse_mode="Markdown"
        )     
    except Exception as e:
        logger.error(f"Error en status_handler: {e}")
        try:
            is_admin = user_id == int(settings.ADMIN_ID)
        except:
            is_admin = False
            
        await TelegramHandlerUtils.safe_edit_message(
            query,
            context,
            text=CommonMessages.Errors.GENERIC.format(error=str(e)),
            reply_markup=UserKeyboards.main_menu(is_admin=is_admin)
        )

async def operations_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service=None):
    """Handler para mostrar el menú de operaciones con botones de roles condicionales."""
    query = update.callback_query
    
    # Validar que query no sea None
    if not await TelegramHandlerUtils.validate_callback_query(query, context, update):
        return
        
    await TelegramHandlerUtils.safe_answer_query(query)
    
    try:
        user_id = update.effective_user.id
        user = None
        
        # Obtener información del usuario si vpn_service está disponible
        if vpn_service:
            try:
                user_status = await vpn_service.get_user_status(user_id)
                user = user_status.get("user")
            except Exception as e:
                logger.warning(f"No se pudo obtener información del usuario {user_id}: {e}")
        
        await TelegramHandlerUtils.safe_edit_message(
            query,
            context,
            text=OperationMessages.Menu.MAIN,
            reply_markup=OperationKeyboards.operations_menu(user=user),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error en operations_handler: {e}")
        await TelegramHandlerUtils.safe_edit_message(
            query,
            context,
            text=CommonMessages.Errors.GENERIC.format(error=str(e)),
            reply_markup=OperationKeyboards.operations_menu()
        )


async def achievements_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, achievement_service):
    """Handler para mostrar el menú de logros."""
    query = update.callback_query
    
    # Validar que query no sea None
    if not await TelegramHandlerUtils.validate_callback_query(query, context, update):
        return
        
    await TelegramHandlerUtils.safe_answer_query(query)
    
    try:
        user_id = update.effective_user.id
        user_achievements = await achievement_service.get_user_summary(user_id)
        
        text = "🏆 **Sistema de Logros**\n\n"
        text += f"📊 **Progreso General:** {user_achievements['completed_achievements']}/{user_achievements['total_achievements']} logros desbloqueados\n"
        text += f"⭐ **Puntos de Logro:** {user_achievements['total_reward_stars']}\n"
        text += f"🎁 **Recompensas Pendientes:** {user_achievements['pending_rewards']}\n\n"
        text += "Selecciona una opción para ver más detalles:"
        
        await TelegramHandlerUtils.safe_edit_message(
            query,
            context,
            text=text,
            reply_markup=OperationKeyboards.achievements_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en achievements_handler: {e}")
        await TelegramHandlerUtils.safe_edit_message(
            query,
            context,
            text=CommonMessages.Errors.GENERIC.format(error=str(e)),
            reply_markup=UserKeyboards.main_menu()
        )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mostrar el menú de ayuda."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text=UserMessages.Help.MAIN_MENU,
        reply_markup=SupportKeyboards.help_menu(),
        parse_mode="Markdown"
    )


async def ai_sip_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, ai_support_service):
    """Handler para iniciar Sip AI desde el menú de ayuda."""
    query = update.callback_query
    await query.answer()
    
    try:
        # Obtener el handler de AI Support
        from telegram_bot.handlers.ai_support_handler import AiSupportHandler
        handler = AiSupportHandler(ai_support_service)
        
        # Iniciar conversación con AI
        result = await handler.start_ai_support_callback(update, context)
        
        return result
    except Exception as e:
        logger.error(f"Error en ai_sip_start_handler: {e}")
        await query.edit_message_text(
            text="❌ No se pudo iniciar el asistente IA. Por favor, intenta más tarde.",
            reply_markup=SupportKeyboards.help_menu(),
            parse_mode="Markdown"
        )
        return None


async def usage_guide_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mostrar la guía de uso."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text=UserMessages.Help.HELP,
        reply_markup=CommonKeyboards.back_button("help"),
        parse_mode="Markdown"
    )


async def configuration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mostrar la guía de configuración."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text=UserMessages.Help.CONFIGURATION,
        reply_markup=CommonKeyboards.back_button("help"),
        parse_mode="Markdown"
    )


async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mostrar las preguntas frecuentes."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text=UserMessages.Help.FAQ,
        reply_markup=CommonKeyboards.back_button("help"),
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
        text=SupportMessages.Tickets.MENU,
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
            text=SupportMessages.Tickets.NEW_TICKET_ADMIN.format(name=user.first_name, user_id=user.id),
            parse_mode="HTML"
        )
        
        await query.edit_message_text(
            text=SupportMessages.Tickets.OPEN_TICKET,
            reply_markup=SupportKeyboards.support_active(),
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
            text=CommonMessages.Errors.GENERIC.format(error="No se pudo abrir el canal de soporte."),
            reply_markup=CommonKeyboards.back_button("support_menu")
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
            reply_markup=CommonKeyboards.back_button("support_menu"),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error al obtener tickets: {e}")
        await query.edit_message_text(
            text=CommonMessages.Errors.GENERIC.format(error=str(e)),
            reply_markup=CommonKeyboards.back_button("support_menu")
        )


async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para el menú de administración."""
    query = update.callback_query
    await query.answer()
    
    # Verificar si es admin
    if update.effective_user.id != int(settings.ADMIN_ID):
        await query.edit_message_text(
            text="🚫 **Acceso Denegado**\n\nNo tienes permisos de administración.",
            reply_markup=UserKeyboards.main_menu()
        )
        return
    
    text = AdminMessages.MAIN_MENU
    
    await query.edit_message_text(
        text=text,
        reply_markup=AdminKeyboards.main_menu(),
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
            text=SupportMessages.Tickets.TICKET_CLOSED,
            reply_markup=UserKeyboards.main_menu(),
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
            text=CommonMessages.Errors.GENERIC.format(error="No se pudo cerrar el ticket."),
            reply_markup=SupportKeyboards.support_active()
        )

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para cancelar cualquier operación y volver al menú principal."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Determinar si es admin
    is_admin = user.id == int(settings.ADMIN_ID)
    
    await query.edit_message_text(
        text=CommonMessages.Navigation.CANCEL,
        reply_markup=UserKeyboards.main_menu(is_admin=is_admin),
        parse_mode="Markdown"
    )
     
    # Cancelar cualquier conversación en curso
    if context.user_data:
        context.user_data.clear()
        logger.log_bot_event("INFO", f"Datos de usuario limpiados para usuario {user.id}")


# Función para registrar todos los handlers de callbacks inline
def get_inline_callback_handlers(vpn_service=None, achievement_service=None, support_service=None, admin_service=None):
    """Retorna una lista de handlers para callbacks inline."""
    from application.services.common.container import get_container
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

    handlers.append(CallbackQueryHandler(lambda u, c: status_handler(u, c, vpn_service), pattern="^status$"))
    handlers.append(CallbackQueryHandler(lambda u, c: operations_handler(u, c, vpn_service), pattern="^operations$"))
    handlers.append(CallbackQueryHandler(lambda u, c: achievements_handler(u, c, achievement_service), pattern="^achievements$"))
    handlers.append(CallbackQueryHandler(help_handler, pattern="^help$"))
       
    # Handlers del centro de ayuda
    handlers.append(CallbackQueryHandler(usage_guide_handler, pattern="^usage_guide$"))
    handlers.append(CallbackQueryHandler(configuration_handler, pattern="^configuration$"))
    handlers.append(CallbackQueryHandler(faq_handler, pattern="^faq$"))
    handlers.append(CallbackQueryHandler(support_menu_handler, pattern="^support_menu$"))
    
    # Handler para iniciar Sip AI desde el menú de ayuda
    handlers.append(CallbackQueryHandler(lambda u, c: ai_sip_start_handler(u, c, ai_support_service), pattern="^ai_sip_start$"))
    
    # Handlers de soporte
    handlers.append(CallbackQueryHandler(lambda u, c: create_ticket_handler(u, c, support_service), pattern="^create_ticket$"))
    handlers.append(CallbackQueryHandler(lambda u, c: my_tickets_handler(u, c, support_service), pattern="^my_tickets$"))
    
    handlers.append(CallbackQueryHandler(admin_handler, pattern="^admin$"))
    
    # Añadir handler para cerrar ticket
    handlers.append(CallbackQueryHandler(lambda u, c: close_ticket_handler(u, c, support_service), pattern="^close_ticket$"))
    
    # Registrar handlers de roles de usuario (Gestor de Tareas y Anunciante)
    try:
        from domain.interfaces.iuser_repository import IUserRepository
        
        container = get_container()
        user_repository = container.resolve(IUserRepository)
        
        # Handlers para Gestor de Tareas
        user_task_handlers = get_user_task_manager_handlers(task_service=None, user_repository=user_repository)
        handlers.extend(user_task_handlers)
        
        # Handlers para Anunciante
        user_announcer_handlers = get_user_announcer_handlers(user_repository=user_repository)
        handlers.extend(user_announcer_handlers)
    except Exception as e:
        logger.warning(f"No se pudieron registrar handlers de roles de usuario: {e}")
    
    # Añadir handler para cancelar operaciones
    handlers.append(CallbackQueryHandler(cancel_handler, pattern="^cancel$"))
     
    return handlers
