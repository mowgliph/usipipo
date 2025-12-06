# 📋 Guía de Instalación - uSipipo VPN Bot

**Sistema integrado de gestión de VPN con Telegram Bot**

Esta guía proporciona instrucciones detalladas y secuenciales para la instalación de uSipipo VPN Bot en un servidor Ubuntu 22.04 LTS, desde un entorno limpio hasta un despliegue completamente funcional. Se recomienda seguir cada paso con precisión para garantizar la integridad del sistema.

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

### Hardware Mínimo Recomendado
- Servidor VPS con Ubuntu 22.04 LTS.
- 2 GB de RAM (4 GB recomendado para rendimiento óptimo).
- 20 GB de almacenamiento SSD.
- 1 núcleo de CPU (2 o más recomendado).
- Dirección IP pública estática.

### Software Necesario
- Acceso root o con privilegios sudo al servidor.
- Conexión SSH configurada y segura.
- Puertos disponibles: 51820/UDP (WireGuard), puerto aleatorio para API de Outline, puerto aleatorio para interfaz web de Pi-hole.

### Servicios Externos
- Cuenta de Telegram activa.
- Bot de Telegram creado mediante [@BotFather](https://t.me/BotFather).

---

## 🖥️ Preparación del Servidor

### Paso 1: Actualización del Sistema
Conéctese al servidor mediante SSH y ejecute el siguiente comando para actualizar los paquetes del sistema:

```bash
sudo apt update && sudo apt upgrade -y
```

### Paso 2: Instalación de Dependencias Básicas
Instale las herramientas esenciales requeridas:

```bash
sudo apt install -y curl git wget nano ufw
```

### Paso 3: Configuración del Firewall Básico
Configure reglas iniciales en UFW para seguridad:

```bash
# Permitir acceso SSH
sudo ufw allow 22/tcp

# Permitir tráfico WireGuard
sudo ufw allow 51820/udp

# Habilitar el firewall
sudo ufw --force enable

# Verificar el estado
sudo ufw status
```

---

## 🐳 Instalación de Docker

### Opción A: Script Automatizado
El repositorio incluye un script para la instalación automatizada de Docker. Proceda de la siguiente manera:

```bash
# Clonar el repositorio
git clone https://github.com/mowgliph/usipipo.git
cd usipipo

# Otorgar permisos de ejecución
chmod +x docker.sh

# Ejecutar el script de instalación
./docker.sh
# Seleccione la opción 1 en el menú interactivo.
```

### Opción B: Instalación Manual
Si prefiere una instalación manual, siga estos pasos:

```bash
# Eliminar versiones antiguas de Docker
sudo apt remove docker docker-engine docker.io containerd runc

# Instalar dependencias previas
sudo apt install -y ca-certificates curl gnupg lsb-release

# Agregar clave GPG oficial de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Configurar repositorio oficial
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Actualizar repositorios e instalar Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Agregar el usuario actual al grupo docker
sudo usermod -aG docker $USER

# Aplicar cambios de grupo (o reinicie la sesión SSH)
newgrp docker

# Verificar la instalación
docker --version
docker compose version
```

---

## 🔐 Configuración de Servicios VPN

### Paso 1: Preparación del Directorio del Proyecto
Si no ha clonado el repositorio previamente:

```bash
cd ~
git clone https://github.com/mowgliph/usipipo.git
cd usipipo
```

### Paso 2: Inicio de Servicios Docker
Ejecute el script de instalación para inicializar los servicios:

```bash
./docker.sh
# Seleccione la opción 2: "Start VPN Services".
```

El script automatizará los siguientes procesos:
- Detección de la IP pública del servidor.
- Generación de certificados SSL para Outline.
- Creación de la configuración de WireGuard.
- Configuración de Pi-hole con DNS personalizado.
- Asignación de puertos aleatorios para mayor seguridad.

**Salida Esperada:**
Al finalizar, se mostrará información similar a la siguiente:

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

**Nota Importante:** Registre esta información, ya que será requerida para la configuración del archivo `.env` del bot.

### Paso 3: Extracción de la Clave Pública de WireGuard
Ejecute el siguiente comando para obtener la clave pública del servidor WireGuard:

```bash
docker exec wireguard cat /config/server/publickey
```

Copie esta clave para su uso posterior.

---

## 🤖 Instalación del Bot de Telegram

### Paso 1: Creación del Bot en Telegram
1. Inicie Telegram y contacte a [@BotFather](https://t.me/BotFather).
2. Envía el comando `/newbot`.
3. Siga las instrucciones para asignar un nombre y un nombre de usuario único.
4. **Registre el token proporcionado** (formato: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`).

### Paso 2: Obtención del ID de Usuario de Telegram
1. Contacte al bot [@userinfobot](https://t.me/userinfobot) en Telegram.
2. Envía el comando `/start`.
3. **Registre su ID numérico** (formato: `123456789`).

### Paso 3: Instalación de Node.js 18 o Superior
Instale Node.js mediante el repositorio NodeSource:

```bash
# Configurar repositorio NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# Instalar Node.js
sudo apt install -y nodejs

# Verificar la instalación
node --version  # Debe mostrar v18.x o superior
npm --version
```

### Paso 4: Instalación de Dependencias del Bot
Navegue al directorio del bot e instale las dependencias:

```bash
cd ~/usipipo/bot
npm install
```

Esto instalará las bibliotecas especificadas en `package.json`:
- `telegraf`: Framework para el desarrollo de bots de Telegram.
- `axios`: Cliente HTTP para integraciones con APIs.
- `dotenv`: Gestión de variables de entorno.
- `uuid`: Generación de identificadores únicos.

### Instalación y Configuración del Logger (Winston)
El proyecto utiliza Winston para logging estructurado con rotación diaria y sanitización de datos sensibles.

#### Paso 1: Instalación de Dependencias de Winston
Desde el directorio del bot (`~/usipipo/bot`), ejecute:

```bash
npm install winston winston-daily-rotate-file
```

Esto instala:
- `winston`: Librería principal de logging con soporte para múltiples niveles.
- `winston-daily-rotate-file`: Plugin para rotación automática de logs diarios.

#### Paso 2: Creación del Directorio de Logs
```bash
mkdir -p ~/usipipo/logs
```

#### Paso 3: Configuración del Nivel de Logging (Opcional)
Agregue la siguiente línea al archivo `.env` (se configurará en detalle más adelante):

```
LOG_LEVEL=info  # Opciones disponibles: error, warn, info, http, verbose, debug, silly
```

#### Paso 4: Verificación de Integración
El módulo `utils/logger.js` está preintegrado en el código y se activará automáticamente al reiniciar el bot. Los logs se almacenarán en:

- `~/usipipo/logs/app-YYYY-MM-DD.log`
- `~/usipipo/logs/errors-YYYY-MM-DD.log`

---

## ⚙️ Configuración de Variables de Entorno

### Paso 1: Creación del Archivo `.env`
Desde el directorio raíz del proyecto:

```bash
cd ~/usipipo
cp example.env .env
nano .env
```

### Paso 2: Completar la Configuración
Edite el archivo `.env` con los valores obtenidos en pasos previos:

```
# ========== TELEGRAM BOT ==========
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
AUTHORIZED_USERS=123456789  # ID de Telegram del administrador (primer usuario)

# ========== SERVER CONFIGURATION ==========
SERVER_IPV4=123.45.67.89  # IP pública del servidor
SERVER_IPV6=  # Opcional; deje vacío si no aplica IPv6
SERVER_IP=123.45.67.89  # Igual a SERVER_IPV4

# ========== PI-HOLE ==========
PIHOLE_WEB_PORT=12345  # Puerto asignado durante la instalación
PIHOLE_WEBPASS=abc123xyz456  # Contraseña generada automáticamente
PIHOLE_DNS=123.45.67.89  # Utilice SERVER_IPV4

# ========== WIREGUARD ==========
WIREGUARD_PORT=51820  # Puerto asignado
WIREGUARD_SERVER_PUBLIC_KEY=ABCDEFGHabcdefgh1234567890...  # Clave extraída
WIREGUARD_ENDPOINT=123.45.67.89:51820  # IP:puerto
WIREGUARD_PATH=/config/wg0.conf  # Ruta por defecto

# ========== OUTLINE ==========
OUTLINE_API_URL=https://123.45.67.89:54321/SECRET123  # URL del Manager Config
OUTLINE_API_SECRET=SECRET123  # Secreto de la API (parte final de la URL)
OUTLINE_API_PORT=54321  # Puerto asignado

# ========== GENERAL ==========
PRESERVE_CERTS=true  # Preservar certificados SSL entre reinicios
```

**Ejemplo Completo de `.env`:**

```
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
WIREGUARD_PATH=/config/wg_confs/wg0.conf

OUTLINE_API_URL=https://203.0.113.45:34567/ABcDef1234
OUTLINE_API_SECRET=ABcDef1234
OUTLINE_API_PORT=34567

PRESERVE_CERTS=true
```

### Paso 3: Validación de Sintaxis
Verifique la integridad del archivo `.env`:

```bash
node -e "require('dotenv').config(); console.log('✅ .env válido')"
```

---

## 🚀 Despliegue con PM2

PM2 es un gestor de procesos robusto que asegura la ejecución continua del bot, incluso tras reinicios del servidor.

### Paso 1: Instalación Global de PM2
```bash
sudo npm install -g pm2
```

### Paso 2: Creación del Archivo de Configuración de PM2
Desde el directorio raíz del proyecto:

```bash
nano ecosystem.config.js
```

Inserte el siguiente contenido:

```javascript
module.exports = {
  apps: [{
    name: 'usipipo',
    script: './bot/index.js',
    cwd: '/root/usipipo',
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

**Ajuste de Ruta:** Modifique `/root/usipipo` según la ubicación real del repositorio.

### Paso 3: Creación del Directorio de Logs
```bash
mkdir -p ~/usipipo/logs
```

### Paso 4: Inicio del Bot con PM2
```bash
cd ~/usipipo
pm2 start ecosystem.config.js
```

### Paso 5: Configuración para Inicio Automático
```bash
# Guardar la configuración actual
pm2 save

# Generar script de inicio automático
pm2 startup systemd

# Ejecutar el comando generado por PM2 (ejemplo aproximado):
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u $USER --hp $HOME
```

### Paso 6: Comandos Útiles de PM2
```bash
# Estado del proceso
pm2 status

# Logs en tiempo real
pm2 logs usipipo

# Logs de errores
pm2 logs usipipo --err

# Reinicio
pm2 restart usipipo

# Detención
pm2 stop usipipo

# Eliminación (sin borrar archivos)
pm2 delete usipipo

# Monitoreo de recursos
pm2 monit
```

---

## ✅ Verificación y Pruebas

### Paso 1: Verificación del Estado del Bot
```bash
pm2 status
```

Salida esperada:

```
┌─────┬────────────────────┬─────────┬─────────┬─────────┬──────────┐
│ id  │ name               │ mode    │ ↺       │ status  │ cpu      │
├─────┼────────────────────┼─────────┼─────────┼─────────┼──────────┤
│ 0   │ usipipo            │ fork    │ 0       │ online  │ 0%       │
└─────┴────────────────────┴─────────┴─────────┴─────────┴──────────┘
```

### Paso 2: Revisión de Logs del Bot
```bash
pm2 logs usipipo --lines 50
```

Salida esperada:

```
🚀 uSipipo VPN Bot iniciado exitosamente
📡 Admin ID: 987654321
👥 Usuarios autorizados: 1
🌍 Servidor: 203.0.113.45:51820
```

### Paso 3: Prueba en Telegram
1. Busque el bot en Telegram por su nombre de usuario (ej.: `@usipipo`).
2. Envía `/start`.
3. Verifique la recepción del menú principal con opciones como:
   - 🔐 Crear WireGuard
   - 🌐 Crear Outline
   - 📊 Ver Clientes Activos
   - ℹ️ Estado del Servidor
   - ❓ Ayuda

### Paso 4: Verificación de Servicios Docker
```bash
docker compose ps
```

Salida esperada (todos en estado `Up`):

```
NAME                IMAGE                              STATUS
outline             quay.io/outline/shadowbox:stable   Up 5 minutes
pihole              pihole/pihole:latest               Up 5 minutes (healthy)
wireguard           linuxserver/wireguard:latest       Up 5 minutes
```

### Paso 5: Prueba de Creación de Configuraciones VPN
Desde el bot en Telegram:
1. Seleccione **"🔐 Crear WireGuard"** y verifique la recepción de:
   - Archivo `.conf` descargable.
   - Código QR.
   - Instrucciones de conexión.
2. Seleccione **"🌐 Crear Outline"** y verifique la recepción de:
   - Enlace de acceso (`ss://...`).
   - Instrucciones de instalación.

---

## 🛠️ Mantenimiento y Troubleshooting

### Comandos de Diagnóstico
**Estado General del Sistema:**
```bash
# Servicios Docker
docker compose ps

# Estado del bot
pm2 status

# Logs de Docker (últimas 100 líneas)
docker compose logs --tail=100

# Logs del bot (últimas 100 líneas)
pm2 logs usipipo --lines 100
```

### Problemas Comunes

#### 🔴 El Bot No Responde en Telegram
**Diagnóstico:**
```bash
pm2 logs usipipo --err
```

**Soluciones:**
1. Verifique la validez del token en `.env`.
2. Pruebe la conectividad a la API de Telegram:
   ```bash
   curl -I https://api.telegram.org
   ```
3. Reinície el bot:
   ```bash
   pm2 restart usipipo
   ```

#### 🔴 Error: "WIREGUARD_SERVER_PUBLIC_KEY not found"
**Solución:**
```bash
# Extraer clave correcta
docker exec wireguard cat /config/server/publickey

# Editar .env
nano ~/usipipo/.env
# Actualice WIREGUARD_SERVER_PUBLIC_KEY=...

# Reiniciar
pm2 restart usipipo
```

#### 🔴 Error: "Outline API connection failed"
**Diagnóstico:**
```bash
docker logs outline --tail 50
```

**Soluciones:**
1. Reinície el contenedor:
   ```bash
   docker compose restart outline
   ```
2. Regenerar certificados:
   - Edite `.env` y establezca `PRESERVE_CERTS=false`.
   - Ejecute `./docker.sh` (opciones 4 y luego 2).
3. Verifique conectividad:
   ```bash
   curl -k https://localhost:${OUTLINE_API_PORT}
   ```

#### 🔴 WireGuard No Genera Configuraciones
**Diagnóstico:**
```bash
docker exec wireguard wg show
```

**Soluciones:**
1. Reinície el contenedor:
   ```bash
   docker compose restart wireguard
   ```
2. Verifique rango de IPs:
   ```bash
   docker exec wireguard cat /config/wg0.conf | grep AllowedIPs
   ```

### Actualización del Bot
```bash
cd ~/usipipo

# Respaldar configuración local
cp .env .env.backup

# Actualizar repositorio
git pull origin main

# Restaurar configuración
cp .env.backup .env

# Reinstalar dependencias
cd bot
npm install

# Reiniciar
pm2 restart usipipo
```

### Backup de Configuración
**Creación de Backup:**
```bash
# Crear directorio
mkdir -p ~/backups

# Generar backup
tar -czf ~/backups/usipipo-backup-$(date +%Y%m%d).tar.gz \
  ~/usipipo/.env \
  ~/usipipo/bot/data/authorized_users.json \
  ~/usipipo/docker-compose.yml

# Listar backups
ls -lh ~/backups/
```

**Restauración de Backup:**
```bash
# Detener servicios
pm2 stop usipipo
docker compose down

# Extraer
tar -xzf ~/backups/usipipo-backup-YYYYMMDD.tar.gz -C ~/

# Reiniciar
docker compose up -d
pm2 restart usipipo
```

### Monitoreo de Recursos
```bash
# Estadísticas de contenedores
docker stats

# Uso de disco
df -h

# Procesos del sistema (instale htop si es necesario: sudo apt install htop)
htop
```

### Ubicaciones de Logs
```bash
# Logs PM2
~/usipipo/logs/pm2-out.log
~/usipipo/logs/pm2-error.log

# Logs Docker
docker compose logs -f outline
docker compose logs -f wireguard
docker compose logs -f pihole

# Logs del sistema
/var/log/syslog
```

---

## 📞 Soporte

### Documentación Adicional
- [Telegraf](https://telegrafjs.org/)
- [WireGuard](https://www.wireguard.com/)
- [Outline](https://getoutline.org/)
- [Pi-hole](https://docs.pi-hole.net/)
- [PM2](https://pm2.keymetrics.io/)

### Contacto
- Correo electrónico: usipipo@etlgr.com
- Reporte de incidencias: [GitHub Issues](https://github.com/mowgliph/usipipo/issues)

---

## ✨ Siguientes Pasos

Tras la verificación exitosa:
1. **Agregar Usuarios Autorizados:** Solicite IDs de Telegram a usuarios (usando `/miinfo` en el bot) y ejecute `/agregar [ID] [nombre_opcional]` como administrador.
2. **Configurar Límites de Datos en Outline:** Edite `bot/config/constants.js` para modificar `OUTLINE_DEFAULT_DATA_LIMIT`.
3. **Personalizar Mensajes:** Modifique `bot/utils/messages.js` para adaptar textos.
4. **Monitorear Uso:** Utilice `/stats` o **"📊 Ver Clientes Activos"** para estadísticas.
5. **Backups Automáticos:** Cree un script crontab para backups diarios:

   ```bash
   sudo nano /etc/cron.daily/usipipo-backup
   ```

   Contenido:
   ```bash
   #!/bin/bash
   tar -czf /root/backups/usipipo-backup-$(date +%Y%m%d).tar.gz \
     /root/usipipo/.env \
     /root/usipipo/bot/data/authorized_users.json
   
   # Retener solo últimos 7 días
   find /root/backups -name "usipipo-backup-*.tar.gz" -mtime +7 -delete
   ```

   Permisos:
   ```bash
   sudo chmod +x /etc/cron.daily/usipipo-backup
   ```

---

## 📄 Licencia

Este proyecto se distribuye bajo la Licencia MIT. Consulte el archivo [LICENSE](LICENSE) para detalles completos.

---

**¡Instalación completada exitosamente!** 🎉

Su sistema VPN gestionado mediante Telegram con bloqueo de anuncios integrado está ahora operativo. Asegúrese de monitorear regularmente su infraestructura para mantener la seguridad y el rendimiento óptimos.