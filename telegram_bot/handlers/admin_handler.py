"""
Handler de administración para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from config import settings
from utils.logger import logger
from utils.telegram_utils import TelegramHandlerUtils

from application.services.admin_service import AdminService
from telegram_bot.messages import AdminMessages
from telegram_bot.keyboard import AdminKeyboards, UserKeyboards
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
        self.admin_service = admin_service
    
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
    
    async def show_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra lista de usuarios."""
        query = update.callback_query
        
        # Validar que query no sea None
        if not await TelegramHandlerUtils.validate_callback_query(query, context, update):
            return
        
        await TelegramHandlerUtils.safe_answer_query(query)
        
        try:
            users = await self.admin_service.get_all_users()
            
            if not users:
                await query.edit_message_text(
                    text=AdminMessages.Users.NO_USERS,
                    reply_markup=AdminKeyboards.main_menu()
                )
                return ADMIN_MENU
            
            # Formatear mensaje de usuarios
            user_list = []
            for user in users[:10]:  # Limitar a 10 para no sobrecargar
                vip_status = "👑 VIP" if user['is_vip'] else "👤 Regular"
                activity = user['last_activity'].strftime("%d/%m/%Y") if user['last_activity'] else "Nunca"
                
                user_list.append(
                    f"👤 **{user['first_name']}** (ID: `{user['user_id']}`)\n"
                    f"📊 Claves: {user['active_keys']}/{user['total_keys']} | ⭐ {user['stars_balance']}\n"
                    f"{vip_status} | 📅 Última actividad: {activity}\n"
                )
            
            message = AdminMessages.Users.LIST.format(users="\n\n".join(user_list))
            
            await query.edit_message_text(
                text=message,
                reply_markup=AdminKeyboards.users_actions(),
                parse_mode="Markdown"
            )
            return VIEWING_USERS
            
        except Exception as e:
            logger.error(f"Error mostrando usuarios: {e}")
            await query.edit_message_text(
                text=AdminMessages.Errors.GENERIC.format(error=str(e)),
                reply_markup=AdminKeyboards.main_menu()
            )
            return ADMIN_MENU
    
    async def show_keys(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra lista de todas las claves."""
        query = update.callback_query
        
        # Validar que query no sea None
        if not await TelegramHandlerUtils.validate_callback_query(query, context, update):
            return
        
        await TelegramHandlerUtils.safe_answer_query(query)
        
        try:
            keys = await self.admin_service.get_all_keys()
            
            if not keys:
                await query.edit_message_text(
                    text=AdminMessages.Keys.NO_KEYS,
                    reply_markup=AdminKeyboards.main_menu()
                )
                return ADMIN_MENU
            
            # Agrupar claves por tipo
            wg_keys = [k for k in keys if k['key_type'] == 'wireguard']
            ss_keys = [k for k in keys if k['key_type'] == 'outline']
            
            message = AdminMessages.Keys.LIST.format(
                wireguard_count=len(wg_keys),
                outline_count=len(ss_keys)
            )
            
            # Crear teclado inline con claves para eliminar
            keyboard = []
            
            # Agregar claves WireGuard
            if wg_keys:
                keyboard.append([InlineKeyboardButton(f"🔐 WireGuard ({len(wg_keys)})", callback_data="filter_wg")])
                for key in wg_keys[:5]:  # Limitar a 5 por tipo
                    status_emoji = "🟢" if key['is_active'] else "🔴"
                    keyboard.append([
                        InlineKeyboardButton(
                            f"{status_emoji} {key['key_name']} - {key['user_name']}", 
                            callback_data=f"delete_key_{key['key_id']}"
                        )
                    ])
            
            # Agregar claves Outline
            if ss_keys:
                keyboard.append([InlineKeyboardButton(f"🔒 Outline ({len(ss_keys)})", callback_data="filter_ss")])
                for key in ss_keys[:5]:  # Limitar a 5 por tipo
                    status_emoji = "🟢" if key['is_active'] else "🔴"
                    keyboard.append([
                        InlineKeyboardButton(
                            f"{status_emoji} {key['key_name']} - {key['user_name']}", 
                            callback_data=f"delete_key_{key['key_id']}"
                        )
                    ])
            
            keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="admin")])
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return VIEWING_KEYS
            
        except Exception as e:
            logger.error(f"Error mostrando claves: {e}")
            await query.edit_message_text(
                text=AdminMessages.Errors.GENERIC.format(error=str(e)),
                reply_markup=AdminKeyboards.back_to_menu()
            )
            return ADMIN_MENU
    
    async def confirm_delete_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra confirmación para eliminar clave."""
        query = update.callback_query
        
        # Validar que query no sea None
        if not await TelegramHandlerUtils.validate_callback_query(query, context, update):
            return
            
        await TelegramHandlerUtils.safe_answer_query(query)
        
        # Extraer key_id del callback_data
        key_id = query.data.replace("delete_key_", "")
        
        try:
            # Obtener información de la clave
            keys = await self.admin_service.get_all_keys()
            key_info = next((k for k in keys if k['key_id'] == key_id), None)
            
            if not key_info:
                await query.edit_message_text(
                    text=AdminMessages.Keys.NOT_FOUND,
                    reply_markup=AdminKeyboards.main_menu()
                )
                return ADMIN_MENU
            
            # Guardar key_id en context para usar en confirmación
            context.user_data['pending_delete_key'] = key_id
            
            message = AdminMessages.Confirmation.DELETE_KEY.format(
                key_name=key_info['key_name'],
                user_name=key_info['user_name'],
                key_type=key_info['key_type'].upper(),
                data_used=self._format_bytes(key_info['data_used'])
            )
            
            await query.edit_message_text(
                text=message,
                reply_markup=AdminKeyboards.confirm_delete(key_id),
                parse_mode="Markdown"
            )
            return CONFIRMING_DELETE
            
        except Exception as e:
            logger.error(f"Error en confirmación de eliminación: {e}")
            await query.edit_message_text(
                text=AdminMessages.Errors.GENERIC.format(error=str(e)),
                reply_markup=AdminKeyboards.back_to_menu()
            )
            return ADMIN_MENU
    
    async def execute_delete_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ejecuta la eliminación de la clave."""
        query = update.callback_query
        
        # Validar que query no sea None
        if not await TelegramHandlerUtils.validate_callback_query(query, context, update):
            return
            
        await TelegramHandlerUtils.safe_answer_query(query)
        
        key_id = query.data.replace("confirm_delete_", "")
        
        try:
            # Ejecutar eliminación completa
            result = await self.admin_service.delete_user_key_complete(key_id)
            
            if result['success']:
                message = AdminMessages.Confirmation.DELETE_SUCCESS.format(
                    key_id=key_id,
                    key_type=result.get('key_type', 'Unknown'),
                    server_deleted="✅" if result['server_deleted'] else "❌",
                    db_deleted="✅" if result['db_deleted'] else "❌"
                )
                
                # Notificar al usuario si es posible
                await self._notify_user_key_deleted(result.get('user_id'), key_id)
                
            else:
                message = AdminMessages.Errors.DELETE_ERROR.format(
                    key_id=key_id,
                    error=result.get('error', 'Error desconocido')
                )
            
            await query.edit_message_text(
                text=message,
                reply_markup=AdminKeyboards.main_menu(),
                parse_mode="Markdown"
            )
            return ADMIN_MENU
            
        except Exception as e:
            logger.error(f"Error ejecutando eliminación de clave {key_id}: {e}")
            await query.edit_message_text(
                text=AdminMessages.Errors.GENERIC.format(error=str(e)),
                reply_markup=AdminKeyboards.main_menu()
            )
            return ADMIN_MENU
    
    async def show_server_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra estado de los servidores."""
        query = update.callback_query
        
        # Validar que query no sea None
        if not await TelegramHandlerUtils.validate_callback_query(query, context, update):
            return
            
        await TelegramHandlerUtils.safe_answer_query(query)
        
        try:
            status = await self.admin_service.get_server_status()
            
            message = AdminMessages.System.SERVER_STATUS_HEADER
            
            for server_type, server_info in status.items():
                health_emoji = "🟢" if server_info['is_healthy'] else "🔴"
                message += AdminMessages.System.SERVER_STATUS.format(
                    server_type=server_type.upper(),
                    health_emoji=health_emoji,
                    total_keys=server_info['total_keys'],
                    active_keys=server_info['active_keys'],
                    version=server_info.get('version', 'N/A'),
                    error=server_info.get('error_message', 'Ninguno')
                )
            
            await query.edit_message_text(
                text=message,
                reply_markup=AdminKeyboards.main_menu(),
                parse_mode="Markdown"
            )
            return ADMIN_MENU
            
        except Exception as e:
            logger.error(f"Error mostrando estado de servidores: {e}")
            await query.edit_message_text(
                text=AdminMessages.Errors.GENERIC.format(error=str(e)),
                reply_markup=AdminKeyboards.main_menu()
            )
            return ADMIN_MENU
    
    async def back_to_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Vuelve al menú principal de administración."""
        query = update.callback_query
        
        # Validar que query no sea None
        if not await TelegramHandlerUtils.validate_callback_query(query, context, update):
            return
            
        await TelegramHandlerUtils.safe_answer_query(query)
        
        await query.edit_message_text(
            text=AdminMessages.Menu.MAIN,
            reply_markup=AdminKeyboards.main_menu(),
            parse_mode="Markdown"
        )
        return ADMIN_MENU
    
    def _format_bytes(self, bytes_count: int) -> str:
        """Formatea bytes a formato legible."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"
    
    async def _notify_user_key_deleted(self, user_id: int, key_id: str):
        """Notifica al usuario que su clave fue eliminada."""
        try:
            # Aquí se podría enviar una notificación al usuario
            # Por ahora solo logueamos
            logger.info(f"Se debería notificar al usuario {user_id} sobre eliminación de clave {key_id}")
        except Exception as e:
            logger.error(f"Error notificando al usuario {user_id}: {e}")
    
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra estadísticas del bot."""
        query = update.callback_query
        await query.answer()

        from utils.logger import logger
        from datetime import datetime
        
        monitoring = logger.monitoring_handler

        if not monitoring:
            await query.edit_message_text(
                text="⚠️ El sistema de monitorización no está activo.",
                reply_markup=AdminKeyboards.main_menu()
            )
            return ADMIN_MENU

        # Calcular estadísticas
        logs = monitoring.bot_logs
        error_count = sum(1 for log in logs if log['level'] == 'ERROR')
        warning_count = sum(1 for log in logs if log['level'] == 'WARNING')
        info_count = sum(1 for log in logs if log['level'] == 'INFO')
        
        stats_text = (
            f"📊 *Estadísticas del Bot*\n\n"
            f"🔴 *Errores (24h):* {error_count}\n"
            f"🟡 *Advertencias (24h):* {warning_count}\n"
            f"🟢 *Info (24h):* {info_count}\n"
            f"📝 *Total Logs:* {len(logs)}\n\n"
            f"🕐 *Última Actualización:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=AdminKeyboards.main_menu(),
            parse_mode="Markdown"
        )
        return ADMIN_MENU

    def get_handlers(self) -> ConversationHandler:
        """Retorna los handlers de administración."""
        return ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("^🔧 Admin$"), self.admin_menu)
            ],
            states={
                ADMIN_MENU: [
                    CallbackQueryHandler(self.show_users, pattern="^show_users$"),
                    CallbackQueryHandler(self.show_keys, pattern="^show_keys$"),
                    CallbackQueryHandler(self.show_server_status, pattern="^server_status$"),
                    CallbackQueryHandler(self.show_stats, pattern="^stats$"),
                ],
                VIEWING_USERS: [
                    CallbackQueryHandler(self.back_to_menu, pattern="^admin$"),
                ],
                VIEWING_KEYS: [
                    CallbackQueryHandler(self.confirm_delete_key, pattern="^delete_key_"),
                    CallbackQueryHandler(self.back_to_menu, pattern="^admin$"),
                ],
                CONFIRMING_DELETE: [
                    CallbackQueryHandler(self.execute_delete_key, pattern="^confirm_delete_"),
                    CallbackQueryHandler(self.back_to_menu, pattern="^cancel_delete$"),
                ],
            },
            fallbacks=[
                CallbackQueryHandler(self.back_to_menu, pattern="^admin$"),
            ],
            per_message=False,  
            per_chat=True,
            per_user=True,      
        )

@with_spinner(operation_type="loading")
async def admin_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para el comando /admin."""
    user = update.effective_user

    if user.id == int(settings.ADMIN_ID):
        # Mostrar menú de administración
        await update.message.reply_text(
            text=AdminMessages.Menu.MAIN,
            reply_markup=AdminKeyboards.main_menu(),
            parse_mode="Markdown"
        )
    else:
        # Acceso denegado, mostrar menú principal
        await update.message.reply_text(
            "⚠️ Acceso denegado. Función solo para administradores.",
            reply_markup=UserKeyboards.main_menu(is_admin=False),
            parse_mode="Markdown"
        )


def get_admin_handler(admin_service: AdminService) -> ConversationHandler:
    """Función para obtener el handler de administración."""
    handler = AdminHandler(admin_service)
    return handler.get_handlers()
