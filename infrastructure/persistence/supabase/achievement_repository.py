"""
Implementación del repositorio de logros para PostgreSQL.

Author: uSipipo Team
Version: 1.0.0
"""

import logging
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_
from domain.entities.achievement import Achievement, UserAchievement, UserStats, AchievementType
from domain.interfaces.iachievement_repository import IAchievementRepository, IUserStatsRepository

logger = logging.getLogger(__name__)

class AchievementRepository(IAchievementRepository):
    """Implementación del repositorio de logros."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_all_achievements(self) -> List[Achievement]:
        """Obtiene todos los logros activos."""
        try:
            from infrastructure.persistence.supabase.models import AchievementModel
            
            query = select(AchievementModel).where(AchievementModel.is_active == True)
            result = await self.db_session.execute(query)
            achievements = result.scalars().all()
            
            return [
                Achievement(
                    id=achievement.id,
                    name=achievement.name,
                    description=achievement.description,
                    type=AchievementType(achievement.type),
                    tier=achievement.tier,
                    requirement_value=achievement.requirement_value,
                    reward_stars=achievement.reward_stars,
                    icon=achievement.icon,
                    is_active=achievement.is_active
                )
                for achievement in achievements
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo todos los logros: {e}")
            return []
    
    async def get_achievement_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """Obtiene un logro por su ID."""
        try:
            from infrastructure.persistence.supabase.models import AchievementModel
            
            query = select(AchievementModel).where(
                and_(AchievementModel.id == achievement_id, AchievementModel.is_active == True)
            )
            result = await self.db_session.execute(query)
            achievement = result.scalar_one_or_none()
            
            if achievement:
                return Achievement(
                    id=achievement.id,
                    name=achievement.name,
                    description=achievement.description,
                    type=AchievementType(achievement.type),
                    tier=achievement.tier,
                    requirement_value=achievement.requirement_value,
                    reward_stars=achievement.reward_stars,
                    icon=achievement.icon,
                    is_active=achievement.is_active
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo logro {achievement_id}: {e}")
            return None
    
    async def get_achievements_by_type(self, achievement_type: AchievementType) -> List[Achievement]:
        """Obtiene logros por tipo."""
        try:
            from infrastructure.persistence.supabase.models import AchievementModel
            
            query = select(AchievementModel).where(
                and_(AchievementModel.type == achievement_type.value, AchievementModel.is_active == True)
            )
            result = await self.db_session.execute(query)
            achievements = result.scalars().all()
            
            return [
                Achievement(
                    id=achievement.id,
                    name=achievement.name,
                    description=achievement.description,
                    type=AchievementType(achievement.type),
                    tier=achievement.tier,
                    requirement_value=achievement.requirement_value,
                    reward_stars=achievement.reward_stars,
                    icon=achievement.icon,
                    is_active=achievement.is_active
                )
                for achievement in achievements
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo logros por tipo {achievement_type}: {e}")
            return []
    
    async def get_user_achievements(self, user_id: int) -> List[UserAchievement]:
        """Obtiene todos los logros de un usuario."""
        try:
            from infrastructure.persistence.supabase.models import UserAchievementModel
            
            query = select(UserAchievementModel).where(UserAchievementModel.user_id == user_id)
            result = await self.db_session.execute(query)
            user_achievements = result.scalars().all()
            
            return [
                UserAchievement(
                    user_id=ua.user_id,
                    achievement_id=ua.achievement_id,
                    current_value=ua.current_value,
                    is_completed=ua.is_completed,
                    completed_at=ua.completed_at,
                    reward_claimed=ua.reward_claimed,
                    reward_claimed_at=ua.reward_claimed_at
                )
                for ua in user_achievements
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo logros del usuario {user_id}: {e}")
            return []
    
    async def get_user_achievement(self, user_id: int, achievement_id: str) -> Optional[UserAchievement]:
        """Obtiene un logro específico de un usuario."""
        try:
            from infrastructure.persistence.supabase.models import UserAchievementModel
            
            query = select(UserAchievementModel).where(
                and_(UserAchievementModel.user_id == user_id, UserAchievementModel.achievement_id == achievement_id)
            )
            result = await self.db_session.execute(query)
            user_achievement = result.scalar_one_or_none()
            
            if user_achievement:
                return UserAchievement(
                    user_id=user_achievement.user_id,
                    achievement_id=user_achievement.achievement_id,
                    current_value=user_achievement.current_value,
                    is_completed=user_achievement.is_completed,
                    completed_at=user_achievement.completed_at,
                    reward_claimed=user_achievement.reward_claimed,
                    reward_claimed_at=user_achievement.reward_claimed_at
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo logro {achievement_id} del usuario {user_id}: {e}")
            return None
    
    async def create_user_achievement(self, user_achievement: UserAchievement) -> UserAchievement:
        """Crea un nuevo registro de logro para usuario."""
        try:
            from infrastructure.persistence.supabase.models import UserAchievementModel
            
            db_user_achievement = UserAchievementModel(
                user_id=user_achievement.user_id,
                achievement_id=user_achievement.achievement_id,
                current_value=user_achievement.current_value,
                is_completed=user_achievement.is_completed,
                completed_at=user_achievement.completed_at,
                reward_claimed=user_achievement.reward_claimed,
                reward_claimed_at=user_achievement.reward_claimed_at
            )
            
            self.db_session.add(db_user_achievement)
            await self.db_session.commit()
            await self.db_session.refresh(db_user_achievement)
            
            return user_achievement
            
        except Exception as e:
            logger.error(f"Error creando logro para usuario {user_achievement.user_id}: {e}")
            await self.db_session.rollback()
            raise
    
    async def update_user_achievement(self, user_achievement: UserAchievement) -> UserAchievement:
        """Actualiza el progreso de un logro de usuario."""
        try:
            from infrastructure.persistence.supabase.models import UserAchievementModel
            
            query = update(UserAchievementModel).where(
                and_(UserAchievementModel.user_id == user_achievement.user_id, 
                     UserAchievementModel.achievement_id == user_achievement.achievement_id)
            ).values(
                current_value=user_achievement.current_value,
                is_completed=user_achievement.is_completed,
                completed_at=user_achievement.completed_at,
                reward_claimed=user_achievement.reward_claimed,
                reward_claimed_at=user_achievement.reward_claimed_at,
                updated_at=func.now()
            )
            
            await self.db_session.execute(query)
            await self.db_session.commit()
            
            return user_achievement
            
        except Exception as e:
            logger.error(f"Error actualizando logro para usuario {user_achievement.user_id}: {e}")
            await self.db_session.rollback()
            raise
    
    async def get_completed_achievements(self, user_id: int) -> List[UserAchievement]:
        """Obtiene logros completados por un usuario."""
        try:
            from infrastructure.persistence.supabase.models import UserAchievementModel
            
            query = select(UserAchievementModel).where(
                and_(UserAchievementModel.user_id == user_id, UserAchievementModel.is_completed == True)
            )
            result = await self.db_session.execute(query)
            user_achievements = result.scalars().all()
            
            return [
                UserAchievement(
                    user_id=ua.user_id,
                    achievement_id=ua.achievement_id,
                    current_value=ua.current_value,
                    is_completed=ua.is_completed,
                    completed_at=ua.completed_at,
                    reward_claimed=ua.reward_claimed,
                    reward_claimed_at=ua.reward_claimed_at
                )
                for ua in user_achievements
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo logros completados del usuario {user_id}: {e}")
            return []
    
    async def get_pending_rewards(self, user_id: int) -> List[UserAchievement]:
        """Obtiene logros completados con recompensas no reclamadas."""
        try:
            from infrastructure.persistence.supabase.models import UserAchievementModel
            
            query = select(UserAchievementModel).where(
                and_(UserAchievementModel.user_id == user_id, 
                     UserAchievementModel.is_completed == True,
                     UserAchievementModel.reward_claimed == False)
            )
            result = await self.db_session.execute(query)
            user_achievements = result.scalars().all()
            
            return [
                UserAchievement(
                    user_id=ua.user_id,
                    achievement_id=ua.achievement_id,
                    current_value=ua.current_value,
                    is_completed=ua.is_completed,
                    completed_at=ua.completed_at,
                    reward_claimed=ua.reward_claimed,
                    reward_claimed_at=ua.reward_claimed_at
                )
                for ua in user_achievements
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo recompensas pendientes del usuario {user_id}: {e}")
            return []


class UserStatsRepository(IUserStatsRepository):
    """Implementación del repositorio de estadísticas de usuarios."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_user_stats(self, user_id: int) -> Optional[UserStats]:
        """Obtiene las estadísticas de un usuario."""
        try:
            from infrastructure.persistence.supabase.models import UserStatsModel
            
            query = select(UserStatsModel).where(UserStatsModel.user_id == user_id)
            result = await self.db_session.execute(query)
            user_stats = result.scalar_one_or_none()
            
            if user_stats:
                return UserStats(
                    user_id=user_stats.user_id,
                    total_data_consumed_gb=user_stats.total_data_consumed_gb,
                    days_active=user_stats.days_active,
                    total_referrals=user_stats.total_referrals,
                    total_stars_deposited=user_stats.total_stars_deposited,
                    total_keys_created=user_stats.total_keys_created,
                    total_games_won=user_stats.total_games_won,
                    vip_months_purchased=user_stats.vip_months_purchased,
                    last_active_date=user_stats.last_active_date,
                    created_at=user_stats.created_at
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del usuario {user_id}: {e}")
            return None
    
    async def create_user_stats(self, user_stats: UserStats) -> UserStats:
        """Crea estadísticas iniciales para un usuario."""
        try:
            from infrastructure.persistence.supabase.models import UserStatsModel
            
            db_user_stats = UserStatsModel(
                user_id=user_stats.user_id,
                total_data_consumed_gb=user_stats.total_data_consumed_gb,
                days_active=user_stats.days_active,
                total_referrals=user_stats.total_referrals,
                total_stars_deposited=user_stats.total_stars_deposited,
                total_keys_created=user_stats.total_keys_created,
                total_games_won=user_stats.total_games_won,
                vip_months_purchased=user_stats.vip_months_purchased,
                last_active_date=user_stats.last_active_date,
                created_at=user_stats.created_at
            )
            
            self.db_session.add(db_user_stats)
            await self.db_session.commit()
            await self.db_session.refresh(db_user_stats)
            
            return user_stats
            
        except Exception as e:
            logger.error(f"Error creando estadísticas para usuario {user_stats.user_id}: {e}")
            await self.db_session.rollback()
            raise
    
    async def update_user_stats(self, user_stats: UserStats) -> UserStats:
        """Actualiza las estadísticas de un usuario."""
        try:
            from infrastructure.persistence.supabase.models import UserStatsModel
            
            query = update(UserStatsModel).where(UserStatsModel.user_id == user_stats.user_id).values(
                total_data_consumed_gb=user_stats.total_data_consumed_gb,
                days_active=user_stats.days_active,
                total_referrals=user_stats.total_referrals,
                total_stars_deposited=user_stats.total_stars_deposited,
                total_keys_created=user_stats.total_keys_created,
                total_games_won=user_stats.total_games_won,
                vip_months_purchased=user_stats.vip_months_purchased,
                last_active_date=user_stats.last_active_date,
                updated_at=func.now()
            )
            
            await self.db_session.execute(query)
            await self.db_session.commit()
            
            return user_stats
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas para usuario {user_stats.user_id}: {e}")
            await self.db_session.rollback()
            raise
    
    async def get_leaderboard_by_type(self, achievement_type: AchievementType, limit: int = 10) -> List[Dict]:
        """Obtiene ranking de usuarios por tipo de logro."""
        try:
            from infrastructure.persistence.supabase.models import UserStatsModel
            
            # Mapear tipos de logro a campos de estadísticas
            field_mapping = {
                AchievementType.DATA_CONSUMED: UserStatsModel.total_data_consumed_gb,
                AchievementType.DAYS_ACTIVE: UserStatsModel.days_active,
                AchievementType.REFERRALS_COUNT: UserStatsModel.total_referrals,
                AchievementType.STARS_DEPOSITED: UserStatsModel.total_stars_deposited,
                AchievementType.KEYS_CREATED: UserStatsModel.total_keys_created,
                AchievementType.GAMES_WON: UserStatsModel.total_games_won,
                AchievementType.VIP_MONTHS: UserStatsModel.vip_months_purchased
            }
            
            if achievement_type not in field_mapping:
                return []
            
            field = field_mapping[achievement_type]
            
            query = select(
                UserStatsModel.user_id,
                field.label('value')
            ).order_by(field.desc()).limit(limit)
            
            result = await self.db_session.execute(query)
            leaderboard = result.all()
            
            return [
                {
                    'user_id': row.user_id,
                    'value': float(row.value) if achievement_type == AchievementType.DATA_CONSUMED else int(row.value),
                    'rank': index + 1
                }
                for index, row in enumerate(leaderboard)
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo leaderboard para tipo {achievement_type}: {e}")
            return []
    
    async def get_top_users_by_achievements(self, limit: int = 10) -> List[Dict]:
        """Obtiene usuarios con más logros completados."""
        try:
            from infrastructure.persistence.supabase.models import UserAchievementModel
            
            query = select(
                UserAchievementModel.user_id,
                func.count(UserAchievementModel.achievement_id).label('completed_count')
            ).where(
                UserAchievementModel.is_completed == True
            ).group_by(UserAchievementModel.user_id).order_by(
                func.count(UserAchievementModel.achievement_id).desc()
            ).limit(limit)
            
            result = await self.db_session.execute(query)
            top_users = result.all()
            
            return [
                {
                    'user_id': row.user_id,
                    'completed_count': int(row.completed_count),
                    'rank': index + 1
                }
                for index, row in enumerate(top_users)
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo top usuarios por logros: {e}")
            return []
