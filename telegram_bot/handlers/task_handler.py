"""
Handler de tareas para usuarios del bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from loguru import logger
import uuid

from application.services.task_service import TaskService
from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards


class TaskHandler:
    """Handler para el sistema de tareas de usuarios."""
    
    def __init__(self, task_service: TaskService):
        self.task_service = task_service
    
    async def show_task_center(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el centro de tareas."""
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            summary = await self.task_service.get_user_tasks_summary(user_id)
            
            text = Messages.Tasks.SUMMARY.format(
                available=summary["total_available"],
                in_progress=summary["total_in_progress"],
                completed=summary["total_completed"]
            )
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboards.task_center_menu(),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_task_center: {e}")
            await query.edit_message_text(
                text=f"❌ Error: {str(e)}",
                reply_markup=InlineKeyboards.back_button("operations")
            )
    
    async def show_available_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra las tareas disponibles."""
        query = update.callback_query
        await query.answer()
        
        try:
            tasks = await self.task_service.get_active_tasks()
            
            if not tasks:
                await query.edit_message_text(
                    text=Messages.Tasks.NO_TASKS,
                    reply_markup=InlineKeyboards.back_button("task_center"),
                    parse_mode="Markdown"
                )
                return
            
            # Preparar lista de tareas para el teclado
            tasks_list = [{"id": str(t.id), "title": t.title} for t in tasks]
            
            text = "📋 **Tareas Disponibles**\n━━━━━━━━━━━━\n\n"
            text += "Selecciona una tarea para ver más detalles:"
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboards.task_list_keyboard(tasks_list, "task"),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_available_tasks: {e}")
            await query.edit_message_text(
                text=f"❌ Error: {str(e)}",
                reply_markup=InlineKeyboards.back_button("task_center")
            )
    
    async def show_task_detail(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra los detalles de una tarea."""
        query = update.callback_query
        await query.answer()
        
        try:
            # Extraer task_id del callback_data (formato: task_detail_{task_id})
            task_id_str = query.data.split("_detail_")[1]
            task_id = uuid.UUID(task_id_str)
            
            task = await self.task_service.get_task_by_id(task_id)
            
            if not task:
                await query.edit_message_text(
                    text="❌ Tarea no encontrada",
                    reply_markup=InlineKeyboards.back_button("task_center")
                )
                return
            
            user_id = update.effective_user.id
            # Obtener user_task a través del servicio
            from infrastructure.persistence.supabase.task_repository import TaskRepository
            from application.services.common.container import get_container
            container = get_container()
            task_repo = container.resolve(TaskRepository)
            user_task = await task_repo.get_user_task(user_id, task_id)
            
            # Construir mensaje
            guide_section = ""
            if task.guide_text:
                guide_section = Messages.Tasks.TASK_GUIDE.format(guide_text=task.guide_text)
            
            text = Messages.Tasks.TASK_DETAIL.format(
                title=task.title,
                description=task.description,
                reward_stars=task.reward_stars,
                guide_section=guide_section
            )
            
            # Determinar estado de la tarea
            is_completed = user_task.is_completed if user_task else False
            reward_claimed = user_task.reward_claimed if user_task else False
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboards.task_detail_keyboard(
                    task_id_str, is_completed, reward_claimed
                ),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_task_detail: {e}")
            await query.edit_message_text(
                text=f"❌ Error: {str(e)}",
                reply_markup=InlineKeyboards.back_button("task_center")
            )
    
    async def complete_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Marca una tarea como completada."""
        query = update.callback_query
        await query.answer()
        
        try:
            # Extraer task_id del callback_data (formato: task_complete_{task_id})
            task_id_str = query.data.split("_complete_")[1]
            task_id = uuid.UUID(task_id_str)
            
            user_id = update.effective_user.id
            
            user_task = await self.task_service.complete_task(user_id, task_id)
            task = await self.task_service.get_task_by_id(task_id)
            
            text = Messages.Tasks.TASK_COMPLETED.format(
                title=task.title,
                reward_stars=task.reward_stars
            )
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboards.task_detail_keyboard(
                    task_id_str, True, False
                ),
                parse_mode="Markdown"
            )
            
        except ValueError as e:
            await query.answer(str(e), show_alert=True)
        except Exception as e:
            logger.error(f"Error en complete_task: {e}")
            await query.answer(f"Error: {str(e)}", show_alert=True)
    
    async def claim_reward(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reclama la recompensa de una tarea completada."""
        query = update.callback_query
        await query.answer()
        
        try:
            # Extraer task_id del callback_data (formato: task_claim_{task_id})
            task_id_str = query.data.split("_claim_")[1]
            task_id = uuid.UUID(task_id_str)
            
            user_id = update.effective_user.id
            
            await self.task_service.claim_reward(user_id, task_id)
            
            # Obtener balance actualizado
            from application.services.common.container import get_container
            from domain.interfaces.iuser_repository import IUserRepository
            container = get_container()
            user_repo = container.resolve(IUserRepository)
            user = await user_repo.get_by_id(user_id)
            
            task = await self.task_service.get_task_by_id(task_id)
            
            text = Messages.Tasks.REWARD_CLAIMED.format(
                reward_stars=task.reward_stars,
                balance=user.balance_stars if user else 0
            )
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboards.back_button("task_center"),
                parse_mode="Markdown"
            )
            
        except ValueError as e:
            await query.answer(str(e), show_alert=True)
        except Exception as e:
            logger.error(f"Error en claim_reward: {e}")
            await query.answer(f"Error: {str(e)}", show_alert=True)
    
    async def show_completed_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra las tareas completadas."""
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            summary = await self.task_service.get_user_tasks_summary(user_id)
            
            completed = summary["completed"]
            
            if not completed:
                await query.edit_message_text(
                    text="📭 **No hay tareas completadas**\n\nCompleta tareas para verlas aquí.",
                    reply_markup=InlineKeyboards.back_button("task_center"),
                    parse_mode="Markdown"
                )
                return
            
            tasks_list = [
                {
                    "id": str(item["task"].id),
                    "title": item["task"].title
                }
                for item in completed
            ]
            
            text = "✅ **Tareas Completadas**\n━━━━━━━━━━━━\n\n"
            text += "Selecciona una tarea para ver detalles:"
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboards.task_list_keyboard(tasks_list, "task"),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_completed_tasks: {e}")
            await query.edit_message_text(
                text=f"❌ Error: {str(e)}",
                reply_markup=InlineKeyboards.back_button("task_center")
            )
    
    async def show_in_progress_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra las tareas en progreso."""
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            summary = await self.task_service.get_user_tasks_summary(user_id)
            
            in_progress = summary["in_progress"]
            
            if not in_progress:
                await query.edit_message_text(
                    text="📭 **No hay tareas en progreso**\n\nInicia una tarea para verla aquí.",
                    reply_markup=InlineKeyboards.back_button("task_center"),
                    parse_mode="Markdown"
                )
                return
            
            tasks_list = [
                {
                    "id": str(item["task"].id),
                    "title": item["task"].title
                }
                for item in in_progress
            ]
            
            text = "🔄 **Tareas en Progreso**\n━━━━━━━━━━━━\n\n"
            text += "Selecciona una tarea para continuar:"
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboards.task_list_keyboard(tasks_list, "task"),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_in_progress_tasks: {e}")
            await query.edit_message_text(
                text=f"❌ Error: {str(e)}",
                reply_markup=InlineKeyboards.back_button("task_center")
            )
    
    async def show_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el resumen de tareas."""
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            summary = await self.task_service.get_user_tasks_summary(user_id)
            
            text = Messages.Tasks.SUMMARY.format(
                available=summary["total_available"],
                in_progress=summary["total_in_progress"],
                completed=summary["total_completed"]
            )
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboards.task_center_menu(),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_summary: {e}")
            await query.edit_message_text(
                text=f"❌ Error: {str(e)}",
                reply_markup=InlineKeyboards.back_button("operations")
            )
    
    def get_handlers(self):
        """Retorna los handlers de tareas."""
        return [
            CallbackQueryHandler(self.show_task_center, pattern="^task_center$"),
            CallbackQueryHandler(self.show_available_tasks, pattern="^tasks_available$"),
            CallbackQueryHandler(self.show_in_progress_tasks, pattern="^tasks_in_progress$"),
            CallbackQueryHandler(self.show_completed_tasks, pattern="^tasks_completed$"),
            CallbackQueryHandler(self.show_summary, pattern="^tasks_summary$"),
            CallbackQueryHandler(self.show_task_detail, pattern="^task_detail_"),
            CallbackQueryHandler(self.complete_task, pattern="^task_complete_"),
            CallbackQueryHandler(self.claim_reward, pattern="^task_claim_"),
        ]


def get_task_handler(task_service: TaskService):
    """Función helper para obtener el handler de tareas."""
    return TaskHandler(task_service)

