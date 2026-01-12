"""
Teclados para sistema de gestión de tareas de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class TaskManagementKeyboards:
    """Teclados para sistema de gestión de tareas."""

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú principal de gestión de tareas.
        
        Returns:
            InlineKeyboardMarkup: Teclado del menú principal
        """
        keyboard = [
            [
                InlineKeyboardButton("📝 Crear Tarea", callback_data="create_task"),
                InlineKeyboardButton("📋 Lista de Tareas", callback_data="task_list")
            ],
            [
                InlineKeyboardButton("📅 Calendario", callback_data="task_calendar"),
                InlineKeyboardButton("📊 Estadísticas", callback_data="task_stats")
            ],
            [
                InlineKeyboardButton("👥 Equipo", callback_data="team_overview"),
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_tasks() -> InlineKeyboardMarkup:
        """
        Teclado para volver a tareas.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver a Tareas", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_operations() -> InlineKeyboardMarkup:
        """
        Teclado para volver a operaciones.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno a operaciones
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver a Operaciones", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_task_form() -> InlineKeyboardMarkup:
        """
        Teclado para formulario de creación de tareas.
        
        Returns:
            InlineKeyboardMarkup: Teclado de formulario
        """
        keyboard = [
            [
                InlineKeyboardButton("📝 Completar Formulario", callback_data="fill_task_form"),
                InlineKeyboardButton("📋 Usar Plantilla", callback_data="use_task_template")
            ],
            [
                InlineKeyboardButton("📊 Ver Plantillas", callback_data="view_templates"),
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def list_actions(task_count: int) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para lista de tareas.
        
        Args:
            task_count: Cantidad de tareas
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = []
        
        if task_count > 0:
            keyboard.append([
                InlineKeyboardButton("🔍 Filtrar Tareas", callback_data="filter_tasks"),
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data="task_stats")
            ])
        
        keyboard.append([
            InlineKeyboardButton("📅 Ver Calendario", callback_data="task_calendar"),
            InlineKeyboardButton("🔙 Volver", callback_data="task_back")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def task_actions(task_id: int, status: str) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para una tarea específica.
        
        Args:
            task_id: ID de la tarea
            status: Estado actual de la tarea
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = []
        
        if status != "completed":
            keyboard.append([
                InlineKeyboardButton("✅ Completar", callback_data=f"complete_task_{task_id}"),
                InlineKeyboardButton("🔄 Actualizar Estado", callback_data=f"update_status_{task_id}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("✏️ Editar", callback_data=f"edit_task_{task_id}"),
            InlineKeyboardButton("👥 Asignar", callback_data=f"assign_task_{task_id}")
        ])
        
        keyboard.append([
            InlineKeyboardButton("📊 Ver Detalles", callback_data=f"task_details_{task_id}"),
            InlineKeyboardButton("🔙 Volver", callback_data="task_back")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_task_details(task_id: int) -> InlineKeyboardMarkup:
        """
        Teclado para volver a detalles de tarea.
        
        Args:
            task_id: ID de la tarea
            
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver a Tarea", callback_data=f"back_to_task_{task_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def status_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de estado.
        
        Returns:
            InlineKeyboardMarkup: Teclado de estados
        """
        keyboard = [
            [
                InlineKeyboardButton("⏳ Pendiente", callback_data="status_pending"),
                InlineKeyboardButton("🔄 En Progreso", callback_data="status_in_progress"),
                InlineKeyboardButton("✅ Completada", callback_data="status_completed")
            ],
            [
                InlineKeyboardButton("⏸️ Pausada", callback_data="status_paused"),
                InlineKeyboardButton("❌ Cancelada", callback_data="status_cancelled"),
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def priority_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de prioridad.
        
        Returns:
            InlineKeyboardMarkup: Teclado de prioridades
        """
        keyboard = [
            [
                InlineKeyboardButton("🔴 Alta", callback_data="priority_high"),
                InlineKeyboardButton("🟡 Media", callback_data="priority_medium"),
                InlineKeyboardButton("🟢 Baja", callback_data="priority_low")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def calendar_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones de calendario.
        
        Returns:
            InlineKeyboardMarkup: Teclado de calendario
        """
        keyboard = [
            [
                InlineKeyboardButton("📅 Hoy", callback_data="calendar_today"),
                InlineKeyboardButton("📅 Esta Semana", callback_data="calendar_week"),
                InlineKeyboardButton("📅 Este Mes", callback_data="calendar_month")
            ],
            [
                InlineKeyboardButton("⏰ Vencidas", callback_data="calendar_overdue"),
                InlineKeyboardButton("📊 Estadísticas", callback_data="task_stats"),
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def stats_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones de estadísticas.
        
        Returns:
            InlineKeyboardMarkup: Teclado de estadísticas
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Visión General", callback_data="stats_overview"),
                InlineKeyboardButton("📈 Rendimiento", callback_data="stats_performance"),
                InlineKeyboardButton("👥 Equipo", callback_data="stats_team")
            ],
            [
                InlineKeyboardButton("📅 Histórico", callback_data="stats_history"),
                InlineKeyboardButton("🎯 Metas", callback_data="stats_goals"),
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def filter_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de filtro.
        
        Returns:
            InlineKeyboardMarkup: Teclado de filtros
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Por Estado", callback_data="filter_status"),
                InlineKeyboardButton("🎯 Por Prioridad", callback_data="filter_priority"),
                InlineKeyboardButton("📅 Por Fecha", callback_data="filter_date")
            ],
            [
                InlineKeyboardButton("👥 Por Asignado", callback_data="filter_assigned"),
                InlineKeyboardButton("🏷️ Por Etiquetas", callback_data="filter_tags"),
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def template_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones de plantillas.
        
        Returns:
            InlineKeyboardMarkup: Teclado de plantillas
        """
        keyboard = [
            [
                InlineKeyboardButton("📝 Crear Plantilla", callback_data="create_template"),
                InlineKeyboardButton("📋 Ver Plantillas", callback_data="view_templates"),
                InlineKeyboardButton("✏️ Editar Plantilla", callback_data="edit_template")
            ],
            [
                InlineKeyboardButton("🗑️ Eliminar Plantilla", callback_data="delete_template"),
                InlineKeyboardButton("📤 Compartir Plantilla", callback_data="share_template"),
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def team_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones de equipo.
        
        Returns:
            InlineKeyboardMarkup: Teclado de equipo
        """
        keyboard = [
            [
                InlineKeyboardButton("👥 Ver Equipo", callback_data="view_team"),
                InlineKeyboardButton("👋 Invitar Miembro", callback_data="invite_member"),
                InlineKeyboardButton("📊 Estadísticas del Equipo", callback_data="team_stats")
            ],
            [
                InlineKeyboardButton("📋 Asignar Tareas", callback_data="assign_tasks"),
                InlineKeyboardButton("📅 Calendario del Equipo", callback_data="team_calendar"),
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def assignment_success() -> InlineKeyboardMarkup:
        """
        Teclado para asignación exitosa.
        
        Returns:
            InlineKeyboardMarkup: Teclado de éxito
        """
        keyboard = [
            [
                InlineKeyboardButton("📋 Ver Tarea", callback_data="view_assigned_task"),
                InlineKeyboardButton("👥 Asignar Otra", callback_data="assign_another")
            ],
            [
                InlineKeyboardButton("📊 Ver Equipo", callback_data="view_team"),
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def status_updated() -> InlineKeyboardMarkup:
        """
        Teclado para estado actualizado.
        
        Returns:
            InlineKeyboardMarkup: Teclado de estado actualizado
        """
        keyboard = [
            [
                InlineKeyboardButton("📋 Ver Tarea", callback_data="view_updated_task"),
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data="task_stats")
            ],
            [
                InlineKeyboardButton("📅 Ver Calendario", callback_data="task_calendar"),
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def upgrade_to_premium() -> InlineKeyboardMarkup:
        """
        Teclado para actualizar a premium.
        
        Returns:
            InlineKeyboardMarkup: Teclado de actualización
        """
        keyboard = [
            [
                InlineKeyboardButton("👑 Ver Planes VIP", callback_data="vip_plans"),
                InlineKeyboardButton("💎 Ver Beneficios", callback_data="vip_benefits")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirmation_dialog(action: str, details: dict) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para acciones de tareas.
        
        Args:
            action: Tipo de acción
            details: Detalles de la acción
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = []
        
        if action == "complete":
            keyboard.append([
                InlineKeyboardButton("✅ Completar Tarea", callback_data=f"confirm_complete_{details['task_id']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="task_back")
            ])
        elif action == "delete":
            keyboard.append([
                InlineKeyboardButton("🗑️ Eliminar Tarea", callback_data=f"confirm_delete_{details['task_id']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="task_back")
            ])
        elif action == "assign":
            keyboard.append([
                InlineKeyboardButton("✅ Asignar Tarea", callback_data=f"confirm_assign_{details['task_id']}_{details['user_id']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="task_back")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="task_back")
            ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def quick_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones rápidas.
        
        Returns:
            InlineKeyboardMarkup: Teclado de acciones rápidas
        """
        keyboard = [
            [
                InlineKeyboardButton("📝 Crear Rápida", callback_data="quick_create"),
                InlineKeyboardButton("📋 Mis Tareas", callback_data="my_tasks"),
                InlineKeyboardButton("📅 Hoy", callback_data="today_tasks")
            ],
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="task_stats"),
                InlineKeyboardButton("👥 Equipo", callback_data="team_overview"),
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def notification_settings() -> InlineKeyboardMarkup:
        """
        Teclado de configuración de notificaciones.
        
        Returns:
            InlineKeyboardMarkup: Teclado de notificaciones
        """
        keyboard = [
            [
                InlineKeyboardButton("🔔 Activar Notificaciones", callback_data="enable_notifications"),
                InlineKeyboardButton("🔕 Desactivar Notificaciones", callback_data="disable_notifications")
            ],
            [
                InlineKeyboardButton("⏰ Recordatorios", callback_data="reminder_settings"),
                InlineKeyboardButton("📧 Email Notifications", callback_data="email_notifications")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """
        Teclado de ayuda.
        
        Returns:
            InlineKeyboardMarkup: Teclado de ayuda
        """
        keyboard = [
            [
                InlineKeyboardButton("📚 Tutorial Completo", callback_data="task_tutorial"),
                InlineKeyboardButton("❓ Preguntas Frecuentes", callback_data="task_faq")
            ],
            [
                InlineKeyboardButton("📊 Guía de Estadísticas", callback_data="stats_guide"),
                InlineKeyboardButton("👥 Guía de Equipo", callback_data="team_guide")
            ],
            [
                InlineKeyboardButton("💬 Contactar Soporte", callback_data="task_support"),
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def export_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de exportación.
        
        Returns:
            InlineKeyboardMarkup: Teclado de exportación
        """
        keyboard = [
            [
                InlineKeyboardButton("📄 Exportar PDF", callback_data="export_pdf"),
                InlineKeyboardButton("📊 Exportar Excel", callback_data="export_excel"),
                InlineKeyboardButton("📋 Exportar CSV", callback_data="export_csv")
            ],
            [
                InlineKeyboardButton("📧 Enviar por Email", callback_data="export_email"),
                InlineKeyboardButton("💾 Guardar en Nube", callback_data="export_cloud"),
                InlineKeyboardButton("🔙 Volver", callback_data="task_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
