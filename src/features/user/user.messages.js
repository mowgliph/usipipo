'use strict';

/**
 * ============================================================================
 * 💬 USER MESSAGES - uSipipo VPN Bot
 * ============================================================================
 * Mensajes específicos del módulo de usuario.
 * Separado de common.messages.js para mantener modularidad.
 * ============================================================================
 */

const markdown = require('../../core/utils/markdown');
const constants = require('../../config/constants');

// ============================================================================
// 👤 PERFIL DE USUARIO
// ============================================================================

function getProfileHeader(userName = 'Usuario') {
  return `${constants.EMOJI.USER} *PERFIL - ${markdown.escapeMarkdown(userName.toUpperCase())}*\n` +
         `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
}

function getProfileStats(stats) {
  let message = `${constants.EMOJI.STATS} *ESTADÍSTICAS DE USO*\n\n`;

  if (stats.general.totalConnections > 0) {
    message += `🔸 *Conexiones totales:* ${stats.general.totalConnections}\n`;
    message += `🔸 *Datos transferidos:* ${stats.general.totalBytesTransferred}\n`;
    message += `🔸 *VPN favorita:* ${markdown.bold(stats.general.favoriteVPN || 'Ninguna')}\n`;
    message += `🔸 *Tiempo promedio sesión:* ${stats.general.averageSessionTime}\n\n`;
    
    if (Object.keys(stats.vpnUsage || {}).length > 0) {
      message += `${constants.EMOJI.VPN} *USO POR VPN*\n`;
      Object.entries(stats.vpnUsage).forEach(([vpn, count]) => {
        message += `• ${markdown.bold(vpn)}: ${count} conexiones\n`;
      });
      message += '\n';
    }
  } else {
    message += `${constants.EMOJI.INFO} Aún no has realizado conexiones.\n`;
    message += `Usa /vpn para comenzar.\n\n`;
  }

  return message;
}

function getProfileInfo(profile) {
  let message = `${constants.EMOJI.INFO} *INFORMACIÓN DE CUENTA*\n\n`;

  message += `👤 *Nombre:* ${markdown.escapeMarkdown(profile.fullName || 'Sin nombre')}\n`;
  message += `🔖 *Username:* ${profile.username || 'No disponible'}\n`;
  message += `🆔 *ID:* ${markdown.code(profile.id)}\n`;
  message += `🌐 *Idioma:* ${profile.language ? profile.language.toUpperCase() : 'ES'}\n`;
  message += `⭐ *Premium:* ${profile.isPremium ? 'Sí ✅' : 'No'}\n`;
  message += `📅 *Registrado:* ${profile.createdAt || 'N/A'}\n`;
  message += `👀 *Última actividad:* ${profile.lastSeen || 'Nunca'}\n`;

  return message;
}

// ============================================================================
// ⚙️ PREFERENCIAS
// ============================================================================

function getPreferencesHeader() {
  return `${constants.EMOJI.SETTINGS} *CONFIGURACIÓN DE PREFERENCIAS*\n` +
         `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
}

function getVPNPreferences(prefs) {
  return `${constants.EMOJI.VPN} *CONFIGURACIÓN VPN*\n` +
         `• Tipo predeterminado: ${markdown.bold(prefs.defaultType)}\n` +
         `• Auto-conectar: ${prefs.autoConnect ? '✅ Sí' : '❌ No'}\n` +
         `• Opciones avanzadas: ${prefs.showAdvancedOptions ? '✅ Sí' : '❌ No'}\n`;
}

function getNotificationPreferences(prefs) {
  return `${constants.EMOJI.BELL} *NOTIFICACIONES*\n` +
         `• Estado conexión: ${prefs.connectionStatus ? '✅ Sí' : '❌ No'}\n` +
         `• Advertencias cuota: ${prefs.quotaWarnings ? '✅ Sí' : '❌ No'}\n` +
         `• Actualizaciones sistema: ${prefs.systemUpdates ? '✅ Sí' : '❌ No'}\n` +
         `• Promocionales: ${prefs.promotional ? '✅ Sí' : '❌ No'}\n`;
}

function getInterfacePreferences(prefs) {
  return `${constants.EMOJI.PALETTE} *INTERFAZ*\n` +
         `• Idioma: ${markdown.bold(prefs.language)}\n` +
         `• Modo compacto: ${prefs.compactMode ? '✅ Sí' : '❌ No'}\n` +
         `• Mostrar emojis: ${prefs.showEmojis ? '✅ Sí' : '❌ No'}\n` +
         `• Zona horaria: ${prefs.timezone}\n`;
}

