// handlers/admin.handler.js
const userManager = require('../services/userManager.service');
const messages = require('../utils/messages');
const { Markup } = require('telegraf');
const { escapeMarkdown, bold, code } = require('../utils/markdown');


class AdminHandler {
  constructor(notificationService) {
    this.notificationService = notificationService;
    this.pendingBroadcasts = new Map();
  }

  /**
   * Comando: /agregar [ID] [nombre_opcional]
   * Agrega un usuario a la lista de autorizados
   */
  async handleAddUser(ctx) {
    const adminId = ctx.from.id;
    const args = ctx.message.text.split(' ').slice(1);
    
    if (args.length === 0) {
      return ctx.reply(
        `⚠️ ${bold('Uso incorrecto')}\n\n` +
        `📝 Formato: ${code('/agregar [ID] [nombre_opcional]')}\n\n` +
        `${bold('Ejemplos:')}\n` +
        `• ${code('/agregar 123456789')}\n` +
        `• ${code('/agregar 123456789 Juan Pérez')}\n\n` +
        `💡 Obtén el ID con el comando ${code('/miinfo')}`,
        { parse_mode: 'Markdown' }
      );
    }

    const userId = args[0];
    const userName = args.slice(1).join(' ') || null;

    if (!/^\d+$/.test(userId)) {
      return ctx.reply('❌ El ID debe ser numérico');
    }

    try {
      const newUser = await userManager.addUser(userId, adminId, userName);
      const safeName = newUser.name ? escapeMarkdown(newUser.name) : 'No especificado';
      
      await ctx.reply(
        `✅ ${bold('Usuario agregado exitosamente')}\n\n` +
        `🆔 ID: ${code(newUser.id)}\n` +
        `👤 Nombre: ${safeName}\n` +
        `📅 Agregado: ${new Date(newUser.addedAt).toLocaleString('es-ES')}\n\n` +
        `El usuario ya puede usar el bot con /start`,
        { parse_mode: 'Markdown' }
      );

      await this.notifyUserApproved(userId, userName);
      console.log(`✅ Admin ${adminId} agregó usuario ${userId}`);
      
    } catch (error) {
      console.error('Error agregando usuario:', error);
      ctx.reply(`❌ Error: ${escapeMarkdown(error.message)}`);
    }
  }

  /**
   * Comando: /remover [ID]
   * Remueve un usuario de la lista
   */
  async handleRemoveUser(ctx) {
    const args = ctx.message.text.split(' ').slice(1);
    
    if (args.length === 0) {
      return ctx.reply(
        '⚠️ **Uso incorrecto**\n\n' +
        '📝 Formato: `/remover [ID]`\n\n' +
        '**Ejemplo:** `/remover 123456789`',
        { parse_mode: 'Markdown' }
      );
    }

    const userId = args[0];

    try {
      await userManager.removeUser(userId);
      
      await ctx.reply(
        `🗑️ **Usuario removido**\n\n` +
        `🆔 ID: \`${userId}\`\n` +
        `El usuario ya no tiene acceso al bot`,
        { parse_mode: 'Markdown' }
      );

      // Notificar al usuario
      await this.notifyUserRemoved(userId);
      
    } catch (error) {
      ctx.reply(`❌ Error: ${error.message}`);
    }
  }

  /**
   * Comando: /suspender [ID]
   * Suspende temporalmente a un usuario
   */
  async handleSuspendUser(ctx) {
    const args = ctx.message.text.split(' ').slice(1);
    
    if (args.length === 0) {
      return ctx.reply(
        '⚠️ Formato: `/suspender [ID]`',
        { parse_mode: 'Markdown' }
      );
    }

    try {
      const user = await userManager.suspendUser(args[0]);
      
      await ctx.reply(
        `⏸️ **Usuario suspendido**\n\n` +
        `🆔 ID: \`${user.id}\`\n` +
        `Para reactivar usa: /reactivar ${user.id}`,
        { parse_mode: 'Markdown' }
      );
      
    } catch (error) {
      ctx.reply(`❌ Error: ${error.message}`);
    }
  }

  /**
   * Comando: /reactivar [ID]
   */
  async handleReactivateUser(ctx) {
    const args = ctx.message.text.split(' ').slice(1);
    
    if (args.length === 0) {
      return ctx.reply('⚠️ Formato: `/reactivar [ID]`', { parse_mode: 'Markdown' });
    }

    try {
      const user = await userManager.reactivateUser(args[0]);
      
      await ctx.reply(
        `▶️ **Usuario reactivado**\n\n` +
        `🆔 ID: \`${user.id}\`\n` +
        `El usuario puede usar el bot nuevamente`,
        { parse_mode: 'Markdown' }
      );
      
      await this.notifyUserReactivated(user.id);
      
    } catch (error) {
      ctx.reply(`❌ Error: ${error.message}`);
    }
  }

  /**
   * Comando: /usuarios
   * Lista todos los usuarios autorizados
   */
  async handleListUsers(ctx) {
    const users = userManager.getAllUsers();
    const stats = userManager.getUserStats();
    
    if (users.length === 0) {
      return ctx.reply('📭 No hay usuarios registrados');
    }

    let message = `👥 ${bold('USUARIOS AUTORIZADOS')}\n\n`;
    message += `📊 ${bold('Estadísticas:')}\n`;
    message += `• Total: ${stats.total}\n`;
    message += `• Activos: ${stats.active}\n`;
    message += `• Suspendidos: ${stats.suspended}\n`;
    message += `• Admins: ${stats.admins}\n\n`;
    message += `━━━━━━━━━━━━━━━━━━━━\n\n`;

    users.forEach((user, index) => {
      const statusIcon = user.status === 'active' ? '✅' : '⏸️';
      const roleIcon = user.role === 'admin' ? '👑' : '👤';
      const safeName = user.name ? escapeMarkdown(user.name) : '';
      
      message += `${index + 1}. ${statusIcon} ${roleIcon} ${code(user.id)}\n`;
      if (safeName) message += `   📝 ${safeName}\n`;
      message += `   📅 ${new Date(user.addedAt).toLocaleDateString('es-ES')}\n\n`;
    });

    return ctx.reply(message, { parse_mode: 'Markdown' });
  }



  /**
   * Comando: /stats
   * Muestra estadísticas detalladas
   */
  async handleStats(ctx) {
    const stats = userManager.getUserStats();
    const users = userManager.getAllUsers();
    
    // Calcular usuarios agregados en las últimas 24h
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const recentUsers = users.filter(u => new Date(u.addedAt) > oneDayAgo);
    
    const message = 
      `📊 **ESTADÍSTICAS DEL SISTEMA**\n\n` +
      `👥 **Usuarios:**\n` +
      `• Total: ${stats.total}\n` +
      `• Activos: ${stats.active}\n` +
      `• Suspendidos: ${stats.suspended}\n` +
      `• Administradores: ${stats.admins}\n` +
      `• Usuarios regulares: ${stats.users}\n\n` +
      `📈 **Actividad:**\n` +
      `• Nuevos (24h): ${recentUsers.length}\n\n` +
      `🕐 Actualizado: ${new Date().toLocaleString('es-ES')}`;
    
    return ctx.reply(message, { parse_mode: 'Markdown' });
  }

  /**
   * Notifica al usuario que fue aprobado
   */
  async notifyUserApproved(userId, userName) {
    try {
      const message = 
        `🎉 **¡Solicitud Aprobada!**\n\n` +
        `✅ Tu acceso a **uSipipo VPN Bot** ha sido autorizado.\n\n` +
        `Ahora puedes usar el comando /start para acceder al menú principal y crear tus configuraciones VPN.\n\n` +
        `¡Bienvenido${userName ? ' ' + userName : ''}! 🚀`;
      
      await this.notificationService.bot.telegram.sendMessage(
        userId,
        message,
        { parse_mode: 'Markdown' }
      );
      
    } catch (error) {
      console.error(`❌ Error notificando a usuario ${userId}:`, error.message);
    }
  }

  /**
   * Notifica al usuario que fue removido
   */
  async notifyUserRemoved(userId) {
    try {
      const message = 
        `⚠️ **Acceso Revocado**\n\n` +
        `Tu autorización para usar **uSipipo VPN Bot** ha sido removida.\n\n` +
        `Si crees que esto es un error, contacta al administrador.`;
      
      await this.notificationService.bot.telegram.sendMessage(
        userId,
        message,
        { parse_mode: 'Markdown' }
      );
      
    } catch (error) {
      console.error(`Error notificando remoción a ${userId}`);
    }
  }

  /**
   * Notifica al usuario que fue reactivado
   */
  async notifyUserReactivated(userId) {
    try {
      const message = 
        `✅ **Acceso Reactivado**\n\n` +
        `Tu acceso a **uSipipo VPN Bot** ha sido restaurado.\n\n` +
        `Usa /start para continuar.`;
      
      await this.notificationService.bot.telegram.sendMessage(
        userId,
        message,
        { parse_mode: 'Markdown' }
      );
      
    } catch (error) {
      console.error(`Error notificando reactivación a ${userId}`);
    }
  }
  
  /**
  * Comando: /broadcast [mensaje]
  * Envía un mensaje a todos los usuarios activos
  */
  async handleBroadcast(ctx) {
    const adminId = ctx.from.id.toString();
    const messageText = ctx.message.text.replace(/^\/broadcast\s*/, '').trim();
    
    if (!messageText) {
      return ctx.reply(
        `📢 ${bold('Comando Broadcast')}\n\n` +
        `${bold('Uso:')} ${code('/broadcast [mensaje]')}\n\n` +
        `${bold('Ejemplos:')}\n` +
        `• ${code('/broadcast ¡Nuevo servidor disponible!')}\n` +
        `• ${code('/broadcast 🎉 Promoción: 50% descuento este mes')}\n\n` +
        `${bold('Formato soportado:')}\n` +
        `• Texto plano\n` +
        `• Emojis\n` +
        `• Markdown básico (${code('*negrita*')}, ${code('_cursiva_')})\n\n` +
        `💡 El mensaje se enviará a todos los usuarios activos.`,
        { parse_mode: 'Markdown' }
      );
    }

    // Obtener estadísticas de usuarios
    const users = userManager.getAllUsers();
    const activeUsers = users.filter(u => u.status === 'active');
    const userCount = activeUsers.filter(u => u.role === 'user').length;
    const adminCount = activeUsers.filter(u => u.role === 'admin').length;

    // Guardar mensaje pendiente para confirmación
    const broadcastId = Date.now().toString();
    this.pendingBroadcasts.set(broadcastId, {
      message: messageText,
      adminId: adminId,
      createdAt: new Date(),
      targetCount: activeUsers.length
    });

    // Limpiar broadcasts antiguos (más de 5 minutos)
    this.cleanOldBroadcasts();

    return ctx.reply(
      `📢 ${bold('CONFIRMAR BROADCAST')}\n\n` +
      `${bold('Mensaje a enviar:')}\n` +
      `━━━━━━━━━━━━━━━━━━━━\n` +
      `${messageText}\n` +
      `━━━━━━━━━━━━━━━━━━━━\n\n` +
      `${bold('Destinatarios:')}\n` +
      `• 👤 Usuarios: ${userCount}\n` +
      `• 👑 Admins: ${adminCount}\n` +
      `• 📊 Total: ${activeUsers.length}\n\n` +
      `⚠️ ${bold('¿Confirmas el envío?')}`,
      {
        parse_mode: 'Markdown',
        ...Markup.inlineKeyboard([
          [
            Markup.button.callback('✅ Enviar a TODOS', `broadcast_all_${broadcastId}`),
          ],
          [
            Markup.button.callback('👤 Solo Usuarios', `broadcast_users_${broadcastId}`),
            Markup.button.callback('👑 Solo Admins', `broadcast_admins_${broadcastId}`)
          ],
          [
            Markup.button.callback('❌ Cancelar', `broadcast_cancel_${broadcastId}`)
          ]
        ])
      }
    );
  }
  
  /**
  * Procesa la confirmación del broadcast
  */
  async handleBroadcastConfirm(ctx, broadcastId, target) {
    await ctx.answerCbQuery();

    const broadcast = this.pendingBroadcasts.get(broadcastId);
    
    if (!broadcast) {
      return ctx.editMessageText(
        '⚠️ Esta solicitud de broadcast ha expirado.\n\nUsa /broadcast para crear una nueva.',
        { parse_mode: 'Markdown' }
      );
    }

    // Eliminar el broadcast pendiente
    this.pendingBroadcasts.delete(broadcastId);

    // Determinar destinatarios según target
    const users = userManager.getAllUsers();
    let recipients;
    let targetLabel;

    switch (target) {
      case 'all':
        recipients = users.filter(u => u.status === 'active');
        targetLabel = 'todos los usuarios';
        break;
      case 'users':
        recipients = users.filter(u => u.status === 'active' && u.role === 'user');
        targetLabel = 'usuarios regulares';
        break;
      case 'admins':
        recipients = users.filter(u => u.status === 'active' && u.role === 'admin');
        targetLabel = 'administradores';
        break;
      default:
        recipients = [];
    }

    if (recipients.length === 0) {
      return ctx.editMessageText(
        '📭 No hay destinatarios disponibles para este broadcast.',
        { parse_mode: 'Markdown' }
      );
    }

    // Actualizar mensaje a "enviando..."
    await ctx.editMessageText(
      `📤 ${bold('Enviando broadcast...')}\n\n` +
      `⏳ Enviando a ${recipients.length} ${targetLabel}...\n` +
      `Por favor espera...`,
      { parse_mode: 'Markdown' }
    );

    // Enviar el broadcast
    const results = await this.notificationService.sendBroadcast(
      broadcast.message,
      recipients
    );

    // Mostrar resultados
    const successRate = ((results.success / recipients.length) * 100).toFixed(1);
    
    await ctx.editMessageText(
      `📢 ${bold('BROADCAST COMPLETADO')}\n\n` +
      `${bold('Estadísticas de envío:')}\n` +
      `• ✅ Enviados: ${results.success}\n` +
      `• ❌ Fallidos: ${results.failed}\n` +
      `• 📊 Tasa de éxito: ${successRate}%\n\n` +
      `${bold('Destinatarios:')} ${targetLabel}\n` +
      `${bold('Hora:')} ${new Date().toLocaleString('es-ES')}\n\n` +
      (results.failed > 0 
        ? `⚠️ Algunos usuarios pueden haber bloqueado el bot.`
        : `✅ Todos los mensajes fueron entregados.`),
      { parse_mode: 'Markdown' }
    );

    console.log(`📢 Broadcast enviado por admin ${broadcast.adminId}: ${results.success}/${recipients.length} exitosos`);
  }
  
  /**
  * Cancela un broadcast pendiente
  */
  async handleBroadcastCancel(ctx, broadcastId) {
    await ctx.answerCbQuery('Broadcast cancelado');
    
    this.pendingBroadcasts.delete(broadcastId);
    
    await ctx.editMessageText(
      '❌ Broadcast cancelado.\n\nUsa /broadcast para crear uno nuevo.',
      { parse_mode: 'Markdown' }
    );
  }
  
  /**
  * Comando: /mensaje [ID] [mensaje]
  * Envía un mensaje directo a un usuario específico
  */
  async handleDirectMessage(ctx) {
    const args = ctx.message.text.split(' ').slice(1);
    
    if (args.length < 2) {
      return ctx.reply(
        `💬 ${bold('Mensaje Directo')}\n\n` +
        `${bold('Uso:')} ${code('/mensaje [ID] [mensaje]')}\n\n` +
        `${bold('Ejemplo:')}\n` +
        `${code('/mensaje 123456789 Hola, tu acceso ha sido renovado')}\n\n` +
        `💡 Útil para comunicación personalizada con usuarios.`,
        { parse_mode: 'Markdown' }
      );
    }

    const targetUserId = args[0];
    const messageText = args.slice(1).join(' ');

    // Verificar que el usuario existe
    const targetUser = userManager.getUser(targetUserId);
    
    if (!targetUser) {
      return ctx.reply(
        `❌ Usuario ${code(targetUserId)} no encontrado en la base de datos.`,
        { parse_mode: 'Markdown' }
      );
    }

    try {
      const formattedMessage = 
        `💬 ${bold('Mensaje del Administrador')}\n` +
        `━━━━━━━━━━━━━━━━━━━━\n\n` +
        `${messageText}\n\n` +
        `━━━━━━━━━━━━━━━━━━━━\n` +
        `📅 ${new Date().toLocaleString('es-ES')}`;

      await this.notificationService.bot.telegram.sendMessage(
        targetUserId,
        formattedMessage,
        { parse_mode: 'Markdown' }
      );

      const userName = targetUser.name ? escapeMarkdown(targetUser.name) : 'Sin nombre';
      
      await ctx.reply(
        `✅ ${bold('Mensaje enviado')}\n\n` +
        `👤 Destinatario: ${userName}\n` +
        `🆔 ID: ${code(targetUserId)}\n` +
        `📝 Mensaje: ${escapeMarkdown(messageText.substring(0, 50))}...`,
        { parse_mode: 'Markdown' }
      );

      console.log(`💬 Mensaje directo enviado a ${targetUserId} por admin ${ctx.from.id}`);

    } catch (error) {
      console.error(`Error enviando mensaje directo a ${targetUserId}:`, error);
      
      await ctx.reply(
        `❌ No se pudo enviar el mensaje a ${code(targetUserId)}\n\n` +
        `Posibles causas:\n` +
        `• El usuario bloqueó el bot\n` +
        `• El usuario eliminó su cuenta\n` +
        `• Error de conexión`,
        { parse_mode: 'Markdown' }
      );
    }
  }
  
  /**
   * Comando: /plantillas
   * Muestra plantillas de mensajes predefinidas
   */
  async handleTemplates(ctx) {
    return ctx.reply(
      `📋 ${bold('PLANTILLAS DE MENSAJES')}\n\n` +
      `${bold('1. Bienvenida:')}\n` +
      `${code('/broadcast 🎉 ¡Bienvenidos nuevos usuarios! Recuerden usar /help para ver todas las funciones disponibles.')}\n\n` +
      `${bold('2. Mantenimiento:')}\n` +
      `${code('/broadcast ⚠️ Mantenimiento programado: El servicio estará en mantenimiento el [FECHA] de [HORA] a [HORA]. Disculpen las molestias.')}\n\n` +
      `${bold('3. Promoción:')}\n` +
      `${code('/broadcast 🎁 ¡PROMOCIÓN ESPECIAL! Este mes disfruta de [BENEFICIO]. Válido hasta [FECHA].')}\n\n` +
      `${bold('4. Nueva función:')}\n` +
      `${code('/broadcast 🚀 ¡Nueva función disponible! Ahora puedes [DESCRIPCIÓN]. Pruébalo con /start')}\n\n` +
      `${bold('5. Actualización:')}\n` +
      `${code('/broadcast 📢 Actualización importante: [DESCRIPCIÓN]. Por favor actualiza tu configuración.')}\n\n` +
      `💡 Copia y personaliza estas plantillas según tu necesidad.`,
      { parse_mode: 'Markdown' }
    );
  }

  /**
   * Limpia broadcasts pendientes antiguos (más de 5 minutos)
   */
  cleanOldBroadcasts() {
    const fiveMinutesAgo = Date.now() - (5 * 60 * 1000);
    
    for (const [id, broadcast] of this.pendingBroadcasts.entries()) {
      if (new Date(broadcast.createdAt).getTime() < fiveMinutesAgo) {
        this.pendingBroadcasts.delete(id);
      }
    }
  }
}

module.exports = AdminHandler;
