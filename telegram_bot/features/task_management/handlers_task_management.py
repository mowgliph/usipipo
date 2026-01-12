"""
Handlers para sistema de gestión de tareas de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler, CommandHandler, ConversationHandler
from application.services.task_service import TaskService
from application.services.vpn_service import VpnService
from .messages_task_management import TaskManagementMessages
from .keyboards_task_management import TaskManagementKeyboards
from utils.logger import logger

# Estados de conversación
TASK_MENU = 0
CREATING_TASK = 1
ASSIGNING_TASK = 2
TASK_DETAILS = 3
EDITING_TASK = 4


class TaskManagementHandler:
    """Handler para sistema de gestión de tareas."""
    
    def __init__(self, task_service: TaskService, vpn_service: VpnService = None):
        """
        Inicializa el handler de gestión de tareas.
        
        Args:
            task_service: Servicio de tareas
            vpn_service: Servicio de VPN (opcional)
        """
        self.task_service = task_service
        self.vpn_service = vpn_service
        logger.info("📋 TaskManagementHandler inicializado")

    async def show_task_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el menú principal de gestión de tareas.
        """
        query = update.callback_query
        
        if query:
            await query.answer()
            user_id = update.effective_user.id
        else:
            user_id = update.effective_user.id
        
        try:
            # Verificar si el usuario tiene rol premium
            has_premium_role = await self._check_premium_role(user_id)
            
            if not has_premium_role:
                message = TaskManagementMessages.Error.PREMIUM_REQUIRED
                keyboard = TaskManagementKeyboards.upgrade_to_premium()
            else:
                # Obtener estadísticas de tareas
                stats = await self.task_service.get_user_task_stats(user_id)
                
                message = TaskManagementMessages.Menu.MAIN.format(
                    total_tasks=stats.get('total_tasks', 0),
                    pending_tasks=stats.get('pending_tasks', 0),
                    completed_tasks=stats.get('completed_tasks', 0),
                    in_progress=stats.get('in_progress', 0)
                )
                keyboard = TaskManagementKeyboards.main_menu()
            
            if query:
                await query.edit_message_text(
                    text=message,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    text=message,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            
            return TASK_MENU
            
        except Exception as e:
            logger.error(f"Error en show_task_menu: {e}")
            await self._show_error(update, context)
            return ConversationHandler.END

    async def create_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el formulario para crear una tarea.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            message = TaskManagementMessages.Create.FORM
            keyboard = TaskManagementKeyboards.create_task_form()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            return CREATING_TASK
            
        except Exception as e:
            logger.error(f"Error en create_task: {e}")
            await query.edit_message_text(
                text=TaskManagementMessages.Error.SYSTEM_ERROR,
                reply_markup=TaskManagementKeyboards.back_to_tasks(),
                parse_mode="Markdown"
            )
            return TASK_MENU

    async def show_task_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra la lista de tareas del usuario.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Obtener tareas del usuario
            tasks = await self.task_service.get_user_tasks(user_id)
            
            if not tasks:
                message = TaskManagementMessages.List.NO_TASKS
                keyboard = TaskManagementKeyboards.back_to_tasks()
            else:
                message = TaskManagementMessages.List.HEADER
                
                for task in tasks[:10]:  # Mostrar solo primeros 10
                    status = "✅" if task.status == "completed" else "⏳" if task.status == "pending" else "🔄"
                    priority = "🔴 Alta" if task.priority == "high" else "🟡 Media" if task.priority == "medium" else "🟢 Baja"
                    message += f"\n{status} {priority} {task.title}\n"
                    message += f"   📅 {task.due_date}\n"
                    message += f"   👥 Asignado a: {task.assigned_to or 'Sin asignar'}\n"
                
                if len(tasks) > 10:
                    message += f"\n📊 ... y {len(tasks) - 10} más"
                
                keyboard = TaskManagementKeyboards.list_actions(len(tasks))
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_task_list: {e}")
            await query.edit_message_text(
                text=TaskManagementMessages.Error.SYSTEM_ERROR,
                reply_markup=TaskManagementKeyboards.back_to_tasks(),
                parse_mode="Markdown"
            )

    async def show_task_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra detalles de una tarea específica.
        """
        query = update.callback_query
        await query.answer()
        
        task_id = int(query.data.split("_")[-1])
        user_id = update.effective_user.id
        
        try:
            task = await self.task_service.get_task_by_id(task_id)
            
            if not task or task.user_id != user_id:
                message = TaskManagementMessages.Error.TASK_NOT_FOUND
                keyboard = TaskManagementKeyboards.back_to_tasks()
            else:
                status = "✅ Completada" if task.status == "completed" else "⏳ Pendiente" if task.status == "pending" else "🔄 En Progreso"
                priority = "🔴 Alta" if task.priority == "high" else "🟡 Media" if task.priority == "medium" else "🟢 Baja"
                
                message = TaskManagementMessages.Details.TASK_DETAILS.format(
                    title=task.title,
                    description=task.description,
                    status=status,
                    priority=priority,
                    created_at=task.created_at.strftime("%d/%m/%Y %H:%M"),
                    due_date=task.due_date.strftime("%d/%m/%Y %H:%M") if task.due_date else "Sin fecha límite",
                    assigned_to=task.assigned_to or "Sin asignar",
                    progress=f"{task.progress}%",
                    tags=task.tags
                )
                
                keyboard = TaskManagementKeyboards.task_actions(task_id, task.status)
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_task_details: {e}")
            await query.edit_message_text(
                text=TaskManagementMessages.Error.SYSTEM_ERROR,
                reply_markup=TaskManagementKeyboards.back_to_tasks(),
                parse_mode="Markdown"
            )

    async def assign_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Asigna una tarea a un usuario.
        """
        query = update.callback_query
        await query.answer()
        
        task_id = int(query.data.split("_")[-1])
        user_id = update.effective_user.id
        
        try:
            # Obtener lista de usuarios disponibles para asignación
            available_users = await self.task_service.get_available_users_for_assignment(user_id)
            
            if not available_users:
                message = TaskManagementMessages.Assignment.NO_USERS_AVAILABLE
                keyboard = TaskManagementKeyboards.back_to_task_details(task_id)
            else:
                message = TaskManagementMessages.Assignment.SELECT_USER.format(
                    task_title=await self.task_service.get_task_title(task_id)
                )
                
                keyboard = []
                for user in available_users:
                    keyboard.append([
                        InlineKeyboardButton(
                            f"👤 {user.username or 'Usuario ' + str(user.telegram_id)}",
                            callback_data=f"assign_to_{task_id}_{user.telegram_id}"
                        )
                    ])
                
                keyboard.append([
                    InlineKeyboardButton("🔙 Volver", callback_data=f"back_to_task_{task_id}")
                ])
                
                keyboard = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en assign_task: {e}")
            await query.edit_message_text(
                text=TaskManagementMessages.Error.SYSTEM_ERROR,
                reply_markup=TaskManagementKeyboards.back_to_tasks(),
                parse_mode="Markdown"
            )

    async def confirm_assignment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Confirma la asignación de una tarea.
        """
        query = update.callback_query
        await query.answer()
        
        callback_parts = query.data.split("_")
        task_id = int(callback_parts[2])
        assigned_user_id = int(callback_parts[3])
        admin_id = update.effective_user.id
        
        try:
            # Asignar tarea
            result = await self.task_service.assign_task(task_id, assigned_user_id, admin_id)
            
            if result['success']:
                message = TaskManagementMessages.Assignment.ASSIGNMENT_SUCCESS.format(
                    task_title=result['task_title'],
                    assigned_user=result['assigned_user'],
                    task_id=task_id
                )
                keyboard = TaskManagementKeyboards.assignment_success()
            else:
                message = TaskManagementMessages.Error.ASSIGNMENT_FAILED.format(
                    error=result.get('error', 'Unknown error')
                )
                keyboard = TaskManagementKeys.back_to_task_details(task_id)
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en confirm_assignment: {e}")
            await query.edit_message_text(
                text=TaskManagementMessages.Error.SYSTEM_ERROR,
                reply_markup=TaskManagementKeyboards.back_to_tasks(),
                parse_mode="Markdown"
            )

    async def update_task_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Actualiza el estado de una tarea.
        """
        query = update.callback_query
        await query.answer()
        
        callback_parts = query.data.split("_")
        task_id = int(callback_parts[2])
        new_status = callback_parts[3]
        user_id = update.effective_user.id
        
        try:
            # Actualizar estado
            result = await self.task_service.update_task_status(task_id, new_status, user_id)
            
            if result['success']:
                message = TaskManagementMessages.Status.UPDATE_SUCCESS.format(
                    task_title=result['task_title'],
                    old_status=result['old_status'],
                    new_status=result['new_status'],
                    task_id=task_id
                )
                keyboard = TaskManagementKeyboards.status_updated()
            else:
                message = TaskManagementMessages.Error.STATUS_UPDATE_FAILED.format(
                    error=result.get('error', 'Unknown error')
                )
                keyboard = TaskManagementKeyboards.back_to_task_details(task_id)
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en update_task_status: {e}")
            await query.edit_message_text(
                text=TaskManagementMessages.Error.SYSTEM_ERROR,
                reply_markup=TaskManagementKeyboards.back_to_tasks(),
                parse_mode="Markdown"
            )

    async def show_task_calendar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el calendario de tareas.
        """
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        try:
            # Obtener calendario de tareas
            calendar = await self.task_service.get_user_task_calendar(user_id)
            
            message = TaskManagementMessages.Calendar.CALENDAR_HEADER
            
            for date, tasks in calendar.items():
                date_str = date.strftime("%d/%m/%Y")
                message += f"\n\n📅 {date_str}\n"
                
                for task in tasks:
                    status = "✅" if task.status == "completed" else "⏳" if task.status == "pending" else "🔄"
                    priority = "🔴" if task.priority == "high" else "🟡" if task.priority == "medium" else "🟢"
                    message += f"  {status} {priority} {task.title}\n"
            
            keyboard = TaskManagementKeyboards.calendar_actions()
            
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_task_calendar: {e}")
            await query.edit_message_text(
                text=TaskManagementMessages.Error.SYSTEM_ERROR,
                reply_markup=TaskManagementKeyboards.back_to_tasks(),
                parse_mode="Markdown"
            )

    # Métodos privados
    async def _check_premium_role(self, user_id: int) -> bool:
        """Verifica si el usuario tiene rol premium."""
        try:
            # Aquí iría la lógica real para verificar rol premium
            # Por ahora, simulamos la verificación
            if self.vpn_service:
                user_status = await self.vpn_service.get_user_status(user_id)
                user = user_status.get("user")
                return user.has_premium_role if user else False
            return False
        except Exception as e:
            logger.error(f"Error verificando rol premium: {e}")
            return False

    async def _show_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra error genérico."""
        message = TaskManagementMessages.Error.SYSTEM_ERROR
        keyboard = TaskManagementKeyboards.back_to_operations()
        
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )


