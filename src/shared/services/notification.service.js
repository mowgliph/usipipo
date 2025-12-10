'use strict';

/**
 * services/notification.service.js
 *
 * Refactorizado a Markdown V1 para máxima compatibilidad y estabilidad.
 * Soluciona el error "escapeHtml is not a function".
 */

const config = require('../config/environment');
const messages = require('../utils/messages');
const userManager = require('./userManager.service');
const logger = require('../utils/logger');

class NotificationService {
  constructor(bot) {
    this.bot = bot;
  }

  // ============================================================================
  // 🛡️ HELPER: Escape Markdown V1
  // ============================================================================
  
  /**
   * Escapa caracteres reservados de Markdown V1 para evitar errores de parseo.
   * Caracteres: _ * ` [
   */
  _escapeMarkdown(text) {
    if (!text) return '';
    return String(text).replace(/([_*\[`])/g, '\\$1');
  }

  // ============================================================================
  // 📡 NOTIFICACIONES AL ADMIN — Solicitud de acceso
  // ============================================================================

  async notifyAdminAccessRequest(user) {
    try {
      // Se asume que messages.ACCESS_REQUEST_ADMIN_NOTIFICATION devuelve texto compatible
      // Si devuelve HTML, fallará. Idealmente ese método también debe devolver Markdown.
      // Aquí forzamos un formato seguro por si acaso:
      
      const safeName = this._escapeMarkdown(user.first_name || 'Sin nombre');
      const safeUsername = user.username ? `@${this._escapeMarkdown(user.username)}` : 'N/A';
      const safeId = user.id;

      const msg = `🔔 *Nueva Solicitud de Acceso*\n\n` +
                  `👤 *Usuario:* ${safeName}\n` +
                  `🔖 *Username:* ${safeUsername}\n` +
                  `🆔 *ID:* \`${safeId}\`\n\n` +
                  `_Usa /add ${safeId} para aprobar._`;

      await this.bot.telegram.sendMessage(config.ADMIN_ID, msg, {
        parse_mode: 'Markdown'
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
      const safeError = this._escapeMarkdown(errorMessage);
      // JSON stringify no necesita escape si va dentro de bloque de código, 
      // pero por seguridad escapamos backticks internos si existen.
      let jsonContext = JSON.stringify(context, null, 2);
      jsonContext = jsonContext.replace(/`/g, "'"); 

      const msg =
        `*⚠️ ERROR CRÍTICO EN EL BOT*\n\n` +
        `*Error:* ${safeError}\n\n` +
        `*Contexto:*\n\`\`\`\n${jsonContext}\n\`\`\`\n\n` +
        `_Hora: ${this._escapeMarkdown(new Date().toLocaleString())}_`;

      await this.bot.telegram.sendMessage(config.ADMIN_ID, msg, {
        parse_mode: 'Markdown'
      });

      logger.warn('Error crítico notificado al admin', { errorMessage, context });
      return true;

    } catch (err) {
      // Usamos console.error aquí para evitar bucles infinitos con el logger si este falla
      console.error('notifyAdminError — fallo notificando al admin (Backup Log)', err);
      return false;
    }
  }

  // ============================================================================
  // 🔔 NOTIFICACIÓN NO CRÍTICA — Alertas internas (jobs)
  // ============================================================================

  async notifyAdminAlert(subject, context = {}) {
    try {
      let jsonContext = JSON.stringify(context, null, 2);
      jsonContext = jsonContext.replace(/`/g, "'");

      const msg =
        `*🔔 ALERTA DEL SISTEMA*\n\n` +
        `*Asunto:* ${this._escapeMarkdown(subject)}\n\n` +
        `*Contexto:*\n\`\`\`\n${jsonContext}\n\`\`\``;

      await this.bot.telegram.sendMessage(config.ADMIN_ID, msg, {
        parse_mode: 'Markdown'
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

  async sendDirectMessage(userId, messageMarkdown) {
    try {
      await this.bot.telegram.sendMessage(String(userId), messageMarkdown, {
        parse_mode: 'Markdown'
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

  async sendBroadcast(messageMarkdown, recipients, options = {}) {
    const { includeHeader = true } = options;

    const finalMessage = includeHeader
      ? `*📢 ANUNCIO*\n━━━━━━━━━━━━━━━━━━━━\n\n${messageMarkdown}\n\n━━━━━━━━━━━━━━━━━━━━\n_🤖 uSipipo VPN Bot_`
      : messageMarkdown;

    const results = { success: 0, failed: 0, errors: [] };

    const BATCH_SIZE = 20;
    const DELAY = 1000;

    for (let i = 0; i < recipients.length; i += BATCH_SIZE) {
      const batch = recipients.slice(i, i + BATCH_SIZE);

      const tasks = batch.map((user) =>
        this.bot.telegram
          .sendMessage(user.id, finalMessage, { parse_mode: 'Markdown' })
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

  async sendBroadcastWithPhoto(messageMarkdown, photoUrl, recipients) {
    const results = { success: 0, failed: 0, errors: [] };

    const BATCH_SIZE = 15;
    const DELAY = 1500;

    for (let i = 0; i < recipients.length; i += BATCH_SIZE) {
      const batch = recipients.slice(i, i + BATCH_SIZE);

      const tasks = batch.map((user) =>
        this.bot.telegram
          .sendPhoto(user.id, photoUrl, {
            caption: `*📢 ANUNCIO*\n\n${messageMarkdown}`,
            parse_mode: 'Markdown'
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

      // Preparamos info básica
      const infoMsg = `🌐 *IP:* \`${config.SERVER_IPV4 || 'N/A'}\`\n` +
                      `🔒 *WG Port:* \`${config.WIREGUARD_PORT || 'N/A'}\`\n` +
                      `🔑 *Outline:* \`${config.OUTLINE_API_PORT || 'N/A'}\``;

      const finalMessage = `*🚀 INICIO DEL SISTEMA*\n\n` +
                           `${infoMsg}\n\n` +
                           `👥 *Usuarios:* ${stats.total}\n` +
                           `👮 *Admins:* ${stats.admins}`;

      const results = { success: 0, failed: 0 };

      for (const admin of admins) {
        try {
          await this.bot.telegram.sendMessage(admin.id, finalMessage, {
            parse_mode: 'Markdown'
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
