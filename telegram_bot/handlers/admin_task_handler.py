"""
Handler de administración de tareas para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from utils.logger import logger
import uuid
import re
from config import settings

from application.services.task_service import TaskService
from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard import TaskKeyboards, CommonKeyboards

# Estados de la conversación
WAITING_TASK_DATA = 1
WAITING_TASK_EDIT = 2


class AdminTaskHandler:
    """Handler para la administración de tareas."""
    
    def __init__(self, task_service: TaskService):
        self.task_service = task_service
    
    async def show_admin_task_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú de administración de tareas."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        # Verificar si es admin
        if user.id != int(settings.ADMIN_ID):
            await query.edit_message_text(
                text=Messages.Admin.UNAUTHORIZED,
                parse_mode="Markdown"
            )
            return
        
        text = "🔧 **Administración de Tareas**\n━━━━━━━━━━━━\n\n"
        text += "Gestiona las tareas del sistema:"
        
        await query.edit_message_text(
            text=text,
            reply_markup=TaskKeyboards.admin_task_menu(),
            parse_mode="Markdown"
        )
    
    async def start_create_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el proceso de creación de tarea."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        if user.id != int(settings.ADMIN_ID):
            await query.edit_message_text(
                text=Messages.Admin.UNAUTHORIZED,
                parse_mode="Markdown"
            )
            return ConversationHandler.END
        
        await query.edit_message_text(
            text=Messages.Tasks.ADMIN_CREATE_TASK,
            reply_markup=CommonKeyboards.back_button("admin_task_menu"),
            parse_mode="Markdown"
        )
        
        return WAITING_TASK_DATA
    
    async def process_task_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa los datos de la tarea enviados por el admin."""
        user = update.effective_user
        
        if user.id != int(settings.ADMIN_ID):
            return ConversationHandler.END
        
        text = update.message.text
        
        try:
            # Parsear el mensaje
            # Formato esperado:
            # Título
            # Descripción
            # 
            # **Recompensa:** X estrellas
            # **Guía:** (opcional) texto de guía
            
            lines = text.split("\n")
            title = lines[0].strip()
            
            # Buscar descripción (hasta encontrar "**Recompensa:**")
            description_lines = []
            reward_line_idx = -1
            
            for i, line in enumerate(lines[1:], 1):
                if "**Recompensa:**" in line or "Recompensa:" in line:
                    reward_line_idx = i
                    break
                description_lines.append(line)
            
            description = "\n".join(description_lines).strip()
            
            # Extraer recompensa
            reward_match = re.search(r"(\d+)\s*estrellas?", text, re.IGNORECASE)
            if not reward_match:
                await update.message.reply_text(
                    "❌ No se encontró la recompensa. Formato: **Recompensa:** X estrellas",
                    parse_mode="Markdown"
                )
                return WAITING_TASK_DATA
            
            reward_stars = int(reward_match.group(1))
            
            # Extraer guía (opcional)
            guide_match = re.search(r"\*\*Guía:\*\*\s*(.+?)(?=\n\n|\Z)", text, re.DOTALL | re.IGNORECASE)
            guide_text = guide_match.group(1).strip() if guide_match else None
            
            # Crear la tarea
            task = await self.task_service.create_task(
                title=title,
                description=description,
                reward_stars=reward_stars,
                created_by=user.id,
                guide_text=guide_text
            )
            
            text = Messages.Tasks.ADMIN_TASK_CREATED.format(
                title=task.title,
                reward_stars=task.reward_stars,
                task_id=str(task.id)
            )
            
            await update.message.reply_text(
                text=text,
                reply_markup=CommonKeyboards.back_button("admin_task_menu"),
                parse_mode="Markdown"
            )
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Error procesando datos de tarea: {e}")
            await update.message.reply_text(
                f"❌ Error al crear la tarea: {str(e)}\n\nIntenta de nuevo:",
                parse_mode="Markdown"
            )
            return WAITING_TASK_DATA
    
    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lista todas las tareas."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        if user.id != int(settings.ADMIN_ID):
            await query.edit_message_text(
                text=Messages.Admin.UNAUTHORIZED,
                parse_mode="Markdown"
            )
            return
        
        try:
            tasks = await self.task_service.get_all_tasks()
            
            if not tasks:
                await query.edit_message_text(
                    text="📭 **No hay tareas creadas**\n\nCrea una nueva tarea para comenzar.",
                    reply_markup=CommonKeyboards.back_button("admin_task_menu"),
                    parse_mode="Markdown"
                )
                return
            
            tasks_list_text = ""
            tasks_for_keyboard = []
            
            for task in tasks[:10]:  # Máximo 10 tareas
                status_icon = "✅" if task.is_active else "❌"
                tasks_list_text += Messages.Tasks.ADMIN_TASK_ITEM.format(
                    status=status_icon,
                    title=task.title,
                    reward_stars=task.reward_stars,
                    task_id=str(task.id)
                )
                
                tasks_for_keyboard.append({
                    "id": str(task.id),
                    "title": task.title,
                    "is_active": task.is_active
                })
            
            text = Messages.Tasks.ADMIN_TASK_LIST.format(tasks_list=tasks_list_text)
            
            await query.edit_message_text(
                text=text,
                reply_markup=TaskKeyboards.admin_task_list_keyboard(tasks_for_keyboard),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error listando tareas: {e}")
            await query.edit_message_text(
                text=f"❌ Error: {str(e)}",
                reply_markup=CommonKeyboards.back_button("admin_task_menu")
            )
    
    async def show_task_detail_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra los detalles de una tarea (admin)."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        if user.id != int(settings.ADMIN_ID):
            await query.edit_message_text(
                text=Messages.Admin.UNAUTHORIZED,
                parse_mode="Markdown"
            )
            return
        
        try:
            # Extraer task_id del callback_data (formato: admin_task_detail_{task_id})
            task_id_str = query.data.split("_detail_")[1]
            task_id = uuid.UUID(task_id_str)
            
            task = await self.task_service.get_task_by_id(task_id)
            
            if not task:
                await query.edit_message_text(
                    text="❌ Tarea no encontrada",
                    reply_markup=CommonKeyboards.back_button("admin_task_list")
                )
                return
            
            status_icon = "✅" if task.is_active else "❌"
            
            text = f"{status_icon} **{task.title}**\n"
            text += "━━━━━━━━━━━━\n\n"
            text += f"**Descripción:**\n{task.description}\n\n"
            text += f"**Recompensa:** {task.reward_stars} ⭐\n"
            
            if task.guide_text:
                text += f"\n**Guía:**\n{task.guide_text}\n"
            
            text += f"\n**ID:** `{task.id}`\n"
            text += f"**Creada:** {task.created_at.strftime('%d/%m/%Y %H:%M')}\n"
            
            if task.expires_at:
                text += f"**Expira:** {task.expires_at.strftime('%d/%m/%Y %H:%M')}\n"
            
            await query.edit_message_text(
                text=text,
                reply_markup=TaskKeyboards.admin_task_detail_keyboard(task_id_str),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error mostrando detalle de tarea: {e}")
            await query.edit_message_text(
                text=f"❌ Error: {str(e)}",
                reply_markup=CommonKeyboards.back_button("admin_task_list")
            )
    
    async def delete_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Elimina una tarea."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        if user.id != int(settings.ADMIN_ID):
            await query.edit_message_text(
                text=Messages.Admin.UNAUTHORIZED,
                parse_mode="Markdown"
            )
            return
        
        try:
            # Extraer task_id del callback_data (formato: admin_task_delete_{task_id})
            task_id_str = query.data.split("_delete_")[1]
            task_id = uuid.UUID(task_id_str)
            
            success = await self.task_service.delete_task(task_id)
            
            if success:
                await query.edit_message_text(
                    text="✅ **Tarea eliminada correctamente**",
                    reply_markup=CommonKeyboards.back_button("admin_task_list"),
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(
                    text="❌ Error al eliminar la tarea",
                    reply_markup=CommonKeyboards.back_button("admin_task_list"),
                    parse_mode="Markdown"
                )
            
        except Exception as e:
            logger.error(f"Error eliminando tarea: {e}")
            await query.edit_message_text(
                text=f"❌ Error: {str(e)}",
                reply_markup=CommonKeyboards.back_button("admin_task_list")
            )
    
    def get_handlers(self):
        """Retorna los handlers de administración de tareas."""
        return [
            CallbackQueryHandler(self.show_admin_task_menu, pattern="^admin_task_menu$"),
            CallbackQueryHandler(self.list_tasks, pattern="^admin_task_list$"),
            CallbackQueryHandler(self.show_task_detail_admin, pattern="^admin_task_detail_"),
            CallbackQueryHandler(self.delete_task, pattern="^admin_task_delete_"),
            ConversationHandler(
                entry_points=[
                    CallbackQueryHandler(
                        self.start_create_task,
                        pattern="^admin_task_create$"
                    )
                ],
                states={
                    WAITING_TASK_DATA: [
                        MessageHandler(
                            filters.TEXT & ~filters.COMMAND,
                            self.process_task_data
                        )
                    ]
                },
                fallbacks=[
                    CallbackQueryHandler(
                        lambda u, c: ConversationHandler.END,
                        pattern="^admin_task_menu$"
                    )
                ],
                per_message=True,
                per_chat=True,
                per_user=True,
            )
        ]


def get_admin_task_handler(task_service: TaskService):
    """Función helper para obtener el handler de administración de tareas."""
    return AdminTaskHandler(task_service)

