'use strict';

/**
 * ============================================================================
 * 👑 ADMIN MESSAGES - uSipipo VPN Bot
 * ============================================================================
 * Mensajes específicos para funciones administrativas.
 * Todos los mensajes utilizan Markdown V1 para compatibilidad total.
 * ============================================================================
 */

const markdown = require('../../../core/utils/markdown');
const constants = require('../../../config/constants');
const config = require('../../../config/environment');

// ============================================================================
// 🏠 MENSAJES DE BIENVENIDA ADMIN
// ============================================================================

function getAdminWelcomeMessage(adminName) {
  return `${constants.EMOJI.ADMIN} *Panel de Administración*\n\n` +
         `Bienvenido, ${markdown.bold(markdown.escapeMarkdown(adminName))}\n\n` +
         `Desde aquí puedes:\n` +
         `• Gestionar usuarios autorizados\n` +
         `• Ver estadísticas del sistema\n` +
         `• Administrar conexiones VPN\n` +
         `• Enviar notificaciones\n` +
         `• Consultar logs y estado\n\n` +
         `Usa los botones o comandos para navegar.`;
}

function getAdminMenuMessage() {
  return `${constants.EMOJI.ADMIN} *Menú de Administración*\n\n` +
         `Selecciona una opción del menú:`;
}

// ============================================================================
// 👥 GESTIÓN DE USUARIOS
// ============================================================================

function getUserListMessage(users, page = 1, pageSize = 10) {
  if (!users || users.length === 0) {
    return `${constants.EMOJI.WARNING} *No hay usuarios registrados*\n\n` +
           `El sistema aún no tiene usuarios autorizados.`;
  }

  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const pageUsers = users.slice(start, end);
  const totalPages = Math.ceil(users.length / pageSize);

  let msg = `${constants.EMOJI.USER} *Lista de Usuarios* (Página ${page}/${totalPages})\n\n`;
  msg += `*Total:* ${users.length} usuarios\n`;
  msg += `━━━━━━━━━━━━━━━━━━━━\n\n`;

  pageUsers.forEach((user, index) => {
    const num = start + index + 1;
    const role = user.role === 'admin' ? '👑' : '👤';
    const status = user.status === 'active' ? '✅' : '⛔';
    const name = user.name || 'Sin nombre';
    
    msg += `${num}. ${role} ${status} ${markdown.bold(markdown.escapeMarkdown(name))}\n`;
    msg += `   ID: ${markdown.code(user.id)}\n`;
    msg += `   Rol: ${markdown.escapeMarkdown(user.role)}\n`;
    
    if (user.wg) {
      msg += `   🔐 WireGuard: ${markdown.code(user.wg.clientName || 'N/A')}\n`;
    }
    if (user.outline) {
      msg += `   🌐 Outline: ${markdown.code(user.outline.keyId || 'N/A')}\n`;
    }
    
    msg += `\n`;
  });

  return msg.trim();
}

function getUserDetailMessage(user) {
  if (!user) {
    return `${constants.EMOJI.ERROR} *Usuario no encontrado*\n\n` +
           `El usuario solicitado no existe en el sistema.`;
  }

  const roleIcon = user.role === 'admin' ? '👑' : '👤';
  const statusIcon = user.status === 'active' ? '✅' : '⛔';
  const name = user.name || 'Sin nombre';

  let msg = `${roleIcon} *Detalle de Usuario*\n\n`;
  msg += `*Nombre:* ${markdown.escapeMarkdown(name)}\n`;
  msg += `*ID:* ${markdown.code(user.id)}\n`;
  msg += `*Rol:* ${markdown.escapeMarkdown(user.role)}\n`;
  msg += `*Estado:* ${statusIcon} ${markdown.escapeMarkdown(user.status)}\n`;
  msg += `*Agregado:* ${markdown.escapeMarkdown(user.addedAt ? new Date(user.addedAt).toLocaleString('es-ES') : 'N/A')}\n`;
  msg += `*Por:* ${markdown.escapeMarkdown(user.addedBy || 'Sistema')}\n\n`;

  msg += `*━━ Servicios VPN ━━*\n\n`;

  if (user.wg) {
    msg += `🔐 *WireGuard:*\n`;
    msg += `   Cliente: ${markdown.code(user.wg.clientName || 'N/A')}\n`;
    msg += `   IP: ${markdown.code(user.wg.ip || 'N/A')}\n`;
    msg += `   Última conexión: ${markdown.escapeMarkdown(user.wg.lastSeen ? new Date(user.wg.lastSeen).toLocaleString('es-ES') : 'Nunca')}\n`;
    
    if (user.wg.suspended) {
      msg += `   ⚠️ Estado: SUSPENDIDO\n`;
      msg += `   Suspendido: ${markdown.escapeMarkdown(new Date(user.wg.suspendedAt).toLocaleString('es-ES'))}\n`;
    }
    msg += `\n`;
  } else {
    msg += `🔐 WireGuard: No configurado\n\n`;
  }

  if (user.outline) {
    msg += `🌐 *Outline:*\n`;
    msg += `   Key ID: ${markdown.code(user.outline.keyId || 'N/A')}\n`;
    msg += `   Nombre: ${markdown.escapeMarkdown(user.outline.name || 'N/A')}\n`;
    msg += `   Uso: ${markdown.escapeMarkdown(formatBytes(user.outline.usedBytes || 0))}\n`;
    
    if (user.outline.suspended) {
      msg += `   ⚠️ Estado: SUSPENDIDO\n`;
      msg += `   Suspendido: ${markdown.escapeMarkdown(new Date(user.outline.suspendedAt).toLocaleString('es-ES'))}\n`;
    }
    msg += `\n`;
  } else {
    msg += `🌐 Outline: No configurado\n\n`;
  }

  return msg.trim();
}

