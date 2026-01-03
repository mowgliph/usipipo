# 👑 Guía de Administración - uSipipo VPN Manager

> **Control total sobre tu sistema VPN**  
*Guía completa del panel de administración*

## 📋 Tabla de Contenidos

1. [🎯 Acceso al Panel](#-acceso-al-panel)
2. [📊 Panel Principal](#-panel-principal)
3. [👥 Gestión de Usuarios](#-gestión-de-usuarios)
4. [🔐 Gestión de Claves VPN](#-gestión-de-claves-vpn)
5. [🖥️ Estado de Servidores](#️-estado-de-servidores)
6. [📈 Estadísticas y Métricas](#-estadísticas-y-métricas)
7. [🎫 Gestión de Soporte](#-gestión-de-soporte)
8. [📢 Broadcast Masivo](#-broadcast-masivo)
9. [🔧 Configuración Avanzada](#-configuración-avanzada)
10. [🚨 Alertas y Notificaciones](#-alertas-y-notificaciones)

---

## 🎯 Acceso al Panel

### 🔐 **Requisitos de Acceso**
- **ADMIN_ID**: Tu ID de Telegram debe estar configurado como administrador
- **Bot Iniciado**: El bot debe estar corriendo y accesible
- **Permisos**: Acceso completo a funciones de administración

### 🤖 **Acceder al Panel**
1. **Abre tu bot** en Telegram
2. **Envía `/start`** si no lo has hecho
3. **Busca el botón** "🔧 Admin" (solo visible para administradores)
4. **Presiona el botón** para acceder al panel

```
🔧 Panel de Administración

👥 Ver Usuarios    🔐 Ver Claves
🖥️ Estado Servidores  📊 Estadísticas
```

---

## 📊 Panel Principal

### 🎛️ **Menú Principal de Administración**

El panel principal te da acceso a todas las funciones administrativas:

#### 👥 **Ver Usuarios**
- Lista completa de todos los usuarios registrados
- Información detallada: VIP, claves, balance, actividad
- Estadísticas de uso por usuario
- Acciones rápidas de gestión

#### 🔐 **Ver Claves**
- Todas las claves VPN del sistema
- Filtrado por protocolo (WireGuard/Outline)
- Estado: activas/inactivas, datos usados
- Eliminación directa desde el panel

#### 🖥️ **Estado Servidores**
- Monitoreo en tiempo real de WireGuard y Outline
- Métricas de salud: claves activas, errores, versión
- Diagnóstico automático de problemas
- Reinicio de servicios si es necesario

#### 📊 **Estadísticas**
- Métricas globales del sistema
- Gráficos de uso y crecimiento
- Análisis de rendimiento
- Exportación de datos

---

## 👥 Gestión de Usuarios

### 📋 **Vista de Usuarios**

#### 📊 **Información de Usuario**
```
👤 Juan Pérez (@juanperez)
🆔 ID: 123456789
👑 Plan: VIP (expira: 2024-12-31)
🔐 Claves: 3/10 (2 activas, 1 inactiva)
💰 Balance: 150 estrellas
📊 Datos usados: 25.3 GB este mes
🕐 Última actividad: 2024-01-15 14:30
```

#### 🔍 **Filtros y Búsqueda**
- **Búsqueda por nombre** o username
- **Filtro por plan** (Gratis/VIP)
- **Filtro por estado** (Activo/Inactivo)
- **Ordenamiento** por fecha de registro o actividad

#### ⚡ **Acciones Rápidas**
- **Ver detalles** completos del usuario
- **Gestionar claves** del usuario
- **Modificar plan** (Gratis ↔ VIP)
- **Enviar mensaje** directo
- **Suspender usuario** (si es necesario)

### 📝 **Gestión Detallada**

#### 👑 **Planes de Usuario**
- **Plan Gratis**: 2 claves, 10 GB/mes
- **Plan VIP**: 10 claves, 50 GB/mes
- **Planes Personalizados**: Configuración flexible

#### 💰 **Balance y Transacciones**
- **Historial completo** de transacciones
- **Depósitos** y retiros de estrellas
- **Comisiones** de referidos
- **Reembolsos** y ajustes

---

## 🔐 Gestión de Claves VPN

### 📋 **Vista de Claves**

#### 🔐 **Lista de Claves**
```
🔐 Claves VPN Registradas

🔐 WireGuard: 15 claves
🔒 Outline: 23 claves

🟢 user1_wg - Juan Pérez - Activa - 2.5 GB
🟢 user2_ol - María García - Activa - 1.8 GB  
🔴 user3_wg - Carlos López - Inactiva - 0.0 GB
🟢 user4_ol - Ana Martínez - Activa - 5.2 GB
```

#### 🏷️ **Información de Clave**
- **ID único**: Identificador interno
- **Usuario**: Propietario de la clave
- **Protocolo**: WireGuard u Outline
- **Estado**: Activa/Inactiva/Expirada
- **Datos usados**: Tráfico consumido
- **Fecha creación**: Cuándo se creó
- **Último uso**: Última conexión

### ⚡ **Operaciones con Claves**

#### 🗑️ **Eliminación de Claves**
1. **Seleccionar clave** de la lista
2. **Ver detalles** de configuración
3. **Confirmar eliminación** con advertencias
4. **Ejecución simultánea**:
   - ❌ Eliminar de WireGuard
   - ❌ Eliminar de Outline  
   - ❌ Eliminar de Base de Datos

#### ⚠️ **Confirmación de Eliminación**
```
⚠️ Confirmar Eliminación

🔑 Nombre: user1_wg
👤 Usuario: Juan Pérez
🔒 Tipo: WIREGUARD
📊 Datos usados: 2.5 GB

⚠️ Esta acción:
❌ Eliminará la clave de los servidores VPN
❌ Eliminará la clave de la base de datos
❌ El usuario perderá acceso inmediatamente
❌ No se puede deshacer

✅ Confirmar Eliminación    ❌ Cancelar
```

#### 🔄 **Operaciones Adicionales**
- **Renovar clave**: Extender validez
- **Cambiar protocolo**: Migrar WireGuard ↔ Outline
- **Resetear datos**: Reiniciar contador de uso
- **Suspender temporal**: Desactivar sin eliminar

---

## 🖥️ Estado de Servidores

### 📊 **Monitoreo en Tiempo Real**

#### 🛡️ **WireGuard Status**
```
🟢 WireGuard Server
📊 Claves totales: 15
🟢 Claves activas: 12
🔧 Versión: 1.0.3
❌ Errores: 0
📈 Uso CPU: 15%
💾 Memoria: 2.1GB/4GB
🌐 Red: 125 Mbps ↑ / 340 Mbps ↓
```

#### 🌐 **Outline Status**
```
🟢 Outline Server
📊 Claves totales: 23
🟢 Claves activas: 18
🔧 Versión: shadowbox-8.2.2
❌ Errores: 0
📈 Uso CPU: 8%
💾 Memoria: 512MB/1GB
🌐 Red: 89 Mbps ↑ / 210 Mbps ↓
```

### 🔧 **Gestión de Servicios**

#### ⚡ **Acciones Rápidas**
- **Reiniciar servicio**: WireGuard u Outline
- **Recargar configuración**: Aplicar cambios sin reiniciar
- **Ver logs**: Acceso a logs en tiempo real
- **Diagnosticar**: Ejecutar pruebas de conectividad

#### 📈 **Métricas Detalladas**
- **Rendimiento**: CPU, memoria, disco, red
- **Conexiones**: Concurrentes, totales por día
- **Tráfico**: Subida/bajada por protocolo
- **Errores**: Tipos y frecuencia de problemas

---

## 📈 Estadísticas y Métricas

### 📊 **Dashboard Principal**

#### 🎯 **Métricas Globales**
```
📊 Estadísticas del Sistema

👥 Usuarios totales: 1,247
🆔 Nuevos hoy: +23
👑 Usuarios VIP: 156 (12.5%)
🔐 Claves activas: 234/389
📊 Tráfico hoy: 2.3 TB
💰 Ingresos mes: 1,250 estrellas
```

#### 📈 **Gráficos y Tendencias**
- **Crecimiento de usuarios**: Nuevos registros por día/semana/mes
- **Uso de VPN**: Tráfico consumido por período
- **Adopción de planes**: Gratis vs VIP
- **Actividad del sistema**: Picos de uso y horas pico

### 📋 **Reportes Detallados**

#### 📊 **Reportes Disponibles**
- **Usuarios**: Activos, inactivos, por plan
- **Claves**: Por protocolo, estado, uso
- **Tráfico**: Por usuario, período, protocolo
- **Ingresos**: Por fuente, período, tendencia

#### 📤 **Exportación de Datos**
- **Formatos**: CSV, JSON, PDF
- **Períodos**: Diario, semanal, mensual, personalizado
- **Filtros**: Por usuario, protocolo, estado
- **Automatización**: Reportes programados

---

## 🎫 Gestión de Soporte

### 💬 **Sistema de Tickets**

#### 📋 **Vista de Tickets**
```
🎫 Tickets de Soporte

🔴 Abiertos: 3
🟡 En progreso: 2
🟢 Cerrados: 147

#T001 - Juan Pérez - "No puedo conectar" - Abierto hace 2h
#T002 - María García - "Error configuración" - En progreso hace 1d
#T003 - Carlos López - "Renovar clave" - Cerrado hace 3d
```

#### 🏷️ **Estados de Tickets**
- **🔴 Abierto**: Nuevo ticket sin atender
- **🟡 En progreso**: Ticket siendo atendido
- **🟢 Cerrado**: Ticket resuelto
- **⚫ Cancelado**: Ticket cancelado por usuario

#### ⚡ **Gestión de Tickets**
- **Ver detalles** completos del ticket
- **Responder directamente** al usuario
- **Cambiar estado** manualmente
- **Asignar prioridad** (Baja/Media/Alta)
- **Cierre automático** después de 48h sin respuesta

---

## 📢 Broadcast Masivo

### 📢 **Envío de Mensajes**

#### 📝 **Crear Broadcast**
```
📢 Nuevo Broadcast

📝 Mensaje:
¡Nueva función disponible! 🎉
Ahora puedes disfrutar de conexión más rápida
con nuestros servidores actualizados.

👥 Destinatarios:
○ Todos los usuarios
○ Solo usuarios VIP  
○ Usuarios inactivos (>7 días)
○ Personalizar...

🕐 Programar:
○ Enviar ahora
○ Programar para: [fecha/hora]
```

#### 🎯 **Segmentación de Audiencia**
- **Todos los usuarios**: Mensaje global
- **Por plan**: Gratis o VIP
- **Por actividad**: Activos, inactivos, nuevos
- **Personalizado**: Filtros avanzados
- **Prueba**: Enviar a ti mismo primero

#### 📊 **Estadísticas de Broadcast**
- **Enviados**: Total de mensajes enviados
- **Leídos**: Mensajes leídos
- **Clics**: Interacciones con botones
- **Errores**: Usuarios no alcanzados

---

## 🔧 Configuración Avanzada

### ⚙️ **Configuración del Sistema**

#### 🌐 **Ajustes Generales**
```
⚙️ Configuración del Sistema

🤖 Bot Token: [EDITAR]
👑 Admin ID: 123456789
🌍 Idioma por defecto: Español
🔧 Modo mantenimiento: [DESACTIVADO]
📊 Nivel de logs: INFO
```

#### 🔌 **Configuración VPN**
- **WireGuard**: Puerto, red interna, DNS
- **Outline**: Puerto API, certificados
- **Límites**: Claves por usuario, datos por plan
- **Seguridad**: Tiempos de expiración

#### 💰 **Configuración de Pagos**
- **Planes**: Precios y límites
- **Referidos**: Porcentajes de comisión
- **Moneda**: Telegram Stars
- **Facturación**: Ciclos y renovaciones

---

## 🚨 Alertas y Notificaciones

### 🔔 **Sistema de Alertas**

#### ⚠️ **Tipos de Alertas**
- **🔴 Críticas**: Servidor caído, sin espacio en disco
- **🟡 Advertencias**: Alto uso de CPU, memoria baja
- **🔵 Informativas**: Nuevo usuario, actualización disponible

#### 📱 **Canales de Notificación**
- **Telegram**: Notificaciones directas al admin
- **Email**: Alertas por correo electrónico
- **Webhook**: Integración con sistemas externos
- **Logs**: Registro completo en archivos

#### ⚙️ **Configuración de Alertas**
```
🚨 Configuración de Alertas

🔴 Servidor caído: [ACTIVADO] - Notificar inmediatamente
🟡 CPU > 80%: [ACTIVADO] - Notificar después de 5min
🟡 Memoria < 10%: [ACTIVADO] - Notificar inmediatamente
🔵 Nuevo usuario: [DESACTIVADO] - Resumen diario
```

---

## 🎯 Mejores Prácticas

### 👑 **Gestión de Usuarios**
- **Revisa regularmente** usuarios inactivos
- **Ofrece upgrades** a usuarios activos
- **Monitorea abusos** y patrones sospechosos
- **Mantén comunicación** con la comunidad

### 🔐 **Seguridad de Claves**
- **Elimina claves** de usuarios suspendidos
- **Rota claves** periódicamente
- **Monitorea uso** anómalo de datos
- **Mantén backups** de configuraciones

### 🖥️ **Mantenimiento de Servidores**
- **Actualiza software** regularmente
- **Monitorea rendimiento** continuamente
- **Revisa logs** de errores
- **Planifica capacidad** para crecimiento

---

## 🆘 Solución de Problemas

### 🐛 **Problemas Comunes del Panel**

#### ❌ **"No veo el botón Admin"**
```bash
# Verificar tu ID de admin
python -c "
from config import settings
print(f'Tu ADMIN_ID configurado: {settings.ADMIN_ID}')
"

# Obtener tu ID real
# Envía un mensaje a @userinfobot
```

#### ❌ **"El panel no responde"**
```bash
# Verificar logs del bot
tail -f logs/bot.log

# Reiniciar el bot
sudo systemctl restart usipipo-bot
```

#### ❌ **"No puedo eliminar claves"**
```bash
# Verificar permisos de servicios
sudo systemctl status wg-quick@wg0
docker ps | grep outline

# Verificar conexión a base de datos
python -c "
from config import settings
import psycopg2
conn = psycopg2.connect(settings.DATABASE_URL)
print('✅ Conexión a BD OK')
conn.close()
"
```

---

## 📚 Recursos Adicionales

### 📖 **Documentación Relacionada**
- [📋 Instalación Completa](./INSTALL.md) - Configuración inicial
- [⚙️ Configuración](./CONFIGURATION.md) - Todas las opciones
- [🤖 Comandos del Bot](./BOT_COMMANDS.md) - Comandos disponibles
- [🐛 Troubleshooting](./TROUBLESHOOTING.md) - Problemas comunes

### 🔧 **Herramientas Útiles**
- **Logs en tiempo real**: `tail -f logs/vpn_manager.log`
- **Estado de servicios**: `systemctl status usipipo-bot`
- **Diagnóstico**: Scripts en `/scripts/health_check.sh`
- **Backup**: `/scripts/backup_config.sh`

---

<div align="center">

**👑 Panel de Administración Completo**  
*Control total sobre tu sistema VPN uSipipo*

[📖 Documentación](./README.md) • [🚀 Instalación](./INSTALL.md) • [💬 Soporte](https://discord.gg/usipipo)

Made with ❤️ by uSipipo Team

</div>
