# 📋 Guía de Instalación Completa - uSipipo VPN Manager

> **Guía paso a paso para desplegar uSipipo en tu propio servidor VPS**  
> Tiempo estimado: **15-20 minutos**

## 🎯 Resumen de Instalación

Esta guía te llevará a través del proceso completo de instalación de uSipipo VPN Manager:

1. **📋 Preparación del Servidor** - Configuración inicial del VPS
2. **🔧 Instalación Automática** - Script que configura todo automáticamente
3. **⚙️ Configuración Manual** - Ajustes finos y personalización
4. **🤖 Configuración del Bot** - Telegram Bot setup
5. **🗄️ Base de Datos** - Supabase configuration
6. **🚀 Puesta en Marcha** - Iniciar el sistema

---

## 📋 1. Preparación del Servidor

### 🖥️ **Requisitos Mínimos**
- **VPS**: Ubuntu 20.04+ o Debian 11+
- **CPU**: 1 vCPU (2 recomendado)
- **RAM**: 2GB (4GB recomendado)
- **Almacenamiento**: 20GB SSD (40GB recomendado)
- **Red**: IPv4 pública + IPv6 (opcional)

### 🔐 **Configuración Inicial**
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Crear usuario no-root (recomendado)
sudo adduser usipipo
sudo usermod -aG sudo usipipo

# Cambiar al nuevo usuario
su - usipipo
```

### 📦 **Instalar Dependencias Base**
```bash
# Herramientas esenciales
sudo apt install -y curl wget git unzip htop nano

# Python 3.9+ (si no está instalado)
sudo apt install -y python3 python3-pip python3-venv

# Docker (para Outline)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 🔥 **Configurar Firewall**
```bash
# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir WireGuard
sudo ufw allow 51820/udp

# Activar firewall
sudo ufw --force enable
```

---

## 🔧 2. Instalación Automática

### 📥 **Clonar Repositorio**
```bash
# Clonar el proyecto
git clone https://github.com/tu-usuario/usipipo.git
cd usipipo

# Hacer ejecutable el script de instalación
chmod +x install.sh
```

### 🚀 **Ejecutar Instalador**
```bash
# Ejecutar instalación interactiva
./install.sh
```

El instalador te guiará a través de:

#### 📋 **Menú Principal**
```
🛡️ uSipipo VPN Manager - Installation Menu
═══════════════════════════════════════════════════════════════════════════════
1. 📦 Complete Installation (Recommended)
2. 🔧 Install WireGuard Only
3. 🌐 Install Outline Only
4. 📊 Show Installation Status
5. 🗑️  Uninstall Services
6. 📋 View Logs
7. ❌ Exit
```

#### ✅ **Qué Instala el Script**
- **WireGuard**: Configuración completa con claves automáticas
- **Outline**: Docker container con Shadowbox
- **Firewall**: Reglas automáticas para VPN
- **Systemd Services**: Servicios auto-iniciables
- **Environment File**: `.env` con toda la configuración

### 📝 **Archivo de Configuración**
El instalador creará un archivo `.env` con esta estructura:

```bash
# =============================================================================
# uSipipo VPN Manager - Environment Configuration
# =============================================================================

# Telegram Bot Configuration
TELEGRAM_TOKEN=TU_TELEGRAM_BOT_TOKEN_AQUI
ADMIN_ID=TU_ID_DE_TELEGRAM

# Server Network Information
SERVER_IPV4=TU_IPV4_PUBLICA
SERVER_IPV6=TU_IPV6_PUBLICA
SERVER_IP=TU_IP_PUBLICA

# WireGuard Configuration
WG_INTERFACE=wg0
WG_SERVER_IPV4=10.88.88.1
WG_SERVER_IPV6=fd42:42:42::1
WG_SERVER_PORT=51820
WG_SERVER_PUBKEY=TU_CLAVE_PUBLICA_WG
WG_SERVER_PRIVKEY=TU_CLAVE_PRIVADA_WG

# Outline Configuration
OUTLINE_API_URL=https://tu-ip:8080/YOUR_SECRET_KEY
OUTLINE_CERT_SHA256=TU_CERT_SHA256
OUTLINE_API_PORT=8080
OUTLINE_KEYS_PORT=443

# FastAPI Backend
SECRET_KEY=TU_SECRET_KEY_AQUI
API_HOST=0.0.0.0
API_PORT=8000

# Database Configuration
SUPABASE_URL=TU_URL_SUPABASE
SUPABASE_SERVICE_KEY=TU_SERVICE_KEY
DATABASE_URL=tu_url_postgresql
```

