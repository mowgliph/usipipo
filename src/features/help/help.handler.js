'use strict';

/**
 * ============================================================================
 * 🎛️ HELP HANDLER - uSipipo VPN Bot
 * ============================================================================
 * Controlador principal para todas las interacciones del módulo de ayuda.
 * Maneja comandos, callbacks y navegación.
 * ============================================================================
 */

const { Composer } = require('telegraf');
const helpService = require('./help.service');
const logger = require('../../../core/utils/logger');
const { requireAuth } = require('../../../core/middleware/auth.middleware');
const constants = require('../../../config/constants');

const helpHandler = new Composer();

// ============================================================================
// 🔒 APLICAR MIDDLEWARE DE AUTENTICACIÓN
// ============================================================================

helpHandler.use(requireAuth);

// ============================================================================
// 📌 COMANDO: /help
// ============================================================================

helpHandler.command('help', async (ctx) => {
  try {
    const userId = String(ctx.from.id);
    const args = ctx.message.text.split(' ').slice(1);
    const category = args[0] || 'main';

    const content = helpService.getHelpContent(category, userId);

    await ctx.reply(content.message, {
      parse_mode: 'Markdown',
      disable_web_page_preview: true,
      ...content.keyboard
    });

    logger.info('[Help] Command executed', {
      userId,
      category,
      username: ctx.from.username
    });

  } catch (error) {
    logger.error('[Help] Command error', error, {
      userId: ctx.from?.id,
      command: ctx.message?.text
    });

    await ctx.reply(
      `${constants.EMOJI.ERROR} Error al cargar la ayuda. Intenta de nuevo.`,
      { parse_mode: 'Markdown' }
    );
  }
});

// ============================================================================
// 📌 ALIAS: /ayuda
// ============================================================================

helpHandler.command('ayuda', async (ctx) => {
  return ctx.telegram.sendMessage(
    ctx.chat.id,
    'ℹ️ Usa el comando /help para acceder al centro de ayuda.',
    { parse_mode: 'Markdown' }
  );
});

// ============================================================================
// 🔘 CALLBACK: Navegación principal
// ============================================================================

helpHandler.action('help_main', async (ctx) => {
  try {
    await ctx.answerCbQuery();
    
    const userId = String(ctx.from.id);
    const content = helpService.getHelpContent('main', userId);

    await ctx.editMessageText(content.message, {
      parse_mode: 'Markdown',
      disable_web_page_preview: true,
      ...content.keyboard
    });

    logger.debug('[Help] Main menu displayed', { userId });

  } catch (error) {
    logger.error('[Help] Callback error - help_main', error);
    await ctx.answerCbQuery('❌ Error al cargar el menú.');
  }
});

// ============================================================================
// 🔘 CALLBACK: Ayuda VPN
// ============================================================================

helpHandler.action('help_vpn', async (ctx) => {
  try {
    await ctx.answerCbQuery();
    
    const userId = String(ctx.from.id);
    const content = helpService.getHelpContent('vpn', userId);

    await ctx.editMessageText(content.message, {
      parse_mode: 'Markdown',
      disable_web_page_preview: true,
      ...content.keyboard
    });

    logger.debug('[Help] VPN help displayed', { userId });

  } catch (error) {
    logger.error('[Help] Callback error - help_vpn', error);
    await ctx.answerCbQuery('❌ Error al cargar ayuda VPN.');
  }
});

// ============================================================================
// 🔘 CALLBACK: Ayuda Perfil
// ============================================================================

helpHandler.action('help_profile', async (ctx) => {
  try {
    await ctx.answerCbQuery();
    
    const userId = String(ctx.from.id);
    const content = helpService.getHelpContent('profile', userId);

    await ctx.editMessageText(content.message, {
      parse_mode: 'Markdown',
      disable_web_page_preview: true,
      ...content.keyboard
    });

    logger.debug('[Help] Profile help displayed', { userId });

  } catch (error) {
    logger.error('[Help] Callback error - help_profile', error);
    await ctx.answerCbQuery('❌ Error al cargar ayuda de perfil.');
  }
});

// ============================================================================
// 🔘 CALLBACK: Ayuda Sistema
// ============================================================================

helpHandler.action('help_system', async (ctx) => {
  try {
    await ctx.answerCbQuery();
    
    const userId = String(ctx.from.id);
    const content = helpService.getHelpContent('system', userId);

    await ctx.editMessageText(content.message, {
      parse_mode: 'Markdown',
      disable_web_page_preview: true,
      ...content.keyboard
    });

    logger.debug('[Help] System help displayed', { userId });

  } catch (error) {
    logger.error('[Help] Callback error - help_system', error);
    await ctx.answerCbQuery('❌ Error al cargar info del sistema.');
  }
});

// ============================================================================
// 🔘 CALLBACK: Ayuda Admin (solo administradores)
// ============================================================================

