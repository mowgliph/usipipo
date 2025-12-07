const { Markup } = require('telegraf');
const userManager = require('../services/userManager.service');
const logger = require('../utils/logger');
const messages = require('../utils/messages');

class AdminHandler {
  constructor(notificationService) {
    this.notificationService = notificationService;
    this.pendingBroadcasts = new Map();
  }

  // /add [ID] [nombre]
  async handleAddUser(ctx) {
    try {
      const { adminId, args } = this.#parseCommand(ctx);
      logger.info(adminId, 'handleAddUser', { args });

      if (args.length === 0) {
        return ctx.reply('⚠️ Uso: /add [ID] [nombre_opcional]');
      }

      const userId = args[0];
      if (!/^\d+$/.test(userId)) {
        return ctx.reply('⚠️ El ID debe ser numérico');
      }

      const userName = args.slice(1).join(' ') || null;
      const newUser = await userManager.addUser(userId, adminId, userName);

      await ctx.reply(messages.ADMIN_USER_ADDED(userId, newUser.name, new Date(newUser.addedAt).toLocaleString('es-ES')));

      // Notify user (via notificationService)
      await this.notificationService.bot.telegram.sendMessage(
        userId,
        messages.NOTIFY_USER_APPROVED(newUser.name)
      );

      logger.success(adminId, 'add_user', userId);
    } catch (err) {
      this.#handleError(ctx, err, 'handleAddUser');
    }
  }

  // /rm [ID]
  async handleRemoveUser(ctx) {
    try {
      const { adminId, args } = this.#parseCommand(ctx);
      logger.info(adminId, 'handleRemoveUser', { args });

      const userId = args[0];
      if (!userId) return ctx.reply('⚠️ Uso: /rm [ID]');

      await userManager.removeUser(userId);
      await ctx.reply(messages.ADMIN_USER_REMOVED(userId));

      // notify user
      await this.notificationService.bot.telegram.sendMessage(userId, messages.NOTIFY_USER_REMOVED());
      logger.success(adminId, 'remove_user', userId);
    } catch (err) {
      this.#handleError(ctx, err, 'handleRemoveUser');
    }
  }

  // /sus [ID]
  async handleSuspendUser(ctx) {
    try {
      const { adminId, args } = this.#parseCommand(ctx);
      logger.info(adminId, 'handleSuspendUser', { args });

      if (!args[0]) return ctx.reply('⚠️ Uso: /sus [ID]');

      const user = await userManager.suspendUser(args[0]);
      await ctx.reply(messages.ADMIN_USER_SUSPENDED(user.id));

      logger.success(adminId, 'suspend_user', user.id);
    } catch (err) {
      this.#handleError(ctx, err, 'handleSuspendUser');
    }
  }

  // /react [ID]
  async handleReactivateUser(ctx) {
    try {
      const { adminId, args } = this.#parseCommand(ctx);
      logger.info(adminId, 'handleReactivateUser', { args });

      if (!args[0]) return ctx.reply('⚠️ Uso: /react [ID]');

      const user = await userManager.reactivateUser(args[0]);
      await ctx.reply(messages.ADMIN_USER_REACTIVATED(user.id));

      // notify user
      await this.notificationService.bot.telegram.sendMessage(user.id, messages.NOTIFY_USER_REACTIVATED());
      logger.success(adminId, 'reactivate_user', user.id);
    } catch (err) {
      this.#handleError(ctx, err, 'handleReactivateUser');
    }
  }

  // /users
  async handleListUsers(ctx) {
    try {
      const adminId = ctx.from.id;
      logger.info(adminId, 'handleListUsers');

      const users = userManager.getAllUsers();
      const stats = userManager.getUserStats();

      return ctx.reply(messages.ADMIN_USER_LIST(users, stats));
    } catch (err) {
      this.#handleError(ctx, err, 'handleListUsers');
    }
  }

  // /stats
  async handleStats(ctx) {
    try {
      const adminId = ctx.from.id;
      logger.info(adminId, 'handleStats');

      const stats = userManager.getUserStats();
      const users = userManager.getAllUsers();
      const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
      const recentUsers = users.filter(u => new Date(u.addedAt).getTime() > oneDayAgo).length;

      return ctx.reply(messages.ADMIN_STATS(stats, recentUsers));
    } catch (err) {
      this.#handleError(ctx, err, 'handleStats');
    }
  }

  // /broadcast [mensaje]
  async handleBroadcast(ctx) {
    try {
      const adminId = ctx.from.id.toString();
      logger.info(adminId, 'handleBroadcast');

      const messageText = (ctx.message?.text || '').replace(/^\/broadcasts?\s*/i, '').trim();
      if (!messageText) return ctx.reply(messages.BROADCAST_HELP);

      const users = userManager.getAllUsers();
      const activeUsers = users.filter(u => u.status === 'active');
      const userCount = activeUsers.filter(u => u.role === 'user').length;
      const adminCount = activeUsers.filter(u => u.role === 'admin').length;

      const safeMessage = messages._helpers.escapeHtml(messageText);
      const broadcastId = Date.now().toString();

      this.pendingBroadcasts.set(broadcastId, {
        adminId,
        message: safeMessage,
        createdAt: Date.now(),
        targets: { userCount, adminCount, total: activeUsers.length }
      });

      this.#cleanOldBroadcasts();

      await ctx.reply(messages.BROADCAST_PREVIEW(broadcastId, safeMessage, userCount, adminCount, activeUsers.length),
        this.#getBroadcastKeyboard(broadcastId)
      );
    } catch (err) {
      this.#handleError(ctx, err, 'handleBroadcast');
    }
  }

