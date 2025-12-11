'use strict';

const startService = require('./start.service');
const messages = require('./start.messages');
const keyboards = require('./start.keyboard');
const logger = require('../../core/utils/logger');
const { withErrorHandling } = require('../../core/middleware/error.middleware');

class StartHandler {
  
  constructor(bot) {
    this.bot = bot;
    this.register();
  }

  register() {
    // Registra el comando /start con manejo de errores
    this.bot.start(withErrorHandling(this.handleStart.bind(this)));
    
    // Registra la acción del botón de invitados
    this.bot.action('check_status', withErrorHandling(this.handleCheckStatus.bind(this)));
  }

  /**
   * Manejador principal de /start
   */
  async handleStart(ctx) {
    const telegramUser = ctx.from;
    
    // Procesar lógica de negocio
    const result = await startService.processUserEntry(telegramUser);
    
    logger.info('START_COMMAND', { 
      userId: telegramUser.id, 
      type: result.type 
    });

    // Responder según el tipo de usuario
    switch (result.type) {
      case 'ADMIN':
        await ctx.reply(
          messages.getAdminWelcome(telegramUser), 
          { 
            parse_mode: 'Markdown',
            ...keyboards.getAdminKeyboard()
          }
        );
        break;

      case 'AUTHORIZED':
        await ctx.reply(
          messages.getAuthorizedWelcome(telegramUser), 
          { 
            parse_mode: 'Markdown',
            ...keyboards.getUserKeyboard()
          }
        );
        break;

      case 'SUSPENDED':
        await ctx.reply(
          messages.getSuspendedMessage(),
          { parse_mode: 'Markdown' }
        );
        break;

      case 'GUEST':
      default:
        await ctx.reply(
          messages.getUnauthorizedWelcome(telegramUser),
          { 
            parse_mode: 'Markdown',
            ...keyboards.getGuestKeyboard()
          }
        );
        break;
    }
  }

  /**
   * Acción para el botón "Verificar Estado"
   */
  async handleCheckStatus(ctx) {
    // Reutilizamos la lógica de start pero editando el mensaje o enviando uno nuevo
    const telegramUser = ctx.from;
    const result = await startService.processUserEntry(telegramUser);

    if (result.type === 'AUTHORIZED' || result.type === 'ADMIN') {
      await ctx.answerCbQuery('✅ ¡Ya estás autorizado!');
      // Redirigir al flujo normal
      return this.handleStart(ctx);
    } else {
      await ctx.answerCbQuery('❌ Aún no estás autorizado.');
      await ctx.reply('⚠️ Tu estado sigue siendo: *Sin autorización*. Contacta al administrador.', { parse_mode: 'Markdown' });
    }
  }
}

module.exports = StartHandler;
