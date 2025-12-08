'use strict';

/**
 * handlers/admin.handler.js
 *
 * Refactor admin handler - estilo Premium (Moderado)
 *
 * Requisitos (ya presentes en el proyecto):
 * - services/userManager.service (userManager)
 * - services/notification.service (NotificationService) → inyectado en constructor
 * - utils/messages (mensajes HTML reutilizables)
 * - utils/logger
 *
 * Nota: Este handler no envía notificaciones de sistema por sí mismo salvo a través
 *       de notificationService para broadcast/errores/admin-notify.
 */

const userManager = require('../services/userManager.service');
const messages = require('../utils/messages');
const logger = require('../utils/logger');

class AdminHandler {
  constructor(notificationService) {
    this.notificationService = notificationService;
    // Pending broadcasts stored in memory: { id: { messageHtml, scope, fromAdminId } }
    this.pendingBroadcasts = new Map();
  }

  // ---------------------------
  // Helpers internos
  // ---------------------------
  _isAdmin(userId) {
    return userManager.isAdmin(userId);
  }

  _moderadoHeader(title) {
    // Header visual estilo "Moderado"
    return `👑 ${title}\n━━━━━━━━━━━━━━━━━━━━\n`;
  }

  _requireAdminReply(ctx) {
    const userId = ctx.from?.id;
    if (!this._isAdmin(userId)) {
      logger.warn('Admin access denied', { userId });
      ctx.reply(messages.ADMIN_ONLY);
      return false;
    }
    return true;
  }

