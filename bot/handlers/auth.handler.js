'use strict';

const { isAuthorized, isAdmin } = require('../middleware/auth.middleware');
const userManager = require('../services/userManager.service');
const messages = require('../utils/messages');
const keyboards = require('../utils/keyboards');
const logger = require('../utils/logger');

class AuthHandler {
  constructor(notificationService) {
    this.notificationService = notificationService;
  }

  // ============================================================================
  // 🎛️ START — Vista principal tipo App
  // ============================================================================
  async handleStart(ctx) {
    try {
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

      // FIX: Se añade parse_mode: 'Markdown' para que se vean las negritas
      // Se combina el teclado con las opciones extra
      await ctx.reply(msg, {
        parse_mode: 'Markdown',
        ...keyboard
      });

    } catch (err) {
      logger.error('handleStart error', err);
      ctx.reply('❌ Error al iniciar el menú.');
    }
  }

  // ============================================================================
  // 👤 MI INFO
  // ============================================================================
  async handleUserInfo(ctx) {
    try {
      // Si viene de un botón, cerramos el reloj de arena
      if (ctx.callbackQuery) await ctx.answerCbQuery().catch(() => {});

      const user = ctx.from;
      const authorized = isAuthorized(user.id.toString());

      const msg = messages.USER_INFO(user, authorized);
      
      await ctx.reply(msg, {
        parse_mode: 'Markdown',
        ...keyboards.userInfoMenu() // Se usa la función que añadimos en keyboards.js
      });
    } catch (err) {
      logger.error('handleUserInfo error', err);
    }
  }

  // ============================================================================
  // 📧 SOLICITAR ACCESO (botón)
  // ============================================================================
  async handleAccessRequest(ctx) {
    try {
      // FIX CRÍTICO: Verificar explícitamente si es un callbackQuery antes de responder
      if (ctx.callbackQuery) await ctx.answerCbQuery('Solicitando...').catch(() => {});
      
      const user = ctx.from;

      await ctx.reply(messages.ACCESS_REQUEST_SENT(user), { parse_mode: 'Markdown' });
      
      // Notificar al admin
      await this.notificationService.notifyAdminAccessRequest(user);
    } catch (err) {
      logger.error('handleAccessRequest error', err);
    }
  }

  // ============================================================================
  // 📊 ESTADO DEL USUARIO
  // ============================================================================
  async handleCheckStatus(ctx) {
    try {
      // FIX CRÍTICO: Evita el error "answerCbQuery isn't available for message"
      if (ctx.callbackQuery) await ctx.answerCbQuery().catch(() => {});
      
      const user = ctx.from;
      const userId = user.id.toString();
      const info = userManager.getUser(userId);

      // 1. Usuario no existe en la DB
      if (!info) {
        const msg = messages.STATUS_NOT_REGISTERED 
          ? messages.STATUS_NOT_REGISTERED(user) 
          : '⚠️ *No estás registrado en el sistema.*';
        
        return ctx.reply(msg, {
          parse_mode: 'Markdown',
          ...keyboards.homeUnauthorized()
        });
      }

      // 2. Verificar estado
      // Nota: Reemplazamos keyboards.minimalBack() por keyboards.backButton()
      // para evitar crash, ya que minimalBack no existía en el archivo anterior.
      switch (info.status) {
        case 'active':
          const msgActive = messages.STATUS_ACTIVE 
            ? messages.STATUS_ACTIVE(user, info) 
            : '✅ *Cuenta Activa*';
            
          return ctx.reply(msgActive, {
            parse_mode: 'Markdown',
            ...keyboards.homeAuthorized()
          });

        case 'suspended':
          const msgSuspended = messages.STATUS_SUSPENDED 
            ? messages.STATUS_SUSPENDED(user) 
            : '⏸️ *Cuenta Suspendida*';

          return ctx.reply(msgSuspended, {
            parse_mode: 'Markdown',
            ...keyboards.backButton()
          });

        default:
          return ctx.reply('❓ *Estado desconocido*', {
            parse_mode: 'Markdown',
            ...keyboards.backButton()
          });
      }
    } catch (err) {
      logger.error('handleCheckStatus error', err);
      ctx.reply('❌ Error verificando estado.');
    }
  }

  // ============================================================================
  // ❓ AYUDA
  // ============================================================================
  async handleHelp(ctx) {
    try {
      if (ctx.callbackQuery) await ctx.answerCbQuery().catch(() => {});

      const authorized = isAuthorized(ctx.from.id.toString());
      const msg = authorized ? messages.HELP_AUTHORIZED : messages.HELP_UNAUTHORIZED;

      // Aseguramos que msg sea string para evitar errores si messages.js falla
      const finalMsg = typeof msg === 'string' ? msg : 'ℹ️ *Sección de Ayuda*';

      return ctx.reply(finalMsg, {
        parse_mode: 'Markdown',
        ...keyboards.helpMenu()
      });
    } catch (err) {
      logger.error('handleHelp error', err);
    }
  }

  // ============================================================================
  // 👥 (ADMIN) — Vista rápida de usuarios 
  // ============================================================================
  async handleListUsers(ctx) {
    const userId = ctx.from.id.toString();
    if (!isAdmin(userId)) {
      // Enviamos sin markdown si es un mensaje simple de error, o con markdown si messages.js lo soporta
      return ctx.reply(messages.ADMIN_ONLY || '⛔ Acceso denegado', { parse_mode: 'Markdown' });
    }

    try {
      const users = userManager.getAllUsers();
      const stats = userManager.getUserStats();
      const msg = messages.ADMIN_USER_LIST(users, stats);

      // Usamos backButton() porque adminBackMenu() no existía en keyboards.js
      return ctx.reply(msg, {
        parse_mode: 'Markdown',
        ...keyboards.backButton()
      });
    } catch (err) {
      logger.error('handleListUsers error', err);
      ctx.reply('❌ Error listando usuarios.');
    }
  }
}

module.exports = AuthHandler;
