"""
Mensajes del sistema de juegos para el bot uSipipo.

Author: uSipipo Team
Version: 2.0.0
"""

class GameMessages:
    """Mensajes del sistema de juegos."""
    
    # Menú principal de juegos
    MENU = """🎮 **Play & Earn** 🎮

¡Gana estrellas jugando y úsalas para obtener planes VIP!

📊 **Límites semanales:**
• 1 juego por día
• Máximo 3 victorias por semana
• Reinicia cada lunes

Elige tu juego y buena suerte! 🍀"""

    # Estado del juego
    GAME_STATUS = """📊 **Tu Estado de Juego**

⭐ **Estrellas acumuladas:** {stars}
🎮 **Juegos jugados hoy:** {games_today}/1
🏆 **Victorias esta semana:** {weekly_wins}/3
📅 **Último juego:** {last_game}

{status_message}"""

    # Juegos individuales
    BOWLING_GAME = """🎳 **Bowling Challenge**

Lanza la bola y derriba todos los pines!

🏆 **Premio:** 1 estrella ⭐

¿Listo para lanzar? 🎳"""

    DARTS_GAME = """🎯 **Darts Master**

Apunta al centro y obtén la máxima puntuación!

🏆 **Premio:** 1 estrella ⭐

¿Preparado para disparar? 🎯"""

    DICE_GAME = """🎲 **Dice Roll**

Lanza los dados y obtén la combinación perfecta!

🏆 **Premio:** 1 estrella ⭐

¿Sientes la suerte? 🎲"""

    # Resultados
    WIN_MESSAGE = """🎉 **¡FELICIDADES! HAS GANADO!** 🎉

🏆 **Victoria en {game_type}**
⭐ **Estrellas ganadas:** +{stars}
💰 **Nuevo balance:** {total_stars} estrellas

¡Sigue jugando y acumula más estrellas! 🌟"""

    LOSE_MESSAGE = """😔 **No esta vez...** 😔

🎮 **{game_type}**
💭 **Sigue intentando, la suerte cambiará**
🎯 **Mañana podrás jugar de nuevo**

¡No te rindas! 🍀"""

    # Mensajes específicos para cada juego
    BOWLING_WIN_MESSAGE = """🎳 **¡STRIKE!** 🎳

🎯 ¡Derribaste todos los pines! 🎯
🏆 **Victoria en Bowling**
⭐ **Estrellas ganadas:** +{stars}
💰 **Nuevo balance:** {total_stars} estrellas

¡Eres un campeón del bowling! 🌟"""

    DARTS_WIN_MESSAGE = """🎯 **¡BULLSEYE!** 🎯

🎯 ¡Impacto en el centro! 50 puntos! 🎯
🏆 **Victoria en Dardos**
⭐ **Estrellas ganadas:** +{stars}
💰 **Nuevo balance:** {total_stars} estrellas

¡Eres un maestro de los dardos! 🌟"""

    DICE_WIN_MESSAGE = """🎲 **¡DOBLE SEIS!** 🎲

🎲 ¡Sacaste un 6 y un 6! 🎲
🏆 **Victoria en Dados**
⭐ **Estrellas ganadas:** +{stars}
💰 **Nuevo balance:** {total_stars} estrellas

¡La suerte está de tu lado! 🌟"""

    BOWLING_LOSE_MESSAGE = """🎳 **Casi lo logras...** 🎳

🎯 ¡Derribaste 5 pines! 🎯
😔 **No esta vez...**
🎯 **Mañana podrás jugar de nuevo**

¡Sigue practicando! 🍀"""

    DARTS_LOSE_MESSAGE = """🎯 **Casi en el blanco...** 🎯

🎯 ¡Impacto en el borde! 10 puntos! 🎯
😔 **No esta vez...**
🎯 **Mañana podrás jugar de nuevo**

¡Mejora tu puntería! 🍀"""

    DICE_LOSE_MESSAGE = """🎲 **Casi lo logras...** 🎲

🎲 ¡Sacaste un 2 y un 3! 🎲
😔 **No esta vez...**
🎯 **Mañana podrás jugar de nuevo**

¡La suerte cambiará! 🍀"""

    # Mensajes de restricción
    ALREADY_PLAYED_TODAY = """⏰ **Ya jugaste hoy**

Has usado tu juego diario disponible.

📅 **Próximo juego:** Mañana
⏰ **Vuelve en:** {hours_left} horas

¡Aprovecha para descansar y mañana tendrás nueva oportunidad! 🌙"""

    WEEKLY_LIMIT_REACHED = """🏆 **¡Límite semanal alcanzado!**

¡Felicidades! Has alcanzado el máximo de 3 victorias esta semana.

📅 **Reinicio:** Próximo lunes
🎯 **Sigue practicando** para la próxima semana

¡Eres un verdadero campeón! 🏆"""

    # Información de balance
    BALANCE_INFO = """💰 **Tu Balance de Estrellas**

⭐ **Estrellas disponibles:** {stars}
📅 **Última actualización:** {last_updated}

💡 **Usa tus estrellas para:**
• Comprar planes VIP
• Acceder a funciones premium
• Obtener beneficios exclusivos

¿Quieres canjear tus estrellas? /planes"""

    # Leaderboard
    LEADERBOARD = """🏆 **Tabla de Líderes** 🏆

{leaderboard_entries}

📊 **Tu posición:** #{your_position}
⭐ **Tus estrellas:** {your_stars}

¡Sigue jugando para subir en la tabla! 🎮"""

    # Ayuda
    HELP = """❓ **Ayuda - Play & Earn**

🎮 **¿Cómo funciona?**
1. Juega 1 vez al día (bowling, dardos o dados)
2. Gana hasta 3 veces por semana
3. Cada victoria = 1 estrella
4. Usa estrellas para comprar planes

💡 **Consejos:**🔄 **¿Cuándo se reinicia?**
• Juegos diarios: Cada 24 horas
• Victorias semanales: Cada lunes

¿Necesitas más ayuda? Contacta al administrador."""

    @staticmethod
    def get_game_emoji(game_type: str) -> str:
        """Obtener emoji según tipo de juego."""
        emojis = {
            'bowling': '🎳',
            'darts': '🎯',
            'dice': '🎲'
        }
        return emojis.get(game_type, '🎮')

    @staticmethod
    def get_game_name(game_type: str) -> str:
        """Obtener nombre del juego en español."""
        names = {
            'bowling': 'Bowling',
            'darts': 'Dardos',
            'dice': 'Dados'
        }
        return names.get(game_type, 'Juego')
