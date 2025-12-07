// =====================================================
// HTML UTILITIES
// =====================================================

const escapeHtml = (text) =>
  text ? String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') : '';

const bold = (text) => `<b>${text}</b>`;
const code = (text) => `<code>${text}</code>`;

// =====================================================
// FORMAT FUNCTIONS
// =====================================================

/**
 * Convierte bytes a unidades legibles (B, KB, MB, GB, TB).
 */
function formatBytes(bytes) {
  if (!bytes || bytes <= 0) return '0 B';

  const k = 1024;
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const val = (bytes / Math.pow(k, i)).toFixed(2);

  return `${val} ${units[i]}`;
}

/**
 * Convierte timestamp UNIX a fecha legible en español.
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
 * Limita texto a maxLength añadiendo "...".
 */
function truncate(text, maxLength = 50) {
  if (typeof text !== 'string' || text.length <= maxLength) return text || '';
  return `${text.substring(0, maxLength)}...`;
}

// =====================================================
// LIST FORMATTERS (Compact Style)
// =====================================================

/**
 * Formatea lista de clientes WireGuard en estilo compacto.
 */
function formatWireGuardClients(clients = []) {
  if (clients.length === 0) {
    return '📭 No hay clientes WireGuard';
  }

  let msg = `🔐 ${bold('WireGuard')} • ${clients.length} clientes\n\n`;

  clients.forEach((c, i) => {
    msg += `${i + 1}) IP: ${code(escapeHtml(c.ip))}\n`;
    msg += `   Última conexión: ${escapeHtml(c.lastSeen)}\n`;
    msg += `   Recibido: ${escapeHtml(c.dataReceived)} | Enviado: ${escapeHtml(c.dataSent)}\n\n`;
  });

  return msg.trim();
}

/**
 * Formatea lista de claves Outline en estilo compacto.
 */
function formatOutlineKeys(keys = []) {
  if (keys.length === 0) {
    return '📭 No hay claves Outline';
  }

  let msg = `🌐 ${bold('Outline')} • ${keys.length} claves\n\n`;

  keys.forEach((k, i) => {
    msg += `${i + 1}) ID: ${code(escapeHtml(k.id))} • ${escapeHtml(k.name || 'Sin nombre')}\n`;
  });

  return msg.trim();
}

/**
 * Formatea vista combinada de WireGuard + Outline.
 */
function formatClientsList(wgClients, outlineKeys) {
  let msg = `${bold('📊 CLIENTES ACTIVOS')}\n\n`;

  msg += formatWireGuardClients(wgClients) + '\n\n';
  msg += formatOutlineKeys(outlineKeys);

  return msg.trim();
}

/**
 * Sanitiza entrada eliminando < >.
 */
function sanitizeInput(input) {
  if (typeof input !== 'string') return '';
  return input.replace(/[<>]/g, '');
}

module.exports = {
  formatBytes,
  formatTimestamp,
  truncate,
  formatWireGuardClients,
  formatOutlineKeys,
  formatClientsList,
  sanitizeInput
};