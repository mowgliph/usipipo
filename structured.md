Estructura Completa del Proyecto: Bot + API de Gestión VPN

🗂️ Estructura de Directorios y Archivos
(venv) mowgli@usipipo:~/us$ tree -I *venv* -L 5
.
├── alembic.ini
├── api
│   ├── __init__.py
│   └── v1
│       ├── endpoints
│       │   └── __init__.py
│       └── __init__.py
├── application
│   ├── __init__.py
│   ├── ports
│   │   └── __init__.py
│   ├── __pycache__
│   │   └── __init__.cpython-313.pyc
│   └── services
│       ├── common
│       │   ├── container.py
│       │   ├── __init__.py
│       │   └── __pycache__
│       │       ├── container.cpython-313.pyc
│       │       └── __init__.cpython-313.pyc
│       ├── __init__.py
│       ├── __pycache__
│       │   ├── __init__.cpython-313.pyc
│       │   ├── support_service.cpython-313.pyc
│       │   └── vpn_service.cpython-313.pyc
│       ├── support_service.py
│       └── vpn_service.py
├── config.py
├── core
│   ├── __init__.py
│   └── lifespan.py
├── domain
│   ├── entities
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-313.pyc
│   │   │   ├── ticket.cpython-313.pyc
│   │   │   ├── user.cpython-313.pyc
│   │   │   └── vpn_key.cpython-313.pyc
│   │   ├── ticket.py
│   │   ├── user.py
│   │   └── vpn_key.py
│   ├── __init__.py
│   ├── interfaces
│   │   ├── ikey_repository.py
│   │   ├── __init__.py
│   │   ├── iuser_repository.py
│   │   ├── ivpn_service.py
│   │   └── __pycache__
│   │       ├── ikey_repository.cpython-313.pyc
│   │       ├── __init__.cpython-313.pyc
│   │       └── iuser_repository.cpython-313.pyc
│   └── __pycache__
│       └── __init__.cpython-313.pyc
├── example.env
├── infrastructure
│   ├── api_clients
│   │   ├── client_outline.py
│   │   ├── client_wireguard.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       ├── client_outline.cpython-313.pyc
│   │       ├── client_wireguard.cpython-313.pyc
│   │       └── __init__.cpython-313.pyc
│   ├── __init__.py
│   ├── jobs
│   │   ├── __init__.py
│   │   ├── ticket_cleaner.py
│   │   └── usage_sync.py
│   ├── persistence
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   └── __init__.cpython-313.pyc
│   │   └── supabase
│   │       ├── __init__.py
│   │       ├── key_repository.py
│   │       ├── models
│   │       │   ├── base.py
│   │       │   ├── __init__.py
│   │       │   └── __pycache__
│   │       ├── __pycache__
│   │       │   ├── __init__.cpython-313.pyc
│   │       │   ├── key_repository.cpython-313.pyc
│   │       │   ├── supabase_client.cpython-313.pyc
│   │       │   ├── ticket_repository.cpython-313.pyc
│   │       │   └── user_repository.cpython-313.pyc
│   │       ├── supabase_client.py
│   │       ├── ticket_repository.py
│   │       └── user_repository.py
│   └── __pycache__
│       └── __init__.cpython-313.pyc
├── install.sh
├── LICENCE
├── main.py
├── migrations
│   ├── env.py
│   ├── __pycache__
│   │   └── env.cpython-313.pyc
│   ├── README
│   ├── script.py.mako
│   └── versions
│       ├── d617956ef9ba_init_db_usipipo.py
│       └── __pycache__
│           └── d617956ef9ba_init_db_usipipo.cpython-313.pyc
├── ol_server.sh
├── piker.json
├── __pycache__
│   └── config.cpython-313.pyc
├── requirements.txt
├── static
│   ├── configs
│   │   └── __init__.py
│   ├── __init__.py
│   └── qr_codes
│       └── __init__.py
├── structured.md
├── telegram_bot
│   ├── handlers
│   │   ├── ayuda_handler.py
│   │   ├── crear_llave_handler.py
│   │   ├── __init__.py
│   │   ├── keys_manager_handler.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-313.pyc
│   │   │   └── start_handler.cpython-313.pyc
│   │   ├── start_handler.py
│   │   ├── status_handler.py
│   │   └── support_handler.py
│   ├── __init__.py
│   ├── keyboard
│   │   ├── __init__.py
│   │   └── keyboard.py
│   ├── messages
│   │   ├── __init__.py
│   │   ├── messages.py
│   │   └── __pycache__
│   │       └── __init__.cpython-313.pyc
│   └── __pycache__
│       └── __init__.cpython-313.pyc
├── temp
│   └── __init__.py
├── templates
│   └── __init__.py
├── test_db.py
├── To-Do.md
├── utils
│   ├── __init__.py
│   └── qr_generator.py
└── wg_server.sh
47 directories, 103 files
(venv) mowgli@usipipo:~/us$

