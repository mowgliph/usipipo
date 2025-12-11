'use strict';

/**
 * ============================================================================
 * 📡 INFO HANDLER - uSipipo VPN Bot
 * ============================================================================
 * Manejadores de comandos y callbacks para el módulo de información
 * ============================================================================
 */

const messages = require('./info.messages');
const keyboards = require('./info.keyboard');
const infoService = require('./info.service');
const { requireAuth } = require('../../core/middleware/auth.middleware');
const { withErrorHandling } = require('../../core/middleware/error.middleware');
const logger = require('../../core/utils/logger');
const markdown = require('../../core/utils/markdown');
const constants = require('../../config/constants');

// ============================================================================
// 📋 COMANDO PRINCIPAL: /info
// ============================================================================

const handleInfoCommand = withErrorHandling(async (ctx) => {
  logger.info('[InfoHandler] Comando /info ejecutado', {
    userId: ctx.from.id,
    username: ctx.from.username
  });

  const introMessage = `${constants.EMOJI.INFO} ${markdown.bold('Centro de Información')}\n\n` +
                       `Selecciona una categoría para obtener más información:`;

  await ctx.reply(introMessage, {
    parse_mode: 'Markdown',
    ...keyboards.getInfoMainKeyboard()
  });
});

// ============================================================================
// 🖥️ CALLBACKS: INFORMACIÓN DEL SISTEMA
// ============================================================================

const handleSystemInfo = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery('📊 Cargando información del sistema...');

  const message = messages.getSystemInfoMessage();
  
  await ctx.editMessageText(message, {
    parse_mode: 'Markdown',
    ...keyboards.getBackToInfoKeyboard()
  });
});

const handleServerInfo = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery('🌐 Cargando información del servidor...');

  const message = messages.getServerInfoMessage();
  
  await ctx.editMessageText(message, {
    parse_mode: 'Markdown',
    ...keyboards.getBackToInfoKeyboard()
  });
});

const handleNetworkInfo = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery('📡 Cargando información de red...');

  const message = messages.getNetworkInfoMessage();
  
  await ctx.editMessageText(message, {
    parse_mode: 'Markdown',
    ...keyboards.getBackToInfoKeyboard()
  });
});

// ============================================================================
// 🔐 CALLBACKS: INFORMACIÓN VPN
// ============================================================================

const handleWireGuardInfo = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery('🔐 Cargando información de WireGuard...');

  const message = messages.getWireGuardInfoMessage();
  
  await ctx.editMessageText(message, {
    parse_mode: 'Markdown',
    ...keyboards.getBackToInfoKeyboard()
  });
});

const handleOutlineInfo = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery('🌐 Cargando información de Outline...');

  const message = messages.getOutlineInfoMessage();
  
  await ctx.editMessageText(message, {
    parse_mode: 'Markdown',
    ...keyboards.getBackToInfoKeyboard()
  });
});

const handleComparisonInfo = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery('⚖️ Comparando protocolos...');

  const message = messages.getComparisonMessage();
  
  await ctx.editMessageText(message, {
    parse_mode: 'Markdown',
    ...keyboards.getBackToInfoKeyboard()
  });
});

// ============================================================================
// 🛡️ CALLBACKS: SEGURIDAD Y PRIVACIDAD
// ============================================================================

const handleSecurityInfo = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery('🛡️ Cargando información de seguridad...');

  const message = messages.getSecurityInfoMessage();
  
  await ctx.editMessageText(message, {
    parse_mode: 'Markdown',
    ...keyboards.getBackToInfoKeyboard()
  });
});

const handleDataPolicyInfo = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery('📋 Cargando política de datos...');

  const message = messages.getDataPolicyMessage();
  
  await ctx.editMessageText(message, {
    parse_mode: 'Markdown',
    ...keyboards.getBackToInfoKeyboard()
  });
});

// ============================================================================
// ❓ CALLBACKS: FAQ Y AYUDA
// ============================================================================

const handleFAQ = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery('❓ Cargando preguntas frecuentes...');

  const message = messages.getFAQMessage();
  
  await ctx.editMessageText(message, {
    parse_mode: 'Markdown',
    ...keyboards.getBackToInfoKeyboard()
  });
});

const handleTroubleshooting = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery('🔧 Cargando solución de problemas...');

  const message = messages.getTroubleshootingMessage();
  
  await ctx.editMessageText(message, {
    parse_mode: 'Markdown',
    ...keyboards.getBackToInfoKeyboard()
  });
});

// ============================================================================
// 📞 CALLBACKS: CONTACTO Y ACERCA DE
// ============================================================================

const handleContactInfo = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery('📞 Cargando información de contacto...');

  const message = messages.getContactMessage();
  
  await ctx.editMessageText(message, {
    parse_mode: 'Markdown',
    ...keyboards.getBackToInfoKeyboard()
  });
});

const handleAboutInfo = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery('ℹ️ Cargando información del bot...');

  const message = messages.getAboutMessage();
  
  await ctx.editMessageText(message, {
    parse_mode: 'Markdown',
    ...keyboards.getBackToInfoKeyboard()
  });
});

// ============================================================================
// 📱 CALLBACK: DESCARGAS
// ============================================================================

