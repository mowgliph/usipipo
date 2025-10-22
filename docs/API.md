# 📡 API de uSipipo para Desarrolladores

## Descripción General

uSipipo proporciona una API REST completa para integraciones externas, permitiendo a desarrolladores interactuar programáticamente con el sistema de gestión de VPN, proxies y usuarios.

## Autenticación

La API utiliza autenticación JWT (JSON Web Tokens). Para obtener un token:

### Endpoint de Autenticación
```
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "telegram_id": 123456789,
  "api_key": "your_api_key"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Uso del Token
Incluye el token en el header `Authorization`:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Endpoints Principales

### 👥 Gestión de Usuarios

#### Listar Usuarios
```
GET /api/v1/users
```

**Parámetros de Query:**
- `limit`: Número máximo de resultados (default: 50)
- `offset`: Desplazamiento para paginación (default: 0)
- `status`: Filtrar por estado (active, inactive)
- `role`: Filtrar por rol (user, admin, superadmin)

**Response:**
```json
{
  "users": [
    {
      "id": "uuid-string",
      "telegram_id": 123456789,
      "username": "usuario",
      "first_name": "Juan",
      "last_name": "Pérez",
      "is_admin": false,
      "is_active": true,
      "created_at": "2025-10-22T12:00:00Z",
      "last_login_at": "2025-10-22T15:30:00Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

#### Obtener Usuario por ID
```
GET /api/v1/users/{user_id}
```

#### Actualizar Usuario
```
PUT /api/v1/users/{user_id}
```

**Request Body:**
```json
{
  "is_active": true,
  "is_admin": false
}
```

### 🔐 Gestión de VPN

#### Listar Configuraciones VPN
```
GET /api/v1/vpn/configs
```

**Parámetros de Query:**
- `user_id`: Filtrar por usuario
- `vpn_type`: Filtrar por tipo (wireguard, outline)
- `status`: Filtrar por estado (active, expired, revoked)
- `is_trial`: Filtrar trials (true/false)

**Response:**
```json
{
  "configs": [
    {
      "id": "uuid-string",
      "user_id": "uuid-string",
      "vpn_type": "wireguard",
      "config_name": "Mi VPN",
      "status": "active",
      "created_at": "2025-10-22T12:00:00Z",
      "expires_at": "2025-11-22T12:00:00Z",
      "is_trial": false,
      "bandwidth_used_mb": 150.5
    }
  ],
  "total": 25
}
```

#### Crear Configuración VPN
```
POST /api/v1/vpn/create
```

**Request Body:**
```json
{
  "user_id": "uuid-string",
  "vpn_type": "wireguard",
  "is_trial": false,
  "months": 3,
  "config_name": "VPN Premium"
}
```

**Response:**
```json
{
  "config_id": "uuid-string",
  "config_data": {
    "server_address": "vpn.example.com",
    "server_port": 51820,
    "private_key": "private_key_here",
    "public_key": "public_key_here",
    "allowed_ips": "0.0.0.0/0",
    "endpoint": "vpn.example.com:51820"
  },
  "qr_code_url": "https://api.qrserver.com/v1/create-qr-code/...",
  "expires_at": "2025-11-22T12:00:00Z"
}
```

#### Revocar Configuración VPN
```
DELETE /api/v1/vpn/configs/{config_id}
```

### 🌐 Gestión de Proxies MTProto

#### Listar Proxies MTProto
```
GET /api/v1/proxy/mtproto
```

**Response:**
```json
{
  "proxies": [
    {
      "id": "uuid-string",
      "user_id": "uuid-string",
      "host": "proxy.example.com",
      "port": 443,
      "secret": "dd1234567890abcdef",
      "tag": "@MTProxybot_tag",
      "status": "active",
      "created_at": "2025-10-22T12:00:00Z",
      "expires_at": "2025-11-22T12:00:00Z"
    }
  ],
  "total": 10
}
```

#### Crear Proxy MTProto
```
POST /api/v1/proxy/mtproto
```

**Request Body:**
```json
{
  "user_id": "uuid-string",
  "host": "proxy.example.com",
  "port": 443
}
```

### 🔍 Gestión de Proxies Shadowmere

#### Listar Proxies Shadowmere
```
GET /api/v1/proxy/shadowmere
```

**Parámetros de Query:**
- `proxy_type`: Filtrar por tipo (SOCKS5, HTTP, HTTPS)
- `country`: Filtrar por país
- `is_working`: Filtrar por estado (true/false)
- `max_response_time`: Tiempo máximo de respuesta en ms

**Response:**
```json
{
  "proxies": [
    {
      "id": 123,
      "proxy_address": "192.168.1.1:8080",
      "proxy_type": "HTTP",
      "country": "US",
      "is_working": true,
      "response_time": 150.5,
      "last_checked": "2025-10-22T15:00:00Z",
      "detection_date": "2025-10-20T10:00:00Z"
    }
  ],
  "total": 5000
}
```

#### Verificar Proxy
```
POST /api/v1/proxy/shadowmere/{proxy_id}/check
```

### 💰 Gestión de Pagos

#### Listar Pagos
```
GET /api/v1/payments
```

**Parámetros de Query:**
- `user_id`: Filtrar por usuario
- `status`: Filtrar por estado (pending, completed, failed)
- `payment_method`: Filtrar por método (stars, qvapay)

**Response:**
```json
{
  "payments": [
    {
      "id": "uuid-string",
      "user_id": "uuid-string",
      "amount_usd": 5.00,
      "amount_stars": 500,
      "currency": "XTR",
      "status": "completed",
      "vpn_type": "wireguard",
      "months": 3,
      "payment_method": "stars",
      "created_at": "2025-10-22T12:00:00Z"
    }
  ],
  "total": 45
}
```

#### Webhook de Pagos QvaPay
```
POST /api/v1/payments/webhook/qvapay
```

**Headers:**
```
X-QvaPay-Signature: signature_here
Content-Type: application/json
```

**Request Body:**
```json
{
  "transaction_id": "qva_tx_123",
  "amount": 5.00,
  "currency": "USD",
  "status": "completed",
  "user_id": "uuid-string",
  "metadata": {
    "vpn_type": "wireguard",
    "months": 3
  }
}
```

### 📊 Estadísticas y Monitoreo

#### Estadísticas Generales
```
GET /api/v1/stats/overview
```

**Response:**
```json
{
  "users": {
    "total": 1500,
    "active_today": 450,
    "new_this_month": 120
  },
  "vpn": {
    "total_configs": 1200,
    "active_configs": 980,
    "trial_configs": 320,
    "paid_configs": 660
  },
  "payments": {
    "total_revenue_usd": 2500.00,
    "total_revenue_stars": 250000,
    "this_month_usd": 450.00
  },
  "system": {
    "uptime": "15 days, 8 hours",
    "cpu_usage": 45.2,
    "memory_usage": 62.1,
    "disk_usage": 23.5
  }
}
```

#### Logs de Auditoría
```
GET /api/v1/audit/logs
```

**Parámetros de Query:**
- `user_id`: Filtrar por usuario
- `action`: Filtrar por acción
- `start_date`: Fecha de inicio (ISO 8601)
- `end_date`: Fecha de fin (ISO 8601)
- `limit`: Número máximo de resultados

**Response:**
```json
{
  "logs": [
    {
      "id": "uuid-string",
      "user_id": "uuid-string",
      "action": "vpn_config_created",
      "details": "Created WireGuard config for user",
      "created_at": "2025-10-22T12:00:00Z"
    }
  ],
  "total": 5000
}
```

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| 200 | OK - Operación exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Token inválido o expirado |
| 403 | Forbidden - Permisos insuficientes |
| 404 | Not Found - Recurso no encontrado |
| 409 | Conflict - Conflicto con estado actual |
| 422 | Unprocessable Entity - Validación fallida |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Error del servidor |

## Rate Limiting

La API implementa rate limiting para prevenir abuso:

- **General**: 1000 requests por hora por IP
- **Autenticación**: 10 requests por minuto por IP
- **Creación de recursos**: 50 requests por hora por usuario
- **Listados**: 500 requests por hora por usuario

## Ejemplos de Integración

### Python - Crear Configuración VPN
```python
import requests

# Autenticación
auth_response = requests.post('https://api.usipipo.com/v1/auth/login', json={
    'telegram_id': 123456789,
    'api_key': 'your_api_key'
})
token = auth_response.json()['access_token']

# Headers para requests autenticados
headers = {'Authorization': f'Bearer {token}'}

# Crear configuración VPN
vpn_response = requests.post('https://api.usipipo.com/v1/vpn/create',
    headers=headers,
    json={
        'user_id': 'user-uuid',
        'vpn_type': 'wireguard',
        'is_trial': True
    }
)

config_data = vpn_response.json()
print(f"Config creada: {config_data['config_id']}")
```

### JavaScript/Node.js - Listar Usuarios
```javascript
const axios = require('axios');

// Login
const loginResponse = await axios.post('https://api.usipipo.com/v1/auth/login', {
    telegram_id: 123456789,
    api_key: 'your_api_key'
});

const token = loginResponse.data.access_token;
const headers = { Authorization: `Bearer ${token}` };

// Listar usuarios
const usersResponse = await axios.get('https://api.usipipo.com/v1/users', {
    headers,
    params: { limit: 10, status: 'active' }
});

console.log(`Total usuarios: ${usersResponse.data.total}`);
```

## Webhooks

### Configuración de Webhooks

Para configurar webhooks, contacta al administrador del sistema. Los webhooks pueden configurarse para:

- Notificaciones de pagos completados
- Alertas de sistema
- Eventos de usuario
- Cambios en configuraciones VPN

### Seguridad de Webhooks

Los webhooks incluyen firma HMAC-SHA256 para verificación:

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)
```

## Versionado

La API utiliza versionado en la URL:
- `v1`: Versión actual (estable)
- Futuras versiones mantendrán compatibilidad hacia atrás

## Soporte

Para soporte técnico de la API:
- Email: api-support@usipipo.com
- Documentación: https://docs.usipipo.com/api
- Status Page: https://status.usipipo.com

---

**Última actualización: Octubre 2025**