  _parseArgsFromText(text = '') {
    // split by spaces but keep quoted groups (simple)
    const args = text.match(/(?:[^\s"]+|"[^"]*")+/g) || [];
    return args.map(a => a.replace(/^"|"$/g, ''));
  }

  // ---------------------------
  // List users (compact + premium)
  // ---------------------------
  async handleListUsers(ctx) {
    const userId = ctx.from?.id;
    if (!this._requireAdminReply(ctx)) return;

    try {
      const users = userManager.getAllUsers();
      const stats = userManager.getUserStats();

      const msg = messages.ADMIN_USER_LIST(users, stats);

      await ctx.reply(msg, { parse_mode: 'HTML' });

      logger.info('admin:list_users', { userId, total: users.length });
    } catch (err) {
      logger.error('handleListUsers error', err);
      await ctx.reply('❌ Error obteniendo la lista de usuarios.');
    }
  }

  // ---------------------------
  // Add user: /add <id> [name]
  // ---------------------------
  async handleAddUser(ctx) {
    const userId = ctx.from?.id;
    if (!this._requireAdminReply(ctx)) return;

    try {
      const text = ctx.message?.text || '';
      const parts = this._parseArgsFromText(text);
      // first element is command
      if (parts.length < 2) {
        await ctx.reply('Uso: /add <ID> [Nombre]');
        return;
      }

      const targetId = parts[1];
      const name = parts.slice(2).join(' ') || 'Sin nombre';

      const added = await userManager.addUser(targetId, String(userId), name);

      const addedAt = added.addedAt || new Date().toISOString();
      const reply = this._moderadoHeader('Usuario autorizado') +
        `🆔 ID: <code>${added.id}</code>\n` +
        `👤 Nombre: ${added.name ? this._escape(added.name) : '—'}\n` +
        `📅 Desde: ${this._escape(new Date(addedAt).toLocaleString())}`;

      await ctx.reply(reply, { parse_mode: 'HTML' });

      logger.success(userId, 'admin_add_user', { addedId: targetId, by: userId });

      // Notify the new user (if bot can contact them)
      try {
        await this.notificationService.bot.telegram.sendMessage(added.id, `✅ Has sido autorizado. Usa /start para continuar.`);
      } catch (notifyErr) {
        logger.debug('No se pudo notificar al usuario añadido', { err: notifyErr.message, targetId });
      }

    } catch (err) {
      logger.error('handleAddUser error', err);
      await ctx.reply(`❌ Error añadiendo usuario: ${err.message}`);
    }
  }

  // ---------------------------
  // Remove user: /rm <id>
  // ---------------------------
  async handleRemoveUser(ctx) {
    const userId = ctx.from?.id;
    if (!this._requireAdminReply(ctx)) return;

    try {
      const text = ctx.message?.text || '';
      const parts = this._parseArgsFromText(text);
      if (parts.length < 2) {
        await ctx.reply('Uso: /rm <ID>');
        return;
      }

      const targetId = parts[1];

      await userManager.removeUser(targetId);

      const reply = this._moderadoHeader('Usuario removido') +
        `🆔 ID: <code>${this._escape(targetId)}</code>\n` +
        `El acceso ha sido revocado.`;

      await ctx.reply(reply, { parse_mode: 'HTML' });

      logger.warn(userId, 'admin_remove_user', { removedId: targetId });

      // Notify removed user (best-effort)
      try {
        await this.notificationService.bot.telegram.sendMessage(targetId, `⚠️ Tu acceso ha sido revocado. Contacta al admin si es un error.`);
      } catch (_) {
        // silent
      }

    } catch (err) {
      logger.error('handleRemoveUser error', err);
      await ctx.reply(`❌ No se pudo remover el usuario: ${err.message}`);
    }
  }

  // ---------------------------
  // Suspend user: /sus <id>
  // ---------------------------
  async handleSuspendUser(ctx) {
    const userId = ctx.from?.id;
    if (!this._requireAdminReply(ctx)) return;

    try {
      const text = ctx.message?.text || '';
      const parts = this._parseArgsFromText(text);
      if (parts.length < 2) {
        await ctx.reply('Uso: /sus <ID>');
        return;
      }

      const targetId = parts[1];
      const suspended = await userManager.suspendUser(targetId);

      const reply = this._moderadoHeader('Usuario suspendido') +
        `🆔 ID: <code>${this._escape(targetId)}</code>\n` +
        `⏸️ Estado: suspendido\n` +
        `📅 Hora: ${this._escape(new Date(suspended.suspendedAt).toLocaleString())}`;

      await ctx.reply(reply, { parse_mode: 'HTML' });

      logger.warn(userId, 'admin_suspend_user', { targetId });

      // Notify user
      try {
        await this.notificationService.bot.telegram.sendMessage(targetId, `⏸️ Tu cuenta ha sido suspendida. Contacta al admin si crees que es un error.`);
      } catch (_) {}

    } catch (err) {
      logger.error('handleSuspendUser error', err);
      await ctx.reply(`❌ No se pudo suspender al usuario: ${err.message}`);
    }
  }

  // ---------------------------
  // Reactivate user: /react <id>
  // ---------------------------
  async handleReactivateUser(ctx) {
    const userId = ctx.from?.id;
    if (!this._requireAdminReply(ctx)) return;

    try {
      const text = ctx.message?.text || '';
      const parts = this._parseArgsFromText(text);
      if (parts.length < 2) {
        await ctx.reply('Uso: /react <ID>');
        return;
      }

      const targetId = parts[1];
      const re = await userManager.reactivateUser(targetId);

      const reply = this._moderadoHeader('Usuario reactivado') +
        `🆔 ID: <code>${this._escape(targetId)}</code>\n` +
        `▶️ Estado: activo\n` +
        `📅 Hora: ${this._escape(new Date().toISOString())}`;

      await ctx.reply(reply, { parse_mode: 'HTML' });

      logger.info(userId, 'admin_reactivate_user', { targetId });

      // Notify user
      try {
        await this.notificationService.bot.telegram.sendMessage(targetId, `✅ Tu cuenta ha sido reactivada. Puedes usar /start ahora.`);
      } catch (_) {}

    } catch (err) {
      logger.error('handleReactivateUser error', err);
      await ctx.reply(`❌ No se pudo reactivar al usuario: ${err.message}`);
    }
  }

  // ---------------------------
  // Stats: /stats
  // ---------------------------
  async handleStats(ctx) {
    const userId = ctx.from?.id;
    if (!this._requireAdminReply(ctx)) return;

    try {
      const stats = userManager.getUserStats();

      const msg = this._moderadoHeader('ESTADÍSTICAS') +
        `Total: ${stats.total}\n` +
        `Activos: ${stats.active}\n` +
        `Suspendidos: ${stats.suspended}\n` +
        `Admins: ${stats.admins}\n\n` +
        `Nuevos (24h): —`;

      await ctx.reply(msg, { parse_mode: 'HTML' });

      logger.info(userId, 'admin_stats', stats);

    } catch (err) {
      logger.error('handleStats error', err);
      await ctx.reply('❌ Error obteniendo estadísticas.');
    }
  }

  // ---------------------------
  // Broadcast: /broadcast <mensaje>
  // Preview -> confirm via inline buttons
  // ---------------------------
  async handleBroadcast(ctx) {
    const userId = ctx.from?.id;
    if (!this._requireAdminReply(ctx)) return;

    try {
      const text = (ctx.message && ctx.message.text) || '';
      const parts = text.split(' ').slice(1);
      const messageRaw = parts.join(' ').trim();
      if (!messageRaw) {
        await ctx.reply('Uso: /broadcast <mensaje>');
        return;
      }

      // build a simple id
      const broadcastId = `b_${Date.now()}`;
      const recipients = userManager.getAllUsers().filter(u => u.status === 'active');

      // save pending broadcast
      this.pendingBroadcasts.set(broadcastId, {
        messageHtml: messageRaw,
        recipients,
        from: userId
      });

      const preview = messages.BROADCAST_PREVIEW(broadcastId, messageRaw, recipients.length, 1, recipients.length + 1);

      // confirmation keyboard
      const keyboard = {
        reply_markup: {
          inline_keyboard: [
            [
              { text: '✅ Confirmar', callback_data: `broadcast_confirm_${broadcastId}` },
              { text: '❌ Cancelar', callback_data: `broadcast_cancel_${broadcastId}` }
            ]
          ]
        },
        parse_mode: 'HTML'
      };

      await ctx.reply(preview, keyboard);

      logger.info(userId, 'admin_broadcast_preview', { broadcastId, recipients: recipients.length });

    } catch (err) {
      logger.error('handleBroadcast error', err);
      await ctx.reply('❌ Error preparando broadcast.');
    }
  }

  // Confirm broadcast (action)
  async handleBroadcastConfirm(ctx, broadcastId) {
    const userId = ctx.from?.id;
    if (!this._requireAdminReply(ctx)) return;

    try {
      const pending = this.pendingBroadcasts.get(broadcastId);
      if (!pending) {
        await ctx.reply('❌ Broadcast no encontrado o ya procesado.');
        return;
      }

      const recipients = pending.recipients || [];
      const messageHtml = pending.messageHtml;

      // Build list of recipients for service: map to { id }
      const recipientsForSend = recipients.map(u => ({ id: u.id }));

      await ctx.reply('⏳ Enviando broadcast...');

      const results = await this.notificationService.sendBroadcast(messageHtml, recipientsForSend, { includeHeader: true });

      const resultMsg = messages.BROADCAST_RESULT(results.success, results.failed);
      await ctx.reply(resultMsg, { parse_mode: 'HTML' });

      this.pendingBroadcasts.delete(broadcastId);

      logger.info(userId, 'admin_broadcast_sent', { broadcastId, results });

    } catch (err) {
      logger.error('handleBroadcastConfirm error', err);
      await ctx.reply('❌ Error enviando broadcast.');
    }
  }

  // Cancel broadcast (action)
  async handleBroadcastCancel(ctx, broadcastId) {
    const userId = ctx.from?.id;
    if (!this._requireAdminReply(ctx)) return;

    try {
      const had = this.pendingBroadcasts.delete(broadcastId);
      if (had) {
        await ctx.reply('✅ Broadcast cancelado.');
        logger.info(userId, 'admin_broadcast_cancel', { broadcastId });
      } else {
        await ctx.reply('ℹ️ Broadcast no encontrado o ya procesado.');
      }
    } catch (err) {
      logger.error('handleBroadcastCancel error', err);
      await ctx.reply('❌ Error cancelando broadcast.');
    }
  }

  // ---------------------------
  // Direct message: /sms <ID> <mensaje>
  // ---------------------------
  async handleDirectMessage(ctx) {
    const userId = ctx.from?.id;
    if (!this._requireAdminReply(ctx)) return;

    try {
      const text = ctx.message?.text || '';
      const parts = this._parseArgsFromText(text);

      if (parts.length < 3) {
        await ctx.reply('Uso: /sms <ID> <mensaje>');
        return;
      }

      const targetId = parts[1];
      const message = parts.slice(2).join(' ');

      await this.notificationService.bot.telegram.sendMessage(targetId, message);

      await ctx.reply(messages.ADMIN_DIRECT_MSG_SENT(targetId, ''));
      logger.info(userId, 'admin_sms_sent', { targetId });

    } catch (err) {
      logger.error('handleDirectMessage error', err);
      await ctx.reply(`❌ Error enviando mensaje directo: ${err.message}`);
    }
  }

  // ---------------------------
  // Templates list
  // ---------------------------
  async handleTemplates(ctx) {
    const userId = ctx.from?.id;
    if (!this._requireAdminReply(ctx)) return;

    try {
      await ctx.reply(messages.ADMIN_TEMPLATES(), { parse_mode: 'HTML' });
    } catch (err) {
      logger.error('handleTemplates error', err);
      await ctx.reply('❌ Error mostrando plantillas.');
    }
  }

  // ---------------------------
  // Utility: escape simple HTML (used for plain strings)
  // ---------------------------
  _escape(text = '') {
    return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
}

module.exports = AdminHandler;