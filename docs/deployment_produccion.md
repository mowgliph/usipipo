# 🚀 Guía de Deployment y Configuración para Producción

## Descripción General

Esta guía proporciona instrucciones completas para desplegar uSipipo en un entorno de producción, incluyendo configuración de seguridad, monitoreo, backup y escalabilidad.

## 📋 Prerrequisitos de Producción

### Infraestructura Recomendada

#### VPS/Dedicated Server
- **CPU**: 2-4 cores (Intel/AMD moderno)
- **RAM**: 4-8 GB mínimo, 16 GB recomendado
- **Almacenamiento**: 50-100 GB SSD
- **Red**: 100 Mbps+ con IPv4 e IPv6
- **Uptime SLA**: 99.9%+

#### Sistema Operativo
- **Primario**: Ubuntu 22.04 LTS
- **Alternativo**: Debian 11+, CentOS 8+
- **Kernel**: 5.4+ para WireGuard

### Requisitos de Red

#### Puertos Requeridos
```
22/tcp   - SSH (administración)
80/tcp   - HTTP (redirect to HTTPS)
443/tcp  - HTTPS (API y bot)
51820/udp - WireGuard VPN
443/tcp  - Outline VPN (Shadowsocks)
3306/tcp - MariaDB (solo local)
6379/tcp - Redis (planeado, solo local)
```

#### Firewall (UFW)
```bash
# Configuración básica de firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 51820/udp  # WireGuard
sudo ufw --force enable
```

## 🛠️ Instalación Paso a Paso

### Paso 1: Configuración Inicial del Servidor

#### 1.1 Actualización del Sistema
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar utilidades básicas
sudo apt install -y curl wget git htop iotop ncdu tree jq

# Configurar timezone
sudo timedatectl set-timezone America/Havana
```

#### 1.2 Configuración de Usuario
```bash
# Crear usuario para la aplicación
sudo useradd -m -s /bin/bash usipipo
sudo usermod -aG sudo usipipo

# Configurar SSH key-only access
sudo mkdir -p /home/usipipo/.ssh
sudo chmod 700 /home/usipipo/.ssh
# Copiar authorized_keys
sudo chown -R usipipo:usipipo /home/usipipo/.ssh
```

#### 1.3 Instalar Python y Dependencias
```bash
# Instalar Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Instalar build tools
sudo apt install -y build-essential libssl-dev libffi-dev python3-setuptools

# Instalar pip
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
```

### Paso 2: Base de Datos

#### 2.1 Instalar MariaDB
```bash
# Instalar MariaDB
sudo apt install -y mariadb-server mariadb-client

# Iniciar y habilitar servicio
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Configuración segura
sudo mysql_secure_installation
```

#### 2.2 Crear Base de Datos y Usuario
```bash
sudo mysql -u root -p << EOF
CREATE DATABASE usipipo_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'usipipo_user'@'localhost' IDENTIFIED BY 'tu_password_seguro_aqui';
GRANT ALL PRIVILEGES ON usipipo_prod.* TO 'usipipo_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
EOF
```

#### 2.3 Optimización MariaDB para Producción
```bash
# Crear archivo de configuración personalizado
sudo tee /etc/mysql/mariadb.conf.d/99-usipipo.cnf > /dev/null <<EOF
[mysqld]
# Configuración básica
bind-address = 127.0.0.1
port = 3306

# InnoDB optimizations
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT

# Connection settings
max_connections = 200
wait_timeout = 28800
interactive_timeout = 28800

# Query cache (deprecated in MySQL 8.0+, but available in MariaDB)
query_cache_size = 256M
query_cache_type = ON
query_cache_limit = 1M

# Logging
slow_query_log = ON
slow_query_log_file = /var/log/mysql/mariadb-slow.log
long_query_time = 2

# Security
sql_mode = STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO
EOF

# Reiniciar MariaDB
sudo systemctl restart mariadb
```

### Paso 3: Instalar y Configurar Servicios VPN

#### 3.1 WireGuard
```bash
# Instalar WireGuard
sudo apt install -y wireguard wireguard-tools qrencode

# Generar claves del servidor
sudo mkdir -p /etc/wireguard
wg genkey | sudo tee /etc/wireguard/server_private.key | wg pubkey | sudo tee /etc/wireguard/server_public.key

