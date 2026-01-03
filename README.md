# 🛡️ uSipipo VPN Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Telegram Bot](https://img.shields.io/badge/Telegram%20Bot-API-21.6+-blue.svg)](https://python-telegram-bot.org/)

> **Sistema completo de gestión VPN con Telegram Bot, API REST y panel de administración**  
> Soporte multi-protocolo (WireGuard + Outline) con arquitectura limpia y escalable

## 🌟 Características Principales

### 🤖 **Telegram Bot**
- **Panel de usuario intuitivo** con menús interactivos
- **Creación automática** de claves VPN (WireGuard + Outline)
- **Gestión de claves**: listar, eliminar, renovar
- **Sistema de planes**: Gratis y VIP con Telegram Stars
- **Programa de referidos** con comisiones automáticas
- **Soporte integrado** con chat directo al admin
- **Juegos Play & Earn** para ganar estrellas

### 🛠️ **Panel de Administración**
- **Control total** sobre usuarios y claves
- **Eliminación directa** en servidores VPN
- **Monitoreo en tiempo real** de servidores
- **Estadísticas detalladas** de uso
- **Gestión de tickets** de soporte
- **Broadcast masivo** a usuarios

### 🔌 **Protocolos VPN**
- **WireGuard**: Alto rendimiento con configuración automática
- **Outline (Shadowsocks)**: Fácil de usar con clientes multiplataforma
- **Gestión unificada** desde una sola interfaz
- **Rotación automática** de claves expiradas

### 🏗️ **Arquitectura**
- **Clean Architecture** con separación de responsabilidades
- **Inyección de dependencias** con Punq
- **Base de datos PostgreSQL** con Supabase
- **API REST** con FastAPI
- **Logging estructurado** con Loguru
- **Testing automatizado** con pytest

## 📋 Requisitos del Sistema

### 🖥️ **Servidor Requerido**
- **VPS** con Ubuntu 20.04+ o Debian 11+
- **Mínimo**: 1 vCPU, 2GB RAM, 20GB SSD
- **Recomendado**: 2 vCPU, 4GB RAM, 40GB SSD
- **IPv4 pública** (IPv6 opcional)
- **Puertos**: 80, 443, 51820/UDP, 22/SSH

### 🐍 **Software**
- **Python 3.9+**
- **Docker & Docker Compose** (para Outline)
- **PostgreSQL** (via Supabase o local)
- **WireGuard** tools

## 🚀 Instalación Rápida

### 1️⃣ **Clonar Repositorio**
```bash
git clone https://github.com/mowgliph/usipipo.git
cd usipipo
```

### 2️⃣ **Ejecutar Instalador Automático**
```bash
chmod +x install.sh
./install.sh
```

El instalador automáticamente:
- ✅ Instala WireGuard y Outline
- ✅ Configura Docker si es necesario
- ✅ Genera claves y certificados
- ✅ Crea archivo `.env` con toda la configuración
- ✅ Configura firewall y puertos

