'use strict';

/**
 * ============================================================================
 * 💬 VPN MESSAGES - uSipipo VPN Bot
 * ============================================================================
 * Mensajes específicos para el módulo de gestión VPN.
 * Sigue el patrón de common.messages pero especializado en VPN.
 * ============================================================================
 */

const markdown = require('../../core/utils/markdown');
const { formatBytes, formatTimestamp } = require('../../core/utils/formatters');
const constants = require('../../config/constants');
const config = require('../../config/environment');

// ============================================================================
// 🏠 MENSAJES DE MENÚ PRINCIPAL VPN
// ============================================================================

function getVPNMainMenuMessage() {
  return `${constants.EMOJI.VPN} ${markdown.bold('GESTIÓN DE CONEXIONES VPN')}\n\n` +
         `Administra tus conexiones seguras a internet.\n\n` +
         `${constants.EMOJI.INFO} Tipos disponibles:\n` +
         `• ${markdown.bold('WireGuard')} - Rápido y moderno\n` +
         `• ${markdown.bold('Outline')} - Fácil y seguro\n\n` +
         `Selecciona una opción del menú:`;
}

function getVPNTypeSelectionMessage() {
  return `${constants.EMOJI.VPN} ${markdown.bold('Seleccionar tipo de VPN')}\n\n` +
         `¿Qué tipo de conexión VPN deseas gestionar?\n\n` +
         `${markdown.bold('WireGuard:')}\n` +
         `• Protocolo moderno y ultrarrápido\n` +
         `• Ideal para dispositivos móviles\n` +
         `• Consumo mínimo de batería\n\n` +
         `${markdown.bold('Outline:')}\n` +
         `• Configuración simple\n` +
         `• Compatible con múltiples dispositivos\n` +
         `• Resistente a bloqueos`;
}

// ============================================================================
// 🔐 MENSAJES DE WIREGUARD
// ============================================================================

function getWireGuardWelcomeMessage() {
  return `${constants.EMOJI.VPN} ${markdown.bold('WireGuard VPN')}\n\n` +
         `Protocolo VPN de última generación.\n\n` +
         `${constants.EMOJI.SUCCESS} Ventajas:\n` +
         `• Velocidad ultrarrápida\n` +
         `• Conexión estable\n` +
         `• Bajo consumo de batería\n` +
         `• Cifrado de grado militar\n\n` +
         `Selecciona una opción:`;
}

function getWireGuardCreationSuccessMessage(clientData) {
  const { clientName, ipv4, ipv6, config, qrCode } = clientData;
  
  let msg = `${constants.EMOJI.SUCCESS} ${markdown.bold('Cliente WireGuard creado')}\n\n`;
  msg += `${constants.EMOJI.USER} ${markdown.bold('Cliente:')} ${markdown.code(clientName)}\n`;
  msg += `${constants.EMOJI.SERVER} ${markdown.bold('IP asignada:')} ${markdown.code(ipv4)}\n`;
  
  if (ipv6) {
    msg += `${constants.EMOJI.SERVER} ${markdown.bold('IPv6:')} ${markdown.code(ipv6)}\n`;
  }
  
  msg += `\n${markdown.bold('📱 Instrucciones de conexión:')}\n\n`;
  msg += `1. Descarga WireGuard:\n`;
  msg += `   ${markdown.link('Descargar app oficial', constants.URLS.WIREGUARD_DOWNLOAD)}\n\n`;
  msg += `2. Abre la app y toca "+" → "Crear desde código QR"\n\n`;
  msg += `3. Escanea el código QR que te enviaré a continuación\n\n`;
  msg += `4. Activa la conexión y ¡listo!\n\n`;
  msg += `${constants.EMOJI.INFO} También puedes usar el archivo de configuración (.conf)`;
  
  return msg;
}

function getWireGuardConfigFileMessage(clientName) {
  return `${constants.EMOJI.VPN} ${markdown.bold('Archivo de configuración')}\n\n` +
         `Cliente: ${markdown.code(clientName)}\n\n` +
         `Este archivo contiene toda tu configuración.\n\n` +
         `${markdown.bold('💾 Cómo usarlo:')}\n` +
         `1. Descarga el archivo\n` +
         `2. Abre WireGuard app\n` +
         `3. Importa el archivo\n` +
         `4. Activa la conexión\n\n` +
         `${constants.EMOJI.WARNING} ${markdown.bold('IMPORTANTE:')}\n` +
         `No compartas este archivo. Contiene tus claves privadas.`;
}

