Plan de Implementación Paso a Paso: uSipipo VPN Manager

📋 LISTA MAESTRA DE TAREAS (To-Do)

🏗️ FASE 1: CIMIENTOS DEL PROYECTO (Día 1-2)

Objetivo: Configurar el entorno y la estructura base.

1. Paso 1.1 - Crear estructura de directorios.
   ```
   mkdir -p mi_bot_vpn/{core,api/{v1/endpoints},telegram_bot/handlers,domain/{entities,interfaces},application/{services/common,ports},infrastructure/{persistence/supabase/models,api_clients},utils,templates,static/{qr_codes,configs},logs,temp}
   ```
2. Paso 1.2 - Crear requirements.txt con dependencias principales.
3. Paso 1.3 - Crear config.py (basado en el .env final que acordamos).
4. Paso 1.4 - Crear .env (copiar de tu plantilla y añadir SUPABASE_URL, SUPABASE_SERVICE_KEY, SECRET_KEY, etc.).
5. Paso 1.5 - Crear core/__init__.py y core/lifespan.py (gestor de ciclo de vida para FastAPI).

📦 FASE 2: CAPA DE DOMINIO (Día 3)

Objetivo: Definir las entidades y contratos centrales del negocio.

1. Paso 2.1 - Crear domain/entities/user.py (clase User con telegram_id, etc.).
2. Paso 2.2 - Crear domain/entities/vpn_key.py (clase VpnKey con key_data, type, user_id).
3. Paso 2.3 - Crear domain/interfaces/iuser_repository.py (interfaz IUserRepository con save, find_by_telegram_id).
4. Paso 2.4 - Crear domain/interfaces/ikey_repository.py (interfaz IKeyRepository).
5. Paso 2.5 - Crear domain/interfaces/ivpn_service.py (interfaz IVpnService con create_key, list_keys, revoke_key).

🗃️ FASE 3: CAPA DE INFRAESTRUCTURA - PERSISTENCIA (Día 4)

Objetivo: Implementar la conexión y operaciones con Supabase.

1. Paso 3.1 - Crear infrastructure/persistence/supabase/supabase_client.py (función get_client() singleton).
2. Paso 3.2 - Crear infrastructure/persistence/supabase/user_repository.py (clase SupabaseUserRepository implementando IUserRepository).
3. Paso 3.3 - Crear infrastructure/persistence/supabase/key_repository.py (clase SupabaseKeyRepository).
4. Paso 3.4 - VERIFICACIÓN: Crear un script temporal test_db.py para probar la conexión y operaciones CRUD básicas con Supabase.

⚙️ FASE 4: CAPA DE INFRAESTRUCTURA - CLIENTES VPN (Día 5)

Objetivo: Implementar la comunicación con los servidores de Outline y WireGuard.

1. Paso 4.1 - Crear infrastructure/api_clients/outline_client.py (clase OutlineClient que use outline-vpn-api).
2. Paso 4.2 - Crear infrastructure/api_clients/wireguard_client.py (clase WireGuardClient que use wireguard-tools o subprocess).
3. Paso 4.3 - VERIFICACIÓN: Crear un script temporal test_vpn_clients.py para probar la creación de una clave en Outline y WireGuard.

🧠 FASE 5: CAPA DE APLICACIÓN - SERVICIOS (Día 6-7)

Objetivo: Implementar la lógica de negocio que orquesta todo.

1. Paso 5.1 - Crear application/ports/outline_manager.py (clase OutlineManager, adaptador que use OutlineClient).
2. Paso 5.2 - Crear application/ports/wireguard_manager.py (clase WireGuardManager).
3. Paso 5.3 - Crear application/services/common/key_generator.py (funciones utilitarias para generar nombres, códigos).
4. Paso 5.4 - Crear application/services/vpn_orchestrator.py (clase VpnOrchestrator, implementa IVpnService, usa los managers y repositorios).
5. Paso 5.5 - Crear application/services/user_service.py (clase UserService para lógica de usuarios).
6. Paso 5.6 - VERIFICACIÓN: Actualizar test_db.py para probar el VpnOrchestrator completo (crear clave, listar, revocar).

🔌 FASE 6: NÚCLEO Y CONFIGURACIÓN FINAL (Día 8)

Objetivo: Conectar todas las piezas con Inyección de Dependencias.

1. Paso 6.1 - Crear core/container.py (configurar el contenedor punq para registrar e inyectar todas las dependencias: repositorios, managers, servicios).
2. Paso 6.2 - Crear utils/logger_setup.py (configurar logging estructurado para todo el proyecto).
3. Paso 6.3 - Crear utils/exceptions.py (definir excepciones personalizadas del dominio, ej: KeyLimitExceededError).

🤖 FASE 7: CAPA DE PRESENTACIÓN - BOT DE TELEGRAM (Día 9-10)

Objetivo: Construir la interfaz del bot, comando por comando.

1. Paso 7.1 - Crear core/bot_runner.py (configuración e inicialización del cliente python-telegram-bot).
2. Paso 7.2 - Crear telegram_bot/handlers/start_handler.py (comando /start básico).
3. Paso 7.3 - Crear telegram_bot/handlers/nueva_clave_handler.py (implementa el flujo para crear clave, usando VpnOrchestrator inyectado).
4. Paso 7.4 - Crear telegram_bot/handlers/listar_claves_handler.py.
5. Paso 7.5 - Crear telegram_bot/handlers/error_handler.py.
6. Paso 7.6 - Crear telegram_bot/handlers/__init__.py (para registrar todos los handlers).
7. Paso 7.7 - Crear bot.py (punto de entrada que une bot_runner y el contenedor).
8. Paso 7.8 - VERIFICACIÓN: Ejecutar python bot.py y probar los comandos /start y /nuevaclave en Telegram.

🌐 FASE 8: CAPA DE PRESENTACIÓN - API FASTAPI (Día 11-12)

Objetivo: Construir la API web, endpoint por endpoint.

1. Paso 8.1 - Crear api/dependencies.py (funciones get_vpn_service, get_current_user que resuelven del contenedor).
2. Paso 8.2 - Crear api/v1/endpoints/health.py (endpoint GET /health de prueba).
3. Paso 8.3 - Crear api/v1/endpoints/keys.py (endpoints POST /keys, GET /keys, DELETE /keys/{key_id}).
4. Paso 8.4 - Crear api/v1/endpoints/auth.py (endpoint POST /token para login, usando Supabase Auth o JWT).
5. Paso 8.5 - Crear api/v1/router.py (incluye todos los routers de endpoints).
6. Paso 8.6 - Crear api.py (aplicación FastAPI principal con lifespan, CORS, incluye router).
7. Paso 8.7 - VERIFICACIÓN: Ejecutar uvicorn api:app --reload y probar los endpoints con curl o Swagger (/docs).

🚀 FASE 9: DESPLIEGE Y AUTOMATIZACIÓN (Día 13)

Objetivo: Preparar el proyecto para producción en el VPS.

1. Paso 9.1 - Crear README.md con instrucciones de despliegue y uso.
2. Paso 9.2 - Crear scripts/install_dependencies.sh (opcional, para facilitar la instalación en el VPS).
3. Paso 9.3 - Crear docker-compose.yml (opcional, si decides usar Docker).
4. Paso 9.4 - DESPLIEGUE INICIAL: Sincronizar código con el VPS, configurar .env definitivo, probar con Pyker/PM2.
