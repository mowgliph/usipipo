"""
Teclados para sistema de anuncios de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class AnnouncerKeyboards:
    """Teclados para sistema de anuncios."""

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú principal de anuncios.
        
        Returns:
            InlineKeyboardMarkup: Teclado del menú principal
        """
        keyboard = [
            [
                InlineKeyboardButton("📝 Crear Campaña", callback_data="create_campaign"),
                InlineKeyboardButton("📋 Lista de Campañas", callback_data="campaign_list")
            ],
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="campaign_stats"),
                InlineKeyboardButton("📋 Plantillas", callback_data="ad_templates")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_announcer() -> InlineKeyboardMarkup:
        """
        Teclado para volver a anuncios.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver a Anuncios", callback_data="announcer_back")
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
    def create_campaign_form() -> InlineKeyboardMarkup:
        """
        Teclado para formulario de creación de campaña.
        
        Returns:
            InlineKeyboardMarkup: Teclado de formulario
        """
        keyboard = [
            [
                InlineKeyboardButton("📝 Completar Formulario", callback_data="fill_campaign_form"),
                InlineKeyboardButton("📋 Usar Plantilla", callback_data="use_campaign_template")
            ],
            [
                InlineKeyboardButton("📊 Ver Plantillas", callback_data="view_ad_templates"),
                InlineKeyboardButton("🔙 Volver", callback_data="announcer_back")
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
                InlineKeyboardButton("🎯 Personalizado", callback_data="audience_custom"),
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data="audience_stats")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="announcer_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def compose_ad_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones de composición de anuncios.
        
        Returns:
            InlineKeyboardMarkup: Teclado de composición
        """
        keyboard = [
            [
                InlineKeyboardButton("📝 Escribir Anuncio", callback_data="write_ad"),
                InlineKeyboardButton("📋 Usar Plantilla", callback_data="use_ad_template"),
                InlineKeyboardButton("👁️ Vista Previa", callback_data="preview_ad")
            ],
            [
                InlineKeyboardButton("📊 Ver Audiencia", callback_data="view_audience"),
                InlineKeyboardButton("💰 Ajustar Presupuesto", callback_data="adjust_budget"),
                InlineKeyboardButton("🔙 Volver", callback_data="announcer_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirm_campaign() -> InlineKeyboardMarkup:
        """
        Teclado de confirmación de campaña.
        
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = [
            [
                InlineKeyboardButton("✅ Lanzar Campaña", callback_data="launch_campaign"),
                InlineKeyboardButton("⏰ Programar", callback_data="schedule_campaign"),
                InlineKeyboardButton("💾 Guardar Borrador", callback_data="save_draft")
            ],
            [
                InlineKeyboardButton("📝 Editar Anuncio", callback_data="edit_ad"),
                InlineKeyboardButton("👥 Cambiar Audiencia", callback_data="change_audience"),
                InlineKeyboardButton("❌ Cancelar", callback_data="announcer_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def campaign_success() -> InlineKeyboardMarkup:
        """
        Teclado para campaña exitosa.
        
        Returns:
            InlineKeyboardMarkup: Teclado de éxito
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data="view_campaign_stats"),
                InlineKeyboardButton("📋 Ver Detalles", callback_data="view_campaign_details"),
                InlineKeyboardButton("📝 Crear Otra", callback_data="create_campaign")
            ],
            [
                InlineKeyboardButton("🔙 Volver a Anuncios", callback_data="announcer_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def campaign_actions(campaign_count: int) -> InlineKeyboardMarkup:
        """
        Teclado de acciones de campañas.
        
        Args:
            campaign_count: Cantidad de campañas
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = []
        
        if campaign_count > 0:
            keyboard.append([
                InlineKeyboardButton("📊 Estadísticas Generales", callback_data="general_stats"),
                InlineKeyboardButton("📈 Análisis de Rendimiento", callback_data="performance_analysis")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver a Anuncios", callback_data="announcer_back")
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
                InlineKeyboardButton("👥 Análisis de Audiencia", callback_data="audience_analysis"),
                InlineKeyboardButton("📊 Comparación", callback_data="comparison_stats")
            ],
            [
                InlineKeyboardButton("📅 Histórico", callback_data="historical_stats"),
                InlineKeyboardButton("💰 ROI Analysis", callback_data="roi_analysis"),
                InlineKeyboardButton("🎯 Métricas Clave", callback_data="key_metrics")
            ],
            [
                InlineKeyboardButton("🔙 Volver a Anuncios", callback_data="announcer_back")
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
                InlineKeyboardButton("🔙 Volver a Anuncios", callback_data="announcer_back")
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
                InlineKeyboardButton("⏸️ Pausar Campaña", callback_data="pause_campaign"),
                InlineKeyboardButton("🔙 Cancelar Programación", callback_data="cancel_schedule")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="announcer_back")
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
                InlineKeyboardButton("🕐 15:00 (Tarde)")
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
        Teclado de confirmación para acciones de anuncios.
        
        Args:
            action: Tipo de acción
            details: Detalles de la acción
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = []
        
        if action == "launch":
            keyboard.append([
                InlineKeyboardButton("✅ Lanzar Ahora", callback_data="confirm_launch"),
                InlineKeyboardButton("❌ Cancelar", callback_data="announcer_back")
            ])
        elif action == "schedule":
            keyboard.append([
                InlineKeyboardButton("✅ Programar", callback_data="confirm_schedule"),
                InlineKeyboardButton("❌ Cancelar", callback_data="announcer_back")
            ])
        elif action == "delete":
            keyboard.append([
                InlineKeyboardButton("✅ Eliminar", callback_data=f"confirm_delete_{details['id']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="announcer_back")
            ])
        elif action == "charge":
            keyboard.append([
                InlineKeyboardButton(f"✅ Pagar ${details['amount']}", callback_data="confirm_charge"),
                InlineKeyboardButton("❌ Cancelar", callback_data="announcer_back")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="announcer_back")
            ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def upgrade_to_announcer() -> InlineKeyboardMarkup:
        """
        Teclado para actualizar a anunciante.
        
        Returns:
            InlineKeyboardMarkup: Teclado de actualización
        """
        keyboard = [
            [
                InlineKeyboardButton("📢 Ver Planes de Anunciante", callback_data="announcer_plans"),
                InlineKeyboardButton("💎 Ver Beneficios", callback_data="announcer_benefits")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def budget_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de presupuesto.
        
        Returns:
            InlineKeyboardMarkup: Teclado de presupuesto
        """
        keyboard = [
            [
                InlineKeyboardButton("💰 $10", callback_data="budget_10"),
                InlineKeyboardButton("💰 $25", callback_data="budget_25"),
                InlineKeyboardButton("💰 $50", callback_data="budget_50")
            ],
            [
                InlineKeyboardButton("💰 $100", callback_data="budget_100"),
                InlineKeyboardButton("💰 $250", callback_data="budget_250"),
                InlineKeyboardButton("💰 $500", callback_data="budget_500")
            ],
            [
                InlineKeyboardButton("💰 Personalizado", callback_data="budget_custom"),
                InlineKeyboardButton("🔙 Volver", callback_data="announcer_back")
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
                InlineKeyboardButton("📅 Por Fecha", callback_data="filter_by_date"),
                InlineKeyboardButton("📊 Por Estado", callback_data="filter_by_status"),
                InlineKeyboardButton("👥 Por Audiencia", callback_data="filter_by_audience")
            ],
            [
                InlineKeyboardButton("💰 Por Presupuesto", callback_data="filter_by_budget"),
                InlineKeyboardButton("📈 Por Rendimiento", callback_data="filter_by_performance"),
                InlineKeyboardButton("🎯 Por Tipo", callback_data="filter_by_type")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="announcer_back")
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
                InlineKeyboardButton("🔙 Volver", callback_data="announcer_back")
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
                InlineKeyboardButton("📝 Nueva Campaña", callback_data="quick_campaign"),
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data="quick_stats"),
                InlineKeyboardButton("📋 Ver Campañas", callback_data="quick_campaigns")
            ],
            [
                InlineKeyboardButton("⏰ Programadas", callback_data="quick_scheduled"),
                InlineKeyboardButton("📋 Plantillas", callback_data="quick_templates"),
                InlineKeyboardButton("🔙 Volver", callback_data="announcer_back")
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
                InlineKeyboardButton("📚 Tutorial Completo", callback_data="announcer_tutorial"),
                InlineKeyboardButton("❓ Preguntas Frecuentes", callback_data="announcer_faq")
            ],
            [
                InlineKeyboardButton("📊 Guía de Estadísticas", callback_data="stats_guide"),
                InlineKeyboardButton("📋 Guía de Plantillas", callback_data="templates_guide")
            ],
            [
                InlineKeyboardButton("💬 Contactar Soporte", callback_data="announcer_support"),
                InlineKeyboardButton("🔙 Volver", callback_data="announcer_back")
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
                InlineKeyboardButton("🔙 Volver", callback_data="announcer_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def payment_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de pago.
        
        Returns:
            InlineKeyboardMarkup: Teclado de pago
        """
        keyboard = [
            [
                InlineKeyboardButton("💳 Balance de Cuenta", callback_data="pay_balance"),
                InlineKeyboardButton("💳 Tarjeta de Crédito", callback_data="pay_card"),
                InlineKeyboardButton("🏦 Transferencia Bancaria", callback_data="pay_transfer")
            ],
            [
                InlineKeyboardButton("₿ Criptomonedas", callback_data="pay_crypto"),
                InlineKeyboardButton("🔙 Cancelar", callback_data="announcer_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
