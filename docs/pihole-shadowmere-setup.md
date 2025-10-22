# 📋 Documentación Completa: Configuración de Pi-hole y Shadowmere para uSipipo

## 🎯 Introducción y Objetivos

Esta documentación proporciona una guía completa para instalar y configurar **Pi-hole** (servidor DNS con bloqueo de anuncios) y **Shadowmere** (detector de proxies SOCKS5) en el proyecto **uSipipo**, un bot de Telegram para gestión de VPN.

### 🎯 Objetivos
- Instalar Pi-hole como servidor DNS centralizado
- Configurar Shadowmere para detección automática de proxies
- Integrar ambos servicios con uSipipo
- Configurar DNS para servicios VPN (Outline, WireGuard, MTProto)
- Proporcionar comandos de gestión y troubleshooting

### 📋 Requisitos Previos
- **Sistema Operativo**: Debian 10+ o Ubuntu 18.04+
- **Privilegios**: Root o sudo
- **Red**: Conexión a internet estable
- **Espacio**: Mínimo 2GB libres en disco
- **Puertos**: 53 (DNS), 80 (Pi-hole web), 8080 (Shadowmere API)

---

## 🛠️ Instalación Paso a Paso

### 1. 📦 Instalación de Pi-hole

#### Script Automatizado
```bash
# Ejecutar como root
sudo ./scripts/pihole-install.sh
```

#### ¿Qué hace el script?
- ✅ Instala Docker si no está presente
- ✅ Crea red Docker dedicada (`pihole-network`)
- ✅ Crea volúmenes persistentes (`pihole-data`, `pihole-dnsmasq`)
- ✅ Genera puerto aleatorio para interfaz web (8000-9000)
- ✅ Configura Pi-hole con DNSSEC y DNS upstream (1.1.1.1, 1.0.0.1)
- ✅ Genera credenciales aleatorias (web password + API key)
- ✅ Crea archivo `.env.pihole.generated` con variables para uSipipo

#### Variables Generadas
```bash
# Archivo: .env.pihole.generated
PIHOLE_HOST="localhost"
PIHOLE_PORT="8123"  # Puerto aleatorio generado
PIHOLE_DNS_PORT="53"
# PIHOLE_PASSWORD="random_password"  # Mantener secreto
# PIHOLE_API_KEY="random_api_key"    # Mantener secreto
PIHOLE_CONTAINER_NAME="pihole"
PIHOLE_NETWORK_NAME="pihole-network"
PIHOLE_VOLUME_NAME="pihole-data"
PIHOLE_DNSMASQ_VOLUME_NAME="pihole-dnsmasq"
```

#### Acceso a Pi-hole
- **URL Web**: `http://localhost:{PIHOLE_PORT}/admin`
- **Usuario**: `admin`
- **Contraseña**: Ver `.env.pihole.generated` (línea comentada)

### 2. 🔍 Instalación de Shadowmere

#### Script Automatizado
```bash
# Ejecutar como root
sudo ./scripts/shadowmere-install.sh
```

#### ¿Qué hace el script?
- ✅ Instala dependencias (Python3, pip, git, build-essential)
- ✅ Crea usuario sistema `shadowmere`
- ✅ Clona repositorio desde GitHub
- ✅ Instala dependencias Python (aiohttp, requests, etc.)
- ✅ Genera puerto aleatorio para API (5000-6000)
- ✅ Crea configuración YAML completa
- ✅ Configura servicio systemd
- ✅ Crea archivo `.env.shadowmere.generated` con variables para uSipipo

#### Variables Generadas
```bash
# Archivo: .env.shadowmere.generated
SHADOWMERE_HOST="localhost"
SHADOWMERE_PORT="5432"  # Puerto aleatorio generado
SHADOWMERE_API_URL="http://localhost:5432"
SHADOWMERE_SCAN_INTERVAL="3600"
SHADOWMERE_VALIDATION_INTERVAL="1800"
SHADOWMERE_SERVICE_NAME="shadowmere"
SHADOWMERE_DIR="/opt/shadowmere"
SHADOWMERE_USER="shadowmere"
```

