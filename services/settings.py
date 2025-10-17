# services/settings.py

from __future__ import annotations
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from database.crud import settings as crud_settings, logs as crud_logs
from database import models
import logging

# =====================================================
# ⚙️ SERVICIO DE CONFIGURACIONES DE USUARIO
# =====================================================
# Gestiona las preferencias de cada usuario y registra
# los cambios relevantes en la auditoría del sistema.
# =====================================================

logger = logging.getLogger("usipipo.services.settings")


async def get_settings(session: AsyncSession, user_id: str) -> List[models.UserSetting]:
    """
    Devuelve todas las configuraciones de un usuario.
    """
    try:
        return await crud_settings.list_user_settings(session, user_id)
    except Exception as e:
        logger.exception("Error obteniendo settings de usuario", extra={"user_id": user_id})
        return []


async def get_setting(session: AsyncSession, user_id: str, key: str) -> Optional[models.UserSetting]:
    """
    Obtiene un setting específico de un usuario.
    Retorna None si no existe o si ocurre un error.
    """
    try:
        return await crud_settings.get_user_setting(session, user_id, key)
    except Exception as e:
        logger.exception("Error obteniendo setting específico", extra={"user_id": user_id, "key": key})
        return None


async def update_setting(session: AsyncSession, user_id: str, key: str, value: str) -> Optional[models.UserSetting]:
    """
    Crea o actualiza un setting de usuario y registra el cambio en logs.
    El commit principal ocurre solo una vez para reducir I/O y evitar conflictos.
    """
    try:
        # 1️⃣ Actualizar/crear configuración
        setting = await crud_settings.set_user_setting(session, user_id, key, value, commit=False)

        # 2️⃣ Registrar acción en auditoría
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="update_setting",
            payload={"key": key, "value": value},
            commit=False
        )

        # 3️⃣ Confirmar ambas operaciones en una sola transacción
        await session.commit()
        await session.refresh(setting)

        return setting

    except Exception as e:
        logger.exception("Error actualizando setting", extra={"user_id": user_id, "key": key})
        await session.rollback()
        return None