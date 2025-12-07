// handlers/admin.handler.js
const { Markup } = require('telegraf'); // Movido al top level para mejor performance
const userManager = require('../services/userManager.service');
const logger = require('../utils/logger');

// =====================================================
// UTILIDADES HTML INTERNAS
// =====================================================

const escapeHtml = (text) => {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
};

const bold = (text) => `<b>${text}</b>`;
const code = (text) => `<code>${text}</code>`;

// =====================================================
// CLASE ADMIN HANDLER
// =====================================================

class AdminHandler {
  constructor(notificationService) {
    this.notificationService = notificationService;
    this.pendingBroadcasts = new Map();
  }

  /**
   * Comando: /add [ID] [nombre_opcional] - Autorizar usuario
   */
  async handleAddUser(ctx) {
    try {
      const { adminId, args } = this.#parseCommand(ctx);
      logger.info(adminId, 'handleAddUser', { args });

      const result = await this.#processAddUser(args);
      // parse_mode global es HTML, no necesitamos especificarlo
      await ctx.reply(result.message);

      await this.#notifyUserApproved(result.userId, result.userName);
      logger.success(adminId, 'Usuario agregado', result.userId);

    } catch (error) {
      this.#handleError(ctx, error, 'handleAddUser');
    }
  }

  /**
   * Comando: /rm [ID] - Remover usuario
   */
  async handleRemoveUser(ctx) {
    try {
      const { adminId, args } = this.#parseCommand(ctx);
      logger.info(adminId, 'handleRemoveUser', { args });

      const userId = args[0];
      await userManager.removeUser(userId);

      await ctx.reply(
        this.#formatSuccessMessage(
          '🗑️ Usuario removido',
          `🆔 ID: ${code(userId)}`,
          'El usuario ya no tiene acceso al bot'
        )
      );

      await this.#notifyUserRemoved(userId);
      logger.success(adminId, 'Usuario removido', userId);

    } catch (error) {
      this.#handleError(ctx, error, 'handleRemoveUser');
    }
  }

  /**
   * Comando: /sus [ID] - Suspender usuario
   */
  async handleSuspendUser(ctx) {
    try {
      const { adminId, args } = this.#parseCommand(ctx);
      logger.info(adminId, 'handleSuspendUser', { args });

      if (args.length === 0) {
        return ctx.reply(this.#formatUsageError('sus', '/sus [ID]'));
      }

      const user = await userManager.suspendUser(args[0]);
      await ctx.reply(
        this.#formatSuccessMessage(
          `⏸️ Usuario suspendido`,
          `🆔 ID: ${code(user.id)}`,
          `Para reactivar usa: ${code(`/react ${user.id}`)}`
        )
      );

      logger.success(adminId, 'Usuario suspendido', user.id);

    } catch (error) {
      this.#handleError(ctx, error, 'handleSuspendUser');
    }
  }

  /**
   * Comando: /react [ID] - Reactivar usuario
   */
  async handleReactivateUser(ctx) {
    try {
      const { adminId, args } = this.#parseCommand(ctx);
      logger.info(adminId, 'handleReactivateUser', { args });

      if (args.length === 0) {
        return ctx.reply(this.#formatUsageError('react', '/react [ID]'));
      }

      const user = await userManager.reactivateUser(args[0]);
      await ctx.reply(
        this.#formatSuccessMessage(
          '▶️ Usuario reactivado',
          `🆔 ID: ${code(user.id)}`,
          'El usuario puede usar el bot nuevamente'
        )
      );

      await this.#notifyUserReactivated(user.id);
      logger.success(adminId, 'Usuario reactivado', user.id);

    } catch (error) {
      this.#handleError(ctx, error, 'handleReactivateUser');
    }
  }

  /**
   * Comando: /users - Lista todos los usuarios
   */
  async handleListUsers(ctx) {
    try {
      const adminId = ctx.from.id;
      logger.info(adminId, 'handleListUsers');

      const users = userManager.getAllUsers();
      const stats = userManager.getUserStats();

      if (users.length === 0) {
        return ctx.reply('📭 No hay usuarios registrados');
      }

      const message = this.#formatUserList(users, stats);
      await ctx.reply(message);

      logger.success(adminId, 'Lista de usuarios enviada', { total: users.length });

    } catch (error) {
      this.#handleError(ctx, error, 'handleListUsers');
    }
  }

  /**
   * Comando: /stats - Estadísticas del sistema
   */
  async handleStats(ctx) {
    try {
      const adminId = ctx.from.id;
      logger.info(adminId, 'handleStats');

      const stats = userManager.getUserStats();
      const users = userManager.getAllUsers();
      const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
      const recentUsers = users.filter(u => new Date(u.addedAt) > oneDayAgo);

      const message = this.#formatStatsMessage(stats, recentUsers.length);
      await ctx.reply(message);

      logger.success(adminId, 'Estadísticas enviadas');

    } catch (error) {
      this.#handleError(ctx, error, 'handleStats');
    }
  }

  /**
   * Comando: /broadcast [mensaje] - Broadcast con confirmación
   */
  async handleBroadcast(ctx) {
    try {
      const adminId = ctx.from.id.toString();
      logger.info(adminId, 'handleBroadcast');

      const messageText = ctx.message.text.replace(/^\/broadcasts?\s*/, '').trim();
      
      if (!messageText) {
        return ctx.reply(this.#formatBroadcastHelp());
      }

      await this.#processBroadcast(ctx, adminId, messageText);

    } catch (error) {
      this.#handleError(ctx, error, 'handleBroadcast');
    }
  }

  /**
   * Confirma y envía broadcast
   */
  async handleBroadcastConfirm(ctx, broadcastId, target) {
    try {
      await ctx.answerCbQuery();
      const adminId = ctx.from.id.toString();

      logger.info(adminId, 'handleBroadcastConfirm', { broadcastId, target });
      await this.#processBroadcastConfirm(ctx, broadcastId, target);
      
    } catch (error) {
      this.#handleError(ctx, error, 'handleBroadcastConfirm');
      await ctx.answerCbQuery('Error procesando broadcast').catch(() => {});
    }
  }

  /**
   * Cancela broadcast pendiente
   */
  async handleBroadcastCancel(ctx, broadcastId) {
    try {
      await ctx.answerCbQuery('Broadcast cancelado');
      const adminId = ctx.from.id.toString();

      logger.info(adminId, 'handleBroadcastCancel', { broadcastId });
      this.pendingBroadcasts.delete(broadcastId);

      await ctx.editMessageText(
        `❌ Broadcast cancelado.

Usa /broadcast para crear uno nuevo.`
      );

    } catch (error) {
      logger.error('handleBroadcastCancel', error, { broadcastId });
    }
  }

  /**
   * Comando: /sms [ID] [mensaje] - Mensaje directo
   */
  async handleDirectMessage(ctx) {
    try {
      const { adminId, args } = this.#parseCommand(ctx);
      logger.info(adminId, 'handleDirectMessage', { args });

      if (args.length < 2) {
        return ctx.reply(this.#formatDirectMessageHelp());
      }

      const [targetUserId, ...messageParts] = args;
      const messageText = messageParts.join(' ');

      const targetUser = userManager.getUser(targetUserId);
      if (!targetUser) {
        return ctx.reply(
          `❌ Usuario ${code(targetUserId)} no encontrado en la base de datos.`
        );
      }

      await this.#sendDirectMessage(targetUserId, messageText);
      
      const userName = targetUser.name ? escapeHtml(targetUser.name) : 'Sin nombre';
      await ctx.reply(
        this.#formatSuccessMessage(
          '✅ Mensaje enviado',
          `👤 Destinatario: ${userName}`,
          `🆔 ID: ${code(targetUserId)}`
        )
      );

      logger.success(adminId, 'Mensaje directo enviado', targetUserId);

    } catch (error) {
      this.#handleError(ctx, error, 'handleDirectMessage');
    }
  }

  /**
   * Comando: /templates - Plantillas de mensajes
   */
  async handleTemplates(ctx) {
    try {
      const adminId = ctx.from.id;
      logger.info(adminId, 'handleTemplates');

      await ctx.reply(this.#formatTemplatesMessage());

    } catch (error) {
      this.#handleError(ctx, error, 'handleTemplates');
    }
  }

  // ========== MÉTODOS PRIVADOS ==========

  #parseCommand(ctx) {
    const adminId = ctx.from.id;
    const args = ctx.message.text.split(' ').slice(1);
    return { adminId, args };
  }

  async #processAddUser(args) {
    if (args.length === 0) {
      throw new Error('Formato: /add [ID] [nombre_opcional]');
    }

    const userId = args[0];
    if (!/^\d+$/.test(userId)) {
      throw new Error('El ID debe ser numérico');
    }

    const userName = args.slice(1).join(' ') || null;
    const newUser = await userManager.addUser(userId, this.#getAdminId(), userName);

    return {
      message: this.#formatSuccessMessage(
        '✅ Usuario agregado exitosamente',
        `🆔 ID: ${code(userId)}`,
        `👤 Nombre: ${newUser.name ? escapeHtml(newUser.name) : 'No especificado'}`,
        `📅 Agregado: ${new Date(newUser.addedAt).toLocaleString('es-ES')}`
      ),
      userId,
      userName: newUser.name
    };
  }

  #formatSuccessMessage(title, ...lines) {
    let message = `${title}

`;
    message += lines.map(line => `• ${line}`).join('\n');
    return message;
  }

  #formatUsageError(command, format) {
    return `⚠️ ${bold('Uso incorrecto')}

` +
           `📝 Formato: ${code(format)}

` +
           `💡 Obtén el ID con ${code('/miinfo')}`;
  }

  #formatUserList(users, stats) {
    let message = `👥 ${bold('USUARIOS AUTORIZADOS')}

`;
    message += `📊 ${bold('Estadísticas:')}
`;
    message += `• Total: ${stats.total}
• Activos: ${stats.active}
`;
    message += `• Suspendidos: ${stats.suspended}
• Admins: ${stats.admins}

`;
    message += `━━━━━━━━━━━━━━━━━━━━

`;

    users.forEach((user, index) => {
      const statusIcon = user.status === 'active' ? '✅' : '⏸️';
      const roleIcon = user.role === 'admin' ? '👑' : '👤';
      const safeName = user.name ? escapeHtml(user.name) : '';

      message += `${index + 1}. ${statusIcon} ${roleIcon} ${code(user.id)}
`;
      if (safeName) message += `   📝 ${safeName}
`;
      message += `   📅 ${new Date(user.addedAt).toLocaleDateString('es-ES')}

`;
    });

    return message;
  }

  #formatStatsMessage(stats, recentUsers) {
    return `📊 ${bold('ESTADÍSTICAS DEL SISTEMA')}

` +
           `👥 ${bold('Usuarios:')}
` +
           `• Total: ${stats.total}
• Activos: ${stats.active}
` +
           `• Suspendidos: ${stats.suspended}
• Administradores: ${stats.admins}
` +
           `• Usuarios regulares: ${stats.users}

` +
           `📈 ${bold('Actividad:')}
• Nuevos (24h): ${recentUsers}

` +
           `🕐 Actualizado: ${new Date().toLocaleString('es-ES')}`;
  }

  #formatBroadcastHelp() {
    return `📢 ${bold('Comando Broadcast')}

` +
           `${bold('Uso:')} ${code('/broadcast [mensaje]')}

` +
           `${bold('Ejemplos:')}
• ${code('/broadcast ¡Nuevo servidor disponible!')}
` +
           `• ${code('/broadcast 🎉 Promoción: 50% descuento este mes')}

` +
           `💡 El mensaje se enviará a todos los usuarios activos.`;
  }

  async #processBroadcast(ctx, adminId, messageText) {
    const users = userManager.getAllUsers();
    const activeUsers = users.filter(u => u.status === 'active');
    const userCount = activeUsers.filter(u => u.role === 'user').length;
    const adminCount = activeUsers.filter(u => u.role === 'admin').length;

    // Escapamos el mensaje para que sea HTML seguro al previsualizar y enviar
    const safeMessage = escapeHtml(messageText);

    const broadcastId = Date.now().toString();
    this.pendingBroadcasts.set(broadcastId, {
      message: safeMessage, // Guardamos la versión segura
      adminId,
      createdAt: new Date(),
      targetCount: activeUsers.length
    });

    this.#cleanOldBroadcasts();

    await ctx.reply(
      `📢 ${bold('CONFIRMAR BROADCAST')}

` +
      `${bold('Mensaje:')}
━━━━━━━━━━━━━━━━━━━━
${safeMessage}
━━━━━━━━━━━━━━━━━━━━

` +
      `${bold('Destinatarios:')}
• 👤 Usuarios: ${userCount}
• 👑 Admins: ${adminCount}
` +
      `• 📊 Total: ${activeUsers.length}

⚠️ ${bold('¿Confirmas el envío?')}`,
      this.#getBroadcastKeyboard(broadcastId)
    );
  }

  #getBroadcastKeyboard(broadcastId) {
    return Markup.inlineKeyboard([
      [Markup.button.callback('✅ Enviar a TODOS', `broadcast_all_${broadcastId}`)],
      [
        Markup.button.callback('👤 Solo Usuarios', `broadcast_users_${broadcastId}`),
        Markup.button.callback('👑 Solo Admins', `broadcast_admins_${broadcastId}`)
      ],
      [Markup.button.callback('❌ Cancelar', `broadcast_cancel_${broadcastId}`)]
    ]);
  }

  async #processBroadcastConfirm(ctx, broadcastId, target) {
    const broadcast = this.pendingBroadcasts.get(broadcastId);
    if (!broadcast) {
      throw new Error('Solicitud de broadcast expirada');
    }

    this.pendingBroadcasts.delete(broadcastId);

    const users = userManager.getAllUsers();
    const recipients = this.#getBroadcastRecipients(users, target);
    
    if (recipients.length === 0) {
      throw new Error('No hay destinatarios disponibles');
    }

    await ctx.editMessageText(
      `📤 ${bold('Enviando broadcast...')}

⏳ Enviando a ${recipients.length} usuarios...`
    );

    // NotificationService enviará usando HTML global, así que pasamos el mensaje ya saneado
    const results = await this.notificationService.sendBroadcast(
      broadcast.message,
      recipients
    );

    const successRate = recipients.length > 0 
        ? ((results.success / recipients.length) * 100).toFixed(1) 
        : '0.0';

    await ctx.editMessageText(
      `📢 ${bold('BROADCAST COMPLETADO')}

` +
      `${bold('Estadísticas:')}
• ✅ Enviados: ${results.success}
` +
      `• ❌ Fallidos: ${results.failed}
• 📊 Éxito: ${successRate}%

` +
      `${bold('Hora:')} ${new Date().toLocaleString('es-ES')}` +
      (results.failed > 0 ? '\n\n⚠️ Algunos usuarios bloquearon el bot.' : '')
    );
  }

  #getBroadcastRecipients(users, target) {
    switch (target) {
      case 'all': return users.filter(u => u.status === 'active');
      case 'users': return users.filter(u => u.status === 'active' && u.role === 'user');
      case 'admins': return users.filter(u => u.status === 'active' && u.role === 'admin');
      default: return [];
    }
  }

  #formatDirectMessageHelp() {
    return `💬 ${bold('Mensaje Directo')}

` +
           `${bold('Uso:')} ${code('/sms [ID] [mensaje]')}

` +
           `${bold('Ejemplo:')} ${code('/sms 123456789 Hola, tu acceso ha sido renovado')}`;
  }

  #formatTemplatesMessage() {
    return `📋 ${bold('PLANTILLAS DE MENSAJES')}

` +
           `${bold('1. Bienvenida:')}
${code('/broadcast 🎉 ¡Bienvenidos nuevos usuarios!')}

` +
           `${bold('2. Mantenimiento:')}
${code('/broadcast ⚠️ Mantenimiento [FECHA] [HORA]-[HORA]')}

` +
           `${bold('3. Promoción:')}
${code('/broadcast 🎁 PROMOCIÓN: [BENEFICIO] hasta [FECHA]')}

` +
           `💡 Copia y personaliza.`;
  }

  async #sendDirectMessage(userId, messageText) {
    // Sanitizamos el mensaje directo también
    const safeText = escapeHtml(messageText);

    const formattedMessage = `💬 ${bold('Mensaje del Administrador')}
━━━━━━━━━━━━━━━━━━━━

${safeText}

━━━━━━━━━━━━━━━━━━━━
📅 ${new Date().toLocaleString('es-ES')}`;

    await this.notificationService.bot.telegram.sendMessage(userId, formattedMessage);
  }

  async #notifyUserApproved(userId, userName) {
    try {
      const message = `🎉 ${bold('¡Solicitud Aprobada!')}

` +
                     `✅ Tu acceso a ${bold('uSipipo VPN Bot')} ha sido autorizado.

` +
                     `Ahora puedes usar /start para el menú principal.

` +
                     `¡Bienvenido${userName ? ` ${escapeHtml(userName)}` : ''}! 🚀`;

      await this.notificationService.bot.telegram.sendMessage(userId, message);
    } catch (error) {
      logger.error(`notifyUserApproved ${userId}`, error);
    }
  }

  async #notifyUserRemoved(userId) {
    try {
      const message = `⚠️ ${bold('Acceso Revocado')}

` +
                     `Tu autorización para ${bold('uSipipo VPN Bot')} ha sido removida.

` +
                     `Contacta al administrador si crees que es un error.`;

      await this.notificationService.bot.telegram.sendMessage(userId, message);
    } catch (error) {
      logger.error(`notifyUserRemoved ${userId}`, error);
    }
  }

  async #notifyUserReactivated(userId) {
    try {
      const message = `✅ ${bold('Acceso Reactivado')}

` +
                     `Tu acceso a ${bold('uSipipo VPN Bot')} ha sido restaurado.

` +
                     `Usa /start para continuar.`;

      await this.notificationService.bot.telegram.sendMessage(userId, message);
    } catch (error) {
      logger.error(`notifyUserReactivated ${userId}`, error);
    }
  }

  #cleanOldBroadcasts() {
    const fiveMinutesAgo = Date.now() - (5 * 60 * 1000);
    for (const [id, broadcast] of this.pendingBroadcasts.entries()) {
      if (new Date(broadcast.createdAt).getTime() < fiveMinutesAgo) {
        this.pendingBroadcasts.delete(id);
      }
    }
  }

  #handleError(ctx, error, method) {
    const adminId = ctx?.from?.id || 'unknown';
    const errorMessage = error.message || 'Error desconocido';
    
    logger.error(method, error, { adminId, errorMessage });
    
    ctx.reply(`❌ Error: ${escapeHtml(errorMessage)}`);
  }

  #getAdminId() {
    return this.#parseCommand({ from: { id: 'system' } }).adminId; // Mock para uso interno si fuera necesario
  }
}

module.exports = AdminHandler;
