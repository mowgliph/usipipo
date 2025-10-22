## Instrucciones rápidas para agentes AI (uSipipo)

Objetivo: ayudar a un agente a ser productivo rápidamente en este repositorio Python que implementa un bot de Telegram para gestionar VPNs (WireGuard / Outline) y pagos.

- Lenguaje y entorno: Python 3.11+, dependencias en `requirements.txt`. Archivo de ejemplo de variables de entorno: `example.env.md`.
- Entrypoint del bot: `bot/main.py` (usa `ApplicationBuilder` de python-telegram-bot y registra handlers desde `routes/routes.py`). Para ejecutar en desarrollo: ejecuta `python -m bot.main` o `python bot/main.py` con las variables de entorno configuradas.

Arquitectura y responsabilidad de componentes (big picture):
- `bot/`: handlers de Telegram organizados por responsabilidad (ej. `bot/handlers/vpn.py` para lógica VPN, `bot/handlers/qvapay.py` para conversación QvaPay). Los handlers se registran en `routes/routes.py`.
- `services/`: lógica de negocio y orquestación (por ejemplo `services/vpn.py`, `services/wireguard.py`, `services/qvapay_user_client.py`). Evita duplicar lógica aquí; los handlers deben delegar a `services`.
- `database/`: modelos SQLAlchemy 2.0 (`database/models.py`), helpers de acceso (`database/db.py`) y CRUD en `database/crud/*`. Usa siempre las funciones asíncronas y `get_session()` (context manager) para operar con la DB.
- `scripts/` y `jobs/`: scripts de utilidades y tareas programadas (APScheduler). `jobs/register_jobs.py` enlaza jobs en el arranque.

Convenciones y patrones importantes (específicos de este proyecto):
- Async-first: todo el acceso a DB y la mayor parte de la lógica es asíncrona. Usa `async def` y `async with get_session()` desde `database/db.py`.
- Session pattern: obtiene sesión con `async with get_session() as session:`; realizar cambios y `await session.commit()` en el mismo contexto si corresponde.
- Logging y errores: logger principal `usipipo`. Los handlers siguen patrón: try/except amplio -> `logger.exception(...)` + helpers `log_error_and_notify` / `log_and_notify` y `notify_admins` para alertas. Mantén ese patrón al añadir código nuevo.
- Helpers de respuesta: funciones en `utils/helpers.py` como `send_warning`, `send_success`, `send_vpn_config` para respuestas estándar al usuario. Reutilízalas en handlers.
- Permisos: decorador `@require_registered` (en `utils/permissions.py`) para comandos que requieren usuario registrado.
- Pagos: apoyar dos flujos: "Estrellas" (Telegram) y QvaPay. Revisa `bot/handlers/vpn.py` para ejemplos completos de callbacks, precheckout y successful_payment.

Integraciones externas clave:
- Base de datos: requiere `DATABASE_ASYNC_URL` (async driver: `asyncmy` o `aiomysql`). `database/db.py` valida driver y contiene `init_db()` para desarrollo.
- WireGuard/Outline: variables en `config/config.py` (`WG_*`, `OUTLINE_*`). Las instalaciones/recetas están en `scripts/*-install.sh`.
- QvaPay: cliente en `services/qvapay_user_client.py` y usage mostrado en `bot/handlers/vpn.py`.

Tests y flujos de desarrollo:
- Tests: hay tests en `test/` (por ejemplo `test/test_qvapay.py`). Ejecutar con `pytest -q` desde la raíz.
- Inicializar DB (dev): usar `database.db.init_db()` de forma programática o los scripts `scripts/init_db.py` / `scripts/reset_db.py`.
- Ejecutar localmente: asegúrate de exportar `DATABASE_ASYNC_URL` y `TELEGRAM_BOT_TOKEN` (usa `example.env.md` como guía), luego `python -m bot.main`.

Código: ejemplos y lugares a editar al añadir características
- Nuevo comando: crear handler en `bot/handlers/`, seguir patrón `async def <name>(update, context)` y registrar en `routes/routes.py` o en su propio `register_*_handlers(app)`.
- Acceso DB: usar `from database.db import get_session` y `async with get_session() as session:`; llamar a funciones CRUD en `database/crud/*`.
- Añadir servicio: crear en `services/` y exponer funciones async; los handlers deben orquestar solo interacción bot <-> services.

Notas operativas y límites conocidos
- No hay migraciones Alembic en este repositorio; en producción se espera usar Alembic. Para desarrollo `init_db()` crea tablas.
- `DATABASE_ASYNC_URL` es obligatorio y el proceso fallará si no está presente.
- Evitar cambios que rompan los contratos JSON en `vpn.config_data` o `ip_manager.extra_data`, porque se guardan como JSON en BD y otros servicios (WireGuard/Outline) asumen campos concretos.

Si falta algo o las variables de entorno críticas no están claras, lee `config/config.py` y `example.env.md`.

Preguntas para el mantenedor si aparece el agente:
- ¿Desean añadir migraciones (Alembic) en el repo o prefieren init_db en dev? 
- ¿Hay convenciones para nuevas columnas JSON (nombres, versiones, migraciones de formato)?

Fin.
