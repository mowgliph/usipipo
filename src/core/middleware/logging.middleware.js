'use strict';

/**
 * ============================================================================
 * 📊 LOGGING MIDDLEWARE - uSipipo VPN Bot
 * ============================================================================
 * Middleware para logging estructurado de todas las interacciones.
 * Registra: entrada, procesamiento y salida de cada request.
 * ============================================================================
 */

const logger = require('../utils/logger');
const constants = require('../../config/constants');

/**
 * Extrae metadata del contexto de Telegram
 */
function extractContextMetadata(ctx) {
  return {
    userId: ctx.from?.id,
    username: ctx.from?.username ? `@${ctx.from.username}` : null,
    firstName: ctx.from?.first_name || '',
    lastName: ctx.from?.last_name || '',
    chatId: ctx.chat?.id,
    chatType: ctx.chat?.type,
    updateType: ctx.updateType,
    messageId: ctx.message?.message_id || ctx.callbackQuery?.message?.message_id,
    text: ctx.message?.text || ctx.callbackQuery?.data || 'N/A',
    isCallback: !!ctx.callbackQuery,
    isCommand: ctx.message?.text?.startsWith('/') || false
  };
}

/**
 * Formatea el nombre completo del usuario
 */
function formatUserName(meta) {
  const fullName = [meta.firstName, meta.lastName].filter(Boolean).join(' ');
  return fullName || meta.username || `User#${meta.userId}`;
}

/**
 * Middleware principal de logging
 */
async function loggingMiddleware(ctx, next) {
  const startTime = Date.now();
  const meta = extractContextMetadata(ctx);
  const userName = formatUserName(meta);

  // Log de entrada (request)
  logger.info(`${constants.EMOJI.IN} ENTRY`, {
    user: userName,
    userId: meta.userId,
    type: meta.updateType,
    content: meta.text.substring(0, 100),
    chatType: meta.chatType,
    isCommand: meta.isCommand,
    isCallback: meta.isCallback
  });

  try {
    // Continuar con la cadena de middlewares
    await next();
    
    const duration = Date.now() - startTime;
    
    // Log de salida exitosa (response)
    logger.info(`${constants.EMOJI.OUT} EXIT_SUCCESS`, {
      user: userName,
      userId: meta.userId,
      type: meta.updateType,
      duration: `${duration}ms`,
      status: 'COMPLETED'
    });

  } catch (error) {
    const duration = Date.now() - startTime;
    
    // Log de salida con error
    logger.error(`${constants.EMOJI.ERROR} EXIT_ERROR`, error, {
      user: userName,
      userId: meta.userId,
      type: meta.updateType,
      duration: `${duration}ms`,
      status: 'ERROR'
    });

    // Propagar el error para que el error middleware lo maneje
    throw error;
  }
}

/**
 * Middleware específico para log de comandos
 */
function commandLoggingMiddleware(ctx, next) {
  const meta = extractContextMetadata(ctx);
  
  if (meta.isCommand) {
    const userName = formatUserName(meta);
    logger.http('COMMAND', `/command${meta.text}`, 200, 0, {
      user: userName,
      userId: meta.userId,
      command: meta.text,
      chatType: meta.chatType
    });
  }
  
  return next();
}

/**
 * Middleware para log de callbacks (botones)
 */
function callbackLoggingMiddleware(ctx, next) {
  const meta = extractContextMetadata(ctx);
  
  if (meta.isCallback) {
    const userName = formatUserName(meta);
    logger.http('CALLBACK', `/callback${meta.text}`, 200, 0, {
      user: userName,
      userId: meta.userId,
      callbackData: meta.text,
      chatType: meta.chatType
    });
  }
  
  return next();
}

module.exports = {
  loggingMiddleware,
  commandLoggingMiddleware,
  callbackLoggingMiddleware
};