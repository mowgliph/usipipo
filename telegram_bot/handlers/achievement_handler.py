"""
Handler del sistema de logros para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from application.services.achievement_service import AchievementService
from telegram_bot.messages.achievement_messages import AchievementMessages
from telegram_bot.keyboard import Keyboards
from domain.entities.achievement import AchievementType
from utils.spinner import with_spinner, database_spinner

logger = logging.getLogger(__name__)

@database_spinner
async def achievements_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, achievement_service: AchievementService):
    """Maneja el menú principal de logros."""
    user_id = update.effective_user.id
    
    try:
        # Obtener resumen del usuario
        summary = await achievement_service.get_user_summary(user_id)
        
        if not summary:
            # Inicializar logros si no existen
            await achievement_service.initialize_user_achievements(user_id)
            summary = await achievement_service.get_user_summary(user_id)
        
        # Formatear mensaje principal
        message = AchievementMessages.Menu.MAIN.format(
            completed=summary.get('completed_achievements', 0),
            total=summary.get('total_achievements', 0),
            stars=summary.get('total_reward_stars', 0),
            pending=summary.get('pending_rewards', 0)
        )
        
        await update.message.reply_text(
            text=message,
            reply_markup=Keyboards.achievements_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en achievements_menu_handler: {e}")
        await update.message.reply_text(
            text=AchievementMessages.Errors.SYSTEM_ERROR,
            parse_mode="Markdown"
        )

async def achievements_progress_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, achievement_service: AchievementService):
    """Muestra el progreso general de logros del usuario."""
    user_id = update.effective_user.id
    
    try:
        summary = await achievement_service.get_user_summary(user_id)
        
        if not summary:
            await achievement_service.initialize_user_achievements(user_id)
            summary = await achievement_service.get_user_summary(user_id)
        
        message = f"""
📊 **Tu Progreso General**

🏆 **Logros Completados:** {summary.get('completed_achievements', 0)}/{summary.get('total_achievements', 0)}
📈 **Porcentaje de Completación:** {summary.get('completion_percentage', 0)}%
⭐ **Estrellas Ganadas:** {summary.get('total_reward_stars', 0)}
🎁 **Recompensas Pendientes:** {summary.get('pending_rewards', 0)}

📋 **Logros Recientes:**
"""
        
        recent_achievements = summary.get('recent_achievements', [])
        if recent_achievements:
            for achievement in recent_achievements:
                message += f"• {achievement['name']} - +{achievement['reward_stars']} estrellas\n"
        else:
            message += "Aún no has completado logros. ¡Empieza ahora! 🚀\n"
        
        await update.callback_query.edit_message_text(
            text=message,
            reply_markup=Keyboards.achievements_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en achievements_progress_handler: {e}")
        await update.callback_query.edit_message_text(
            text=AchievementMessages.Errors.SYSTEM_ERROR,
            parse_mode="Markdown"
        )

async def achievements_list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, achievement_service: AchievementService):
    """Muestra la lista de logros por categorías."""
    try:
        message = AchievementMessages.Menu.LIST_HEADER.format(
            total_achievements=56,  # Total predefinido
            completed=0,  # Se calculará dinámicamente
            percentage=0  # Se calculará dinámicamente
        )
        
        await update.callback_query.edit_message_text(
            text=message,
            reply_markup=Keyboards.achievements_categories(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en achievements_list_handler: {e}")
        await update.callback_query.edit_message_text(
            text=AchievementMessages.Errors.SYSTEM_ERROR,
            parse_mode="Markdown"
        )

async def achievements_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, achievement_service: AchievementService):
    """Muestra logros de una categoría específica."""
    user_id = update.effective_user.id
    query = update.callback_query
    
    try:
        # Extraer tipo de categoría del callback_data
        category_type = query.data.replace("achievements_category_", "")
        
        # Mapear a AchievementType
        type_mapping = {
            'data': AchievementType.DATA_CONSUMED,
            'days': AchievementType.DAYS_ACTIVE,
            'referrals': AchievementType.REFERRALS_COUNT,
            'stars': AchievementType.STARS_DEPOSITED,
            'keys': AchievementType.KEYS_CREATED,
            'games': AchievementType.GAMES_WON,
            'vip': AchievementType.VIP_MONTHS
        }
        
        if category_type not in type_mapping:
            await query.edit_message_text(
                text=AchievementMessages.Errors.NOT_FOUND,
                parse_mode="Markdown"
            )
            return
        
        achievement_type = type_mapping[category_type]
        
        # Obtener logros de esta categoría
        achievements = await achievement_service.achievement_repository.get_achievements_by_type(achievement_type)
        user_progress = await achievement_service.get_user_achievements_progress(user_id)
        
        # Formatear mensaje
        category_name = AchievementMessages.Categories.__dict__.get(f"{achievement_type.value.upper()}", "Categoría")
        message = f"{category_name}\n\n"
        
        for achievement in achievements:
            user_achievement = user_progress.get(achievement.id)
            current_value = user_achievement.current_value if user_achievement else 0
            progress_percentage = min((current_value / achievement.requirement_value) * 100, 100) if achievement.requirement_value > 0 else 0
            progress_bar = AchievementMessages.get_progress_bar(current_value, achievement.requirement_value)
            
            status = "✅ Completado" if (user_achievement and user_achievement.is_completed) else "⏳ En progreso"
            
            message += f"""
{achievement.icon} **{achievement.name}**
{achievement.description}

