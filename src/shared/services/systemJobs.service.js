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

const WireGuardService = require('../../features/vpn/providers/wireguard.service');
const OutlineService = require('../../features/vpn/providers/outline.service');
const managerService = require('./manager.service');
const logger = require('../../core/utils/logger');
const markdown = require('../../core/utils/markdown');

// UI Helpers del bot
const messages = require('../messages/common.messages.js');

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

    // Protection against concurrent executions
    this.isRunningWG = false;
    this.isRunningOutline = false;
  }

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  async initialize() {
    await this.#loadStore();

    // Cleanup old entries on startup
    await this.cleanupOldEntries();

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
      await this.#migrateStore();
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
  // MIGRATION & CLEANUP
  // ============================================================================

  async #migrateStore() {
    // Migration logic if store format changes
    if (!this.store.meta) {
      this.store.meta = { lastRun: null };
      logger.info('[SystemJobs] Migrated store to include meta');
    }
    // Add more migrations as needed
  }

  async cleanupOldEntries(daysOld = 30) {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - daysOld);
    const cutoffISO = cutoff.toISOString();

    let cleanedWG = 0;
    let cleanedOutline = 0;

    // Clean WG entries
    for (const [clientName, entry] of Object.entries(this.store.wg)) {
      if (entry.lastUpdated && entry.lastUpdated < cutoffISO) {
        delete this.store.wg[clientName];
        cleanedWG++;
      }
    }

    // Clean Outline entries
    for (const [keyId, entry] of Object.entries(this.store.outline)) {
      if (entry.lastUpdated && entry.lastUpdated < cutoffISO) {
        delete this.store.outline[keyId];
        cleanedOutline++;
      }
    }

    if (cleanedWG > 0 || cleanedOutline > 0) {
      await this.#saveStore();
      logger.info('[SystemJobs] Limpieza de entradas antiguas completada', {
        wgEntriesRemoved: cleanedWG,
        outlineEntriesRemoved: cleanedOutline,
        daysOld
      });
    }

    return { wg: cleanedWG, outline: cleanedOutline };
  }

  getStoreStats() {
    const wgCount = Object.keys(this.store.wg).length;
    const outlineCount = Object.keys(this.store.outline).length;
    const totalEntries = wgCount + outlineCount;

    let totalUsageWG = 0;
    let totalUsageOutline = 0;

    for (const entry of Object.values(this.store.wg)) {
      totalUsageWG += entry.cumulative || 0;
    }

    for (const entry of Object.values(this.store.outline)) {
      totalUsageOutline += entry.cumulative || 0;
    }

    return {
      wg: {
        entries: wgCount,
        totalUsage: totalUsageWG,
        averageUsage: wgCount > 0 ? totalUsageWG / wgCount : 0
      },
      outline: {
        entries: outlineCount,
        totalUsage: totalUsageOutline,
        averageUsage: outlineCount > 0 ? totalUsageOutline / outlineCount : 0
      },
      total: {
        entries: totalEntries,
        totalUsage: totalUsageWG + totalUsageOutline
      },
      meta: this.store.meta
    };
  }

  // ============================================================================
  // WIREGUARD QUOTA MONITOR
  // ============================================================================

  async runWireGuardJob() {
    if (this.isRunningWG) {
      logger.warn('[SystemJobs] WireGuard job ya está ejecutándose, saltando');
      return;
    }
    this.isRunningWG = true;

    try {
      logger.info('[SystemJobs] Ejecutando WireGuard quota-job');
      await this.#loadStore();

      const users = managerService.getAllUsers();

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
        entry.lastUpdated = new Date().toISOString();

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
    } finally {
      this.isRunningWG = false;
    }
  }

  async #suspendWireGuardClient(user, entry) {
    const userId = user.id;
    const clientName = user.wg.clientName;

    try {
      await WireGuardService.deleteClient(userId);

      const wgData = { ...user.wg, suspended: true, suspendedAt: new Date().toISOString() };
      await managerService.setWireGuardData(userId, wgData);

      // Notificar usuario
      await this.notificationService.sendDirectMessage(
        userId,
        messages.getQuotaExceededWG({
          clientName,
          usedBytes: entry.cumulative,
          limitBytes: this.limits.wireguard
        })
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
    if (this.isRunningOutline) {
      logger.warn('[SystemJobs] Outline job ya está ejecutándose, saltando');
      return;
    }
    this.isRunningOutline = true;

    try {
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
        entry.lastUpdated = new Date().toISOString();
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
    } finally {
      this.isRunningOutline = false;
    }
  }

  async #suspendOutlineKey(entry, key) {
    try {
      await OutlineService.deleteKey(key.id);

      // Reflejar en managerService
      const u = managerService.getCompleteUser(String(entry.userId));
      if (u && u.outline && u.outline.keyId === key.id) {
        const outlineData = { ...u.outline, suspended: true, suspendedAt: new Date().toISOString() };
        await managerService.setOutlineData(entry.userId, outlineData);
      }

      // Notificar usuario
      await this.notificationService.sendDirectMessage(
        entry.userId,
        messages.getQuotaExceededOutline({
          keyName: key.name,
          usedBytes: entry.cumulative,
          limitBytes: this.limits.outline
        })
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