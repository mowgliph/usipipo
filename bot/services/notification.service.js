// services/notification.service.js
const config = require('../config/environment');
const messages = require('../utils/messages');

class NotificationService {
  constructor(bot) {
    this.bot = bot;
  }

  /**
   * Notifica al administrador sobre solicitudes de acceso
   */
  async notifyAdminAccessRequest(user) {
    try {
      await this.bot.telegram.sendMessage(
        config.ADMIN_ID,
        messages.ACCESS_REQUEST_ADMIN_NOTIFICATION(user),
        { parse_mode: 'Markdown' }
      );
      console.log(`✅ Notificación enviada al admin sobre solicitud de ${user.id}`);
      return true;
    } catch (error) {
      console.error('❌ Error al notificar al admin:', error.message);
      return false;
    }
  }

  /**
   * Notifica al administrador sobre errores críticos
   */
  async notifyAdminError(errorMessage, context = {}) {
    try {
      const message = 
        `🚨 **ERROR CRÍTICO EN EL BOT**\n\n` +
        `⚠️ ${errorMessage}\n\n` +
        `📋 **Contexto:**\n` +
        `\`\`\`json\n${JSON.stringify(context, null, 2)}\n\`\`\`\n\n` +
        `🕐 ${new Date().toLocaleString()}`;

      await this.bot.telegram.sendMessage(
        config.ADMIN_ID,
        message,
        { parse_mode: 'Markdown' }
      );
      return true;
    } catch (error) {
      console.error('❌ Error al enviar notificación de error:', error.message);
      return false;
    }
  }

  /**
   * Envía mensaje broadcast a todos los usuarios autorizados
   */
  async broadcastToAuthorizedUsers(message) {
    const results = {
      success: 0,
      failed: 0
    };

    for (const userId of config.AUTHORIZED_USERS) {
      try {
        await this.bot.telegram.sendMessage(userId, message, { parse_mode: 'Markdown' });
        results.success++;
      } catch (error) {
        console.error(`❌ Error enviando mensaje a ${userId}:`, error.message);
        results.failed++;
      }
    }

    return results;
  }
}

module.exports = NotificationService;
