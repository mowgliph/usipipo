"""
Mensajes para soporte, tareas y logros del bot uSipipo.

Organiza los mensajes relacionados con:
- Centro de soporte y tickets
- Sistema de tareas
- Logros y recompensas

Author: uSipipo Team
Version: 1.0.0
"""


class SupportMessages:
    """Mensajes para el sistema de soporte."""
    
    # ============================================
    # SUPPORT TICKETS
    # ============================================
    
    class Tickets:
        """Mensajes de tickets de soporte."""
        
        MENU = (
            "🎫 **Centro de Soporte**\n"
            "━━━━━━━━━━━━\n\n"
            "¿Cómo podemos ayudarte?"
        )
        
        CATEGORIES = (
            "📋 **Categoría del Problema**\n\n"
            "• 🔌 Problemas de Conexión\n"
            "• 💳 Problemas de Pago\n"
            "• 👤 Cuenta y Perfil\n"
            "• 💡 Sugerencias\n"
            "• ❓ Otra (especificar)\n"
        )
        
        DESCRIBE = (
            "📝 **Describe tu problema**\n\n"
            "Sé lo más detallado posible:\n"
            "- Qué pasó\n"
            "- Cuándo ocurrió\n"
            "- Qué dispositivo usas\n\n"
            "Envía tu mensaje:"
        )
        
        SCREENSHOT = (
            "📸 **Adjuntar Evidencia (Opcional)**\n\n"
            "Si tienes un screenshot o video,\n"
            "puedes compartirlo ahora.\n\n"
            "O presiona Enviar para continuar."
        )
        
        CREATED = (
            "✅ **Ticket Creado**\n\n"
            "🆔 **ID del Ticket:** `{ticket_id}`\n"
            "📌 **Estado:** En Espera de Revisión\n"
            "⏰ **Creado:** {created_time}\n\n"
            "Nuestro equipo lo revisará pronto.\n"
            "Te notificaremos cuando haya respuesta."
        )
        
        LIST_HEADER = (
            "🎫 **Mis Tickets de Soporte**\n"
            "━━━━━━━━━━━━\n"
        )
        
        TICKET_ENTRY = (
            "🆔 #{ticket_id} - {category}\n"
            "   Creado: {created_time} | Estado: {status}\n"
            "   Respuestas: {reply_count}\n"
        )
        
        NO_TICKETS = (
            "📭 **Sin tickets**\n\n"
            "Aquí aparecerán tus consultas."
        )
        
        DETAIL = (
            "🎫 **Detalle del Ticket**\n"
            "━━━━━━━━━━━━\n\n"
            "🆔 **ID:** `{ticket_id}`\n"
            "📋 **Categoría:** {category}\n"
            "📌 **Estado:** {status}\n"
            "⏰ **Creado:** {created_time}\n"
            "👤 **Asignado a:** {assigned_to}\n\n"
            "**TU MENSAJE:**\n"
            "{message}\n\n"
            "**RESPUESTAS:**\n"
            "{replies}\n"
        )
        
        TICKET_CLOSED = (
            "✅ **Ticket Cerrado**\n\n"
            "El soporte ha resuelto tu problema.\n"
            "Si necesitas ayuda nuevamente,\n"
            "crea un nuevo ticket."
        )
        
        NEW_TICKET_ADMIN = (
            "🎫 **Nuevo Ticket de Soporte**\n\n"
            "👤 Usuario: {name}\n"
            "🆔 ID: {user_id}\n\n"
            "El usuario ha abierto un ticket de soporte."
        )
        
        OPEN_TICKET = (
            "🎫 **Soporte Abierto**\n\n"
            "✅ Tu ticket ha sido creado.\n\n"
            "Describe tu problema y te ayudaremos:\n\n"
            "🔴 Finalizar Soporte - para cerrar el ticket"
        )
        
        USER_MESSAGE_TO_ADMIN = (
            "💬 **Mensaje de Usuario**\n\n"
            "👤 De: {name}\n\n"
            "{text}"
        )
        
        ADMIN_MESSAGE_TO_USER = (
            "💬 **Respuesta del Soporte**\n\n"
            "{text}\n\n"
            "🔴 Finalizar Soporte - para cerrar"
        )
        
        REOPEN_CONFIRM = (
            "⚠️ **Reabrirs el Ticket?**\n\n"
            "🆔 ID: `{ticket_id}`\n\n"
            "¿Deseas reportar que el problema\n"
            "no fue resuelto?"
        )
    
    # ============================================
    # FAQ & KNOWLEDGE BASE
    # ============================================
    
    class FAQ:
        """Mensajes de preguntas frecuentes."""
        
        CATEGORIES = (
            "❓ **Preguntas Frecuentes**\n\n"
            "Selecciona un tema:"
        )
        
        CONNECTION_ISSUES = (
            "🔌 **Problemas de Conexión**\n"
            "━━━━━━━━━━━━\n\n"
            "❓ **¿Por qué no conecta?**\n"
            "✓ Verifica tu WiFi\n"
            "✓ Reinicia la app\n"
            "✓ Prueba otra llave\n\n"
            "❓ **¿Es lento?**\n"
            "✓ Acércate al router\n"
            "✓ Cambia de servidor\n"
            "✓ Reduce otros downloads\n\n"
            "❓ **¿Se desconecta?**\n"
            "✓ Actualiza la app\n"
            "✓ Borra caché y datos\n"
            "✓ Crea una nueva llave\n"
        )
        
        PAYMENT_ISSUES = (
            "💳 **Problemas de Pago**\n"
            "━━━━━━━━━━━━\n\n"
            "❓ **¿No puedo pagar?**\n"
            "✓ Verifica tu tarjeta\n"
            "✓ Intenta otro método\n"
            "✓ Contacta a soporte\n\n"
            "❓ **¿No me acreditó?**\n"
            "✓ Espera 5-10 minutos\n"
            "✓ Recarga la página\n"
            "✓ Abre un ticket\n\n"
            "❓ **¿Cómo obtengo factura?**\n"
            "✓ Iré a tu email\n"
            "✓ En la sección de Transacciones\n"
            "✓ O contacta a soporte\n"
        )
        
        VIP_INFO = (
            "👑 **Información sobre VIP**\n"
            "━━━━━━━━━━━━\n\n"
            "❓ **¿Qué incluye VIP?**\n"
            "✓ Datos ilimitados\n"
            "✓ 10 conexiones simultáneas\n"
            "✓ Acceso a todos los servidores\n"
            "✓ Bonus de referidos 5x\n\n"
            "❓ **¿Se puede cancelar?**\n"
            "✓ Sí, en cualquier momento\n"
            "✓ Conservas acceso hasta expiración\n\n"
            "❓ **¿Puedo cambiar de plan?**\n"
            "✓ Sí, cuando sea\n"
            "✓ Se ajustará el precio\n"
        )
    
    # ============================================
    # NOTIFICATIONS
    # ============================================
    
    class Notifications:
        """Mensajes de notificaciones."""
        
        SUPPORT_REPLY = (
            "💬 **Nueva Respuesta de Soporte**\n\n"
            "🆔 Ticket: `{ticket_id}`\n"
            "📋 Categoría: {category}\n\n"
            "{message}\n\n"
            "👉 Responde en el bot para continuar."
        )
        
        TICKET_ASSIGNED = (
            "👤 **Tu Ticket ha sido Asignado**\n\n"
            "🆔 `{ticket_id}`\n"
            "👨‍💼 Asignado a: {support_name}\n\n"
            "Será revisado en breve."
        )
        
        KEY_EXPIRING = (
            "⏰ **Tu Llave Está por Expirar**\n\n"
            "🔑 {key_name}\n"
            "⏳ Expira en: {days} días\n\n"
            "Crea una nueva para mantener acceso."
        )


