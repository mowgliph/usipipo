// handlers/auth.handler.js
const { isAuthorized, isAdmin } = require('../middleware/auth.middleware');
const messages = require('../utils/messages');
const keyboards = require('../utils/keyboards');
const config = require('../config/environment');

class AuthHandler {
  constructor(notificationService) {
    this.notificationService = notificationService;
  }

  /**
   * Manejador del comando /start
   */
  async handleStart(ctx) {
    const userId = ctx.from.id.toString();
    const userName = ctx.from.first_name || 'Usuario';
    
    if (isAuthorized(userId)) {
      return ctx.reply(
        messages.WELCOME_AUTHORIZED(userName),
        {
          parse_mode: 'Markdown',
          ...keyboards.mainMenuAuthorized()
        }
      );
    } else {
      return ctx.reply(
        messages.WELCOME_UNAUTHORIZED(userName),
        {
          parse_mode: 'Markdown',
          ...keyboards.mainMenuUnauthorized()
        }
      );
    }
  }

  /**
   * Muestra información del usuario
   */
  async handleUserInfo(ctx) {
    const user = ctx.from;
    const userId = user.id.toString();
    const authorized = isAuthorized(userId);
    
    return ctx.reply(
      messages.USER_INFO(user, authorized),
      { parse_mode: 'Markdown' }
    );
  }

  /**
   * Procesa solicitud de acceso
   */
  async handleAccessRequest(ctx) {
    await ctx.answerCbQuery();
    const user = ctx.from;
    
    // Mensaje para el usuario
    await ctx.reply(
      messages.ACCESS_REQUEST_SENT(user),
      { parse_mode: 'Markdown' }
    );
    
    // Notificar al administrador
    await this.notificationService.notifyAdminAccessRequest(user);
  }

  /**
   * Lista usuarios autorizados (solo admin)
   */
  async handleListUsers(ctx) {
    const userId = ctx.from.id.toString();
    
    if (!isAdmin(userId)) {
      return ctx.reply(messages.ADMIN_ONLY);
    }
    
    const listaUsuarios = config.AUTHORIZED_USERS.map((id, index) => 
      `${index + 1}. ID: \`${id}\`${id === config.ADMIN_ID ? ' 👑 (Admin)' : ''}`
    ).join('\n');
    
    return ctx.reply(
      `👥 **USUARIOS AUTORIZADOS**\n\n${listaUsuarios}\n\n` +
      `📝 Total: ${config.AUTHORIZED_USERS.length} usuarios`,
      { parse_mode: 'Markdown' }
    );
  }
}

module.exports = AuthHandler;
