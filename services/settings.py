# services/settings.py

from sqlalchemy.orm import Session
from typing import Optional, List
from database.crud import settings, logs
from database import models
import traceback

# =====================================================
# ⚙️ SERVICIO DE CONFIGURACIONES DE USUARIO
# =====================================================
# Gestiona las preferencias de cada usuario y registra
# los cambios relevantes en la auditoría del sistema.
# =====================================================


def get_settings(db: Session, user_id: int) -> List[models.UserSetting]:
    """
    Devuelve todas las configuraciones de un usuario.
    """
    try:
        return settings.get_user_settings(db, user_id)
    except Exception as e:
        print(f"[WARN] Error obteniendo settings de usuario {user_id}: {e}")
        traceback.print_exc()
        db.rollback()
        return []


def get_setting(db: Session, user_id: int, key: str) -> Optional[models.UserSetting]:
    """
    Obtiene un setting específico de un usuario.
    Retorna None si no existe o si ocurre un error.
    """
    try:
        return settings.get_user_setting(db, user_id, key)
    except Exception as e:
        print(f"[WARN] Error obteniendo setting '{key}' para usuario {user_id}: {e}")
        traceback.print_exc()
        db.rollback()
        return None


def update_setting(db: Session, user_id: int, key: str, value: str) -> Optional[models.UserSetting]:
    """
    Crea o actualiza un setting de usuario y registra el cambio en logs.
    El commit principal ocurre solo una vez para reducir I/O y evitar conflictos.
    """
    try:
        # 1️⃣ Actualizar/crear configuración
        setting = settings.set_user_setting(db, user_id, key, value)

        # 2️⃣ Registrar acción en auditoría
        logs.log_action(db, user_id, "update_setting", f"{key}={value}")

        # 3️⃣ Confirmar ambas operaciones en una sola transacción
        db.commit()
        db.refresh(setting)

        return setting

    except Exception as e:
        print(f"[WARN] Error actualizando setting '{key}' para usuario {user_id}: {e}")
        traceback.print_exc()
        db.rollback()
        return None