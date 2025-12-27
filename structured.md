Estructura Completa del Proyecto: Bot + API de Gestión VPN

🗂️ Estructura de Directorios y Archivos

```
usipipo/
│
├── bot.py                      # Punto de entrada del bot de Telegram (< 50 líneas)
├── api.py                      # Punto de entrada de FastAPI (< 50 líneas)
├── config.py                   # Configuración centralizada (< 150 líneas)
├── requirements.txt            # Dependencias del proyecto
├── .env.example                # Variables de entorno (plantilla)
├── README.md                   # Documentación de despliegue
│
├── core/                       # Configuración central e inicio
│   ├── __init__.py
│   ├── container.py            # Contenedor de inyección de dependencias (punq)
│   ├── bot_runner.py           # Inicializa y lanza el bot de Telegram
│   └── lifespan.py             # Gestión del ciclo de vida (FastAPI)
│
├── api/                        # CAPA DE PRESENTACIÓN: FastAPI (Web)
│   ├── __init__.py
│   ├── dependencies.py         # Dependencias para inyección en endpoints
│   └── v1/                     # Versión 1 de la API
│       ├── __init__.py
│       ├── router.py           # Router principal que incluye todos los endpoints
│       └── endpoints/          # UN ARCHIVO POR CONJUNTO DE ENDPOINTS
│           ├── __init__.py
│           ├── auth.py         # POST /token, registro, etc.
│           ├── users.py        # GET/PUT/PATCH /users
│           ├── keys.py         # POST/GET/DELETE /vpn/keys
│           └── health.py       # GET /health
│
├── telegram_bot/               # CAPA DE PRESENTACIÓN: Bot de Telegram
│   ├── __init__.py
│   └── handlers/               # UN ARCHIVO POR HANDLER/COMANDO
│       ├── __init__.py         # Registra todos los handlers
│       ├── start_handler.py    # Maneja /start
│       ├── ayuda_handler.py    # Maneja /ayuda
│       ├── nueva_clave_handler.py # Maneja /nuevaclave
│       ├── listar_claves_handler.py
│       ├── eliminar_clave_handler.py
│       └── error_handler.py    # Manejo global de errores del bot
│
├── domain/                     # CAPA DE DOMINIO (Núcleo del negocio)
│   ├── __init__.py
│   ├── entities/               # Entidades de negocio
│   │   ├── __init__.py
│   │   ├── user.py             # class User:
│   │   └── vpn_key.py          # class VpnKey:
│   └── interfaces/             # Interfaces abstractas (ABSTRACCIONES)
│       ├── __init__.py
│       ├── ivpn_service.py     # Ej: class IVpnService(ABC):
│       ├── iuser_repository.py # class IUserRepository(ABC):
│       └── ikey_repository.py  # class IKeyRepository(ABC):
│
├── application/                # CAPA DE APLICACIÓN (Casos de uso)
│   ├── __init__.py
│   ├── services/               # Implementaciones de casos de uso
│   │   ├── __init__.py
│   │   ├── vpn_orchestrator.py # Orquesta Outline/WireGuard
│   │   ├── user_service.py     # Lógica de usuarios
│   │   └── common/             # FUNCIONES COMUNES PARA SERVICIOS
│   │       ├── __init__.py
│   │       ├── key_generator.py # Lógica genérica de creación de claves
│   │       ├── quota_manager.py # Gestión de límites de datos
│   │       └── formatters.py   # Formateo de respuestas
│   └── ports/                  # Interfaces de salida (puertos)
│       ├── __init__.py
│       ├── outline_manager.py  # Adaptador que usa outline-vpn-api
│       └── wireguard_manager.py # Adaptador que usa wireguard-tools
│
├── infrastructure/             # CAPA DE INFRAESTRUCTURA (Detalles externos)
│   ├── __init__.py
│   ├── persistence/            # Persistencia (Supabase/PostgreSQL)
│   │   ├── __init__.py
│   │   └── supabase/           # Implementación concreta para Supabase
│   │       ├── __init__.py
│   │       ├── supabase_client.py # Cliente configurado de Supabase
│   │       ├── user_repository.py # Implementa IUserRepository
│   │       ├── key_repository.py  # Implementa IKeyRepository
│   │       └── models/          # Modelos de datos específicos de Supabase
│   │           ├── __init__.py
│   │           ├── supabase_user.py
│   │           └── supabase_vpnkey.py
│   └── api_clients/            # Clientes HTTP/low-level
│       ├── __init__.py
│       ├── outline_client.py   # Llama directamente a la API de Outline
│       └── wireguard_client.py # Ejecuta comandos wg
│
└── utils/                      # Utilidades técnicas transversales
    ├── __init__.py
    ├── logger_setup.py         # Configuración estructurada de logging
    ├── security.py             # Funciones de hashing, validación, JWT
    ├── decorators.py           # Ej: @retry, @time_execution
    └── exceptions.py           # Excepciones personalizadas del dominio
```

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

