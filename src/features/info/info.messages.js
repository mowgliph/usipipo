'use strict';

/**
 * ============================================================================
 * ℹ️ INFO MESSAGES - uSipipo VPN Bot
 * ============================================================================
 * Mensajes relacionados con información del sistema, servidor y documentación
 * ============================================================================
 */

const markdown = require('../../core/utils/markdown');
const constants = require('../../config/constants');
const config = require('../../config/environment');

// ============================================================================
// 📊 INFORMACIÓN DEL SISTEMA
// ============================================================================

function getSystemInfoMessage() {
  return `${constants.EMOJI.SERVER} ${markdown.bold('Información del Sistema')}\n\n` +
         `${markdown.bold('Estado:')} Operativo ${constants.EMOJI.SUCCESS}\n` +
         `${markdown.bold('Versión:')} 2.0.0\n` +
         `${markdown.bold('Entorno:')} ${markdown.code(config.NODE_ENV)}\n` +
         `${markdown.bold('Uptime:')} Sistema activo\n\n` +
         `_Sistema de gestión VPN empresarial_`;
}

function getServerInfoMessage() {
  const wgEndpoint = `${config.SERVER_IP}:${config.WG_SERVER_PORT}`;
  const outlineApi = `${config.OUTLINE_SERVER_IP}:${config.OUTLINE_API_PORT}`;

  return `${constants.EMOJI.SERVER} ${markdown.bold('Información del Servidor')}\n\n` +
         `${markdown.bold('🌐 Servidor Principal')}\n` +
         `• IPv4: ${markdown.code(config.SERVER_IPV4)}\n` +
         (config.SERVER_IPV6 ? `• IPv6: ${markdown.code(config.SERVER_IPV6)}\n` : '') +
         `\n${markdown.bold('🔐 WireGuard')}\n` +
         `• Endpoint: ${markdown.code(wgEndpoint)}\n` +
         `• Interfaz: ${markdown.code(config.WG_INTERFACE)}\n` +
         `• Red interna: ${markdown.code(config.WG_SERVER_IPV4)}\n` +
         `\n${markdown.bold('🌐 Outline')}\n` +
         `• API: ${markdown.code(outlineApi)}\n` +
         `• Puerto claves: ${markdown.code(config.OUTLINE_KEYS_PORT)}\n` +
         `\n_Información técnica del servidor VPN_`;
}

function getNetworkInfoMessage() {
  return `${constants.EMOJI.VPN} ${markdown.bold('Información de Red')}\n\n` +
         `${markdown.bold('🔒 Protocolos Soportados')}\n` +
         `• WireGuard (UDP)\n` +
         `• Outline/Shadowsocks (TCP)\n\n` +
         `${markdown.bold('🌍 Características')}\n` +
         `• Cifrado end-to-end\n` +
         `• Sin logs de actividad\n` +
         `• Conexión de alta velocidad\n` +
         `• Múltiples dispositivos\n\n` +
         `${markdown.bold('📡 DNS')}\n` +
         (config.PIHOLE_DNS ? 
           `• Pi-hole: ${markdown.code(config.PIHOLE_DNS)}\n` : 
           `• Cloudflare: ${markdown.code('1.1.1.1')}\n`) +
         `\n_Tu privacidad es nuestra prioridad_`;
}

// ============================================================================
// 📖 DOCUMENTACIÓN Y GUÍAS
// ============================================================================

function getWireGuardInfoMessage() {
  return `${constants.EMOJI.VPN} ${markdown.bold('WireGuard - Información')}\n\n` +
         `${markdown.bold('¿Qué es WireGuard?')}\n` +
         `WireGuard es un protocolo VPN moderno, extremadamente rápido y seguro. ` +
         `Utiliza criptografía de última generación y es más simple que OpenVPN o IPSec.\n\n` +
         `${markdown.bold('✨ Ventajas:')}\n` +
         `• Velocidad superior\n` +
         `• Código auditable y minimalista\n` +
         `• Bajo consumo de batería\n` +
         `• Reconexión instantánea\n` +
         `• Compatible con todos los dispositivos\n\n` +
         `${markdown.bold('📱 Descargar Cliente:')}\n` +
         `${constants.URLS.WIREGUARD_DOWNLOAD}\n\n` +
         `${markdown.bold('🔧 Configuración:')}\n` +
         `1. Descarga la app oficial\n` +
         `2. Solicita tu configuración con /vpn\n` +
         `3. Escanea el QR o importa el archivo .conf\n` +
         `4. ¡Conéctate!\n\n` +
         `_Recomendado para uso diario en móviles_`;
}

