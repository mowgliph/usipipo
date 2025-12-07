// handlers/auth.handler.js
const { isAuthorized, isAdmin } = require('../middleware/auth.middleware');
const userManager = require('../services/userManager.service');
const messages = require('../utils/messages');
const keyboards = require('../utils/keyboards');

// Nota: No necesitamos importar markdown helpers aquí porque messages.js ya devuelve HTML listo
// Si handleListUsers necesita escapar datos manuales, usaremos una función helper simple local.

const escapeHtml = (text) => {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
};

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
        keyboards.mainMenuAuthorized() // parse_mode es HTML por default global
      );
    }

    return ctx.reply(
      messages.WELCOME_UNAUTHORIZED(userName),
      keyboards.mainMenuUnauthorized()
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

    // messages.USER_INFO ya devuelve HTML válido
    return ctx.reply(messages.USER_INFO(user, authorized));
  }

  /**
   * Procesa solicitud de acceso
   * @param {Object} ctx - Contexto de Telegraf
   * @returns {Promise<void>}
   */
  async handleAccessRequest(ctx) {
    await ctx.answerCbQuery().catch(() => {}); // Evitar errores si no es callback
    const user = ctx.from;

    // Mensaje para el usuario
    await ctx.reply(messages.ACCESS_REQUEST_SENT(user));

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
      return ctx.reply(messages.ADMIN_ONLY);
    }

    const activeUsers = userManager.getAllUsers().filter(u => u.status === 'active');
    
    // Construcción del mensaje en HTML
    let formattedMessage = `👥 <b>USUARIOS AUTORIZADOS</b>\n\n`;

    if (activeUsers.length === 0) {
        formattedMessage += '<i>No hay usuarios activos.</i>';
    } else {
        const listaUsuarios = activeUsers.map((user, index) => {
            const roleTag = user.role === 'admin' ? '👑 (Admin)' : '';
            const safeName = escapeHtml(user.name || 'Sin nombre');
            // Formato: 1. ID: 123456 - Nombre 👑
            return `${index + 1}. ID: <code>${user.id}</code> ${roleTag} - ${safeName}`;
        }).join('\n');
        
        formattedMessage += listaUsuarios;
        formattedMessage += `\n\n📝 <b>Total:</b> ${activeUsers.length} usuarios`;
    }

    return ctx.reply(formattedMessage);
  }

  /**
   * Comprueba el estado de acceso del usuario
   * @param {Object} ctx - Contexto de Telegraf
   * @returns {Promise<void>}
   */
  async handleCheckStatus(ctx) {
    if (ctx.callbackQuery) {
      await ctx.answerCbQuery().catch(() => {});
    }

    const userId = ctx.from.id.toString();
    const user = ctx.from;

    // Verificar si el usuario está en la base de datos
    const userData = userManager.getUser(userId);

    if (!userData) {
      // Usuario no registrado
      return ctx.reply(
        messages.STATUS_NOT_REGISTERED(user),
        keyboards.mainMenuUnauthorized()
      );
    }

    // Usuario existe, verificar estado
    if (userData.status === 'active') {
      return ctx.reply(
        messages.STATUS_ACTIVE(user, userData),
        keyboards.mainMenuAuthorized()
      );
    } else if (userData.status === 'suspended') {
      return ctx.reply(messages.STATUS_SUSPENDED(user, userData));
    } else {
      // Estado desconocido
      return ctx.reply(messages.STATUS_UNKNOWN(user));
    }
  }

  // Agregado handleHelp que faltaba según bot.instance.js
  async handleHelp(ctx) {
      const userId = ctx.from.id.toString();
      if (isAuthorized(userId)) {
          return ctx.reply(messages.HELP_AUTHORIZED);
      }
      return ctx.reply(messages.HELP_UNAUTHORIZED);
  }
}

module.exports = AuthHandler;
