"""
Repositorios de logros y estadísticas con SQLAlchemy Async.

Author: uSipipo Team
Version: 2.0.0
"""

from typing import List, Optional, Dict
from datetime import datetime

from sqlalchemy import select, update, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from utils.logger import logger

from domain.entities.achievement import Achievement, UserAchievement, UserStats, AchievementType
from domain.interfaces.iachievement_repository import IAchievementRepository, IUserStatsRepository
from .models import AchievementModel, UserAchievementModel, UserStatsModel
from .base_repository import BaseSupabaseRepository

class AchievementRepository(BaseSupabaseRepository, IAchievementRepository):
    """Implementación del repositorio de logros con SQLAlchemy Async."""
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            session: Sesión async de SQLAlchemy.
        """
        super().__init__(session)
    
    def _model_to_entity(self, model: AchievementModel) -> Achievement:
        """Convierte un modelo SQLAlchemy a entidad de dominio."""
        return Achievement(
            id=model.id,
            name=model.name,
            description=model.description,
            type=AchievementType(model.type) if model.type else AchievementType.GENERAL,
            tier=model.tier,
            requirement_value=model.requirement_value,
            reward_stars=model.reward_stars,
            icon=model.icon,
            is_active=model.is_active
        )
    
    async def get_all_achievements(self, current_user_id: int) -> List[Achievement]:
        """Obtiene todos los logros activos."""
        await self._set_current_user(current_user_id)
        try:
            query = select(AchievementModel).where(AchievementModel.is_active == True)
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

        except Exception as e:
            logger.error(f"❌ Error obteniendo todos los logros: {e}")
            return []

    async def get_achievement_by_id(self, achievement_id: str, current_user_id: int) -> Optional[Achievement]:
        """Obtiene un logro por su ID."""
        await self._set_current_user(current_user_id)
        try:
            query = select(AchievementModel).where(
                and_(
                    AchievementModel.id == achievement_id,
                    AchievementModel.is_active == True
                )
            )
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._model_to_entity(model)

        except Exception as e:
            logger.error(f"❌ Error obteniendo logro {achievement_id}: {e}")
            return None

    async def get_achievements_by_type(self, achievement_type: AchievementType, current_user_id: int) -> List[Achievement]:
        """Obtiene logros por tipo."""
        await self._set_current_user(current_user_id)
        try:
            query = select(AchievementModel).where(
                and_(
                    AchievementModel.type == achievement_type.value,
                    AchievementModel.is_active == True
                )
            )
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

        except Exception as e:
            logger.error(f"❌ Error obteniendo logros por tipo {achievement_type}: {e}")
            return []

    async def get_user_achievements(self, user_id: int, current_user_id: int) -> List[UserAchievement]:
        """Obtiene todos los logros de un usuario."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserAchievementModel).where(UserAchievementModel.user_id == user_id)
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [
                UserAchievement(
                    user_id=m.user_id,
                    achievement_id=m.achievement_id,
                    current_value=m.current_value or 0,
                    is_completed=m.is_completed or False,
                    completed_at=m.completed_at,
                    reward_claimed=m.reward_claimed or False,
                    reward_claimed_at=m.reward_claimed_at
                )
                for m in models
            ]

        except Exception as e:
            logger.error(f"❌ Error obteniendo logros del usuario {user_id}: {e}")
            return []

    async def get_user_achievement(self, user_id: int, achievement_id: str, current_user_id: int) -> Optional[UserAchievement]:
        """Obtiene un logro específico de un usuario."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserAchievementModel).where(
                and_(
                    UserAchievementModel.user_id == user_id,
                    UserAchievementModel.achievement_id == achievement_id
                )
            )
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return UserAchievement(
                user_id=model.user_id,
                achievement_id=model.achievement_id,
                current_value=model.current_value or 0,
                is_completed=model.is_completed or False,
                completed_at=model.completed_at,
                reward_claimed=model.reward_claimed or False,
                reward_claimed_at=model.reward_claimed_at
            )

        except Exception as e:
            logger.error(f"❌ Error obteniendo logro {achievement_id} del usuario {user_id}: {e}")
            return None

    async def create_user_achievement(self, user_achievement: UserAchievement, current_user_id: int) -> UserAchievement:
        """Crea un nuevo registro de logro para usuario."""
        await self._set_current_user(current_user_id)
        try:
            model = UserAchievementModel(
                user_id=user_achievement.user_id,
                achievement_id=user_achievement.achievement_id,
                current_value=user_achievement.current_value or 0,
                is_completed=user_achievement.is_completed or False,
                completed_at=user_achievement.completed_at,
                reward_claimed=user_achievement.reward_claimed or False,
                reward_claimed_at=user_achievement.reward_claimed_at
            )

            self.session.add(model)
            await self.session.commit()

            logger.debug(f"💾 Logro creado para usuario {user_achievement.user_id}: {user_achievement.achievement_id}")
            return user_achievement

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error creando logro para usuario {user_achievement.user_id}: {e}")
            raise

    async def update_user_achievement(self, user_achievement: UserAchievement, current_user_id: int) -> UserAchievement:
        """Actualiza el progreso de un logro de usuario."""
        await self._set_current_user(current_user_id)
        try:
            query = (
                update(UserAchievementModel)
                .where(
                    and_(
                        UserAchievementModel.user_id == user_achievement.user_id,
                        UserAchievementModel.achievement_id == user_achievement.achievement_id
                    )
                )
                .values(
                    current_value=user_achievement.current_value or 0,
                    is_completed=user_achievement.is_completed or False,
                    completed_at=user_achievement.completed_at,
                    reward_claimed=user_achievement.reward_claimed or False,
                    reward_claimed_at=user_achievement.reward_claimed_at,
                    updated_at=func.now()
                )
            )

            await self.session.execute(query)
            await self.session.commit()

            logger.debug(f"✏️ Logro actualizado para usuario {user_achievement.user_id}: {user_achievement.achievement_id}")
            return user_achievement

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error actualizando logro para usuario {user_achievement.user_id}: {e}")
            raise

    async def get_completed_achievements(self, user_id: int, current_user_id: int) -> List[UserAchievement]:
        """Obtiene logros completados por un usuario."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserAchievementModel).where(
                and_(
                    UserAchievementModel.user_id == user_id,
                    UserAchievementModel.is_completed == True
                )
            )
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [
                UserAchievement(
                    user_id=m.user_id,
                    achievement_id=m.achievement_id,
                    current_value=m.current_value or 0,
                    is_completed=m.is_completed or False,
                    completed_at=m.completed_at,
                    reward_claimed=m.reward_claimed or False,
                    reward_claimed_at=m.reward_claimed_at
                )
                for m in models
            ]

        except Exception as e:
            logger.error(f"❌ Error obteniendo logros completados del usuario {user_id}: {e}")
            return []

    async def get_pending_rewards(self, user_id: int, current_user_id: int) -> List[UserAchievement]:
        """Obtiene logros completados con recompensas no reclamadas."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserAchievementModel).where(
                and_(
                    UserAchievementModel.user_id == user_id,
                    UserAchievementModel.is_completed == True,
                    UserAchievementModel.reward_claimed == False
                )
            )
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [
                UserAchievement(
                    user_id=m.user_id,
                    achievement_id=m.achievement_id,
                    current_value=m.current_value or 0,
                    is_completed=m.is_completed or False,
                    completed_at=m.completed_at,
                    reward_claimed=m.reward_claimed or False,
                    reward_claimed_at=m.reward_claimed_at
                )
                for m in models
            ]

        except Exception as e:
            logger.error(f"❌ Error obteniendo recompensas pendientes del usuario {user_id}: {e}")
            return []


class UserStatsRepository(IUserStatsRepository):
    """Implementación del repositorio de estadísticas de usuarios con SQLAlchemy Async."""
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            session: Sesión async de SQLAlchemy.
        """
        super().__init__(session)
    
    def _model_to_entity(self, model: UserStatsModel) -> UserStats:
        """Convierte un modelo SQLAlchemy a entidad de dominio."""
        return UserStats(
            user_id=model.user_id,
            total_data_consumed_gb=model.total_data_consumed_gb or 0.0,
            days_active=model.days_active or 0,
            total_referrals=model.total_referrals or 0,
            total_stars_deposited=model.total_stars_deposited or 0,
            total_keys_created=model.total_keys_created or 0,
            total_games_won=model.total_games_won or 0,
            vip_months_purchased=model.vip_months_purchased or 0,
            last_active_date=model.last_active_date,
            created_at=model.created_at
        )
    
    async def get_user_stats(self, user_id: int, current_user_id: int) -> Optional[UserStats]:
        """Obtiene las estadísticas de un usuario."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserStatsModel).where(UserStatsModel.user_id == user_id)
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._model_to_entity(model)

        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas del usuario {user_id}: {e}")
            return None

    async def create_user_stats(self, user_stats: UserStats, current_user_id: int) -> UserStats:
        """Crea estadísticas iniciales para un usuario."""
        await self._set_current_user(current_user_id)
        try:
            logger.debug(f"🔍 Attempting to create user_stats for user_id {user_stats.user_id}")

            # Use INSERT ... ON CONFLICT DO NOTHING to prevent duplicate key violations
            insert_stmt = insert(UserStatsModel).values(
                user_id=user_stats.user_id,
                total_data_consumed_gb=user_stats.total_data_consumed_gb or 0.0,
                days_active=user_stats.days_active or 0,
                total_referrals=user_stats.total_referrals or 0,
                total_stars_deposited=user_stats.total_stars_deposited or 0,
                total_keys_created=user_stats.total_keys_created or 0,
                total_games_won=user_stats.total_games_won or 0,
                vip_months_purchased=user_stats.vip_months_purchased or 0,
                last_active_date=user_stats.last_active_date,
                created_at=user_stats.created_at or datetime.now()
            ).on_conflict_do_nothing(index_elements=['user_id'])

            await self.session.execute(insert_stmt)
            await self.session.commit()

            logger.debug(f"💾 Estadísticas creadas o ya existen para usuario {user_stats.user_id}")
            return user_stats

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error creando estadísticas para usuario {user_stats.user_id}: {e}")
            raise

    async def update_user_stats(self, user_stats: UserStats, current_user_id: int) -> UserStats:
        """Actualiza las estadísticas de un usuario."""
        await self._set_current_user(current_user_id)
        try:
            query = (
                update(UserStatsModel)
                .where(UserStatsModel.user_id == user_stats.user_id)
                .values(
                    total_data_consumed_gb=user_stats.total_data_consumed_gb or 0.0,
                    days_active=user_stats.days_active or 0,
                    total_referrals=user_stats.total_referrals or 0,
                    total_stars_deposited=user_stats.total_stars_deposited or 0,
                    total_keys_created=user_stats.total_keys_created or 0,
                    total_games_won=user_stats.total_games_won or 0,
                    vip_months_purchased=user_stats.vip_months_purchased or 0,
                    last_active_date=user_stats.last_active_date,
                    updated_at=func.now()
                )
            )

            await self.session.execute(query)
            await self.session.commit()

            logger.debug(f"✏️ Estadísticas actualizadas para usuario {user_stats.user_id}")
            return user_stats

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error actualizando estadísticas para usuario {user_stats.user_id}: {e}")
            raise

    async def get_leaderboard_by_type(self, achievement_type: AchievementType, limit: int = 10, current_user_id: int = None) -> List[Dict]:
        """Obtiene ranking de usuarios por tipo de logro."""
        if current_user_id:
            await self._set_current_user(current_user_id)
        try:
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
                logger.warning(f"⚠️ Tipo de logro no mapeado: {achievement_type}")
                return []

            field = field_mapping[achievement_type]

            query = (
                select(
                    UserStatsModel.user_id,
                    field.label('value')
                )
                .order_by(field.desc())
                .limit(limit)
            )

            result = await self.session.execute(query)
            rows = result.all()

            return [
                {
                    'user_id': row.user_id,
                    'value': float(row.value) if achievement_type == AchievementType.DATA_CONSUMED else int(row.value),
                    'rank': index + 1
                }
                for index, row in enumerate(rows)
            ]

        except Exception as e:
            logger.error(f"❌ Error obteniendo leaderboard para tipo {achievement_type}: {e}")
            return []

    async def get_top_users_by_achievements(self, limit: int = 10, current_user_id: int = None) -> List[Dict]:
        """Obtiene usuarios con más logros completados."""
        if current_user_id:
            await self._set_current_user(current_user_id)
        try:
            query = (
                select(
                    UserAchievementModel.user_id,
                    func.count(UserAchievementModel.achievement_id).label('completed_count')
                )
                .where(UserAchievementModel.is_completed == True)
                .group_by(UserAchievementModel.user_id)
                .order_by(func.count(UserAchievementModel.achievement_id).desc())
                .limit(limit)
            )

            result = await self.session.execute(query)
            rows = result.all()

            return [
                {
                    'user_id': row.user_id,
                    'completed_count': int(row.completed_count),
                    'rank': index + 1
                }
                for index, row in enumerate(rows)
            ]

        except Exception as e:
            logger.error(f"❌ Error obteniendo top usuarios por logros: {e}")
            return []