function getOutlineInfoMessage() {
  return `${constants.EMOJI.SERVER} ${markdown.bold('Outline - Información')}\n\n` +
         `${markdown.bold('¿Qué es Outline?')}\n` +
         `Outline es una VPN basada en Shadowsocks, creada por Jigsaw (Google). ` +
         `Es resistente a la censura y muy fácil de usar.\n\n` +
         `${markdown.bold('✨ Ventajas:')}\n` +
         `• Resistente a bloqueos\n` +
         `• Configuración en un clic\n` +
         `• Sin archivos de configuración\n` +
         `• Ideal para países con censura\n` +
         `• Multiplataforma\n\n` +
         `${markdown.bold('📱 Descargar Cliente:')}\n` +
         `${constants.URLS.OUTLINE_DOWNLOAD}\n\n` +
         `${markdown.bold('🔧 Configuración:')}\n` +
         `1. Descarga Outline Client\n` +
         `2. Solicita tu clave de acceso con /vpn\n` +
         `3. Copia el enlace ss:// y pégalo en la app\n` +
         `4. ¡Conéctate automáticamente!\n\n` +
         `_Recomendado para evadir censura y bloqueos_`;
}

function getComparisonMessage() {
  return `${constants.EMOJI.INFO} ${markdown.bold('WireGuard vs Outline')}\n\n` +
         `${markdown.bold('🔐 WireGuard:')}\n` +
         `✅ Más rápido\n` +
         `✅ Mejor para uso móvil\n` +
         `✅ Menor consumo de batería\n` +
         `❌ Puede ser bloqueado en algunos países\n\n` +
         `${markdown.bold('🌐 Outline:')}\n` +
         `✅ Resistente a censura\n` +
         `✅ Configuración más simple\n` +
         `✅ Funciona en redes restrictivas\n` +
         `❌ Ligeramente más lento\n\n` +
         `${markdown.bold('💡 Recomendación:')}\n` +
         `• ${markdown.bold('Uso diario:')} WireGuard\n` +
         `• ${markdown.bold('Censura/Bloqueos:')} Outline\n` +
         `• ${markdown.bold('Máxima seguridad:')} Usa ambos según necesites\n\n` +
         `_Puedes solicitar ambas configuraciones sin costo adicional_`;
}

// ============================================================================
// 🛡️ SEGURIDAD Y PRIVACIDAD
// ============================================================================

function getSecurityInfoMessage() {
  return `${constants.EMOJI.VPN} ${markdown.bold('Seguridad y Privacidad')}\n\n` +
         `${markdown.bold('🔒 Cifrado:')}\n` +
         `• WireGuard: ChaCha20 + Poly1305\n` +
         `• Outline: AES-256-GCM\n` +
         `• Claves únicas por usuario\n\n` +
         `${markdown.bold('🚫 Política de No-Logs:')}\n` +
         `• No registramos sitios visitados\n` +
         `• No almacenamos historial de navegación\n` +
         `• No vendemos datos de usuarios\n` +
         `• Logs técnicos mínimos (solo errores)\n\n` +
         `${markdown.bold('🛡️ Protección:')}\n` +
         `• Oculta tu IP real\n` +
         `• Cifra todo el tráfico\n` +
         `• Protege en WiFi públicas\n` +
         `• Evita rastreo de ISP\n\n` +
         `_Tu privacidad es fundamental para nosotros_`;
}

function getDataPolicyMessage() {
  return `${constants.EMOJI.INFO} ${markdown.bold('Política de Datos')}\n\n` +
         `${markdown.bold('📊 Datos que registramos:')}\n` +
         `• ID de usuario (solo Telegram ID)\n` +
         `• Consumo de ancho de banda\n` +
         `• Estado de conexión (activo/suspendido)\n` +
         `• Fecha de creación de cuenta\n\n` +
         `${markdown.bold('🚫 Datos que NO registramos:')}\n` +
         `• Historial de navegación\n` +
         `• Sitios web visitados\n` +
         `• Contenido transmitido\n` +
         `• Datos personales sensibles\n\n` +
         `${markdown.bold('⏱️ Retención:')}\n` +
         `Los datos técnicos se conservan solo mientras la cuenta esté activa. ` +
         `Al eliminar tu acceso, todos los datos se eliminan permanentemente.\n\n` +
         `_Transparencia total en el manejo de datos_`;
}

// ============================================================================
// ❓ PREGUNTAS FRECUENTES
// ============================================================================

