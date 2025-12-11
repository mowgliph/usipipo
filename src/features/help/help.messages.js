'use strict';

/**
 * ============================================================================
 * 💬 HELP MESSAGES - uSipipo VPN Bot
 * ============================================================================
 * Mensajes de ayuda organizados por categorías y contextos.
 * Usa Markdown V1 para máxima compatibilidad.
 * ============================================================================
 */

const markdown = require('../../../core/utils/markdown');
const constants = require('../../../config/constants');
const config = require('../../../config/environment');

// ============================================================================
// 📖 MENSAJES PRINCIPALES DE AYUDA
// ============================================================================

function getMainHelpMessage(isAdmin = false) {
  let message = `${constants.EMOJI.INFO} *CENTRO DE AYUDA - uSipipo VPN*\n\n`;
  
  message += `Selecciona una categoría para obtener información detallada:\n\n`;
  
  message += `${constants.EMOJI.VPN} *Conexiones VPN*\n`;
  message += `Aprende a crear y gestionar tus conexiones seguras.\n\n`;
  
  message += `${constants.EMOJI.USER} *Gestión de Perfil*\n`;
  message += `Configura tu cuenta y preferencias.\n\n`;
  
  message += `${constants.EMOJI.INFO} *Información del Sistema*\n`;
  message += `Conoce el estado y características del servicio.\n\n`;
  
  if (isAdmin) {
    message += `${constants.EMOJI.ADMIN} *Panel Administrativo*\n`;
    message += `Herramientas de gestión y monitoreo.\n\n`;
  }
  
  message += `${constants.EMOJI.SUCCESS} *Solución de Problemas*\n`;
  message += `Resuelve dudas y problemas comunes.\n\n`;
  
  message += `_Usa los botones de abajo para navegar._`;
  
  return message;
}

// ============================================================================
// 🔐 AYUDA: CONEXIONES VPN
// ============================================================================

