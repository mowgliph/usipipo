// utils/formatters.js
const { escapeMarkdown, bold } = require('./markdown');

/**
 * Formatea bytes a unidades legibles (B, KB, MB, GB, TB).
 * @param {number} bytes - Bytes a formatear
 * @returns {string} String formateado
 */
function formatBytes(bytes) {
  if (!bytes || bytes <= 0) {
    return '0 B';
  }

  const k = 1024;
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const value = (bytes / Math.pow(k, i)).toFixed(2);

  return `${value} ${units[i]}`;
}

/**
 * Formatea timestamp Unix (segundos) a fecha legible en español.
 * @param {string|number} timestamp - Timestamp Unix
 * @returns {string} Fecha formateada o 'Nunca'
 */
function formatTimestamp(timestamp) {
  if (!timestamp || timestamp === '0') {
    return 'Nunca';
  }

  const date = new Date(parseInt(timestamp, 10) * 1000);
  if (isNaN(date.getTime())) {
    return 'Nunca';
  }

  return date.toLocaleString('es-ES', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Trunca texto añadiendo "..." si excede longitud máxima.
 * @param {string} text - Texto a truncar
 * @param {number} [maxLength=50] - Longitud máxima
 * @returns {string} Texto truncado
 */
function truncate(text, maxLength = 50) {
  if (typeof text !== 'string' || text.length <= maxLength) {
    return text || '';
  }

  return `${text.substring(0, maxLength)}...`;
}

/**
 * Formatea lista de clientes WireGuard para Telegram.
 * @param {Array<Object>} clients - Lista de clientes
 * @returns {string} Mensaje formateado
 */
function formatWireGuardClients(clients) {
  if (!clients || clients.length === 0) {
    return '📭 No hay clientes WireGuard activos';
  }

  let message = `🔐 ${bold('WireGuard')} (${clients.length} clientes)
━━━━━━━━━━━━━━━━━━
`;

  clients.forEach((client, index) => {
    message += `${index + 1}. IP: ${code(client.ip)}
`;
    message += `   📡 Última conexión: ${escapeMarkdown(client.lastSeen)}
`;
    message += `   📥 Recibido: ${escapeMarkdown(client.dataReceived)}
`;
    message += `   📤 Enviado: ${escapeMarkdown(client.dataSent)}

`;
  });

  return message.trimEnd();
}

/**
 * Formatea lista de claves Outline para Telegram.
 * @param {Array<Object>} keys - Lista de claves
 * @returns {string} Mensaje formateado
 */
function formatOutlineKeys(keys) {
  if (!keys || keys.length === 0) {
    return '📭 No hay claves Outline activas';
  }

  let message = `🌐 ${bold('Outline')} (${keys.length} claves)
━━━━━━━━━━━━━━━━━━
`;

  keys.forEach((key, index) => {
    const keyName = key.name ? escapeMarkdown(key.name) : 'Sin nombre';
    message += `${index + 1}. ID: ${code(key.id)} - ${keyName}
`;
  });

  return message.trimEnd();
}

/**
 * Formatea vista combinada de clientes WireGuard + Outline.
 * @param {Array<Object>} wgClients - Clientes WireGuard
 * @param {Array<Object>} outlineKeys - Claves Outline
 * @returns {string} Mensaje combinado
 */
function formatClientsList(wgClients, outlineKeys) {
  let message = `${bold('📊 CLIENTES ACTIVOS')}

`;

  message += `${formatWireGuardClients(wgClients)}

`;
  message += formatOutlineKeys(outlineKeys);

  return message.trimEnd();
}

/**
 * Sanitiza entrada removiendo caracteres problemáticos básicos (< >).
 * @param {string} input - Entrada a sanitizar
 * @returns {string} Input limpio
 */
function sanitizeInput(input) {
  if (typeof input !== 'string') {
    return '';
  }

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