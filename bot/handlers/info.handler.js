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
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    try {
      const outlineInfo = await OutlineService.getServerInfo();

      await ctx.reply(messages.SERVER_STATUS(outlineInfo), {
        parse_mode: 'HTML',
        ...keyboards.backButton()
      });

      logger.info('server_status', { userId, ok: true });
    } catch (err) {
      logger.error('server_status', err, { userId });

      await ctx.reply(messages.ERROR_SERVER_STATUS, {
        parse_mode: 'HTML',
        ...keyboards.backButton()
      });
    }
  }

  // ==========================================================================
  // ❓ AYUDA
  // ==========================================================================
  async handleHelp(ctx) {
    const userId = ctx.from?.id?.toString();
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    const authorized = isAuthorized(userId);
    const text = authorized
      ? messages.HELP_AUTHORIZED
      : messages.HELP_UNAUTHORIZED;

    try {
      await ctx.reply(text, {
        parse_mode: 'HTML',
        reply_markup: authorized
          ? keyboards.mainMenuAuthorized().reply_markup
          : keyboards.mainMenuUnauthorized().reply_markup
      });

      logger.info('help', { userId, authorized });
    } catch (err) {
      logger.error('help', err, { userId });
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
        parse_mode: 'HTML',
        ...keyboards.backButton()
      });

      logger.info('command_list', { userId, admin });
    } catch (err) {
      logger.error('command_list', err, { userId });

      await ctx.reply('⚠️ Error al mostrar los comandos.', {
        ...keyboards.backButton()
      });
    }
  }
}

module.exports = InfoHandler;