function getVPNHelpMessage() {
  let message = `${constants.EMOJI.VPN} *AYUDA: CONEXIONES VPN*\n\n`;
  
  message += `*¿Qué es una VPN?*\n`;
  message += `Una Red Privada Virtual (VPN) cifra tu conexión a internet y protege tu privacidad.\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `*WireGuard* 🔐\n`;
  message += `• Protocolo moderno y veloz\n`;
  message += `• Ideal para uso diario\n`;
  message += `• Menor consumo de batería\n`;
  message += `• Conexión más estable\n\n`;
  
  message += `*Cómo usar WireGuard:*\n`;
  message += `1. Solicita una configuración: ${markdown.code('/vpn wireguard')}\n`;
  message += `2. Descarga la app: ${markdown.link('WireGuard', constants.URLS.WIREGUARD_DOWNLOAD)}\n`;
  message += `3. Importa el archivo ${markdown.code('.conf')} o escanea el código QR\n`;
  message += `4. Activa la conexión\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `*Outline* 🌐\n`;
  message += `• Fácil configuración\n`;
  message += `• Un solo clic para conectar\n`;
  message += `• Diseñado para evadir censura\n`;
  message += `• Multiplataforma\n\n`;
  
  message += `*Cómo usar Outline:*\n`;
  message += `1. Solicita una clave: ${markdown.code('/vpn outline')}\n`;
  message += `2. Descarga la app: ${markdown.link('Outline', constants.URLS.OUTLINE_DOWNLOAD)}\n`;
  message += `3. Copia y pega tu clave de acceso\n`;
  message += `4. Conéctate automáticamente\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `${constants.EMOJI.INFO} *Comandos útiles:*\n`;
  message += `• ${markdown.code('/vpn list')} - Ver tus conexiones\n`;
  message += `• ${markdown.code('/vpn delete')} - Eliminar una conexión\n`;
  message += `• ${markdown.code('/vpn stats')} - Ver estadísticas de uso\n\n`;
  
  message += `_¿Necesitas más ayuda? Contacta al administrador._`;
  
  return message;
}

// ============================================================================
// 👤 AYUDA: GESTIÓN DE PERFIL
// ============================================================================

function getProfileHelpMessage() {
  let message = `${constants.EMOJI.USER} *AYUDA: GESTIÓN DE PERFIL*\n\n`;
  
  message += `*Tu Perfil*\n`;
  message += `Aquí puedes ver y gestionar tu información de usuario.\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `*Comandos disponibles:*\n\n`;
  
  message += `${markdown.code('/profile')}\n`;
  message += `Muestra tu información completa:\n`;
  message += `• ID de usuario\n`;
  message += `• Nombre registrado\n`;
  message += `• Estado de autorización\n`;
  message += `• Conexiones VPN activas\n`;
  message += `• Uso de datos\n\n`;
  
  message += `${markdown.code('/settings')}\n`;
  message += `Configura tus preferencias:\n`;
  message += `• Notificaciones\n`;
  message += `• Idioma (próximamente)\n`;
  message += `• Formato de datos\n\n`;
  
  message += `${markdown.code('/stats')}\n`;
  message += `Estadísticas personales:\n`;
  message += `• Total de datos consumidos\n`;
  message += `• Tiempo de conexión\n`;
  message += `• Histórico de uso\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `${constants.EMOJI.INFO} *Información importante:*\n`;
  message += `• Tu ID es único e inmutable\n`;
  message += `• Los datos se actualizan cada 10 minutos\n`;
  message += `• Puedes solicitar un reporte completo al admin\n\n`;
  
  message += `_Para cambiar tu información, contacta al administrador._`;
  
  return message;
}

// ============================================================================
// ℹ️ AYUDA: INFORMACIÓN DEL SISTEMA
// ============================================================================

function getSystemInfoHelpMessage() {
  let message = `${constants.EMOJI.INFO} *AYUDA: INFORMACIÓN DEL SISTEMA*\n\n`;
  
  message += `*Acerca de uSipipo VPN*\n`;
  message += `Servicio de VPN privado y seguro para usuarios autorizados.\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `*Especificaciones del Servidor*\n\n`;
  
  message += `🌐 *IP del Servidor:* ${markdown.code(config.SERVER_IPV4 || 'Privada')}\n`;
  message += `🔐 *Puerto WireGuard:* ${markdown.code(String(config.WG_SERVER_PORT || 'N/A'))}\n`;
  message += `🌐 *Puerto Outline:* ${markdown.code(String(config.OUTLINE_KEYS_PORT || 'N/A'))}\n`;
  message += `🖥️ *Entorno:* ${markdown.code(config.NODE_ENV)}\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `*Límites de Uso*\n\n`;
  
  const wgLimit = process.env.WG_DATA_LIMIT_BYTES || (10 * 1024 * 1024 * 1024);
  const wgLimitGB = (Number(wgLimit) / (1024 * 1024 * 1024)).toFixed(0);
  
  const outlineLimit = process.env.OUTLINE_DATA_LIMIT_BYTES || (10 * 1024 * 1024 * 1024);
  const outlineLimitGB = (Number(outlineLimit) / (1024 * 1024 * 1024)).toFixed(0);
  
  message += `📊 *WireGuard:* ${wgLimitGB} GB/mes\n`;
  message += `📊 *Outline:* ${outlineLimitGB} GB/mes\n\n`;
  
  message += `_Los límites se reinician automáticamente cada mes._\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `*Comandos de Sistema*\n\n`;
  
  message += `${markdown.code('/status')}\n`;
  message += `Estado actual del servidor y servicios.\n\n`;
  
  message += `${markdown.code('/info')}\n`;
  message += `Información detallada del sistema.\n\n`;
  
  message += `${markdown.code('/ping')}\n`;
  message += `Verifica la conectividad con el servidor.\n\n`;
  
  message += `_Para reportar problemas, usa_ ${markdown.code('/report')}.`;
  
  return message;
}

