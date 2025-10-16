#!/usr/bin/env python3
# scripts/init_db.py
import asyncio
import subprocess
import sys
import getpass
import os
import logging
from typing import Optional

import typer
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Importar desde database.db
from database.db import async_engine, init_db as async_init_db, get_sync_database_url

logger = logging.getLogger("usipipo")
app = typer.Typer(add_completion=False)


# --------------------
# Helpers de sistema
# --------------------
def run_command(cmd: list[str], use_sudo: bool = False) -> bool:
    """Ejecuta un comando del sistema. Opcionalmente con sudo."""
    if use_sudo:
        cmd = ["sudo"] + cmd
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_mariadb_installed() -> bool:
    """Verifica si mariadb (cliente) está instalado."""
    # Primero intentamos con mariadb (nuevo cliente)
    try:
        subprocess.run(["mariadb", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    # Si falla, intentamos con mysql (cliente viejo)
    try:
        subprocess.run(["mysql", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def install_mariadb_interactive() -> bool:
    """
    Intenta instalar MariaDB usando apt. Opcionalmente con sudo.
    Funciona para Debian/Ubuntu.
    """
    print("Intentando instalar MariaDB...")
    # Intenta sin sudo primero
    if run_command(["apt-get", "update"]) and run_command(["apt-get", "install", "-y", "mariadb-server", "mariadb-client"]):
        print("✅ MariaDB instalado con apt (sin sudo).")
        return True
    # Si falla, intenta con sudo
    if run_command(["apt-get", "update"], use_sudo=True) and run_command(["apt-get", "install", "-y", "mariadb-server", "mariadb-client"], use_sudo=True):
        print("✅ MariaDB instalado con apt (con sudo).")
        return True
    print("❌ No se pudo instalar MariaDB automáticamente.")
    return False


# --------------------
# Síncrono: creación de DB/usuario y validación
# (se hace con engine sync porque la creación de DB no
#  siempre es práctica desde un engine async)
# --------------------
def create_db_and_user_sync(db_name: str, db_user: str, host: str = "localhost", port: int = 3306) -> tuple[str, str]:
    """
    Crea la base de datos y el usuario en MariaDB usando sudo mariadb.
    Solicita la contraseña interactivamente.
    Retorna una tupla con (DATABASE_URL_sync, DATABASE_URL_async).
    """
    db_pass = getpass.getpass(f"🔑 Ingresa la contraseña para el nuevo usuario '{db_user}': ")
    db_pass_confirm = getpass.getpass(f"🔑 Confirma la contraseña para el usuario '{db_user}': ")
    if db_pass != db_pass_confirm:
        print("❌ Las contraseñas no coinciden.")
        raise typer.Exit(code=1)

    sql_commands = f"""
    CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE USER IF NOT EXISTS '{db_user}'@'{host}' IDENTIFIED BY '{db_pass}';
    GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{db_user}'@'{host}';
    FLUSH PRIVILEGES;
    """
    try:
        # Usamos sudo mariadb para ejecutar con permisos
        # Se asume que el usuario actual tiene permisos de sudo para ejecutar mariadb
        subprocess.run(["sudo", "mariadb", "-e", sql_commands], check=True)
        print(f"✅ Base de datos '{db_name}' y usuario '{db_user}' creados.")
    except subprocess.CalledProcessError as e:
        logger.error("Error creando DB/usuario: %s", e, extra={"user_id": None})
        raise RuntimeError("No se pudo crear la base de datos o el usuario. Asegúrate de tener permisos de sudo para mariadb.") from e

    # Construir URLs
    db_url_sync = f"mysql+pymysql://{db_user}:{db_pass}@{host}:{port}/{db_name}"
    db_url_async = f"mysql+asyncmy://{db_user}:{db_pass}@{host}:{port}/{db_name}"

    return db_url_sync, db_url_async


def validate_connection_sync(db_url: str) -> None:
    """Valida la conexión a la base de datos usando un engine síncrono."""
    try:
        engine = create_engine(db_url, echo=False, future=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        print("✅ Conexión a la base de datos verificada.")
    except Exception as e:
        logger.error("Error validando conexión: %s", e, extra={"user_id": None})
        raise


def ensure_schema_simple(db_url: str) -> None:
    """
    Ejecuta tareas de ajuste simples en el esquema si es necesario.
    Por ejemplo, añadir columnas faltantes críticas.
    """
    engine = create_engine(db_url, echo=False, future=True)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "users" not in tables:
        print("⚠️ Tabla 'users' aún no existe. Se omitirá validación de columnas.")
        engine.dispose()
        return

    with engine.connect() as conn:
        # Ejemplo: Asegurar que 'is_superadmin' exista
        result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'is_superadmin';")).fetchone()
        if not result:
            print("⚠️ Columna 'is_superadmin' no existe. Creándola...")
            conn.execute(text("ALTER TABLE users ADD COLUMN is_superadmin TINYINT(1) NOT NULL DEFAULT 0;"))
            conn.commit() # Asegurar commit para DDL
            print("✅ Columna 'is_superadmin' añadida.")
    engine.dispose()


# --------------------
# Async wrappers
# --------------------
async def _async_init_db_create() -> None:
    """Wrapper asíncrono para inicializar el esquema."""
    await async_init_db(create=True)


# --------------------
# CLI Commands
# --------------------
@app.command()
def create(
    db_name: str = typer.Option("usipipo", help="Nombre de la base de datos"),
    db_user: str = typer.Option("usipipo", help="Usuario a crear para la base"),
    host: str = typer.Option("localhost", help="Host para el usuario DB"),
    port: int = typer.Option(3306, help="Puerto DB"),
    skip_db_install: bool = typer.Option(False, help="Si True no intentará instalar MariaDB"),
    write_env: bool = typer.Option(True, help="Si True imprimirá/guardará las líneas DATABASE_URL en .env"),
):
    """
    Crea la base de datos y usuario (local). Intenta instalar MariaDB si no está presente.
    Luego valida la conexión y crea tablas (async).
    Finalmente, imprime las variables de entorno necesarias para uSipipo.
    """
    try:
        if not skip_db_install and not check_mariadb_installed():
            print("⚠️ MariaDB no está instalado. Intentando instalar...")
            if not install_mariadb_interactive():
                print("❌ No se pudo instalar MariaDB automáticamente. Instala manualmente o usa --skip-db-install.")
                raise typer.Exit(code=1)

        db_url_sync, db_url_async = create_db_and_user_sync(db_name=db_name, db_user=db_user, host=host, port=port)
        validate_connection_sync(db_url_sync)

        print("🔹 Creando tablas (async)...")
        # temporalmente exportamos DATABASE_ASYNC_URL para que async init use la misma DB
        os.environ.setdefault("DATABASE_ASYNC_URL", db_url_async)
        asyncio.run(_async_init_db_create())
        print("✅ Tablas creadas/actualizadas correctamente en la base de datos.")

        ensure_schema_simple(db_url_sync)

        # Generar y mostrar variables .env
        generate_env_variables(db_url_sync, db_url_async)

        if write_env:
            write_env_to_file(db_url_sync, db_url_async)

    except Exception as e:
        logger.exception("create_command_failed", extra={"user_id": None})
        typer.echo(f"❌ Falló la creación: {e}")
        raise typer.Exit(code=1)


def generate_env_variables(db_url_sync: str, db_url_async: str):
    """Genera e imprime las variables de entorno necesarias para uSipipo."""
    print("\n--- VARIABLES DE ENTORNO PARA USIPIPO ---")
    print("# Copia estas líneas en tu archivo .env")
    print(f"DATABASE_URL={db_url_sync}")
    print(f"DATABASE_ASYNC_URL={db_url_async}")
    print(f"DATABASE_SYNC_URL={db_url_sync}")
    print("# Ajusta otros parámetros según sea necesario")
    print("# TELEGRAM_BOT_TOKEN=")
    print("# MTPROXY_HOST=")
    print("# MTPROXY_PORT=")
    print("# MTPROXY_SECRET=")
    print("# OUTLINE_API_URL=")
    print("# OUTLINE_CERT_SHA256=")
    print("# WG_SERVER_IP=")
    print("# WG_PORT=")
    print("# WG_SUBNET_BASE=")
    print("# WG_DNS=")
    print("# WG_ALLOWED_IPS=")
    print("# DB_POOL_PRE_PING=true")
    print("# DB_ECHO_SQL=false")
    print("# DB_MAX_OVERFLOW=10")
    print("# DB_POOL_SIZE=5")
    print("# DB_POOL_TIMEOUT=30")
    print("# DB_CHARSET=utf8mb4")
    print("-----------------------------------------")


def write_env_to_file(db_url_sync: str, db_url_async: str):
    """Escribe las variables principales de conexión a un archivo .env."""
    env_line_sync = f"DATABASE_URL={db_url_sync}"
    env_line_async = f"DATABASE_ASYNC_URL={db_url_async}"
    env_line_sync_dup = f"DATABASE_SYNC_URL={db_url_sync}"

    print("\n👉 Añadiendo líneas principales a .env...")
    try:
        with open(".env", "a", encoding="utf-8") as f:
            f.write("\n" + env_line_sync + "\n")
            f.write(env_line_async + "\n")
            f.write(env_line_sync_dup + "\n")
        print("✅ Líneas añadidas a .env")
    except Exception as e:
        print(f"⚠️ No se pudo escribir en .env automáticamente: {e}")
        print("Copia las líneas mostradas arriba manualmente.")


@app.command()
def drop(
    db_url: Optional[str] = typer.Option(None, help="URL de la base a dropear. Si no se proporciona usará DATABASE_SYNC_URL env."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirmación automática para drop"),
):
    """
    Elimina todas las tablas de la base de datos. Pide confirmación por defecto.
    Usar con cuidado en entornos semi-production.
    """
    url = db_url or get_sync_database_url() or os.getenv("DATABASE_URL")
    if not url:
        typer.echo("❌ No hay DATABASE_URL o DATABASE_SYNC_URL configurada. Provee --db-url o exporta la variable.")
        raise typer.Exit(code=1)

    if not yes:
        typer.echo("⚠️ Estás a punto de ELIMINAR todas las tablas en la base indicada.")
        confirm = typer.prompt("Escribe 'DROP' para confirmar", default="")
        if confirm != "DROP":
            typer.echo("Aborted by user.")
            raise typer.Exit()

    try:
        engine = create_engine(url, echo=False, future=True)
        Base = None
        # Intentamos cargar metadata si disponible en package
        try:
            from database.db import Base as DeclarativeBase  # type: ignore
            Base = DeclarativeBase
        except Exception:
            Base = None

        if Base:
            print("Eliminando tablas usando metadata...")
            with engine.begin() as conn:
                DeclarativeBase.metadata.drop_all(conn)  # type: ignore
        else:
            # Fallback: intentar DROP esquema básico (peligroso, se ejecuta solo si Base no importó)
            print("Metadata no disponible, eliminando tablas manualmente...")
            with engine.begin() as conn:
                conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
                # lista tablas y dropear cada una
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                for t in tables:
                    print(f"Eliminando tabla: {t}")
                    conn.execute(text(f"DROP TABLE IF EXISTS `{t}`;"))
                conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))

        engine.dispose()
        typer.echo("✅ Todas las tablas han sido eliminadas.")
    except Exception as e:
        logger.exception("drop_command_failed", extra={"user_id": None})
        typer.echo(f"❌ Error al dropear tablas: {e}")
        raise typer.Exit(code=1)


@app.command()
def init(
    migrate: bool = typer.Option(False, help="Si True, imprime instrucciones para usar Alembic (no corre migraciones automáticamente)"),
):
    """
    Inicializa el esquema (usa async init_db helper). En producción usar Alembic.
    """
    if migrate:
        typer.echo("➡️ Modo migrate: revisa Alembic/versions y ejecuta `alembic upgrade head` localmente.")
        raise typer.Exit()

    # Ejecutar init_db async
    try:
        asyncio.run(_async_init_db_create())
        typer.echo("✅ Esquema inicializado (async).")
    except Exception as e:
        logger.exception("init_command_failed", extra={"user_id": None})
        typer.echo(f"❌ Error inicializando esquema: {e}")
        raise typer.Exit(code=1)


@app.command()
def check():
    """
    Verifica la conexión a la DB configurada en DATABASE_URL / DATABASE_SYNC_URL.
    """
    url = get_sync_database_url() or os.getenv("DATABASE_URL")
    if not url:
        typer.echo("❌ No hay DATABASE_URL o DATABASE_SYNC_URL configurada.")
        raise typer.Exit(code=1)
    try:
        validate_connection_sync(url)
    except Exception as e:
        logger.exception("check_command_failed", extra={"user_id": None})
        typer.echo(f"❌ Error verificando conexión: {e}")
        raise typer.Exit(code=1)


# --------------------
# Entrypoint
# --------------------
def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    app()

if __name__ == "__main__":
    main()