'use strict';

/**
 * ============================================================================
 * 💬 COMMON MESSAGES - uSipipo VPN Bot
 * ============================================================================
 * Mensajes centralizados y reutilizables para todo el sistema.
 * 
 * 📌 PRINCIPIOS DE DISEÑO:
 * 1. Consistencia en tono y formato
 * 2. Uso de Markdown V1 para compatibilidad total
 * 3. Emojis de constants.js para consistencia visual
 * 4. Mensajes parametrizables para personalización
 * ============================================================================
 */

const markdown = require('../../core/utils/markdown');
const constants = require('../../config/constants');
const config = require('../../config/environment');

// ============================================================================
// 🏠 MENSAJES DE BIENVENIDA Y MENÚ
// ============================================================================

function getWelcomeMessage(userName = 'Usuario') {
  return `${constants.EMOJI.SUCCESS} *Bienvenido a uSipipo VPN, ${markdown.escapeMarkdown(userName)}!*\n\n` +
         `*Tu acceso seguro a internet* 🔐\n\n` +
         `Con este bot puedes gestionar tus conexiones VPN de forma sencilla:\n` +
         `• WireGuard (rápido y moderno)\n` +
         `• Outline (fácil y seguro)\n\n` +
         `Usa el menú o escribe /help para ver los comandos disponibles.`;
}

function getAuthorizedWelcomeMessage(userName, userId) {
  return `${constants.EMOJI.SUCCESS} *Bienvenido de nuevo, ${markdown.escapeMarkdown(userName)}!*\n\n` +
         `*Tu ID:* ${markdown.code(userId)}\n` +
         `*Estado:* ${constants.STATUS.AUTHORIZED}\n\n` +
         `Ya puedes comenzar a usar el bot. Escribe /menu para ver las opciones.`;
}

function getUnauthorizedMessage(userName, userId) {
  return `${constants.EMOJI.ERROR} *Acceso denegado*\n\n` +
         `Lo siento, *${markdown.escapeMarkdown(userName)}*, no estás autorizado para usar este bot.\n\n` +
         `*Tu ID:* ${markdown.code(userId)}\n` +
         `*Estado:* ${constants.STATUS.UNAUTHORIZED}\n\n` +
         `Contacta al administrador para solicitar acceso.`;
}

// ============================================================================
// 🚨 MENSAJES DE ERROR
// ============================================================================

function getGenericErrorMessage() {
  return `${constants.EMOJI.ERROR} *Error del sistema*\n\n` +
         `Se ha producido un error inesperado. ` +
         `El equipo técnico ha sido notificado.\n\n` +
         `Por favor, intenta de nuevo más tarde.`;
}

function getNotFoundMessage(item = 'recurso') {
  return `${constants.EMOJI.WARNING} *No encontrado*\n\n` +
         `El ${item} solicitado no existe o ha sido eliminado.`;
}

function getAccessDeniedMessage() {
  return `${constants.EMOJI.ERROR} *Acceso denegado*\n\n` +
         `No tienes permisos para realizar esta acción.`;
}

function getAdminOnlyMessage() {
  return `${constants.EMOJI.ERROR} *Acceso restringido*\n\n` +
         `Esta función es exclusiva para administradores.`;
}

// ============================================================================
// ℹ️ MENSAJES DE INFORMACIÓN
// ============================================================================

function getSystemStatusMessage() {
  return `${constants.EMOJI.INFO} *Estado del sistema*\n\n` +
         `*Servidor:* ${markdown.code(config.SERVER_IP || 'N/A')}\n` +
         `*Entorno:* ${markdown.code(config.NODE_ENV)}\n` +
         `*Usuarios autorizados:* ${config.AUTHORIZED_USERS.length}\n` +
         `*Admin:* ${config.ADMIN_ID || 'No definido'}`;
}

function getHelpMessage() {
  return `${constants.EMOJI.INFO} *Ayuda - Comandos disponibles*\n\n` +
         `*/start* - Iniciar el bot\n` +
         `*/menu* - Mostrar menú principal\n` +
         `*/help* - Mostrar esta ayuda\n` +
         `*/status* - Estado del sistema\n` +
         `*/vpn* - Gestionar conexiones VPN\n` +
         `*/profile* - Ver tu perfil\n\n` +
         `Para soporte, contacta al administrador.`;
}

function getCommandsListMessage() {
  return `${constants.EMOJI.INFO} *Lista de comandos*\n\n` +
         `*Básicos:*\n` +
         `• /start - Iniciar bot\n` +
         `• /help - Ayuda\n` +
         `• /menu - Menú principal\n` +
         `• /status - Estado sistema\n\n` +
         `*VPN:*\n` +
         `• /vpn - Gestionar VPN\n` +
         `• /wireguard - WireGuard\n` +
         `• /outline - Outline\n\n` +
         `*Usuario:*\n` +
         `• /profile - Mi perfil\n` +
         `• /settings - Configuración`;
}

// ============================================================================
// ✅ MENSAJES DE CONFIRMACIÓN
// ============================================================================

function getOperationSuccessMessage(operation = 'Operación') {
  return `${constants.EMOJI.SUCCESS} *${operation} completada*\n\n` +
         `La operación se ha realizado correctamente.`;
}