// ============================================================================
// 👑 AYUDA: PANEL ADMINISTRATIVO (SOLO ADMIN)
// ============================================================================

function getAdminHelpMessage() {
  let message = `${constants.EMOJI.ADMIN} *AYUDA: PANEL ADMINISTRATIVO*\n\n`;
  
  message += `*Herramientas de Gestión*\n`;
  message += `Comandos exclusivos para administradores del sistema.\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `*Gestión de Usuarios*\n\n`;
  
  message += `${markdown.code('/admin users')}\n`;
  message += `Lista completa de usuarios autorizados.\n\n`;
  
  message += `${markdown.code('/admin add <userId>')}\n`;
  message += `Autorizar nuevo usuario.\n`;
  message += `_Ejemplo:_ ${markdown.code('/admin add 123456789')}\n\n`;
  
  message += `${markdown.code('/admin remove <userId>')}\n`;
  message += `Revocar acceso de un usuario.\n\n`;
  
  message += `${markdown.code('/admin promote <userId>')}\n`;
  message += `Promocionar usuario a administrador.\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `*Gestión de VPN*\n\n`;
  
  message += `${markdown.code('/admin vpn list')}\n`;
  message += `Ver todas las conexiones VPN activas.\n\n`;
  
  message += `${markdown.code('/admin vpn delete <userId>')}\n`;
  message += `Eliminar conexiones VPN de un usuario.\n\n`;
  
  message += `${markdown.code('/admin vpn stats')}\n`;
  message += `Estadísticas globales de uso.\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `*Monitoreo y Mantenimiento*\n\n`;
  
  message += `${markdown.code('/admin logs')}\n`;
  message += `Acceder a logs del sistema.\n\n`;
  
  message += `${markdown.code('/admin broadcast <mensaje>')}\n`;
  message += `Enviar mensaje a todos los usuarios.\n\n`;
  
  message += `${markdown.code('/admin cleanup')}\n`;
  message += `Limpiar datos huérfanos y optimizar almacenamiento.\n\n`;
  
  message += `${markdown.code('/admin backup')}\n`;
  message += `Generar respaldo de datos.\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `${constants.EMOJI.WARNING} *Precauciones:*\n`;
  message += `• Los comandos admin son irreversibles\n`;
  message += `• Todas las acciones quedan registradas\n`;
  message += `• Usa con responsabilidad\n\n`;
  
  message += `_Para soporte técnico avanzado, consulta la documentación._`;
  
  return message;
}

// ============================================================================
// 🔧 AYUDA: SOLUCIÓN DE PROBLEMAS
// ============================================================================

