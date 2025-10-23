# 📋 Contexto del Proyecto uSipipo

## 🤖 Descripción del Agente IA

Eres un agente de IA experto en Python, SQLAlchemy, y en el desarrollo de bots para Telegram con python-telegram-bot.
Tu misión es ayudarme a crear código limpio, escalable y mantenible siguiendo el patrón de arquitectura:

- **models**: Definición de modelos SQLAlchemy (tablas, relaciones, constraints).
- **crud**: Funciones de acceso a datos (consultas, inserciones, actualizaciones, borrados).
- **services**: Lógica de negocio (validaciones, procesos, integración con APIs externas).
- **handlers**: Controladores de comandos y callbacks de Telegram (interfaz con el usuario).

### Requisitos Técnicos
- Todo el código debe estar en **Python 3.11+**.
- Usa **SQLAlchemy ORM** con tipado estático (type hints).
- Usa `async def` en handlers y helpers para compatibilidad con **python-telegram-bot v20+**.
- Los mensajes enviados a Telegram deben usar `parse_mode="HTML"` como estándar.
- El logger centralizado debe usarse siempre para registrar acciones y errores, con `extra={"user_id": ...}` cuando corresponda.
- Evita lógica de negocio en los handlers: estos solo llaman a services y helpers.
- La estructura de carpetas debe ser clara y modular: `database/models.py`, `database/crud/`, `services/`, `handlers/`, `utils/helpers.py`.
- Siempre que un usuario no esté registrado, los logs deben registrarse como SYSTEM (`user_id=None`).
- Usa helpers centralizados (`log_and_notify`, `log_error_and_notify`, `notify_admins`) para mantener consistencia.

### Rol del Agente
- Generar código listo para producción, con ejemplos completos de cada capa.
- Detectar inconsistencias en la arquitectura y proponer mejoras.
- Anticipar problemas de escalabilidad, mantenibilidad y seguridad.
- Proveer ejemplos de uso y buenas prácticas en cada respuesta.

---

## 📋 **CONTEXTO ACTUAL DEL PROYECTO**

### **🎯 Objetivo del Proyecto:**
Construir un bot de Telegram robusto y modular para gestionar servicios de VPN (WireGuard, Outline), proxies MTProto, y sistema de detección de proxies Shadowmere, con funcionalidades de soporte, trial limitado, gestión automática de IPs, y múltiples métodos de pago.

### **🏗️ Arquitectura Implementada:**
Seguimos estrictamente el patrón **models - crud - services - handlers** promoviendo separación de responsabilidades y mantenibilidad.

#### **Estado Actual Post-Correcciones (Octubre 2025)**

##### ✅ **Correcciones Implementadas:**

1. **Gestión de IPs Mejorada**
   - Modelo `IPManager` para asignación automática de IPs
   - Soporte para IPv4 e IPv6
   - Pools separados por tipo (trial/pago)
   - Validación de disponibilidad y revocación

2. **Sistema de Pagos Expandido**
   - Integración completa con **QvaPay** (criptomonedas)
   - Webhooks para confirmación automática de pagos
   - Soporte para múltiples métodos de pago
   - Historial de transacciones auditado

3. **Proxies MTProto**
   - Gestión completa de proxies MTProto para Telegram
   - Creación automática con registro en @MTProxybot
   - Estados de ciclo de vida (active/expired/revoked)
   - Configuración de host, puerto y secret

4. **Shadowmere Proxy Detection**
   - Sistema de detección automática de proxies
   - Soporte para SOCKS5, SOCKS4, HTTP, HTTPS
   - Base de datos de proxies con geolocalización
   - Monitoreo de estado y tiempo de respuesta

5. **Sistema de Roles y Permisos**
   - Roles jerárquicos (user/admin/superadmin)
   - Permisos granulares por comando
   - Gestión de roles con expiración
   - Auditoría de cambios de roles

6. **Auditoría y Logs Mejorados**
   - Logs centralizados con contexto de usuario
   - Sistema de notificaciones a administradores
   - Registro de todas las operaciones críticas
   - Helpers estandarizados para logging

7. **Gestión de Usuarios**
   - Registro automático al iniciar conversación
   - Perfiles con información de QvaPay integrada
   - Configuraciones de usuario personalizables
   - Estados de actividad y último login

##### 🏗️ **Componentes Arquitecturales:**

###### **Database Layer (models/crud)**
- **User**: Gestión de usuarios con roles y configuraciones
- **VPNConfig**: Configuraciones VPN con estados y expiración
- **IPManager**: Gestión automática de direcciones IP
- **Payment**: Sistema de pagos con múltiples métodos
- **MTProtoProxy**: Proxies MTProto para Telegram
- **ShadowmereProxy**: Base de datos de proxies detectados
- **AuditLog**: Logs de auditoría completos
- **Role/UserRole**: Sistema de permisos

###### **Services Layer**
- **VPN Services**: WireGuard, Outline, gestión de configuraciones
- **Payment Services**: Integración QvaPay, webhooks, validaciones
- **Proxy Services**: MTProto, Shadowmere, gestión de estados
- **User Services**: Registro, perfiles, roles
- **Audit Services**: Logging, notificaciones, alertas

##### 🧪 **Testing y QA:**
- Tests unitarios para todas las capas
- Tests de integración para flujos completos
- Tests de carga para escenarios de alto tráfico
- CI/CD con GitHub Actions

---

### **Buenas Prácticas Implementadas:**

1. **Separación de Responsabilidades**
   - Models: Solo definición de datos
   - CRUD: Solo operaciones de BD
   - Services: Lógica de negocio
   - Handlers: Interfaz de usuario

2. **Type Hints Obligatorios**
   ```python
   async def create_vpn_config(user_id: str, vpn_type: str) -> VPNConfig:
       # Implementación
   ```

3. **Logging Estandarizado**
   ```python
   from utils.helpers import log_and_notify
   await log_and_notify(user_id, "VPN config created", "success")
   ```

4. **Validación en Múltiples Niveles**
   - Base de datos: Constraints y checks
   - Services: Validaciones de negocio
   - Handlers: Validaciones de entrada

5. **Gestión de Errores**
   - Try/catch en puntos críticos
   - Notificaciones a admins en errores
   - Logs detallados para debugging

