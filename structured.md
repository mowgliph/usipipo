// Estructura de uSipipo

usipipo-vpn-bot/
├── index.js                          # Punto de entrada minimalista
├── .env                              # Variables de entorno
├── package.json
├── config/
│   ├── environment.js                # Validación y carga de configuración
│   └── constants.js                  # Constantes globales
├── middleware/
│   └── auth.middleware.js            # Middleware de autenticación
├── handlers/
│   ├── auth.handler.js               # Manejadores de autenticación/usuarios
│   ├── vpn.handler.js                # Manejadores de VPN (WireGuard/Outline)
│   └── info.handler.js               # Manejadores informativos
├── services/
│   ├── wireguard.service.js          # Lógica de WireGuard
│   ├── outline.service.js            # Lógica de Outline
│   └── notification.service.js       # Sistema de notificaciones
├── utils/
│   ├── messages.js                   # Templates de mensajes
│   ├── keyboards.js                  # Teclados inline reutilizables
│   └── formatters.js                 # Funciones de formato
└── bot/
    └── bot.instance.js               # Instancia del bot configurada
    

// Estructura en modo de arbol
.
├── bot
│   ├── bot
│   │   └── bot.instance.js
│   ├── config
│   │   ├── constants.js
│   │   └── environment.js
│   ├── handlers
│   │   ├── auth.handler.js
│   │   ├── info.handler.js
│   │   └── vpn.handler.js
│   ├── index.js
│   ├── middleware
│   │   └── auth.middleware.js
│   ├── services
│   │   ├── notification.service.js
│   │   ├── outline.service.js
│   │   └── wireguard.service.js
│   └── utils
│       ├── configManager.js
│       ├── formatters.js
│       ├── keyboards.js
│       └── messages.js
├── docker-compose.yml
├── docker.sh
├── example.env
├── example.txt
├── LICENCE
├── package.json
├── README.md
└── structured.md