function getTroubleshootingHelpMessage() {
  let message = `${constants.EMOJI.SUCCESS} *SOLUCIÓN DE PROBLEMAS*\n\n`;
  
  message += `*Problemas comunes y sus soluciones:*\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `${constants.EMOJI.ERROR} *"No puedo conectarme a WireGuard"*\n\n`;
  
  message += `*Soluciones:*\n`;
  message += `1. Verifica que la app esté actualizada\n`;
  message += `2. Comprueba tu conexión a internet\n`;
  message += `3. Re-importa el archivo de configuración\n`;
  message += `4. Revisa que el puerto no esté bloqueado\n`;
  message += `5. Solicita una nueva configuración: ${markdown.code('/vpn wireguard')}\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `${constants.EMOJI.ERROR} *"Outline no conecta"*\n\n`;
  
  message += `*Soluciones:*\n`;
  message += `1. Copia correctamente la clave completa\n`;
  message += `2. Verifica tu firewall/antivirus\n`;
  message += `3. Prueba cambiar de red (WiFi/datos móviles)\n`;
  message += `4. Reinstala la app Outline\n`;
  message += `5. Solicita una nueva clave: ${markdown.code('/vpn outline')}\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `${constants.EMOJI.ERROR} *"Consumo de datos muy alto"*\n\n`;
  
  message += `*Posibles causas:*\n`;
  message += `• Apps de fondo consumiendo datos\n`;
  message += `• Streaming en alta calidad\n`;
  message += `• Descargas automáticas activas\n`;
  message += `• Sincronización en la nube\n\n`;
  
  message += `*Soluciones:*\n`;
  message += `1. Revisa tu uso: ${markdown.code('/stats')}\n`;
  message += `2. Cierra apps innecesarias\n`;
  message += `3. Configura límites de datos en tu dispositivo\n`;
  message += `4. Usa redes WiFi cuando sea posible\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `${constants.EMOJI.ERROR} *"El bot no responde"*\n\n`;
  
  message += `*Soluciones:*\n`;
  message += `1. Usa el comando ${markdown.code('/start')} para reiniciar\n`;
  message += `2. Verifica que tengas autorización activa\n`;
  message += `3. Espera unos minutos (puede estar en mantenimiento)\n`;
  message += `4. Contacta al administrador si persiste\n\n`;
  
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  message += `${constants.EMOJI.WARNING} *¿Nada funciona?*\n\n`;
  
  message += `Contacta al administrador con:\n`;
  message += `• Tu ID de usuario: ${markdown.code('/profile')}\n`;
  message += `• Descripción del problema\n`;
  message += `• Capturas de pantalla (si es posible)\n`;
  message += `• Hora aproximada del incidente\n\n`;
  
  message += `_El equipo de soporte responderá lo antes posible._`;
  
  return message;
}

// ============================================================================
// 📋 AYUDA: LISTA DE COMANDOS
// ============================================================================

function getCommandsListMessage(isAdmin = false) {
  let message = `${constants.EMOJI.INFO} *LISTA DE COMANDOS*\n\n`;
  
  message += `*Básicos*\n`;
  message += `${markdown.code('/start')} - Iniciar el bot\n`;
  message += `${markdown.code('/help')} - Centro de ayuda\n`;
  message += `${markdown.code('/menu')} - Menú principal\n\n`;
  
  message += `*VPN*\n`;
  message += `${markdown.code('/vpn')} - Gestionar VPN\n`;
  message += `${markdown.code('/vpn wireguard')} - Crear WireGuard\n`;
  message += `${markdown.code('/vpn outline')} - Crear Outline\n`;
  message += `${markdown.code('/vpn list')} - Listar conexiones\n`;
  message += `${markdown.code('/vpn delete')} - Eliminar conexión\n`;
  message += `${markdown.code('/vpn stats')} - Ver estadísticas\n\n`;
  
  message += `*Usuario*\n`;
  message += `${markdown.code('/profile')} - Mi perfil\n`;
  message += `${markdown.code('/settings')} - Configuración\n`;
  message += `${markdown.code('/stats')} - Mis estadísticas\n\n`;
  
  message += `*Sistema*\n`;
  message += `${markdown.code('/status')} - Estado del servidor\n`;
  message += `${markdown.code('/info')} - Información del sistema\n`;
  message += `${markdown.code('/ping')} - Verificar conectividad\n\n`;
  
  if (isAdmin) {
    message += `*Administración*\n`;
    message += `${markdown.code('/admin')} - Panel admin\n`;
    message += `${markdown.code('/admin users')} - Gestionar usuarios\n`;
    message += `${markdown.code('/admin vpn')} - Gestionar VPN\n`;
    message += `${markdown.code('/admin logs')} - Ver logs\n`;
    message += `${markdown.code('/admin broadcast')} - Enviar anuncio\n`;
    message += `${markdown.code('/admin backup')} - Respaldar datos\n\n`;
  }
  
  message += `_Usa_ ${markdown.code('/help <categoría>')} _para más detalles._`;
  
  return message;
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  getMainHelpMessage,
  getVPNHelpMessage,
  getProfileHelpMessage,
  getSystemInfoHelpMessage,
  getAdminHelpMessage,
  getTroubleshootingHelpMessage,
  getCommandsListMessage
};