const handleDownloadsInfo = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery('📱 Abriendo enlaces de descarga...');

  const message = `${constants.EMOJI.INFO} ${markdown.bold('Descargar Clientes VPN')}\n\n` +
                  `Selecciona tu plataforma para descargar el cliente oficial:\n\n` +
                  `${markdown.bold('🔐 WireGuard:')}\n` +
                  `• iOS, Android, Windows, macOS, Linux\n\n` +
                  `${markdown.bold('🌐 Outline:')}\n` +
                  `• iOS, Android, Windows, macOS, Linux\n\n` +
                  `_Haz clic en los botones de abajo para acceder a las descargas oficiales_`;
  
  await ctx.editMessageText(message, {
    parse_mode: 'Markdown',
    ...keyboards.getDownloadKeyboard()
  });
});

// ============================================================================
// 🔄 CALLBACK: VOLVER AL MENÚ PRINCIPAL
// ============================================================================

const handleBackToInfo = withErrorHandling(async (ctx) => {
  await ctx.answerCbQuery();

  const introMessage = `${constants.EMOJI.INFO} ${markdown.bold('Centro de Información')}\n\n` +
                       `Selecciona una categoría para obtener más información:`;

  await ctx.editMessageText(introMessage, {
    parse_mode: 'Markdown',
    ...keyboards.getInfoMainKeyboard()
  });
});

// ============================================================================
// 📊 COMANDO AVANZADO: /stats (solo para admins)
// ============================================================================

const handleStatsCommand = withErrorHandling(async (ctx) => {
  const stats = infoService.formatSystemStatsForUser();
  const health = await infoService.checkSystemHealth();

  const healthEmoji = health.status === 'healthy' ? constants.EMOJI.SUCCESS :
                      health.status === 'warning' ? constants.EMOJI.WARNING :
                      constants.EMOJI.ERROR;

  let message = `${constants.EMOJI.INFO} ${markdown.bold('Estadísticas del Sistema')}\n\n`;
  
  message += `${markdown.bold('🏥 Estado:')} ${healthEmoji} ${health.status}\n\n`;
  
  message += `${markdown.bold('👥 Usuarios:')}\n`;
  message += `• Total: ${markdown.code(stats.users.total)}\n`;
  message += `• Activos: ${markdown.code(stats.users.active)}\n`;
  message += `• Suspendidos: ${markdown.code(stats.users.suspended)}\n`;
  message += `• Administradores: ${markdown.code(stats.users.admins)}\n\n`;
  
  message += `${markdown.bold('🔐 WireGuard:')}\n`;
  message += `• Activos: ${markdown.code(stats.vpn.wireguard.active)}\n`;
  message += `• Suspendidos: ${markdown.code(stats.vpn.wireguard.suspended)}\n`;
  message += `• Datos totales: ${markdown.code(stats.vpn.wireguard.totalData)}\n`;
  message += `• Promedio: ${markdown.code(stats.vpn.wireguard.averageData)}\n\n`;
  
  message += `${markdown.bold('🌐 Outline:')}\n`;
  message += `• Activos: ${markdown.code(stats.vpn.outline.active)}\n`;
  message += `• Suspendidos: ${markdown.code(stats.vpn.outline.suspended)}\n`;
  message += `• Datos totales: ${markdown.code(stats.vpn.outline.totalData)}\n`;
  message += `• Promedio: ${markdown.code(stats.vpn.outline.averageData)}\n\n`;
  
  message += `${markdown.bold('🖥️ Sistema:')}\n`;
  message += `• Uptime: ${markdown.code(stats.system.uptime)}\n`;
  message += `• CPUs: ${markdown.code(stats.system.cpuCount)}\n`;
  message += `• Memoria: ${markdown.code(stats.system.memoryUsage)}\n`;
  message += `• Libre: ${markdown.code(stats.system.freeMemory)}`;

  await ctx.reply(message, {
    parse_mode: 'Markdown',
    ...keyboards.getBackToInfoKeyboard()
  });
});

// ============================================================================
// 📦 REGISTRO DE HANDLERS
// ============================================================================

function registerInfoHandlers(bot) {
  // Comando principal
  bot.command('info', requireAuth, handleInfoCommand);
  bot.command('stats', requireAuth, handleStatsCommand);

  // Callbacks: Sistema
  bot.action('info_system', requireAuth, handleSystemInfo);
  bot.action('info_server', requireAuth, handleServerInfo);
  bot.action('info_network', requireAuth, handleNetworkInfo);

  // Callbacks: VPN
  bot.action('info_wireguard', requireAuth, handleWireGuardInfo);
  bot.action('info_outline', requireAuth, handleOutlineInfo);
  bot.action('info_comparison', requireAuth, handleComparisonInfo);

  // Callbacks: Seguridad
  bot.action('info_security', requireAuth, handleSecurityInfo);
  bot.action('info_policy', requireAuth, handleDataPolicyInfo);

  // Callbacks: FAQ y Ayuda
  bot.action('info_faq', requireAuth, handleFAQ);
  bot.action('info_troubleshoot', requireAuth, handleTroubleshooting);

  // Callbacks: Contacto y Acerca de
  bot.action('info_contact', requireAuth, handleContactInfo);
  bot.action('info_about', requireAuth, handleAboutInfo);

  // Callbacks: Descargas
  bot.action('info_download', requireAuth, handleDownloadsInfo);

  // Callback: Volver
  bot.action('info_main', requireAuth, handleBackToInfo);

  logger.success('[InfoHandler] Handlers registrados correctamente');
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  registerInfoHandlers,
  
  // Export individual handlers for testing
  handleInfoCommand,
  handleSystemInfo,
  handleServerInfo,
  handleStatsCommand
};
