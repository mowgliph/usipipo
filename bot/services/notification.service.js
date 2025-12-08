'use strict';

const config = require('../config/environment');
const messages = require('../utils/messages');
const userManager = require('./userManager.service');
const logger = require('../utils/logger');

const { escapeHtml, bold, code, italic } = messages._helpers;

class NotificationService {
  constructor(bot) {
    this.bot = bot;
  }

  // ============================================================================
  // 📡 NOTIFICACIONES AL ADMIN — Solicitud de acceso
  // ============================================================================

  async notifyAdminAccessRequest(user) {
    try {
      const formatted = messages.ACCESS_REQUEST_ADMIN_NOTIFICATION(user);

      await this.bot.telegram.sendMessage(config.ADMIN_ID, formatted, {
        parse_mode: 'HTML'
      });

      logger.info(`Notificación de solicitud enviada al Admin`, { user });
      return true;

    } catch (err) {
      logger.error('notifyAdminAccessRequest', err);
      return false;
    }
  }

  // ============================================================================
  // 🛑 NOTIFICACIÓN CRÍTICA — Errores del BOT
  // ============================================================================

  async notifyAdminError(errorMessage, context = {}) {
    try {
      const safeError = escapeHtml(errorMessage);
      const safeContext = code(escapeHtml(JSON.stringify(context, null, 2)));

      const msg =
        `${bold('⚠️ ERROR CRÍTICO EN EL BOT')}\n\n` +
        `${bold(safeError)}\n\n` +
        `${bold('Contexto:')}\n${safeContext}\n\n` +
        `${italic(new Date().toLocaleString())}`;

      await this.bot.telegram.sendMessage(config.ADMIN_ID, msg, {
        parse_mode: 'HTML'
      });

      logger.warn('Error crítico notificado al admin', { errorMessage, context });
      return true;

    } catch (err) {
      logger.error('notifyAdminError — fallo notificando al admin', err);
      return false;
    }
  }

  // ============================================================================
  // 🔔 NOTIFICACIÓN NO CRÍTICA — Alertas internas (jobs)
  // ============================================================================

  async notifyAdminAlert(subject, context = {}) {
    try {
      const formatted =
        `${bold('🔔 ALERTA DEL SISTEMA')}\n\n` +
        `${bold(escapeHtml(subject))}\n\n` +
        `${bold('Contexto:')}\n` +
        `${code(escapeHtml(JSON.stringify(context, null, 2)))}`;

      await this.bot.telegram.sendMessage(config.ADMIN_ID, formatted, {
        parse_mode: 'HTML'
      });

      logger.info('Alerta enviada al admin', { subject, context });
      return true;

    } catch (err) {
      logger.error('notifyAdminAlert', err);
      return false;
    }
  }

  // ============================================================================
  // 📬 MENSAJE DIRECTO A USUARIO (jobs, advertencias, avisos)
  // ============================================================================

  async sendDirectMessage(userId, messageHtml) {
    try {
      await this.bot.telegram.sendMessage(String(userId), messageHtml, {
        parse_mode: 'HTML'
      });
      logger.info('Mensaje directo enviado', { userId });
      return true;
    } catch (err) {
      logger.error('sendDirectMessage', err, { userId });
      return false;
    }
  }

  // ============================================================================
  // 📢 BROADCAST DE TEXTO — Optimizado por lotes
  // ============================================================================

  async sendBroadcast(messageHtml, recipients, options = {}) {
    const { includeHeader = true } = options;

    const finalMessage = includeHeader
      ? `${bold('📢 ANUNCIO')}\n━━━━━━━━━━━━━━━━━━━━\n\n${messageHtml}\n\n━━━━━━━━━━━━━━━━━━━━\n${italic('🤖 uSipipo VPN Bot')}`
      : messageHtml;

    const results = { success: 0, failed: 0, errors: [] };

    const BATCH_SIZE = 20;
    const DELAY = 1000;

    for (let i = 0; i < recipients.length; i += BATCH_SIZE) {
      const batch = recipients.slice(i, i + BATCH_SIZE);

      const tasks = batch.map((user) =>
        this.bot.telegram
          .sendMessage(user.id, finalMessage, { parse_mode: 'HTML' })
          .then(() => ({ ok: true }))
          .catch(err => ({
            ok: false,
            userId: user.id,
            error: err.message
          }))
      );

      const batchResults = await Promise.all(tasks);

      for (const r of batchResults) {
        if (r.ok) results.success++;
        else {
          results.failed++;
          results.errors.push({ userId: r.userId, error: r.error });
        }
      }

      if (i + BATCH_SIZE < recipients.length) {
        await new Promise(res => setTimeout(res, DELAY));
      }
    }

    logger.info('Broadcast ejecutado', results);
    return results;
  }

  // ============================================================================
  // 🖼️ BROADCAST CON FOTO — Optimizado por lotes
  // ============================================================================

  async sendBroadcastWithPhoto(messageHtml, photoUrl, recipients) {
    const results = { success: 0, failed: 0, errors: [] };

    const BATCH_SIZE = 15;
    const DELAY = 1500;

    for (let i = 0; i < recipients.length; i += BATCH_SIZE) {
      const batch = recipients.slice(i, i + BATCH_SIZE);

      const tasks = batch.map((user) =>
        this.bot.telegram
          .sendPhoto(user.id, photoUrl, {
            caption: `${bold('📢 ANUNCIO')}\n\n${messageHtml}`,
            parse_mode: 'HTML'
          })
          .then(() => ({ ok: true }))
          .catch(err => ({
            ok: false,
            userId: user.id,
            error: err.message
          }))
      );

      const batchResults = await Promise.all(tasks);

      for (const r of batchResults) {
        if (r.ok) results.success++;
        else {
          results.failed++;
          results.errors.push({ userId: r.userId, error: r.error });
        }
      }

      if (i + BATCH_SIZE < recipients.length) {
        await new Promise(res => setTimeout(res, DELAY));
      }
    }

    logger.info('Broadcast con foto ejecutado', results);
    return results;
  }

  // ============================================================================
  // 🚀 NOTIFICACIÓN DE ARRANQUE DE SISTEMA
  // ============================================================================

  async notifyAdminsSystemStartup() {
    try {
      const stats = userManager.getUserStats();
      const users = userManager.getAllUsers();

      const admins = users.filter(
        (u) => u.role === 'admin' && u.status === 'active'
      );

      const info = {
        ip: config.SERVER_IPV4,
        wgPort: config.WIREGUARD_PORT,
        outlinePort: config.OUTLINE_API_PORT
      };

      const formatted = messages.SYSTEM_STARTUP(info, stats.admins, stats.total);
      const finalMessage = `${bold('🚀 INICIO DEL SISTEMA')}\n\n${formatted}`;

      const results = { success: 0, failed: 0 };

      for (const admin of admins) {
        try {
          await this.bot.telegram.sendMessage(admin.id, finalMessage, {
            parse_mode: 'HTML'
          });
          results.success++;
        } catch (err) {
          results.failed++;
          logger.warn('notifyAdminsSystemStartup — fallo en admin', {
            admin: admin.id,
            msg: err.message
          });
        }
      }

      logger.info('Notificaciones de arranque enviadas', results);
      return results;

    } catch (err) {
      logger.error('notifyAdminsSystemStartup — error crítico', err);
      return { success: 0, failed: 0 };
    }
  }
}

module.exports = NotificationService;