---

## ⚙️ 3. Configuración Manual

### 🔑 **Generar Claves Adicionales**
```bash
# Generar SECRET_KEY para FastAPI
openssl rand -hex 32

# Generar claves JWT (opcional)
openssl rand -base64 32
```

### 🌐 **Configurar Dominio (Opcional)**
```bash
# Si tienes un dominio, configura DNS:
# A record: vpn.tudominio.com -> TU_IP_PUBLICA
# AAAA record: vpn.tudominio.com -> TU_IPV6_PUBLICA
```

### 📧 **Configurar Email (Opcional)**
```bash
# Para notificaciones automáticas
ADMIN_EMAIL=tu@email.com
```

---

## 🤖 4. Configuración del Bot de Telegram

### 📱 **Crear Bot en Telegram**
1. **Abre @BotFather** en Telegram
2. **Envía**: `/newbot`
3. **Sigue las instrucciones**:
   ```
   🤖 Bot name: uSipipo VPN Manager
   🏷️ Username: usipipo_vpn_bot
   ```
4. **Copia el token** (se ve así: `1234567890:ABCDEF...`)

### 👤 **Obtener tu ID de Usuario**
1. **Abre @userinfobot** en Telegram
2. **Envía cualquier mensaje**
3. **Copia tu User ID** (número largo)

### 🔧 **Configurar Bot**
Edita tu archivo `.env`:
```bash
# Reemplaza con tus valores reales
TELEGRAM_TOKEN=1234567890:ABCDEFghijklmnopqrstuvwxyz123456789
ADMIN_ID=987654321
```

---

## 🗄️ 5. Configuración de Base de Datos

