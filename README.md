# 🐙 uSipipo

**uSipipo** es una herramienta desarrollada en **Python puro** que funciona como un **bot de Telegram** para gestionar configuraciones de VPN (WireGuard y Outline), proxies MTProto y gestión de proxies Shadowmere directamente desde el mismo VPS donde se aloja el bot.

Este proyecto está diseñado para facilitar la creación de claves de acceso, incluyendo **pruebas gratuitas de 7 días**, y ofrecer configuraciones de VPN de pago mediante **Estrellas de Telegram** y **QvaPay** (criptomonedas).

---

## 🏗️ Arquitectura del Proyecto

uSipipo sigue una arquitectura modular y escalable basada en el patrón **models-crud-services-handlers**:

- **models**: Definición de modelos SQLAlchemy con tipado estático
- **crud**: Operaciones de base de datos (consultas, inserciones, actualizaciones)
- **services**: Lógica de negocio y integración con APIs externas
- **handlers**: Controladores de comandos y callbacks de Telegram

### Estructura de Carpetas
```
usipipo/
├── bot/
│   ├── handlers/          # Controladores de comandos Telegram
│   └── main.py           # Punto de entrada del bot
├── database/
│   ├── models.py         # Modelos SQLAlchemy
│   ├── crud/            # Operaciones de base de datos
│   └── db.py            # Configuración de base de datos
├── services/            # Lógica de negocio
├── routes/              # Registro de handlers
├── utils/               # Utilidades y helpers
├── config/              # Configuraciones del sistema
├── scripts/             # Scripts de instalación y configuración
├── jobs/                # Tareas programadas
├── docs/                # Documentación
└── test/                # Pruebas
```

---

## 🔓 Características principales

- ✅ Generación automática de configuraciones **WireGuard** y **Outline**
- 🎁 Pruebas gratuitas de **7 días**
- 💸 Sistema de pagos con **Estrellas de Telegram**
- 💳 Sistema de pagos con **QvaPay** (criptomonedas)
- 🔄 Gestión de **proxies MTProto** para Telegram
- 🌐 Detección y gestión de **proxies Shadowmere** (SOCKS5, HTTP, HTTPS)
- 🤖 Todo gestionado desde un **bot de Telegram**
- 🛠️ Código modular, mantenible y extensible
- 📊 Sistema de auditoría y logs centralizados
- 🔐 Gestión de roles y permisos
- 📦 Repositorio **Open Source** mantenido por [mowgliph](https://github.com/mowgliph)

---

## 📋 Requisitos del Sistema

- **Python**: 3.11+
- **Base de Datos**: MariaDB/MySQL
- **Sistema Operativo**: Ubuntu 20.04+/Debian 10+ (recomendado)
- **Memoria RAM**: Mínimo 1GB (recomendado 2GB+)
- **Espacio en Disco**: 5GB+ para logs y configuraciones

---

## 🚀 Instalación Rápida

### 1. Clonar el repositorio
```bash
cd /opt
git clone https://github.com/mowgliph/usipipo.git
cd usipipo
```

### 2. Instalar dependencias
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp example.env .env
nano .env
# Configurar TELEGRAM_BOT_TOKEN y DATABASE_URL
```

### 4. Inicializar base de datos
```bash
python scripts/init_db.py
```

### 5. Ejecutar el bot
```bash
python bot/main.py
```

Para instalación completa, consulta [docs/INSTALL.md](docs/INSTALL.md).

---

## 📖 Uso del Bot

### Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `/start` | Iniciar el bot y registro automático |
| `/register` | Registro manual de usuario |
| `/profile` | Ver perfil y configuraciones activas |
| `/vpn` | Gestionar configuraciones VPN |
| `/proxy` | Gestionar proxies MTProto |
| `/status` | Ver estado del sistema |
| `/help` | Mostrar ayuda |

### Ejemplos de Uso

#### Crear VPN Trial
```
/start
# El bot registra automáticamente al usuario
/vpn
# Seleccionar "Crear Trial" -> Elegir tipo (WireGuard/Outline)
# Recibir configuración QR y archivo .conf
```

#### Pago con Estrellas
```
/vpn
# Seleccionar "Comprar Premium" -> Elegir duración
# Pagar con Estrellas de Telegram
# Recibir configuración de pago
```

#### Gestión de Proxies
```
/proxy
# Ver proxies activos
# Crear nuevo proxy MTProto
# Gestionar configuración
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno (.env)
```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
DATABASE_URL=mysql+pymysql://user:pass@localhost/usipipo
LOG_LEVEL=INFO
ADMIN_USER_IDS=123456789,987654321
OUTLINE_API_URL=https://tu-outline-server.com
QVAPAY_APP_ID=tu_app_id
QVAPAY_APP_SECRET=tu_app_secret
```

### Configuración de VPN
- **WireGuard**: Configuración automática de interfaces
- **Outline**: Integración con Outline Manager API
- **MTProto**: Proxies para Telegram con registro automático

### Gestión de IPs
- Sistema automático de asignación de IPs
- Soporte para IPv4 e IPv6
- Gestión de pools por tipo (trial/pago)

---

## 📊 API para Desarrolladores

uSipipo expone una API REST para integraciones externas. Consulta [docs/API.md](docs/API.md) para documentación completa.

### Endpoints Principales
- `GET /api/v1/users` - Lista de usuarios
- `POST /api/v1/vpn/create` - Crear configuración VPN
- `GET /api/v1/proxy/list` - Lista de proxies
- `POST /api/v1/payments/webhook` - Webhook de pagos

---

## 🔒 Seguridad y Mejores Prácticas

- **Logs Centralizados**: Todos los eventos se registran con contexto de usuario
- **Validación de Datos**: Constraints a nivel de base de datos y aplicación
- **Gestión de Permisos**: Sistema de roles para acceso granular
- **Auditoría**: Registro completo de todas las operaciones
- **Rate Limiting**: Protección contra abuso en handlers
- **Secrets Management**: Variables sensibles en archivos .env

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Guías de Desarrollo
- Seguir PEP 8 para estilo de código
- Usar type hints en todas las funciones
- Escribir tests para nuevas funcionalidades
- Actualizar documentación

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/mowgliph/usipipo/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/mowgliph/usipipo/discussions)
- **Email**: mowgliph@github.com

---

**¡Gracias por usar uSipipo!** 🐙