helpHandler.action('help_admin', async (ctx) => {
  try {
    await ctx.answerCbQuery();
    
    const userId = String(ctx.from.id);
    const content = helpService.getHelpContent('admin', userId);

    await ctx.editMessageText(content.message, {
      parse_mode: 'Markdown',
      disable_web_page_preview: true,
      ...content.keyboard
    });

    logger.debug('[Help] Admin help displayed', { userId });

  } catch (error) {
    logger.error('[Help] Callback error - help_admin', error);
    await ctx.answerCbQuery('❌ Error al cargar ayuda admin.');
  }
});

// ============================================================================
// 🔘 CALLBACK: Solución de problemas
// ============================================================================

helpHandler.action('help_troubleshooting', async (ctx) => {
  try {
    await ctx.answerCbQuery();
    
    const userId = String(ctx.from.id);
    const content = helpService.getHelpContent('troubleshooting', userId);

    await ctx.editMessageText(content.message, {
      parse_mode: 'Markdown',
      disable_web_page_preview: true,
      ...content.keyboard
    });

    logger.debug('[Help] Troubleshooting help displayed', { userId });

  } catch (error) {
    logger.error('[Help] Callback error - help_troubleshooting', error);
    await ctx.answerCbQuery('❌ Error al cargar solución de problemas.');
  }
});

// ============================================================================
// 🔘 CALLBACK: Lista de comandos
// ============================================================================

helpHandler.action('help_commands', async (ctx) => {
  try {
    await ctx.answerCbQuery();
    
    const userId = String(ctx.from.id);
    const content = helpService.getHelpContent('commands', userId);

    await ctx.editMessageText(content.message, {
      parse_mode: 'Markdown',
      disable_web_page_preview: true,
      ...content.keyboard
    });

    logger.debug('[Help] Commands list displayed', { userId });

  } catch (error) {
    logger.error('[Help] Callback error - help_commands', error);
    await ctx.answerCbQuery('❌ Error al cargar lista de comandos.');
  }
});

// ============================================================================
// 🔘 CALLBACK: Enlaces de descarga
// ============================================================================

helpHandler.action('help_download_wg', async (ctx) => {
  const links = helpService.getDownloadLinks();
  await ctx.answerCbQuery('📥 Abriendo enlace de descarga...', { url: links.wireguard });
  logger.debug('[Help] WireGuard download link opened', { userId: ctx.from.id });
});

helpHandler.action('help_download_outline', async (ctx) => {
  const links = helpService.getDownloadLinks();
  await ctx.answerCbQuery('📥 Abriendo enlace de descarga...', { url: links.outline });
  logger.debug('[Help] Outline download link opened', { userId: ctx.from.id });
});

// ============================================================================
// 🔘 CALLBACK: Contactar administrador
// ============================================================================

helpHandler.action('help_contact_admin', async (ctx) => {
  try {
    await ctx.answerCbQuery();
    
    const config = require('../../../config/environment');
    const markdown = require('../../../core/utils/markdown');
    
    const message = `${constants.EMOJI.INFO} *Contactar Administrador*\n\n` +
                   `Para reportar un problema o solicitar ayuda:\n\n` +
                   `1. Usa el comando ${markdown.code('/report')}\n` +
                   `2. O contacta directamente al admin con ID: ${markdown.code(config.ADMIN_ID)}\n\n` +
                   `Incluye tu ID de usuario y descripción del problema.`;

    await ctx.editMessageText(message, {
      parse_mode: 'Markdown',
      ...require('./help.keyboard').getBackToHelpKeyboard()
    });

  } catch (error) {
    logger.error('[Help] Callback error - help_contact_admin', error);
    await ctx.answerCbQuery('❌ Error al cargar información de contacto.');
  }
});

// ============================================================================
// 🧹 LIMPIEZA AUTOMÁTICA DE SESIONES
// ============================================================================

// Ejecutar cada hora
setInterval(() => {
  helpService.clearOldSessions(30);
}, 60 * 60 * 1000);

// ============================================================================
// 📊 COMANDO DE ESTADÍSTICAS (SOLO ADMIN)
// ============================================================================

helpHandler.command('helpstats', async (ctx) => {
  try {
    const { isAdmin } = require('../../../core/middleware/auth.middleware');
    const userId = String(ctx.from.id);

    if (!isAdmin(userId)) {
      return ctx.reply('❌ Comando exclusivo para administradores.');
    }

    const stats = helpService.getStats();
    const markdown = require('../../../core/utils/markdown');

    let message = `${constants.EMOJI.INFO} *Estadísticas de Ayuda*\n\n`;
    message += `*Total de solicitudes:* ${markdown.code(String(stats.totalRequests))}\n\n`;
    message += `*Por categoría:*\n`;
    
    for (const [category, count] of Object.entries(stats.byCategory)) {
      message += `• ${category}: ${count}\n`;
    }

    await ctx.reply(message, { parse_mode: 'Markdown' });

    logger.info('[Help] Stats command executed', { userId, stats });

  } catch (error) {
    logger.error('[Help] Stats command error', error);
    await ctx.reply('❌ Error al obtener estadísticas.');
  }
});

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = helpHandler;
