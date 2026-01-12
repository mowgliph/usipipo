"""
Mensajes para sistema de gestión de tareas de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""


class TaskManagementMessages:
    """Mensajes para sistema de gestión de tareas."""
    
    # ============================================
    # MENU
    #============================================
    
    class Menu:
        """Mensajes del menú de gestión de tareas."""
        
        MAIN = (
            "📋 **Centro de Gestión de Tareas**\n\n"
            "Sistema profesional de gestión de proyectos.\n\n"
            "📊 **Tus Estadísticas:**\n"
            "• Total de Tareas: {total_tasks}\n"
            "• Pendientes: {pending_tasks}\n"
            "• Completadas: {completed_tasks}\n"
            "• En Progreso: {in_progress}\n\n"
            "💡 *Organiza, asigna y sigue tus proyectos*"
        )
    
    # ============================================
    # CREATE
    #============================================
    
    class Create:
        """Mensajes de creación de tareas."""
        
        FORM = (
            "✍️ **Crear Nueva Tarea**\n\n"
            "Completa los siguientes campos:\n\n"
            "📝 **Título:** [Nombre de la tarea]\n"
            "📄 **Descripción:** [Detalles y objetivos]\n"
            "📅 **Fecha Límite:** [YYYY-MM-DD]\n"
            "🎯 **Prioridad:** [Alta/Media/Baja]\n"
            "👥 **Asignado a:** [Usuario o dejar vacío]\n"
            "🏷️ **Etiquetas:** [Separadas por comas]\n\n"
            "💡 *Usa formato claro y conciso*"
        )
        
        SUCCESS = (
            "✅ **Tarea Creada Exitosamente**\n\n"
            "Tu tarea ha sido creada y guardada.\n\n"
            "📋 **Detalles:**\n"
            "• Título: {title}\n"
            "• Prioridad: {priority}\n"
            "• Fecha límite: {due_date}\n"
            "• ID: {task_id}\n\n"
            "💡 *La tarea está lista para ser asignada*"
        )
        
        VALIDATION_ERROR = (
            "⚠️ **Error de Validación**\n\n"
            "La información de la tarea necesita ajustes:\n\n"
            "{validation_errors}\n\n"
            "💡 *Por favor, corrige los campos indicados*"
        )
    
    # ============================================
    # LIST
    #============================================
    
    class List:
        """Mensajes de lista de tareas."""
        
        NO_TASKS = (
            "📭 **Sin Tareas**\n\n"
            "No tienes tareas registradas.\n\n"
            "💡 *Crea tu primera tarea para empezar*"
        )
        
        HEADER = (
            "📋 **Tus Tareas**\n\n"
            "Lista de todas tus tareas activas:\n"
        )
        
        FILTER_OPTIONS = (
            "🔍 **Filtrar Tareas**\n\n"
            "Filtra tus tareas por:\n\n"
            "📊 **Estado:**\n"
            "• Todas\n"
            "• Pendientes\n"
            "• En progreso\n"
            "• Completadas\n\n"
            "🎯 **Prioridad:**\n"
            "• Alta\n"
            "• Media\n"
            "• Baja\n\n"
            "📅 **Fecha:**\n"
            "• Hoy\n"
            "• Esta semana\n"
            "• Este mes\n"
            "• Vencidas\n\n"
            "💡 *Combina filtros para mayor precisión*"
        )
    
    # ============================================
    # DETAILS
    #============================================
    
    class Details:
        """Mensajes de detalles de tareas."""
        
        TASK_DETAILS = (
            "📋 **Detalles de la Tarea**\n\n"
            "**{title}**\n\n"
            "📄 **Descripción:**\n{description}\n\n"
            "📊 **Estado:** {status}\n"
            "🎯 **Prioridad:** {priority}\n"
            "📅 **Creada:** {created_at}\n"
            "⏰ **Fecha Límite:** {due_date}\n"
            "👥 **Asignado a:** {assigned_to}\n"
            "📈 **Progreso:** {progress}\n"
            "🏷️ **Etiquetas:** {tags}\n\n"
            "💡 *Esta tarea está {status}*"
        )
        
        EDIT_FORM = (
            "✏️ **Editar Tarea**\n\n"
            "Actualiza los campos deseados:\n\n"
            "📝 **Título:** {title}\n"
            "📄 **Descripción:** {description}\n"
            "📊 **Estado:** {status}\n"
            "🎯 **Prioridad:** {priority}\n"
            "📅 **Fecha Límite:** {due_date}\n"
            "👥 **Asignado a:** {assigned_to}\n"
            "📈 **Progreso:** {progress}%\n"
            "🏷️ **Etiquetas:** {tags}\n\n"
            "💡 *Modifica solo los campos necesarios*"
        )
        
        UPDATE_SUCCESS = (
            "✅ **Tarea Actualizada**\n\n"
            "Los cambios han sido guardados.\n\n"
            "📋 **Detalles Actualizados:**\n"
            "• Título: {title}\n"
            "• Estado: {status}\n"
            "• Progreso: {progress}%\n\n"
            "💡 *La tarea está actualizada*"
        )
    
    # ============================================
    # ASSIGNMENT
    #============================================
    
    class Assignment:
        """Mensajes de asignación de tareas."""
        
        NO_USERS_AVAILABLE = (
            "📭 **Sin Usuarios Disponibles**\n\n"
            "No hay usuarios disponibles para asignar esta tarea.\n\n"
            "💡 *Invita más usuarios al equipo*"
        )
        
        SELECT_USER = (
            "👥 **Seleccionar Usuario**\n\n"
            "Asigna la tarea **{task_title}** a:\n\n"
            "💡 *Elige el usuario más adecuado para esta tarea*"
        )
        
        ASSIGNMENT_SUCCESS = (
            "✅ **Tarea Asignada**\n\n"
            "La tarea ha sido asignada exitosamente.\n\n"
            "📋 **Detalles:**\n"
            "• Tarea: {task_title}\n"
            "• Asignado a: {assigned_user}\n"
            "• ID: {task_id}\n\n"
            "💡 *El usuario recibirá una notificación*"
        )
    
    # ============================================
    # STATUS
    #============================================
    
    class Status:
        """Mensajes de estado de tareas."""
        
        UPDATE_SUCCESS = (
            "✅ **Estado Actualizado**\n\n"
            "El estado de la tarea ha sido cambiado.\n\n"
            "📋 **Detalles:**\n"
            "• Tarea: {task_title}\n"
            "• Estado anterior: {old_status}\n"
            "• Nuevo estado: {new_status}\n"
            "• ID: {task_id}\n\n"
            "💡 *El progreso ha sido actualizado*"
        )
        
        STATUS_OPTIONS = (
            "📊 **Actualizar Estado**\n\n"
            "Selecciona el nuevo estado:\n\n"
            "⏳ **Pendiente:**\n"
            "• Tarea no iniciada\n"
            "• Esperando asignación\n\n"
            "🔄 **En Progreso:**\n"
            "• Trabajo activo\n"
            "• Avance en curso\n\n"
            "✅ **Completada:**\n"
            "• Trabajo finalizado\n"
            "• Objetivos alcanzados\n\n"
            "⏸️ **Pausada:**\n"
            "• Trabajo temporalmente detenido\n"
            "• Esperando recursos\n\n"
            "❌ **Cancelada:**\n"
            "• Tarea anulada\n"
            "• Ya no es necesaria\n\n"
            "💡 *El estado afecta el progreso general*"
        )
    
    # ============================================
    # CALENDAR
    #============================================
    
    class Calendar:
        """Mensajes de calendario de tareas."""
        
        CALENDAR_HEADER = (
            "📅 **Calendario de Tareas**\n\n"
            "Tus tareas organizadas por fecha:\n"
        )
        
        NO_TASKS_TODAY = (
            "📅 **Sin Tareas Hoy**\n\n"
            "No tienes tareas programadas para hoy.\n\n"
            "💡 *Disfruta de tu día libre*"
        )
        
        UPCOMING_DEADLINES = (
            "⏰ **Próximas Fechas Límite**\n\n"
            "Tareas que vencen pronto:\n\n"
            "{deadline_tasks}\n\n"
            "💡 *Prioriza estas tareas*"
        )
        
        OVERDUE_TASKS = (
            "⚠️ **Tareas Vencidas**\n\n"
            "Tareas que han pasado su fecha límite:\n\n"
            "{overdue_tasks}\n\n"
            "💡 *Atiende estas tareas urgentemente*"
        )
    
    # ============================================
    # ERRORS
    #============================================
    
    class Error:
        """Mensajes de error."""
        
        SYSTEM_ERROR = (
            "❌ **Error del Sistema**\n\n"
            "No pude procesar tu solicitud de gestión de tareas.\n\n"
            "Por favor, intenta más tarde o contacta soporte."
        )
        
        TASK_NOT_FOUND = (
            "📭 **Tarea No Encontrada**\n\n"
            "La tarea solicitada no existe o no tienes acceso.\n\n"
            "💡 *Verifica el ID de la tarea*"
        )
        
        PREMIUM_REQUIRED = (
            "🔒 **Función Premium Requerida**\n\n"
            "La gestión de tareas es una función premium.\n\n"
            "💡 *Actualiza tu plan para acceder a esta función*"
        )
        
        ASSIGNMENT_FAILED = (
            "❌ **Error en Asignación**\n\n"
            "No pude asignar la tarea.\n\n"
            "Error: {error}\n\n"
            "💡 *Verifica los permisos del usuario*"
        )
        
        STATUS_UPDATE_FAILED = (
            "❌ **Error al Actualizar Estado**\n\n"
            "No pude actualizar el estado de la tarea.\n\n"
            "Error: {error}\n\n"
            "💡 *Intenta con un estado válido*"
        )
    
    # ============================================
    # SUCCESS
    #============================================
    
    class Success:
        """Mensajes de éxito."""
        
        TASK_COMPLETED = (
            "✅ **Tarea Completada**\n\n"
            "¡Felicidades! Has completado la tarea.\n\n"
            "📋 **Detalles:**\n"
            "• Tarea: {task_title}\n"
            "• Completada: {completion_date}\n"
            "• Tiempo empleado: {time_spent}\n\n"
            "💎 *¡Excelente trabajo!*"
        )
        
        MILESTONE_REACHED = (
            "🎯 **Hito Alcanzado**\n\n"
            "¡Has alcanzado un hito importante!\n\n"
            "🏆 **Logro:** {milestone_name}\n"
            "📊 **Progreso:** {progress}%\n"
            "🎁 **Recompensa:** {reward}\n\n"
            "💎 *¡Sigue así para alcanzar más metas!*"
        )
        
        PROJECT_COMPLETED = (
            "🎉 **Proyecto Completado**\n\n"
            "¡Has completado todas las tareas del proyecto!\n\n"
            "📊 **Estadísticas:**\n"
            "• Tareas totales: {total_tasks}\n"
            "• Tiempo total: {total_time}\n"
            "• Eficiencia: {efficiency}%\n\n"
            "🎁 **Recompensa del Proyecto:** {project_reward}\n\n"
            "💎 *¡Proyecto exitosamente completado!*"
        )
    
    # ============================================
    # TEMPLATES
    #============================================
    
    class Templates:
        """Mensajes de plantillas de tareas."""
        
        NO_TEMPLATES = (
            "📭 **Sin Plantillas**\n\n"
            "No hay plantillas de tareas guardadas.\n\n"
            "💡 *Crea plantillas para tareas repetitivas*"
        )
        
        LIST_HEADER = (
            "📋 **Plantillas de Tareas**\n\n"
            "Plantillas disponibles para usar:\n"
        )
        
        CREATE_SUCCESS = (
            "✅ **Plantilla Creada**\n\n"
            "Tu plantilla ha sido guardada.\n\n"
            "📋 **Detalles:**\n"
            "• Nombre: {template_name}\n"
            "• Descripción: {description}\n"
            "• ID: {template_id}\n\n"
            "💡 *Usa esta plantilla para crear tareas similares*"
        )
    
    # ============================================
    # COLLABORATION
    #============================================
    
    class Collaboration:
        """Mensajes de colaboración."""
        
        TEAM_OVERVIEW = (
            "👥 **Visión del Equipo**\n\n"
            "Estado actual del equipo:\n\n"
            "👤 **Miembros:** {team_members}\n"
            "📋 **Tareas Activas:** {active_tasks}\n"
            "✅ **Completadas Hoy:** {completed_today}\n"
            "📈 **Productividad:** {productivity}%\n\n"
            "💡 *Trabajando juntos para alcanzar objetivos*"
        )
        
        INVITATION_SENT = (
            "✅ **Invitación Enviada**\n\n"
            "La invitación ha sido enviada exitosamente.\n\n"
            "👤 **Invitado:** {user_name}\n"
            "📋 **Proyecto:** {project_name}\n"
            "📧 **Email:** {email}\n\n"
            "💡 *El usuario recibirá la invitación por email*"
        )
        
        MEMBER_JOINED = (
            "👋 **Nuevo Miembro**\n\n"
            "¡Un nuevo miembro se ha unido al equipo!\n\n"
            "👤 **Usuario:** {user_name}\n"
            "📅 **Fecha:** {join_date}\n"
            "🎯 **Rol:** {role}\n\n"
            "💡 *Bienvenido al equipo!*"
        )
    
    # ============================================
    # NOTIFICATIONS
    #============================================
    
    class Notifications:
        """Mensajes de notificaciones."""
        
        TASK_ASSIGNED = (
            "📋 **Nueva Tarea Asignada**\n\n"
            "Te han asignado una nueva tarea.\n\n"
            "📝 **Título:** {task_title}\n"
            "👤 **Asignado por:** {assigned_by}\n"
            "📅 **Fecha Límite:** {due_date}\n"
            "🎯 **Prioridad:** {priority}\n\n"
            "💡 *Revisa los detalles y empieza a trabajar*"
        )
        
        DEADLINE_REMINDER = (
            "⏰ **Recordatorio de Fecha Límite**\n\n"
            "Una tarea está por vencer.\n\n"
            "📝 **Título:** {task_title}\n"
            "📅 **Vence en:** {time_remaining}\n"
            "🎯 **Prioridad:** {priority}\n\n"
            "💡 *No olvides completarla a tiempo*"
        )
        
        TASK_COMPLETED_NOTIFICATION = (
            "✅ **Tarea Completada**\n\n"
            "Una tarea ha sido completada.\n\n"
            "📝 **Título:** {task_title}\n"
            "👤 **Completada por:** {completed_by}\n"
            "📅 **Fecha:** {completion_date}\n\n"
            "💡 *Excelente trabajo del equipo*"
        )
