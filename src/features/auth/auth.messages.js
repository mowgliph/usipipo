'use strict';

/**
 * ============================================================================
 * 💬 AUTH MESSAGES - uSipipo VPN Bot
 * ============================================================================
 * Mensajes específicos del módulo de autenticación.
 * Usa Markdown V1 para compatibilidad total.
 * ============================================================================
 */

const markdown = require('../../../core/utils/markdown');
const constants = require('../../../config/constants');
const config = require('../../../config/environment');

// ============================================================================
// 🔐 MENSAJES DE AUTENTICACIÓN
// ============================================================================

/**
 * Mensaje de bienvenida para usuarios no autorizados
 */
function getUnauthorizedWelcomeMessage(user) {
  const userName = markdown.escapeMarkdown(user.first_name || 'Usuario');
  const userId = user.id;
  const username = user.username ? `@${markdown.escapeMarkdown(user.username)}` : 'N/A';

  return `${constants.EMOJI.WARNING} *Acceso Restringido*\n\n` +
         `Hola *${userName}*, bienvenido a *uSipipo VPN Bot*.\n\n` +
         `${constants.EMOJI.INFO} *Tu Información:*\n` +
         `• *Nombre:* ${userName}\n` +
         `• *Username:* ${username}\n` +
         `• *ID:* ${markdown.code(userId)}\n\n` +
         `${constants.EMOJI.ERROR} *Estado:* No autorizado\n\n` +
         `━━━━━━━━━━━━━━━━━━━━\n\n` +
         `Para usar este bot necesitas autorización del administrador.\n\n` +
         `Tu solicitud ha sido enviada automáticamente. ` +
         `Recibirás una notificación cuando seas aprobado.\n\n` +
         `_Si tienes dudas, contacta al administrador._`;
}

/**
 * Mensaje de bienvenida para usuarios autorizados
 */
function getAuthorizedWelcomeMessage(user, role = 'user') {
  const userName = markdown.escapeMarkdown(user.first_name || 'Usuario');
  const userId = user.id;
  const username = user.username ? `@${markdown.escapeMarkdown(user.username)}` : 'N/A';
  
  const roleEmoji = role === 'admin' ? constants.EMOJI.ADMIN : constants.EMOJI.USER;
  const roleText = role === 'admin' ? 'Administrador' : 'Usuario Autorizado';

  return `${constants.EMOJI.SUCCESS} *¡Acceso Concedido!*\n\n` +
         `Bienvenido de nuevo, *${userName}*\n\n` +
         `${constants.EMOJI.INFO} *Tu Información:*\n` +
         `• *Nombre:* ${userName}\n` +
         `• *Username:* ${username}\n` +
         `• *ID:* ${markdown.code(userId)}\n` +
         `• *Rol:* ${roleEmoji} ${roleText}\n\n` +
         `━━━━━━━━━━━━━━━━━━━━\n\n` +
         `${constants.EMOJI.VPN} *Servicios Disponibles:*\n` +
         `• WireGuard VPN\n` +
         `• Outline VPN\n` +
         `• Gestión de conexiones\n` +
         `• Soporte 24/7\n\n` +
         `Usa /menu para ver todas las opciones disponibles.`;
}

/**
 * Notificación al admin sobre nueva solicitud de acceso
 */
function getAccessRequestNotification(user) {
  const userName = markdown.escapeMarkdown(user.first_name || 'Sin nombre');
  const lastName = user.last_name ? markdown.escapeMarkdown(user.last_name) : '';
  const fullName = lastName ? `${userName} ${lastName}` : userName;
  const username = user.username ? `@${markdown.escapeMarkdown(user.username)}` : 'Sin username';
  const userId = user.id;
  const languageCode = user.language_code || 'Desconocido';

  return `${constants.EMOJI.WARNING} *Nueva Solicitud de Acceso*\n\n` +
         `${constants.EMOJI.USER} *Información del Usuario:*\n` +
         `• *Nombre:* ${fullName}\n` +
         `• *Username:* ${username}\n` +
         `• *ID:* ${markdown.code(userId)}\n` +
         `• *Idioma:* ${markdown.code(languageCode)}\n\n` +
         `━━━━━━━━━━━━━━━━━━━━\n\n` +
         `${constants.EMOJI.ADMIN} *Acciones Disponibles:*\n\n` +
         `• Para *autorizar*: ${markdown.code(`/add ${userId}`)}\n` +
         `• Para *rechazar*: ${markdown.code(`/block ${userId}`)}\n` +
         `• Para *info*: ${markdown.code(`/userinfo ${userId}`)}\n\n` +
         `_El usuario está esperando tu respuesta._`;
}

