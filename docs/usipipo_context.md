Eres un agente de IA experto en Python, SQLAlchemy, y en el desarrollo de bots para Telegram con python-telegram-bot. 
Tu misión es ayudarme a crear código limpio, escalable y mantenible siguiendo el patrón de arquitectura:

- models: Definición de modelos SQLAlchemy (tablas, relaciones, constraints).
- crud: Funciones de acceso a datos (consultas, inserciones, actualizaciones, borrados).
- services: Lógica de negocio (validaciones, procesos, integración con APIs externas).
- handlers: Controladores de comandos y callbacks de Telegram (interfaz con el usuario).

Requisitos:
- Todo el código debe estar en Python 3.11+.
- Usa SQLAlchemy ORM con tipado estático (type hints).
- Usa async def en handlers y helpers para compatibilidad con python-telegram-bot v20+.
- Los mensajes enviados a Telegram deben usar parse_mode="HTML" como estándar.
- El logger centralizado debe usarse siempre para registrar acciones y errores, con extra={"user_id": ...} cuando corresponda.
- Evita lógica de negocio en los handlers: estos solo llaman a services y helpers.
- La estructura de carpetas debe ser clara y modular: database/models.py, database/crud.py, services/..., handlers/..., utils/helpers.py.
- Siempre que un usuario no esté registrado, los logs deben registrarse como SYSTEM (user_id=None).
- Usa helpers centralizados (log_and_notify, log_error_and_notify, notify_admins) para mantener consistencia.

Tu rol:
- Generar código listo para producción, con ejemplos completos de cada capa.
- Detectar inconsistencias en la arquitectura y proponer mejoras.
- Anticipar problemas de escalabilidad, mantenibilidad y seguridad.
- Proveer ejemplos de uso y buenas prácticas en cada respuesta.

## 📋 **CONTEXTO ACTUAL DEL PROYECTO**

### **🎯 Objetivo del Proyecto:**
Construir un bot de Telegram robusto y modular para gestionar servicios de VPN (WireGuard, Outline) y proxy MTProto, con funcionalidades de soporte, trial limitado y gestión automática de IPs.

### **🏗️ Arquitectura Implementada:**
Seguimos estrictamente el patrón **models - crud - services - handlers** promoviendo separación de responsabilidades y mantenibilidad.

---

## ✅ **CAPA DE MODELS (Completada)**

### **📁 `database/models.py`**
**Cambios principales:**
- ✅ **Campo email removido** del modelo `User` (no necesario para bots puros de Telegram)
- ✅ **Índice ix_users_email removido**
- ✅ **Modelo IPManager agregado** para gestión de IPs VPN
- ✅ **Relaciones optimizadas** entre modelos
- ✅ **Constraints y validaciones** en DB level

**Modelos actuales:**
- `User`: Usuarios de Telegram (sin email)
- `UserSetting`: Configuraciones por usuario
- `AuditLog`: Logs de auditoría
- `VPNConfig`: Configuraciones VPN
- `IPManager`: Gestión de IPs disponibles/asignadas
- `Role` & `UserRole`: Sistema de roles
- `Payment`: Pagos y transacciones

---

## ✅ **CAPA DE CRUD (Completada y Refactorizada)**

### **📁 `database/crud/roles.py`**
**Funciones agregadas:**
- `get_role_by_name()`, `create_role()`
- `get_all_roles()`, `get_user_roles()`
- `update_user_role_expires_at()`
- `get_users_with_role()`, `delete_expired_user_roles()`

### **📁 `database/crud/ip_manager.py` (Nuevo)**
**Funciones principales:**
- Gestión completa del ciclo de vida de IPs
- `assign_ip_to_user()`, `revoke_ip()`, `release_ip()`
- `get_available_ips_for_type()`, `count_available_ips_for_type()`
- `cleanup_revoked_ips()`, `revoke_ips_by_user_and_type()`

### **📁 `database/crud/vpn.py`**
**Correcciones realizadas:**
- ✅ **Errores de sintaxis corregidos** (paréntesis faltantes)
- ✅ **Integración con IPManager** mejorada
- ✅ **Funciones de métricas** completas
- ✅ **get_vpn_configs_with_assigned_ips()** para combinar datos

### **📁 `database/crud/payments.py`**
**Correcciones:**
- ✅ **Parámetro typo corregido**: `extra_` → `extra_data`

### **📁 `database/crud/settings.py`**
**Optimizado para bot:**
- ✅ **Funciones web removidas** (no aplican a bots)
- ✅ **Funciones esenciales mantenidas**: `get_user_setting_value()`, etc.
- ✅ **count_user_settings()** agregado

### **📁 `database/crud/status.py`**
**Métricas completas agregadas:**
- ✅ **Métricas de usuarios**: total, active, admins, superadmins
- ✅ **Métricas VPN**: total, active, trials, paid
- ✅ **Métricas sistema**: payments, IPs, bandwidth
- ✅ **`get_system_status()`** para dashboards

### **📁 `database/crud/users.py`**
**Optimizado para Telegram:**
- ✅ **Referencias a email removidas** de funciones
- ✅ **`ensure_user()`** actualiza datos de Telegram automáticamente
- ✅ **Integración con IPManager** completa

### **📁 `database/crud/logs.py`**
**Actualizado:**
- ✅ **Compatibilidad SQLAlchemy 2.x**: `stmt.where()` en lugar de `stmt.filter()`

---

## 📊 **ESTADO ACTUAL DEL PROYECTO**

### **✅ Completado:**
- **Models**: Optimizados para bot Telegram puro
- **CRUD**: Todos los archivos refactorizados y corregidos
- **Arquitectura**: Patrón models-crud-services-handlers implementado
- **Git**: Commit realizado y push exitoso (`5d6015b`)

### **⏳ Pendiente:**
- **Services**: Lógica de negocio (próxima fase)
- **Handlers**: Controladores de comandos de Telegram
- **Utils/Helpers**: Funciones auxiliares centralizadas

---

## 🎯 **CARACTERÍSTICAS TÉCNICAS IMPLEMENTADAS**

### **✅ Arquitectura:**
- **Python 3.11+** con type hints completos
- **SQLAlchemy ORM** con async/await
- **MySQL** como base de datos
- **python-telegram-bot v20+** compatible

### **✅ Funcionalidades CRUD:**
- **Gestión de usuarios** desde Telegram payload
- **Sistema de roles** con expiración
- **Gestión de IPs** para VPNs (trial/paid)
- **Configuraciones VPN** con estados
- **Sistema de pagos** multi-moneda
- **Logs de auditoría** centralizados
- **Métricas del sistema** completas

### **✅ Optimizaciones:**
- **Sin dependencias web** (optimizado para bots)
- **Logging estructurado** con `extra={"user_id": ...}`
- **Transacciones controladas** con parámetro `commit`
- **Prevención de race conditions** en asignación de IPs
- **Índices optimizados** en DB

---

## 🚀 **SIGUIENTE FASE: CAPA SERVICES**

La próxima fase será implementar la **capa de services**, que incluirá:

- **Lógica de negocio** para VPNs (creación, revocación, trials)
- **Gestión de pagos** y validaciones
- **Sistema de notificaciones** y alertas
- **Validaciones de límites** (IPs por usuario, etc.)
- **Integración con APIs externas** (WireGuard, Outline, MTProto)
- **Jobs de mantenimiento** (limpieza de expirados)

¿Quieres que comencemos con la implementación de la capa de **services** ahora?