function getUserAddedMessage(userId, userName) {
  return `${constants.EMOJI.SUCCESS} *Usuario agregado*\n\n` +
         `*Nombre:* ${markdown.escapeMarkdown(userName)}\n` +
         `*ID:* ${markdown.code(userId)}\n\n` +
         `El usuario ahora está autorizado para usar el bot.`;
}

function getUserRemovedMessage(userId) {
  return `${constants.EMOJI.SUCCESS} *Usuario eliminado*\n\n` +
         `*ID:* ${markdown.code(userId)}\n\n` +
         `El usuario ha sido desautorizado y ya no puede usar el bot.`;
}

function getUserRoleChangedMessage(userId, newRole) {
  const roleIcon = newRole === 'admin' ? '👑' : '👤';
  return `${constants.EMOJI.SUCCESS} *Rol actualizado*\n\n` +
         `*ID:* ${markdown.code(userId)}\n` +
         `*Nuevo rol:* ${roleIcon} ${markdown.escapeMarkdown(newRole)}\n\n` +
         `Los permisos del usuario han sido actualizados.`;
}

// ============================================================================
// 📊 ESTADÍSTICAS DEL SISTEMA
// ============================================================================

function getSystemStatsMessage(stats) {
  let msg = `${constants.EMOJI.INFO} *Estadísticas del Sistema*\n\n`;
  
  msg += `*━━ Usuarios ━━*\n`;
  msg += `Total: ${markdown.code(String(stats.total))}\n`;
  msg += `Activos: ${markdown.code(String(stats.active))} ✅\n`;
  msg += `Suspendidos: ${markdown.code(String(stats.suspended))} ⛔\n`;
  msg += `Administradores: ${markdown.code(String(stats.admins))} 👑\n`;
  msg += `Usuarios: ${markdown.code(String(stats.users))} 👤\n\n`;
  
  msg += `*━━ Servicios VPN ━━*\n`;
  msg += `Con WireGuard: ${markdown.code(String(stats.withWireGuard))} 🔐\n`;
  msg += `Con Outline: ${markdown.code(String(stats.withOutline))} 🌐\n`;
  msg += `Con ambos: ${markdown.code(String(stats.withBothVpn))} 🔐🌐\n\n`;
  
  msg += `*━━ Servidor ━━*\n`;
  msg += `IP: ${markdown.code(config.SERVER_IP)}\n`;
  msg += `Entorno: ${markdown.code(config.NODE_ENV)}\n`;
  msg += `WireGuard Port: ${markdown.code(String(config.WG_SERVER_PORT))}\n`;
  msg += `Outline API: ${markdown.code(String(config.OUTLINE_API_PORT))}\n`;

  return msg;
}

function getSystemHealthMessage(health) {
  const statusIcon = health.status === 'healthy' ? '✅' : '⚠️';
  
  let msg = `${statusIcon} *Estado del Sistema*\n\n`;
  msg += `*Estado general:* ${markdown.escapeMarkdown(health.status)}\n`;
  msg += `*Uptime:* ${markdown.escapeMarkdown(health.uptime)}\n`;
  msg += `*Memoria:* ${markdown.escapeMarkdown(health.memory)}\n`;
  msg += `*CPU:* ${markdown.escapeMarkdown(health.cpu)}\n\n`;
  
  msg += `*━━ Servicios ━━*\n`;
  msg += `WireGuard: ${health.wireguard ? '✅' : '❌'}\n`;
  msg += `Outline: ${health.outline ? '✅' : '❌'}\n`;
  msg += `Database: ${health.database ? '✅' : '❌'}\n`;

  return msg;
}

