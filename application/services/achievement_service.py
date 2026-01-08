'''
Servicio de logros para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
'''

from datetime import datetime
from typing import List, Optional, Dict
from domain.entities.achievement import Achievement, UserAchievement, UserStats, AchievementType, get_achievements_by_type
from domain.interfaces.iachievement_service import IAchievementService
from domain.interfaces.iachievement_repository import IAchievementRepository, IUserStatsRepository
from utils.logger import logger

class AchievementService(IAchievementService):
    '''Implementación del servicio de logros.'''
    
    def __init__(
        self, 
        achievement_repository: IAchievementRepository,
        user_stats_repository: IUserStatsRepository
    ):
        self.achievement_repository = achievement_repository
        self.user_stats_repository = user_stats_repository
    
    async def initialize_user_achievements(self, user_id: int) -> None:
        '''Inicializa todos los logros para un nuevo usuario.'''
        try:
            # Obtener todos los logros disponibles
            achievements = await self.achievement_repository.get_all_achievements()
            
            # Crear registro de estadísticas iniciales
            logger.debug(f"Initializing user_stats for user_id {user_id}")
            user_stats = UserStats(user_id=user_id)
            await self.user_stats_repository.create_user_stats(user_stats)
            
            # Crear registros de progreso para cada logro
            for achievement in achievements:
                existing_user_achievement = await self.achievement_repository.get_user_achievement(
                    user_id, achievement.id
                )
                
                if not existing_user_achievement:
                    # Crear si no existe
                    user_achievement = UserAchievement(
                        user_id=user_id,
                        achievement_id=achievement.id
                    )
                    await self.achievement_repository.create_user_achievement(user_achievement)
            
            logger.info(f"Logros inicializados para usuario {user_id}")
            
        except Exception as e:
            logger.error(f"Error inicializando logros para usuario {user_id}: {e}")
            raise
    
    async def update_user_stats(self, user_id: int, stats_update: Dict) -> None:
        '''Actualiza las estadísticas de un usuario y verifica logros.'''
        try:
            # Obtener estadísticas actuales
            user_stats = await self.user_stats_repository.get_user_stats(user_id)
            if not user_stats:
                # Crear si no existen
                user_stats = UserStats(user_id=user_id)
                await self.user_stats_repository.create_user_stats(user_stats)
            
            # Actualizar estadísticas según el tipo
            updated_achievements = []
            
            if 'data_consumed_gb' in stats_update:
                user_stats.update_data_consumed(stats_update['data_consumed_gb'])
                updated_achievements.extend(
                    await self.check_and_update_achievements(
                        user_id, 
                        AchievementType.DATA_CONSUMED, 
                        int(user_stats.total_data_consumed_gb)
                    )
                )
            
            if 'daily_activity' in stats_update and stats_update['daily_activity']:
                user_stats.update_daily_activity()
                updated_achievements.extend(
                    await self.check_and_update_achievements(
                        user_id, 
                        AchievementType.DAYS_ACTIVE, 
                        user_stats.days_active
                    )
                )
            
            if 'referral' in stats_update and stats_update['referral']:
                user_stats.increment_referrals()
                updated_achievements.extend(
                    await self.check_and_update_achievements(
                        user_id, 
                        AchievementType.REFERRALS_COUNT, 
                        user_stats.total_referrals
                    )
                )
            
            if 'stars_deposited' in stats_update:
                user_stats.add_stars_deposited(stats_update['stars_deposited'])
                updated_achievements.extend(
                    await self.check_and_update_achievements(
                        user_id, 
                        AchievementType.STARS_DEPOSITED, 
                        user_stats.total_stars_deposited
                    )
                )
            
            if 'key_created' in stats_update and stats_update['key_created']:
                user_stats.increment_keys_created()
                updated_achievements.extend(
                    await self.check_and_update_achievements(
                        user_id, 
                        AchievementType.KEYS_CREATED, 
                        user_stats.total_keys_created
                    )
                )
            
            if 'game_won' in stats_update and stats_update['game_won']:
                user_stats.increment_games_won()
                updated_achievements.extend(
                    await self.check_and_update_achievements(
                        user_id, 
                        AchievementType.GAMES_WON, 
                        user_stats.total_games_won
                    )
                )
            
            if 'vip_months' in stats_update:
                user_stats.add_vip_months(stats_update['vip_months'])
                updated_achievements.extend(
                    await self.check_and_update_achievements(
                        user_id, 
                        AchievementType.VIP_MONTHS, 
                        user_stats.vip_months_purchased
                    )
                )
            
            # Guardar estadísticas actualizadas
            await self.user_stats_repository.update_user_stats(user_stats)
            
            # Log de logros actualizados
            if updated_achievements:
                logger.info(f"Usuario {user_id} completó {len(updated_achievements)} nuevos logros")
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas para usuario {user_id}: {e}")
            raise
    
    async def check_and_update_achievements(self, user_id: int, achievement_type: AchievementType, new_value: int) -> List[Achievement]:
        '''Verifica y actualiza logros basados en un nuevo valor.'''
        completed_achievements = []
        
        try:
            # Obtener logros del tipo específico
            achievements = await self.achievement_repository.get_achievements_by_type(achievement_type)
            
            for achievement in achievements:
                # Obtener progreso actual del usuario para este logro
                user_achievement = await self.achievement_repository.get_user_achievement(
                    user_id, achievement.id
                )
                
                if not user_achievement:
                    # Crear si no existe
                    user_achievement = UserAchievement(
                        user_id=user_id,
                        achievement_id=achievement.id
                    )
                    await self.achievement_repository.create_user_achievement(user_achievement)
                
                # Actualizar progreso
                if user_achievement.update_progress(new_value):
                    # El logro se completó
                    await self.achievement_repository.update_user_achievement(user_achievement)
                    completed_achievements.append(achievement)
                    logger.info(f"Usuario {user_id} completó logro: {achievement.name}")
                else:
                    # Actualizar progreso aunque no se haya completado
                    await self.achievement_repository.update_user_achievement(user_achievement)
            
        except Exception as e:
            logger.error(f"Error verificando logros para usuario {user_id}: {e}")
            raise
        
        return completed_achievements
    
    async def claim_achievement_reward(self, user_id: int, achievement_id: str) -> bool:
        '''Reclama la recompensa de un logro completado.'''
        try:
            # Obtener logro del usuario
            user_achievement = await self.achievement_repository.get_user_achievement(
                user_id, achievement_id
            )
            
            if not user_achievement or not user_achievement.is_completed:
                return False
            
            if user_achievement.reward_claimed:
                return False  # Ya reclamada
            
            # Obtener detalles del logro para conocer la recompensa
            achievement = await self.achievement_repository.get_achievement_by_id(achievement_id)
            if not achievement:
                return False
            
            # Marcar como reclamada
            if user_achievement.claim_reward():
                await self.achievement_repository.update_user_achievement(user_achievement)
                logger.info(f"Usuario {user_id} reclamó recompensa de {achievement.reward_stars} estrellas del logro {achievement.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error reclamando recompensa para usuario {user_id}, logro {achievement_id}: {e}")
            return False
    
    async def get_user_achievements_progress(self, user_id: int) -> Dict[str, UserAchievement]:
        '''Obtiene el progreso de todos los logros de un usuario.'''
        try:
            user_achievements = await self.achievement_repository.get_user_achievements(user_id)
            return {ua.achievement_id: ua for ua in user_achievements}
        except Exception as e:
            logger.error(f"Error obteniendo progreso de logros para usuario {user_id}: {e}")
            return {}
    
    async def get_user_completed_achievements(self, user_id: int) -> List[UserAchievement]:
        '''Obtiene los logros completados de un usuario.'''
        try:
            return await self.achievement_repository.get_completed_achievements(user_id)
        except Exception as e:
            logger.error(f"Error obteniendo logros completados para usuario {user_id}: {e}")
            return []
    
    async def get_user_pending_rewards(self, user_id: int) -> List[UserAchievement]:
        '''Obtiene las recompensas pendientes de un usuario.'''
        try:
            return await self.achievement_repository.get_pending_rewards(user_id)
        except Exception as e:
            logger.error(f"Error obteniendo recompensas pendientes para usuario {user_id}: {e}")
            return []
    
    async def get_achievement_leaderboard(self, achievement_type: AchievementType, limit: int = 10) -> List[Dict]:
        '''Obtiene el ranking de usuarios para un tipo de logro.'''
        try:
            return await self.user_stats_repository.get_leaderboard_by_type(achievement_type, limit)
        except Exception as e:
            logger.error(f"Error obteniendo leaderboard para tipo {achievement_type}: {e}")
            return []
    
    async def get_user_summary(self, user_id: int) -> Dict:
        '''Obtiene un resumen completo de logros del usuario.'''
        try:
            # Estadísticas del usuario
            user_stats = await self.user_stats_repository.get_user_stats(user_id)
            
            # Logros completados - convertir a lista para evitar problemas con async generators
            completed_achievements = await self.get_user_completed_achievements(user_id)
            completed_achievements = list(completed_achievements)
            
            # Recompensas pendientes
            pending_rewards = await self.get_user_pending_rewards(user_id)
            
            # Total de logros disponibles
            total_achievements = len(await self.achievement_repository.get_all_achievements())
            
            # Calcular progreso general
            completion_percentage = (len(completed_achievements) / total_achievements) * 100 if total_achievements > 0 else 0
            
            # Total de estrellas ganadas por logros
            total_reward_stars = 0
            for ua in completed_achievements:
                achievement = await self.achievement_repository.get_achievement_by_id(ua.achievement_id)
                if achievement:
                    total_reward_stars += achievement.reward_stars
 
            # Construir lista de logros recientes
            recent_achievements = []
            for ua in sorted(completed_achievements, key=lambda x: x.completed_at or datetime.min, reverse=True)[:5]:
                achievement = await self.achievement_repository.get_achievement_by_id(ua.achievement_id)
                if achievement:
                    recent_achievements.append({
                        'name': achievement.name,
                        'completed_at': ua.completed_at,
                        'reward_stars': achievement.reward_stars
                    })

            return {
                'user_stats': user_stats.to_dict() if user_stats else None,
                'completed_achievements': len(completed_achievements),
                'total_achievements': total_achievements,
                'completion_percentage': round(completion_percentage, 2),
                'pending_rewards': len(pending_rewards),
                'total_reward_stars': total_reward_stars,
                'recent_achievements': recent_achievements
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen para usuario {user_id}: {e}")
            return {}
    
    async def get_next_achievements(self, user_id: int, limit: int = 5) -> List[Dict]:
        '''Obtiene los próximos logros que el usuario puede completar.'''
        try:
            user_stats = await self.user_stats_repository.get_user_stats(user_id)
            if not user_stats:
                return []
            
            # Mapear valores actuales
            current_values = {
                AchievementType.DATA_CONSUMED: int(user_stats.total_data_consumed_gb),
                AchievementType.DAYS_ACTIVE: user_stats.days_active,
                AchievementType.REFERRALS_COUNT: user_stats.total_referrals,
                AchievementType.STARS_DEPOSITED: user_stats.total_stars_deposited,
                AchievementType.KEYS_CREATED: user_stats.total_keys_created,
                AchievementType.GAMES_WON: user_stats.total_games_won,
                AchievementType.VIP_MONTHS: user_stats.vip_months_purchased
            }
            
            # Obtener logros no completados
            all_user_achievements = await self.get_user_achievements_progress(user_id)
            next_achievements = []
            
            for achievement_type, current_value in current_values.items():
                # Obtener logros de este tipo
                achievements = await self.achievement_repository.get_achievements_by_type(achievement_type)
                
                for achievement in achievements:
                    user_achievement = all_user_achievements.get(achievement.id)
                    
                    # Solo considerar logros no completados
                    if not user_achievement or not user_achievement.is_completed:
                        progress_percentage = (current_value / achievement.requirement_value) * 100 if achievement.requirement_value > 0 else 0
                        
                        next_achievements.append({
                            'achievement': achievement.to_dict(),
                            'current_value': current_value,
                            'requirement_value': achievement.requirement_value,
                            'progress_percentage': min(progress_percentage, 100),
                            'remaining': max(0, achievement.requirement_value - current_value)
                        })
            
            # Ordenar por progreso y tomar los más cercanos
            next_achievements.sort(key=lambda x: x['progress_percentage'], reverse=True)
            return next_achievements[:limit]
            
        except Exception as e:
            logger.error(f"Error obteniendo próximos logros para usuario {user_id}: {e}")
            return []