  // Confirm broadcast (callbacks)
  async handleBroadcastConfirm(ctx, broadcastId, target) {
    try {
      if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
      const adminId = ctx.from.id.toString();
      logger.info(adminId, 'handleBroadcastConfirm', { broadcastId, target });

      await this.#processBroadcastConfirm(ctx, broadcastId, target);
    } catch (err) {
      this.#handleError(ctx, err, 'handleBroadcastConfirm');
    }
  }

  // Cancel broadcast
  async handleBroadcastCancel(ctx, broadcastId) {
    try {
      if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
      const adminId = ctx.from.id.toString();
      logger.info(adminId, 'handleBroadcastCancel', { broadcastId });

      this.pendingBroadcasts.delete(broadcastId);

      await ctx.editMessageText('❌ Broadcast cancelado.');
    } catch (err) {
      logger.error('handleBroadcastCancel', err);
    }
  }

  // /sms [ID] [mensaje]
  async handleDirectMessage(ctx) {
    try {
      const { adminId, args } = this.#parseCommand(ctx);
      logger.info(adminId, 'handleDirectMessage', { args });

      if (args.length < 2) return ctx.reply('⚠️ Uso: /sms [ID] [mensaje]');

      const [targetId, ...rest] = args;
      const messageText = rest.join(' ');
      const target = userManager.getUser(targetId);

      if (!target) return ctx.reply(`❌ Usuario ${messages._helpers.code(targetId)} no encontrado`);

      // send via notification service (sanitized inside)
      await this.notificationService.bot.telegram.sendMessage(targetId,
        `💬 ${messages._helpers.bold('Mensaje del Administrador')}\n\n${messages._helpers.escapeHtml(messageText)}`
      );

      await ctx.reply(messages.ADMIN_DIRECT_MSG_SENT(targetId, target.name));
      logger.success(adminId, 'direct_message', targetId);
    } catch (err) {
      this.#handleError(ctx, err, 'handleDirectMessage');
    }
  }

  // /templates
  async handleTemplates(ctx) {
    try {
      const adminId = ctx.from.id;
      logger.info(adminId, 'handleTemplates');
      await ctx.reply(messages.ADMIN_TEMPLATES());
    } catch (err) {
      this.#handleError(ctx, err, 'handleTemplates');
    }
  }

  // ========== PRIVATES ==========

  #parseCommand(ctx) {
    const adminId = ctx.from?.id || 'system';
    const text = ctx.message?.text || '';
    const args = text.split(' ').slice(1).filter(Boolean);
    return { adminId, args };
  }

  #getBroadcastKeyboard(bId) {
    return Markup.inlineKeyboard([
      [Markup.button.callback('✅ Enviar a TODOS', `broadcast_all_${bId}`)],
      [
        Markup.button.callback('👤 Solo Usuarios', `broadcast_users_${bId}`),
        Markup.button.callback('👑 Solo Admins', `broadcast_admins_${bId}`)
      ],
      [Markup.button.callback('❌ Cancelar', `broadcast_cancel_${bId}`)]
    ]);
  }

  async #processBroadcastConfirm(ctx, broadcastId, target) {
    const b = this.pendingBroadcasts.get(broadcastId);
    if (!b) return ctx.reply('❌ Broadcast expirado o inválido.');

    this.pendingBroadcasts.delete(broadcastId);

    const users = userManager.getAllUsers();
    const recipients = this.#filterRecipients(users, target);
    if (recipients.length === 0) return ctx.reply('❌ No hay destinatarios.');

    await ctx.editMessageText('📤 Enviando broadcast...');

    const results = await this.notificationService.sendBroadcast(b.message, recipients);

    await ctx.editMessageText(messages.BROADCAST_RESULT(results.success, results.failed));
  }

  #filterRecipients(users, target) {
    switch (target) {
      case 'all': return users.filter(u => u.status === 'active');
      case 'users': return users.filter(u => u.status === 'active' && u.role === 'user');
      case 'admins': return users.filter(u => u.status === 'active' && u.role === 'admin');
      default: return [];
    }
  }

  #cleanOldBroadcasts() {
    const cutoff = Date.now() - 5 * 60 * 1000;
    for (const [id, b] of this.pendingBroadcasts.entries()) {
      if (b.createdAt < cutoff) this.pendingBroadcasts.delete(id);
    }
  }

  #handleError(ctx, err, method) {
    const adminId = ctx.from?.id || 'unknown';
    const msg = err?.message || 'Error interno';
    logger.error(method, err, { adminId, msg });
    ctx.reply(`❌ Error: ${messages._helpers.escapeHtml(msg)}`);
  }
}

module.exports = AdminHandler;