# Configurar interfaz wg0
sudo tee /etc/wireguard/wg0.conf > /dev/null <<EOF
[Interface]
Address = 10.0.0.1/24
ListenPort = 51820
PrivateKey = $(cat /etc/wireguard/server_private.key)
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Peers will be added dynamically by the application
EOF

# Habilitar IP forwarding
sudo tee /etc/sysctl.d/99-wireguard.conf > /dev/null <<EOF
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1
EOF
sudo sysctl -p /etc/sysctl.d/99-wireguard.conf

# Iniciar WireGuard
sudo systemctl start wg-quick@wg0
sudo systemctl enable wg-quick@wg0
```

#### 3.2 Outline VPN (Shadowsocks)
```bash
# Instalar Docker (requerido para Outline)
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# Crear directorio para Outline
sudo mkdir -p /opt/outline
cd /opt/outline

# Descargar y configurar Outline Manager
wget https://raw.githubusercontent.com/Jigsaw-Code/outline-server/master/src/server_manager/install_scripts/install_server.sh
chmod +x install_server.sh

# Ejecutar instalación (interactiva)
sudo ./install_server.sh
```

### Paso 4: Desplegar uSipipo

#### 4.1 Clonar y Configurar
```bash
# Clonar repositorio
cd /opt
sudo git clone https://github.com/mowgliph/usipipo.git
sudo chown -R usipipo:usipipo usipipo
cd usipipo

# Crear entorno virtual
sudo -u usipipo python3.11 -m venv venv
sudo -u usipipo bash -c "source venv/bin/activate && pip install -r requirements.txt"
```

#### 4.2 Configuración de Producción
```bash
# Copiar archivo de configuración
sudo -u usipipo cp example.env .env

# Editar configuración de producción
sudo -u usipipo tee .env > /dev/null <<EOF
# Bot Configuration
TELEGRAM_BOT_TOKEN=tu_token_de_produccion
ADMIN_USER_IDS=tu_telegram_id

# Database
DATABASE_URL=mysql+pymysql://usipipo_user:tu_password_seguro@localhost/usipipo_prod

# Security
SECRET_KEY=tu_clave_secreta_muy_segura_de_al_menos_32_caracteres
API_SECRET_KEY=tu_api_key_para_integraciones

# VPN Configuration
WIREGUARD_INTERFACE=wg0
WIREGUARD_ENDPOINT=tu.dominio.com
OUTLINE_API_URL=https://tu-outline-server.com

# Payments
QVAPAY_APP_ID=tu_qvapay_app_id
QVAPAY_APP_SECRET=tu_qvapay_app_secret

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/usipipo/bot.log

# System
SYSTEM_TIMEZONE=America/Havana
BACKUP_RETENTION_DAYS=30
EOF

# Crear directorio de logs
sudo mkdir -p /var/log/usipipo
sudo chown usipipo:usipipo /var/log/usipipo
```

#### 4.3 Inicializar Base de Datos
```bash
# Ejecutar como usuario usipipo
sudo -u usipipo bash -c "cd /opt/usipipo && source venv/bin/activate && python scripts/init_db.py"
```

### Paso 5: Configuración de Systemd

#### 5.1 Crear Servicio Systemd
```bash
# Crear archivo de servicio
sudo tee /etc/systemd/system/usipipo.service > /dev/null <<EOF
[Unit]
Description=uSipipo Telegram Bot (Production)
After=network.target mariadb.service
Requires=mariadb.service

[Service]
Type=simple
User=usipipo
Group=usipipo
WorkingDirectory=/opt/usipipo
Environment=PATH=/opt/usipipo/venv/bin
EnvironmentFile=/opt/usipipo/.env
ExecStart=/opt/usipipo/venv/bin/python bot/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=usipipo

# Security
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/opt/usipipo /var/log/usipipo
ProtectHome=yes

# Limits
LimitNOFILE=65536
MemoryLimit=1G

[Install]
WantedBy=multi-user.target
EOF

# Recargar systemd y habilitar servicio
sudo systemctl daemon-reload
sudo systemctl enable usipipo
sudo systemctl start usipipo
```

#### 5.2 Configurar Log Rotation
```bash
# Crear configuración de logrotate
sudo tee /etc/logrotate.d/usipipo > /dev/null <<EOF
/var/log/usipipo/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 usipipo usipipo
    postrotate
        systemctl reload usipipo
    endscript
}
EOF
```

### Paso 6: Configuración Web (Nginx + SSL)

#### 6.1 Instalar Nginx
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

#### 6.2 Configurar Nginx
```bash
# Crear configuración de sitio
sudo tee /etc/nginx/sites-available/usipipo > /dev/null <<EOF
server {
    listen 80;
    server_name tu.dominio.com;

    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu.dominio.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/tu.dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu.dominio.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # API endpoints (cuando se implemente)
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Default
    location / {
        return 404;
    }
}
EOF

# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/usipipo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 6.3 Configurar SSL con Let's Encrypt
```bash
# Obtener certificado SSL
sudo certbot --nginx -d tu.dominio.com

# Configurar renovación automática
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Paso 7: Monitoreo y Alertas

#### 7.1 Instalar Monit
```bash
sudo apt install -y monit

# Configurar monitoreo de servicios
sudo tee /etc/monit/conf.d/usipipo > /dev/null <<EOF
# Monitor uSipipo service
check process usipipo with pidfile /var/run/usipipo.pid
    start program = "/bin/systemctl start usipipo"
    stop program = "/bin/systemctl stop usipipo"
    if failed port 443 protocol https request /health then restart
    if 5 restarts within 5 cycles then timeout

# Monitor MariaDB
check process mariadb with pidfile /var/run/mysqld/mysqld.pid
    start program = "/bin/systemctl start mariadb"
    stop program = "/bin/systemctl stop mariadb"
    if failed unixsocket /var/run/mysqld/mysqld.sock then restart

# Monitor WireGuard
check process wireguard with pidfile /var/run/wg-quick.wg0.pid
    start program = "/bin/systemctl start wg-quick@wg0"
    stop program = "/bin/systemctl stop wg-quick@wg0"

# Monitor Nginx
check process nginx with pidfile /var/run/nginx.pid
    start program = "/bin/systemctl start nginx"
    stop program = "/bin/systemctl stop nginx"
    if failed port 443 protocol https request /health then restart
EOF

sudo systemctl restart monit
sudo systemctl enable monit
```

#### 7.2 Configurar Alertas por Email
```bash
# Instalar mailutils
sudo apt install -y mailutils

# Configurar envío de emails en monit
sudo tee /etc/monit/monitrc > /dev/null <<EOF
set mailserver smtp.gmail.com port 587
    username "tu-email@gmail.com" password "tu-app-password"
    using tlsv12

set alert tu-email@gmail.com
EOF

sudo systemctl restart monit
```

### Paso 8: Backup y Recuperación

#### 8.1 Configurar Backups Automáticos
```bash
# Crear script de backup
sudo tee /opt/usipipo/scripts/backup.sh > /dev/null <<EOF
#!/bin/bash

BACKUP_DIR="/opt/backups/usipipo"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="usipipo_backup_\${DATE}"

# Crear directorio de backup
mkdir -p \${BACKUP_DIR}

# Backup de base de datos
mysqldump -u usipipo_user -p'tu_password_seguro' usipipo_prod > \${BACKUP_DIR}/\${BACKUP_NAME}_db.sql

# Backup de configuraciones
tar -czf \${BACKUP_DIR}/\${BACKUP_NAME}_config.tar.gz /opt/usipipo/.env /etc/wireguard /etc/nginx/sites-available/usipipo

# Backup de logs
tar -czf \${BACKUP_DIR}/\${BACKUP_NAME}_logs.tar.gz /var/log/usipipo

# Limpiar backups antiguos (mantener 30 días)
find \${BACKUP_DIR} -name "usipipo_backup_*" -mtime +30 -delete

echo "Backup completado: \${BACKUP_NAME}"
EOF

# Hacer ejecutable
sudo chmod +x /opt/usipipo/scripts/backup.sh

# Configurar cron para backup diario
sudo crontab -e
# Agregar: 0 2 * * * /opt/usipipo/scripts/backup.sh
```

#### 8.2 Script de Restauración
```bash
sudo tee /opt/usipipo/scripts/restore.sh > /dev/null <<EOF
#!/bin/bash

if [ -z "\$1" ]; then
    echo "Uso: \$0 <backup_name>"
    exit 1
fi

BACKUP_NAME=\$1
BACKUP_DIR="/opt/backups/usipipo"

echo "Restaurando backup: \${BACKUP_NAME}"

# Detener servicios
sudo systemctl stop usipipo

# Restaurar base de datos
mysql -u usipipo_user -p'tu_password_seguro' usipipo_prod < \${BACKUP_DIR}/\${BACKUP_NAME}_db.sql

