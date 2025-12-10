/**
 * @fileoverview AuthHandler.js — Manejador de autenticación y perfil de usuario (v1.1.0)
 * @version 1.1.0
 * @author Team uSipipo
 * @description Gestiona perfil (/miinfo), solicitudes de acceso, estado de cuenta y ayuda.
 * StartHandler.js maneja ahora /start y callback 'start' (migrado v1.0.0).
 */

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
  // 👤 MI INFO (/miinfo, botón "Mi Info")
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
        ...keyboards.userInfoMenu()
      });
    } catch (err) {
      logger.error('handleUserInfo error', err);
    }
  }

  // ============================================================================
  // 📧 SOLICITAR ACCESO (botón "Solicitar Acceso")
  // ============================================================================
  async handleAccessRequest(ctx) {
    try {
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
  // 📊 ESTADO DEL USUARIO (/status, botón "Verificar Estado")
  // ============================================================================
  async handleCheckStatus(ctx) {
    try {
      if (ctx.callbackQuery) await ctx.answerCbQuery().catch(() => {});
      
      const user = ctx.from;
      const userId = user.id.toString();
      const info = userManager.getUser(userId);

      if (!info) {
        const msg = messages.STATUS_NOT_REGISTERED 
          ? messages.STATUS_NOT_REGISTERED(user) 
          : '⚠️ *No estás registrado en el sistema.*';
        
        return ctx.reply(msg, {
          parse_mode: 'Markdown',
          ...keyboards.homeUnauthorized()
        });
      }

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
  // 👥 (ADMIN) — Vista rápida de usuarios (/users)
  // ============================================================================
  async handleListUsers(ctx) {
    const userId = ctx.from.id.toString();
    if (!isAdmin(userId)) {
      return ctx.reply(messages.ADMIN_ONLY || '⛔ Acceso denegado', { parse_mode: 'Markdown' });
    }

    try {
      const users = userManager.getAllUsers();
      const stats = userManager.getUserStats();
      const msg = messages.ADMIN_USER_LIST(users, stats);

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