function getWireGuardQRCodeMessage() {
  return `${constants.EMOJI.VPN} ${markdown.bold('Código QR - WireGuard')}\n\n` +
         `Escanea este código con la app de WireGuard:\n\n` +
         `📱 ${markdown.bold('Pasos:')}\n` +
         `1. Abre WireGuard\n` +
         `2. Toca el botón "+"\n` +
         `3. Selecciona "Crear desde código QR"\n` +
         `4. Escanea el código de abajo\n` +
         `5. Activa la conexión`;
}

function getWireGuardStatsMessage(stats) {
  const { clientName, ipv4, stats: usage, quota } = stats;
  
  let msg = `${constants.EMOJI.VPN} ${markdown.bold('Estadísticas WireGuard')}\n\n`;
  msg += `${markdown.bold('Cliente:')} ${markdown.code(clientName)}\n`;
  msg += `${markdown.bold('IP:')} ${markdown.code(ipv4)}\n`;
  msg += `━━━━━━━━━━━━━━━━━━\n\n`;
  
  msg += `📊 ${markdown.bold('Uso de datos:')}\n`;
  msg += `📥 Descarga: ${markdown.code(formatBytes(usage.dataReceived))}\n`;
  msg += `📤 Subida: ${markdown.code(formatBytes(usage.dataSent))}\n`;
  msg += `📦 Total: ${markdown.code(formatBytes(usage.total))}\n\n`;
  
  msg += `🕒 ${markdown.bold('Última conexión:')}\n`;
  msg += `${usage.lastHandshake || 'Nunca'}\n\n`;
  
  msg += `📈 ${markdown.bold('Cuota de datos:')}\n`;
  msg += `Usado: ${quota.percentage}% de ${formatBytes(quota.limit)}\n`;
  
  // Barra de progreso visual
  const progressBar = generateProgressBar(parseFloat(quota.percentage));
  msg += `${progressBar}\n`;
  msg += `Restante: ${markdown.code(formatBytes(quota.limit - usage.total))}`;
  
  if (quota.exceeded) {
    msg += `\n\n${constants.EMOJI.ERROR} ${markdown.bold('Cuota excedida')}\n`;
    msg += `Has superado tu límite de datos.`;
  }
  
  return msg;
}

function getWireGuardDeleteConfirmMessage(clientName) {
  return `${constants.EMOJI.WARNING} ${markdown.bold('Confirmar eliminación')}\n\n` +
         `¿Estás seguro de eliminar el cliente WireGuard?\n\n` +
         `${markdown.bold('Cliente:')} ${markdown.code(clientName)}\n\n` +
         `${constants.EMOJI.ERROR} ${markdown.bold('Esta acción NO se puede deshacer.')}\n\n` +
         `Se eliminarán:\n` +
         `• Configuración del servidor\n` +
         `• Archivo de configuración\n` +
         `• Estadísticas de uso\n` +
         `• Código QR`;
}

function getWireGuardDeletedMessage(clientName) {
  return `${constants.EMOJI.SUCCESS} ${markdown.bold('Cliente eliminado')}\n\n` +
         `El cliente ${markdown.code(clientName)} ha sido eliminado correctamente.\n\n` +
         `Tu conexión WireGuard ya no funcionará.\n\n` +
         `Puedes crear una nueva conexión cuando lo necesites.`;
}

function getWireGuardAlreadyExistsMessage() {
  return `${constants.EMOJI.WARNING} ${markdown.bold('Configuración existente')}\n\n` +
         `Ya tienes una configuración WireGuard activa.\n\n` +
         `${constants.EMOJI.INFO} Opciones:\n` +
         `• Ver tu configuración actual\n` +
         `• Ver estadísticas de uso\n` +
         `• Eliminar y crear una nueva\n\n` +
         `Usa los botones del menú para gestionar tu conexión.`;
}

function getWireGuardNotFoundMessage() {
  return `${constants.EMOJI.WARNING} ${markdown.bold('Sin configuración')}\n\n` +
         `No tienes ninguna configuración WireGuard activa.\n\n` +
         `${constants.EMOJI.INFO} Para comenzar:\n` +
         `Usa el botón "➕ Nueva Conexión" para crear tu primera configuración VPN.`;
}

