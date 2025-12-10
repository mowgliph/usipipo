'use strict';

/**
 * ============================================================================
 * 🧩 FORMATTERS — uSipipo VPN Manager
 * Lógica centralizada para presentación de datos y sanitización.
 * 
 * 📦 DEPENDENCIAS:
 *   - markdown.js (fuente única de Markdown V1)
 *   - constants.js (para emojis y configuraciones)
 * 
 * 🎯 OBJETIVO: Formatear datos específicos del negocio VPN usando Markdown V1
 * 
 * ⚠️ IMPORTANTE: Este archivo NO re-exporta funciones de markdown.
 *    Todos los módulos deben importar markdown.js directamente.
 * ============================================================================
 */

const markdown = require('./markdown');
const constants = require('../../config/constants');

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
// 📋 LIST FORMATTERS (VPN-SPECIFIC)
// ============================================================================

function formatWireGuardClients(clients) {
  const safeClients = Array.isArray(clients) ? clients : [];
  if (safeClients.length === 0) {
    return `${constants.EMOJI.WARNING} ${markdown.escapeMarkdown('No hay clientes WireGuard activos.')}`;
  }

  let msg = `${constants.EMOJI.VPN} ${markdown.bold('WireGuard')} - ${safeClients.length} cliente(s)\n\n`;

  safeClients.forEach((c, i) => {
    const ip = c.ip || 'IP Desconocida';
    const lastSeen = c.lastSeen ? markdown.escapeMarkdown(c.lastSeen) : 'N/A';
    msg += `${i + 1}. IP: ${markdown.code(ip)}\n`;
    msg += `   🕒 Última vez: ${lastSeen}\n`;
    msg += `   📉 Descarga: ${markdown.escapeMarkdown(c.dataReceived || '0')} - 📈 Subida: ${markdown.escapeMarkdown(c.dataSent || '0')}\n\n`;
  });
  return msg.trim();
}

function formatOutlineKeys(keys) {
  const safeKeys = Array.isArray(keys) ? keys : [];
  if (safeKeys.length === 0) {
    return `${constants.EMOJI.WARNING} ${markdown.escapeMarkdown('No hay claves Outline activas.')}`;
  }

  let msg = `${constants.EMOJI.SERVER} ${markdown.bold('Outline')} - ${safeKeys.length} clave(s)\n\n`;

  safeKeys.forEach((k, i) => {
    msg += `${i + 1}. ID: ${markdown.code(k.id)} - ${markdown.escapeMarkdown(k.name || 'Sin nombre')}\n`;
  });
  return msg.trim();
}

function formatClientsList(wgClients, outlineKeys) {
  let msg = `${markdown.bold('📊 CLIENTES ACTIVOS')}\n\n`;
  msg += formatWireGuardClients(wgClients) + '\n';
  msg += '━━━━━━━━━━━━━━━━━━\n';
  msg += formatOutlineKeys(outlineKeys);
  return msg.trim();
}

// ============================================================================
// 📊 VPN CONFIG FORMATTERS
// ============================================================================

function formatWireGuardConfig(config) {
  if (!config || typeof config !== 'object') return '';
  
  const lines = [
    '[Interface]',
    `PrivateKey = ${config.privateKey}`,
    `Address = ${config.address}`,
    `DNS = ${config.dns || '1.1.1.1'}`,
    '',
    '[Peer]',
    `PublicKey = ${config.serverPublicKey}`,
    `Endpoint = ${config.endpoint}`,
    `AllowedIPs = ${config.allowedIps}`,
    'PersistentKeepalive = 25'
  ];
  
  return lines.join('\n');
}

function formatOutlineAccessUrl(keyData) {
  if (!keyData || !keyData.accessUrl) return 'URL no disponible';
  return markdown.link('🔗 Enlace de conexión Outline', keyData.accessUrl);
}

// ============================================================================
// 🔧 UTILITY FUNCTIONS
// ============================================================================

function sanitizeInput(input) {
  if (!input || typeof input !== 'string') return '';
  return input.replace(/[<>]/g, '').trim();
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
  // Data Formatters
  formatBytes,
  formatTimestamp,
  truncate,
  
  // VPN List Formatters
  formatWireGuardClients,
  formatOutlineKeys,
  formatClientsList,
  
  // VPN Config Formatters
  formatWireGuardConfig,
  formatOutlineAccessUrl,
  
  // Utils
  sanitizeInput
};