/**
 * Mensaje de éxito al autorizar un usuario
 */
function getUserAuthorizedMessage(targetUser, authorizedBy) {
  const userName = markdown.escapeMarkdown(targetUser.first_name || 'Usuario');
  const userId = targetUser.id;
  const adminName = markdown.escapeMarkdown(authorizedBy.first_name || 'Admin');

  return `${constants.EMOJI.SUCCESS} *Usuario Autorizado*\n\n` +
         `El usuario *${userName}* ${markdown.code(userId)} ha sido autorizado exitosamente.\n\n` +
         `*Autorizado por:* ${adminName}\n` +
         `*Fecha:* ${markdown.code(new Date().toLocaleString('es-ES'))}\n\n` +
         `El usuario recibirá una notificación y podrá comenzar a usar el bot.`;
}

/**
 * Notificación al usuario cuando es autorizado
 */
function getUserWasAuthorizedNotification() {
  return `${constants.EMOJI.SUCCESS} *¡Felicitaciones!*\n\n` +
         `Tu solicitud de acceso ha sido *aprobada*.\n\n` +
         `Ahora tienes acceso completo a todos los servicios VPN:\n\n` +
         `${constants.EMOJI.VPN} *Servicios Disponibles:*\n` +
         `• WireGuard VPN\n` +
         `• Outline VPN\n` +
         `• Gestión de conexiones\n` +
         `• Soporte técnico\n\n` +
         `Usa /menu para comenzar o /help para ver la guía completa.\n\n` +
         `_¡Bienvenido a uSipipo VPN!_`;
}

/**
 * Mensaje de error al autorizar usuario
 */
function getAuthorizationErrorMessage(error) {
  return `${constants.EMOJI.ERROR} *Error en Autorización*\n\n` +
         `No se pudo completar la autorización del usuario.\n\n` +
         `*Detalle:* ${markdown.code(error.message || 'Error desconocido')}\n\n` +
         `Por favor, verifica los datos e intenta nuevamente.`;
}

/**
 * Mensaje cuando el usuario ya está autorizado
 */
function getAlreadyAuthorizedMessage(userId) {
  return `${constants.EMOJI.INFO} *Usuario Ya Autorizado*\n\n` +
         `El usuario ${markdown.code(userId)} ya se encuentra en la lista de autorizados.\n\n` +
         `No es necesario realizar ninguna acción adicional.`;
}

/**
 * Mensaje de información del sistema de autorización
 */
function getAuthSystemInfoMessage() {
  const totalAuthorized = config.AUTHORIZED_USERS.length;
  const adminId = config.ADMIN_ID || 'No definido';

  return `${constants.EMOJI.INFO} *Sistema de Autorización*\n\n` +
         `${constants.EMOJI.ADMIN} *Administrador Principal:*\n` +
         `• ID: ${markdown.code(adminId)}\n\n` +
         `${constants.EMOJI.USER} *Usuarios Autorizados:*\n` +
         `• Total: ${markdown.bold(String(totalAuthorized))}\n\n` +
         `━━━━━━━━━━━━━━━━━━━━\n\n` +
         `*Funcionamiento:*\n\n` +
         `1. Los usuarios no autorizados reciben un mensaje de acceso denegado\n` +
         `2. Se envía notificación automática al administrador\n` +
         `3. El admin puede aprobar o rechazar solicitudes\n` +
         `4. Los usuarios aprobados reciben notificación inmediata\n\n` +
         `Usa /listusers para ver todos los usuarios autorizados.`;
}