function getWireGuardSuspendedMessage(reason) {
  return `${constants.EMOJI.ERROR} ${markdown.bold('Servicio suspendido')}\n\n` +
         `Tu conexión WireGuard ha sido suspendida.\n\n` +
         `${markdown.bold('Motivo:')} ${markdown.escapeMarkdown(reason)}\n\n` +
         `${constants.EMOJI.INFO} Contacta al administrador para reactivar el servicio.`;
}

// ============================================================================
// 🌐 MENSAJES DE OUTLINE
// ============================================================================

function getOutlineWelcomeMessage() {
  return `${constants.EMOJI.SERVER} ${markdown.bold('Outline VPN')}\n\n` +
         `Servicio VPN simple y seguro.\n\n` +
         `${constants.EMOJI.SUCCESS} Ventajas:\n` +
         `• Configuración instantánea\n` +
         `• Un solo enlace para conectar\n` +
         `• Compatible con todos los dispositivos\n` +
         `• Resistente a censura\n\n` +
         `Selecciona una opción:`;
}

function getOutlineCreationSuccessMessage(keyData) {
  const { keyId, name, accessUrl } = keyData;
  
  let msg = `${constants.EMOJI.SUCCESS} ${markdown.bold('Clave Outline creada')}\n\n`;
  msg += `${constants.EMOJI.USER} ${markdown.bold('Nombre:')} ${markdown.code(name)}\n`;
  msg += `${constants.EMOJI.SERVER} ${markdown.bold('ID:')} ${markdown.code(keyId)}\n\n`;
  
  msg += `${markdown.bold('📱 Instrucciones de conexión:')}\n\n`;
  msg += `1. Descarga Outline:\n`;
  msg += `   ${markdown.link('Descargar app oficial', constants.URLS.OUTLINE_DOWNLOAD)}\n\n`;
  msg += `2. Abre la app Outline\n\n`;
  msg += `3. Copia el enlace de acceso que te enviaré\n\n`;
  msg += `4. Pégalo en la app y toca "Conectar"\n\n`;
  msg += `${constants.EMOJI.INFO} El enlace es válido indefinidamente`;
  
  return msg;
}

function getOutlineAccessUrlMessage(accessUrl, keyName) {
  return `${constants.EMOJI.VPN} ${markdown.bold('Enlace de acceso Outline')}\n\n` +
         `${markdown.bold('Clave:')} ${markdown.code(keyName)}\n\n` +
         `${markdown.bold('🔗 Tu enlace de conexión:')}\n` +
         `${markdown.code(accessUrl)}\n\n` +
         `${markdown.bold('📱 Cómo usarlo:')}\n` +
         `1. Copia el enlace completo (toca para copiar)\n` +
         `2. Abre la app Outline\n` +
         `3. Pega el enlace\n` +
         `4. ¡Conecta!\n\n` +
         `${constants.EMOJI.WARNING} ${markdown.bold('IMPORTANTE:')}\n` +
         `No compartas este enlace. Es personal y único.`;
}

function getOutlineStatsMessage(stats) {
  const { keyId, name, metrics, quota } = stats;
  
  let msg = `${constants.EMOJI.SERVER} ${markdown.bold('Estadísticas Outline')}\n\n`;
  msg += `${markdown.bold('Clave:')} ${markdown.code(name)}\n`;
  msg += `${markdown.bold('ID:')} ${markdown.code(keyId)}\n`;
  msg += `━━━━━━━━━━━━━━━━━━\n\n`;
  
  msg += `📊 ${markdown.bold('Uso de datos:')}\n`;
  msg += `📦 Total transferido: ${markdown.code(metrics.bytesUsedHuman)}\n\n`;
  
  msg += `📈 ${markdown.bold('Cuota de datos:')}\n`;
  msg += `Usado: ${quota.percentage}% de ${quota.limitHuman}\n`;
  
  // Barra de progreso visual
  const progressBar = generateProgressBar(parseFloat(quota.percentage));
  msg += `${progressBar}\n`;
  msg += `Restante: ${markdown.code(quota.remainingHuman)}\n\n`;
  
  msg += `🕒 ${markdown.bold('Última actualización:')}\n`;
  msg += `${metrics.lastUpdated ? new Date(metrics.lastUpdated).toLocaleString('es-ES') : 'N/A'}`;
  
  if (quota.exceeded) {
    msg += `\n\n${constants.EMOJI.ERROR} ${markdown.bold('Cuota excedida')}\n`;
    msg += `Has superado tu límite de datos.`;
  } else if (quota.warning) {
    msg += `\n\n${constants.EMOJI.WARNING} ${markdown.bold('Advertencia de cuota')}\n`;
    msg += `Estás cerca de tu límite de datos.`;
  }
  
  return msg;
}

