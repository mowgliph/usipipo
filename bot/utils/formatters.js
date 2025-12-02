// utils/formatters.js

/**
 * Formatea bytes a unidades legibles
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Formatea timestamp a fecha legible
 */
function formatTimestamp(timestamp) {
  if (timestamp === '0' || !timestamp) return 'Nunca';
  const date = new Date(parseInt(timestamp) * 1000);
  return date.toLocaleString('es-ES', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Trunca texto largo
 */
function truncate(text, maxLength = 50) {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Formatea lista de clientes WireGuard
 */
function formatWireGuardClients(clients) {
  if (clients.length === 0) {
    return '📭 No hay clientes WireGuard activos';
  }

  let message = `🔐 **WireGuard** (${clients.length} clientes)\n`;
  message += '━━━━━━━━━━━━━━━━━\n';
  
  clients.forEach((client, index) => {
    message += `${index + 1}. IP: \`${client.ip}\`\n`;
    message += `   📡 Última conexión: ${client.lastSeen}\n`;
    message += `   📥 Recibido: ${client.dataReceived}\n`;
    message += `   📤 Enviado: ${client.dataSent}\n\n`;
  });

  return message;
}

/**
 * Formatea lista de claves Outline
 */
function formatOutlineKeys(keys) {
  if (keys.length === 0) {
    return '📭 No hay claves Outline activas';
  }

  let message = `🌐 **Outline** (${keys.length} claves)\n`;
  message += '━━━━━━━━━━━━━━━━━\n';
  
  keys.forEach((key, index) => {
    message += `${index + 1}. ID: \`${key.id}\` - ${key.name || 'Sin nombre'}\n`;
  });

  return message;
}

/**
 * Formatea lista completa de clientes
 */
function formatClientsList(wgClients, outlineKeys) {
  let message = '📊 **CLIENTES ACTIVOS**\n\n';
  message += formatWireGuardClients(wgClients);
  message += '\n';
  message += formatOutlineKeys(outlineKeys);
  return message;
}

/**
 * Sanitiza entrada de usuario
 */
function sanitizeInput(input) {
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
