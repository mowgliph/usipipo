# 🤖 Comandos del Bot - uSipipo VPN Manager

> **Guía completa de comandos y funcionalidades del bot**  
*Todos los comandos disponibles para usuarios y administradores*

## 📋 Tabla de Contenidos

1. [🚀 Comandos Principales](#-comandos-principales)
2. [👤 Comandos de Usuario](#-comandos-de-usuario)
3. [👑 Comandos de Administración](#-comandos-de-administración)
4. [🔌 Gestión de VPN](#-gestión-de-vpn)
5. [💰 Comandos de Pagos](#-comandos-de-pagos)
6. [🎮 Comandos de Juegos](#-comandos-de-juegos)
7. [📞 Comandos de Soporte](#-comandos-de-soporte)
8. [⚙️ Comandos de Configuración](#️-comandos-de-configuración)

---

## 🚀 Comandos Principales

### 📋 **Comandos Básicos**

#### `/start`
**Descripción**: Inicia el bot y muestra el menú principal
**Uso**: `/start`
**Ejemplo**:
```
/start
```
**Respuesta esperada**:
```
🛡️ uSipipo VPN Manager

¡Bienvenido! 🎉

Soy tu asistente personal para gestionar claves VPN de forma segura y sencilla.

👤 Usuario: Juan Pérez
🆔 ID: 123456789
👑 Plan: Gratis
🔐 Claves: 1/2

📋 Menú Principal:
🛡️ Mis Llaves    ➕ Crear Nueva
📊 Estado        💰 Operaciones
⚙️ Ayuda
```

#### `/help`
**Descripción**: Muestra ayuda y comandos disponibles
**Uso**: `/help` o `/help <comando>`
**Ejemplos**:
```
/help              # Muestra todos los comandos
/help start         # Ayuda específica del comando start
/help admin        # Ayuda de comandos de admin
```

#### `/status`
**Descripción**: Muestra estado general del sistema
**Uso**: `/status`
**Ejemplo**:
```
/status
```
**Respuesta esperada**:
```
📊 Estado del Sistema

🤖 Bot: 🟢 En línea
🛡️ WireGuard: 🟢 Activo (15 claves)
🌐 Outline: 🟢 Activo (23 claves)
🗄️ Base de datos: 🟢 Conectada
📈 Uso: 2.3 TB hoy
👥 Usuarios: 1,247 activos
```

---

## 👤 Comandos de Usuario

### 🛡️ **Gestión de Claves**

#### `/keys` o "🛡️ Mis Llaves"
**Descripción**: Muestra todas las claves VPN del usuario
**Uso**: `/keys` o presionar el botón "🛡️ Mis Llaves"
**Ejemplo**:
```
/keys
```
**Respuesta esperada**:
```
🛡️ Mis Claves VPN

🔑 Claves Activas: 2/2

🟢 mi_wg_key - WireGuard
📊 Datos usados: 1.2 GB / 10 GB
🕐 Creada: 2024-01-10
⏰ Expira: 2024-02-10

🟢 mi_ol_key - Outline
📊 Datos usados: 0.8 GB / 10 GB  
🕐 Creada: 2024-01-12
⏰ Expira: 2024-02-12

🗑️ [Eliminar] 🔄 [Renovar] 📋 [Configuración]
```

#### `/create` o "➕ Crear Nueva"
**Descripción**: Inicia el proceso de creación de una nueva clave VPN
**Uso**: `/create` o presionar "➕ Crear Nueva"
**Proceso**:
1. **Seleccionar protocolo**: WireGuard u Outline
2. **Nombre de clave**: Personalizar (opcional)
3. **Confirmación**: Crear la clave
4. **Resultado**: QR y configuración

**Ejemplo**:
```
/create
```
**Proceso interactivo**:
```
🔌 Elige el protocolo VPN:

🛡️ WireGuard
   • Alto rendimiento
   • Configuración sencilla
   • Compatible con todos los dispositivos

🌐 Outline (Shadowsocks)
   • Fácil de usar
   • Clientes multiplataforma
   • Ideal para principiantes

🔘 [WireGuard]    🔘 [Outline]
```

#### `/delete <key_id>`
**Descripción**: Elimina una clave VPN específica
**Uso**: `/delete <key_id>`
**Parámetros**:
- `key_id`: ID de la clave a eliminar
**Ejemplo**:
```
/delete wg_123456
```
**Confirmación requerida**:
```
⚠️ Confirmar Eliminación

¿Estás seguro de eliminar esta clave?

🔑 Clave: wg_123456
📊 Datos usados: 1.2 GB
⏰ Expira: 2024-02-10

⚠️ Esta acción no se puede deshacer

✅ [Sí, eliminar]    ❌ [Cancelar]
```

---

## 👑 Comandos de Administración

### 🔧 **Panel de Administración**

#### `/admin` o "🔧 Admin"
**Descripción**: Accede al panel de administración (solo admin)
**Uso**: `/admin` o botón "🔧 Admin" (solo visible para ADMIN_ID)
**Requisitos**: Ser el administrador configurado
**Ejemplo**:
```
/admin
```
**Panel de administración**:
```
🔧 Panel de Administración

👥 Ver Usuarios    🔐 Ver Claves
🖥️ Servidores     📊 Estadísticas
🎫 Soporte        📢 Broadcast
```

#### `/admin_users`
**Descripción**: Muestra lista completa de usuarios
**Uso**: `/admin_users`
**Ejemplo**:
```
/admin_users
```
**Respuesta esperada**:
```
👥 Usuarios Registrados (1,247 total)

🟢 Juan Pérez (@juanperez) - VIP - 3 claves - 25.3 GB
🟢 María García (@mariagarcia) - Gratis - 2 claves - 8.1 GB
🔴 Carlos López (@carloslopez) - Gratis - 0 claves - 0.0 GB
...
```

#### `/admin_keys`
**Descripción**: Muestra todas las claves del sistema
**Uso**: `/admin_keys`
**Ejemplo**:
```
/admin_keys
```
**Respuesta esperada**:
```
🔐 Claves VPN Registradas

🛡️ WireGuard: 15 claves
🌐 Outline: 23 claves

🟢 user1_wg - Juan Pérez - Activa - 2.5 GB
🟢 user2_ol - María García - Activa - 1.8 GB
🔴 user3_wg - Carlos López - Inactiva - 0.0 GB
...
```

#### `/admin_delete <key_id>`
**Descripción**: Elimina cualquier clave del sistema (admin)
**Uso**: `/admin_delete <key_id>`
**Ejemplo**:
```
/admin_delete user3_wg
```

#### `/admin_stats`
**Descripción**: Muestra estadísticas completas del sistema
**Uso**: `/admin_stats`
**Ejemplo**:
```
/admin_stats
```
**Estadísticas del sistema**:
```
📊 Estadísticas Globales

👥 Usuarios totales: 1,247
🆔 Nuevos hoy: +23
👑 Usuarios VIP: 156 (12.5%)
🔐 Claves activas: 234/389
📊 Tráfico hoy: 2.3 TB
💰 Ingresos mes: 1,250 estrellas
```

#### `/logs`
**Descripción**: Muestra las últimas líneas del log del sistema (solo admin)
**Uso**: `/logs`
**Requisitos**: Ser el administrador configurado
**Ejemplo**:
```
/logs
```
**Respuesta esperada**:
```
📋 Últimas Líneas de Log

```
2024-01-15 10:30:15 | INFO     | main:main - 🚀 Iniciando uSipipo VPN Manager Bot...
2024-01-15 10:30:16 | INFO     | main:main - ✅ Contenedor de dependencias configurado correctamente.
2024-01-15 10:30:16 | INFO     | main:main - 🌊 Servicio de IA Sip inicializado correctamente.
2024-01-15 10:30:17 | INFO     | main:main - 🤖 Bot en línea y escuchando mensajes...
2024-01-15 10:30:20 | INFO     | admin_service:get_dashboard_stats - 📊 Obteniendo estadísticas del dashboard
```

📅 *Extraído: 2024-01-15 10:35:22*
```

---

## 🔌 Gestión de VPN

### 📊 **Estado de Conexión**

#### `/my_status`
**Descripción**: Muestra estado personal del usuario
**Uso**: `/my_status`
**Ejemplo**:
```
/my_status
```
**Respuesta esperada**:
```
📊 Mi Estado

👤 Usuario: Juan Pérez (@juanperez)
🆔 ID: 123456789
👑 Plan: Gratis
🔐 Claves: 2/2 (ambas activas)
💰 Balance: 0 estrellas
📊 Datos totales: 2.0 GB este mes
🕐 Registro: 2024-01-05
```

#### `/usage`
**Descripción**: Muestra uso detallado de datos
**Uso**: `/usage` o `/usage <key_id>`
**Ejemplos**:
```
/usage           # Uso general de todas las claves
/usage wg_123   # Uso de una clave específica
```

**Respuesta esperada**:
```
📊 Uso de Datos

📈 Este mes: 2.0 GB / 10 GB (20%)
📅 Hoy: 125 MB
📊 Promedio diario: 67 MB

🔑 Por clave:
🟢 mi_wg_key: 1.2 GB
🟢 mi_ol_key: 0.8 GB
```

---

## 💰 Comandos de Pagos

### 💎 **Gestión de Balance**

#### `/balance`
**Descripción**: Muestra balance y transacciones
**Uso**: `/balance`
**Ejemplo**:
```
/balance
```
**Respuesta esperada**:
```
💰 Mi Balance

⭐ Balance actual: 150 estrellas
💎 VIP hasta: 2024-12-31

📋 Historial reciente:
➕ +50 estrellas (depósito) - 2024-01-10
➖ -10 estrellas (VIP mensual) - 2024-01-01
➕ +25 estrellas (referido María) - 2023-12-28
```

#### `/vip`
**Descripción**: Muestra información y opciones del plan VIP
**Uso**: `/vip`
**Ejemplo**:
```
/vip
```
**Respuesta esperada**:
```
👑 Plan VIP

🎟 Beneficios VIP:
• 10 claves (vs 2 gratuitas)
• 50 GB datos (vs 10 GB gratuitos)
• Soporte prioritario
• Acceso a servidores exclusivos

💰 Precios:
• 1 mes: 10 estrellas
• 3 meses: 27 estrellas (-10% descuento)
• 6 meses: 50 estrellas (-17% descuento)
• 12 meses: 90 estrellas (-25% descuento)

🛒 [Comprar 1 mes] 🛒 [Comprar 3 meses]
🛒 [Comprar 6 meses] 🛒 [Comprar 12 meses]
```

#### `/deposit`
**Descripción**: Muestra opciones para depositar estrellas
**Uso**: `/deposit`
**Ejemplo**:
```
/deposit
```

---

## 🎮 Comandos de Juegos

### 🎲 **Play & Earn**

#### `/game` o "🎮 Juga y Gana"
**Descripción**: Accede al sistema de juegos para ganar estrellas
**Uso**: `/game` o botón "🎮 Juga y Gana"
**Ejemplo**:
```
/game
```
**Juegos disponibles**:
```
🎮 Juegos Play & Earn

🎲 Ruleta de la Suerte
   • Gana hasta 100 estrellas
   • 3 intentos gratuitos diarios
   • 🎲 [Jugar]

🎯 Tiro al Blanco
   • Precisión = más estrellas
   • 5 intentos gratuitos diarios
   • 🎯 [Jugar]

🧩 Adivina el Número
   • Premio acumulado progresivo
   • 1 intento gratuito diario
   • 🧩 [Jugar]

📊 Mis Estadísticas:
🏆 Nivel: 5
⭐ Estrellas ganadas: 1,250
🎮 Juegos jugados: 347
🏅 Mejor racha: 12 victorias
```

#### `/game_stats`
**Descripción**: Muestra estadísticas de juegos
**Uso**: `/game_stats`
**Ejemplo**:
```
/game_stats
```

---

## 📞 Comandos de Soporte

### 💬 **Sistema de Soporte**

#### `/support` o "🎫 Soporte"
**Descripción**: Inicia un ticket de soporte
**Uso**: `/support` o botón "🎫 Soporte"
**Ejemplo**:
```
/support
```
**Proceso de soporte**:
```
🎫 Soporte Técnico

¿En qué podemos ayudarte?

📝 Describe tu problema:
• No puedo conectar
• Error en configuración
• Problema con pago
• Otro problema

💬 [No puedo conectar] 💬 [Error configuración]
💬 [Problema pago] 💬 [Otro problema]
```

#### `/sipai` o "🌊 Sip"
**Descripción**: Inicia una conversación con el asistente de IA Sip para obtener ayuda inmediata con problemas de VPN, configuración y seguridad
**Uso**: `/sipai` o botón "🌊 Sip"
**Ejemplo**:
```
/sipai
```
**Respuesta esperada**:
```
🌊 **¡Hola! Soy Sip, tu asistente especializado de uSipipo** 🌊

Estoy aquí para ayudarte con todo lo relacionado con VPN, seguridad y privacidad.

🤖 **¿En qué puedo ayudarte?**

🔌 **Conexiones VPN:**
• Problemas para conectar
• Configuración en diferentes dispositivos
• Solución de errores comunes

🔒 **Seguridad y Privacidad:**
• Cifrado de datos
• Protección en redes públicas
• Mejores prácticas de seguridad

💡 **Escribe tu pregunta** y te ayudaré de inmediato.

🔴 *Para finalizar el chat, escribe "Finalizar"*
```

**Flujo de conversación**:
1. Usuario envía `/sipai`
2. Sip responde con mensaje de bienvenida
3. Usuario hace preguntas sobre VPN/configuración
4. Sip responde usando IA (Groq)
5. Si el problema requiere atención humana, Sip escala automáticamente a ticket

**Comandos dentro del chat**:
- `Finalizar` - Termina la conversación
- `Salir` - Termina la conversación
- `Exit` - Termina la conversación

**Escalado automático**: Sip detectará automáticamente cuando necesites hablar con un humano y creará un ticket de soporte.

#### `/ticket <mensaje>`
**Descripción**: Crea un ticket con mensaje específico
**Uso**: `/ticket <tu mensaje de soporte>`
**Ejemplo**:
```
/ticket No puedo conectar con mi clave WireGuard, muestra error de handshake
```

#### `/tickets`
**Descripción**: Muestra tus tickets de soporte
**Uso**: `/tickets`
**Ejemplo**:
```
/tickets
```
**Respuesta esperada**:
```
🎫 Mis Tickets de Soporte

#T003 - "No puedo conectar" - 🟢 Cerrado - 2024-01-10
#T002 - "Error configuración" - 🟡 En progreso - 2024-01-12
#T001 - "Renovar clave" - 🔴 Abierto - 2024-01-15
```

---

## ⚙️ Comandos de Configuración

### 🔧 **Configuración Personal**

#### `/settings`
**Descripción**: Muestra configuración personal del usuario
**Uso**: `/settings`
**Ejemplo**:
```
/settings
```
**Respuesta esperada**:
```
⚙️ Mi Configuración

🌍 Idioma: Español
🔔 Notificaciones: Activadas
🕐 Zona horaria: UTC-3
🔐 Clave por defecto: WireGuard
📊 Reportes de uso: Semanales

🔧 [Editar configuración]
```

#### `/language`
**Descripción**: Cambia el idioma del bot
**Uso**: `/language <código>`
**Ejemplos**:
```
/language es    # Español
/language en    # Inglés
/language pt    # Portugués
```

#### `/notifications`
**Descripción**: Gestiona preferencias de notificaciones
**Uso**: `/notifications [on|off]`
**Ejemplos**:
```
/notifications on   # Activar notificaciones
/notifications off  # Desactivar notificaciones
```

---

## 🎯 Comandos Avanzados

### 🔍 **Comandos de Búsqueda**

#### `/search <término>`
**Descripción**: Busca en ayuda y documentación
**Uso**: `/search <término de búsqueda>`
**Ejemplos**:
```
/search configuración
/search error conexión
/search cómo pagar
```

#### `/history`
**Descripción**: Muestra historial de comandos usados
**Uso**: `/history`
**Ejemplo**:
```
/history
```

---

## 📋 Referencia Rápida

### 🚀 **Comandos Esenciales**
| Comando | Descripción | Uso |
|---------|-------------|------|
| `/start` | Inicia el bot | `/start` |
| `/help` | Muestra ayuda | `/help` |
| `/keys` | Mis claves VPN | `/keys` |
| `/create` | Crear nueva clave | `/create` |
| `/status` | Estado del sistema | `/status` |

### 👑 **Comandos de Admin**
| Comando | Descripción | Requiere |
|---------|-------------|----------|
| `/admin` | Panel admin | ✅ Admin |
| `/admin_users` | Lista usuarios | ✅ Admin |
| `/admin_keys` | Lista claves | ✅ Admin |
| `/admin_stats` | Estadísticas | ✅ Admin |
| `/admin_delete` | Eliminar clave | ✅ Admin |
| `/logs` | Ver logs del sistema | ✅ Admin |

### 💰 **Comandos de Pagos**
| Comando | Descripción | Uso |
|---------|-------------|------|
| `/balance` | Mi balance | `/balance` |
| `/vip` | Plan VIP | `/vip` |
| `/deposit` | Depositar | `/deposit` |

### 🎮 **Comandos de Juegos**
| Comando | Descripción | Uso |
|---------|-------------|------|
| `/game` | Juegos disponibles | `/game` |
| `/game_stats` | Estadísticas de juegos | `/game_stats` |

### 📞 **Comandos de Soporte**
| Comando | Descripción | Uso |
|---------|-------------|------|
| `/support` | Ticket de soporte humano | `/support` |
| `/sipai` | Asistente IA Sip | `/sipai` |
| `/ticket <mensaje>` | Crear ticket directo | `/ticket <msg>` |
| `/tickets` | Ver mis tickets | `/tickets` |

---

## 🔧 Atajos y Botones

### 📱 **Botones Interactivos**
El bot también responde a botones del menú principal:

- **"🛡️ Mis Llaves"** = `/keys`
- **"➕ Crear Nueva"** = `/create`
- **"📊 Estado"** = `/status`
- **"💰 Operaciones"** = Abre menú de operaciones
- **"⚙️ Ayuda"** = `/help`
- **"🎮 Juga y Gana"** = `/game`
- **"🎫 Soporte"** = `/support`
- **"🔧 Admin"** = `/admin` (solo admin)

### ⌨️ **Comandos Rápidos**
- **`?`** = `/help`
- **`!status`** = `/status`
- **`!keys`** = `/keys`

---

## 🚨 Códigos de Error

### 📋 **Mensajes de Error Comunes**

| Código | Mensaje | Solución |
|--------|----------|----------|
| `AUTH_REQUIRED` | Autenticación requerida | Usa `/start` primero |
| `KEY_NOT_FOUND` | Clave no encontrada | Verifica el ID de la clave |
| `INSUFFICIENT_BALANCE` | Balance insuficiente | Deposita estrellas |
| `ADMIN_REQUIRED` | Requiere admin | Solo para administradores |
| `RATE_LIMIT` | Demasiadas peticiones | Espera unos segundos |

---

## 📞 Ayuda Adicional

### 🔍 **Obtener Ayuda Específica**
```bash
# Ayuda de un comando específico
/help <comando>

# Ejemplos:
/help create
/help admin
/help vip
```

### 📚 **Documentación Relacionada**
- [👑 Administración](./ADMIN.md) - Guía completa del panel admin
- [⚙️ Configuración](./CONFIGURATION.md) - Todas las opciones
- [🔌 VPN Setup](./VPN_SETUP.md) - Configuración avanzada
- [🐛 Troubleshooting](./TROUBLESHOOTING.md) - Problemas comunes

### 💬 **Soporte en Vivo**
- **📱 Telegram**: @usipipo_support
- **💬 Discord**: [Servidor de ayuda](https://discord.gg/usipipo)
- **📧 Email**: support@usipipo.com

---

<div align="center">

**🤖 Comandos Completos del Bot**  
*Domina todas las funcionalidades de uSipipo*

[📖 Documentación](./README.md) • [👑 Panel Admin](./ADMIN.md) • [💬 Soporte](https://discord.gg/usipipo)

Made with ❤️ by uSipipo Team

</div>
