#!/usr/bin/env python3
# scripts/init_db.py
"""
Database initialization script for uSipipo.

This script focuses exclusively on database initialization tasks:
- Creating database schema (async)
- Dropping all tables (async)
- Checking database connection and integrity
- Initializing schema

All operations use async architecture with AsyncSessionLocal.
Compatible with DATABASE_* environment variables from mariadb-install.sh.
"""

import asyncio
import logging
import os
import sys
from typing import Optional

import typer
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import AsyncSessionLocal, async_engine, get_sync_database_url, init_db, Base
from utils.helpers import log_error_and_notify

logger = logging.getLogger("usipipo.init_db")
app = typer.Typer(add_completion=False)


async def verify_database_integrity() -> bool:
    """
    Verifica la integridad de la base de datos.

    Checks:
    - Conexión básica
    - Existencia de tablas críticas
    - Estructura básica de tablas principales

    Returns:
        bool: True si la integridad es correcta, False en caso contrario
    """
    try:
        async with AsyncSessionLocal() as session:
            # Verificar conexión
            await session.execute(text("SELECT 1"))

            # Verificar tablas críticas
            inspector = inspect(async_engine.sync_engine)
            tables = inspector.get_table_names()

            required_tables = ["users", "roles", "vpn_configs", "payments", "logs"]
            missing_tables = [table for table in required_tables if table not in tables]

            if missing_tables:
                logger.warning("Tablas faltantes detectadas: %s", missing_tables)
                return False

            # Verificar estructura básica de tabla users
            if "users" in tables:
                columns = [col["name"] for col in inspector.get_columns("users")]
                required_columns = ["id", "telegram_id", "username", "is_superadmin"]
                missing_columns = [col for col in required_columns if col not in columns]

                if missing_columns:
                    logger.warning("Columnas faltantes en tabla users: %s", missing_columns)
                    return False

            logger.info("Verificación de integridad de base de datos completada exitosamente")
            return True

    except Exception as e:
        logger.exception("Error durante verificación de integridad: %s", e)
        return False


async def async_drop_tables() -> None:
    """
    Elimina todas las tablas de la base de datos de forma asíncrona.
    """
    try:
        async with async_engine.begin() as conn:
            logger.info("Eliminando todas las tablas usando metadata...")
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Todas las tablas han sido eliminadas exitosamente")
    except Exception as e:
        logger.exception("Error eliminando tablas: %s", e)
        raise


# --------------------
# CLI Commands
# --------------------
@app.command()
def create(
    write_env: bool = typer.Option(True, help="Si True, muestra instrucciones para variables de entorno"),
):
    """
    Inicializa el esquema de la base de datos usando las variables de entorno.
    Valida la conexión, crea tablas (async) y verifica integridad.
    """
    async def _create_async():
        try:
            # Verificar variables de entorno
            db_url = get_sync_database_url()
            if not db_url:
                typer.echo("❌ No se encontró DATABASE_URL o DATABASE_SYNC_URL en las variables de entorno.")
                typer.echo("Ejecuta primero scripts/mariadb-install.sh para configurar MariaDB.")
                raise typer.Exit(code=1)

            # Verificar que DATABASE_ASYNC_URL esté configurada
            db_async_url = os.getenv("DATABASE_ASYNC_URL")
            if not db_async_url:
                typer.echo("❌ DATABASE_ASYNC_URL no está configurada.")
                typer.echo("Asegúrate de que las variables de entorno estén correctamente configuradas.")
                raise typer.Exit(code=1)

            typer.echo("🔹 Verificando conexión a la base de datos...")
            # Usar la función de integridad que incluye verificación de conexión
            integrity_ok = await verify_database_integrity()
            if not integrity_ok:
                typer.echo("⚠️ La base de datos existe pero puede tener problemas de integridad.")

            typer.echo("🔹 Creando/actualizando tablas (async)...")
            await init_db(create=True)
            typer.echo("✅ Tablas creadas/actualizadas correctamente.")

            typer.echo("🔹 Verificando integridad final...")
            integrity_ok = await verify_database_integrity()
            if integrity_ok:
                typer.echo("✅ Integridad de base de datos verificada.")
            else:
                typer.echo("⚠️ La base de datos tiene problemas de integridad. Revisa los logs.")

            if write_env:
                typer.echo("\n--- VARIABLES DE ENTORNO PARA USIPIPO ---")
                typer.echo("# Asegúrate de que estas variables estén en tu archivo .env")
                typer.echo(f"DATABASE_URL={db_url}")
                typer.echo(f"DATABASE_ASYNC_URL={db_async_url}")
                typer.echo(f"DATABASE_SYNC_URL={db_url}")
                typer.echo("# Ajusta otros parámetros según sea necesario")
                typer.echo("# TELEGRAM_BOT_TOKEN=")
                typer.echo("# ... (otras variables)")
                typer.echo("-----------------------------------------")

        except Exception as e:
            await log_error_and_notify(
                session=None,
                bot=None,
                chat_id=None,
                user_id=None,
                action="init_db_create",
                error=e,
                public_message="Error inicializando base de datos"
            )
            typer.echo(f"❌ Falló la creación: {e}")
            raise typer.Exit(code=1)

    asyncio.run(_create_async())