class TaskMessages:
    """Mensajes para el sistema de tareas."""
    
    # ============================================
    # USER TASKS
    # ============================================
    
    class UserTasks:
        """Mensajes de tareas para usuarios."""
        
        MENU = (
            "📋 **Mis Tareas**\n"
            "━━━━━━━━━━━━\n\n"
            "Completa tareas y gana recompensas.\n\n"
            "🏆 **Tareas disponibles:** {available_count}\n"
            "✅ **Completadas hoy:** {completed_today}\n"
            "⭐ **Puntos totales:** {total_points}\n"
        )
        
        SUMMARY = (
            "📊 **Resumen de Tareas**\n"
            "━━━━━━━━━━━━\n\n"
            "✅ **Disponibles:** {available}\n"
            "⏳ **En progreso:** {in_progress}\n"
            "🎯 **Completadas:** {completed}\n"
        )
        
        AVAILABLE = (
            "📋 **Tareas Disponibles**\n"
            "━━━━━━━━━━━━\n"
        )
        
        TASK_ENTRY = (
            "📌 {task_name}\n"
            "   Descripción: {description}\n"
            "   Recompensa: {reward} ⭐ | {time_limit} horas\n"
        )
        
        NO_TASKS = (
            "✨ **No hay tareas**\n\n"
            "Vuelve pronto para nuevas oportunidades."
        )
        
        TASK_DETAIL = (
            "📌 **{task_name}**\n"
            "━━━━━━━━━━━━\n\n"
            "📝 {description}\n\n"
            "🎁 **Recompensa:** {reward} ⭐\n"
            "⏰ **Tiempo límite:** {time_limit} horas\n"
            "📊 **Dificultad:** {difficulty}\n"
            "👥 **Completadas por:** {completed_count} usuarios\n\n"
            "{requirements}"
        )
        
        TASK_GUIDE = (
            "📖 **Guía de la Tarea**\n\n"
            "{guide_text}\n"
        )
        
        TASK_COMPLETED = (
            "✅ **Tarea Completada**\n\n"
            "🎉 **{title}**\n"
            "⭐ **Recompensa:** {reward_stars} estrellas\n\n"
            "¡Excelente trabajo!"
        )
        
        REWARD_CLAIMED = (
            "🎁 **Recompensa Reclamada**\n\n"
            "⭐ **{reward_stars} estrellas** recibidas\n"
            "💰 **Balance actual:** {balance} estrellas\n\n"
            "¡Sigue así!"
        )
        
        COMPLETED = (
            "✅ **Tarea Completada**\n\n"
            "🎉 {task_name}\n"
            "🎁 **Ganancias:** {reward} ⭐\n\n"
            "¡Excelente trabajo!"
        )
        
        INCOMPLETE = (
            "❌ **Tarea Incompleta**\n\n"
            "{task_name}\n\n"
            "Requisitos faltantes: {missing}"
        )
    
    # ============================================
    # ADMIN TASKS
    # ============================================
    
    class AdminTasks:
        """Mensajes de gestión de tareas (admin)."""
        
        MENU = (
            "📋 **Gestión de Tareas**\n"
            "━━━━━━━━━━━━\n\n"
            "• ➕ Crear Nueva\n"
            "• 📊 Listar Todas\n"
            "• ✏️ Editar\n"
            "• 🗑️ Eliminar\n"
        )
        
        CREATE_FORM = (
            "➕ **Crear Nueva Tarea**\n"
            "━━━━━━━━━━━━\n\n"
            "Nombre de la tarea:"
        )
        
        TASK_CREATED = (
            "✅ **Tarea Creada**\n\n"
            "🆔 ID: `{task_id}`\n"
            "📌 {task_name}\n"
            "🎁 Recompensa: {reward} ⭐\n"
        )
        
        LIST_HEADER = (
            "📋 **Todas las Tareas**\n"
            "━━━━━━━━━━━━\n"
        )
        
        TASK_ENTRY = (
            "🆔 {task_id} - {task_name}\n"
            "   Recompensa: {reward} ⭐ | Completadas: {completed_count}\n"
        )
        
        NO_TASKS = (
            "📭 **Sin tareas creadas**"
        )