function getOperationFailedMessage(operation = 'Operación') {
  return `${constants.EMOJI.ERROR} *${operation} fallida*\n\n` +
         `No se pudo completar la operación. Intenta de nuevo.`;
}

function getConfirmationMessage(action = 'esta acción') {
  return `${constants.EMOJI.WARNING} *Confirmación requerida*\n\n` +
         `¿Estás seguro de que deseas ${action}?\n\n` +
         `Esta acción no se puede deshacer.`;
}

// ============================================================================
// 🛠️ MENSAJES DE SISTEMA
// ============================================================================

function getMaintenanceMessage() {
  return `${constants.EMOJI.WARNING} *Mantenimiento programado*\n\n` +
         `El sistema está en mantenimiento. ` +
         `Por favor, vuelve más tarde.\n\n` +
         `Disculpa las molestias.`;
}

function getUpdateMessage() {
  return `${constants.EMOJI.INFO} *Actualización disponible*\n\n` +
         `Hay una nueva versión del bot disponible. ` +
         `Algunas funciones pueden no estar operativas.\n\n` +
         `Actualiza para obtener las últimas características.`;
}

function getLogsInfoMessage() {
  return `${constants.EMOJI.INFO} *Registros del sistema*\n\n` +
         `Todos los accesos y acciones quedan registrados para:\n` +
         `• Seguridad\n` +
         `• Auditoría\n` +
         `• Resolución de problemas\n\n` +
         `No se almacenan datos personales sensibles.`;
}
// ============================================================================
// 🚨 QUOTA MESSAGES
// ============================================================================

function getQuotaWarningWG({ percentage, clientName, usedBytes, limitBytes }) {
  const usedGB = (usedBytes / (1024 * 1024 * 1024)).toFixed(2);
  const limitGB = (limitBytes / (1024 * 1024 * 1024)).toFixed(2);
  return `${constants.EMOJI.WARNING} *Advertencia de Cuota - WireGuard*\n\n` +
         `Cliente: ${markdown.code(clientName)}\n` +
         `Uso: ${usedGB} GB / ${limitGB} GB (${percentage}%)\n\n` +
         `Has alcanzado el ${percentage}% de tu límite de datos.\n` +
         `Considera reducir el uso o contactar al administrador.`;
}

function getQuotaExceededWG({ clientName, usedBytes, limitBytes }) {
  const usedGB = (usedBytes / (1024 * 1024 * 1024)).toFixed(2);
  const limitGB = (limitBytes / (1024 * 1024 * 1024)).toFixed(2);
  return `${constants.EMOJI.ERROR} *Cuota Excedida - WireGuard Suspendido*\n\n` +
         `Cliente: ${markdown.code(clientName)}\n` +
         `Uso: ${usedGB} GB / ${limitGB} GB\n\n` +
         `Has excedido tu límite de datos. El servicio ha sido suspendido.\n` +
         `Contacta al administrador para reactivar o aumentar la cuota.`;
}

function getQuotaWarningOutline({ percentage, keyName, usedBytes, limitBytes }) {
  const usedGB = (usedBytes / (1024 * 1024 * 1024)).toFixed(2);
  const limitGB = (limitBytes / (1024 * 1024 * 1024)).toFixed(2);
  return `${constants.EMOJI.WARNING} *Advertencia de Cuota - Outline*\n\n` +
         `Clave: ${markdown.code(keyName)}\n` +
         `Uso: ${usedGB} GB / ${limitGB} GB (${percentage}%)\n\n` +
         `Has alcanzado el ${percentage}% de tu límite de datos.\n` +
         `Considera reducir el uso o contactar al administrador.`;
}

function getQuotaExceededOutline({ keyName, usedBytes, limitBytes }) {
  const usedGB = (usedBytes / (1024 * 1024 * 1024)).toFixed(2);
  const limitGB = (limitBytes / (1024 * 1024 * 1024)).toFixed(2);
  return `${constants.EMOJI.ERROR} *Cuota Excedida - Outline Suspendido*\n\n` +
         `Clave: ${markdown.code(keyName)}\n` +
         `Uso: ${usedGB} GB / ${limitGB} GB\n\n` +
         `Has excedido tu límite de datos. El servicio ha sido suspendido.\n` +
         `Contacta al administrador para reactivar o aumentar la cuota.`;
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // Welcome Messages
  getWelcomeMessage,
  getAuthorizedWelcomeMessage,
  getUnauthorizedMessage,

  // Error Messages
  getGenericErrorMessage,
  getNotFoundMessage,
  getAccessDeniedMessage,
  getAdminOnlyMessage,

  // Information Messages
  getSystemStatusMessage,
  getHelpMessage,
  getCommandsListMessage,

  // Confirmation Messages
  getOperationSuccessMessage,
  getOperationFailedMessage,
  getConfirmationMessage,

  // System Messages
  getMaintenanceMessage,
  getUpdateMessage,
  getLogsInfoMessage,

  // Quota Messages
  getQuotaWarningWG,
  getQuotaExceededWG,
  getQuotaWarningOutline,
  getQuotaExceededOutline
};