@app.command()
def drop(
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirmación automática para drop"),
):
    """
    Elimina todas las tablas de la base de datos. Pide confirmación por defecto.
    Usar con cuidado en entornos semi-production.
    """
    async def _drop_async():
        try:
            db_url = get_sync_database_url() or os.getenv("DATABASE_URL")
            if not db_url:
                typer.echo("❌ No hay DATABASE_URL o DATABASE_SYNC_URL configurada.")
                raise typer.Exit(code=1)

            if not yes:
                typer.echo("⚠️ Estás a punto de ELIMINAR todas las tablas en la base de datos.")
                confirm = typer.prompt("Escribe 'DROP' para confirmar", default="")
                if confirm != "DROP":
                    typer.echo("Operación cancelada.")
                    raise typer.Exit()

            typer.echo("🔹 Eliminando todas las tablas...")
            await async_drop_tables()
            typer.echo("✅ Todas las tablas han sido eliminadas.")

        except Exception as e:
            await log_error_and_notify(
                session=None,
                bot=None,
                chat_id=None,
                user_id=None,
                action="init_db_drop",
                error=e,
                public_message="Error eliminando tablas de base de datos"
            )
            typer.echo(f"❌ Error al eliminar tablas: {e}")
            raise typer.Exit(code=1)

    asyncio.run(_drop_async())


@app.command()
def init():
    """
    Inicializa el esquema de la base de datos (usa async init_db helper).
    En producción usar Alembic para migraciones.
    """
    async def _init_async():
        try:
            typer.echo("🔹 Inicializando esquema (async)...")
            await init_db(create=True)
            typer.echo("✅ Esquema inicializado.")
        except Exception as e:
            await log_error_and_notify(
                session=None,
                bot=None,
                chat_id=None,
                user_id=None,
                action="init_db_init",
                error=e,
                public_message="Error inicializando esquema de base de datos"
            )
            typer.echo(f"❌ Error inicializando esquema: {e}")
            raise typer.Exit(code=1)

    asyncio.run(_init_async())


@app.command()
def check():
    """
    Verifica la conexión a la DB y la integridad del esquema configurado en DATABASE_URL/DATABASE_SYNC_URL.
    """
    async def _check_async():
        try:
            db_url = get_sync_database_url() or os.getenv("DATABASE_URL")
            if not db_url:
                typer.echo("❌ No hay DATABASE_URL o DATABASE_SYNC_URL configurada.")
                raise typer.Exit(code=1)

            typer.echo("🔹 Verificando conexión e integridad...")
            integrity_ok = await verify_database_integrity()

            if integrity_ok:
                typer.echo("✅ Conexión e integridad de base de datos verificadas correctamente.")
            else:
                typer.echo("⚠️ La base de datos tiene problemas de integridad.")
                typer.echo("Revisa los logs para más detalles.")
                raise typer.Exit(code=1)

        except Exception as e:
            await log_error_and_notify(
                session=None,
                bot=None,
                chat_id=None,
                user_id=None,
                action="init_db_check",
                error=e,
                public_message="Error verificando base de datos"
            )
            typer.echo(f"❌ Error verificando conexión: {e}")
            raise typer.Exit(code=1)

    asyncio.run(_check_async())


# --------------------
# Entrypoint
# --------------------
def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    app()


if __name__ == "__main__":
    main()