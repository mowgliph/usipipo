"""
Mensajes para sistema de logros de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram_bot.common.messages import CommonMessages


class AchievementsMessages:
    """Mensajes para sistema de logros."""
    
    # ============================================
    # MENU
    # ============================================
    
    class Menu:
        """Mensajes del menú principal."""
        
        MAIN = (
            "🏆 **Sistema de Logros**\n\n"
            "📊 **Progreso General:** {completed}/{total} logros desbloqueados\n"
            "⭐ **Puntos de Logro:** {stars}\n"
            "🎁 **Recompensas Pendientes:** {pending}\n\n"
            "Selecciona una opción para ver más detalles:"
        )
    
    # ============================================
    # PROGRESS
    # ============================================
    
    class Progress:
        """Mensajes de progreso."""
        
        OVERVIEW = (
            "📊 **Tu Progreso de Logros**\n\n"
            "✅ **Completados:** {completed}/{total} ({percentage}%)\n"
            "⭐ **Puntos Ganados:** {stars}\n"
            "🎁 **Recompensas Pendientes:** {pending}\n\n"
            "¡Sigue así para desbloquear más logros!"
        )
    
    # ============================================
    # LIST
    # ============================================
    
    class List:
        """Mensajes de lista de logros."""
        
        HEADER = "📋 **Lista de Logros**\n\n"
        
        NO_ACHIEVEMENTS = (
            "📭 **Sin logros disponibles**\n\n"
            "No hay logros disponibles en este momento.\n"
            "¡Vuelve pronto para nuevas oportunidades!"
        )
    
    # ============================================
    # REWARDS
    # ============================================
    
    class Reward:
        """Mensajes de recompensas."""
        
        CLAIMED = (
            "🎉 **¡Recompensa Reclamada!**\n\n"
            "Has recibido **{stars} ⭐** por completar:\n"
            "🏆 **{title}**\n\n"
            "¡Sigue así para desbloquear más logros!"
        )
        
        ALREADY_CLAIMED = (
            "⚠️ **Recompensa Ya Reclamada**\n\n"
            "Ya has recibido la recompensa de este logro.\n\n"
            "Revisa otros logros pendientes de completar."
        )
        
        NO_PENDING = (
            "📭 **Sin Recompensas Pendientes**\n\n"
            "No tienes recompensas pendientes por reclamar.\n\n"
            "¡Completa más logros para ganar recompensas!"
        )
    
    # ============================================
    # LEADERBOARD
    # ============================================
    
    class Leaderboard:
        """Mensajes del leaderboard."""
        
        HEADER = "🏆 **Tabla de Líderes**\n\n"
        
        NO_DATA = (
            "📭 **Sin Datos**\n\n"
            "No hay datos disponibles para el leaderboard.\n\n"
            "¡Sé el primero en aparecer aquí!"
        )
    
    # ============================================
    # ERRORS - Using common messages
    # ============================================
    
    class Error(CommonMessages.Error):
        """Mensajes de error específicos de logros."""
        
        ACHIEVEMENT_NOT_FOUND = (
            "❌ **Logro No Encontrado**\n\n"
            "El logro que buscas no existe.\n\n"
            "Por favor, selecciona un logro válido."
        )
        
        REWARD_ERROR = (
            "❌ **Error en Recompensa**\n\n"
            "No pude procesar tu recompensa.\n\n"
            "Por favor, intenta más tarde o contacta soporte."
        )
