'use strict';

/**
 * systemJobs.service.js (Versión Final — Arquitectura PRO)
 *
 * ✔ Control de cuota WireGuard y Outline
 * ✔ Suspende SOLO el servicio afectado (no el usuario completo)
 * ✔ Persistencia acumulativa en ./data/usage_store.json
 * ✔ Notifica al usuario con mensajes profesionales
 * ✔ Notifica al admin con contexto detallado
 * ✔ Manejo de errores aislados (evita caída del job)
 */

const fs = require('fs').promises;
const path = require('path');

const WireGuardService = require('./wireguard.service');
const OutlineService = require('./outline.service');
const userManager = require('./userManager.service');
const logger = require('../utils/logger');

// UI Helpers del bot
const messages = require('../utils/messages');

const DATA_DIR = path.join(__dirname, '..', 'data');
const STORE_FILE = path.join(DATA_DIR, 'usage_store.json');

class SystemJobsService {
  constructor(notificationService) {
    this.notificationService = notificationService;

    this.intervalMinutes = parseInt(
      process.env.QUOTA_CHECK_INTERVAL || '10',
      10
    );

    this.limits = {
      wireguard:
        parseInt(
          process.env.WG_DATA_LIMIT_BYTES ||
            String(10 * 1024 * 1024 * 1024),
          10
        ),
      outline:
        parseInt(
          process.env.OUTLINE_DATA_LIMIT_BYTES ||
            String(10 * 1024 * 1024 * 1024),
          10
        )
    };

    this.store = { wg: {}, outline: {}, meta: { lastRun: null } };
  }

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  async initialize() {
    await this.#loadStore();

    // Ejecutar inmediatamente
    this.runWireGuardJob();
    this.runOutlineJob();

    // Iniciar intervalos
    setInterval(
      () => this.runWireGuardJob(),
      this.intervalMinutes * 60 * 1000
    );

    setInterval(
      () => this.runOutlineJob(),
      this.intervalMinutes * 60 * 1000
    );

    logger.success('[SystemJobs] Inicializado correctamente', {
      WG_Limit_GB: (this.limits.wireguard / 1024 / 1024 / 1024).toFixed(2),
      Outline_Limit_GB: (this.limits.outline / 1024 / 1024 / 1024).toFixed(2)
    });
  }

  // ============================================================================
  // INTERNAL STORE
  // ============================================================================