📈 **Progreso:** {current_value}/{achievement.requirement} ({progress_percentage:.1f}%)
{progress_bar}
🎁 **Recompensa:** {achievement.reward_stars} estrellas
📅 **Estado:** {status}

"""
        
        await query.edit_message_text(
            text=message,
            reply_markup=Keyboards.achievements_categories(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en achievements_category_handler: {e}")
        await query.edit_message_text(
            text=AchievementMessages.Errors.SYSTEM_ERROR,
            parse_mode="Markdown"
        )

async def achievements_next_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, achievement_service: AchievementService):
    """Muestra los próximos logros que el usuario puede completar."""
    user_id = update.effective_user.id
    
    try:
        next_achievements = await achievement_service.get_next_achievements(user_id, limit=5)
        
        if not next_achievements:
            message = """
🎯 **Próximos Logros**

¡Felicidades! Has completado todos los logros disponibles o no tienes progreso registrado.

📊 Usa el bot para empezar a desbloquear logros:
• Crea tu primera clave VPN
• Usa el bot diariamente
• Refiere a tus amigos
"""
            await update.callback_query.edit_message_text(
                text=message,
                reply_markup=Keyboards.achievements_menu(),
                parse_mode="Markdown"
            )
            return
        
        message = AchievementMessages.Menu.NEXT_ACHIEVEMENTS
        
        for next_ach in next_achievements:
            achievement = next_ach['achievement']
            progress_bar = AchievementMessages.get_progress_bar(
                next_ach['current_value'], 
                next_ach['requirement_value']
            )
            
            message += f"""
{achievement['icon']} **{achievement['name']}**
{achievement['description']}

{progress_bar}
📊 **Progreso:** {next_ach['current_value']}/{next_ach['requirement_value']}
🎯 **Te faltan:** {next_ach['remaining']} más
🎁 **Recompensa:** {achievement['reward_stars']} estrellas

"""
        
        await update.callback_query.edit_message_text(
            text=message,
            reply_markup=Keyboards.achievements_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en achievements_next_handler: {e}")
        await update.callback_query.edit_message_text(
            text=AchievementMessages.Errors.SYSTEM_ERROR,
            parse_mode="Markdown"
        )

async def achievements_rewards_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, achievement_service: AchievementService):
    """Muestra las recompensas pendientes del usuario."""
    user_id = update.effective_user.id
    
    try:
        pending_rewards = await achievement_service.get_user_pending_rewards(user_id)
        
        if not pending_rewards:
            message = """
🎁 **Recompensas Pendientes**

No tienes recompensas pendientes.

📊 Completa más logros para ganar estrellas:
• Usa 🎯 "Próximos Logros" para ver tu progreso
• Sigue usando el bot diariamente
• Refiere a tus amigos

¡Sigue así! 🚀
"""
            await update.callback_query.edit_message_text(
                text=message,
                reply_markup=Keyboards.achievements_menu(),
                parse_mode="Markdown"
            )
            return
        
        # Obtener detalles de los logros pendientes
        rewards_details = []
        total_stars = 0
        
        for user_achievement in pending_rewards:
            achievement = await achievement_service.achievement_repository.get_achievement_by_id(user_achievement.achievement_id)
            if achievement:
                rewards_details.append({
                    'id': achievement.id,
                    'name': achievement.name,
                    'icon': achievement.icon,
                    'reward_stars': achievement.reward_stars
                })
                total_stars += achievement.reward_stars
        
        # Formatear mensaje
        message = AchievementMessages.Menu.REWARDS_SUMMARY.format(
            count=len(pending_rewards),
            achievements="\n".join([
                f"{reward['icon']} **{reward['name']}** - +{reward['reward_stars']} estrellas"
                for reward in rewards_details
            ]),
            total_stars=total_stars
        )
        
        await update.callback_query.edit_message_text(
            text=message,
            reply_markup=Keyboards.pending_rewards(rewards_details),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en achievements_rewards_handler: {e}")
        await update.callback_query.edit_message_text(
            text=AchievementMessages.Errors.SYSTEM_ERROR,
            parse_mode="Markdown"
        )

async def claim_reward_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, achievement_service: AchievementService):
    """Maneja el reclamo de recompensas de logros."""
    user_id = update.effective_user.id
    query = update.callback_query
    
    try:
        # Extraer achievement_id del callback_data
        achievement_id = query.data.replace("claim_reward_", "")
        
        # Intentar reclamar la recompensa
        success = await achievement_service.claim_achievement_reward(user_id, achievement_id)
        
        if not success:
            # Obtener detalles del logro para dar mensaje específico
            user_achievement = await achievement_service.achievement_repository.get_user_achievement(user_id, achievement_id)
            achievement = await achievement_service.achievement_repository.get_achievement_by_id(achievement_id)
            
            if not achievement:
                message = AchievementMessages.Errors.NOT_FOUND
            elif user_achievement and user_achievement.reward_claimed:
                message = AchievementMessages.Errors.ALREADY_CLAIMED
            elif not (user_achievement and user_achievement.is_completed):
                current_value = user_achievement.current_value if user_achievement else 0
                message = AchievementMessages.Errors.NOT_COMPLETED.format(
                    current=current_value,
                    requirement=achievement.requirement_value
                )
            else:
                message = AchievementMessages.Errors.SYSTEM_ERROR
        else:
            # Éxito al reclamar
            achievement = await achievement_service.achievement_repository.get_achievement_by_id(achievement_id)
            user = await achievement_service.user_repository.get_user(user_id)
            balance = user.balance_stars if user else 0
            
            message = AchievementMessages.Notifications.REWARD_CLAIMED.format(
                icon=achievement.icon,
                name=achievement.name,
                reward=achievement.reward_stars,
                balance=balance
            )
        
        await query.edit_message_text(
            text=message,
            reply_markup=Keyboards.achievements_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en claim_reward_handler: {e}")
        await query.edit_message_text(
            text=AchievementMessages.Errors.SYSTEM_ERROR,
            parse_mode="Markdown"
        )

async def achievements_leaderboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, achievement_service: AchievementService):
    """Muestra el menú de rankings."""
    try:
        message = """
