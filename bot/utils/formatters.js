'use strict';

/**
 * ============================================================================
 * 🧩 FORMATTERS — uSipipo VPN Manager
 * Lógica centralizada para presentación de datos y sanitización.
 * ============================================================================
 */

// ============================================================================
// 📝 TELEGRAM MARKDOWN UTILITIES (Integrated)
// ============================================================================

/**
 * Escapa caracteres reservados para Telegram Markdown V1.
 * En V1 solo escapamos: _ * ` [
 */
function escapeMarkdown(text) {
  if (text === null || text === undefined) return '';
  return String(text).replace(/[[_*`]/g, '\\$&');
}

function bold(text) {
  return `*${escapeMarkdown(text)}*`;
}

// 👇 ESTA ERA LA FUNCIÓN QUE FALTABA
function italic(text) {
  return `_${escapeMarkdown(text)}_`;
}

function code(text) {
  return `\`${String(text).replace(/`/g, '\\`')}\``; // Solo escapa backticks internos
}

function pre(text, language = '') {
  return `\`\`\`${language}\n${String(text).replace(/`/g, '\\`')}\n\`\`\``;
}

// ============================================================================
// 📏 DATA FORMATTING
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

function formatTimestamp(timestamp) {
  if (!timestamp || timestamp === '0' || timestamp === 0) return 'Nunca';
  const date = new Date(Number(timestamp) * 1000);
  if (isNaN(date.getTime())) return 'Nunca';
  
  return date.toLocaleString('es-ES', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  });
}

function truncate(text, maxLength = 50) {
  if (!text || typeof text !== 'string') return '';
  return text.length <= maxLength ? text : `${text.substring(0, maxLength)}...`;
}

// ============================================================================
// 📋 LIST FORMATTERS
// ============================================================================

function formatWireGuardClients(clients) {
  const safeClients = Array.isArray(clients) ? clients : [];
  if (safeClients.length === 0) return `📭 ${escapeMarkdown('No hay clientes WireGuard activos.')}`;

  let msg = `🔐 ${bold('WireGuard')} - ${safeClients.length} cliente(s)\n\n`;

  safeClients.forEach((c, i) => {
    const ip = c.ip || 'IP Desconocida';
    const lastSeen = c.lastSeen ? escapeMarkdown(c.lastSeen) : 'N/A';
    msg += `${i + 1}. IP: ${code(ip)}\n`;
    msg += `   🕒 Última vez: ${lastSeen}\n`;
    msg += `   📉 Descarga: ${escapeMarkdown(c.dataReceived || '0')} - 📈 Subida: ${escapeMarkdown(c.dataSent || '0')}\n\n`;
  });
  return msg.trim();
}

function formatOutlineKeys(keys) {
  const safeKeys = Array.isArray(keys) ? keys : [];
  if (safeKeys.length === 0) return `📭 ${escapeMarkdown('No hay claves Outline activas.')}`;

  let msg = `🌐 ${bold('Outline')} - ${safeKeys.length} clave(s)\n\n`;

  safeKeys.forEach((k, i) => {
    msg += `${i + 1}. ID: ${code(k.id)} - ${escapeMarkdown(k.name || 'Sin nombre')}\n`;
  });
  return msg.trim();
}

function formatClientsList(wgClients, outlineKeys) {
  let msg = `${bold('📊 CLIENTES ACTIVOS')}\n\n`;
  msg += formatWireGuardClients(wgClients) + '\n';
  msg += '━━━━━━━━━━━━━━━━━━\n';
  msg += formatOutlineKeys(outlineKeys);
  return msg.trim();
}

function sanitizeInput(input) {
  if (!input || typeof input !== 'string') return '';
  return input.replace(/[<>]/g, '').trim();
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
  // Markdown Helpers
  escapeMarkdown,
  escapeHtml: escapeMarkdown, // Alias de seguridad
  bold,
  italic, // 👈 AHORA SÍ SE EXPORTA
  code,
  pre,

  // Data Formatters
  formatBytes,
  formatTimestamp,
  truncate,

  // List Formatters
  formatWireGuardClients,
  formatOutlineKeys,
  formatClientsList,

  // Utils
  sanitizeInput
};