#### Configuración Shadowmere
```yaml
# Archivo: /opt/shadowmere/config/shadowmere.yml
api:
  host: 0.0.0.0
  port: 5432
  debug: false

scanner:
  interval: 3600  # 1 hora
  validation_interval: 1800  # 30 minutos
  max_concurrent: 50
  timeout: 10
  proxy_types:
    - socks5
    - socks4
    - http
    - https

storage:
  type: sqlite
  path: "/opt/shadowmere/data/proxies.db"
  retention_days: 30

logging:
  level: INFO
  file: "/opt/shadowmere/logs/shadowmere.log"
```

### 3. 🔧 Configuración DNS para VPN

#### Script Automatizado
```bash
# Ejecutar como root (después de instalar Pi-hole)
sudo ./scripts/configure-dns-vpn.sh
```

#### ¿Qué hace el script?
- ✅ Lee configuraciones de `.env.pihole.generated`
- ✅ Configura DNS en contenedores Outline
- ✅ Actualiza configuraciones WireGuard (cliente/servidor)
- ✅ Configura DNS en servicio MTProto
- ✅ Valida funcionamiento DNS
- ✅ Crea archivo `.env.dns-config.generated`

#### Servicios Soportados
- **Outline**: Configura DNS en contenedor Docker
- **WireGuard**: Actualiza archivos `.conf` de clientes
- **MTProto**: Configura drop-in systemd con DNS

#### Variables Generadas
```bash
# Archivo: .env.dns-config.generated
PIHOLE_DNS_HOST="localhost"
PIHOLE_DNS_PORT="53"
OUTLINE_DNS_CONFIGURED=true
WIREGUARD_DNS_CONFIGURED=true
MTPROXY_DNS_CONFIGURED=true
```

---

## 🔗 Integración con uSipipo

### 1. 📝 Variables de Entorno

#### Copiar Variables al .env
```bash
# Después de ejecutar todos los scripts de instalación
cat .env.pihole.generated >> .env
cat .env.shadowmere.generated >> .env
cat .env.dns-config.generated >> .env
```

#### Variables Requeridas en .env
```bash
# Pi-hole
PIHOLE_HOST="localhost"
PIHOLE_PORT="8123"
PIHOLE_DNS_PORT="53"

# Shadowmere
SHADOWMERE_HOST="localhost"
SHADOWMERE_PORT="5432"
SHADOWMERE_API_URL="http://localhost:5432"

# DNS Configuration
PIHOLE_DNS_HOST="localhost"
PIHOLE_DNS_PORT="53"

# Pagos con Estrellas de Telegram
TELEGRAM_BOT_TOKEN="tu_bot_token_aqui"
STARS_PAYMENT_WEBHOOK_URL="https://tu-dominio.com/webhook/stars"
STARS_PAYMENT_ENABLED=true
```

### 2. 🗄️ Modelos de Base de Datos

#### ShadowmereProxy
```python
# database/models.py
class ShadowmereProxy(Base):
    __tablename__ = "shadowmere_proxies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    proxy_address: Mapped[str] = mapped_column(String(45), unique=True)
    proxy_type: Mapped[str] = mapped_column(String(16))
    country: Mapped[Optional[str]] = mapped_column(String(64))
    is_working: Mapped[bool] = mapped_column(Boolean, default=True)
    response_time: Mapped[Optional[float]] = mapped_column(Float)
    last_checked: Mapped[datetime] = mapped_column(DateTime)
    detection_date: Mapped[datetime] = mapped_column(DateTime)
```

#### MTProtoProxy
```python
class MTProtoProxy(Base):
    __tablename__ = "mtproto_proxies"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    host: Mapped[str] = mapped_column(String(45))
    port: Mapped[int] = mapped_column(Integer)
    secret: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default="active")
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
```

