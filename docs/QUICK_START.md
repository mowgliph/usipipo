# 🚀 Inicio Rápido - uSipipo VPN Manager

> **Configura tu propio servidor VPN en 5 minutos**  
*Guía rápida para usuarios impacientes*

## 🎯 Resumen Express

Este tutorial te permitirá tener un servidor VPN completamente funcional con:

- ✅ **Bot de Telegram** para gestión automática
- ✅ **WireGuard + Outline** protocolos disponibles
- ✅ **Panel de administración** integrado
- ✅ **Sistema de usuarios** automático
- ✅ **Configuración SSL** incluida

---

## ⚡ Instalación Ultra-Rápida

### 1️⃣ **Preparación (1 minuto)**

```bash
# Clonar y entrar al directorio
git clone https://github.com/tu-usuario/usipipo.git
cd usipipo

# Hacer ejecutable el script
chmod +x install.sh
```

### 2️⃣ **Ejecutar Instalador (3 minutos)**

```bash
# Ejecutar instalación automática
./install.sh
```

Selecciona la opción **"1. 📦 Complete Installation"** y presiona Enter.

El script instalará automáticamente:
- 🛡️ WireGuard con configuración
- 🌐 Outline con Docker
- 🔥 Reglas de firewall
- 📁 Archivos de configuración

### 3️⃣ **Configurar Bot (1 minuto)**