### 3️⃣ **Configurar Bot de Telegram**
1. Crea un bot con [@BotFather](https://t.me/BotFather)
2. Copia el token del bot
3. Obtén tu ID de usuario con [@userinfobot](https://t.me/userinfobot)
4. Edita `.env` con tus credenciales

### 4️⃣ **Configurar Base de Datos**
1. Crea un proyecto en [Supabase](https://supabase.com)
2. Copia las credenciales al `.env`
3. Ejecuta migraciones con Alembic

### 5️⃣ **Iniciar el Sistema**
```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Ejecutar migraciones de base de datos
alembic upgrade head

# Iniciar el bot
python main.py
```

## 📖 Documentación Detallada

### 📚 **Guías Completas**
- [📋 Instalación Completa](./docs/INSTALL.md) - Guía paso a paso detallada
- [⚙️ Configuración](./docs/CONFIGURATION.md) - Todas las opciones de configuración
- [🔧 Administración](./docs/ADMIN.md) - Guía del panel de administración
- [🤖 Bot Commands](./docs/BOT_COMMANDS.md) - Comandos y funcionalidades del bot
- [🔌 VPN Setup](./docs/VPN_SETUP.md) - Configuración avanzada de VPN
- [🐛 Troubleshooting](./docs/TROUBLESHOOTING.md) - Problemas comunes y soluciones

### 🏗️ **Arquitectura**
- [📐 Clean Architecture](./docs/ARCHITECTURE.md) - Estructura del proyecto
- [🔌 API Documentation](./docs/API.md) - Documentación de la API REST
- [🗄️ Database Schema](./docs/DATABASE.md) - Esquema de base de datos
- [🧪 Testing](./docs/TESTING.md) - Guía de testing

## 🎯 Uso Básico

### 👤 **Para Usuarios**
1. **Inicia el bot** con `/start`
2. **Crea tu primera clave** con "➕ Crear Nueva"
3. **Elige el protocolo** (WireGuard u Outline)
4. **Escanea el QR** o descarga la configuración
5. **Conéctate** y navega de forma segura

### 👑 **Para Administradores**
1. **Accede al panel** con el botón "🔧 Admin"
2. **Gestiona usuarios** desde el panel de administración
3. **Monitorea servidores** en tiempo real
4. **Elimina claves** directamente desde el bot
5. **Envía broadcast** a todos los usuarios

## 🔧 Configuración Principal

### 📝 **Variables de Entorno Esenciales**
```bash
# Telegram Bot
TELEGRAM_TOKEN=tu_token_aqui
ADMIN_ID=tu_id_telegram

# Base de Datos
SUPABASE_URL=tu_url_supabase
SUPABASE_SERVICE_KEY=tu_service_key
DATABASE_URL=tu_url_postgresql

# Servidor
SERVER_IP=tu_ip_publica
SECRET_KEY=tu_clave_secreta
```

### 🌐 **Protocolos VPN**
```bash
# WireGuard
WG_SERVER_PORT=51820
WG_SERVER_IPV4=10.88.88.1

# Outline
OUTLINE_API_PORT=8080
OUTLINE_KEYS_PORT=443
```

## 📊 Características Avanzadas

### 💰 **Sistema de Pagos**
- **Telegram Stars** integrados
- **Planes VIP** con beneficios adicionales
- **Comisiones por referidos** automáticas
- **Balance y transacciones** detalladas

### 🎮 **Gamificación**
- **Juegos Play & Earn** para ganar estrellas
- **Sistema de niveles** y recompensas
- **Torneos y eventos** especiales
- **Ranking de usuarios** activos

### 🔒 **Seguridad**
- **JWT tokens** para autenticación
- **Rate limiting** para prevenir abusos
- **Logging completo** de todas las acciones
- **IP whitelist** opcional para API

### 📈 **Monitoreo**
- **Logs estructurados** con Loguru
- **Métricas en tiempo real** del sistema
- **Alertas automáticas** de errores
- **Dashboard de administración** integrado

## 🤝 Contribuir

¡Contribuciones son bienvenidas! Por favor:

1. **Fork** el repositorio
2. **Crea una rama** (`git checkout -b feature/amazing-feature`)
3. **Commit** tus cambios (`git commit -m 'Add amazing feature'`)
4. **Push** a la rama (`git push origin feature/amazing-feature`)
5. **Abre un Pull Request**

### 📋 **Guías de Contribución**
- [🤝 Contributing Guide](./docs/CONTRIBUTING.md)
- [🔨 Development Setup](./docs/DEVELOPMENT.md)
- [📝 Code Style](./docs/CODE_STYLE.md)

## 📄 Licencia

Este proyecto está licenciado bajo la **MIT License** - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

### 📞 **Obtener Ayuda**
- **📖 Documentación**: [docs/](./docs/)
- **🐛 Issues**: [GitHub Issues](https://github.com/mowgliph/usipipo/issues)
- **💬 Discord**: [Servidor de Discord](https://discord.gg/tu-invite)
- **📧 Email**: support@usipipo.com

### 🔍 **Troubleshooting Común**
- **Bot no responde**: Revisa token y conexión a internet
- **Claves no funcionan**: Verifica configuración de firewall
- **Error de base de datos**: Confirma credenciales de Supabase
- **Problemas de VPN**: Revisa logs del servidor

## 🎉 Agradecimientos

- **[python-telegram-bot](https://python-telegram-bot.org/)** - Framework del bot
- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework API
- **[WireGuard](https://www.wireguard.com/)** - Protocolo VPN
- **[Outline](https://getoutline.org/)** - VPN Manager
- **[Supabase](https://supabase.com/)** - Backend as a Service

---

<div align="center">

**🛡️ uSipipo VPN Manager**  
*Gestión VPN simplificada con el poder de Telegram*

[🌐 Website](https://usipipo.com) • [📖 Docs](./docs/) • [🚀 Getting Started](./docs/INSTALL.md) • [💬 Support](https://discord.gg/tu-invite)

Made with ❤️ by the uSipipo Team

</div>
