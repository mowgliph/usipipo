# Instalación y Configuración de uSipipo

Este documento proporciona un paso a paso detallado para instalar y configurar uSipipo en un VPS personal.

## Requisitos Previos

- Un servidor VPS con Ubuntu 20.04+ o Debian 10+
- Acceso root o sudo al servidor
- Un nombre de dominio apuntando a la IP de tu VPS
- Python 3.8+ instalado

## Paso 1: Configuración Inicial del Servidor

### 1.1 Actualizar el Sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Instalar Dependencias
```bash
sudo apt install -y python3-pip python3-venv git sqlite3 qrencode curl wget
```


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
source venv/bin/activate
```


### 2.3 Instalar Dependencias de Python

```bash
pip install -r requirements.txt
```


### 2.1.1 Instalar WireGuard VPN

Ejecuta el script de instalación de WireGuard:
```bash
sudo bash scripts/wireguard-install.sh
```


### 2.1.2 Instalar Outline VPN Server Manager

Ejecuta el script de instalación de Outline:
```bash
sudo bash scripts/outline-install.sh
```

### 2.1.3 Instalar MTProto Proxy

Ejecuta el script de instalación de MTProto Proxy:
```bash
sudo bash scripts/mtproto-install.sh
```

## Paso 3: Configuración de la Base de Datos




### 3.1 Inicializar la Base de Datos
```bash
python scripts/init_db.py
```


### 3.2 Configurar Variables de Entorno
Copia el archivo de ejemplo de configuración:

```bash
cp example.env.md .env
```

Edita el archivo `.env` con tus configuraciones:
```bash
nano .env
```


Asegúrate de configurar todas las variables necesarias:

- `TELEGRAM_BOT_TOKEN`: Token de tu bot de Telegram
- `TELEGRAM_PROVIDER_TOKEN`: Token de proveedor de Telegram (opcional)
- `DATABASE_URL`: Ruta a tu base de datos SQLite
- `OUTLINE_API_URL`: URL de tu servidor Outline
- `OUTLINE_CERT_SHA256`: SHA256 del certificado SSL de Outline
- `BOT_VERSION`: Versión del bot
- `WG_INTERFACE`: Interfaz de WireGuard (ej: wg0)
- `WG_CONFIG_DIR`: Directorio de configuración de WireGuard
- `SERVER_PUBLIC_KEY`: Clave pública del servidor WireGuard
- `SERVER_ENDPOINT`: Endpoint público del servidor
- `WG_SUBNET_PREFIX`: Prefijo de subred WireGuard
- `WG_IP_START`: IP inicial para asignar a clientes
- `WG_IP_END`: IP final para asignar a clientes



## Paso 4: Configurar Servicio Systemd para el Bot


### 4.1 Crear Archivo de Servicio

```bash
sudo nano /etc/systemd/system/usipipo.service
```


Añade la siguiente configuración:


```ini
[Unit]
Description=uSipipo Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/usipipo
Environment=PATH=/opt/usipipo/venv/bin
ExecStart=/opt/usipipo/venv/bin/python bot/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```



### 4.2 Habilitar y Iniciar el Servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable usipipo
sudo systemctl start usipipo
```

## Paso 5: Configuración Final




### 5.1 Configurar Variables de Entorno de Producción
Edita tu archivo `.env` para incluir:

```env
DEBUG=False
ENVIRONMENT=production
```




### 5.2 Inicializar Base de Datos
```bash
python scripts/init_db.py
```




### 5.3 Reiniciar Servicios
```bash
sudo systemctl restart usipipo
```

## Paso 6: Verificación



### 6.1 Verificar Servicios
```bash
sudo systemctl status usipipo
sudo systemctl status wg-quick@wg0
```



### 6.2 Probar la Aplicación
Envía un mensaje a tu bot de Telegram para verificar que está funcionando correctamente.



### 6.3 Configurar Administrador
Usa los comandos del bot para configurar tu cuenta de administrador:


- Inicia el bot y sigue las instrucciones
- Usa el comando `/admin` para configurar permisos de administrador


## Soporte

Si encuentras problemas durante la instalación, por favor:

1. Revisa los logs de los servicios
2. Consulta la documentación del proyecto
3. Abre un issue en el repositorio de GitHub

---

¡Felicidades! Ahora tienes uSipipo instalado y funcionando en tu VPS personal.
