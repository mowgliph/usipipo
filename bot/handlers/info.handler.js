/**
 * @fileoverview Manejador de comandos de información (estado del servidor, ayuda, lista de comandos).
 * @version 1.0.1
 * @author Team uSipipo
 * @description Implementa la limpieza de la UI (eliminación del mensaje de interacción previa).
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
  
  /**
   * 🆕 Método auxiliar para eliminar el mensaje de la interacción previa (comando o botón).
   * @private
   * @param {object} ctx - Objeto de contexto de Telegraf.
   */
  async _cleanPreviousMessage(ctx) {
    let chatId = ctx.chat?.id;
    let messageId;

    if (ctx.callbackQuery) {
      // Si es un callback de un botón, el mensaje a eliminar es el mensaje del botón.
      messageId = ctx.callbackQuery.message?.message_id;
    } else if (ctx.message) {
      // Si es un comando o texto, el mensaje a eliminar es el mensaje del usuario.
      messageId = ctx.message.message_id;
    }

    if (chatId && messageId) {
      try {
        await ctx.deleteMessage(messageId);
        logger.debug(`Mensaje ${messageId} eliminado en chat ${chatId}.`);
      } catch (e) {
        // Ignoramos errores comunes como "Message to delete not found" (si ya fue eliminado)
        // o si el bot no tiene permisos de administrador.
        logger.debug('No se pudo eliminar el mensaje previo:', e.message);
      }
    }
  }

  // ==========================================================================
  // 🖥️ ESTADO DEL SERVIDOR (/status)
  // ==========================================================================
  /**
   * Maneja la solicitud del estado del servidor.
   * @param {object} ctx - Objeto de contexto de Telegraf.
   */
  async handleServerStatus(ctx) {
    const userId = ctx.from?.id;

    // 1. Limpieza de UI: Eliminar el mensaje del comando o botón
    await this._cleanPreviousMessage(ctx);
    
    // 2. Responde al callbackQuery si existe para eliminar el estado de carga
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
          outlineInfo = { version: 'N/A', status: 'Unavailable', error: true };
          logData.service_ok = false;
        }
      } catch (serviceErr) {
        logger.warn('OutlineService.getServerInfo ha fallado', serviceErr.message, logData);
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

    // 1. Limpieza de UI: Eliminar el mensaje del comando o botón
    await this._cleanPreviousMessage(ctx);

    // 2. Responde al callbackQuery si existe
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

    // 1. Limpieza de UI: Eliminar el mensaje del comando o botón
    await this._cleanPreviousMessage(ctx);

    // 2. Responde al callbackQuery si existe
    if (ctx.callbackQuery) {
      await ctx.answerCbQuery().catch(e => logger.debug('Error al responder a cbQuery en commands:', e.message));
    }

    try {
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
