'use strict';

const { isAuthorized, isAdmin } = require('../middleware/auth.middleware');
const userManager = require('../services/userManager.service');
const messages = require('../utils/messages');
const keyboards = require('../utils/keyboards');

class AuthHandler {
  constructor(notificationService) {
    this.notificationService = notificationService;
  }

  // ============================================================================
  // 🎛️ START — Vista principal tipo App
  // ============================================================================
  async handleStart(ctx) {
    const userId = ctx.from.id.toString();
    const name = ctx.from.first_name || 'Usuario';

    const authorized = isAuthorized(userId);

    // messages.js ya devuelve texto formateado en Markdown V1 y escapado
    const msg = authorized
      ? messages.WELCOME_AUTHORIZED(name)
      : messages.WELCOME_UNAUTHORIZED(name);

    const keyboard = authorized
      ? keyboards.homeAuthorized()
      : keyboards.homeUnauthorized();

    return ctx.reply(msg, keyboard);
  }

  // ============================================================================
  // 👤 MI INFO
  // ============================================================================
  async handleUserInfo(ctx) {
    const user = ctx.from;
    const authorized = isAuthorized(user.id.toString());

    const msg = messages.USER_INFO(user, authorized);
    return ctx.reply(msg, keyboards.userInfoMenu(authorized));
  }

  // ============================================================================
  // 📧 SOLICITAR ACCESO (botón)
  // ============================================================================
  async handleAccessRequest(ctx) {
    // Responder al callback para detener el spinner de carga en Telegram
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    
    const user = ctx.from;

    await ctx.reply(messages.ACCESS_REQUEST_SENT(user));
    await this.notificationService.notifyAdminAccessRequest(user);
  }

  // ============================================================================
  // 📊 ESTADO DEL USUARIO
  // ============================================================================
  async handleCheckStatus(ctx) {
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    
    const user = ctx.from;
    const userId = user.id.toString();
    const info = userManager.getUser(userId);

    // 1. Usuario no existe en la DB
    if (!info) {
      // Nota: Asegúrate de que STATUS_NOT_REGISTERED exista en messages.js
      return ctx.reply(
        messages.STATUS_NOT_REGISTERED ? messages.STATUS_NOT_REGISTERED(user) : '⚠️ No estás registrado.',
        keyboards.homeUnauthorized()
      );
    }

    // 2. Verificar estado
    switch (info.status) {
      case 'active':
        return ctx.reply(
          messages.STATUS_ACTIVE ? messages.STATUS_ACTIVE(user, info) : '✅ *Cuenta Activa*',
          keyboards.homeAuthorized()
        );

      case 'suspended':
        return ctx.reply(
          messages.STATUS_SUSPENDED ? messages.STATUS_SUSPENDED(user) : '⏸️ *Cuenta Suspendida*', 
          keyboards.minimalBack()
        );

      default:
        return ctx.reply(
          messages.STATUS_UNKNOWN ? messages.STATUS_UNKNOWN(user) : '❓ Estado desconocido', 
          keyboards.minimalBack()
        );
    }
  }

  // ============================================================================
  // ❓ AYUDA
  // ============================================================================
  async handleHelp(ctx) {
    const authorized = isAuthorized(ctx.from.id.toString());
    const msg = authorized ? messages.HELP_AUTHORIZED : messages.HELP_UNAUTHORIZED;

    return ctx.reply(msg, keyboards.helpMenu(authorized));
  }

  // ============================================================================
  // 👥 (ADMIN) — Vista rápida de usuarios 
  // ============================================================================
  async handleListUsers(ctx) {
    const userId = ctx.from.id.toString();
    if (!isAdmin(userId)) {
      return ctx.reply(messages.ADMIN_ONLY);
    }

    const users = userManager.getAllUsers();
    const stats = userManager.getUserStats();
    const msg = messages.ADMIN_USER_LIST(users, stats);

    return ctx.reply(msg, keyboards.adminBackMenu());
  }
}

module.exports = AuthHandler;
