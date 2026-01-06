"""
Servicio de tareas para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

from typing import List, Optional, Dict
from datetime import datetime
import uuid
from utils.logger import logger

from domain.entities.task import Task, UserTask
from infrastructure.persistence.supabase.task_repository import TaskRepository
from application.services.payment_service import PaymentService


class TaskService:
    """Servicio para gestionar tareas y recompensas."""
    
    def __init__(self, task_repo: TaskRepository, payment_service: PaymentService):
        self.task_repo = task_repo
        self.payment_service = payment_service
    
    async def create_task(
        self,
        title: str,
        description: str,
        reward_stars: int,
        created_by: int,
        guide_text: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> Task:
        """Crea una nueva tarea."""
        task = Task(
            id=uuid.uuid4(),
            title=title,
            description=description,
            reward_stars=reward_stars,
            guide_text=guide_text,
            created_by=created_by,
            expires_at=expires_at
        )
        
        return await self.task_repo.create_task(task)
    
    async def get_active_tasks(self) -> List[Task]:
        """Obtiene todas las tareas activas disponibles."""
        return await self.task_repo.get_active_tasks()
    
    async def get_all_tasks(self) -> List[Task]:
        """Obtiene todas las tareas (para administradores)."""
        return await self.task_repo.get_all_tasks()
    
    async def get_task_by_id(self, task_id: uuid.UUID) -> Optional[Task]:
        """Obtiene una tarea por su ID."""
        return await self.task_repo.get_task_by_id(task_id)
    
    async def update_task(self, task: Task) -> Task:
        """Actualiza una tarea existente."""
        return await self.task_repo.update_task(task)
    
    async def delete_task(self, task_id: uuid.UUID) -> bool:
        """Elimina una tarea (soft delete)."""
        return await self.task_repo.delete_task(task_id)
    
    async def get_user_tasks_summary(self, user_id: int) -> Dict:
        """Obtiene un resumen de las tareas del usuario."""
        active_tasks = await self.task_repo.get_active_tasks()
        user_tasks = await self.task_repo.get_user_tasks(user_id)
        
        # Crear un diccionario de tareas del usuario por task_id
        user_tasks_dict = {ut.task_id: ut for ut in user_tasks}
        
        # Categorizar tareas
        available_tasks = []
        completed_tasks = []
        in_progress_tasks = []
        
        for task in active_tasks:
            user_task = user_tasks_dict.get(task.id)
            
            if user_task is None:
                # Tarea disponible pero no iniciada
                available_tasks.append({
                    "task": task,
                    "user_task": None,
                    "status": "available"
                })
            elif user_task.is_completed:
                # Tarea completada
                completed_tasks.append({
                    "task": task,
                    "user_task": user_task,
                    "status": "completed"
                })
            else:
                # Tarea en progreso
                in_progress_tasks.append({
                    "task": task,
                    "user_task": user_task,
                    "status": "in_progress"
                })
        
        return {
            "available": available_tasks,
            "completed": completed_tasks,
            "in_progress": in_progress_tasks,
            "total_available": len(available_tasks),
            "total_completed": len(completed_tasks),
            "total_in_progress": len(in_progress_tasks)
        }
    
    async def start_task(self, user_id: int, task_id: uuid.UUID) -> UserTask:
        """Inicia una tarea para un usuario."""
        task = await self.task_repo.get_task_by_id(task_id)
        
        if task is None:
            raise ValueError("Tarea no encontrada")
        
        if not task.is_available():
            raise ValueError("La tarea no está disponible")
        
        # Verificar si ya existe
        existing = await self.task_repo.get_user_task(user_id, task_id)
        
        if existing:
            return existing
        
        # Crear nuevo registro
        user_task = UserTask(
            user_id=user_id,
            task_id=task_id
        )
        
        return await self.task_repo.create_or_update_user_task(user_task)
    
    async def complete_task(self, user_id: int, task_id: uuid.UUID) -> UserTask:
        """Marca una tarea como completada."""
        user_task = await self.task_repo.get_user_task(user_id, task_id)
        
        # Si no existe, crear el registro
        if user_task is None:
            user_task = UserTask(
                user_id=user_id,
                task_id=task_id
            )
        
        if user_task.is_completed:
            raise ValueError("La tarea ya está completada")
        
        task = await self.task_repo.get_task_by_id(task_id)
        
        if task is None:
            raise ValueError("Tarea no encontrada")
        
        if not task.is_available():
            raise ValueError("La tarea no está disponible")
        
        # Marcar como completada
        user_task.is_completed = True
        user_task.completed_at = datetime.now()
        
        return await self.task_repo.create_or_update_user_task(user_task)
    
    async def claim_reward(self, user_id: int, task_id: uuid.UUID) -> bool:
        """Reclama la recompensa de una tarea completada."""
        user_task = await self.task_repo.get_user_task(user_id, task_id)
        
        if user_task is None:
            raise ValueError("Tarea no encontrada")
        
        if not user_task.is_completed:
            raise ValueError("La tarea no está completada")
        
        if user_task.reward_claimed:
            raise ValueError("La recompensa ya fue reclamada")
        
        task = await self.task_repo.get_task_by_id(task_id)
        
        if task is None:
            raise ValueError("Tarea no encontrada")
        
        # Acreditar estrellas al usuario
        success = await self.payment_service.update_balance(
            telegram_id=user_id,
            amount=task.reward_stars,
            transaction_type="task_reward",
            description=f"Recompensa por completar tarea: {task.title}",
            reference_id=str(task_id)
        )
        
        if not success:
            raise ValueError("Error al acreditar la recompensa")
        
        # Marcar recompensa como reclamada
        user_task.claim_reward()
        await self.task_repo.create_or_update_user_task(user_task)
        
        logger.info(f"✅ Usuario {user_id} reclamó {task.reward_stars} estrellas por la tarea {task_id}")
        return True
    
    async def get_user_completed_tasks(self, user_id: int) -> List[UserTask]:
        """Obtiene todas las tareas completadas por un usuario."""
        return await self.task_repo.get_completed_user_tasks(user_id)

