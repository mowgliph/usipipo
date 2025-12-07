// utils/formatters.js

// =====================================================
// UTILIDADES HTML INTERNAS
// =====================================================

/**
 * Escapa caracteres especiales de HTML (<, >, &).
 */
const escapeHtml = (text) => {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
};

const bold = (text) => `<b>${text}</b>`;
const code = (text) => `<code>${text}</code>`;

// =====================================================
// FUNCIONES DE FORMATEO
// =====================================================

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
 * Formatea lista de clientes WireGuard para Telegram (HTML).
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
    // Se asume que client.ip es seguro, pero por si acaso escapamos
    message += `${index + 1}. IP: ${code(escapeHtml(client.ip))}
`;
    // Usamos escapeHtml para datos que podrían venir del exterior
    message += `   📡 Última conexión: ${escapeHtml(client.lastSeen)}
`;
    message += `   📥 Recibido: ${escapeHtml(client.dataReceived)}
`;
    message += `   📤 Enviado: ${escapeHtml(client.dataSent)}

`;
  });

  return message.trimEnd();
}

/**
 * Formatea lista de claves Outline para Telegram (HTML).
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
    const keyName = key.name ? escapeHtml(key.name) : 'Sin nombre';
    // key.id suele ser numérico, pero escapamos por seguridad
    message += `${index + 1}. ID: ${code(escapeHtml(key.id))} - ${keyName}
`;
  });

  return message.trimEnd();
}

/**
 * Formatea vista combinada de clientes WireGuard + Outline (HTML).
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
 * Útil para limpiar inputs antes de procesarlos, aunque escapeHtml es preferible para display.
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
