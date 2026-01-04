"""
DEPRECADO: Este archivo se mantuvo para compatibilidad.

Los modelos han sido unificados en infrastructure/persistence/supabase/models/base.py

Por favor importa desde:
    from infrastructure.persistence.supabase.models import (
        AchievementModel,
        UserStatsModel,
        UserAchievementModel
    )

Author: uSipipo Team
Version: 2.0.0
"""

# Importar desde la ubicación centralizada para compatibilidad
from .base import (
    AchievementModel,
    UserStatsModel,
    UserAchievementModel
)

__all__ = [
    "AchievementModel",
    "UserStatsModel",
    "UserAchievementModel",
]
