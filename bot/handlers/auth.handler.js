// handlers/auth.handler.js
const { isAuthorized, isAdmin } = require('../middleware/auth.middleware');
const userManager = require('../services/userManager.service');
const messages = require('../utils/messages');
const keyboards = require('../utils/keyboards');
const config = require('../config/environment');

class AuthHandler {
  constructor(notificationService) {
    this.notificationService = notificationService;
  }

  /**
   * Manejador del comando /start
   * @param {Object} ctx - Contexto de Telegraf
   * @returns {Promise<void>}
   */
  async handleStart(ctx) {
    const userId = ctx.from.id.toString();
    const userName = ctx.from.first_name || 'Usuario';

    if (isAuthorized(userId)) {
      return ctx.reply(
        messages.WELCOME_AUTHORIZED(userName),
        {
          parse_mode: 'MarkdownV2',
          ...keyboards.mainMenuAuthorized()
        }
      );
    }

    return ctx.reply(
      messages.WELCOME_UNAUTHORIZED(userName),
      {
        parse_mode: 'MarkdownV2',
        ...keyboards.mainMenuUnauthorized()
      }
    );
  }

  /**
   * Muestra información del usuario
   * @param {Object} ctx - Contexto de Telegraf
   * @returns {Promise<void>}
   */
  async handleUserInfo(ctx) {
    const user = ctx.from;
    const userId = user.id.toString();
    const authorized = isAuthorized(userId);

    return ctx.reply(
      messages.USER_INFO(user, authorized),
      { parse_mode: 'MarkdownV2' }
    );
  }

  /**
   * Procesa solicitud de acceso
   * @param {Object} ctx - Contexto de Telegraf
   * @returns {Promise<void>}
   */
  async handleAccessRequest(ctx) {
    await ctx.answerCbQuery();
    const user = ctx.from;

    // Mensaje para el usuario
    await ctx.reply(
      messages.ACCESS_REQUEST_SENT(user),
      { parse_mode: 'MarkdownV2' }
    );

    // Notificar al administrador
    await this.notificationService.notifyAdminAccessRequest(user);
  }

  /**
   * Lista usuarios autorizados (solo admin)
   * @param {Object} ctx - Contexto de Telegraf
   * @returns {Promise<void>}
   */
  async handleListUsers(ctx) {
    const userId = ctx.from.id.toString();

    if (!isAdmin(userId)) {
      return ctx.reply(messages.ADMIN_ONLY, { parse_mode: 'MarkdownV2' });
    }

    const activeUsers = userManager.getAllUsers().filter(u => u.status === 'active');
    const listaUsuarios = activeUsers.map((user, index) =>
      `\( {index + 1}. ID: \){code(user.id)} \( {user.role === 'admin' ? '👑 (Admin)' : ''} - \){escapeMarkdown(user.name || 'Sin nombre')}`
    ).join('\n');

    const formattedMessage = `👥 **USUARIOS AUTORIZADOS**\n\n\( {listaUsuarios}\n\n📝 Total: \){activeUsers.length} usuarios`;

    return ctx.reply(formattedMessage, { parse_mode: 'MarkdownV2' });
  }

  /**
   * Comprueba el estado de acceso del usuario
   * @param {Object} ctx - Contexto de Telegraf
   * @returns {Promise<void>}
   */
  async handleCheckStatus(ctx) {
    if (ctx.type === 'callback_query') {
      await ctx.answerCbQuery();
    }

    const userId = ctx.from.id.toString();
    const user = ctx.from;

    // Verificar si el usuario está en la base de datos
    const userData = userManager.getUser(userId);

    if (!userData) {
      // Usuario no registrado
      return ctx.reply(
        messages.STATUS_NOT_REGISTERED(user),
        {
          parse_mode: 'MarkdownV2',
          ...keyboards.mainMenuUnauthorized()
        }
      );
    }

    // Usuario existe, verificar estado
    if (userData.status === 'active') {
      return ctx.reply(
        messages.STATUS_ACTIVE(user, userData),
        {
          parse_mode: 'MarkdownV2',
          ...keyboards.mainMenuAuthorized()
        }
      );
    } else if (userData.status === 'suspended') {
      return ctx.reply(
        messages.STATUS_SUSPENDED(user, userData),
        { parse_mode: 'MarkdownV2' }
      );
    } else {
      // Estado desconocido
      return ctx.reply(
        messages.STATUS_UNKNOWN(user),
        { parse_mode: 'MarkdownV2' }
      );
    }
  }
}

module.exports = AuthHandler;