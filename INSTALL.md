# Instalación y Configuración de uSipipo

Este documento detalla cómo instalar y configurar uSipipo, un bot de Telegram basado en Python 3.11+, SQLAlchemy ORM, y python-telegram-bot v20+. Sigue la arquitectura models-crud-services-handlers para un código limpio, escalable y mantenible. El bot gestiona WireGuard, Outline VPN, y MTProto Proxy, con un backend robusto.

## Requisitos Previos

**Sistema Operativo:** Ubuntu 20.04+/Debian 10+ (recomendado), macOS, o Windows con WSL2.

**Python:** 3.11+ (requerido para python-telegram-bot v20+ con soporte async). Descarga desde [python.org](https://www.python.org/).

**Base de Datos:** MariaDB (recomendado para producción y desarrollo). Instala MariaDB:
```bash
sudo apt install mariadb-server mariadb-client
```

**Git:** Para clonar el repositorio.

**Dependencias del Sistema:** python3-pip, python3-venv, git, qrencode, curl, wget.

**Claves API:** Obtén un `TELEGRAM_BOT_TOKEN` de BotFather. Para Outline, configura una API URL y certificado SHA256.

**Dominio:** Un dominio apuntando a la IP del VPS (opcional para producción).

---

### Verifica Python

```bash
python3 --version  # Debe mostrar 3.11+
```

---

## Paso 1: Configuración Inicial del Servidor

### 1.1 Actualizar el Sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Instalar Dependencias del Sistema
```bash
sudo apt install -y python3-pip python3-venv git qrencode curl wget
```

#### Para MariaDB:
```bash
sudo apt install -y mariadb-server mariadb-client
sudo systemctl enable mariadb
sudo systemctl start mariadb
sudo mysql_secure_installation
```

---

## Paso 2: Instalación de uSipipo

### 2.1 Clonar el Repositorio
```bash
cd /opt
sudo git clone https://github.com/mowgliph/usipipo.git
sudo chown -R $USER:$USER usipipo
cd usipipo
```

### 2.2 Configurar Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# Windows (WSL): source venv/bin/activate
# Windows (CMD): venv\Scripts\activate
```

#### Alternativa con Poetry
```bash
pip install poetry
poetry install
poetry shell
```

### 2.3 Instalar Dependencias de Python
```bash
pip install -r requirements.txt
```

Ejemplo de `requirements.txt`:
```
python-telegram-bot>=20.0
sqlalchemy>=2.0
pymysql
python-dotenv
aiohttp
```

---

## Paso 3: Configuración de la Base de Datos

### 3.1 Configurar Variables de Entorno
```bash
cp example.env .env
nano .env
```
Configura las variables:
```
TELEGRAM_BOT_TOKEN=tu-token-aqui
DATABASE_URL=mysql+pymysql://user:pass@localhost/usipipo
...
```

### 3.2 Inicializar la Base de Datos
```bash
sudo mysql -u root -p -e "CREATE DATABASE usipipo; CREATE USER 'usipipo_user'@'localhost' IDENTIFIED BY 'tu-contrasena'; GRANT ALL PRIVILEGES ON usipipo.* TO 'usipipo_user'@'localhost'; FLUSH PRIVILEGES;"
python scripts/init_db.py
```

---

## Paso 4: Configurar Servicio Systemd

### 4.1 Crear Archivo de Servicio
```bash
sudo nano /etc/systemd/system/usipipo.service
```
Agrega:
```
[Unit]
Description=uSipipo Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/usipipo
Environment=PATH=/opt/usipipo/venv/bin
EnvironmentFile=/opt/usipipo/.env
ExecStart=/opt/usipipo/venv/bin/python bot/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 4.2 Habilitar e Iniciar el Servicio
```bash
sudo systemctl daemon-reload
sudo systemctl enable usipipo
sudo systemctl start usipipo
```

---

## Paso 5: Verificación

### 5.1 Verificar Servicios
```bash
sudo systemctl status usipipo
sudo systemctl status wg-quick@wg0
```

### 5.2 Probar el Bot
Envía `/start` al bot en Telegram.

### 5.3 Verificar Logs
Logs: `logs/bot.log`

---

## Paso 6: Configuración de Producción

- Logging Centralizado con `utils/helpers.py`  
- Escalabilidad con Docker  
- Seguridad mediante secrets manager  

Ejemplo de `Dockerfile`:
```
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "bot/main.py"]
```

---

## Troubleshooting

- “Permission denied” en scripts → `chmod +x script.sh`  
- Bot no responde → revisa `TELEGRAM_BOT_TOKEN`  
- DB error → revisa `DATABASE_URL`  
- Logs vacíos → `LOG_LEVEL=INFO`

---

## Soporte

- Ver logs: `journalctl -u usipipo`
- Consultar repositorio o abrir issue en GitHub

---

**¡Felicidades! uSipipo está instalado y listo en tu VPS.**  
Última actualización: Octubre 2025.