  async #loadStore() {
    try {
      await fs.mkdir(DATA_DIR, { recursive: true });
      const raw = await fs.readFile(STORE_FILE, 'utf8').catch(() => null);
      this.store = raw ? JSON.parse(raw) : { wg: {}, outline: {}, meta: {} };
    } catch (err) {
      logger.error('[SystemJobs] Error cargando store', err);
      this.store = { wg: {}, outline: {}, meta: {} };
    }
  }

  async #saveStore() {
    try {
      await fs.writeFile(
        STORE_FILE + '.tmp',
        JSON.stringify(this.store, null, 2),
        'utf8'
      );
      await fs.rename(STORE_FILE + '.tmp', STORE_FILE);
    } catch (err) {
      logger.error('[SystemJobs] Error guardando store', err);
    }
  }

  // ============================================================================
  // WIREGUARD QUOTA MONITOR
  // ============================================================================

  async runWireGuardJob() {
    logger.info('[SystemJobs] Ejecutando WireGuard quota-job');
    await this.#loadStore();

    const users = userManager.getAllUsers();

    for (const user of users) {
      const userId = String(user.id);
      const wg = user.wg;
      if (!wg || !wg.clientName) continue;

      const clientName = wg.clientName;

      try {
        const usage = await WireGuardService.getClientUsage(userId);
        const current = usage.totalBytes;

        // Inicializar en store
        if (!this.store.wg[clientName]) {
          this.store.wg[clientName] = {
            last: current,
            cumulative: 0,
            userId
          };
          await this.#saveStore();
          continue;
        }

        // Calcular delta
        const entry = this.store.wg[clientName];
        let delta = current - entry.last;
        if (delta < 0) delta = current; // reinicio del server

        entry.cumulative += delta;
        entry.last = current;

        await this.#saveStore();

        // Verificar límite
        if (entry.cumulative >= this.limits.wireguard) {
          await this.#suspendWireGuardClient(user, entry);
        }
      } catch (err) {
        logger.warn('[SystemJobs] WG error por usuario', {
          userId,
          err: err.message
        });
      }
    }

    this.store.meta.lastRun = new Date().toISOString();
    await this.#saveStore();
  }

  async #suspendWireGuardClient(user, entry) {
    const userId = user.id;
    const clientName = user.wg.clientName;

    try {
      await WireGuardService.deleteClient(userId);

      user.wg.suspended = true;
      user.wg.suspendedAt = new Date().toISOString();
      await userManager.saveUsers();

      // Notificar usuario
      await this.notificationService.sendDirectMessage(
        userId,
        messages.QUOTA_WG_EXCEEDED(clientName)
      );

      // Notificar admin
      await this.notificationService.notifyAdminError(
        `WireGuard suspendido por cuota`,
        {
          userId,
          clientName,
          usedBytes: entry.cumulative
        }
      );

      logger.warn('[SystemJobs] WG suspendido por cuota', {
        userId,
        clientName
      });
    } catch (err) {
      logger.error('[SystemJobs] Error suspendiendo WG', err);
    }
  }

  // ============================================================================
  // OUTLINE QUOTA MONITOR
  // ============================================================================

  async runOutlineJob() {
    logger.info('[SystemJobs] Ejecutando Outline quota-job');
    await this.#loadStore();

    let keys = [];
    try {
      keys = await OutlineService.listAccessKeys();
    } catch (err) {
      logger.error('[SystemJobs] No se pudo obtener claves Outline', err);
      return;
    }

    for (const key of keys) {
      const keyId = key.id;
      const used = Number(key.usedBytes || 0);
      const userId = key.userId;

      try {
        if (!this.store.outline[keyId]) {
          this.store.outline[keyId] = {
            last: used,
            cumulative: 0,
            userId
          };
          await this.#saveStore();
          continue;
        }

        const entry = this.store.outline[keyId];

        let delta = used - entry.last;
        if (delta < 0) delta = used;

        entry.cumulative += delta;
        entry.last = used;
        await this.#saveStore();

        if (entry.cumulative >= this.limits.outline) {
          await this.#suspendOutlineKey(entry, key);
        }
      } catch (err) {
        logger.error('[SystemJobs] Error procesando key Outline', err);
      }
    }

    this.store.meta.lastRun = new Date().toISOString();
    await this.#saveStore();
  }

  async #suspendOutlineKey(entry, key) {
    try {
      await OutlineService.deleteKey(key.id);

      // Reflejar en userManager
      const u = userManager.getUser(String(entry.userId));
      if (u && u.outline && u.outline.keyId === key.id) {
        u.outline.suspended = true;
        u.outline.suspendedAt = new Date().toISOString();
        await userManager.saveUsers();
      }

      // Notificar usuario
      await this.notificationService.sendDirectMessage(
        entry.userId,
        messages.QUOTA_OUTLINE_EXCEEDED(key.name)
      );

      // Notificar admin
      await this.notificationService.notifyAdminError(
        `Clave Outline suspendida por cuota`,
        {
          keyId: key.id,
          userId: entry.userId,
          usedBytes: entry.cumulative
        }
      );

      logger.warn('[SystemJobs] Clave Outline suspendida', {
        userId: entry.userId,
        keyId: key.id
      });
    } catch (err) {
      logger.error('[SystemJobs] Error suspendiendo Outline key', err);
    }
  }
}

module.exports = SystemJobsService;