"""
Teclados para sistema de referidos de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class ReferralKeyboards:
    """Teclados para sistema de referidos."""

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú principal de referidos.
        
        Returns:
            InlineKeyboardMarkup: Teclado del menú principal
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="referral_stats"),
                InlineKeyboardButton("👥 Lista de Referidos", callback_data="referral_list")
            ],
            [
                InlineKeyboardButton("📢 Compartir Enlace", callback_data="referral_share"),
                InlineKeyboardButton("🏆 Leaderboard", callback_data="referral_leaderboard")
            ],
            [
                InlineKeyboardButton("💰 Historial de Ganancias", callback_data="referral_earnings"),
                InlineKeyboardButton("💡 Consejos", callback_data="referral_tips")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_referral() -> InlineKeyboardMarkup:
        """
        Teclado para volver a referidos.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver a Referidos", callback_data="referral_back")
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
    def stats_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones de estadísticas.
        
        Returns:
            InlineKeyboardMarkup: Teclado de estadísticas
        """
        keyboard = [
            [
                InlineKeyboardButton("📈 Rendimiento", callback_data="referral_performance"),
                InlineKeyboardButton("📅 Histórico Mensual", callback_data="referral_monthly")
            ],
            [
                InlineKeyboardButton("🎯 Comparar con Promedio", callback_data="referral_compare"),
                InlineKeyboardButton("📊 Exportar Datos", callback_data="referral_export")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def list_actions(referral_count: int) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para lista de referidos.
        
        Args:
            referral_count: Cantidad de referidos
            
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = []
        
        if referral_count > 0:
            keyboard.append([
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data="referral_stats"),
                InlineKeyboardButton("💰 Ver Ganancias", callback_data="referral_earnings")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def share_actions(referral_link: str) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para compartir.
        
        Args:
            referral_link: Enlace de referido
            
        Returns:
            InlineKeyboardMarkup: Teclado de compartir
        """
        keyboard = [
            [
                InlineKeyboardButton("📋 Copiar Enlace", callback_data=f"copy_link_{referral_link}"),
                InlineKeyboardButton("📤 Compartir", callback_data=f"share_link_{referral_link}")
            ],
            [
                InlineKeyboardButton("📱 Compartir en WhatsApp", callback_data=f"share_whatsapp_{referral_link}"),
                InlineKeyboardButton("📧 Compartir por Email", callback_data=f"share_email_{referral_link}")
            ],
            [
                InlineKeyboardButton("📢 Compartir en Telegram", callback_data=f"share_telegram_{referral_link}"),
                InlineKeyboardButton("💡 Consejos", callback_data="referral_tips")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def leaderboard_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones del leaderboard.
        
        Returns:
            InlineKeyboardMarkup: Teclado de leaderboard
        """
        keyboard = [
            [
                InlineKeyboardButton("🎯 Mi Posición", callback_data="referral_my_rank"),
                InlineKeyboardButton("🎁 Recompensas", callback_data="referral_rewards")
            ],
            [
                InlineKeyboardButton("📊 Histórico", callback_data="referral_leaderboard_history"),
                InlineKeyboardButton("🏅 Medallas", callback_data="referral_medals")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def earnings_actions(earnings_count: int) -> InlineKeyboardMarkup:
        """
        Teclado de acciones de ganancias.
        
        Args:
            earnings_count: Cantidad de ganancias
            
        Returns:
            InlineKeyboardMarkup: Teclado de ganancias
        """
        keyboard = []
        
        if earnings_count > 0:
            keyboard.append([
                InlineKeyboardButton("💸 Retirar", callback_data="referral_withdraw"),
                InlineKeyboardButton("📊 Resumen Mensual", callback_data="referral_monthly_summary")
            ])
        
        keyboard.append([
            InlineKeyboardButton("📈 Ver Estadísticas", callback_data="referral_stats"),
            InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def tips_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones de consejos.
        
        Returns:
            InlineKeyboardMarkup: Teclado de consejos
        """
        keyboard = [
            [
                InlineKeyboardButton("🎯 Estrategias", callback_data="referral_strategies"),
                InlineKeyboardButton("🏆 Mejores Prácticas", callback_data="referral_best_practices")
            ],
            [
                InlineKeyboardButton("📱 Consejos Redes Sociales", callback_data="referral_social_tips"),
                InlineKeyboardButton("💬 Consejos Comunidad", callback_data="referral_community_tips")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def referral_details(referral_id: str) -> InlineKeyboardMarkup:
        """
        Teclado de detalles de referido.
        
        Args:
            referral_id: ID del referido
            
        Returns:
            InlineKeyboardMarkup: Teclado de detalles
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data=f"referral_stats_{referral_id}"),
                InlineKeyboardButton("💰 Ver Ganancias", callback_data=f"referral_earnings_{referral_id}")
            ],
            [
                InlineKeyboardButton("📧 Contactar", callback_data=f"referral_contact_{referral_id}"),
                InlineKeyboardButton("🔙 Volver", callback_data="referral_list")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def apply_referral() -> InlineKeyboardMarkup:
        """
        Teclado para aplicar código de referido.
        
        Returns:
            InlineKeyboardMarkup: Teclado de aplicación
        """
        keyboard = [
            [
                InlineKeyboardButton("🔑 Aplicar Código", callback_data="apply_referral_code"),
                InlineKeyboardButton("❓ ¿Cómo funciona?", callback_data="referral_how_it_works")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirmation_dialog(action: str, details: dict) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para acciones de referidos.
        
        Args:
            action: Tipo de acción
            details: Detalles de la acción
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = []
        
        if action == "withdraw":
            keyboard.append([
                InlineKeyboardButton(f"✅ Retirar ${details['amount']}", callback_data=f"confirm_withdraw_{details['amount']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="referral_back")
            ])
        elif action == "share":
            keyboard.append([
                InlineKeyboardButton("✅ Compartir", callback_data=f"confirm_share_{details['platform']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="referral_back")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="referral_back")
            ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def social_sharing(referral_link: str) -> InlineKeyboardMarkup:
        """
        Teclado para compartir en redes sociales.
        
        Args:
            referral_link: Enlace de referido
            
        Returns:
            InlineKeyboardMarkup: Teclado de redes sociales
        """
        keyboard = [
            [
                InlineKeyboardButton("📱 WhatsApp", callback_data=f"share_whatsapp_{referral_link}"),
                InlineKeyboardButton("📧 Telegram", callback_data=f"share_telegram_{referral_link}"),
                InlineKeyboardButton("📧 Email", callback_data=f"share_email_{referral_link}")
            ],
            [
                InlineKeyboardButton("📘 Facebook", callback_data=f"share_facebook_{referral_link}"),
                InlineKeyboardButton("🐦 Twitter", callback_data=f"share_twitter_{referral_link}"),
                InlineKeyboardButton("📷 Instagram", callback_data=f"share_instagram_{referral_link}")
            ],
            [
                InlineKeyboardButton("💼 LinkedIn", callback_data=f"share_linkedin_{referral_link}"),
                InlineKeyboardButton("📱 TikTok", callback_data=f"share_tiktok_{referral_link}"),
                InlineKeyboardButton("🎮 Discord", callback_data=f"share_discord_{referral_link}")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def performance_filters() -> InlineKeyboardMarkup:
        """
        Teclado de filtros de rendimiento.
        
        Returns:
            InlineKeyboardMarkup: Teclado de filtros
        """
        keyboard = [
            [
                InlineKeyboardButton("📅 Últimos 7 días", callback_data="filter_week"),
                InlineKeyboardButton("📅 Últimos 30 días", callback_data="filter_month"),
                InlineKeyboardButton("📅 Últimos 90 días", callback_data="filter_quarter")
            ],
            [
                InlineKeyboardButton("📊 Por Mes", callback_data="filter_monthly"),
                InlineKeyboardButton("📈 Por Semana", callback_data="filter_weekly"),
                InlineKeyboardButton("📅 Por Año", callback_data="filter_yearly")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def leaderboard_filters() -> InlineKeyboardMarkup:
        """
        Teclado de filtros del leaderboard.
        
        Returns:
            InlineKeyboardMarkup: Teclado de filtros
        """
        keyboard = [
            [
                InlineKeyboardButton("🏆 Top 10", callback_data="leaderboard_top_10"),
                InlineKeyboardButton("🎯 Mi Posición", callback_data="leaderboard_my_position"),
                InlineKeyboardButton("👥 Amigos", callback_data="leaderboard_friends")
            ],
            [
                InlineKeyboardButton("📅 Este Mes", callback_data="leaderboard_monthly"),
                InlineKeyboardButton("📅 Semana", callback_data="leaderboard_weekly"),
                InlineKeyboardButton("📅 Todo el Tiempo", callback_data="leaderboard_all_time")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
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
                InlineKeyboardButton("💾 Guardar en Nube", callback_data="export_cloud")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def withdrawal_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de retiro.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retiro
        """
        keyboard = [
            [
                InlineKeyboardButton("💳 Retirar Todo", callback_data="withdraw_all"),
                InlineKeyboardButton("💳 Retirar Parcial", callback_data="withdraw_partial")
            ],
            [
                InlineKeyboardButton("📊 Ver Saldo", callback_data="view_balance"),
                InlineKeyboardButton("📅 Próximo Pago", callback_data="next_payment")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def rewards_display() -> InlineKeyboardMarkup:
        """
        Teclado de visualización de recompensas.
        
        Returns:
            InlineKeyboardMarkup: Teclado de recompensas
        """
        keyboard = [
            [
                InlineKeyboardButton("🏆 Ver Recompensas Actuales", callback_data="view_current_rewards"),
                InlineKeyboardButton("🎁 Historial de Recompensas", callback_data="rewards_history")
            ],
            [
                InlineKeyboardButton("📊 Cómo Ganar Más", callback_data="how_to_earn_more"),
                InlineKeyboardButton("🎯 Metas y Logros", callback_data="goals_achievements")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def help_options() -> InlineKeyboardMarkup:
        """
        Teclado de opciones de ayuda.
        
        Returns:
            InlineKeyboardMarkup: Teclado de ayuda
        """
        keyboard = [
            [
                InlineKeyboardButton("📚 Tutorial Completo", callback_data="tutorial_full"),
                InlineKeyboardButton("❓ Preguntas Frecuentes", callback_data="faq")
            ],
            [
                InlineKeyboardButton("💬 Contactar Soporte", callback_data="contact_support"),
                InlineKeyboardButton("📖 Guía Rápida", callback_data="quick_guide")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
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
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data="referral_stats"),
                InlineKeyboardButton("📢 Compartir Enlace", callback_data="referral_share"),
                InlineKeyboardButton("🏆 Leaderboard", callback_data="referral_leaderboard")
            ],
            [
                InlineKeyboardButton("💰 Ver Ganancias", callback_data="referral_earnings"),
                InlineKeyboardButton("💡 Consejos", callback_data="referral_tips"),
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
