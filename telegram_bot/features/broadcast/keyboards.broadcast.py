"""
Teclados para sistema de difusión masiva de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class BroadcastKeyboards:
    """Teclados para sistema de difusión masiva."""

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú principal de broadcast.
        
        Returns:
            InlineKeyboardMarkup: Teclado del menú principal
        """
        keyboard = [
            [
                InlineKeyboardButton("📝 Crear Broadcast", callback_data="create_broadcast"),
                InlineKeyboardButton("📊 Historial", callback_data="broadcast_history")
            ],
            [
                InlineKeyboardButton("📈 Estadísticas", callback_data="broadcast_stats"),
                InlineKeyboardButton("📋 Plantillas", callback_data="broadcast_templates")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_broadcast() -> InlineKeyboardMarkup:
        """
        Teclado para volver a broadcast.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver a Broadcast", callback_data="broadcast_back")
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
    def type_selection() -> InlineKeyboardMarkup:
        """
        Teclado de selección de tipo de broadcast.
        
        Returns:
            InlineKeyboardMarkup: Teclado de tipos
        """
        keyboard = [
            [
                InlineKeyboardButton("📢 General", callback_data="type_general"),
                InlineKeyboardButton("⚠️ Urgente", callback_data="type_urgent"),
                InlineKeyboardButton("🎉 Promocional", callback_data="type_promotional")
            ],
            [
                InlineKeyboardButton("📚 Informativo", callback_data="type_informational"),
                InlineKeyboardButton("🔧 Mantenimiento", callback_data="type_maintenance"),
                InlineKeyboardButton("📋 Ver Descripciones", callback_data="type_descriptions")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="broadcast_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def audience_selection() -> InlineKeyboardMarkup:
        """
        Teclado de selección de audiencia.
        
        Returns:
            InlineKeyboardMarkup: Teclado de audiencia
        """
        keyboard = [
            [
                InlineKeyboardButton("🌍 Todos los Usuarios", callback_data="audience_all"),
                InlineKeyboardButton("🟢 Usuarios Activos", callback_data="audience_active"),
                InlineKeyboardButton("👑 Usuarios VIP", callback_data="audience_vip")
            ],
            [
                InlineKeyboardButton("🔔 Usuarios Suscritos", callback_data="audience_subscribed"),
                InlineKeyboardButton("📊 Por Segmento", callback_data="audience_segment"),
                InlineKeyboardButton("📈 Ver Estadísticas", callback_data="audience_stats")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="broadcast_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def segment_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de segmentación.
        
        Returns:
            InlineKeyboardMarkup: Teclado de segmentación
        """
        keyboard = [
            [
                InlineKeyboardButton("📅 Por Fecha de Registro", callback_data="segment_by_date"),
                InlineKeyboardButton("💰 Por Nivel VIP", callback_data="segment_by_vip"),
                InlineKeyboardButton("🎮 Por Actividad", callback_data="segment_by_activity")
            ],
            [
                InlineKeyboardButton("🌍 Por Ubicación", callback_data="segment_by_location"),
                InlineKeyboardButton("📱 Por Dispositivo", callback_data="segment_by_device"),
                InlineKeyboardButton("🎯 Personalizado", callback_data="segment_custom")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="audience_selection")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def compose_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones de composición.
        
        Returns:
            InlineKeyboardMarkup: Teclado de composición
        """
        keyboard = [
            [
                InlineKeyboardButton("📝 Escribir Mensaje", callback_data="write_message"),
                InlineKeyboardButton("📋 Usar Plantilla", callback_data="use_template"),
                InlineKeyboardButton("👁️ Vista Previa", callback_data="preview_message")
            ],
            [
                InlineKeyboardButton("📊 Ver Audiencia", callback_data="view_audience"),
                InlineKeyboardButton("⏰ Programar Envío", callback_data="schedule_send"),
                InlineKeyboardButton("🔙 Volver", callback_data="broadcast_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirm_send() -> InlineKeyboardMarkup:
        """
        Teclado de confirmación de envío.
        
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = [
            [
                InlineKeyboardButton("✅ Enviar Ahora", callback_data="send_broadcast"),
                InlineKeyboardButton("⏰ Programar", callback_data="schedule_broadcast"),
                InlineKeyboardButton("💾 Guardar Borrador", callback_data="save_draft")
            ],
            [
                InlineKeyboardButton("📝 Editar Mensaje", callback_data="edit_message"),
                InlineKeyboardButton("👥 Cambiar Audiencia", callback_data="change_audience"),
                InlineKeyboardButton("❌ Cancelar", callback_data="broadcast_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def broadcast_success() -> InlineKeyboardMarkup:
        """
        Teclado para broadcast exitoso.
        
        Returns:
            InlineKeyboardMarkup: Teclado de éxito
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data="view_stats"),
                InlineKeyboardButton("📋 Ver Detalles", callback_data="view_details"),
                InlineKeyboardButton("📝 Crear Otro", callback_data="create_broadcast")
            ],
            [
                InlineKeyboardButton("🔙 Volver a Broadcast", callback_data="broadcast_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def history_actions(count: int) -> InlineKeyboardMarkup:
        """
        Teclado de acciones de historial.
        
        Args:
            count: Cantidad de broadcasts
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = []
        
        if count > 0:
            keyboard.append([
                InlineKeyboardButton("📊 Estadísticas Generales", callback_data="general_stats"),
                InlineKeyboardButton("📈 Análisis de Rendimiento", callback_data="performance_analysis")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver a Broadcast", callback_data="broadcast_back")
        ])
        
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
                InlineKeyboardButton("📈 Rendimiento", callback_data="performance_stats"),
                InlineKeyboardButton("📊 Comparación", callback_data="comparison_stats"),
                InlineKeyboardButton("📅 Histórico", callback_data="historical_stats")
            ],
            [
                InlineKeyboardButton("🎯 Análisis de Audiencia", callback_data="audience_analysis"),
                InlineKeyboardButton("📱 Dispositivos", callback_data="device_stats"),
                InlineKeyboardButton("⏰ Horarios Óptimos", callback_data="optimal_times")
            ],
            [
                InlineKeyboardButton("🔙 Volver a Broadcast", callback_data="broadcast_back")
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
                InlineKeyboardButton("🔙 Volver a Broadcast", callback_data="broadcast_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def scheduling_menu() -> InlineKeyboardMarkup:
        """
        Teclado de programación.
        
        Returns:
            InlineKeyboardMarkup: Teclado de programación
        """
        keyboard = [
            [
                InlineKeyboardButton("📅 Seleccionar Fecha", callback_data="select_date"),
                InlineKeyboardButton("⏰ Seleccionar Hora", callback_data="select_time"),
                InlineKeyboardButton("🔄 Configurar Recurrencia", callback_data="configure_recurring")
            ],
            [
                InlineKeyboardButton("📊 Ver Horarios Óptimos", callback_data="optimal_times"),
                InlineKeyboardButton("🔙 Cancelar Programación", callback_data="cancel_schedule"),
                InlineKeyboardButton("🔙 Volver", callback_data="broadcast_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def date_selection() -> InlineKeyboardMarkup:
        """
        Teclado de selección de fecha.
        
        Returns:
            InlineKeyboardMarkup: Teclado de fechas
        """
        keyboard = [
            [
                InlineKeyboardButton("📅 Hoy", callback_data="date_today"),
                InlineKeyboardButton("📅 Mañana", callback_data="date_tomorrow"),
                InlineKeyboardButton("📅 Esta Semana", callback_data="date_this_week")
            ],
            [
                InlineKeyboardButton("📅 Próxima Semana", callback_data="date_next_week"),
                InlineKeyboardButton("📅 Fecha Personalizada", callback_data="date_custom"),
                InlineKeyboardButton("🔙 Volver", callback_data="scheduling_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def time_selection() -> InlineKeyboardMarkup:
        """
        Teclado de selección de hora.
        
        Returns:
            InlineKeyboardMarkup: Teclado de horas
        """
        keyboard = [
            [
                InlineKeyboardButton("🕐 09:00 (Mañana)", callback_data="time_09:00"),
                InlineKeyboardButton("🕐 12:00 (Mediodía)", callback_data="time_12:00"),
                InlineKeyboardButton("🕐 15:00 (Tarde)", callback_data="time_15:00")
            ],
            [
                InlineKeyboardButton("🕐 18:00 (Fin de Jornada)", callback_data="time_18:00"),
                InlineKeyboardButton("🕐 21:00 (Noche)", callback_data="time_21:00"),
                InlineKeyboardButton("🕐 Hora Personalizada", callback_data="time_custom")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="scheduling_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def recurring_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones recurrentes.
        
        Returns:
            InlineKeyboardMarkup: Teclado de recurrentes
        """
        keyboard = [
            [
                InlineKeyboardButton("📅 Una Vez", callback_data="recurring_once"),
                InlineKeyboardButton("📅 Diario", callback_data="recurring_daily"),
                InlineKeyboardButton("📅 Semanal", callback_data="recurring_weekly")
            ],
            [
                InlineKeyboardButton("📅 Mensual", callback_data="recurring_monthly"),
                InlineKeyboardButton("📅 Personalizado", callback_data="recurring_custom"),
                InlineKeyboardButton("🔙 Volver", callback_data="scheduling_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirmation_dialog(action: str, details: dict) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para acciones de broadcast.
        
        Args:
            action: Tipo de acción
            details: Detalles de la acción
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = []
        
        if action == "send":
            keyboard.append([
                InlineKeyboardButton("✅ Enviar Ahora", callback_data="confirm_send"),
                InlineKeyboardButton("❌ Cancelar", callback_data="broadcast_back")
            ])
        elif action == "schedule":
            keyboard.append([
                InlineKeyboardButton("✅ Programar", callback_data="confirm_schedule"),
                InlineKeyboardButton("❌ Cancelar", callback_data="broadcast_back")
            ])
        elif action == "delete":
            keyboard.append([
                InlineKeyboardButton("✅ Eliminar", callback_data=f"confirm_delete_{details['id']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="broadcast_back")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="broadcast_back")
            ])
        
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
                InlineKeyboardButton("📅 Por Fecha", callback_data="filter_by_date"),
                InlineKeyboardButton("📝 Por Tipo", callback_data="filter_by_type"),
                InlineKeyboardButton("👥 Por Audiencia", callback_data="filter_by_audience")
            ],
            [
                InlineKeyboardButton("📊 Por Estado", callback_data="filter_by_status"),
                InlineKeyboardButton("💰 Por Costo", callback_data="filter_by_cost"),
                InlineKeyboardButton("📈 Por Rendimiento", callback_data="filter_by_performance")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="broadcast_back")
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
                InlineKeyboardButton("🔙 Volver", callback_data="broadcast_back")
            ]
        ]
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
                InlineKeyboardButton("📝 Nuevo Broadcast", callback_data="quick_broadcast"),
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data="quick_stats"),
                InlineKeyboardButton("📋 Ver Historial", callback_data="quick_history")
            ],
            [
                InlineKeyboardButton("📅 Programados", callback_data="quick_scheduled"),
                InlineKeyboardButton("📋 Plantillas", callback_data="quick_templates"),
                InlineKeyboardButton("🔙 Volver", callback_data="broadcast_back")
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
                InlineKeyboardButton("📚 Tutorial Completo", callback_data="broadcast_tutorial"),
                InlineKeyboardButton("❓ Preguntas Frecuentes", callback_data="broadcast_faq")
            ],
            [
                InlineKeyboardButton("📊 Guía de Estadísticas", callback_data="stats_guide"),
                InlineKeyboardButton("📋 Guía de Plantillas", callback_data="templates_guide")
            ],
            [
                InlineKeyboardButton("💬 Contactar Soporte", callback_data="broadcast_support"),
                InlineKeyboardButton("🔙 Volver", callback_data="broadcast_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