### 3. 🔧 Servicios

#### ShadowmereService
```python
# services/shadowmere.py
class ShadowmereService:
    def __init__(self, shadowmere_api_url: str, shadowmere_port: int):
        # Inicialización del servicio

    async def sync_proxies_to_db(self, session: AsyncSession) -> Dict[str, int]:
        # Sincroniza proxies desde API a BD

    async def get_top_working_proxies(self, session: AsyncSession, limit: int = 10):
        # Obtiene mejores proxies funcionando
```

#### Proxy Service
```python
# services/proxy.py
async def create_free_proxy_for_user(session: AsyncSession, user_id: str) -> Optional[MTProtoProxy]:
    # Crea proxy MTProto gratuito para usuario
```

### 4. 📱 Handlers de Telegram

#### Comando /proxy
- ✅ Crea proxy MTProto gratuito (30 días)
- ✅ Muestra información de proxy existente
- ✅ Genera enlace de conexión `tg://proxy?...`
- ✅ Maneja renovación y revocación

#### Comando /shadowmere (/proxys)
- ✅ Muestra top 10 proxies funcionando
- ✅ Incluye estadísticas (total, funcionando, por tipo)
- ✅ Formato HTML con emojis y códigos

### 5. ⭐ Pagos con Estrellas de Telegram

#### Funcionamiento de los Pagos
Los pagos con estrellas de Telegram permiten a los usuarios adquirir servicios VPN premium directamente desde el bot usando la moneda nativa de Telegram. El sistema integra:

- **Creación de facturas**: El bot genera facturas usando la API de pagos de Telegram
- **Moneda XTR**: Las estrellas (XTR) son la moneda oficial de Telegram
- **Verificación automática**: Los pagos se verifican a través de webhooks o consultas a la API
- **Activación inmediata**: Una vez confirmado el pago, la VPN se activa automáticamente

#### Variables de Entorno Requeridas
```bash
# Archivo: .env
# Pagos con Estrellas de Telegram
TELEGRAM_BOT_TOKEN="tu_bot_token_aqui"  # Token del bot de Telegram
STARS_PAYMENT_WEBHOOK_URL="https://tu-dominio.com/webhook/stars"  # URL para webhooks (opcional)
STARS_PAYMENT_ENABLED=true  # Habilitar pagos con estrellas
```

#### Comandos del Bot para Pagos
```bash
# Comando /pay o /stars
/pay wireguard 3    # Pagar 3 meses de WireGuard con estrellas
/stars outline 6    # Pagar 6 meses de Outline con estrellas

# Ejemplos de uso:
/pay wireguard 1    # 1 mes WireGuard
/pay outline 12     # 12 meses Outline
/stars wireguard 6  # 6 meses WireGuard
```

#### Modelo de Base de Datos para Pagos
```python
# database/models.py
class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    telegram_payment_id: Mapped[Optional[str]] = mapped_column(String(255))
    stars_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='XTR')
    status: Mapped[str] = mapped_column(String(16), default="pending")
    service_type: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=func.utc_timestamp())
```

#### Servicios de Pagos
```python
# services/stars_payments.py
class StarsPaymentService:
    async def process_star_payment(self, payment, telegram_user_id, bot):
        # Crear invoice usando Telegram Payments API
        # Retorna invoice_id y payment_url

    async def verify_payment(self, payment, invoice_id):
        # Verificar estado del pago
        # Retorna "paid", "failed", o "pending"

    async def handle_stars_webhook(self, webhook_data):
        # Procesar webhooks de pagos exitosos
```

---

## 🎮 Comandos de Gestión

