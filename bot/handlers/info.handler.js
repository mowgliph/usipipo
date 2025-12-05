// handlers/info.handler.js
const OutlineService = require('../services/outline.service');
const messages = require('../utils/messages');
const { isAuthorized } = require('../middleware/auth.middleware');
const { isAdmin } = require('../middleware/auth.middleware'); 

class InfoHandler {
  /**
   * Muestra estado del servidor
   */
  async handleServerStatus(ctx) {
    await ctx.answerCbQuery();
    
    try {
      const outlineInfo = await OutlineService.getServerInfo();
      await ctx.reply(messages.SERVER_STATUS(outlineInfo), { parse_mode: 'Markdown' });
      
    } catch (error) {
      ctx.reply(messages.ERROR_SERVER_STATUS);
    }
  }

  /**
   * Muestra ayuda
   */
  async handleHelp(ctx) {
    if (ctx.updateType === 'callback_query') {
      await ctx.answerCbQuery();
    }
    
    const userId = ctx.from.id.toString();
    const message = isAuthorized(userId) 
      ? messages.HELP_AUTHORIZED 
      : messages.HELP_UNAUTHORIZED;
    
    return ctx.reply(message, { parse_mode: 'Markdown' });
  }
  
  /**
   * Maneja el comando /comandos
   */
  async handleCommandList(ctx) {
    try {
      const userId = ctx.from.id;
      // Verificamos si es admin usando la utilidad existente
      const isUserAdmin = isAdmin(userId);
      
      await ctx.reply(messages.COMMANDS_LIST(isUserAdmin), {
        parse_mode: 'Markdown'
      });
    } catch (error) {
      console.error('Error en handleCommandList:', error);
      ctx.reply('⚠️ Error al mostrar los comandos.');
    }
  }
  
}

module.exports = InfoHandler;
