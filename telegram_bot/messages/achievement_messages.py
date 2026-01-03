"""
Mensajes del sistema de logros para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

class AchievementMessages:
    """Mensajes relacionados con el sistema de logros."""
    
    class Menu:
        """Mensajes del menú de logros."""
        MAIN = """
🏆 **Sistema de Logros**

¡Desbloquea logros y gana estrellas! 🌟

📊 **Tu Progreso**
• Logros completados: {completed}/{total}
• Estrellas ganadas: {stars} ⭐
• Recompensas pendientes: {pending}

📋 **Opciones disponibles:
"""
        
        LIST_HEADER = """
🏆 **Tus Logros**

{total_achievements} logros disponibles • {completed} completados ({percentage}%)

📊 **Filtrar por tipo:**
"""
        
        ACHIEVEMENT_DETAIL = """
{icon} **{name}**
{description}

📈 **Progreso:** {current}/{requirement} ({progress}%)
🎁 **Recompensa:** {reward} estrellas
📅 **Estado:** {status}

{progress_bar}
"""
        
        NEXT_ACHIEVEMENTS = """
🎯 **Próximos Logros**

Estos son los logros más cercanos que puedes completar:

"""
        
        LEADERBOARD = """
🏆 **Ranking de {category}

{entries}
"""
        
        REWARDS_SUMMARY = """
🎁 **Recompensas Pendientes**

Tienes {count} logros completados esperando que reclames sus recompensas:

{achievements}

💰 **Total a reclamar:** {total_stars} estrellas

👇 Presiona en un logro para reclamar su recompensa:
"""
    
    class Notifications:
        """Mensajes de notificación de logros."""
        ACHIEVEMENT_UNLOCKED = """
🎉 **¡LOGRO DESBLOQUEADO!**

{icon} **{name}**
{description}

🎁 **Has ganado {reward} estrellas!**

💡 Usa el botón de abajo para reclamar tu recompensa.
"""
        
        REWARD_CLAIMED = """
✅ **Recompensa Reclamada**

{icon} **{name}**
🎁 {reward} estrellas han sido añadidas a tu balance.

💰 **Tu balance actual:** {balance} estrellas

¡Sigue así para desbloquear más logros! 🚀
"""
        
        MULTIPLE_ACHIEVEMENTS = """
🎊 **¡FELICIDADES!**

Has desbloqueado {count} logros nuevos:

{achievements}

🎁 **Total de estrellas ganadas:** {total_stars} estrellas

¡Impresionante! Sigue así para alcanzar la cima 🏆
"""
        
        MILESTONE_REACHED = """
🌟 **¡HITO ALCANZADO!**

Has completado {percentage}% de todos los logros disponibles!

📊 **Estadísticas:**
• Logros completados: {completed}/{total}
• Estrellas ganadas: {stars}
• Categorías dominadas: {categories}

¡Eres una leyenda en uSipipo! 🏆
"""
    
    class Progress:
        """Mensajes de progreso."""
        PROGRESS_UPDATE = """
📈 **Progreso Actualizado**

{icon} **{name}**
📊 Progreso: {current}/{requirement} ({progress}%)

{progress_bar}

🎯 **Te faltan {remaining} para completarlo!**
"""
        
        CLOSE_TO_ACHIEVEMENT = """
🔥 **¡Casi lo logras!**

{icon} **{name}**
📊 Progreso: {current}/{requirement} ({progress}%)

{progress_bar}

🎯 ¡Solo {remaining} más para desbloquearlo!
"""
    
    class Errors:
        """Mensajes de error."""
        NOT_FOUND = """
❌ **Logro no encontrado**

El logro que buscas no existe o no está disponible.

📋 Usa el menú principal para ver todos los logros disponibles.
"""
        
        ALREADY_CLAIMED = """
⚠️ **Recompensa ya reclamada**

Ya has reclamado la recompensa de este logro.

📊 Revisa tus logros completados en el menú principal.
"""
        
        NOT_COMPLETED = """
⏳ **Logro no completado**

Aún no has completado los requisitos para este logro.

📈 **Progreso actual:** {current}/{requirement}

¡Sigue esforzándote! 🚀
"""
        
        SYSTEM_ERROR = """
❌ **Error del sistema**

Ha ocurrido un error al procesar tu solicitud.

🔧 Por favor, inténtalo de nuevo más tarde.
Si el problema persiste, contacta con soporte.
"""
    
    class Categories:
        """Nombres de categorías."""
        DATA_CONSUMED = "📊 Consumo de Datos"
        DAYS_ACTIVE = "📅 Días Activos"
        REFERRALS_COUNT = "👥 Referidos"
        STARS_DEPOSITED = "💰 Estrellas Depositadas"
        KEYS_CREATED = "🔑 Claves Creadas"
        GAMES_WON = "🎮 Juegos Ganados"
        VIP_MONTHS = "👑 Meses VIP"
    
    class Tiers:
        """Nombres de niveles."""
        BRONZE = "🥉 Bronce"
        SILVER = "🥈 Plata"
        GOLD = "🥇 Oro"
        PLATINUM = "💎 Platino"
        DIAMOND = "💍 Diamante"
    
    @staticmethod
    def get_progress_bar(current: int, requirement: int, length: int = 20) -> str:
        """Genera una barra de progreso visual."""
        if requirement == 0:
            return "█" * length
        
        percentage = min((current / requirement) * 100, 100)
        filled = int((percentage / 100) * length)
        empty = length - filled
        
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {percentage:.1f}%"
    
    @staticmethod
    def format_achievement_list(achievements: list) -> str:
        """Formatea una lista de logros para mostrar."""
        if not achievements:
            return "No hay logros disponibles en esta categoría."
        
        formatted = []
        for achievement in achievements:
            status = "✅ Completado" if achievement.get('is_completed', False) else "⏳ En progreso"
            formatted.append(
                f"{achievement['icon']} **{achievement['name']}** - {status}"
            )
        
        return "\n".join(formatted)
    
    @staticmethod
    def format_leaderboard_entry(entry: dict, index: int) -> str:
        """Formatea una entrada del ranking."""
        medal = ""
        if index == 0:
            medal = "🥇"
        elif index == 1:
            medal = "🥈"
        elif index == 2:
            medal = "🥉"
        else:
            medal = f"#{index + 1}"
        
        return f"{medal} Usuario {entry['user_id']}: {entry['value']}"
