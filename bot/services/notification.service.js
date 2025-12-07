// services/notification.service.js
const config = require('../config/environment');
const messages = require('../utils/messages');
const userManager = require('./userManager.service');

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
const italic = (text) => `<i>${text}</i>`;
const code = (text) => `<code>${text}</code>`;

// =====================================================
// CLASE NOTIFICATION SERVICE
// =====================================================

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
      // messages.js ya devuelve HTML válido, no necesitamos escapar nada aquí
      const formattedMessage = messages.ACCESS_REQUEST_ADMIN_NOTIFICATION(user);
      
      await this.bot.telegram.sendMessage(config.ADMIN_ID, formattedMessage);
      
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
      // Escapamos el JSON para que no rompa el HTML si contiene < o >
      const escapedContext = code(escapeHtml(JSON.stringify(context, null, 2)));
      const safeErrorMessage = escapeHtml(errorMessage);

      const message = `${bold('ERROR CRÍTICO EN EL BOT')}\n\n` +
        `${bold(safeErrorMessage)}\n\n` +
        `${bold('Contexto:')}\n` +
        `${escapedContext}\n\n` +
        `${italic(new Date().toLocaleString())}`;

      await this.bot.telegram.sendMessage(config.ADMIN_ID, message);
      return true;
    } catch (error) {
      console.error('Error al enviar notificación de error:', error.message);
      return false;
    }
  }

  /**
   * Envía mensaje broadcast a todos los usuarios autorizados activos
   * @param {string} message - Mensaje a enviar (debe ser HTML válido)
   * @returns {Object} Resultados del envío (success, failed)
   */
  async broadcastToAuthorizedUsers(message) {
    const users = userManager.getAllUsers().filter(u => u.status === 'active');
    const results = { success: 0, failed: 0 };

    for (const user of users) {
      try {
        await this.bot.telegram.sendMessage(user.id, message);
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

      // messages.SYSTEM_STARTUP ya retorna HTML
      let message = messages.SYSTEM_STARTUP(serverInfo, stats.admins, stats.total);
      
      // Agregamos un prefijo si se desea, asegurando formato HTML
      message = `${bold('INICIO DEL SISTEMA')}:\n\n${message}`;

      console.log(`Enviando notificación de inicio a ${admins.length} administradores...`);

      const results = { success: 0, failed: 0 };

      for (const admin of admins) {
        try {
          await this.bot.telegram.sendMessage(admin.id, message);
          results.success++;
        } catch (error) {
          console.error(`Error notificando inicio al admin ${admin.id}:`, error.message);
          results.failed++;
        }
      }

      console.log(`Notificación de inicio completada: ${results.success} enviados, ${results.failed} fallidos.`);
      return results;

    } catch (error) {
      console.error('Error crítico al notificar inicio del sistema:', error);
      return { success: 0, failed: 0 };
    }
  }

  /**
   * Envía un mensaje broadcast a una lista de usuarios
   * @param {string} message - Mensaje base a enviar (ya viene sanitizado desde admin.handler)
   * @param {Array} recipients - Lista de usuarios destinatarios
   * @param {Object} options - Opciones (delay, includeHeader)
   * @returns {Object} Resultados del envío (success, failed, errors)
   */
  async sendBroadcast(message, recipients, options = {}) {
    const results = { success: 0, failed: 0, errors: [] };

    const { delay = 50, includeHeader = true } = options;

    // Formatear con HTML
    const formattedMessage = includeHeader
      ? `${bold('ANUNCIO')}\n━━━━━━━━━━━━━━━━━━━━\n\n${message}\n\n━━━━━━━━━━━━━━━━━━━━\n${italic('🤖 uSipipo VPN Bot')}`
      : message;

    for (const user of recipients) {
      try {
        await this.bot.telegram.sendMessage(user.id, formattedMessage);
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

    console.log(`Broadcast completado: ${results.success} exitosos, ${results.failed} fallidos`);
    return results;
  }

  /**
   * Envía broadcast con imagen
   * @param {string} message - Mensaje/caption (Sanitizado)
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
            caption: `${bold('ANUNCIO')}\n\n${message}`,
            parse_mode: 'HTML' // En sendPhoto sí es bueno ser explícito a veces, pero el global debería cubrirlo
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
