'use strict';

/**
 * ============================================================================
 * 🧩 FORMATO Y UTILIDADES HTML — uSipipo VPN Manager
 * Conjunto de funciones para formateo, sanitización y presentación de datos.
 * Diseño profesional, seguro y consistente con el cliente final.
 * ============================================================================
 */

// ============================================================================
// 🔐 HTML UTILITIES
// ============================================================================

/**
 * Escapa caracteres HTML peligrosos para evitar inyección.
 */
const escapeHtml = (text) =>
  text
    ? String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
    : '';

const bold = (text) => `<b>${escapeHtml(text)}</b>`;
const italic = (text) => `<i>${escapeHtml(text)}</i>`;
const code = (text) => `<code>${escapeHtml(text)}</code>`;

// ============================================================================
// 📏 FORMAT FUNCTIONS
// ============================================================================

/**
 * Convierte bytes en formato legible (B, KB, MB, GB, TB).
 */
function formatBytes(bytes) {
  if (!bytes || bytes <= 0) return '0 B';

  const k = 1024;
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const value = (bytes / Math.pow(k, i)).toFixed(2);

  return `${value} ${units[i]}`;
}

/**
 * Convierte timestamp UNIX a una fecha legible en español.
 */
function formatTimestamp(timestamp) {
  if (!timestamp || timestamp === '0') return 'Nunca';

  const date = new Date(parseInt(timestamp, 10) * 1000);
  if (isNaN(date.getTime())) return 'Nunca';

  return date.toLocaleString('es-ES', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Recorta texto largo añadiendo "..."
 */
function truncate(text, maxLength = 50) {
  if (!text || typeof text !== 'string') return '';
  return text.length <= maxLength
    ? text
    : `${text.substring(0, maxLength)}...`;
}

// ============================================================================
// 📋 LIST FORMATTERS (Compact & Professional)
// ============================================================================

/**
 * Formatea lista de clientes WireGuard.
 */
function formatWireGuardClients(clients = []) {
  if (clients.length === 0) {
    return '📭 No hay clientes WireGuard';
  }

  let msg = `🔐 ${bold('WireGuard')} • ${clients.length} cliente(s)\n\n`;

  clients.forEach((c, i) => {
    msg += `${i + 1}) IP: ${code(c.ip)}\n`;
    msg += `   Última conexión: ${escapeHtml(c.lastSeen || 'N/A')}\n`;
    msg += `   Recibido: ${escapeHtml(c.dataReceived)} • Enviado: ${escapeHtml(c.dataSent)}\n\n`;
  });

  return msg.trim();
}

/**
 * Formatea lista de claves Outline.
 */
function formatOutlineKeys(keys = []) {
  if (keys.length === 0) {
    return '📭 No hay claves Outline';
  }

  let msg = `🌐 ${bold('Outline')} • ${keys.length} clave(s)\n\n`;

  keys.forEach((k, i) => {
    msg += `${i + 1}) ID: ${code(k.id)} • ${escapeHtml(k.name || 'Sin nombre')}\n`;
  });

  return msg.trim();
}

/**
 * Vista conjunta WireGuard + Outline
 */
function formatClientsList(wgClients, outlineKeys) {
  let msg = `${bold('📊 CLIENTES ACTIVOS')}\n\n`;

  msg += formatWireGuardClients(wgClients) + '\n\n';
  msg += formatOutlineKeys(outlineKeys);

  return msg.trim();
}

// ============================================================================
// 🧹 SANITIZACIÓN
// ============================================================================

/**
 * Elimina caracteres conflictivos para entrada segura.
 */
function sanitizeInput(input) {
  if (typeof input !== 'string') return '';
  return input.replace(/[<>]/g, '');
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
  escapeHtml,
  bold,
  italic,
  code,

  formatBytes,
  formatTimestamp,
  truncate,

  formatWireGuardClients,
  formatOutlineKeys,
  formatClientsList,

  sanitizeInput
};