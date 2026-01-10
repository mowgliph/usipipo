"""
Teclados para sistema de juegos de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class GameKeyboards:
    """Teclados para sistema de juegos."""

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú principal de juegos.
        
        Returns:
            InlineKeyboardMarkup: Teclado del menú principal
        """
        keyboard = [
            [
                InlineKeyboardButton("🎰 Ruleta de la Suerte", callback_data="spin_wheel"),
                InlineKeyboardButton("🧠 Trivia", callback_data="trivia_menu")
            ],
            [
                InlineKeyboardButton("🎯 Desafíos Diarios", callback_data="daily_challenges"),
                InlineKeyboardButton("📊 Estadísticas", callback_data="game_stats")
            ],
            [
                InlineKeyboardButton("🏆 Leaderboard", callback_data="game_leaderboard"),
                InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_game() -> InlineKeyboardMarkup:
        """
        Teclado para volver a juegos.
        
        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver a Juegos", callback_data="game_back")
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
    def spin_wheel() -> InlineKeyboardMarkup:
        """
        Teclado para ruleta de la suerte.
        
        Returns:
            InlineKeyboardMarkup: Teclado de ruleta
        """
        keyboard = [
            [
                InlineKeyboardButton("🎰 Girar Ruleta", callback_data="play_spin_wheel"),
                InlineKeyboardButton("💎 Comprar Giros", callback_data="buy_spins")
            ],
            [
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data="spin_stats"),
                InlineKeyboardButton("🔙 Volver", callback_data="game_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def spin_result(prize: str) -> InlineKeyboardMarkup:
        """
        Teclado para resultado de ruleta.
        
        Args:
            prize: Premio ganado
            
        Returns:
            InlineKeyboardMarkup: Teclado de resultado
        """
        keyboard = []
        
        if "Giro Extra" in prize:
            keyboard.append([
                InlineKeyboardButton("🎰 Girar de Nuevo", callback_data="play_spin_wheel"),
                InlineKeyboardButton("📊 Ver Estadísticas", callback_data="spin_stats")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("🎰 Girar de Nuevo", callback_data="play_spin_wheel"),
                InlineKeyboardButton("🎯 Jugar Trivia", callback_data="trivia_menu")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Volver a Juegos", callback_data="game_back")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def buy_spins() -> InlineKeyboardMarkup:
        """
        Teclado para comprar giros.
        
        Returns:
            InlineKeyboardMarkup: Teclado de compra
        """
        keyboard = [
            [
                InlineKeyboardButton("💳 5 Giros - 5 estrellas", callback_data="buy_spins_5"),
                InlineKeyboardButton("💳 10 Giros - 9 estrellas", callback_data="buy_spins_10"),
                InlineKeyboardButton("💳 25 Giros - 20 estrellas", callback_data="buy_spins_25")
            ],
            [
                InlineKeyboardButton("💳 50 Giros - 35 estrellas", callback_data="buy_spins_50"),
                InlineKeyboardButton("💳 100 Giros - 60 estrellas", callback_data="buy_spins_100")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="game_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def trivia_categories() -> InlineKeyboardMarkup:
        """
        Teclado de categorías de trivia.
        
        Returns:
            InlineKeyboardMarkup: Teclado de categorías
        """
        keyboard = [
            [
                InlineKeyboardButton("🔧 Tecnología", callback_data="trivia_technology"),
                InlineKeyboardButton("🌍 Geografía", callback_data="trivia_geography"),
                InlineKeyboardButton("🎬 Entretenimiento", callback_data="trivia_entertainment")
            ],
            [
                InlineKeyboardButton("🔬 Ciencia", callback_data="trivia_science"),
                InlineKeyboardButton("🎮 Videojuegos", callback_data="trivia_games"),
                InlineKeyboardButton("🎲 Aleatorio", callback_data="trivia_random")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="game_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def trivia_answers(correct_answer: int) -> InlineKeyboardMarkup:
        """
        Teclado de respuestas de trivia.
        
        Args:
            correct_answer: Número de respuesta correcta
            
        Returns:
            InlineKeyboardMarkup: Teclado de respuestas
        """
        keyboard = [
            [
                InlineKeyboardButton("1️⃣", callback_data="trivia_answer_1"),
                InlineKeyboardButton("2️⃣", callback_data="trivia_answer_2"),
                InlineKeyboardButton("3️⃣", callback_data="trivia_answer_3"),
                InlineKeyboardButton("4️⃣", callback_data="trivia_answer_4")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def trivia_success() -> InlineKeyboardMarkup:
        """
        Teclado para trivia exitosa.
        
        Returns:
            InlineKeyboardMarkup: Teclado de éxito
        """
        keyboard = [
            [
                InlineKeyboardButton("🧠 Siguiente Pregunta", callback_data="trivia_next"),
                InlineKeyboardButton("🎰 Jugar Ruleta", callback_data="spin_wheel")
            ],
            [
                InlineKeyboardButton("🎯 Otro Tema", callback_data="trivia_menu"),
                InlineKeyboardButton("🔙 Volver", callback_data="game_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def trivia_retry() -> InlineKeyboardMarkup:
        """
        Teclado para reintento de trivia.
        
        Returns:
            InlineKeyboardMarkup: Teclado de reintento
        """
        keyboard = [
            [
                InlineKeyboardButton("🔄 Intentar de Nuevo", callback_data="trivia_retry"),
                InlineKeyboardButton("🧠 Otra Pregunta", callback_data="trivia_next"),
                InlineKeyboardButton("🎯 Cambiar Tema", callback_data="trivia_menu")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="game_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def challenges_actions() -> InlineKeyboardMarkup:
        """
        Teclado de acciones de desafíos.
        
        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = [
            [
                InlineKeyboardButton("🎯 Ver Desafíos", callback_data="view_challenges"),
                InlineKeyboardButton("📊 Progreso", callback_data="challenge_progress")
            ],
            [
                InlineKeyboardButton("🎁 Recompensas", callback_data="challenge_rewards"),
                InlineKeyboardButton("🔙 Volver", callback_data="game_back")
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
                InlineKeyboardButton("📈 Rendimiento", callback_data="performance_stats"),
                InlineKeyboardButton("🎯 Comparar", callback_data="compare_stats")
            ],
            [
                InlineKeyboardButton("📊 Historial", callback_data="stats_history"),
                InlineKeyboardButton("🏆 Leaderboard", callback_data="game_leaderboard")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="game_back")
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
                InlineKeyboardButton("🎯 Mi Posición", callback_data="my_rank"),
                InlineKeyboardButton("🎁 Recompensas", callback_data="leaderboard_rewards")
            ],
            [
                InlineKeyboardButton("📊 Histórico", callback_data="leaderboard_history"),
                InlineKeyboardButton("🏅 Medallas", callback_data="leaderboard_medals")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="game_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def game_over_actions(won: bool) -> InlineKeyboardMarkup:
        """
        Teclado de acciones fin de juego.
        
        Args:
            won: Si el usuario ganó
            
        Returns:
            InlineKeyboardMarkup: Teclado de fin de juego
        """
        keyboard = []
        
        if won:
            keyboard.append([
                InlineKeyboardButton("🎮 Jugar de Nuevo", callback_data="play_again"),
                InlineKeyboardButton("🎰 Probar Ruleta", callback_data="spin_wheel")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("🔄 Reintentar", callback_data="play_again"),
                InlineKeyboardButton("🎰 Probar Ruleta", callback_data="spin_wheel")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🧠 Jugar Trivia", callback_data="trivia_menu"),
            InlineKeyboardButton("🔙 Volver", callback_data="game_back")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirmation_dialog(action: str, details: dict) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para acciones de juegos.
        
        Args:
            action: Tipo de acción
            details: Detalles de la acción
            
        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = []
        
        if action == "buy_spins":
            keyboard.append([
                InlineKeyboardButton(f"✅ Comprar {details['spins']} giros", callback_data=f"confirm_buy_spins_{details['spins']}_{details['cost']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="game_back")
            ])
        elif action == "use_bonus":
            keyboard.append([
                InlineKeyboardButton("✅ Usar Bonus", callback_data="confirm_use_bonus"),
                InlineKeyboardButton("❌ Cancelar", callback_data="game_back")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="game_back")
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
                InlineKeyboardButton("🎰 Ruleta Rápida", callback_data="quick_spin"),
                InlineKeyboardButton("🧠 Trivia Rápida", callback_data="quick_trivia"),
                InlineKeyboardButton("🎯 Desafío Rápido", callback_data="quick_challenge")
            ],
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="game_stats"),
                InlineKeyboardButton("🏆 Leaderboard", callback_data="game_leaderboard"),
                InlineKeyboardButton("🔙 Volver", callback_data="game_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """
        Teclado de configuración de juegos.
        
        Returns:
            InlineKeyboardMarkup: Teclado de configuración
        """
        keyboard = [
            [
                InlineKeyboardButton("🔔 Notificaciones", callback_data="game_notifications"),
                InlineKeyboardButton("🎵 Sonidos", callback_data="game_sounds"),
                InlineKeyboardButton("🎨 Temas", callback_data="game_themes")
            ],
            [
                InlineKeyboardButton("📊 Privacidad", callback_data="game_privacy"),
                InlineKeyboardButton("💾 Guardar Progreso", callback_data="save_progress"),
                InlineKeyboardButton("🔄 Restablecer", callback_data="reset_game")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="game_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """
        Teclado de ayuda de juegos.
        
        Returns:
            InlineKeyboardMarkup: Teclado de ayuda
        """
        keyboard = [
            [
                InlineKeyboardButton("📚 Tutorial Completo", callback_data="game_tutorial"),
                InlineKeyboardButton("❓ Preguntas Frecuentes", callback_data="game_faq")
            ],
            [
                InlineKeyboardButton("🎯 Estrategias", callback_data="game_strategies"),
                InlineKeyboardButton("💡 Consejos", callback_data="game_tips")
            ],
            [
                InlineKeyboardButton("💬 Contactar Soporte", callback_data="game_support"),
                InlineKeyboardButton("🔙 Volver", callback_data="game_back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