function getFAQMessage() {
  return `${constants.EMOJI.INFO} ${markdown.bold('Preguntas Frecuentes')}\n\n` +
         `${markdown.bold('❓ ¿Puedo usar ambas VPNs?')}\n` +
         `Sí, puedes solicitar WireGuard y Outline. Usa cada una según tus necesidades.\n\n` +
         `${markdown.bold('❓ ¿Cuántos dispositivos puedo conectar?')}\n` +
         `WireGuard: 1 dispositivo por configuración\n` +
         `Outline: Hasta 5 dispositivos simultáneos\n\n` +
         `${markdown.bold('❓ ¿Hay límite de datos?')}\n` +
         `Sí, cada servicio tiene un límite mensual. Consulta con /profile tu cuota actual.\n\n` +
         `${markdown.bold('❓ ¿Qué pasa si excedo el límite?')}\n` +
         `El servicio se suspende automáticamente. Contacta al admin para renovar.\n\n` +
         `${markdown.bold('❓ ¿Es legal usar VPN?')}\n` +
         `Sí, en la mayoría de países el uso de VPN es completamente legal. Consulta las leyes locales.\n\n` +
         `${markdown.bold('❓ ¿Funciona en China/Irán?')}\n` +
         `Outline tiene mejor tasa de éxito en países con censura fuerte.\n\n` +
         `_¿Más preguntas? Usa /help para contactar soporte_`;
}

function getTroubleshootingMessage() {
  return `${constants.EMOJI.WARNING} ${markdown.bold('Solución de Problemas')}\n\n` +
         `${markdown.bold('🔴 No puedo conectarme:')}\n` +
         `1. Verifica que copiaste correctamente la configuración\n` +
         `2. Comprueba tu conexión a internet\n` +
         `3. Desactiva otros VPNs activos\n` +
         `4. Reinicia la app del cliente\n\n` +
         `${markdown.bold('🐌 Conexión lenta:')}\n` +
         `1. Prueba cambiar de protocolo (WG ↔ Outline)\n` +
         `2. Verifica tu velocidad de internet base\n` +
         `3. Cierra apps que consuman mucho ancho de banda\n` +
         `4. Contacta al admin si persiste\n\n` +
         `${markdown.bold('⚠️ Configuración expirada:')}\n` +
         `1. Solicita una nueva con /vpn\n` +
         `2. Elimina la configuración antigua\n` +
         `3. Importa la nueva configuración\n\n` +
         `${markdown.bold('📱 Problemas en iOS:')}\n` +
         `• Asegúrate de dar permisos VPN en Configuración\n` +
         `• Reinicia el dispositivo después de instalar\n\n` +
         `_Si el problema persiste, contacta con /help_`;
}

// ============================================================================
// 📞 CONTACTO Y SOPORTE
// ============================================================================

function getContactMessage() {
  const adminMention = config.ADMIN_ID ? 
    `Administrador: ${markdown.userMention('Admin', config.ADMIN_ID)}` :
    'Usa /help para ver comandos de soporte';

  return `${constants.EMOJI.USER} ${markdown.bold('Contacto y Soporte')}\n\n` +
         `${markdown.bold('💬 Soporte Técnico:')}\n` +
         `${adminMention}\n\n` +
         `${markdown.bold('🐛 Reportar Errores:')}\n` +
         `Usa el comando /report seguido de la descripción del problema.\n\n` +
         `${markdown.bold('💡 Sugerencias:')}\n` +
         `Tus ideas son bienvenidas. Contacta al administrador con tus propuestas.\n\n` +
         `${markdown.bold('⏱️ Tiempo de Respuesta:')}\n` +
         `• Errores críticos: < 1 hora\n` +
         `• Consultas técnicas: < 24 horas\n` +
         `• Solicitudes generales: < 48 horas\n\n` +
         `_Estamos aquí para ayudarte_`;
}

function getAboutMessage() {
  return `${constants.EMOJI.INFO} ${markdown.bold('Sobre uSipipo VPN')}\n\n` +
         `${markdown.bold('🎯 Misión:')}\n` +
         `Proporcionar acceso seguro, privado y libre a internet para todos los usuarios.\n\n` +
         `${markdown.bold('🛠️ Tecnología:')}\n` +
         `• Bot desarrollado con Node.js + Telegraf\n` +
         `• Servidores VPN autoalojados\n` +
         `• Infraestructura optimizada\n` +
         `• Código abierto y auditable\n\n` +
         `${markdown.bold('🌟 Características:')}\n` +
         `• Gestión automatizada\n` +
         `• Múltiples protocolos VPN\n` +
         `• Control de cuotas inteligente\n` +
         `• Notificaciones en tiempo real\n\n` +
         `${markdown.bold('📅 Versión:')}\n` +
         `2.0.0 (${config.NODE_ENV})\n\n` +
         `_Construido con ${constants.EMOJI.VPN} por el equipo uSipipo_`;
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // System Information
  getSystemInfoMessage,
  getServerInfoMessage,
  getNetworkInfoMessage,

  // Documentation
  getWireGuardInfoMessage,
  getOutlineInfoMessage,
  getComparisonMessage,

  // Security & Privacy
  getSecurityInfoMessage,
  getDataPolicyMessage,

  // FAQ & Troubleshooting
  getFAQMessage,
  getTroubleshootingMessage,

  // Contact & About
  getContactMessage,
  getAboutMessage
};
