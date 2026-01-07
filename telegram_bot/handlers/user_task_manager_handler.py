"""
Handler de Gestión de Tareas para Usuarios con Rol de Gestor de Tareas.

Permite a usuarios con el rol 'task_manager' crear, editar y gestionar tareas para otros usuarios.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from utils.logger import logger
from datetime import datetime, timezone
import uuid

from application.services.task_service import TaskService
from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard.inline_keyboards import InlineKeyboards
from domain.entities.user import UserRole, UserStatus

# Estados de conversación
TASK_MENU = 0
CREATING_TASK = 1
TASK_TITLE = 2
TASK_DESCRIPTION = 3
TASK_REWARD = 4
CONFIRMING_TASK = 5
MANAGING_TASKS = 6
VIEWING_TASK_STATS = 7


class UserTaskManagerHandler:
    """Handler para gestión de tareas por usuarios con rol Gestor de Tareas."""

    def __init__(self, task_service: TaskService, user_repository):
        self.task_service = task_service
        self.user_repository = user_repository

    async def _check_role_permission(self, user_id: int) -> bool:
        """Verificar si el usuario tiene permiso (rol de Gestor de Tareas activo)."""
        try:
            user = await self.user_repository.get_user(user_id)
            if not user:
                return False
            
            return user.is_task_manager_active()
        except Exception as e:
            logger.error(f"Error verificando permiso de gestor de tareas: {e}")
            return False

    async def task_manager_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar menú principal del Gestor de Tareas."""
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            
            # Verificar permiso
            if not await self._check_role_permission(user_id):
                await query.edit_message_text(
                    text="❌ **Acceso Denegado**\n\nNecesitas tener el rol de **Gestor de Tareas** activo.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Volver", callback_data="operations")]
                    ]),
                    parse_mode="Markdown"
                )
                return ConversationHandler.END
            
            # Obtener estadísticas
            user_tasks = await self.task_service.get_user_created_tasks(user_id)
            stats = await self.task_service.get_task_creation_stats(user_id)
            
            message = f"""📋 **Centro de Gestor de Tareas**

👤 **Tu Rol:** Gestor de Tareas

**Estadísticas:**
📊 Tareas Creadas: {stats.get('total_created', 0)}
🟢 Activas: {stats.get('active', 0)}
✅ Completadas: {stats.get('completed', 0)}
📈 Participantes Totales: {stats.get('total_participants', 0)}

**Acciones Disponibles:**"""

            keyboard = [
                [InlineKeyboardButton("➕ Crear Nueva Tarea", callback_data="utm_create_task")],
                [InlineKeyboardButton("📋 Mis Tareas", callback_data="utm_my_tasks")],
                [InlineKeyboardButton("📊 Estadísticas Detalladas", callback_data="utm_view_stats")],
                [InlineKeyboardButton("👥 Ver Participantes", callback_data="utm_view_participants")],
                [InlineKeyboardButton("🔙 Volver", callback_data="operations")]
            ]
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return TASK_MENU
            
        except Exception as e:
            logger.error(f"Error en task_manager_menu: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return TASK_MENU

    async def start_create_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Iniciar creación de tarea."""
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            
            if not await self._check_role_permission(user_id):
                await query.answer("❌ Permiso denegado", show_alert=True)
                return TASK_MENU
            
            context.user_data['new_task'] = {
                'creator_id': user_id,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            message = """➕ **Crear Nueva Tarea**

Ingresa el **título** de la tarea:

💡 *Ejemplos:*
- Instala VPN en tu teléfono
- Completa tu perfil
- Invita un amigo"""
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cancelar", callback_data="utm_menu")]
                ]),
                parse_mode="Markdown"
            )
            return TASK_TITLE
            
        except Exception as e:
            logger.error(f"Error en start_create_task: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return TASK_MENU

    async def get_task_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener título de la tarea."""
        try:
            title = update.message.text
            
            if len(title) < 5 or len(title) > 100:
                await update.message.reply_text(
                    "❌ El título debe tener entre 5 y 100 caracteres"
                )
                return TASK_TITLE
            
            context.user_data['new_task']['title'] = title
            
            message = """📝 **Descripción de la Tarea**

Ingresa una descripción detallada:

💡 *Ejemplo:*
"Descarga nuestra app VPN y conéctate a un servidor. 
Luego confirma que la velocidad es mayor a 10 Mbps"

Máximo 500 caracteres."""
            
            await update.message.reply_text(
                text=message,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cancelar", callback_data="utm_menu")]
                ]),
                parse_mode="Markdown"
            )
            return TASK_DESCRIPTION
            
        except Exception as e:
            logger.error(f"Error en get_task_title: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            return TASK_TITLE

    async def get_task_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener descripción de la tarea."""
        try:
            description = update.message.text
            
            if len(description) < 10 or len(description) > 500:
                await update.message.reply_text(
                    "❌ La descripción debe tener entre 10 y 500 caracteres"
                )
                return TASK_DESCRIPTION
            
            context.user_data['new_task']['description'] = description
            
            message = """⭐ **Recompensa por Completar**

¿Cuántas estrellas ofreces por completar esta tarea?

Rango: 1 - 1000 ⭐

💡 *Sugerencia:*
- Tareas sencillas: 10-50 ⭐
- Tareas moderadas: 50-200 ⭐
- Tareas complejas: 200+ ⭐"""
            
            await update.message.reply_text(
                text=message,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cancelar", callback_data="utm_menu")]
                ]),
                parse_mode="Markdown"
            )
            return TASK_REWARD
            
        except Exception as e:
            logger.error(f"Error en get_task_description: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            return TASK_DESCRIPTION

    async def get_task_reward(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener recompensa de la tarea."""
        try:
            reward_text = update.message.text
            
            try:
                reward = int(reward_text)
            except ValueError:
                await update.message.reply_text(
                    "❌ Debes ingresar un número válido"
                )
                return TASK_REWARD
            
            if reward < 1 or reward > 1000:
                await update.message.reply_text(
                    "❌ La recompensa debe estar entre 1 y 1000 ⭐"
                )
                return TASK_REWARD
            
            context.user_data['new_task']['reward'] = reward
            
            # Mostrar confirmación
            task_data = context.user_data['new_task']
            
            message = f"""✅ **Confirmar Tarea**

📋 **Título:** {task_data['title']}

📝 **Descripción:** {task_data['description']}

⭐ **Recompensa:** {task_data['reward']} ⭐

¿Deseas crear esta tarea?"""
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Crear", callback_data="utm_confirm_task"),
                    InlineKeyboardButton("❌ Cancelar", callback_data="utm_menu")
                ]
            ]
            
            await update.message.reply_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return CONFIRMING_TASK
            
        except Exception as e:
            logger.error(f"Error en get_task_reward: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            return TASK_REWARD

    async def confirm_create_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirmar creación de tarea."""
        query = update.callback_query
        await query.answer()
        
        try:
            task_data = context.user_data.get('new_task', {})
            
            if not task_data:
                await query.answer("❌ Error: Datos de tarea no encontrados", show_alert=True)
                return TASK_MENU
            
            # Crear tarea en BD
            task_id = str(uuid.uuid4())
            result = await self.task_service.create_task(
                task_id=task_id,
                creator_id=task_data['creator_id'],
                title=task_data['title'],
                description=task_data['description'],
                reward=task_data['reward']
            )
            
            if result:
                message = f"""✅ **Tarea Creada Exitosamente**

🆔 ID: `{task_id}`
📋 Título: {task_data['title']}
⭐ Recompensa: {task_data['reward']} ⭐

La tarea está ahora disponible para que otros usuarios la completen.

**Estadísticas en Vivo:**
📊 Visualizaciones: 0
✅ Completadas: 0"""
                
                del context.user_data['new_task']
                
                await query.edit_message_text(
                    text=message,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ Crear Otra", callback_data="utm_create_task")],
                        [InlineKeyboardButton("📋 Mis Tareas", callback_data="utm_my_tasks")],
                        [InlineKeyboardButton("🔙 Menú", callback_data="utm_menu")]
                    ]),
                    parse_mode="Markdown"
                )
            else:
                await query.answer("❌ Error al crear tarea", show_alert=True)
            
            return TASK_MENU
            
        except Exception as e:
            logger.error(f"Error en confirm_create_task: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return TASK_MENU

    async def view_user_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ver tareas del usuario."""
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            
            if not await self._check_role_permission(user_id):
                await query.answer("❌ Permiso denegado", show_alert=True)
                return TASK_MENU
            
            tasks = await self.task_service.get_user_created_tasks(user_id)
            
            if not tasks:
                message = "📋 **Mis Tareas**\n\nNo tienes tareas creadas aún."
                keyboard = [
                    [InlineKeyboardButton("➕ Crear Tarea", callback_data="utm_create_task")],
                    [InlineKeyboardButton("🔙 Menú", callback_data="utm_menu")]
                ]
            else:
                task_list = []
                for task in tasks[:10]:  # Limitar a 10
                    status = "🟢" if task.get('is_active', True) else "🔴"
                    task_list.append(
                        f"{status} **{task.get('title', 'Sin título')}**\n"
                        f"  ⭐ {task.get('reward', 0)} | "
                        f"✅ {task.get('completed_count', 0)} completadas"
                    )
                
                message = f"""📋 **Mis Tareas**

Total: {len(tasks)} tareas

{chr(10).join(task_list)}"""
                
                keyboard = [
                    [InlineKeyboardButton("➕ Crear Nueva", callback_data="utm_create_task")],
                    [InlineKeyboardButton("📊 Estadísticas", callback_data="utm_view_stats")],
                    [InlineKeyboardButton("🔙 Menú", callback_data="utm_menu")]
                ]
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return MANAGING_TASKS
            
        except Exception as e:
            logger.error(f"Error en view_user_tasks: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return TASK_MENU

    async def view_task_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ver estadísticas de tareas."""
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            
            if not await self._check_role_permission(user_id):
                await query.answer("❌ Permiso denegado", show_alert=True)
                return TASK_MENU
            
            stats = await self.task_service.get_task_creation_stats(user_id)
            
            message = f"""📊 **Estadísticas de Tareas**

**Creación:**
📋 Total Creadas: {stats.get('total_created', 0)}
🟢 Activas: {stats.get('active', 0)}
✅ Completadas: {stats.get('completed', 0)}

**Participación:**
👥 Usuarios Únicos: {stats.get('unique_participants', 0)}
📊 Total de Participaciones: {stats.get('total_participations', 0)}

**Recompensas:**
⭐ Total Ofrecido: {stats.get('total_reward_offered', 0)} ⭐
💰 Total Pagado: {stats.get('total_reward_paid', 0)} ⭐

**Ingresos Estimados:**
💵 Comisión (10%): {int(stats.get('total_reward_offered', 0) * 0.1)} ⭐"""
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📋 Mis Tareas", callback_data="utm_my_tasks")],
                    [InlineKeyboardButton("🔙 Menú", callback_data="utm_menu")]
                ]),
                parse_mode="Markdown"
            )
            return VIEWING_TASK_STATS
            
        except Exception as e:
            logger.error(f"Error en view_task_stats: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return TASK_MENU


def get_user_task_manager_handlers(task_service: TaskService, user_repository) -> list:
    """Retorna los handlers para gestión de tareas de usuarios."""
    handler = UserTaskManagerHandler(task_service, user_repository)
    handlers = []
    
    # Menú principal
    handlers.append(
        CallbackQueryHandler(handler.task_manager_menu, pattern="^utm_menu$|^user_task_manager$")
    )
    
    # Conversation handler para crear tareas
    task_creation_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(handler.start_create_task, pattern="^utm_create_task$")],
        states={
            TASK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handler.get_task_title)],
            TASK_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handler.get_task_description)],
            TASK_REWARD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handler.get_task_reward)],
            CONFIRMING_TASK: [CallbackQueryHandler(handler.confirm_create_task, pattern="^utm_confirm_task$")],
        },
        fallbacks=[CallbackQueryHandler(handler.task_manager_menu, pattern="^utm_menu$")]
    )
    handlers.append(task_creation_conversation)
    
    # Ver tareas
    handlers.append(
        CallbackQueryHandler(handler.view_user_tasks, pattern="^utm_my_tasks$")
    )
    
    # Estadísticas
    handlers.append(
        CallbackQueryHandler(handler.view_task_stats, pattern="^utm_view_stats$")
    )
    
    return handlers