function getOutlineDeleteConfirmMessage(keyName) {
  return `${constants.EMOJI.WARNING} ${markdown.bold('Confirmar eliminación')}\n\n` +
         `¿Estás seguro de eliminar la clave Outline?\n\n` +
         `${markdown.bold('Clave:')} ${markdown.code(keyName)}\n\n` +
         `${constants.EMOJI.ERROR} ${markdown.bold('Esta acción NO se puede deshacer.')}\n\n` +
         `Se eliminarán:\n` +
         `• Clave de acceso\n` +
         `• Enlace de conexión\n` +
         `• Estadísticas de uso`;
}

function getOutlineDeletedMessage(keyName) {
  return `${constants.EMOJI.SUCCESS} ${markdown.bold('Clave eliminada')}\n\n` +
         `La clave ${markdown.code(keyName)} ha sido eliminada correctamente.\n\n` +
         `Tu enlace de conexión ya no funcionará.\n\n` +
         `Puedes crear una nueva clave cuando lo necesites.`;
}

function getOutlineAlreadyExistsMessage() {
  return `${constants.EMOJI.WARNING} ${markdown.bold('Clave existente')}\n\n` +
         `Ya tienes una clave Outline activa.\n\n` +
         `${constants.EMOJI.INFO} Opciones:\n` +
         `• Ver tu enlace de acceso\n` +
         `• Ver estadísticas de uso\n` +
         `• Eliminar y crear una nueva\n\n` +
         `Usa los botones del menú para gestionar tu conexión.`;
}

function getOutlineNotFoundMessage() {
  return `${constants.EMOJI.WARNING} ${markdown.bold('Sin clave activa')}\n\n` +
         `No tienes ninguna clave Outline activa.\n\n` +
         `${constants.EMOJI.INFO} Para comenzar:\n` +
         `Usa el botón "➕ Nueva Clave" para crear tu acceso VPN.`;
}

function getOutlineSuspendedMessage(reason) {
  return `${constants.EMOJI.ERROR} ${markdown.bold('Servicio suspendido')}\n\n` +
         `Tu clave Outline ha sido suspendida.\n\n` +
         `${markdown.bold('Motivo:')} ${markdown.escapeMarkdown(reason)}\n\n` +
         `${constants.EMOJI.INFO} Contacta al administrador para reactivar el servicio.`;
}

// ============================================================================
// 📊 MENSAJES DE RESUMEN Y COMPARACIÓN
// ============================================================================

function getVPNStatusSummaryMessage(userData) {
  const { wg, outline } = userData;
  
  let msg = `${constants.EMOJI.VPN} ${markdown.bold('TUS CONEXIONES VPN')}\n\n`;
  
  // Estado WireGuard
  msg += `${markdown.bold('🔐 WireGuard:')}\n`;
  if (wg && wg.clientName) {
    if (wg.suspended) {
      msg += `${constants.EMOJI.ERROR} Suspendido\n`;
    } else {
      msg += `${constants.EMOJI.SUCCESS} Activo - ${markdown.code(wg.clientName)}\n`;
      msg += `   IP: ${markdown.code(wg.ipv4)}\n`;
    }
  } else {
    msg += `${constants.EMOJI.WARNING} Sin configurar\n`;
  }
  
  msg += `\n`;
  
  // Estado Outline
  msg += `${markdown.bold('🌐 Outline:')}\n`;
  if (outline && outline.keyId) {
    if (outline.suspended) {
      msg += `${constants.EMOJI.ERROR} Suspendido\n`;
    } else {
      msg += `${constants.EMOJI.SUCCESS} Activo - ${markdown.code(outline.name)}\n`;
      msg += `   ID: ${markdown.code(outline.keyId)}\n`;
    }
  } else {
    msg += `${constants.EMOJI.WARNING} Sin configurar\n`;
  }
  
  msg += `\n━━━━━━━━━━━━━━━━━━\n`;
  msg += `${constants.EMOJI.INFO} Usa los botones para gestionar tus conexiones.`;
  
  return msg;
}

