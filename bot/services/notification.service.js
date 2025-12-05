// services/notification.service.js
const config = require('../config/environment');
const messages = require('../utils/messages');
const userManager = require('./userManager.service'); // Importamos userManager

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
  
  /**
   * Notifica el inicio del sistema a todos los administradores
   */
  async notifyAdminsSystemStartup() {
    try {
      // Obtener estadísticas actuales
      const stats = userManager.getUserStats();
      const allUsers = userManager.getAllUsers();
      
      // Filtrar solo administradores activos
      const admins = allUsers.filter(u => u.role === 'admin' && u.status === 'active');
      
      // Datos del servidor para el reporte
      const serverInfo = {
        ip: config.SERVER_IPV4,
        wgPort: config.WIREGUARD_PORT,
        outlinePort: config.OUTLINE_API_PORT
      };

      const message = messages.SYSTEM_STARTUP(serverInfo, stats.admins, stats.total);

      console.log(`📢 Enviando notificación de inicio a ${admins.length} administradores...`);

      const results = { success: 0, failed: 0 };

      for (const admin of admins) {
        try {
          await this.bot.telegram.sendMessage(admin.id, message, { parse_mode: 'Markdown' });
          results.success++;
        } catch (error) {
          console.error(`❌ Error notificando inicio al admin ${admin.id}:`, error.message);
          results.failed++;
        }
      }

      console.log(`✅ Notificación de inicio completada: ${results.success} enviados, ${results.failed} fallidos.`);
      return results;

    } catch (error) {
      console.error('❌ Error crítico al notificar inicio del sistema:', error);
    }
  }
  
  /**
   * Envía un mensaje broadcast a una lista de usuarios
   * @param {string} message - Mensaje a enviar
   * @param {Array} recipients - Lista de usuarios destinatarios
   * @param {Object} options - Opciones adicionales
   * @returns {Object} Resultados del envío
   */
  async sendBroadcast(message, recipients, options = {}) {
    const results = {
      success: 0,
      failed: 0,
      errors: []
    };

    const {
      delay = 50, // Delay entre mensajes para evitar rate limiting
      parseMode = 'Markdown',
      includeHeader = true
    } = options;

    // Formatear mensaje con header si se solicita
    const formattedMessage = includeHeader
      ? `📢 ${this.bold('ANUNCIO')}\n━━━━━━━━━━━━━━━━━━━━\n\n${message}\n\n━━━━━━━━━━━━━━━━━━━━\n🤖 uSipipo VPN Bot`
      : message;

    for (const user of recipients) {
      try {
        await this.bot.telegram.sendMessage(
          user.id,
          formattedMessage,
          { parse_mode: parseMode }
        );
        results.success++;
        
        // Pequeño delay para evitar rate limiting de Telegram
        if (delay > 0) {
          await this.sleep(delay);
        }
        
      } catch (error) {
        results.failed++;
        results.errors.push({
          userId: user.id,
          error: error.message
        });
        
        console.error(`❌ Error enviando broadcast a ${user.id}:`, error.message);
      }
    }

    console.log(`📢 Broadcast completado: ${results.success} exitosos, ${results.failed} fallidos`);
    return results;
  }
  
  /**
   * Envía broadcast con imagen
   * @param {string} message - Mensaje/caption
   * @param {string} photoUrl - URL de la imagen
   * @param {Array} recipients - Lista de usuarios
   */
  async sendBroadcastWithPhoto(message, photoUrl, recipients) {
    const results = {
      success: 0,
      failed: 0,
      errors: []
    };

    for (const user of recipients) {
      try {
        await this.bot.telegram.sendPhoto(
          user.id,
          photoUrl,
          {
            caption: `📢 **ANUNCIO**\n\n${message}`,
            parse_mode: 'Markdown'
          }
        );
        results.success++;
        await this.sleep(50);
        
      } catch (error) {
        results.failed++;
        results.errors.push({ userId: user.id, error: error.message });
      }
    }

    return results;
  }
  
  /**
   * Helper para sleep/delay
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

}

module.exports = NotificationService;
