/**
 * @fileoverview Manejador de comandos de información (estado del servidor, ayuda, lista de comandos).
 * @version 1.0.0
 * @author Team uSipipo
 */

'use strict';

const OutlineService = require('../services/outline.service');
const messages = require('../utils/messages');
const keyboards = require('../utils/keyboards');
const { isAuthorized, isAdmin } = require('../middleware/auth.middleware');
const logger = require('../utils/logger');

/**
 * Clase que gestiona las respuestas a comandos de información.
 * Asegura el uso de parse_mode: 'Markdown' (V1) para todas las respuestas.
 */
class InfoHandler {
  /**
   * Asegura que las respuestas de texto usen 'Markdown' para compatibilidad con V1.
   * @private
   * @param {object} keyboard - Objeto de teclado inline o reply.
   * @returns {object} Opciones de respuesta para ctx.reply.
   */
  _getReplyOptions(keyboard = {}) {
    return {
      parse_mode: 'Markdown',
      ...keyboard,
      disable_web_page_preview: true, // Recomendado para evitar previsualizaciones no deseadas
    };
  }

  // ==========================================================================
  // 🖥️ ESTADO DEL SERVIDOR (/status)
  // ==========================================================================
  /**
   * Maneja la solicitud del estado del servidor.
   * Obtiene la información del servicio Outline y la presenta al usuario.
   * @param {object} ctx - Objeto de contexto de Telegraf.
   */
  async handleServerStatus(ctx) {
    const userId = ctx.from?.id;

    // Responde al callbackQuery si existe para eliminar el estado de carga
    if (ctx.callbackQuery) {
      await ctx.answerCbQuery().catch(e => logger.debug('Error al responder a cbQuery en status:', e.message));
    }

    try {
      let outlineInfo = {};
      const logData = { userId };

      // Intento robusto para obtener la información del servidor
      try {
        if (typeof OutlineService.getServerInfo === 'function') {
          outlineInfo = await OutlineService.getServerInfo();
          logData.service_ok = true;
        } else {
          // Fallback en caso de que el método aún no esté disponible o se llame mal
          outlineInfo = { version: 'N/A', status: 'Unavailable', error: true };
          logData.service_ok = false;
        }
      } catch (serviceErr) {
        logger.warn('OutlineService.getServerInfo ha fallado', serviceErr.message, logData);
        // Marcador de error para el mensaje al usuario
        outlineInfo = { error: true, status: 'Error' };
        logData.service_ok = false;
      }

      // El mensaje se formatea con el resultado y se envía.
      await ctx.reply(
        messages.SERVER_STATUS(outlineInfo),
        this._getReplyOptions(keyboards.backButton())
      );

      logger.info('server_status manejado con éxito', logData);
    } catch (err) {
      logger.error('Error al manejar server_status', err, { userId });

      // Mensaje de error formateado para el usuario
      await ctx.reply(
        messages.ERROR_SERVER_STATUS || '⚠️ *Error inesperado obteniendo estado del servidor.*',
        this._getReplyOptions(keyboards.backButton())
      );
    }
  }

  // ==========================================================================
  // ❓ AYUDA (/help)
  // ==========================================================================
  /**
   * Muestra el menú de ayuda, adaptando el mensaje si el usuario está autorizado.
   * @param {object} ctx - Objeto de contexto de Telegraf.
   */
  async handleHelp(ctx) {
    const userId = ctx.from?.id;
    const userIdString = userId?.toString();
    const authorized = isAuthorized(userIdString);

    if (ctx.callbackQuery) {
      await ctx.answerCbQuery().catch(e => logger.debug('Error al responder a cbQuery en help:', e.message));
    }

    // Selecciona el texto y el teclado basado en la autorización
    const text = authorized ? messages.HELP_AUTHORIZED : messages.HELP_UNAUTHORIZED;
    const keyboard = keyboards.helpMenu(); 

    try {
      await ctx.reply(
        text,
        this._getReplyOptions(keyboard)
      );

      logger.info('help manejado con éxito', { userId, authorized });
    } catch (err) {
      logger.error('Error al manejar help', err, { userId });
      
      // Fallback robusto en caso de fallo
      await ctx.reply(
        'ℹ️ *Ayuda no disponible por el momento. Intente más tarde.*',
        this._getReplyOptions()
      );
    }
  }

  // ==========================================================================
  // 📋 LISTA DE COMANDOS (/commands)
  // ==========================================================================
  /**
   * Muestra la lista de comandos disponibles, incluyendo comandos de administrador si aplica.
   * @param {object} ctx - Objeto de contexto de Telegraf.
   */
  async handleCommandList(ctx) {
    const userId = ctx.from?.id;
    const admin = isAdmin(userId);

    if (ctx.callbackQuery) {
      await ctx.answerCbQuery().catch(e => logger.debug('Error al responder a cbQuery en commands:', e.message));
    }

    try {
      // messages.COMMANDS_LIST ya maneja la lógica de incluir comandos de admin
      await ctx.reply(
        messages.COMMANDS_LIST(admin),
        this._getReplyOptions(keyboards.backButton())
      );

      logger.info('command_list manejado con éxito', { userId, admin });
    } catch (err) {
      logger.error('Error al manejar command_list', err, { userId });

      // Mensaje de error para el usuario
      await ctx.reply(
        '⚠️ *Error al mostrar la lista de comandos. Intente de nuevo.*',
        this._getReplyOptions(keyboards.backButton())
      );
    }
  }
}

module.exports = InfoHandler;