def get_task_management_handlers(task_service: TaskService, vpn_service: VpnService = None):
    """
    Retorna los handlers de gestión de tareas.
    
    Args:
        task_service: Servicio de tareas
        vpn_service: (opcional) Servicio de VPN
        
    Returns:
        list: Lista de handlers
    """
    handler = TaskManagementHandler(task_service, vpn_service)
    
    return [
        MessageHandler(filters.Regex("^📋 Tareas$"), handler.show_task_menu),
        CommandHandler("tasks", handler.show_task_menu),
    ]


def get_task_management_callback_handlers(task_service: TaskService, vpn_service: VpnService = None):
    """
    Retorna los handlers de callbacks de gestión de tareas.
    
    Args:
        task_service: Servicio de tareas
        vpn_service: (opcional) Servicio de VPN
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = TaskManagementHandler(task_service, vpn_service)
    
    return [
        CallbackQueryHandler(handler.create_task, pattern="^create_task$"),
        CallbackQueryHandler(handler.show_task_list, pattern="^task_list$"),
        CallbackQueryHandler(handler.show_task_details, pattern="^task_details_"),
        CallbackQueryHandler(handler.assign_task, pattern="^assign_task_"),
        CallbackQueryHandler(handler.confirm_assignment, pattern="^confirm_assignment_"),
        CallbackQueryHandler(handler.update_task_status, pattern="^update_status_"),
        CallbackQueryHandler(handler.show_task_calendar, pattern="^task_calendar$"),
    ]


def get_task_management_conversation_handler(task_service: TaskService, vpn_service: VpnService = None) -> ConversationHandler:
    """
    Retorna el ConversationHandler para gestión de tareas.
    
    Args:
        task_service: Servicio de tareas
        vpn_service: (opcional) Servicio de VPN
        
    Returns:
        ConversationHandler: Handler configurado
    """
    handler = TaskManagementHandler(task_service, vpn_service)
    
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📋 Tareas$"), handler.show_task_menu),
            CommandHandler("tasks", handler.show_task_menu),
        ],
        states={
            TASK_MENU: [
                CallbackQueryHandler(handler.create_task, pattern="^create_task$"),
                CallbackQueryHandler(handler.show_task_list, pattern="^task_list$"),
                CallbackQueryHandler(handler.show_task_calendar, pattern="^task_calendar$"),
                CallbackQueryHandler(handler.back_to_operations, pattern="^back_to_operations$"),
            ],
            CREATING_TASK: [
                CallbackQueryHandler(handler.back_to_tasks, pattern="^back_to_tasks$"),
            ],
            ASSIGNING_TASK: [
                CallbackQueryHandler(handler.confirm_assignment, pattern="^confirm_assignment_"),
                CallbackQueryHandler(handler.back_to_task_details, pattern="^back_to_task_"),
            ],
            TASK_DETAILS: [
                CallbackQueryHandler(handler.assign_task, pattern="^assign_task_"),
                CallbackQueryHandler(handler.update_task_status, pattern="^update_status_"),
                CallbackQueryHandler(handler.back_to_tasks, pattern="^back_to_tasks$"),
            ],
            EDITING_TASK: [
                CallbackQueryHandler(handler.back_to_tasks, pattern="^back_to_tasks$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handler.show_task_menu),
            CallbackQueryHandler(handler.back_to_tasks, pattern="^back_to_tasks$"),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )
