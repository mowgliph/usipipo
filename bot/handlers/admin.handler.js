// handlers/admin.handler.js
const userManager = require('../services/userManager.service');
const messages = require('../utils/messages');
const { Markup } = require('telegraf');

class AdminHandler {
  constructor(notificationService) {
    this.notificationService = notificationService;
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
        '⚠️ **Uso incorrecto**\n\n' +
        '📝 Formato: `/agregar [ID] [nombre_opcional]`\n\n' +
        '**Ejemplos:**\n' +
        '• `/agregar 123456789`\n' +
        '• `/agregar 123456789 Juan Pérez`\n\n' +
        '💡 Obtén el ID con el comando `/miinfo`',
        { parse_mode: 'Markdown' }
      );
    }

    const userId = args[0];
    const userName = args.slice(1).join(' ') || null;

    // Validar que sea un ID numérico
    if (!/^\d+$/.test(userId)) {
      return ctx.reply('❌ El ID debe ser numérico');
    }

    try {
      const newUser = await userManager.addUser(userId, adminId, userName);
      
      // Mensaje de confirmación al admin
      await ctx.reply(
        `✅ **Usuario agregado exitosamente**\n\n` +
        `🆔 ID: \`${newUser.id}\`\n` +
        `👤 Nombre: ${newUser.name || 'No especificado'}\n` +
        `📅 Agregado: ${new Date(newUser.addedAt).toLocaleString('es-ES')}\n\n` +
        `El usuario ya puede usar el bot con /start`,
        { parse_mode: 'Markdown' }
      );

      // Notificar al usuario nuevo
      await this.notifyUserApproved(userId, userName);
      
      console.log(`✅ Admin ${adminId} agregó usuario ${userId}`);
      
    } catch (error) {
      console.error('Error agregando usuario:', error);
      ctx.reply(`❌ Error: ${error.message}`);
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

    let message = `👥 **USUARIOS AUTORIZADOS**\n\n`;
    message += `📊 **Estadísticas:**\n`;
    message += `• Total: ${stats.total}\n`;
    message += `• Activos: ${stats.active}\n`;
    message += `• Suspendidos: ${stats.suspended}\n`;
    message += `• Admins: ${stats.admins}\n\n`;
    message += `━━━━━━━━━━━━━━━━━━━━\n\n`;

    users.forEach((user, index) => {
      const statusIcon = user.status === 'active' ? '✅' : '⏸️';
      const roleIcon = user.role === 'admin' ? '👑' : '👤';
      
      message += `${index + 1}. ${statusIcon} ${roleIcon} \`${user.id}\`\n`;
      if (user.name) message += `   📝 ${user.name}\n`;
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
}

module.exports = AdminHandler;
