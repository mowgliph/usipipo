# ⚙️ Guía de Configuración - uSipipo VPN Manager

> **Configuración completa y personalización del sistema uSipipo**  
> Todas las opciones, variables y ajustes disponibles

## 📋 Tabla de Contenidos

1. [🔧 Configuración Básica](#-configuración-básica)
2. [🤖 Configuración del Bot](#-configuración-del-bot)
3. [🌐 Configuración de Red](#-configuración-de-red)
4. [🔌 Protocolos VPN](#-protocolos-vpn)
5. [🗄️ Base de Datos](#️-base-de-datos)
6. [💰 Sistema de Pagos](#-sistema-de-pagos)
7. [🔒 Seguridad](#-seguridad)
8. [📊 Logging y Monitoreo](#-logging-y-monitoreo)
9. [🎮 Gamificación](#-gamificación)
10. [🔧 Configuración Avanzada](#-configuración-avanzada)

---

## 🔧 Configuración Básica

### 📝 **Archivo .env**
Toda la configuración se centraliza en el archivo `.env` en la raíz del proyecto:

```bash
# =============================================================================
# uSipipo VPN Manager - Environment Configuration
# =============================================================================
# Copia de example.env a .env y rellena los valores requeridos
cp example.env .env
```

### 🌍 **Entorno de Aplicación**
```bash
# Entorno de ejecución
APP_ENV=production          # development | production | staging
DEFAULT_LANG=es             # Idioma por defecto
PROJECT_NAME=uSipipo VPN Manager
```

---

## 🤖 Configuración del Bot

### 🔑 **Credenciales Esenciales**
```bash
# Token del bot (OBTENER DE @BotFather)
TELEGRAM_TOKEN=1234567890:ABCDEFghijklmnopqrstuvwxyz123456789

# ID del administrador principal (OBTENER DE @userinfobot)
ADMIN_ID=987654321

# Usuarios autorizados (opcional, separados por comas)
AUTHORIZED_USERS=123456789,987654321,555666777

# Email del administrador (opcional)
ADMIN_EMAIL=admin@tudominio.com
```

### ⚡ **Rate Limiting**
```bash
# Límite de peticiones por minuto
TELEGRAM_RATE_LIMIT=30      # Límite para usuarios del bot
API_RATE_LIMIT=60          # Límite para la API REST
```

### 🌐 **Webhook (Opcional)**
```bash
# URL para webhook (recomendado para producción)
TELEGRAM_WEBHOOK_URL=https://tudominio.com/webhook/telegram
```

---

## 🌐 Configuración de Red

### 🖥️ **Información del Servidor**
```bash
# Direcciones IP (autodetectadas por install.sh)
SERVER_IPV4=123.45.67.89
SERVER_IPV6=2001:db8::1
SERVER_IP=123.45.67.89
```

### 🔌 **Configuración API**
```bash
# FastAPI Backend
API_HOST=0.0.0.0          # 0.0.0.0 para acceso público
API_PORT=8000              # Puerto de la API

# CORS (Configurar en producción)
CORS_ORIGINS=https://tudominio.com,https://app.tudominio.com
```

---

## 🔌 Protocolos VPN

### 🛡️ **WireGuard Configuration**
```bash
# Configuración de red interna
WG_INTERFACE=wg0                           # Nombre de interfaz
WG_SERVER_IPV4=10.88.88.1                 # IP interna servidor
WG_SERVER_IPV6=fd42:42:42::1              # IPv6 interna servidor
WG_SERVER_PORT=51820                       # Puerto UDP

# Claves (generadas automáticamente por install.sh)
WG_SERVER_PUBKEY=CLAVE_PUBLICA_AQUI
WG_SERVER_PRIVKEY=CLAVE_PRIVADA_AQUI

# Configuración de clientes
WG_ALLOWED_IPS=0.0.0.0/0,::/0            # IPs permitidas
WG_CLIENT_DNS_1=1.1.1.1                   # DNS primario
WG_CLIENT_DNS_2=1.0.0.1                   # DNS secundario

# Rutas y archivos
WG_PATH=/etc/wireguard                     # Directorio de configuración
WG_ENDPOINT=123.45.67.89:51820            # Endpoint público
```

### 🌐 **Outline Configuration**
```bash
# API de Outline
OUTLINE_API_URL=https://123.45.67.89:8080/SECRET_KEY
OUTLINE_CERT_SHA256=CERTIFICADO_SHA256_AQUI
OUTLINE_API_PORT=8080                      # Puerto API
OUTLINE_KEYS_PORT=443                      # Puerto para clientes

# Configuración de servidor
OUTLINE_SERVER_IP=123.45.67.89             # IP pública
OUTLINE_DASHBOARD_URL=https://123.45.67.89:8081  # Dashboard admin
```

---

## 🗄️ Base de Datos

### 🌐 **Supabase Configuration**
```bash
# URLs y claves de Supabase
SUPABASE_URL=https://abcdefg.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=tu-jwt-secret-aqui

# URL de conexión PostgreSQL
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.abcdefg.supabase.co:5432/postgres
```

### 🔧 **Pool de Conexiones**
```bash
# Configuración de base de datos
DB_POOL_SIZE=10              # Tamaño del pool de conexiones
DB_TIMEOUT=30                # Timeout en segundos
```

---

## 💰 Sistema de Pagos

### 🎯 **Planes y Límites**
```bash
# Plan Gratuito
FREE_PLAN_MAX_KEYS=2                     # Máximo de claves
FREE_PLAN_DATA_LIMIT_GB=10               # Límite de datos en GB

# Plan VIP
VIP_PLAN_MAX_KEYS=10                     # Máximo de claves VIP
VIP_PLAN_DATA_LIMIT_GB=50                # Límite de datos VIP
VIP_PLAN_COST_STARS=10                   # Costo en Telegram Stars
```

### 💸 **Sistema de Referidos**
```bash
# Comisiones
REFERRAL_COMMISSION_PERCENT=10           # Porcentaje de comisión

# Ciclos de facturación
BILLING_CYCLE_DAYS=30                    # Días del ciclo
KEY_CLEANUP_DAYS=90                      # Días para limpiar claves inactivas
```

### 💰 **Depósitos Mínimos**
```bash
# Requisitos para eliminar claves
MIN_DEPOSIT_FOR_DELETE=1                 # Depósito mínimo requerido
```

---

## 🔒 Seguridad

### 🔐 **Claves y Tokens**
```bash
# Clave secreta para JWT y encriptación
SECRET_KEY=GENERADA_CON_OPENSSL_RAND_HEX_32
ALGORITHM=HS256                           # Algoritmo de firma JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30           # Expiración de tokens
```

### 🛡️ **Whitelist de IPs (Opcional)**
```bash
# Habilitar whitelist para API
ENABLE_IP_WHITELIST=false                # true para activar
API_ALLOWED_IPS=192.168.1.1,10.0.0.1    # IPs permitidas
```

---

## 📊 Logging y Monitoreo

### 📝 **Configuración de Logs**
```bash
# Nivel de logging
LOG_LEVEL=INFO                            # DEBUG | INFO | WARNING | ERROR | CRITICAL

# Archivo de logs
LOG_FILE_PATH=./logs/vpn_manager.log      # Ruta del archivo de logs
```

### 📈 **Métricas y Monitorización**
```bash
# Habilitar métricas
ENABLE_METRICS=false                      # true para Prometheus, etc.

# Sentry para tracking de errores (opcional)
SENTRY_DSN=https://your-sentry-dsn
```

---

## 🎮 Gamificación

### 🎯 **Configuración de Juegos**
```bash
# Configuración del sistema Play & Earn
# (Estos valores se configuran en la base de datos)
# - Probabilidades de ganar
# - Premios en estrellas
# - Límites diarios
# - Tipos de juegos disponibles
```

---

## 🔧 Configuración Avanzada

### 📁 **Rutas y Directorios**
```bash
# Directorios del sistema
VPN_TEMPLATES_PATH=./templates            # Plantillas de configuración
TEMP_PATH=./temp                         # Directorio temporal
QR_CODE_PATH=./static/qr_codes           # Códigos QR generados
CLIENT_CONFIGS_PATH=./static/configs      # Configuraciones de clientes
```

### ⏰ **Tareas Automatizadas**
```bash
# Configuración de jobs (en main.py)
# - Limpieza de tickets: cada 1 hora
# - Sincronización de uso: cada 30 minutos  
# - Limpieza de claves: cada 1 hora
```

### 🔄 **Validaciones Automáticas**
El sistema valida automáticamente:

- **WG_ENDPOINT**: Se construye automáticamente si no existe
- **OUTLINE_SERVER_IP**: Se autocompleta con SERVER_IP
- **ADMIN_ID**: Se agrega automáticamente a AUTHORIZED_USERS
- **Directorios**: Se crean automáticamente si no existen

---

## 📋 Validación de Configuración

### ✅ **Verificación Inicial**
```bash
# Verificar configuración
python -c "
from config import settings
print('✅ Configuración válida')
print(f'📦 Proyecto: {settings.PROJECT_NAME}')
print(f'🌍 Entorno: {settings.APP_ENV}')
print(f'🛡️ VPNs: {settings.get_vpn_protocols()}')
"
```

### 🔍 **Diagnóstico Completo**
```bash
# Script de diagnóstico
python -c "
from config import settings
import sys

# Verificar configuración esencial
required_vars = ['TELEGRAM_TOKEN', 'ADMIN_ID', 'DATABASE_URL']
missing = [var for var in required_vars if not getattr(settings, var, None)]

if missing:
    print(f'❌ Variables faltantes: {missing}')
    sys.exit(1)
else:
    print('✅ Configuración completa')
    
# Verificar protocolos VPN
protocols = settings.get_vpn_protocols()
print(f'🛡️ Protocolos disponibles: {protocols}')

# Verificar entorno
if settings.is_production:
    print('🔒 Modo producción activado')
else:
    print('⚠️ Modo desarrollo')
"
```

---

## 🔄 Actualización de Configuración

### 📝 **Modificar Variables**
1. **Edita el archivo `.env`**
2. **Reinicia el bot**:
   ```bash
   # Si usas systemd
   sudo systemctl restart usipipo-bot
   
   # O manualmente
   python main.py
   ```

### 🔧 **Recargar Configuración**
Algunos cambios requieren reinicio completo:

- **TELEGRAM_TOKEN**: Requiere reinicio
- **DATABASE_URL**: Requiere reinicio
- **VPN settings**: Requiere reinicio de servicios VPN
- **API settings**: Requiere reinicio del servidor API

---

## 🚨 Configuración de Producción

### 🔒 **Seguridad Adicional**
```bash
# En producción, asegúrate de:
APP_ENV=production
CORS_ORIGINS=https://tudominio.com  # No usar "*"
ENABLE_IP_WHITELIST=true            # Si aplica
LOG_LEVEL=INFO                      # No DEBUG en producción
```

### 🔐 **Variables Secretas**
```bash
# Generar claves seguras:
SECRET_KEY=$(openssl rand -hex 32)
WG_SERVER_PRIVKEY=$(wg genkey)
```

### 🌐 **Dominios Personalizados**
```bash
# Configurar dominios si los tienes:
CORS_ORIGINS=https://vpn.tudominio.com,https://app.tudominio.com
TELEGRAM_WEBHOOK_URL=https://vpn.tudominio.com/webhook/telegram
```

---

## 📞 Ayuda y Soporte

### 🐛 **Problemas Comunes**
- **Token inválido**: Verifica TELEGRAM_TOKEN con @BotFather
- **Error de BD**: Confirma DATABASE_URL y credenciales de Supabase
- **VPN no funciona**: Revisa configuración de firewall y puertos
- **Rate limit**: Ajusta TELEGRAM_RATE_LIMIT si es necesario

### 📖 **Recursos Adicionales**
- [📋 Instalación Completa](./INSTALL.md)
- [🔧 Administración](./ADMIN.md)
- [🐛 Troubleshooting](./TROUBLESHOOTING.md)
- [📐 Arquitectura](./ARCHITECTURE.md)

---

<div align="center">

**⚙️ Configuración Completa**  
*Toda la flexibilidad de uSipipo a tu disposición*

[📖 Documentación](../docs/) • [🚀 Instalación](./INSTALL.md) • [💬 Soporte](https://discord.gg/tu-invite)

Made with ❤️ by uSipipo Team

</div>
