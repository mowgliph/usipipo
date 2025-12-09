'use strict';

const OutlineService = require('../services/outline.service');
const messages = require('../utils/messages');
const keyboards = require('../utils/keyboards');
const { isAuthorized, isAdmin } = require('../middleware/auth.middleware');
const logger = require('../utils/logger');

class InfoHandler {
  // ==========================================================================
  // 🖥️ ESTADO DEL SERVIDOR
  // ==========================================================================
  async handleServerStatus(ctx) {
    const userId = ctx.from?.id;
    // Fix: Verificar si existe el callback antes de responder
    if (ctx.callbackQuery) await ctx.answerCbQuery().catch(() => {});

    try {
      // Intentamos obtener info. Si el método no existe o falla, controlamos el error
      let outlineInfo = {};
      try {
        if (typeof OutlineService.getServerInfo === 'function') {
          outlineInfo = await OutlineService.getServerInfo();
        } else {
          // Fallback si el servicio aún no está listo
          outlineInfo = { version: 'N/A', status: 'Unknown' };
        }
      } catch (serviceErr) {
        logger.warn('OutlineService.getServerInfo failed', serviceErr);
        outlineInfo = { error: true };
      }

      // messages.SERVER_STATUS ya devuelve el texto formateado en Markdown V1
      await ctx.reply(messages.SERVER_STATUS(outlineInfo), {
        parse_mode: 'Markdown',
        ...keyboards.backButton()
      });

      logger.info('server_status', { userId, ok: true });
    } catch (err) {
      logger.error('server_status', err, { userId });

      await ctx.reply(messages.ERROR_SERVER_STATUS || '⚠️ *Error obteniendo estado del servidor.*', {
        parse_mode: 'Markdown',
        ...keyboards.backButton()
      });
    }
  }

  // ==========================================================================
  // ❓ AYUDA
  // ==========================================================================
  async handleHelp(ctx) {
    const userId = ctx.from?.id?.toString();
    if (ctx.callbackQuery) await ctx.answerCbQuery().catch(() => {});

    const authorized = isAuthorized(userId);
    
    // Obtenemos el texto y el teclado correcto
    // Fix: Usamos helpMenu() que definimos en keyboards.js en lugar de reutilizar el home
    const text = authorized
      ? messages.HELP_AUTHORIZED
      : messages.HELP_UNAUTHORIZED;

    const keyboard = keyboards.helpMenu(); 

    try {
      await ctx.reply(text, {
        parse_mode: 'Markdown',
        ...keyboard
      });

      logger.info('help', { userId, authorized });
    } catch (err) {
      logger.error('help', err, { userId });
      // Fallback básico
      await ctx.reply('ℹ️ *Ayuda no disponible por el momento.*', { parse_mode: 'Markdown' });
    }
  }

  // ==========================================================================
  // 📋 LISTA DE COMANDOS
  // ==========================================================================
  async handleCommandList(ctx) {
    const userId = ctx.from?.id;
    const admin = isAdmin(userId);

    try {
      await ctx.reply(messages.COMMANDS_LIST(admin), {
        parse_mode: 'Markdown',
        ...keyboards.backButton()
      });

      logger.info('command_list', { userId, admin });
    } catch (err) {
      logger.error('command_list', err, { userId });

      await ctx.reply('⚠️ *Error al mostrar los comandos.*', {
        parse_mode: 'Markdown',
        ...keyboards.backButton()
      });
    }
  }
}

module.exports = InfoHandler;