function getVPNComparisonMessage() {
  return `${constants.EMOJI.INFO} ${markdown.bold('Comparación de protocolos')}\n\n` +
         `${markdown.bold('🔐 WireGuard:')}\n` +
         `✅ Más rápido\n` +
         `✅ Menor consumo de batería\n` +
         `✅ Mejor para móviles\n` +
         `❌ Configuración más compleja\n\n` +
         `${markdown.bold('🌐 Outline:')}\n` +
         `✅ Configuración instantánea\n` +
         `✅ Un solo enlace\n` +
         `✅ Compatible con todo\n` +
         `❌ Ligeramente más lento\n\n` +
         `${markdown.bold('Recomendación:')}\n` +
         `• ${markdown.bold('WireGuard')} si usas principalmente el móvil\n` +
         `• ${markdown.bold('Outline')} si necesitas simplicidad`;
}

// ============================================================================
// ⚠️ MENSAJES DE ERROR Y ADVERTENCIA
// ============================================================================

function getVPNCreationErrorMessage(vpnType, error) {
  return `${constants.EMOJI.ERROR} ${markdown.bold('Error al crear conexión')}\n\n` +
         `No se pudo crear tu conexión ${vpnType}.\n\n` +
         `${markdown.bold('Error:')} ${markdown.escapeMarkdown(error)}\n\n` +
         `${constants.EMOJI.INFO} Intenta nuevamente o contacta al administrador.`;
}

function getVPNServerErrorMessage() {
  return `${constants.EMOJI.ERROR} ${markdown.bold('Error del servidor VPN')}\n\n` +
         `Los servicios VPN no están disponibles temporalmente.\n\n` +
         `${constants.EMOJI.INFO} Por favor, intenta más tarde o contacta al administrador.`;
}

function getVPNQuotaExceededMessage(vpnType) {
  return `${constants.EMOJI.ERROR} ${markdown.bold('Cuota de datos excedida')}\n\n` +
         `Has alcanzado el límite de datos para ${vpnType}.\n\n` +
         `${constants.EMOJI.INFO} Opciones:\n` +
         `• Espera al próximo ciclo de renovación\n` +
         `• Contacta al administrador para aumentar tu cuota`;
}

// ============================================================================
// 🛠️ UTILIDADES
// ============================================================================

/**
 * Genera una barra de progreso visual ASCII
 */
function generateProgressBar(percentage, length = 10) {
  const filled = Math.round((percentage / 100) * length);
  const empty = length - filled;
  
  const bar = '█'.repeat(filled) + '░'.repeat(empty);
  
  let color = '';
  if (percentage < 50) color = '';
  else if (percentage < 80) color = '🟡';
  else if (percentage < 100) color = '🟠';
  else color = '🔴';
  
  return `${color} [${bar}] ${percentage}%`;
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // Menú principal
  getVPNMainMenuMessage,
  getVPNTypeSelectionMessage,
  
  // WireGuard
  getWireGuardWelcomeMessage,
  getWireGuardCreationSuccessMessage,
  getWireGuardConfigFileMessage,
  getWireGuardQRCodeMessage,
  getWireGuardStatsMessage,
  getWireGuardDeleteConfirmMessage,
  getWireGuardDeletedMessage,
  getWireGuardAlreadyExistsMessage,
  getWireGuardNotFoundMessage,
  getWireGuardSuspendedMessage,
  
  // Outline
  getOutlineWelcomeMessage,
  getOutlineCreationSuccessMessage,
  getOutlineAccessUrlMessage,
  getOutlineStatsMessage,
  getOutlineDeleteConfirmMessage,
  getOutlineDeletedMessage,
  getOutlineAlreadyExistsMessage,
  getOutlineNotFoundMessage,
  getOutlineSuspendedMessage,
  
  // Resumen y comparación
  getVPNStatusSummaryMessage,
  getVPNComparisonMessage,
  
  // Errores
  getVPNCreationErrorMessage,
  getVPNServerErrorMessage,
  getVPNQuotaExceededMessage
};
