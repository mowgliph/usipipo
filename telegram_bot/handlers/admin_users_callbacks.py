"""
Manejador de integraciones de callbacks para el submenu de usuarios en administración.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from application.services.admin_service import AdminService
from telegram_bot.handlers.admin_users_handler import AdminUsersHandler
from config import settings
from utils.logger import logger


def create_admin_users_callbacks(admin_service: AdminService) -> list:
    """
    Crea y retorna los CallbackQueryHandlers para la gestión de usuarios.
    
    Args:
        admin_service: Servicio de administración
        
    Returns:
        Lista de CallbackQueryHandlers configurados
    """
    
    admin_users_handler = AdminUsersHandler(admin_service)
    handlers = []
    
    # Submenu de usuarios
    handlers.append(
        CallbackQueryHandler(admin_users_handler.users_submenu, pattern="^admin_users_submenu$")
    )
    
    # Lista de usuarios
    handlers.append(
        CallbackQueryHandler(admin_users_handler.show_users_list, pattern="^admin_users_list$")
    )
    
    # Paginación
    handlers.append(
        CallbackQueryHandler(admin_users_handler.handle_pagination, pattern="^admin_users_page_|^admin_users_list$")
    )
    
    # Detalle de usuario
    handlers.append(
        CallbackQueryHandler(
            lambda u, c: _handle_user_detail(u, c, admin_users_handler),
            pattern="^admin_user_detail|^admin_user_role_|^admin_user_status_|^admin_user_block_|^admin_user_unblock_|^admin_user_delete_|^admin_user_keys_"
        )
    )
    
    # Asignar rol
    handlers.append(
        CallbackQueryHandler(admin_users_handler.assign_role_menu, pattern="^admin_assign_roles$")
    )
    
    handlers.append(
        CallbackQueryHandler(admin_users_handler.handle_role_assignment, pattern="^admin_assign_role_")
    )
    
    # Duración de rol premium
    handlers.append(
        CallbackQueryHandler(admin_users_handler.handle_role_duration, pattern="^admin_role_duration_")
    )
    
    # Bloqueo de usuario
    handlers.append(
        CallbackQueryHandler(admin_users_handler.block_user_confirm, pattern="^admin_block_user$")
    )
    
    handlers.append(
        CallbackQueryHandler(admin_users_handler.execute_block_user, pattern="^admin_confirm_block_")
    )
    
    # Desbloqueo de usuario
    handlers.append(
        CallbackQueryHandler(admin_users_handler.unblock_user_confirm, pattern="^admin_unblock_user$")
    )
    
    handlers.append(
        CallbackQueryHandler(admin_users_handler.execute_unblock_user, pattern="^admin_confirm_unblock_")
    )
    
    # Eliminación de usuario
    handlers.append(
        CallbackQueryHandler(admin_users_handler.delete_user_confirm, pattern="^admin_delete_user$")
    )
    
    # Cambio de estado
    handlers.append(
        CallbackQueryHandler(
            lambda u, c: _handle_change_status(u, c, admin_users_handler),
            pattern="^admin_change_status$"
        )
    )
    
    return handlers


async def _handle_user_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, handler: AdminUsersHandler):
    """Manejador para los diferentes callbacks de detalle de usuario."""
    query = update.callback_query
    callback_data = query.data
    
    try:
        # Extraer user_id del callback
        if "admin_user_role_" in callback_data:
            user_id = int(callback_data.split("_")[-1])
            context.user_data['selected_user_id'] = user_id
            return await handler.assign_role_menu(update, context)
        
        elif "admin_user_status_" in callback_data:
            user_id = int(callback_data.split("_")[-1])
            context.user_data['selected_user_id'] = user_id
            # Mostrar menu de cambio de estado
            await query.answer()
            from telegram_bot.keyboard import AdminKeyboards
            from telegram_bot.messages import AdminMessages
            
            user_info = await handler.admin_service.get_user_by_id(user_id)
            if user_info:
                message = AdminMessages.Users.CHANGE_STATUS_MENU.format(
                    user_name=user_info['full_name'] or user_info['username'],
                    user_id=user_id,
                    current_status=handler._format_status(user_info['status'])
                )
                await query.edit_message_text(
                    text=message,
                    reply_markup=AdminKeyboards.status_selection(),
                    parse_mode="Markdown"
                )
        
        elif "admin_user_block_" in callback_data:
            user_id = int(callback_data.split("_")[-1])
            context.user_data['selected_user_id'] = user_id
            return await handler.block_user_confirm(update, context)
        
        elif "admin_user_unblock_" in callback_data:
            user_id = int(callback_data.split("_")[-1])
            context.user_data['selected_user_id'] = user_id
            return await handler.unblock_user_confirm(update, context)
        
        elif "admin_user_delete_" in callback_data:
            user_id = int(callback_data.split("_")[-1])
            context.user_data['selected_user_id'] = user_id
            return await handler.delete_user_confirm(update, context)
        
        elif "admin_user_keys_" in callback_data:
            user_id = int(callback_data.split("_")[-1])
            # Mostrar claves del usuario
            await query.answer()
            user_keys = await handler.admin_service.get_user_keys(user_id)
            
            from telegram_bot.keyboard import AdminKeyboards
            
            if not user_keys:
                await query.edit_message_text(
                    text="🔑 **Claves del Usuario**\n\nNo tiene claves registradas.",
                    reply_markup=AdminKeyboards.users_submenu()
                )
            else:
                key_list = []
                for key in user_keys[:5]:  # Limitar a 5
                    status = "🟢" if key.is_active else "🔴"
                    key_list.append(f"{status} **{key.key_name}** ({key.key_type})")
                
                message = f"""🔑 **Claves del Usuario** (ID: `{user_id}`)
 
Total: {len(user_keys)} claves
 
{chr(10).join(key_list)}"""
                
                await query.edit_message_text(
                    text=message,
                    reply_markup=AdminKeyboards.users_submenu(),
                    parse_mode="Markdown"
                )
        
        else:
            # Mostrar detalle general
            return await handler.show_user_detail(update, context)
            
    except Exception as e:
        logger.error(f"Error en manejador de detalle de usuario: {e}")
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


async def _handle_change_status(update: Update, context: ContextTypes.DEFAULT_TYPE, handler: AdminUsersHandler):
    """Manejador para cambio de estado de usuario."""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = int(context.user_data.get('selected_user_id', 0))
        if not user_id:
            await query.answer("❌ Usuario no seleccionado", show_alert=True)
            return
        
        user_info = await handler.admin_service.get_user_by_id(user_id)
        if not user_info:
            await query.answer("❌ Usuario no encontrado", show_alert=True)
            return
        
        from telegram_bot.keyboard import AdminKeyboards
        from telegram_bot.messages import AdminMessages
        
        message = AdminMessages.Users.CHANGE_STATUS_MENU.format(
            user_name=user_info['full_name'] or user_info['username'],
            user_id=user_id,
            current_status=handler._format_status(user_info['status'])
        )
        
        await query.edit_message_text(
            text=message,
            reply_markup=AdminKeyboards.status_selection(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error manejando cambio de estado: {e}")
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)
