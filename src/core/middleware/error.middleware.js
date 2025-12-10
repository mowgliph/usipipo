'use strict';

/**
 * ============================================================================
 * 🚨 ERROR MIDDLEWARE - uSipipo VPN Bot
 * ============================================================================
 * Middleware centralizado para captura y manejo de errores.
 * Se ejecuta como último middleware en la cadena.
 * ============================================================================
 */

const logger = require('../utils/logger');
const markdown = require('../utils/markdown');
const constants = require('../../config/constants');

/**
 * Middleware de manejo de errores global
 */
async function errorMiddleware(error, ctx, next) {
  // Si no hay error, continuamos
  if (!error) return next();

  const userId = ctx.from?.id;
  const chatId = ctx.chat?.id;
  const updateType = ctx.updateType;
  const message = ctx.message?.text || ctx.callbackQuery?.data || 'N/A';

  // Log del error con contexto
  logger.error('UNHANDLED_ERROR', error, {
    userId,
    chatId,
    updateType,
    message,
    stack: error.stack
  });

  // Preparar mensaje de error para el usuario
  let errorMessage = `${constants.EMOJI.ERROR} *Error del sistema*\n\n`;
  errorMessage += `Se ha producido un error inesperado. `;
  errorMessage += `El equipo técnico ha sido notificado.\n\n`;
  errorMessage += `*Detalle:* \`${error.message || 'Error desconocido'}\``;

  // Intentar enviar respuesta al usuario
  try {
    if (ctx.chat && !ctx.update.callback_query) {
      await ctx.reply(markdown.escapeMarkdown(errorMessage), {
        parse_mode: 'Markdown'
      });
    } else if (ctx.callbackQuery) {
      await ctx.answerCbQuery('❌ Error interno. Por favor, intenta de nuevo.');
    }
  } catch (replyError) {
    // Si falla el envío, loguear pero no propagar
    logger.error('ERROR_REPLY_FAILED', replyError, {
      originalError: error.message,
      userId,
      chatId
    });
  }

  // IMPORTANTE: No llamamos a next() aquí para evitar propagación
  return;
}

/**
 * Wrapper para manejo de errores en handlers específicos
 */
function withErrorHandling(handler) {
  return async (ctx, next) => {
    try {
      await handler(ctx, next);
    } catch (error) {
      // Pasar el error al middleware global
      return errorMiddleware(error, ctx, next);
    }
  };
}

module.exports = {
  errorMiddleware,
  withErrorHandling
};