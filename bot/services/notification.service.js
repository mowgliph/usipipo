// services/notification.service.js
const config = require('../config/environment');
const messages = require('../utils/messages');
const userManager = require('./userManager.service');
const { bold, italic, code, strikethrough, spoiler } = require('../utils/markdown'); // Importar utilidades V2

class NotificationService {
  constructor(bot) {
    this.bot = bot;
  }

  /**
   * Notifica al administrador sobre solicitudes de acceso
   * @param {Object} user - Datos del usuario solicitante
   * @returns {Promise<boolean>} True si se envía exitosamente
   */
  async notifyAdminAccessRequest(user) {
    try {
      const formattedMessage = messages.ACCESS_REQUEST_ADMIN_NOTIFICATION(user);
      await this.bot.telegram.sendMessage(
        config.ADMIN_ID,
        formattedMessage, // Asumir que messages.js ya usa V2; si no, aplicar escapes aquí
        { parse_mode: 'MarkdownV2' }
      );
      console.log(`Notificación enviada al admin sobre solicitud de ${user.id}`);
      return true;
    } catch (error) {
      console.error('Error al notificar al admin:', error.message);
      return false;
    }
  }

  /**
   * Notifica al administrador sobre errores críticos
   * @param {string} errorMessage - Mensaje de error descriptivo
   * @param {Object} context - Contexto adicional (opcional)
   * @returns {Promise<boolean>} True si se envía exitosamente
   */
  async notifyAdminError(errorMessage, context = {}) {
    try {
      const escapedContext = code(JSON.stringify(context, null, 2));
      const message = `${bold('ERROR CRÍTICO EN EL BOT')}\n\n` +
        `${bold(errorMessage)}\n\n` +
        `${bold('Contexto:')}\n` +
        `${escapedContext}\n\n` +
        `${italic(new Date().toLocaleString())}`;

      await this.bot.telegram.sendMessage(
        config.ADMIN_ID,
        message,
        { parse_mode: 'MarkdownV2' }
      );
      return true;
    } catch (error) {
      console.error('Error al enviar notificación de error:', error.message);
      return false;
    }
  }

  /**
   * Envía mensaje broadcast a todos los usuarios autorizados activos
   * @param {string} message - Mensaje a enviar (pre-formateado con V2)
   * @returns {Object} Resultados del envío (success, failed)
   */
  async broadcastToAuthorizedUsers(message) {
    const users = userManager.getAllUsers().filter(u => u.status === 'active');
    const results = { success: 0, failed: 0 };

    for (const user of users) {
      try {
        await this.bot.telegram.sendMessage(user.id, message, { parse_mode: 'MarkdownV2' });
        results.success++;
      } catch (error) {
        console.error(`Error enviando mensaje a ${user.id}:`, error.message);
        results.failed++;
      }
    }

    return results;
  }

  /**
   * Notifica el inicio del sistema a todos los administradores activos
   * @returns {Object} Resultados del envío (success, failed)
   */
  async notifyAdminsSystemStartup() {
    try {
      const stats = userManager.getUserStats();
      const allUsers = userManager.getAllUsers();
      const admins = allUsers.filter(u => u.role === 'admin' && u.status === 'active');

      const serverInfo = {
        ip: config.SERVER_IPV4,
        wgPort: config.WIREGUARD_PORT,
        outlinePort: config.OUTLINE_API_PORT
      };

      let message = messages.SYSTEM_STARTUP(serverInfo, stats.admins, stats.total);
      // Si messages.SYSTEM_STARTUP no usa V2, envolver en bold/italic según necesite
      message = `\( {bold('INICIO DEL SISTEMA')}:\n\n \){message}`;

      console.log(`Enviando notificación de inicio a ${admins.length} administradores...`);

      const results = { success: 0, failed: 0 };

      for (const admin of admins) {
        try {
          await this.bot.telegram.sendMessage(admin.id, message, { parse_mode: 'MarkdownV2' });
          results.success++;
        } catch (error) {
          console.error(`Error notificando inicio al admin ${admin.id}:`, error.message);
          results.failed++;
        }
      }

      console.log(`Notificación de inicio completada: \( {results.success} enviados, \){results.failed} fallidos.`);
      return results;

    } catch (error) {
      console.error('Error crítico al notificar inicio del sistema:', error);
      return { success: 0, failed: 0 };
    }
  }

  /**
   * Envía un mensaje broadcast a una lista de usuarios
   * @param {string} message - Mensaje base a enviar
   * @param {Array} recipients - Lista de usuarios destinatarios
   * @param {Object} options - Opciones (delay, includeHeader)
   * @returns {Object} Resultados del envío (success, failed, errors)
   */
  async sendBroadcast(message, recipients, options = {}) {
    const results = { success: 0, failed: 0, errors: [] };

    const { delay = 50, includeHeader = true } = options;

    // Formatear con V2: usar bold para header
    const formattedMessage = includeHeader
      ? `\( {bold('ANUNCIO')}\n━━━━━━━━━━━━━━━━━━━━\n\n \){message}\n\n━━━━━━━━━━━━━━━━━━━━\n${italic('🤖 uSipipo VPN Bot')}`
      : message;

    for (const user of recipients) {
      try {
        await this.bot.telegram.sendMessage(
          user.id,
          formattedMessage,
          { parse_mode: 'MarkdownV2' }
        );
        results.success++;
        if (delay > 0) {
          await this.sleep(delay);
        }
      } catch (error) {
        results.failed++;
        results.errors.push({ userId: user.id, error: error.message });
        console.error(`Error enviando broadcast a ${user.id}:`, error.message);
      }
    }

    console.log(`Broadcast completado: \( {results.success} exitosos, \){results.failed} fallidos`);
    return results;
  }

  /**
   * Envía broadcast con imagen
   * @param {string} message - Mensaje/caption
   * @param {string} photoUrl - URL de la imagen
   * @param {Array} recipients - Lista de usuarios
   * @returns {Object} Resultados del envío (success, failed, errors)
   */
  async sendBroadcastWithPhoto(message, photoUrl, recipients) {
    const results = { success: 0, failed: 0, errors: [] };

    for (const user of recipients) {
      try {
        await this.bot.telegram.sendPhoto(
          user.id,
          photoUrl,
          {
            caption: `\( {bold('ANUNCIO')}\n\n \){message}`,
            parse_mode: 'MarkdownV2'
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
   * @param {number} ms - Milisegundos de espera
   * @returns {Promise<void>}
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

module.exports = NotificationService;