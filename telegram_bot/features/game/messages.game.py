"""
Mensajes para sistema de juegos de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""


class GameMessages:
    """Mensajes para sistema de juegos."""
    
    # ============================================
    # MENU
    # ============================================
    
    class Menu:
        """Mensajes del menú de juegos."""
        
        MAIN = (
            "🎮 **Centro de Juegos**\n\n"
            "¡Bienvenido al sistema Play & Earn!\n\n"
            "🎯 **Juegos Disponibles:**\n"
            "🎰 **Ruleta de la Suerte** - Gana estrellas instantáneas\n"
            "🧠 **Trivia** - Demuestra tu conocimiento\n"
            "🎯 **Desafíos Diarios** - Completa y gana recompensas\n\n"
            "💡 *Juega, diviértete y gana estrellas!*"
        )
    
    # ============================================
    # SPIN WHEEL
    # ============================================
    
    class SpinWheel:
        """Mensajes de ruleta de la suerte."""
        
        DESCRIPTION = (
            "🎰 **Ruleta de la Suerte**\n\n"
            "¡Gira la ruleta y gana estrellas!\n\n"
            "🎁 **Premios Posibles:**\n"
            "⭐ 5 Estrellas - 30% probabilidad\n"
            "⭐ 10 Estrellas - 20% probabilidad\n"
            "⭐ 25 Estrellas - 10% probabilidad\n"
            "⭐ 50 Estrellas - 5% probabilidad\n"
            "⭐ 100 Estrellas - 2% probabilidad\n"
            "💎 Giro Extra - 3% probabilidad\n"
            "😊 Suerte - 30% probabilidad\n\n"
            "💡 *Cada giro cuesta 1 estrella*"
        )
        
        NO_SPINS = (
            "⏳ **Sin Giros Disponibles**\n\n"
            "No tienes giros disponibles.\n\n"
            "💡 *Compra más giros o espera el bonus diario*"
        )
        
        RESULT = (
            "🎉 **Resultado de la Ruleta**\n\n"
            "🎁 **Premio:** {prize}\n"
            "💰 **Ganancias:** +{winnings} estrellas\n"
            "💳 **Nuevo Balance:** {new_balance} estrellas\n"
            "🔄 **Giros Restantes:** {spins_left}\n\n"
            "💡 *¡Felicidades por tu premio!*"
        )
    
    # ============================================
    # TRIVIA
    # ============================================
    
    class Trivia:
        """Mensajes de trivia."""
        
        DESCRIPTION = (
            "🧠 **Trivia uSipipo**\n\n"
            "Demuestra tu conocimiento y gana estrellas.\n\n"
            "📚 **Categorías Disponibles:**\n"
            "🔧 **Tecnología** - VPN, redes, seguridad\n"
            "🌍 **Geografía** - Países, capitales, cultura\n"
            "🎬 **Entretenimiento** - Películas, música, series\n"
            "🔬 **Ciencia** - Historia, descubrimientos\n"
            "🎮 **Videojuegos** - Clásicos y modernos\n\n"
            "💡 *Cada respuesta correcta vale 10 estrellas*"
        )
        
        NO_QUESTIONS = (
            "📭 **Sin Preguntas**\n\n"
            "No hay preguntas disponibles en esta categoría.\n\n"
            "💡 *Intenta con otra categoría*"
        )
        
        QUESTION = (
            "🧠 **Trivia: {category}**\n\n"
            "**Pregunta:**\n{question}\n\n"
            "**Opciones:**\n{options}\n\n"
            "💡 *Selecciona la respuesta correcta*"
        )
        
        CORRECT = (
            "✅ **¡Respuesta Correcta!**\n\n"
            "¡Excelente trabajo en la trivia de {category}!\n\n"
            "🎁 **Recompensa:** +{winnings} estrellas\n\n"
            "💡 *Sigue así para seguir ganando*"
        )
        
        INCORRECT = (
            "❌ **Respuesta Incorrecta**\n\n"
            "La respuesta correcta era: **{correct_answer}**\n\n"
            "💡 *No te desanimes, inténtalo de nuevo*"
        )
    
    # ============================================
    # CHALLENGES
    # ============================================
    
    class Challenges:
        """Mensajes de desafíos."""
        
        NO_CHALLENGES = (
            "📭 **Sin Desafíos**\n\n"
            "No hay desafíos disponibles hoy.\n\n"
            "💡 *Vuelve mañana para nuevos desafíos*"
        )
        
        LIST_HEADER = (
            "🎯 **Desafíos Diarios**\n\n"
            "Completa estos desafíos para ganar recompensas:\n"
        )
        
        COMPLETED = (
            "✅ **Desafío Completado**\n\n"
            "¡Has completado el desafío!\n\n"
            "🎁 **Recompensa:** {reward} estrellas\n"
            "📊 **Progreso:** 100%\n\n"
            "💡 *¡Excelente trabajo!*"
        )
    
    # ============================================
    # STATS
    # ============================================
    
    class Stats:
        """Mensajes de estadísticas."""
        
        USER_STATS = (
            "📊 **Tus Estadísticas de Juegos**\n\n"
            "🎮 **Total de Juegos:** {total_games}\n"
            "💰 **Ganancias Totales:** ${total_winnings:.2f}\n"
            "⭐ **Estrellas Ganadas:** {total_earnings}\n"
            "🎯 **Juego Favorito:** {favorite_game}\n"
            "📈 **Tasa de Victoria:** {win_rate:.1f}%\n"
            "🔥 **Racha Actual:** {current_streak} victorias\n\n"
            "💡 *Sigue mejorando tus estadísticas*"
        )
        
        PERFORMANCE = (
            "📈 **Rendimiento Detallado**\n\n"
            "🎮 **Últimos 7 días:**\n"
            "• Juegos jugados: {weekly_games}\n"
            "• Ganancias: ${weekly_earnings:.2f}\n"
            "• Tasa de victoria: {weekly_win_rate:.1f}%\n\n"
            "📊 **Comparación mensual:**\n"
            "• Mejora: {monthly_improvement:+.1f}%\n"
            "• Ranking: #{user_rank}\n\n"
            "💡 *Estás mejorando constantemente*"
        )
    
    # ============================================
    # LEADERBOARD
    # ============================================
    
    class Leaderboard:
        """Mensajes de leaderboard."""
        
        MAIN = (
            "🏆 **Leaderboard de Juegos**\n\n"
            "🎯 **Tu Posición:** #{user_rank}\n\n"
            "**Top Jugadores del Mes:**\n"
        )
        
        USER_RANK = (
            "🎯 **Tu Posición**\n\n"
            "🏆 **Posición Actual:** #{user_rank}\n"
            "🎮 **Juegos Jugados:** {games_played}\n"
            "💰 **Ganancias:** ${earnings:.2f}\n"
            "📈 **Tasa de Victoria:** {win_rate:.1f}%\n"
            "🔥 **Racha:** {streak} victorias\n\n"
            "💡 *Sigue así para llegar al top*"
        )
        
        REWARDS = (
            "🎁 **Recompensas del Leaderboard**\n\n"
            "🥇 **Top 1:** 500 estrellas + Badge Élite\n"
            "🥈 **Top 2-3:** 200 estrellas + Badge Oro\n"
            "🥉 **Top 4-10:** 100 estrellas + Badge Plata\n"
            "🎯 **Top 11-50:** 50 estrellas + Badge Bronce\n\n"
            "💡 *Las recompensas se pagan mensualmente*"
        )
    
    # ============================================
    # ERRORS
    # ============================================
    
    class Error:
        """Mensajes de error."""
        
        SYSTEM_ERROR = (
            "❌ **Error del Sistema**\n\n"
            "No pude procesar tu solicitud de juego.\n\n"
            "Por favor, intenta más tarde o contacta soporte."
        )
        
        INSUFFICIENT_FUNDS = (
            "💸 **Fondos Insuficientes**\n\n"
            "No tienes suficientes estrellas para este juego.\n\n"
            "💡 *Recarga tu balance para continuar*"
        )
        
        GAME_NOT_AVAILABLE = (
            "⏳ **Juego No Disponible**\n\n"
            "Este juego no está disponible temporalmente.\n\n"
            "💡 *Intenta más tarde o prueba otro juego*"
        )
    
    # ============================================
    # SUCCESS
    # ============================================
    
    class Success:
        """Mensajes de éxito."""
        
        GAME_COMPLETED = (
            "✅ **Juego Completado**\n\n"
            "¡Has completado el juego exitosamente!\n\n"
            "💎 *Disfruta de tus recompensas*"
        )
        
        ACHIEVEMENT_UNLOCKED = (
            "🏆 **Logro Desbloqueado**\n\n"
            "¡Has desbloqueado un nuevo logro!\n\n"
            "🎁 **Recompensa:** {reward} estrellas\n"
            "📊 **Progreso:** {progress}%\n\n"
            "💎 *¡Sigue así para desbloquear más logros!*"
        )
        
        DAILY_BONUS = (
            "🎁 **Bonus Diario Recibido**\n\n"
            "¡Has recibido tu bonus diario!\n\n"
            "⭐ **Giros Extra:** {bonus_spins}\n"
            "💰 **Estrellas:** {bonus_stars}\n\n"
            "💎 *Vuelve mañana para más recompensas*"
        )