🔄 Flujo de Datos entre Capas

Ejemplo 1: Comando /nuevaclave outline en Telegram

1. bot.py → core/bot_runner.py → telegram_bot/handlers/nueva_clave_handler.py
2. El handler llama a application/services/vpn_orchestrator.py
3. El orchestrator usa application/ports/outline_manager.py
4. El manager usa infrastructure/api_clients/outline_client.py
5. Los datos se guardan via infrastructure/persistence/supabase/key_repository.py
6. La respuesta fluye de vuelta al handler → usuario

Ejemplo 2: Petición POST /api/v1/keys en FastAPI

1. api.py → api/v1/endpoints/keys.py
2. El endpoint usa Depends(get_vpn_service) de api/dependencies.py
3. La dependencia resuelve application/services/vpn_orchestrator.py (¡LA MISMA que usa el bot!)
4. Flujo idéntico a partir del paso 3 del ejemplo anterior


🚀 Guía de Despliegue Rápido

1. Preparar el VPS:
   ```bash
   # Instalar Python, pip, git
   sudo apt update && sudo apt install python3.11 python3-pip git
   
   # Clonar el proyecto
   git clone <tu-repositorio>
   cd mi_bot_vpn
   
   # Entorno virtual
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configurar Variables de Entorno:
   ```bash
   cp .env.example .env
   # Editar .env con tus tokens y URLs
   ```
3. Configurar Base de Datos en Supabase:
   · Crear tablas users y vpn_keys en el dashboard de Supabase
   · Obtener SUPABASE_URL y SUPABASE_SERVICE_KEY
4. Ejecutar con Pyker (Recomendado):
   ```bash
   # Instalar Pyker
   curl -fsSL https://raw.githubusercontent.com/mrvi0/pyker/main/install.sh | bash
   
   # Iniciar el bot
   pyker start VpnBot bot.py --venv ./venv --auto-restart
   
   # Iniciar la API
   pyker start VpnApi api.py --venv ./venv --auto-restart --port 8000
   
   # Ver estado
   pyker list
   ```
5. Alternativa con PM2:
   ```bash
   npm install pm2 -g
   pm2 start bot.py --name "vpn-bot" --interpreter python3
   pm2 start "uvicorn api:app" --name "vpn-api"
   pm2 save
   pm2 startup
   ```

✅ Ventajas Clave de Esta Arquitectura

1. Separación de Responsabilidades (SRP): Cada archivo tiene una única razón para cambiar.
2. Reutilización Máxima: Las capas de Aplicación, Dominio e Infraestructura son compartidas al 100% entre el bot y la API.
3. Testabilidad: Aunque no implementes tests, la arquitectura lo facilita enormemente.
4. Escalabilidad: Puedes añadir nuevas interfaces (CLI, dashboard) sin tocar la lógica de negocio.
5. Mantenibilidad: Cambiar de Supabase a otra BD, o de Outline a otro VPN, solo afecta a la capa de Infraestructura.