### 🌐 **Crear Proyecto Supabase**
1. **Ve a [Supabase](https://supabase.com)**
2. **Sign up / Sign in**
3. **Crea nuevo proyecto**:
   - **Nombre**: `usipipo-vpn`
   - **Región**: La más cercana a tu servidor
   - **Password**: Genera una contraseña segura

### 📋 **Obtener Credenciales**
En tu dashboard de Supabase:

#### 🔑 **API Keys**
```
Project URL: https://abcdefg.supabase.co
Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Service Role Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
JWT Secret: tu-jwt-secret-aqui
```

#### 🗄️ **Database URL**
```
postgresql://postgres:[PASSWORD]@db.abcdefg.supabase.co:5432/postgres
```

### ⚙️ **Configurar en .env**
```bash
# Supabase Configuration
SUPABASE_URL=https://abcdefg.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=tu-jwt-secret-aqui
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.abcdefg.supabase.co:5432/postgres
```

---

## 🚀 6. Puesta en Marcha

### 🐍 **Instalar Dependencias Python**
```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### 🗄️ **Ejecutar Migraciones**
```bash
# Instalar Alembic si no está
pip install alembic

# Ejecutar migraciones
alembic upgrade head
```

### 🤖 **Iniciar el Bot**
```bash
# Iniciar el bot principal
python main.py
```

Deberías ver:
```
🚀 Iniciando uSipipo VPN Manager Bot...
✅ Contenedor de dependencias configurado correctamente.
✅ Configuración cargada correctamente
📦 Proyecto: uSipipo VPN Manager
🌍 Entorno: production
🛡️ Protocolos VPN disponibles: wireguard, outline
🔒 Modo PRODUCCIÓN activado
⏰ Job de limpieza de tickets programado (cada 1h).
⏰ Job de cuota programado.
⏰ Job de limpieza de llaves programado.
🤖 Bot en línea y escuchando mensajes...
```

### 🔄 **Crear Servicio Systemd (Opcional)**
Para que el bot se inicie automáticamente:
```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/usipipo-bot.service
```

Contenido:
```ini
[Unit]
Description=uSipipo VPN Manager Bot
After=network.target

[Service]
Type=simple
User=usipipo
WorkingDirectory=/home/usipipo/usipipo
Environment=PATH=/home/usipipo/usipipo/venv/bin
ExecStart=/home/usipipo/usipipo/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable usipipo-bot
sudo systemctl start usipipo-bot

# Verificar estado
sudo systemctl status usipipo-bot
```

---

## ✅ Verificación Final

### 🧪 **Probar Funcionalidades**

#### 🤖 **Bot de Telegram**
1. **Envía `/start`** a tu bot
2. **Verifica menú principal** aparece correctamente
3. **Crea una clave** de prueba
4. **Verifica configuración** generada

#### 🔌 **Protocolos VPN**
```bash
# Verificar WireGuard
sudo wg show

# Verificar Outline
curl -k https://localhost:8080/server/status
```

#### 🗄️ **Base de Datos**
```bash
# Verificar conexión
python -c "
from config import settings
print('✅ Conexión a BD exitosa' if settings.DATABASE_URL else '❌ Error de conexión')
"
```

### 📊 **Panel de Administración**
1. **Envía `/start`** al bot como admin
2. **Busca botón "🔧 Admin"** (solo visible para ADMIN_ID)
3. **Explora opciones** de administración
4. **Verifica monitoreo** de servidores

---

## 🔧 Solución de Problemas

### 🐛 **Problemas Comunes**

#### ❌ **Bot no responde**
```bash
# Verificar token
python -c "
from telegram import Bot
from config import settings
bot = Bot(settings.TELEGRAM_TOKEN)
print(bot.get_me())
"
```

#### 🔌 **WireGuard no funciona**
```bash
# Verificar estado
sudo wg show

# Reiniciar servicio
sudo systemctl restart wg-quick@wg0

# Verificar logs
sudo journalctl -u wg-quick@wg0 -f
```

#### 🌐 **Outline no funciona**
```bash
# Verificar contenedor
docker ps | grep outline

# Verificar logs
docker logs outline

# Reiniciar contenedor
docker restart outline
```

#### 🗄️ **Error de Base de Datos**
```bash
# Verificar conexión
python -c "
import psycopg2
from config import settings
conn = psycopg2.connect(settings.DATABASE_URL)
print('✅ Conexión exitosa')
conn.close()
"
```

### 📞 **Obtener Ayuda**
- **📖 Documentación**: [docs/](../docs/)
- **🐛 Issues**: [GitHub Issues](https://github.com/tu-usuario/usipipo/issues)
- **💬 Discord**: [Servidor de soporte](https://discord.gg/tu-invite)

---

## 🎉 ¡Felicidades!

🎊 **Has instalado exitosamente uSipipo VPN Manager**

### ✅ **Qué tienes funcionando:**
- 🤖 **Bot de Telegram** completamente funcional
- 🔌 **WireGuard + Outline** configurados
- 🗄️ **Base de datos** conectada
- 👑 **Panel de administración** operativo
- 🔄 **Sistema automático** de mantenimiento

### 🚀 **Próximos Pasos:**
1. **Personaliza tu bot** con mensajes y branding
2. **Configura dominios** personalizados si lo deseas
3. **Invita usuarios** a probar el sistema
4. **Monitorea el rendimiento** regularmente
5. **Considera backup** automático de configuraciones

---

<div align="center">

**🛡️ uSipipo VPN Manager está listo para usar**  
*Tu sistema de gestión VPN profesional con Telegram*

[📖 Documentación Completa](../docs/) • [🎮 Probar el Bot](https://t.me/tu_bot) • [💬 Soporte](https://discord.gg/tu-invite)

Made with ❤️ by the uSipipo Team

</div>
