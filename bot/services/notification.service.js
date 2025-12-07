// services/notification.service.js
const config = require('../config/environment');
const messages = require('../utils/messages');
const userManager = require('./userManager.service');

const { escapeHtml, bold, code, italic } = messages._helpers;

class NotificationService {
  constructor(bot) {
    this.bot = bot;
  }

  // ---------------------------------------------------------
  // NOTIFICACIONES AL ADMIN
  // ---------------------------------------------------------
  async notifyAdminAccessRequest(user) {
    try {
      const formatted = messages.ACCESS_REQUEST_ADMIN_NOTIFICATION(user);
      await this.bot.telegram.sendMessage(config.ADMIN_ID, formatted);
      return true;
    } catch (err) {
      console.error('Error al notificar solicitud al admin:', err.message);
      return false;
    }
  }

  async notifyAdminError(errorMessage, context = {}) {
    try {
      const safeError = escapeHtml(errorMessage);
      const safeContext = code(escapeHtml(JSON.stringify(context, null, 2)));

      const msg =
        `${bold('ERROR CRÍTICO EN EL BOT')}\n\n` +
        `${bold(safeError)}\n\n` +
        `${bold('Contexto:')}\n${safeContext}\n\n` +
        `${italic(new Date().toLocaleString())}`;

      await this.bot.telegram.sendMessage(config.ADMIN_ID, msg);
      return true;
    } catch (err) {
      console.error('Error enviando error crítico al admin:', err.message);
      return false;
    }
  }

  // ---------------------------------------------------------
  // BROADCAST (batch processing optimizado)
  // ---------------------------------------------------------
  async sendBroadcast(messageHtml, recipients, options = {}) {
    const { includeHeader = true } = options;

    const finalMessage = includeHeader
      ? `${bold('ANUNCIO')}\n━━━━━━━━━━━━━━━━━━━━\n\n${messageHtml}\n\n━━━━━━━━━━━━━━━━━━━━\n${italic('🤖 uSipipo VPN Bot')}`
      : messageHtml;

    const results = { success: 0, failed: 0, errors: [] };

    const BATCH_SIZE = 20;
    const DELAY = 1000;

    for (let i = 0; i < recipients.length; i += BATCH_SIZE) {
      const batch = recipients.slice(i, i + BATCH_SIZE);

      const tasks = batch.map((u) =>
        this.bot.telegram.sendMessage(u.id, finalMessage)
          .then(() => ({ ok: true }))
          .catch(err => ({ ok: false, userId: u.id, error: err.message }))
      );

      const batchResults = await Promise.all(tasks);

      batchResults.forEach((r) => {
        if (r.ok) results.success++;
        else {
          results.failed++;
          results.errors.push({ userId: r.userId, error: r.error });
        }
      });

      if (i + BATCH_SIZE < recipients.length) {
        await new Promise(res => setTimeout(res, DELAY));
      }
    }

    console.log(`Broadcast: ${results.success} OK, ${results.failed} FAIL`);
    return results;
  }

  // ---------------------------------------------------------
  // BROADCAST CON FOTO
  // ---------------------------------------------------------
  async sendBroadcastWithPhoto(messageHtml, photoUrl, recipients) {
    const results = { success: 0, failed: 0, errors: [] };

    const BATCH_SIZE = 15;
    const DELAY = 1500;

    for (let i = 0; i < recipients.length; i += BATCH_SIZE) {
      const batch = recipients.slice(i, i + BATCH_SIZE);

      const tasks = batch.map((u) =>
        this.bot.telegram.sendPhoto(u.id, photoUrl, {
          caption: `${bold('ANUNCIO')}\n\n${messageHtml}`,
          parse_mode: 'HTML'
        })
          .then(() => ({ ok: true }))
          .catch(err => ({ ok: false, userId: u.id, error: err.message }))
      );

      const batchResults = await Promise.all(tasks);

      batchResults.forEach((r) => {
        if (r.ok) results.success++;
        else {
          results.failed++;
          results.errors.push({ userId: r.userId, error: r.error });
        }
      });

      if (i + BATCH_SIZE < recipients.length) {
        await new Promise(res => setTimeout(res, DELAY));
      }
    }

    return results;
  }

  // ---------------------------------------------------------
  // NOTIFICACIÓN DE INICIO DEL SISTEMA
  // ---------------------------------------------------------
  async notifyAdminsSystemStartup() {
    try {
      const stats = userManager.getUserStats();
      const all = userManager.getAllUsers();
      const admins = all.filter(u => u.role === 'admin' && u.status === 'active');

      const info = {
        ip: config.SERVER_IPV4,
        wgPort: config.WIREGUARD_PORT,
        outlinePort: config.OUTLINE_API_PORT
      };

      const text = messages.SYSTEM_STARTUP(info, stats.admins, stats.total);

      const final = `${bold('INICIO DEL SISTEMA')}\n\n${text}`;

      const results = { success: 0, failed: 0 };

      for (const admin of admins) {
        try {
          await this.bot.telegram.sendMessage(admin.id, final);
          results.success++;
        } catch (err) {
          results.failed++;
        }
      }

      return results;
    } catch (err) {
      console.error('Error crítico notifyAdminsSystemStartup:', err);
      return { success: 0, failed: 0 };
    }
  }
}

module.exports = NotificationService;