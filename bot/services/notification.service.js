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

class NotificationService {
  constructor(bot) {
    this.bot = bot;
  }

  // --- MÉTODOS DE ADMIN (Sin cambios mayores, solo optimización) ---

  async notifyAdminAccessRequest(user) {
    try {
      const formattedMessage = messages.ACCESS_REQUEST_ADMIN_NOTIFICATION(user);
      await this.bot.telegram.sendMessage(config.ADMIN_ID, formattedMessage);
      console.log(`Notificación enviada al admin sobre solicitud de ${user.id}`);
      return true;
    } catch (error) {
      console.error('Error al notificar al admin:', error.message);
      return false;
    }
  }

  async notifyAdminError(errorMessage, context = {}) {
    try {
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

  // --- CORRECCIÓN PRINCIPAL: BROADCAST OPTIMIZADO ---

  /**
   * Envía mensaje a múltiples usuarios procesando por lotes (Batches)
   * para no bloquear el Event Loop.
   */
  async sendBroadcast(message, recipients, options = {}) {
    const { includeHeader = true } = options;
    const results = { success: 0, failed: 0, errors: [] };
    const BATCH_SIZE = 20; // Enviar 20 mensajes en paralelo
    const DELAY_BETWEEN_BATCHES = 1000; // Esperar 1s entre lotes (Rate limiting de Telegram)

    const formattedMessage = includeHeader
      ? `${bold('ANUNCIO')}\n━━━━━━━━━━━━━━━━━━━━\n\n${message}\n\n━━━━━━━━━━━━━━━━━━━━\n${italic('🤖 uSipipo VPN Bot')}`
      : message;

    // Procesar en lotes
    for (let i = 0; i < recipients.length; i += BATCH_SIZE) {
      const batch = recipients.slice(i, i + BATCH_SIZE);
      
      // Ejecutar lote en paralelo
      const promises = batch.map(user => 
        this.bot.telegram.sendMessage(user.id, formattedMessage)
          .then(() => ({ status: 'fulfilled' }))
          .catch(err => ({ status: 'rejected', userId: user.id, error: err.message }))
      );

      const batchResults = await Promise.all(promises);

      // Contabilizar resultados
      batchResults.forEach(res => {
        if (res.status === 'fulfilled') {
          results.success++;
        } else {
          results.failed++;
          results.errors.push({ userId: res.userId, error: res.error });
          console.error(`Error enviando broadcast:`, res.error);
        }
      });

      // Pequeño descanso si quedan más usuarios, para respetar límites de Telegram
      if (i + BATCH_SIZE < recipients.length) {
        await new Promise(resolve => setTimeout(resolve, DELAY_BETWEEN_BATCHES));
      }
    }

    console.log(`Broadcast completado: ${results.success} exitosos, ${results.failed} fallidos`);
    return results;
  }

  /**
   * Notifica el inicio del sistema (Usa la lógica optimizada si hay muchos admins)
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
      message = `${bold('INICIO DEL SISTEMA')}:\n\n${message}`;

      console.log(`Enviando notificación de inicio a ${admins.length} administradores...`);

      // Reutilizamos la lógica de envío simple para admins (suelen ser pocos)
      const results = { success: 0, failed: 0 };
      for (const admin of admins) {
        try {
          await this.bot.telegram.sendMessage(admin.id, message);
          results.success++;
        } catch (error) {
          console.error(`Error admin ${admin.id}:`, error.message);
          results.failed++;
        }
      }
      return results;

    } catch (error) {
      console.error('Error crítico inicio sistema:', error);
      return { success: 0, failed: 0 };
    }
  }

  /**
   * Broadcast con foto optimizado por lotes
   */
  async sendBroadcastWithPhoto(message, photoUrl, recipients) {
    const results = { success: 0, failed: 0, errors: [] };
    const BATCH_SIZE = 15; // Fotos pesan más, lote más pequeño
    const DELAY = 1500;

    for (let i = 0; i < recipients.length; i += BATCH_SIZE) {
      const batch = recipients.slice(i, i + BATCH_SIZE);
      
      const promises = batch.map(user => 
        this.bot.telegram.sendPhoto(user.id, photoUrl, {
            caption: `${bold('ANUNCIO')}\n\n${message}`,
            parse_mode: 'HTML'
          })
          .then(() => ({ status: 'fulfilled' }))
          .catch(err => ({ status: 'rejected', userId: user.id, error: err.message }))
      );

      const batchResults = await Promise.all(promises);

      batchResults.forEach(res => {
        if (res.status === 'fulfilled') results.success++;
        else {
          results.failed++;
          results.errors.push({ userId: res.userId, error: res.error });
        }
      });

      if (i + BATCH_SIZE < recipients.length) {
        await new Promise(resolve => setTimeout(resolve, DELAY));
      }
    }
    return results;
  }
}

module.exports = NotificationService;
