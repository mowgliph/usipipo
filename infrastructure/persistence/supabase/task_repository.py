"""
Repositorio de tareas con SQLAlchemy Async.

Author: uSipipo Team
Version: 1.0.0
"""

from typing import Optional, List
import uuid

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger

from domain.entities.task import Task, UserTask
from .models import TaskModel, UserTaskModel
from .base_repository import BaseSupabaseRepository


class TaskRepository(BaseSupabaseRepository):
    """Implementación del repositorio de tareas con SQLAlchemy Async."""
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            session: Sesión async de SQLAlchemy.
        """
        super().__init__(session)
    
    def _model_to_entity(self, model: TaskModel) -> Task:
        """Convierte un modelo SQLAlchemy a entidad de dominio."""
        return Task(
            id=model.id,
            title=model.title,
            description=model.description,
            reward_stars=model.reward_stars,
            guide_text=model.guide_text,
            is_active=model.is_active,
            created_by=model.created_by,
            created_at=model.created_at,
            expires_at=model.expires_at
        )
    
    def _entity_to_model(self, entity: Task) -> TaskModel:
        """Convierte una entidad de dominio a modelo SQLAlchemy."""
        return TaskModel(
            id=entity.id if entity.id else uuid.uuid4(),
            title=entity.title,
            description=entity.description,
            reward_stars=entity.reward_stars,
            guide_text=entity.guide_text,
            is_active=entity.is_active,
            created_by=entity.created_by,
            created_at=entity.created_at,
            expires_at=entity.expires_at
        )
    
    def _user_task_model_to_entity(self, model: UserTaskModel) -> UserTask:
        """Convierte un modelo UserTaskModel a entidad de dominio."""
        return UserTask(
            user_id=model.user_id,
            task_id=model.task_id,
            is_completed=model.is_completed,
            completed_at=model.completed_at,
            reward_claimed=model.reward_claimed,
            reward_claimed_at=model.reward_claimed_at,
            created_at=model.created_at
        )
    
    def _user_task_entity_to_model(self, entity: UserTask) -> UserTaskModel:
        """Convierte una entidad UserTask a modelo SQLAlchemy."""
        return UserTaskModel(
            user_id=entity.user_id,
            task_id=entity.task_id,
            is_completed=entity.is_completed,
            completed_at=entity.completed_at,
            reward_claimed=entity.reward_claimed,
            reward_claimed_at=entity.reward_claimed_at,
            created_at=entity.created_at
        )
    
    async def create_task(self, task: Task, current_user_id: int) -> Task:
        """Crea una nueva tarea."""
        await self._set_current_user(current_user_id)
        try:
            if not task.id:
                task.id = uuid.uuid4()

            model = self._entity_to_model(task)
            self.session.add(model)
            await self.session.commit()

            logger.debug(f"💾 Tarea {task.id} creada correctamente.")
            return task

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al crear tarea: {e}")
            raise

    async def get_task_by_id(self, task_id: uuid.UUID, current_user_id: int) -> Optional[Task]:
        """Obtiene una tarea por su ID."""
        await self._set_current_user(current_user_id)
        try:
            model = await self.session.get(TaskModel, task_id)

            if model is None:
                return None

            return self._model_to_entity(model)

        except Exception as e:
            logger.error(f"❌ Error al obtener tarea {task_id}: {e}")
            return None

    async def get_active_tasks(self, current_user_id: int) -> List[Task]:
        """Obtiene todas las tareas activas."""
        await self._set_current_user(current_user_id)
        try:
            query = select(TaskModel).where(TaskModel.is_active == True)
            result = await self.session.execute(query)
            models = result.scalars().all()

            tasks = [self._model_to_entity(m) for m in models]
            # Filtrar tareas expiradas
            return [t for t in tasks if not t.is_expired()]

        except Exception as e:
            logger.error(f"❌ Error al obtener tareas activas: {e}")
            return []

    async def get_all_tasks(self, current_user_id: int) -> List[Task]:
        """Obtiene todas las tareas (incluyendo inactivas)."""
        await self._set_current_user(current_user_id)
        try:
            query = select(TaskModel).order_by(TaskModel.created_at.desc())
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

        except Exception as e:
            logger.error(f"❌ Error al obtener todas las tareas: {e}")
            return []

    async def update_task(self, task: Task, current_user_id: int) -> Task:
        """Actualiza una tarea existente."""
        await self._set_current_user(current_user_id)
        try:
            model = await self.session.get(TaskModel, task.id)

            if model is None:
                raise ValueError(f"Tarea {task.id} no encontrada")

            model.title = task.title
            model.description = task.description
            model.reward_stars = task.reward_stars
            model.guide_text = task.guide_text
            model.is_active = task.is_active
            model.expires_at = task.expires_at

            await self.session.commit()
            logger.debug(f"💾 Tarea {task.id} actualizada correctamente.")
            return task

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al actualizar tarea: {e}")
            raise

    async def delete_task(self, task_id: uuid.UUID, current_user_id: int) -> bool:
        """Elimina una tarea (soft delete marcándola como inactiva)."""
        await self._set_current_user(current_user_id)
        try:
            model = await self.session.get(TaskModel, task_id)

            if model is None:
                return False

            model.is_active = False
            await self.session.commit()

            logger.debug(f"✅ Tarea {task_id} desactivada.")
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al eliminar tarea {task_id}: {e}")
            return False

    async def get_user_task(self, user_id: int, task_id: uuid.UUID, current_user_id: int) -> Optional[UserTask]:
        """Obtiene el progreso de un usuario en una tarea específica."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserTaskModel).where(
                and_(
                    UserTaskModel.user_id == user_id,
                    UserTaskModel.task_id == task_id
                )
            )
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._user_task_model_to_entity(model)

        except Exception as e:
            logger.error(f"❌ Error al obtener tarea de usuario: {e}")
            return None

    async def get_user_tasks(self, user_id: int, current_user_id: int) -> List[UserTask]:
        """Obtiene todas las tareas de un usuario."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserTaskModel).where(UserTaskModel.user_id == user_id)
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [self._user_task_model_to_entity(m) for m in models]

        except Exception as e:
            logger.error(f"❌ Error al obtener tareas del usuario {user_id}: {e}")
            return []

    async def create_or_update_user_task(self, user_task: UserTask, current_user_id: int) -> UserTask:
        """Crea o actualiza el progreso de un usuario en una tarea."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserTaskModel).where(
                and_(
                    UserTaskModel.user_id == user_task.user_id,
                    UserTaskModel.task_id == user_task.task_id
                )
            )
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()

            if model is None:
                # Crear nuevo
                model = self._user_task_entity_to_model(user_task)
                self.session.add(model)
            else:
                # Actualizar existente
                model.is_completed = user_task.is_completed
                model.completed_at = user_task.completed_at
                model.reward_claimed = user_task.reward_claimed
                model.reward_claimed_at = user_task.reward_claimed_at

            await self.session.commit()
            logger.debug(f"💾 Progreso de tarea guardado para usuario {user_task.user_id}.")
            return user_task

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al guardar progreso de tarea: {e}")
            raise

    async def get_completed_user_tasks(self, user_id: int, current_user_id: int) -> List[UserTask]:
        """Obtiene todas las tareas completadas por un usuario."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserTaskModel).where(
                and_(
                    UserTaskModel.user_id == user_id,
                    UserTaskModel.is_completed == True
                )
            )
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [self._user_task_model_to_entity(m) for m in models]

        except Exception as e:
            logger.error(f"❌ Error al obtener tareas completadas: {e}")
            return []