/**
 * Mensaje de lista de usuarios autorizados
 */
function getAuthorizedUsersListMessage(users) {
  if (!users || users.length === 0) {
    return `${constants.EMOJI.WARNING} *Lista Vacía*\n\n` +
           `No hay usuarios autorizados en el sistema.\n\n` +
           `Usa ${markdown.code('/add <user_id>')} para autorizar usuarios.`;
  }

  let message = `${constants.EMOJI.USER} *Usuarios Autorizados* (${users.length})\n\n`;
  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;

  users.forEach((user, index) => {
    const userName = user.name ? markdown.escapeMarkdown(user.name) : 'Sin nombre';
    const roleEmoji = user.role === 'admin' ? constants.EMOJI.ADMIN : constants.EMOJI.USER;
    const roleText = user.role === 'admin' ? 'Admin' : 'Usuario';
    
    message += `${index + 1}. ${roleEmoji} *${userName}*\n`;
    message += `   • ID: ${markdown.code(user.id)}\n`;
    message += `   • Rol: ${roleText}\n`;
    message += `   • Estado: ${user.status === 'active' ? '✅ Activo' : '⏸ Inactivo'}\n`;
    
    if (user.addedAt) {
      const date = new Date(user.addedAt).toLocaleDateString('es-ES');
      message += `   • Agregado: ${markdown.code(date)}\n`;
    }
    
    message += '\n';
  });

  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  message += `Usa ${markdown.code('/userinfo <id>')} para ver detalles de un usuario.`;

  return message;
}

/**
 * Mensaje detallado de información de usuario
 */
function getUserDetailedInfoMessage(user) {
  const userName = user.name ? markdown.escapeMarkdown(user.name) : 'Sin nombre';
  const roleEmoji = user.role === 'admin' ? constants.EMOJI.ADMIN : constants.EMOJI.USER;
  const roleText = user.role === 'admin' ? 'Administrador' : 'Usuario';
  const statusEmoji = user.status === 'active' ? '✅' : '⏸';
  const statusText = user.status === 'active' ? 'Activo' : 'Inactivo';

  let message = `${roleEmoji} *Información del Usuario*\n\n`;
  message += `*Datos Básicos:*\n`;
  message += `• Nombre: ${userName}\n`;
  message += `• ID: ${markdown.code(user.id)}\n`;
  message += `• Rol: ${roleText}\n`;
  message += `• Estado: ${statusEmoji} ${statusText}\n\n`;

  if (user.addedAt) {
    const addedDate = new Date(user.addedAt).toLocaleString('es-ES');
    message += `*Registro:*\n`;
    message += `• Agregado: ${markdown.code(addedDate)}\n`;
    message += `• Por: ${markdown.code(user.addedBy || 'Sistema')}\n\n`;
  }

  if (user.wg || user.outline) {
    message += `*Servicios VPN:*\n`;
    
    if (user.wg) {
      message += `• ${constants.EMOJI.VPN} WireGuard: ✅ Configurado\n`;
      message += `  - IP: ${markdown.code(user.wg.ip || 'N/A')}\n`;
    }
    
    if (user.outline) {
      message += `• ${constants.EMOJI.SERVER} Outline: ✅ Configurado\n`;
      message += `  - Key ID: ${markdown.code(user.outline.keyId || 'N/A')}\n`;
    }
    
    message += '\n';
  }

  message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
  message += `Usa ${markdown.code('/menu')} para gestionar este usuario.`;

  return message;
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // Welcome Messages
  getUnauthorizedWelcomeMessage,
  getAuthorizedWelcomeMessage,
  
  // Admin Notifications
  getAccessRequestNotification,
  getUserAuthorizedMessage,
  getUserWasAuthorizedNotification,
  
  // Error Messages
  getAuthorizationErrorMessage,
  getAlreadyAuthorizedMessage,
  
  // Info Messages
  getAuthSystemInfoMessage,
  getAuthorizedUsersListMessage,
  getUserDetailedInfoMessage
};