#### 🤖 **Crear Bot en Telegram**
1. Abre [@BotFather](https://t.me/BotFather) en Telegram
2. Envía: `/newbot`
3. Sigue las instrucciones:
   ```
   🤖 Bot name: Mi VPN Manager
   🏷️ Username: mi_vpn_bot
   ```
4. **Copia el token** (se ve así: `1234567890:ABCDEF...`)

#### 👤 **Obtener tu ID**
1. Abre [@userinfobot](https://t.me/userinfobot)
2. Envía cualquier mensaje
3. **Copia tu User ID** (número largo)

### 4️⃣ **Configurar Credenciales (30 segundos)**

Edita el archivo `.env`:
```bash
nano .env
```

Reemplaza estos valores:
```bash
# Token del bot (de @BotFather)
TELEGRAM_TOKEN=1234567890:ABCDEFghijklmnopqrstuvwxyz123456789

# Tu ID de usuario (de @userinfobot)
ADMIN_ID=987654321
```

### 5️⃣ **Configurar Base de Datos (2 minutos)**

#### 🌐 **Crear Proyecto Supabase**
1. Ve a [Supabase](https://supabase.com)
2. Sign up y crea nuevo proyecto
3. Copia las credenciales:

```bash
# Reemplaza en .env
SUPABASE_URL=https://abcdefg.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.abcdefg.supabase.co:5432/postgres
```

### 6️⃣ **Iniciar el Sistema (30 segundos)**

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
alembic upgrade head

# Iniciar el bot
python main.py
```

---

## 🎉 ¡Listo para Usar!

### 🤖 **Prueba el Bot**
1. **Busca tu bot** en Telegram
2. **Envía `/start`**
3. **Crea tu primera clave** con "➕ Crear Nueva"
4. **Elige el protocolo** (WireGuard u Outline)
5. **Escanea el QR** o descarga la configuración

### 👑 **Panel de Administración**
Como administrador, verás un botón **"🔧 Admin"** con acceso a:
- 📊 **Estado de servidores**
- 👥 **Gestión de usuarios**
- 🔐 **Control de claves**
- 📈 **Estadísticas detalladas**

---

## 🔧 Verificación Rápida

### ✅ **Checklist de Funcionamiento**

- [ ] **Bot responde** a `/start`
- [ ] **Se crean claves** correctamente
- [ ] **QR codes se generan**
- [ ] **Configuraciones se descargan**
- [ ] **Panel admin funciona**
- [ ] **Protocolos VPN conectan**

### 🧪 **Comandos de Verificación**

```bash
# Verificar estado de WireGuard
sudo wg show

# Verificar contenedor de Outline
docker ps | grep outline

# Verificar logs del bot
tail -f logs/bot.log
```

---

## 🚨 Problemas Comunes (Soluciones Rápidas)

### ❌ **"Bot no responde"**
```bash
# Verificar token
python -c "
from telegram import Bot
from config import settings
bot = Bot(settings.TELEGRAM_TOKEN)
print(bot.get_me())
"
```

### ❌ **"Error de base de datos"**
```bash
# Verificar conexión
python -c "
import psycopg2
from config import settings
conn = psycopg2.connect(settings.DATABASE_URL)
print('✅ BD conectada')
conn.close()
"
```

### ❌ **"VPN no conecta"**
```bash
# Verificar firewall
sudo ufw status

# Verificar puertos
sudo netstat -ulnp | grep -E ':(51820|8080|443)'
```

---

## 🎯 Siguientes Pasos

### 📚 **Para Aprender Más**
- [📋 Instalación Completa](./INSTALL.md) - Guía detallada
- [⚙️ Configuración](./CONFIGURATION.md) - Todas las opciones
- [👑 Administración](./ADMIN.md) - Panel de admin completo

### 🔧 **Para Personalizar**
- [🎨 Branding](./CUSTOMIZATION.md) - Personaliza tu bot
- [🌐 Dominios](./DOMAIN_SETUP.md) - Configura dominios propios
- [📊 Métricas](./MONITORING.md) - Sistema de monitoreo

### 🚀 **Para Escalar**
- [📈 Escalabilidad](./SCALABILITY.md) - Multi-servidor
- [🔒 Seguridad](./SECURITY.md) - Mejores prácticas
- [💰 Pagos](./PAYMENTS.md) - Sistema de monetización

---

## 📞 Ayuda Rápida

### 💬 **Soporte Inmediato**
- **📖 Documentación**: [docs/](../docs/)
- **💬 Discord**: [Servidor de ayuda](https://discord.gg/usipipo)
- **🐛 Issues**: [GitHub Issues](https://github.com/tu-usuario/usipipo/issues)

### 🔍 **Diagnóstico Automático**
```bash
# Script de diagnóstico completo
python -c "
from config import settings
import sys

print('🔍 Diagnóstico de uSipipo')
print('=' * 40)

# Verificar configuración esencial
required = ['TELEGRAM_TOKEN', 'ADMIN_ID', 'DATABASE_URL']
missing = [var for var in required if not getattr(settings, var, None)]

if missing:
    print(f'❌ Variables faltantes: {missing}')
    sys.exit(1)

print('✅ Configuración básica OK')
print(f'🛡️ VPNs: {settings.get_vpn_protocols()}')
print(f'🌍 Entorno: {settings.APP_ENV}')

# Verificar servicios
import subprocess
services = ['wg-quick@wg0', 'docker']

for service in services:
    try:
        subprocess.run(['systemctl', 'is-active', service], 
                      check=True, capture_output=True)
        print(f'✅ {service} activo')
    except:
        print(f'❌ {service} inactivo')
"
```

---

## 🎊 ¡Felicidades!

🎉 **Has configurado tu propio servidor VPN profesional**

### ✅ **Lo que tienes funcionando:**
- 🤖 **Bot de Telegram** completamente operativo
- 🔌 **WireGuard + Outline** configurados
- 👥 **Sistema de usuarios** automático
- 👑 **Panel de administración** completo
- 🔒 **Conexiones seguras** para todos tus usuarios

### 🚀 **Qué puedes hacer ahora:**
1. **Invita a usuarios** a probar tu VPN
2. **Personaliza mensajes** y branding
3. **Configura dominios** personalizados
4. **Monitorea el rendimiento** regularmente
5. **Considera planes VIP** para monetizar

---

<div align="center">

**🚀 uSipipo VPN Manager está listo para producción**  
*Tu servidor VPN profesional en menos de 5 minutos*

[📖 Documentación Completa](../docs/) • [🎮 Probar el Bot](https://t.me/tu_bot) • [💬 Soporte](https://discord.gg/usipipo)

Made with ❤️ by uSipipo Team

</div>
