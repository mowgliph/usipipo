# services/audit.py

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database import models
from database.db import async_session
from database.crud import logs as crud_logs
import logging
import traceback

logger = logging.getLogger("usipipo.audit")

class AuditService:
    """Servicio para operaciones de auditoría y logs."""
    
    @classmethod
    async def get_db_session(cls) -> AsyncSession:
        """Obtiene una sesión asíncrona de la base de datos."""
        return async_session()

    @classmethod
    async def log_action(
        cls,
        user_id: Optional[int],
        action: str,
        details: Optional[str] = None,
        session: Optional[AsyncSession] = None,
        **extra_data: Any
    ) -> Dict[str, Any]:
        """
        Registra una acción en el log de auditoría.
        
        Args:
            user_id: ID del usuario que realiza la acción (opcional)
            action: Identificador de la acción (ej: 'user_login', 'vpn_created')
            details: Detalles adicionales de la acción
            session: Sesión de base de datos asíncrona existente (opcional)
            **extra_data: Datos adicionales a incluir en el log
            
        Returns:
            Dict con el resultado de la operación
        """
        should_commit = False
        if session is None:
            session = await cls.get_db_session()
            should_commit = True
            
        try:
            log = await crud_logs.create_audit_log(
                session=session,
                user_id=user_id,
                action=action,
                details=details,
                **extra_data
            )
            
            if should_commit:
                await session.commit()
                await session.refresh(log)
                
            return {
                "ok": True,
                "data": log,
                "message": "Acción registrada correctamente"
            }
            
        except Exception as e:
            logger.error(f"Error en log_action: {str(e)}")
            logger.error(traceback.format_exc())
            if should_commit:
                await session.rollback()
            return {
                "ok": False,
                "data": None,
                "message": "Error al registrar la acción",
                "error": "log_action_failed"
            }
        finally:
            if should_commit and session:
                await session.close()

    @classmethod
    async def get_logs(
        cls,
        limit: int = 20,
        offset: int = 0,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Obtiene registros de auditoría con paginación.
        
        Args:
            limit: Número máximo de registros a devolver
            offset: Desplazamiento para paginación
            user_id: Filtrar por ID de usuario (opcional)
            action: Filtrar por acción (opcional)
            session: Sesión de base de datos asíncrona existente (opcional)
            
        Returns:
            Dict con el resultado de la operación
        """
        should_close = False
        if session is None:
            session = await cls.get_db_session()
            should_close = True
            
        try:
            # Obtener registros
            logs = await crud_logs.get_audit_logs(
                session=session,
                user_id=user_id,
                action=action,
                limit=limit,
                offset=offset
            )
            
            # Obtener conteo total
            total = await crud_logs.count_audit_logs(
                session=session,
                user_id=user_id,
                action=action
            )
            
            return {
                "ok": True,
                "data": {
                    "items": logs,
                    "total": total,
                    "limit": limit,
                    "offset": offset
                },
                "message": f"Se encontraron {len(logs)} de {total} registros"
            }
            
        except Exception as e:
            logger.error(f"Error en get_logs: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "ok": False,
                "data": None,
                "message": "Error al obtener los registros",
                "error": "get_logs_failed"
            }
        finally:
            if should_close and session:
                await session.close()

    @classmethod
    async def clean_old_logs(
        cls,
        days_old: int = 30,
        user_id: Optional[int] = None,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Elimina registros de auditoría más antiguos que el número de días especificado.
        
        Args:
            days_old: Número de días de antigüedad mínima para eliminar
            user_id: Si se especifica, solo elimina registros de este usuario
            session: Sesión de base de datos asíncrona existente (opcional)
            
        Returns:
            Dict con el resultado de la operación
        """
        should_commit = False
        if session is None:
            session = await cls.get_db_session()
            should_commit = True
            
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            deleted_count = await crud_logs.delete_old_logs(
                session=session,
                cutoff=cutoff_date,
                user_id=user_id
            )
            
            if should_commit:
                await session.commit()
                
            return {
                "ok": True,
                "data": {"deleted_count": deleted_count},
                "message": f"Se eliminaron {deleted_count} registros antiguos"
            }
            
        except Exception as e:
            logger.error(f"Error en clean_old_logs: {str(e)}")
            logger.error(traceback.format_exc())
            if should_commit:
                await session.rollback()
            return {
                "ok": False,
                "data": None,
                "message": "Error al limpiar registros antiguos",
                "error": "clean_logs_failed"
            }
        finally:
            if should_close and session:
                await session.close()

    @staticmethod
    def format_logs(logs_list: List[models.AuditLog]) -> str:
        """
        Formatea una lista de logs para su visualización.
        
        Args:
            logs_list: Lista de objetos AuditLog
            
        Returns:
            str: Texto formateado para mostrar al usuario
        """
        if not logs_list:
            return "📭 No hay registros disponibles."

        lines = []
        for log in logs_list:
            username = (
                f"@{log.user.username}"
                if hasattr(log, 'user') and log.user and hasattr(log.user, 'username') and log.user.username
                else (f"ID:{log.user_id}" if log.user_id else "SYSTEM")
            )
            created_at = log.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(log, 'created_at') else 'N/A'
            action = getattr(log, 'action', 'N/A')
            details = getattr(log, 'details', '') or ''
            
            lines.append(
                f"🕒 {created_at} | "
                f"{username} | {action} | {details}"
            )

        return "\n".join(lines)

# Instancia global del servicio
audit_service = AuditService()