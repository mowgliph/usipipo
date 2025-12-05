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
  
  /**
  * Comprueba el estado de acceso del usuario
  */
  async handleCheckStatus(ctx) {
    if (ctx.updateType === 'callback_query') {
    await ctx.answerCbQuery();
    }
  
    const userId = ctx.from.id.toString();
    const user = ctx.from;
  
    // Verificar si el usuario está en la base de datos
    const userManager = require('../services/userManager.service');
    const userData = userManager.getUser(userId);
  
    if (!userData) {
      // Usuario no registrado
      return ctx.reply(
        messages.STATUS_NOT_REGISTERED(user),
        { 
          parse_mode: 'Markdown',
          ...keyboards.mainMenuUnauthorized()
        }
      );
    }
  
    // Usuario existe, verificar estado
    if (userData.status === 'active') {
      return ctx.reply(
        messages.STATUS_ACTIVE(user, userData),
        { 
          parse_mode: 'Markdown',
          ...keyboards.mainMenuAuthorized()
        }
      );
    } else if (userData.status === 'suspended') {
      return ctx.reply(
        messages.STATUS_SUSPENDED(user, userData),
        { parse_mode: 'Markdown' }
      );
    } else {
      // Estado desconocido
      return ctx.reply(
        messages.STATUS_UNKNOWN(user),
        { parse_mode: 'Markdown' }
      );
    }
  }
}

module.exports = AuthHandler;
