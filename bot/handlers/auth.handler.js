const { isAuthorized, isAdmin } = require('../middleware/auth.middleware');
const userManager = require('../services/userManager.service');
const messages = require('../utils/messages');
const keyboards = require('../utils/keyboards');

const escapeHtml = (text) =>
  text ? String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') : '';

class AuthHandler {
  constructor(notificationService) {
    this.notificationService = notificationService;
  }

  /**
   * /start — Menú principal según estado del usuario
   */
  async handleStart(ctx) {
    const userId = ctx.from.id.toString();
    const name = ctx.from.first_name || 'Usuario';

    const msg = isAuthorized(userId)
      ? messages.WELCOME_AUTHORIZED(name)
      : messages.WELCOME_UNAUTHORIZED(name);

    const keyboard = isAuthorized(userId)
      ? keyboards.mainMenuAuthorized()
      : keyboards.mainMenuUnauthorized();

    return ctx.reply(msg, keyboard);
  }

  /**
   * /miinfo — Muestra datos del usuario
   */
  async handleUserInfo(ctx) {
    const user = ctx.from;
    const authorized = isAuthorized(user.id.toString());
    return ctx.reply(messages.USER_INFO(user, authorized));
  }

  /**
   * Botón "Solicitar acceso"
   */
  async handleAccessRequest(ctx) {
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    const user = ctx.from;

    await ctx.reply(messages.ACCESS_REQUEST_SENT(user));
    await this.notificationService.notifyAdminAccessRequest(user);
  }

  /**
   * /users — Lista usuarios activos (admin)
   */
  async handleListUsers(ctx) {
    const userId = ctx.from.id.toString();
    if (!isAdmin(userId)) {
      return ctx.reply(messages.ADMIN_ONLY);
    }

    const active = userManager.getAllUsers().filter(u => u.status === 'active');

    if (active.length === 0) {
      return ctx.reply('👥 <b>USUARIOS AUTORIZADOS</b>\n\n<i>No hay usuarios activos.</i>');
    }

    const list = active
      .map((u, i) => {
        const role = u.role === 'admin' ? '👑' : '';
        const name = escapeHtml(u.name || 'Sin nombre');
        return `${i + 1}. ID: <code>${u.id}</code> ${role} - ${name}`;
      })
      .join('\n');

    const msg =
      `👥 <b>USUARIOS AUTORIZADOS</b>\n\n` +
      list +
      `\n\n📝 <b>Total:</b> ${active.length}`;

    return ctx.reply(msg);
  }

  /**
   * /status — Verifica estado de acceso del usuario
   */
  async handleCheckStatus(ctx) {
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    const user = ctx.from;
    const userId = user.id.toString();
    const info = userManager.getUser(userId);

    // No registrado en DB
    if (!info) {
      return ctx.reply(
        messages.STATUS_NOT_REGISTERED(user),
        keyboards.mainMenuUnauthorized()
      );
    }

    // Registrado → verificar estado
    switch (info.status) {
      case 'active':
        return ctx.reply(
          messages.STATUS_ACTIVE(user, info),
          keyboards.mainMenuAuthorized()
        );
      case 'suspended':
        return ctx.reply(messages.STATUS_SUSPENDED(user, info));
      default:
        return ctx.reply(messages.STATUS_UNKNOWN(user));
    }
  }

  /**
   * /help — Ayuda según estado del usuario
   */
  async handleHelp(ctx) {
    const authorized = isAuthorized(ctx.from.id.toString());
    return ctx.reply(
      authorized ? messages.HELP_AUTHORIZED : messages.HELP_UNAUTHORIZED
    );
  }
}

module.exports = AuthHandler;