### Pi-hole
```bash
# Estado del contenedor
docker ps | grep pihole

# Logs del contenedor
docker logs pihole

# Reiniciar Pi-hole
docker restart pihole

# Acceder al shell
docker exec -it pihole /bin/bash

# Actualizar Pi-hole
docker pull pihole/pihole:latest
docker stop pihole
docker rm pihole
# Re-ejecutar script de instalación
```

### Shadowmere
```bash
# Estado del servicio
sudo systemctl status shadowmere

# Logs del servicio
sudo journalctl -u shadowmere -f

# Reiniciar servicio
sudo systemctl restart shadowmere

# Detener servicio
sudo systemctl stop shadowmere

# Iniciar servicio
sudo systemctl start shadowmere

# Acceder al directorio
sudo -u shadowmere bash
cd /opt/shadowmere

# Ver configuración
cat config/shadowmere.yml

# Ejecutar manualmente
sudo -u shadowmere python3 main.py --config config/shadowmere.yml
```

### DNS Configuration
```bash
# Revertir configuración DNS
sudo ./scripts/configure-dns-vpn.sh --revert

# Re-aplicar configuración
sudo ./scripts/configure-dns-vpn.sh

# Ver configuración aplicada
cat .env.dns-config.generated
```

---

## 🔧 Solución de Problemas

### Problemas Comunes de Instalación

#### Docker no se instala
```bash
# Verificar versión de Debian/Ubuntu
lsb_release -a

# Instalar Docker manualmente
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable docker
sudo systemctl start docker
```

#### Pi-hole no inicia
```bash
# Verificar puertos ocupados
sudo netstat -tulpn | grep :53
sudo netstat -tulpn | grep :80

# Ver logs detallados
docker logs pihole

# Verificar volúmenes
docker volume ls | grep pihole
```

#### Shadowmere no compila dependencias
```bash
# Actualizar pip
sudo pip3 install --upgrade pip

# Instalar dependencias manualmente
sudo pip3 install aiohttp asyncio pysocks requests pyyaml python-dotenv
```

### Errores de Configuración DNS

#### DNS no funciona en VPN
```bash
# Verificar que Pi-hole esté corriendo
curl -s http://localhost:8123/admin/api.php

# Probar resolución DNS
nslookup google.com localhost

# Verificar configuración VPN
# Para WireGuard: cat /etc/wireguard/*.conf | grep DNS
# Para Outline: docker exec outline cat /etc/resolv.conf
```

#### Problemas de conectividad
```bash
# Verificar conectividad a internet
ping 8.8.8.8

# Verificar firewall
sudo ufw status
sudo iptables -L

# Verificar DNS del sistema
cat /etc/resolv.conf
```

### Logs y Debugging

#### Pi-hole Logs
```bash
# Logs del contenedor
docker logs -f pihole

# Logs de DNS queries
docker exec pihole tail -f /var/log/pihole.log

# Estadísticas
docker exec pihole pihole -c
```

#### Shadowmere Logs
```bash
# Logs del servicio
sudo journalctl -u shadowmere -n 50

# Logs de aplicación
sudo tail -f /opt/shadowmere/logs/shadowmere.log

# Ver procesos
ps aux | grep shadowmere
```

#### uSipipo Logs
```bash
# Ver logs del bot
sudo journalctl -u usipipo -f

# Logs de aplicación (si configurado)
tail -f /var/log/usipipo/app.log
```

---

## 📊 Diagramas y Arquitectura

### Arquitectura General
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │────│   uSipipo App   │────│  MariaDB/MySQL  │
│   (Python)      │    │   (Services)    │    │   (Database)    │
│                 │    │                 │    │                 │
│  ⭐ Stars API   │    │ ⭐ Stars Service │    │  ⭐ Payments    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Pi-hole     │    │   Shadowmere    │    │   VPN Services  │
│   (DNS Server)  │    │ (Proxy Scanner) │    │ (Outline/WG/MTP)│
│   (Docker)      │    │   (Python)      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Flujo de Datos DNS
```
Cliente VPN ──DNS Query──> Pi-hole ──Filtered Response──> Cliente
     │                        │
     │                        │
     └─Outline/WireGuard/MTProto─┘
```

### Configuración de Red
```
Internet
    │
    ▼
┌─────────────┐    ┌─────────────┐
│   Router    │────│   Server    │
│ (Port 53)   │    │             │
└─────────────┘    │ ┌─────────┐ │
                   │ │ Pi-hole │ │
                   │ │ (DNS)   │ │
                   │ └─────────┘ │
                   │ ┌─────────┐ │
                   │ │Shadowmere││
                   │ │ (API)   │ │
                   │ └─────────┘ │
                   │ ┌─────────┐ │
                   │ │ uSipipo │ │
                   │ │  (Bot)  │ │
                   │ └─────────┘ │
                   └─────────────┘
```

---

## 📚 Referencias a Archivos

### Scripts Creados/Modificados
- [`scripts/pihole-install.sh`](scripts/pihole-install.sh) - Instalación automatizada de Pi-hole
- [`scripts/shadowmere-install.sh`](scripts/shadowmere-install.sh) - Instalación automatizada de Shadowmere
- [`scripts/configure-dns-vpn.sh`](scripts/configure-dns-vpn.sh) - Configuración DNS para VPN

### Modelos de Base de Datos
- [`database/models.py`](database/models.py) - Modelos ShadowmereProxy y MTProtoProxy
- [`database/crud/shadowmere.py`](database/crud/shadowmere.py) - Operaciones CRUD para proxies Shadowmere
- [`database/crud/proxy.py`](database/crud/proxy.py) - Operaciones CRUD para proxies MTProto

### Servicios
- [`services/shadowmere.py`](services/shadowmere.py) - Servicio de integración con Shadowmere
- [`services/proxy.py`](services/proxy.py) - Servicio de gestión de proxies MTProto

### Handlers de Telegram
- [`bot/handlers/proxy.py`](bot/handlers/proxy.py) - Handler para comando /proxy
- [`bot/handlers/shadowmere.py`](bot/handlers/shadowmere.py) - Handler para comando /shadowmere

### Archivos de Configuración
- [`example.env.md`](example.env.md) - Plantilla de variables de entorno
- [`config/usipipo.service`](config/usipipo.service) - Servicio systemd para uSipipo

---

## ✅ Verificación de Funcionamiento

### Checklist de Instalación
- [ ] Pi-hole instalado y corriendo en Docker
- [ ] Interfaz web accesible en puerto asignado
- [ ] DNS funcionando (nslookup google.com localhost)
- [ ] Shadowmere instalado como servicio systemd
- [ ] API de Shadowmere respondiendo en puerto asignado
- [ ] Variables de entorno copiadas al .env de uSipipo
- [ ] Base de datos inicializada con tablas Shadowmere y Payments
- [ ] Comandos /proxy y /shadowmere funcionando en Telegram
- [ ] Pagos con estrellas de Telegram configurados y funcionando
- [ ] Comandos /pay y /stars disponibles en el bot

### Comandos de Verificación
```bash
# Verificar Pi-hole
curl -s http://localhost:8123/admin/api.php | jq .status

# Verificar Shadowmere
curl -s http://localhost:5432/api/proxies | head -20

# Verificar servicios VPN
sudo systemctl status outline wireguard mtproto-proxy

# Verificar uSipipo
sudo systemctl status usipipo
```

---

## 🎉 Conclusión

Esta documentación proporciona una guía completa para integrar Pi-hole y Shadowmere con uSipipo. Los scripts automatizados simplifican la instalación, mientras que la integración con la base de datos y los handlers de Telegram permite una gestión completa desde el bot.

**Recuerda**: Mantén las credenciales seguras y realiza backups regulares de la configuración y base de datos.

📧 **Soporte**: Para problemas específicos, revisa los logs de cada servicio y consulta la documentación de troubleshooting.