function getSecurityPreferences(prefs) {
  return `${constants.EMOJI.SHIELD} *SEGURIDAD*\n` +
         `• Confirmar acciones: ${prefs.requireConfirmation ? '✅ Sí' : '❌ No'}\n` +
         `• Cerrar otras sesiones: ${prefs.logOutOtherSessions ? '✅ Sí' : '❌ No'}\n` +
         `• Autenticación 2FA: ${prefs.twoFactorAuth ? '✅ Sí' : '❌ No'}\n`;
}

// ============================================================================
// 🔧 ACCIONES DE USUARIO
// ============================================================================

function getEditProfilePrompt() {
  return `${constants.EMOJI.EDIT} *EDITAR PERFIL*\n\n` +
         `¿Qué te gustaría editar?\n` +
         `Usa los botones para seleccionar una opción.`;
}

function getEditPreferencePrompt(category, key) {
  const categoryNames = {
    vpn: 'VPN',
    notifications: 'Notificaciones',
    interface: 'Interfaz',
    security: 'Seguridad'
  };

  return `${constants.EMOJI.EDIT} *EDITAR PREFERENCIA*\n\n` +
         `Categoría: ${markdown.bold(categoryNames[category] || category)}\n` +
         `Opción: ${markdown.bold(key)}\n\n` +
         `Envía el nuevo valor:`;
}

function getPreferenceUpdatedSuccess(category, key, value) {
  return `${constants.EMOJI.SUCCESS} *PREFERENCIA ACTUALIZADA*\n\n` +
         `${markdown.bold(key)} en ${category} actualizado a: ${markdown.bold(value)}`;
}

// ============================================================================
// 📊 ESTADÍSTICAS Y REPORTES
// ============================================================================

function getUsageReport(stats) {
  return `${constants.EMOJI.CHART} *INFORME DE USO*\n\n` +
         `📅 *Período:* Últimos 30 días\n` +
         `🔗 *Conexiones activas:* ${stats.activeConnections || 0}\n` +
         `📦 *Datos usados:* ${stats.dataUsed || '0 GB'}\n` +
         `⏱️ *Tiempo conectado:* ${stats.connectionTime || '0 horas'}\n` +
         `🔝 *VPN más usada:* ${markdown.bold(stats.topVPN || 'Ninguna')}\n`;
}

// ============================================================================
// 🚨 ERRORES Y ADVERTENCIAS
// ============================================================================

function getProfileNotFoundError() {
  return `${constants.EMOJI.ERROR} *PERFIL NO ENCONTRADO*\n\n` +
         `No se encontró un perfil para tu usuario.\n` +
         `Esto puede deberse a:\n` +
         `• Primera vez que usas el bot\n` +
         `• Datos corruptos\n` +
         `• Error de sistema\n\n` +
         `Intenta usar el comando /start para crear un nuevo perfil.`;
}

function getPreferenceNotFoundError(category, key) {
  return `${constants.EMOJI.ERROR} *PREFERENCIA NO ENCONTRADA*\n\n` +
         `La preferencia ${markdown.bold(key)} en ${markdown.bold(category)} no existe.\n` +
         `Usa /preferences para ver las opciones disponibles.`;
}

function getInvalidPreferenceValueError(key, validValues = []) {
  let message = `${constants.EMOJI.ERROR} *VALOR INVÁLIDO*\n\n`;
  message += `El valor para ${markdown.bold(key)} no es válido.\n`;
  
  if (validValues.length > 0) {
    message += `\nValores aceptados:\n`;
    validValues.forEach(value => {
      message += `• ${markdown.code(value)}\n`;
    });
  }

  return message;
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // Profile Messages
  getProfileHeader,
  getProfileStats,
  getProfileInfo,
  
  // Preferences Messages
  getPreferencesHeader,
  getVPNPreferences,
  getNotificationPreferences,
  getInterfacePreferences,
  getSecurityPreferences,
  
  // User Actions
  getEditProfilePrompt,
  getEditPreferencePrompt,
  getPreferenceUpdatedSuccess,
  
  // Statistics
  getUsageReport,
  
  // Errors
  getProfileNotFoundError,
  getPreferenceNotFoundError,
  getInvalidPreferenceValueError
};