// handlers/info.handler.js
const OutlineService = require('../services/outline.service');
const messages = require('../utils/messages');
const { isAuthorized, isAdmin } = require('../middleware/auth.middleware');
const logger = require('../utils/logger');

/**
 * Handler de información del sistema y ayuda del bot.
 * Incluye estado del servidor, guía de uso y lista de comandos.
 */
class InfoHandler {
  /**
   * Obtiene y muestra el estado del servidor (WireGuard + Outline).
   * @param {import('telegraf').Context} ctx
   */
  async handleServerStatus(ctx) {
    const userId = ctx.from?.id;
    await ctx.answerCbQuery?.();

    try {
      const outlineInfo = await OutlineService.getServerInfo();
      await ctx.reply(messages.SERVER_STATUS(outlineInfo), {
        parse_mode: 'MarkdownV2'
      });

      logger.info(userId, 'handleServerStatus', { status: 'success' });
    } catch (error) {
      logger.error('InfoHandler.handleServerStatus', error, { userId });
      await ctx.reply(messages.ERROR_SERVER_STATUS, { parse_mode: 'MarkdownV2' });
    }
  }

  /**
   * Muestra mensaje de ayuda contextual según el rol del usuario.
   * @param {import('telegraf').Context} ctx
   */
  async handleHelp(ctx) {
    await ctx.answerCbQuery?.();

    const userId = ctx.from?.id?.toString();
    const message = isAuthorized(userId)
      ? messages.HELP_AUTHORIZED
      : messages.HELP_UNAUTHORIZED;

    try {
      await ctx.reply(message, { parse_mode: 'MarkdownV2' });
      logger.info(userId, 'handleHelp', { authorized: isAuthorized(userId) });
    } catch (error) {
      logger.error('InfoHandler.handleHelp', error, { userId });
    }
  }

  /**
   * Muestra la lista de comandos disponibles para el usuario actual.
   * @param {import('telegraf').Context} ctx
   */
  async handleCommandList(ctx) {
    const userId = ctx.from?.id;

    try {
      const isUserAdmin = isAdmin(userId);
      await ctx.reply(messages.COMMANDS_LIST(isUserAdmin), {
        parse_mode: 'MarkdownV2'
      });

      logger.info(userId, 'handleCommandList', { isAdmin: isUserAdmin });
    } catch (error) {
      logger.error('InfoHandler.handleCommandList', error, { userId });
      await ctx.reply('⚠️ Error al mostrar los comandos.');
    }
  }
}

module.exports = InfoHandler;