🏆 **Ranking de Logros**

Elige una categoría para ver el ranking de usuarios:

📊 **Categorías disponibles:**
• Consumo de Datos - Los que más navegan
• Días Activos - Los más constantes  
• Referidos - Los mejores influencers
• Estrellas - Los mayores inversores
• Top General - Los con más logros
"""
        
        await update.callback_query.edit_message_text(
            text=message,
            reply_markup=Keyboards.achievements_leaderboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en achievements_leaderboard_handler: {e}")
        await update.callback_query.edit_message_text(
            text=AchievementMessages.Errors.SYSTEM_ERROR,
            parse_mode="Markdown"
        )

async def leaderboard_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, achievement_service: AchievementService):
    """Muestra el ranking de una categoría específica."""
    query = update.callback_query
    
    try:
        # Extraer tipo de leaderboard del callback_data
        leaderboard_type = query.data.replace("leaderboard_", "")
        
        if leaderboard_type == "general":
            # Ranking general por logros completados
            top_users = await achievement_service.user_stats_repository.get_top_users_by_achievements(limit=10)
            category_name = "Top General - Logros Completados"
            
            entries = []
            for entry in top_users:
                medal = ""
                if entry['rank'] == 1:
                    medal = "🥇"
                elif entry['rank'] == 2:
                    medal = "🥈"
                elif entry['rank'] == 3:
                    medal = "🥉"
                else:
                    medal = f"#{entry['rank']}"
                
                entries.append(f"{medal} Usuario {entry['user_id']}: {entry['completed_count']} logros")
        else:
            # Ranking por categoría específica
            type_mapping = {
                'data': (AchievementType.DATA_CONSUMED, "Consumo de Datos (GB)"),
                'days': (AchievementType.DAYS_ACTIVE, "Días Activos"),
                'referrals': (AchievementType.REFERRALS_COUNT, "Referidos"),
                'stars': (AchievementType.STARS_DEPOSITED, "Estrellas Depositadas")
            }
            
            if leaderboard_type not in type_mapping:
                await query.edit_message_text(
                    text=AchievementMessages.Errors.NOT_FOUND,
                    parse_mode="Markdown"
                )
                return
            
            achievement_type, category_name = type_mapping[leaderboard_type]
            leaderboard = await achievement_service.get_achievement_leaderboard(achievement_type, limit=10)
            
            entries = []
            for entry in leaderboard:
                medal = ""
                if entry['rank'] == 1:
                    medal = "🥇"
                elif entry['rank'] == 2:
                    medal = "🥈"
                elif entry['rank'] == 3:
                    medal = "🥉"
                else:
                    medal = f"#{entry['rank']}"
                
                value = entry['value']
                if achievement_type == AchievementType.DATA_CONSUMED:
                    value = f"{value:.1f} GB"
                else:
                    value = str(value)
                
                entries.append(f"{medal} Usuario {entry['user_id']}: {value}")
        
        message = f"""
🏆 **{category_name}**

{chr(10).join(entries)}

📊 ¡Sigue esforzándote para aparecer en el ranking!
"""
        
        await query.edit_message_text(
            text=message,
            reply_markup=Keyboards.achievements_leaderboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en leaderboard_category_handler: {e}")
        await query.edit_message_text(
            text=AchievementMessages.Errors.SYSTEM_ERROR,
            parse_mode="Markdown"
        )
