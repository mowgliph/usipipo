📄 Propuesta de Proyecto: uSipipo VPN

**Fecha:** 27 de noviembre de 2025  
**Versión:** 1.0  
**Preparado para:** Comunidad uSipipo  
**Preparado por:** [Tu nombre/Equipo]

---

## 🌐 Visión General

uSipipo VPN es una solución integral de red privada virtual diseñada específicamente para los miembros de nuestra comunidad. Combina tecnologías de vanguardia (WireGuard y Outline) con protección avanzada contra anuncios y rastreadores (Pi-hole), todo gestionado mediante una interfaz intuitiva de Telegram. Este proyecto busca proporcionar acceso seguro, privado y optimizado a internet para todos los miembros de la comunidad.

## 🎯 Objetivos Clave

1. **Seguridad reforzada**: Proteger la privacidad y datos de los usuarios frente a amenazas en línea.
2. **Experiencia sin anuncios**: Bloquear automáticamente anuncios, rastreadores y malware a nivel de red.
3. **Acceso sencillo**: Permitir a los usuarios obtener configuraciones VPN en segundos mediante Telegram.
4. **Escalabilidad**: Soportar inicialmente 50 usuarios concurrentes con capacidad de expansión.
5. **Autogestión**: Reducir la carga de administración mediante un sistema auto-servicio.

## ⚙️ Alcance del Proyecto

### Incluye:
- Implementación de servidor VPS con:
  - Pi-hole como DNS ad-blocking central
  - WireGuard para conexiones VPN de alto rendimiento
  - Outline Server para acceso a través de apps móviles
- Bot de Telegram para:
  - Autenticación de usuarios autorizados
  - Generación automática de configuraciones WireGuard (archivos .conf + QR)
  - Creación de enlaces de conexión Outline
  - Gestión básica de cuotas y uso
- Documentación completa para usuarios y administradores
- Sistema de monitoreo básico de recursos del servidor

### No incluye:
- Soporte para sistemas operativos legacy (Windows 7 o anteriores)
- Aplicación móvil dedicada (se utilizan clientes estándar)
- Almacenamiento de registros de navegación (política de no-logs)
- Soporte 24/7 (ventana de soporte: 9am-9pm hora local)

## 🌟 Beneficios para los Usuarios

| Beneficio | Descripción |
|-----------|-------------|
| **Privacidad garantizada** | Navegación cifrada sin vigilancia de ISPs o terceros |
| **Experiencia sin anuncios** | Carga más rápida de páginas y menor consumo de datos |
| **Acceso instantáneo** | Configuración en menos de 60 segundos vía Telegram |
| **Compatibilidad universal** | Funciona en iOS, Android, Windows, macOS y Linux |
| **Sin límites de ancho de banda** | Conexión estable para streaming y trabajo remoto |

## 🛠️ Tecnologías Clave

| Componente | Tecnología | Ventaja |
|------------|------------|---------|
| **Núcleo VPN** | WireGuard + Outline | Velocidad 40% superior a OpenVPN |
| **Filtro de contenido** | Pi-hole | Bloqueo de 100,000+ dominios maliciosos |
| **Interfaz de usuario** | Bot de Telegram (Node.js) | Accesible y familiar para usuarios |
| **Infraestructura** | VPS Ubuntu 22.04 LTS | Estabilidad y soporte a largo plazo |
| **Seguridad** | Certificados TLS + autenticación por tokens | Protección contra accesos no autorizados |

## 📅 Cronograma de Implementación

| Fase | Actividades | Duración | Entregables |
|------|-------------|----------|-------------|
| **Preparación** | Selección de VPS, compra de dominio, configuración de DNS | 3 días | Entorno listo para instalación |
| **Implementación** | Instalación de Pi-hole, WireGuard y Outline Server | 2 días | Servicios funcionales en servidor |
| **Desarrollo** | Creación del bot de Telegram y pruebas de integración | 4 días | Bot funcional con todas las funciones |
| **Pruebas** | Validación de seguridad y rendimiento con usuarios beta | 3 días | Reporte de pruebas y ajustes finales |
| **Lanzamiento** | Documentación, capacitación y apertura a todos los miembros | 2 días | Sistema operativo completo |
| **Mantenimiento** | Monitoreo y actualizaciones mensuales | Continuo | Informes de estado mensuales |

## 👥 Equipo Necesario

| Rol | Responsabilidades | Cantidad |
|-----|-------------------|----------|
| **Administrador de Sistemas** | Gestión del VPS, seguridad y actualizaciones | 1 |
| **Desarrollador Full-Stack** | Mantenimiento del bot y mejoras futuras | 1 (puede ser el mismo admin) |
| **Soporte Comunitario** | Resolución de dudas y asistencia a usuarios | 2-3 (voluntarios de la comunidad) |

## 💰 Presupuesto Estimado

| Concepto | Costo Mensual | Costo Inicial | Notas |
|----------|---------------|---------------|-------|
| **Servidor VPS** | $12.00 | $0 | 4GB RAM, 2 vCPU, 80GB SSD |
| **Dominio** | $1.50 | $15.00 | .community por 10 años |
| **Certificados SSL** | $0 | $0 | Let's Encrypt (gratuito) |
| **Desarrollo** | $0 | $0 | Equipo voluntario |
| **Total** | **$13.50** | **$15.00** | + impuestos aplicables |

> *Nota: Costos basados en proveedor de confianza (Hetzner/Contabo). Escalable según crecimiento de usuarios.*

## ✅ Próximos Pasos

1. **Aprobación formal** de esta propuesta por parte de los administradores de la comunidad
2. **Reserva presupuestaria** para el VPS y dominio
3. **Asignación de responsables** para cada fase del proyecto
4. **Reunión de kick-off** con el equipo técnico (72 horas posteriores a la aprobación)
5. **Creación del repositorio** de código en GitHub con estructura definida

---

## 📬 Contacto

Para consultas adicionales o aprobación de esta propuesta:  
📧 usipipo@etlgr.com  
💬 Canal de Telegram: @uSipipo_Soporte  

---

> **Confidencialidad**: Este documento contiene información sensible sobre la infraestructura de la comunidad uSipipo. Su distribución no autorizada está prohibida.  
> **Versión vigente**: Actualizada a 27/11/2025. Sujeta a cambios con aprobación del consejo directivo.
