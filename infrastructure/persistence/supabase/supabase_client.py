"""
⚠️ DEPRECADO: Este módulo ya no se utiliza

Este archivo se mantiene solo por compatibilidad. 
Todos los accesos a base de datos deben usar SQLAlchemy Async en su lugar.

Importaciones reemplazadas:
  - get_supabase() → usar AsyncSession + repositorios SQLAlchemy
  - Client → AsyncSession

Para nuevas implementaciones, usar:
  from infrastructure.persistence.database import get_session_context
  from infrastructure.persistence.supabase.user_repository import SupabaseUserRepository

Author: uSipipo Team
Version: 2.0.0
"""

def get_supabase():
    """DEPRECADO: Esta función ya no debe usarse."""
    raise DeprecationWarning(
        "get_supabase() está deprecado. "
        "Usa AsyncSession con repositorios SQLAlchemy en su lugar."
    )

