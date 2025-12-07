const OutlineService = require('../services/outline.service');
const messages = require('../utils/messages');
const { isAuthorized, isAdmin } = require('../middleware/auth.middleware');
const logger = require('../utils/logger');

class InfoHandler {
  /**
   * Estado del servidor (WireGuard + Outline)
   */
  async handleServerStatus(ctx) {
    const userId = ctx.from?.id;

    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    try {
      const outlineInfo = await OutlineService.getServerInfo();
      await ctx.reply(messages.SERVER_STATUS(outlineInfo));

      logger.info(userId, 'server_status', { ok: true });
    } catch (err) {
      logger.error('server_status', err, { userId });
      await ctx.reply(messages.ERROR_SERVER_STATUS);
    }
  }

  /**
   * /help — Ayuda según usuario autorizado o no
   */
  async handleHelp(ctx) {
    const userId = ctx.from?.id?.toString();

    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    const authorized = isAuthorized(userId);
    const msg = authorized ? messages.HELP_AUTHORIZED : messages.HELP_UNAUTHORIZED;

    try {
      await ctx.reply(msg);
      logger.info(userId, 'help', { authorized });
    } catch (err) {
      logger.error('help', err, { userId });
    }
  }

  /**
   * /commands — Lista compacta de comandos
   */
  async handleCommandList(ctx) {
    const userId = ctx.from?.id;

    try {
      const admin = isAdmin(userId);
      await ctx.reply(messages.COMMANDS_LIST(admin));

      logger.info(userId, 'command_list', { admin });
    } catch (err) {
      logger.error('command_list', err, { userId });
      await ctx.reply('⚠️ Error al mostrar los comandos.');
    }
  }
}

module.exports = InfoHandler;