class AchievementMessages:
    """Mensajes para el sistema de logros."""
    
    # ============================================
    # ACHIEVEMENTS
    # ============================================
    
    class Achievements:
        """Mensajes de logros y recompensas."""
        
        MENU = (
            "🏆 **Mis Logros**\n"
            "━━━━━━━━━━━━\n\n"
            "🏆 **Completados:** {completed_count}\n"
            "📈 **En Progreso:** {in_progress_count}\n"
            "⭐ **Puntos:** {total_points}\n"
            "🎁 **Recompensas Pendientes:** {pending_count}\n"
        )
        
        AVAILABLE = (
            "🏆 **Logros Disponibles**\n"
            "━━━━━━━━━━━━\n"
        )
        
        ACHIEVEMENT_ENTRY = (
            "{emoji} {name}\n"
            "   {description}\n"
            "   Progreso: {progress}% | Recompensa: {reward}\n"
        )
        
        UNLOCKED = (
            "🎉 **¡Logro Desbloqueado!**\n\n"
            "{emoji} **{achievement_name}**\n\n"
            "⭐ **Recompensa:** {reward} puntos\n"
            "🎁 **Bonus:** {bonus}\n\n"
            "¡Qué emocionante!"
        )
        
        ACHIEVEMENT_DETAIL = (
            "{emoji} **{achievement_name}**\n"
            "━━━━━━━━━━━━\n\n"
            "{description}\n\n"
            "📊 **Progreso:** {progress}%\n"
            "⭐ **Recompensa:** {reward} puntos\n"
            "🎁 **Descripción:** {bonus_description}\n"
        )
        
        NO_ACHIEVEMENTS = (
            "🌱 **Empieza tu viaje**\n\n"
            "Completa acciones para desbloquear logros."
        )
    
    # ============================================
    # BADGES & REWARDS
    # ============================================
    
    class Badges:
        """Mensajes de insignias y recompensas."""
        
        EARNED = (
            "🥇 **Insignia Obtenida**\n\n"
            "{badge_emoji} **{badge_name}**\n"
            "{badge_description}\n"
        )
        
        PROFILE_BADGES = (
            "🥇 **Mis Insignias**\n"
            "━━━━━━━━━━━━\n"
        )
        
        BADGE_ENTRY = (
            "{badge_emoji} {badge_name}\n"
            "   Desbloqueada: {unlock_date}\n"
        )
        
        NO_BADGES = (
            "🌱 **Sin insignias aún**\n\n"
            "Completa logros para obtenerlas."
        )
