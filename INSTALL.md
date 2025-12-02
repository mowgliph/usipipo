# 📋 Guía de Instalación - uSipipo VPN Bot

**Sistema integrado de gestión de VPN con Telegram Bot**

Esta guía te llevará paso a paso desde un servidor limpio hasta tener el bot completamente funcional.

---

## 📑 Tabla de Contenidos

1. [Requisitos Previos](#-requisitos-previos)
2. [Preparación del Servidor](#-preparación-del-servidor)
3. [Instalación de Docker](#-instalación-de-docker)
4. [Configuración de Servicios VPN](#-configuración-de-servicios-vpn)
5. [Instalación del Bot de Telegram](#-instalación-del-bot-de-telegram)
6. [Configuración de Variables de Entorno](#-configuración-de-variables-de-entorno)
7. [Despliegue con PM2](#-despliegue-con-pm2)
8. [Verificación y Pruebas](#-verificación-y-pruebas)
9. [Mantenimiento y Troubleshooting](#-mantenimiento-y-troubleshooting)

---

## 🔧 Requisitos Previos

**Hardware mínimo recomendado:**

- VPS/Servidor con Ubuntu 22.04 LTS
- 2 GB de RAM (4 GB recomendado)
- 20 GB de almacenamiento
- 1 CPU core (2+ recomendado)
- Dirección IP pública estática

**Software necesario:**

- Acceso root o sudo al servidor
- Conexión SSH configurada
- Puertos disponibles: 51820 (WireGuard), API Outline (aleatorio), Pi-hole Web (aleatorio)

**Servicios externos:**

- Cuenta de Telegram
- Bot de Telegram creado vía [@BotFather](https://t.me/BotFather)

---

## 🖥️ Preparación del Servidor

### Paso 1: Actualizar el sistema

Conecta a tu servidor vía SSH y ejecuta:

```bash
sudo apt update && sudo apt upgrade -y
```

### Paso 2: Instalar dependencias básicas

```bash
sudo apt install -y curl git wget nano ufw
```

### Paso 3: Configurar firewall básico

```bash
# Permitir SSH
sudo ufw allow 22/tcp

# Permitir WireGuard (el puerto se configurará dinámicamente)
sudo ufw allow 51820/udp

# Habilitar firewall
sudo ufw --force enable

# Verificar estado
sudo ufw status
```

---

## 🐳 Instalación de Docker

### Opción A: Usando el script automatizado

El proyecto incluye un script que instala Docker automáticamente:

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/usipipo-vpn-bot.git
cd usipipo-vpn-bot

# Dar permisos de ejecución
chmod +x docker.sh

# Ejecutar instalación de Docker
./docker.sh
# Selecciona la opción 1 del menú
```

### Opción B: Instalación manual de Docker

Si prefieres hacerlo manualmente:

```bash
# Eliminar versiones antiguas
sudo apt remove docker docker-engine docker.io containerd runc

# Instalar dependencias
sudo apt install -y ca-certificates curl gnupg lsb-release

# Agregar clave GPG oficial de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Configurar repositorio
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Agregar usuario actual al grupo docker
sudo usermod -aG docker $USER

# Aplicar cambios de grupo (o reiniciar sesión SSH)
newgrp docker

# Verificar instalación
docker --version
docker compose version
```

---

## 🔐 Configuración de Servicios VPN

### Paso 1: Preparar directorio del proyecto

Si aún no has clonado el repositorio:

```bash
cd ~
git clone https://github.com/tu-usuario/usipipo-vpn-bot.git
cd usipipo-vpn-bot
```

### Paso 2: Iniciar servicios Docker

Ejecuta el script de instalación:

```bash
./docker.sh
# Selecciona la opción 2: "Start VPN Services"
```

El script realizará automáticamente:

- Detección de tu IP pública
- Generación de certificados SSL para Outline
- Creación de configuración WireGuard
- Configuración de Pi-hole con DNS personalizado
- Asignación de puertos aleatorios para seguridad

**Salida esperada:**

Al finalizar, verás algo similar a:

```
═══════════════════════════════════════════════════════════════════════════════
              🎉 INSTALLATION COMPLETED SUCCESSFULLY! 🎉
═══════════════════════════════════════════════════════════════════════════════

📋 SERVICE CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════
🌐 PI-HOLE (Ad Blocking)
   ├─ Web Interface: http://123.45.67.89:12345/admin
   └─ Password: abc123xyz456

🔒 WIREGUARD VPN
   ├─ Endpoint: 123.45.67.89:51820
   └─ Public Key: ABCDEFGHabcdefgh1234567890...

🚀 OUTLINE VPN
   └─ Manager Config: {"apiUrl":"https://123.45.67.89:54321/SECRET123","certSha256":"ABC123..."}
```

**Importante:** Guarda toda esta información, la necesitarás para el archivo `.env` del bot.

### Paso 3: Extraer clave pública de WireGuard

```bash
docker exec wireguard cat /config/server/publickey
```

Copia esta clave, la necesitarás en el siguiente paso.

---

## 🤖 Instalación del Bot de Telegram

### Paso 1: Crear Bot en Telegram

1. Abre Telegram y busca [@BotFather](https://t.me/BotFather)
2. Envía el comando `/newbot`
3. Sigue las instrucciones para asignar nombre y username
4. **Guarda el token** que te proporciona (formato: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Paso 2: Obtener tu ID de Telegram

1. Busca el bot [@userinfobot](https://t.me/userinfobot) en Telegram
2. Envía `/start`
3. **Guarda tu ID** (formato numérico: `123456789`)

### Paso 3: Instalar Node.js 18+

```bash
# Instalar Node.js usando NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verificar instalación
node --version  # Debe ser v18.x o superior
npm --version
```

### Paso 4: Instalar dependencias del bot

```bash
cd ~/usipipo-vpn-bot/bot
npm install
```

Esto instalará las dependencias definidas en `package.json`:

- `telegraf`: Framework para bots de Telegram
- `axios`: Cliente HTTP para llamadas API
- `dotenv`: Gestión de variables de entorno
- `uuid`: Generación de identificadores únicos

---

## ⚙️ Configuración de Variables de Entorno

### Paso 1: Crear archivo .env

Desde el directorio raíz del proyecto:

```bash
cd ~/usipipo-vpn-bot
cp example.env .env
nano .env
```

### Paso 2: Completar configuración

Edita el archivo `.env` con los valores obtenidos anteriormente:

```bash
# ========== TELEGRAM BOT ==========
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
AUTHORIZED_USERS=123456789  # Tu ID de Telegram (primer usuario será admin)

# ========== SERVER CONFIGURATION ==========
SERVER_IPV4=123.45.67.89  # Tu IP pública del servidor
SERVER_IPV6=  # Opcional, dejar vacío si no tienes IPv6
SERVER_IP=123.45.67.89  # Misma que SERVER_IPV4

# ========== PI-HOLE ==========
PIHOLE_WEB_PORT=12345  # Puerto mostrado en el script de instalación
PIHOLE_WEBPASS=abc123xyz456  # Password generado automáticamente
PIHOLE_DNS=123.45.67.89  # Usar SERVER_IPV4

# ========== WIREGUARD ==========
WIREGUARD_PORT=51820  # Puerto mostrado en el script
WIREGUARD_SERVER_PUBLIC_KEY=ABCDEFGHabcdefgh1234567890...  # Clave extraída anteriormente
WIREGUARD_ENDPOINT=123.45.67.89:51820  # IP:Puerto
WIREGUARD_PATH=/config/wg0.conf  # Ruta por defecto

# ========== OUTLINE ==========
OUTLINE_API_URL=https://123.45.67.89:54321/SECRET123  # URL del Manager Config
OUTLINE_API_SECRET=SECRET123  # Parte final de la URL
OUTLINE_API_PORT=54321  # Puerto mostrado en el script

# ========== GENERAL ==========
PRESERVE_CERTS=true  # Mantener certificados SSL entre reinicios
```

**Ejemplo completo:**

```bash
TELEGRAM_TOKEN=7234567890:AAHdF4G5hJ9kL2mNoPqR6sTuVwXyZ0123AB
AUTHORIZED_USERS=987654321

SERVER_IPV4=203.0.113.45
SERVER_IPV6=
SERVER_IP=203.0.113.45

PIHOLE_WEB_PORT=45678
PIHOLE_WEBPASS=Xy9kL2mN
PIHOLE_DNS=203.0.113.45

WIREGUARD_PORT=51820
WIREGUARD_SERVER_PUBLIC_KEY=8Lq3Nh5TpU7vW9xY0zA1bC2dE3fG4hI5jK6lM7nO8pQ=
WIREGUARD_ENDPOINT=203.0.113.45:51820
WIREGUARD_PATH=/config/wg0.conf

OUTLINE_API_URL=https://203.0.113.45:34567/ABcDef1234
OUTLINE_API_SECRET=ABcDef1234
OUTLINE_API_PORT=34567

PRESERVE_CERTS=true
```

### Paso 3: Validar sintaxis

```bash
# Verificar que no haya errores de sintaxis
node -e "require('dotenv').config(); console.log('✅ .env válido')"
```

---

## 🚀 Despliegue con PM2

PM2 es un gestor de procesos que mantiene el bot ejecutándose permanentemente, incluso después de reinicios del servidor.

### Paso 1: Instalar PM2 globalmente

```bash
sudo npm install -g pm2
```

### Paso 2: Crear archivo de configuración PM2

Desde el directorio raíz del proyecto:

```bash
nano ecosystem.config.js
```

Pega el siguiente contenido:

```javascript
module.exports = {
  apps: [{
    name: 'usipipo-vpn-bot',
    script: './bot/index.js',
    cwd: '/root/usipipo-vpn-bot',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    time: true
  }]
};
```

**Ajustar ruta si es necesario:** Cambia `/root/usipipo-vpn-bot` por la ruta real donde clonaste el repositorio.

### Paso 3: Crear directorio de logs

```bash
mkdir -p ~/usipipo-vpn-bot/logs
```

### Paso 4: Iniciar el bot con PM2

```bash
cd ~/usipipo-vpn-bot
pm2 start ecosystem.config.js
```

### Paso 5: Configurar PM2 para inicio automático

```bash
# Guardar configuración actual
pm2 save

# Generar script de inicio automático
pm2 startup systemd

# Ejecutar el comando que PM2 te muestre (será similar a):
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u $USER --hp $HOME
```

### Paso 6: Comandos útiles de PM2

```bash
# Ver estado del bot
pm2 status

# Ver logs en tiempo real
pm2 logs usipipo-vpn-bot

# Ver logs de errores únicamente
pm2 logs usipipo-vpn-bot --err

# Reiniciar el bot
pm2 restart usipipo-vpn-bot

# Detener el bot
pm2 stop usipipo-vpn-bot

# Eliminar del PM2 (no elimina archivos)
pm2 delete usipipo-vpn-bot

# Monitorear recursos
pm2 monit
```

---

## ✅ Verificación y Pruebas

### Paso 1: Verificar que el bot está ejecutándose

```bash
pm2 status
```

Deberías ver algo como:

```
┌─────┬────────────────────┬─────────┬─────────┬─────────┬──────────┐
│ id  │ name               │ mode    │ ↺       │ status  │ cpu      │
├─────┼────────────────────┼─────────┼─────────┼─────────┼──────────┤
│ 0   │ usipipo-vpn-bot    │ fork    │ 0       │ online  │ 0%       │
└─────┴────────────────────┴─────────┴─────────┴─────────┴──────────┘
```

### Paso 2: Verificar logs del bot

```bash
pm2 logs usipipo-vpn-bot --lines 50
```

Deberías ver:

```
🚀 uSipipo VPN Bot iniciado exitosamente
📡 Admin ID: 987654321
👥 Usuarios autorizados: 1
🌍 Servidor: 203.0.113.45:51820
```

### Paso 3: Probar el bot en Telegram

1. Abre Telegram y busca tu bot por su username (ejemplo: `@usipipo_vpn_bot`)
2. Envía el comando `/start`
3. Deberías recibir el menú principal con opciones:
   - 🔐 Crear WireGuard
   - 🌐 Crear Outline
   - 📊 Ver Clientes Activos
   - ℹ️ Estado del Servidor
   - ❓ Ayuda

### Paso 4: Verificar servicios Docker

```bash
docker compose ps
```

Deberías ver todos los contenedores en estado `Up`:

```
NAME                IMAGE                              STATUS
outline             quay.io/outline/shadowbox:stable   Up 5 minutes
pihole              pihole/pihole:latest               Up 5 minutes (healthy)
wireguard           linuxserver/wireguard:latest       Up 5 minutes
```

### Paso 5: Probar creación de configuración VPN

Desde el bot de Telegram:

1. Toca **"🔐 Crear WireGuard"**
2. Deberías recibir:
   - Archivo `.conf` descargable
   - Código QR para escanear
   - Instrucciones de conexión

3. Toca **"🌐 Crear Outline"**
4. Deberías recibir:
   - Enlace de acceso (`ss://...`)
   - Instrucciones de instalación

---

## 🛠️ Mantenimiento y Troubleshooting

### Comandos de diagnóstico

**Ver estado general del sistema:**

```bash
# Estado de servicios Docker
docker compose ps

# Estado del bot
pm2 status

# Logs de Docker (últimas 100 líneas)
docker compose logs --tail=100

# Logs del bot (últimas 100 líneas)
pm2 logs usipipo-vpn-bot --lines 100
```

### Problemas comunes

#### 🔴 El bot no responde en Telegram

**Diagnóstico:**

```bash
pm2 logs usipipo-vpn-bot --err
```

**Soluciones:**

1. Verificar que el token sea correcto en `.env`
2. Verificar conexión a internet del servidor:
   ```bash
   curl -I https://api.telegram.org
   ```
3. Reiniciar el bot:
   ```bash
   pm2 restart usipipo-vpn-bot
   ```

#### 🔴 Error: "WIREGUARD_SERVER_PUBLIC_KEY not found"

**Solución:**

```bash
# Extraer la clave correcta
docker exec wireguard cat /config/server/publickey

# Agregar al .env
nano ~/usipipo-vpn-bot/.env
# Pegar la clave en WIREGUARD_SERVER_PUBLIC_KEY=...

# Reiniciar bot
pm2 restart usipipo-vpn-bot
```

#### 🔴 Error: "Outline API connection failed"

**Diagnóstico:**

```bash
docker logs outline --tail 50
```

**Soluciones:**

1. Verificar que el contenedor Outline esté corriendo:
   ```bash
   docker compose restart outline
   ```

2. Regenerar certificados SSL:
   ```bash
   # Editar .env y cambiar PRESERVE_CERTS a false
   nano .env
   # PRESERVE_CERTS=false

   # Reiniciar servicios
   ./docker.sh
   # Opción 4: Stop Services
   # Opción 2: Start Services
   ```

3. Verificar conectividad al API:
   ```bash
   curl -k https://localhost:${OUTLINE_API_PORT}
   ```

#### 🔴 WireGuard no genera configuraciones

**Diagnóstico:**

```bash
docker exec wireguard wg show
```

**Soluciones:**

1. Verificar permisos del contenedor:
   ```bash
   docker compose restart wireguard
   ```

2. Verificar espacio disponible de IPs:
   ```bash
   docker exec wireguard cat /config/wg0.conf | grep AllowedIPs
   ```

### Actualizar el bot

```bash
cd ~/usipipo-vpn-bot

# Guardar cambios locales (si los hay)
cp .env .env.backup

# Descargar última versión
git pull origin main

# Restaurar configuración
cp .env.backup .env

# Reinstalar dependencias
cd bot
npm install

# Reiniciar con PM2
pm2 restart usipipo-vpn-bot
```

### Backup de configuración

**Crear backup:**

```bash
# Crear directorio de backups
mkdir -p ~/backups

# Backup de configuración
tar -czf ~/backups/usipipo-backup-$(date +%Y%m%d).tar.gz \
  ~/usipipo-vpn-bot/.env \
  ~/usipipo-vpn-bot/bot/data/authorized_users.json \
  ~/usipipo-vpn-bot/docker-compose.yml

# Listar backups
ls -lh ~/backups/
```

**Restaurar backup:**

```bash
# Detener servicios
pm2 stop usipipo-vpn-bot
docker compose down

# Extraer backup
tar -xzf ~/backups/usipipo-backup-YYYYMMDD.tar.gz -C ~/

# Reiniciar servicios
docker compose up -d
pm2 restart usipipo-vpn-bot
```

### Monitoreo de recursos

```bash
# Uso de CPU y RAM por contenedor
docker stats

# Uso de disco
df -h

# Procesos del sistema
htop  # Si no está instalado: sudo apt install htop
```

### Logs importantes

**Ubicaciones de logs:**

```bash
# Logs del bot (PM2)
~/usipipo-vpn-bot/logs/pm2-out.log
~/usipipo-vpn-bot/logs/pm2-error.log

# Logs de Docker
docker compose logs -f outline
docker compose logs -f wireguard
docker compose logs -f pihole

# Logs del sistema
/var/log/syslog
```

---

## 📞 Soporte

**Documentación adicional:**

- [Documentación de Telegraf](https://telegrafjs.org/)
- [Documentación de WireGuard](https://www.wireguard.com/)
- [Documentación de Outline](https://getoutline.org/)
- [Documentación de Pi-hole](https://docs.pi-hole.net/)
- [Documentación de PM2](https://pm2.keymetrics.io/)

**Contacto:**

- Email: usipipo@etlgr.com
- Issues: [GitHub Issues](https://github.com/tu-usuario/usipipo-vpn-bot/issues)

---

## ✨ Siguientes Pasos

Una vez que el bot esté funcionando correctamente:

1. **Agregar más usuarios autorizados:**
   - Los usuarios deben enviarte su ID de Telegram (comando `/miinfo` en el bot)
   - Ejecuta `/agregar [ID] [nombre_opcional]` desde tu cuenta de admin

2. **Configurar límites de datos en Outline:**
   - Edita `bot/config/constants.js` para cambiar `OUTLINE_DEFAULT_DATA_LIMIT`

3. **Personalizar mensajes del bot:**
   - Edita `bot/utils/messages.js` para cambiar textos

4. **Monitorear uso:**
   - Usa el comando `/stats` en el bot para ver estadísticas
   - Comando `📊 Ver Clientes Activos` para ver conexiones

5. **Configurar backups automáticos:**
   ```bash
   # Crear script de backup diario
   sudo nano /etc/cron.daily/usipipo-backup
   ```

   Contenido:
   ```bash
   #!/bin/bash
   tar -czf /root/backups/usipipo-backup-$(date +%Y%m%d).tar.gz \
     /root/usipipo-vpn-bot/.env \
     /root/usipipo-vpn-bot/bot/data/authorized_users.json
   
   # Mantener solo últimos 7 backups
   find /root/backups -name "usipipo-backup-*.tar.gz" -mtime +7 -delete
   ```

   Dar permisos:
   ```bash
   sudo chmod +x /etc/cron.daily/usipipo-backup
   ```

---

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

---

**¡Instalación completada!** 🎉

Ahora tienes un sistema VPN completo gestionado desde Telegram con bloqueo de anuncios integrado. Disfruta de tu nueva infraestructura de privacidad.