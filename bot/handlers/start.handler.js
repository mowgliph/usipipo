'use strict';

/**
 * @fileoverview StartHandler.js — Manejador principal del menú inicial (v1.0.0)
 * @version 1.0.0
 * @author Team uSipipo
 * @description Maneja /start y callback 'start' con limpieza de UI premium.
 * Compatible con AuthHandler existente y UserManager singleton.
 */

const userManager = require('../services/userManager.service');
const { isAuthorized, isAdmin } = require('../middleware/auth.middleware');
const messages = require('../utils/messages');
const keyboards = require('../utils/keyboards');
const logger = require('../utils/logger');

/**
 * Clase que gestiona el punto de entrada principal del bot.
 * - Comando /start
 * - Botón "Volver al Inicio" (callback_data: 'start')
 * - Limpieza automática de UI previa
 */
class StartHandler {
  /**
   * Opciones centralizadas para todas las respuestas.
   * @private
   * @param {object} extra - Opciones adicionales (reply_markup, etc.)
   * @returns {object} Opciones completas para ctx.reply
   */
  _getReplyOptions(extra = {}) {
    return {
      parse_mode: 'Markdown',
      disable_web_page_preview: true,
      ...extra
    };
  }

  /**
   * 🧹 Limpieza elegante del mensaje previo (comando o botón).
   * Compatible con el patrón de InfoHandler.js v1.0.1
   * @private
   * @param {object} ctx - Contexto de Telegraf
   */
  async _cleanPreviousMessage(ctx) {
    let chatId = ctx.chat?.id;
    let messageId;

    if (ctx.callbackQuery) {
      messageId = ctx.callbackQuery.message?.message_id;
    } else if (ctx.message) {
      messageId = ctx.message.message_id;
    }

    if (chatId && messageId) {
      try {
        await ctx.deleteMessage(messageId);
        logger.debug(`StartHandler: Mensaje ${messageId} eliminado en chat ${chatId}`);
      } catch (e) {
        logger.debug('StartHandler: No se pudo limpiar mensaje previo:', e.message);
      }
    }
  }

  /**
   * 🎛️ PUNTO DE ENTRADA PRINCIPAL
   * Maneja tanto comando /start como callback_data: 'start'
   * @param {object} ctx - Contexto de Telegraf
   */
  async handleStart(ctx) {
    const userId = ctx.from?.id?.toString();
    if (!userId) {
      logger.error('StartHandler: userId no válido');
      return ctx.reply('❌ Error de contexto. Intente /start nuevamente.');
    }

    try {
      // 1. LIMPIEZA DE UI (estándar premium)
      await this._cleanPreviousMessage(ctx);

      // 2. RESPONDER CALLBACK_QUERY (elimina loading en botones)
      if (ctx.callbackQuery) {
        await ctx.answerCbQuery().catch(() => {});
      }

      // 3. RESOLVER ESTADO Y ENVIAR MENÚ
      const authorized = isAuthorized(userId);
      const name = ctx.from.first_name || ctx.from.username || 'Usuario';

      const text = authorized
        ? messages.WELCOME_AUTHORIZED(name)
        : messages.WELCOME_UNAUTHORIZED(name);

      const keyboard = authorized
        ? keyboards.homeAuthorized()
        : keyboards.homeUnauthorized();

      await ctx.reply(text, this._getReplyOptions(keyboard.reply_markup));

      logger.info('StartHandler ejecutado', { 
        userId, 
        authorized, 
        fromCommand: !!ctx.message?.text?.startsWith('/start'),
        fromButton: !!ctx.callbackQuery 
      });

    } catch (error) {
      logger.error('StartHandler.handleStart error', error, { userId });

      // Fallback crítico: siempre funcional
      const fallbackText = '🏠 *Menú Principal*

Seleccione una opción del teclado.';
      await ctx.reply(fallbackText, this._getReplyOptions(keyboards.homeUnauthorized().reply_markup));
    }
  }
}

module.exports = StartHandler;