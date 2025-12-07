const OutlineService = require('../services/outline.service');
const messages = require('../utils/messages');
const { isAuthorized, isAdmin } = require('../middleware/auth.middleware');
const logger = require('../utils/logger');

class InfoHandler {
  async handleServerStatus(ctx) {
    const userId = ctx.from?.id;
    await ctx.answerCbQuery?.();

    try {
      const outlineInfo = await OutlineService.getServerInfo();
      // CORREGIDO: HTML
      await ctx.reply(messages.SERVER_STATUS(outlineInfo), {
        parse_mode: 'HTML'
      });

      logger.info(userId, 'handleServerStatus', { status: 'success' });
    } catch (error) {
      logger.error('InfoHandler.handleServerStatus', error, { userId });
      await ctx.reply(messages.ERROR_SERVER_STATUS, { parse_mode: 'HTML' });
    }
  }

  async handleHelp(ctx) {
    await ctx.answerCbQuery?.();

    const userId = ctx.from?.id?.toString();
    const message = isAuthorized(userId)
      ? messages.HELP_AUTHORIZED
      : messages.HELP_UNAUTHORIZED;

    try {
      // CORREGIDO: HTML
      await ctx.reply(message, { parse_mode: 'HTML' });
      logger.info(userId, 'handleHelp', { authorized: isAuthorized(userId) });
    } catch (error) {
      logger.error('InfoHandler.handleHelp', error, { userId });
    }
  }

  async handleCommandList(ctx) {
    const userId = ctx.from?.id;

    try {
      const isUserAdmin = isAdmin(userId);
      // CORREGIDO: HTML
      await ctx.reply(messages.COMMANDS_LIST(isUserAdmin), {
        parse_mode: 'HTML'
      });

      logger.info(userId, 'handleCommandList', { isAdmin: isUserAdmin });
    } catch (error) {
      logger.error('InfoHandler.handleCommandList', error, { userId });
      await ctx.reply('⚠️ Error al mostrar los comandos.');
    }
  }
}

module.exports = InfoHandler;
