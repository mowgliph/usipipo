#!/usr/bin/env python3
"""
reset_db.py — Script para recrear o sincronizar la base de datos de uSipipo VPN.
Compatible con entornos de desarrollo y semi-producción.

Uso:
  - Modo seguro (solo crea tablas faltantes, NO borra datos):
        python scripts/reset_db.py --safe

  - Modo forzado (borra y recrea TODAS las tablas):
        python scripts/reset_db.py --force
"""

from database.db import Base, engine
from sqlalchemy import inspect
import sys


def get_existing_tables():
    """Devuelve las tablas existentes actualmente en la base de datos."""
    inspector = inspect(engine)
    return inspector.get_table_names()


def safe_create():
    """Crea solo las tablas que aún no existen (modo seguro)."""
    existing = set(get_existing_tables())
    all_tables = set(Base.metadata.tables.keys())
    missing = all_tables - existing

    if not missing:
        print("✅ No hay tablas faltantes. La base de datos está actualizada.")
        return

    print(f"🛠️ Creando tablas faltantes: {', '.join(missing)}")
    for table_name in missing:
        table = Base.metadata.tables[table_name]
        table.create(bind=engine)
    print("✅ Tablas nuevas creadas correctamente.")


def force_reset():
    """Elimina todas las tablas y las vuelve a crear."""
    print("⚠️ Este modo eliminará TODAS las tablas existentes.")
    confirm = input("¿Deseas continuar? (escribe 'CONFIRMAR' para continuar): ")
    if confirm != "CONFIRMAR":
        print("❌ Operación cancelada.")
        return

    print("🧨 Eliminando tablas...")
    Base.metadata.drop_all(bind=engine)
    print("📦 Recreando tablas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos recreada completamente.")


if __name__ == "__main__":
    if "--force" in sys.argv:
        force_reset()
    else:
        safe_create()