# Restaurar configuraciones
sudo tar -xzf \${BACKUP_DIR}/\${BACKUP_NAME}_config.tar.gz -C /

# Reiniciar servicios
sudo systemctl start usipipo

echo "Restauración completada"
EOF

sudo chmod +x /opt/usipipo/scripts/restore.sh
```

## 🔧 Mantenimiento y Operaciones

### Monitoreo Diario

#### Comandos Útiles
```bash
# Estado de servicios
sudo systemctl status usipipo mariadb nginx wg-quick@wg0

# Logs del bot
sudo journalctl -u usipipo -f

# Logs de base de datos
sudo tail -f /var/log/mysql/mariadb-slow.log

# Uso de recursos
htop
iotop
df -h

# Conexiones VPN activas
sudo wg show wg0
```

### Actualizaciones

#### Actualizar uSipipo
```bash
cd /opt/usipipo
sudo -u usipipo git pull origin main
sudo -u usipipo bash -c "source venv/bin/activate && pip install -r requirements.txt"
sudo systemctl restart usipipo
```

#### Actualizar Sistema
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot  # Si es necesario
```

### Troubleshooting

#### Problemas Comunes

**Bot no responde:**
```bash
# Verificar logs
sudo journalctl -u usipipo --since "1 hour ago"

# Verificar token
sudo -u usipipo grep TELEGRAM_BOT_TOKEN /opt/usipipo/.env

# Reiniciar servicio
sudo systemctl restart usipipo
```

**Errores de base de datos:**
```bash
# Verificar conexión
sudo -u usipipo bash -c "cd /opt/usipipo && source venv/bin/activate && python -c 'from database.db import get_db; next(get_db())'"

# Verificar estado MariaDB
sudo systemctl status mariadb
```

**Problemas de VPN:**
```bash
# Verificar WireGuard
sudo wg show wg0

# Verificar Outline
docker ps | grep outline

# Reiniciar servicios VPN
sudo systemctl restart wg-quick@wg0
```

## 📊 Escalabilidad

### Optimizaciones de Rendimiento

#### Base de Datos
- Configurar índices apropiados
- Implementar connection pooling
- Configurar query cache

#### Aplicación
- Implementar cache con Redis
- Optimizar queries SQL
- Usar async/await correctamente

#### Sistema
- Configurar swap si es necesario
- Ajustar límites del sistema
- Monitorear uso de recursos

### Escalado Horizontal

#### Load Balancer
```nginx
upstream usipipo_api {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 443 ssl;
    location /api/ {
        proxy_pass http://usipipo_api;
    }
}
```

#### Base de Datos Replicada
- Configurar master-slave replication
- Implementar read replicas
- Configurar failover automático

## 🔒 Seguridad de Producción

### Configuración de Firewall Avanzada
```bash
# Instalar fail2ban
sudo apt install -y fail2ban

# Configurar protección SSH
sudo tee /etc/fail2ban/jail.d/sshd.conf > /dev/null <<EOF
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

sudo systemctl restart fail2ban
```

### Auditoría de Seguridad
```bash
# Instalar auditd
sudo apt install -y auditd

# Configurar auditoría de archivos críticos
sudo auditctl -w /opt/usipipo/.env -p rwxa -k usipipo_config
sudo auditctl -w /etc/wireguard -p rwxa -k wireguard_config
```

### Backup Off-site
```bash
# Configurar rclone para backup en la nube
sudo apt install -y rclone

# Configurar destino (ejemplo: AWS S3)
rclone config

# Script de backup off-site
sudo tee /opt/usipipo/scripts/backup_offsite.sh > /dev/null <<EOF
#!/bin/bash
rclone copy /opt/backups/usipipo remote:usipipo-backups
EOF
```

## 📞 Contactos de Emergencia

### Alertas Críticas
- **Administrador Principal**: @tu_usuario_telegram
- **Soporte Técnico**: soporte@usipipo.com
- **Monitoreo**: status.usipipo.com

### Procedimientos de Emergencia
1. **Falla del Bot**: Reinicio automático via systemd
2. **Falla de BD**: Failover a replica (si configurado)
3. **Ataque de Seguridad**: Aislar servidor, investigar logs
4. **Pérdida de Datos**: Restaurar desde backup más reciente

---

**Esta configuración proporciona un despliegue robusto y seguro para uSipipo en producción. Monitorea regularmente los logs y métricas para asegurar un funcionamiento óptimo.**

**Última actualización: Octubre 2025**