// ============================================================================
// 📢 NOTIFICACIONES Y BROADCAST
// ============================================================================

function getBroadcastSentMessage(results) {
  return `${constants.EMOJI.SUCCESS} *Broadcast enviado*\n\n` +
         `Exitosos: ${markdown.code(String(results.success))} ✅\n` +
         `Fallidos: ${markdown.code(String(results.failed))} ❌\n\n` +
         `El mensaje ha sido enviado a todos los usuarios activos.`;
}

function getNotificationSentMessage(userId) {
  return `${constants.EMOJI.SUCCESS} *Notificación enviada*\n\n` +
         `El mensaje ha sido enviado al usuario ${markdown.code(userId)}.`;
}

// ============================================================================
// 🔧 MANTENIMIENTO
// ============================================================================

function getMaintenanceModeMessage(enabled) {
  if (enabled) {
    return `${constants.EMOJI.WARNING} *Modo mantenimiento activado*\n\n` +
           `El bot está ahora en modo mantenimiento. ` +
           `Los usuarios no podrán realizar operaciones hasta que se desactive.`;
  } else {
    return `${constants.EMOJI.SUCCESS} *Modo mantenimiento desactivado*\n\n` +
           `El bot ha vuelto a operación normal.`;
  }
}

function getCleanupCompletedMessage(results) {
  return `${constants.EMOJI.SUCCESS} *Limpieza completada*\n\n` +
         `Entradas WireGuard eliminadas: ${markdown.code(String(results.wg))}\n` +
         `Entradas Outline eliminadas: ${markdown.code(String(results.outline))}\n\n` +
         `Datos huérfanos limpiados correctamente.`;
}

// ============================================================================
// ⚠️ MENSAJES DE ERROR ADMIN
// ============================================================================

function getInvalidUserIdMessage() {
  return `${constants.EMOJI.ERROR} *ID de usuario inválido*\n\n` +
         `Proporciona un ID de usuario válido.\n\n` +
         `Formato: ${markdown.code('/add <userId>')}\n` +
         `Ejemplo: ${markdown.code('/add 123456789')}`;
}

function getUserAlreadyExistsMessage(userId) {
  return `${constants.EMOJI.WARNING} *Usuario ya existe*\n\n` +
         `El usuario ${markdown.code(userId)} ya está autorizado en el sistema.`;
}

function getUserNotFoundMessage(userId) {
  return `${constants.EMOJI.ERROR} *Usuario no encontrado*\n\n` +
         `El usuario ${markdown.code(userId)} no existe en el sistema.`;
}

function getCannotRemoveSelfMessage() {
  return `${constants.EMOJI.ERROR} *Acción no permitida*\n\n` +
         `No puedes eliminarte a ti mismo del sistema.`;
}

function getCannotRemoveMainAdminMessage() {
  return `${constants.EMOJI.ERROR} *Acción no permitida*\n\n` +
         `No puedes eliminar al administrador principal del sistema.`;
}

// ============================================================================
// 🛠️ UTILIDADES
// ============================================================================

function formatBytes(bytes) {
  if (!bytes || isNaN(bytes) || bytes <= 0) return '0 B';
  const k = 1024;
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const unit = units[i] || 'TB';
  const value = (bytes / Math.pow(k, i)).toFixed(2);
  return `${value} ${unit}`;
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // Welcome
  getAdminWelcomeMessage,
  getAdminMenuMessage,

  // User Management
  getUserListMessage,
  getUserDetailMessage,
  getUserAddedMessage,
  getUserRemovedMessage,
  getUserRoleChangedMessage,

  // Statistics
  getSystemStatsMessage,
  getSystemHealthMessage,

  // Notifications
  getBroadcastSentMessage,
  getNotificationSentMessage,

  // Maintenance
  getMaintenanceModeMessage,
  getCleanupCompletedMessage,

  // Errors
  getInvalidUserIdMessage,
  getUserAlreadyExistsMessage,
  getUserNotFoundMessage,
  getCannotRemoveSelfMessage,
  getCannotRemoveMainAdminMessage
};
