'use strict';

/**
 * ============================================================================
 * 👑 ADMIN SERVICE - uSipipo VPN Bot
 * ============================================================================
 * Lógica de negocio para operaciones administrativas.
 * ============================================================================
 */

const managerService = require('../../../shared/services/manager.service');
const logger = require('../../../core/utils/logger');
const os = require('os');

class AdminService {
  constructor() {
    this.maintenanceMode = false;
  }

  // ============================================================================
  // 👥 USER MANAGEMENT
  // ============================================================================

  async addUser(userId, addedBy, name = null) {
    try {
      const result = await managerService.addAuthUser(userId, addedBy, name);
      logger.info('[AdminService] Usuario agregado', { userId, addedBy });
      return { success: true, user: result };
    } catch (error) {
      logger.error('[AdminService] Error agregando usuario', error, { userId });
      return { success: false, error: error.message };
    }
  }

  async removeUser(userId, removedBy) {
    try {
      // Validar que no sea el admin principal
      if (String(userId) === String(require('../../../config/environment').ADMIN_ID)) {
        throw new Error('No se puede eliminar al administrador principal');
      }

      // Validar que no se elimine a sí mismo
      if (String(userId) === String(removedBy)) {
        throw new Error('No puedes eliminarte a ti mismo');
      }

      const user = managerService.getAuthUser(userId);
      if (!user) {
        throw new Error('Usuario no encontrado');
      }

      // Eliminar datos VPN asociados
      await managerService.removeVpnData(userId, 'all');

      // Eliminar usuario de auth
      managerService.authUsers.delete(String(userId));
      await managerService.saveAuthUsers();

      logger.info('[AdminService] Usuario eliminado', { userId, removedBy });
      return { success: true };
    } catch (error) {
      logger.error('[AdminService] Error eliminando usuario', error, { userId });
      return { success: false, error: error.message };
    }
  }

  async changeUserRole(userId, newRole, changedBy) {
    try {
      const result = await managerService.updateUserRole(userId, newRole);
      logger.info('[AdminService] Rol de usuario cambiado', { userId, newRole, changedBy });
      return { success: true, user: result };
    } catch (error) {
      logger.error('[AdminService] Error cambiando rol', error, { userId, newRole });
      return { success: false, error: error.message };
    }
  }

  async getUserDetail(userId) {
    try {
      const user = managerService.getCompleteUser(userId);
      if (!user) {
        throw new Error('Usuario no encontrado');
      }
      return { success: true, user };
    } catch (error) {
      logger.error('[AdminService] Error obteniendo detalle de usuario', error, { userId });
      return { success: false, error: error.message };
    }
  }

  async listUsers(page = 1, pageSize = 10) {
    try {
      const allUsers = managerService.getAllUsers();
      const totalPages = Math.ceil(allUsers.length / pageSize);
      
      return {
        success: true,
        users: allUsers,
        page,
        pageSize,
        totalPages,
        total: allUsers.length
      };
    } catch (error) {
      logger.error('[AdminService] Error listando usuarios', error);
      return { success: false, error: error.message };
    }
  }

  async suspendUser(userId, suspendedBy) {
    try {
      const user = managerService.getAuthUser(userId);
      if (!user) {
        throw new Error('Usuario no encontrado');
      }

      user.status = 'suspended';
      user.suspendedAt = new Date().toISOString();
      user.suspendedBy = String(suspendedBy);
      
      await managerService.saveAuthUsers();
      logger.info('[AdminService] Usuario suspendido', { userId, suspendedBy });
      
      return { success: true };
    } catch (error) {
      logger.error('[AdminService] Error suspendiendo usuario', error, { userId });
      return { success: false, error: error.message };
    }
  }

  async activateUser(userId, activatedBy) {
    try {
      const user = managerService.getAuthUser(userId);
      if (!user) {
        throw new Error('Usuario no encontrado');
      }

      user.status = 'active';
      user.activatedAt = new Date().toISOString();
      user.activatedBy = String(activatedBy);
      
      await managerService.saveAuthUsers();
      logger.info('[AdminService] Usuario activado', { userId, activatedBy });
      
      return { success: true };
    } catch (error) {
      logger.error('[AdminService] Error activando usuario', error, { userId });
      return { success: false, error: error.message };
    }
  }

  // ============================================================================
  // 📊 STATISTICS
  // ============================================================================

  async getSystemStats() {
    try {
      const stats = managerService.getUserStats();
      return { success: true, stats };
    } catch (error) {
      logger.error('[AdminService] Error obteniendo estadísticas', error);
      return { success: false, error: error.message };
    }
  }

  async getSystemHealth() {
    try {
      const uptime = process.uptime();
      const uptimeFormatted = this.#formatUptime(uptime);
      
      const memUsage = process.memoryUsage();
      const memoryFormatted = `${(memUsage.heapUsed / 1024 / 1024).toFixed(2)} MB / ${(memUsage.heapTotal / 1024 / 1024).toFixed(2)} MB`;
      
      const cpuUsage = process.cpuUsage();
      const cpuFormatted = `User: ${(cpuUsage.user / 1000000).toFixed(2)}s, System: ${(cpuUsage.system / 1000000).toFixed(2)}s`;

      // Check service status (basic)
      const wireguardStatus = await this.#checkWireGuardStatus();
      const outlineStatus = await this.#checkOutlineStatus();

      const health = {
        status: 'healthy',
        uptime: uptimeFormatted,
        memory: memoryFormatted,
        cpu: cpuFormatted,
        wireguard: wireguardStatus,
        outline: outlineStatus,
        database: true, // JSON files always "available"
        timestamp: new Date().toISOString()
      };

      return { success: true, health };
    } catch (error) {
      logger.error('[AdminService] Error obteniendo salud del sistema', error);
      return { success: false, error: error.message };
    }
  }

  async getDetailedStats() {
    try {
      const stats = managerService.getUserStats();
      const users = managerService.getAllUsers();

      // VPN usage stats
      let totalWGUsage = 0;
      let totalOLUsage = 0;

      users.forEach(user => {
        if (user.wg) {
          totalWGUsage += (user.wg.dataReceived || 0) + (user.wg.dataSent || 0);
        }
        if (user.outline && user.outline.usedBytes) {
          totalOLUsage += user.outline.usedBytes;
        }
      });

      const detailed = {
        ...stats,
        vpnUsage: {
          wireguard: this.#formatBytes(totalWGUsage),
          outline: this.#formatBytes(totalOLUsage),
          total: this.#formatBytes(totalWGUsage + totalOLUsage)
        },
        system: {
          platform: os.platform(),
          arch: os.arch(),
          nodeVersion: process.version,
          totalMemory: this.#formatBytes(os.totalmem()),
          freeMemory: this.#formatBytes(os.freemem())
        }
      };

      return { success: true, stats: detailed };
    } catch (error) {
      logger.error('[AdminService] Error obteniendo estadísticas detalladas', error);
      return { success: false, error: error.message };
    }
  }

  // ============================================================================
  // 🔧 MAINTENANCE
  // ============================================================================

  async cleanupOrphanedData() {
    try {
      const count = await managerService.cleanupOrphanedVpnData();
      logger.info('[AdminService] Limpieza de datos huérfanos completada', { count });
      return { success: true, count };
    } catch (error) {
      logger.error('[AdminService] Error limpiando datos huérfanos', error);
      return { success: false, error: error.message };
    }
  }

  async getStorageStats() {
    try {
      // Get systemJobs store stats if available
      const SystemJobsService = require('../../../shared/services/systemJobs.service');
      let jobStats = null;
      
      if (global.systemJobsService && typeof global.systemJobsService.getStoreStats === 'function') {
        jobStats = global.systemJobsService.getStoreStats();
      }

      const stats = {
        users: {
          auth: managerService.authUsers.size,
          vpn: managerService.vpnUsers.size
        },
        jobs: jobStats,
        timestamp: new Date().toISOString()
      };

      return { success: true, stats };
    } catch (error) {
      logger.error('[AdminService] Error obteniendo stats de storage', error);
      return { success: false, error: error.message };
    }
  }

  async setMaintenanceMode(enabled) {
    try {
      this.maintenanceMode = enabled;
      logger.info('[AdminService] Modo mantenimiento cambiado', { enabled });
      return { success: true, enabled };
    } catch (error) {
      logger.error('[AdminService] Error cambiando modo mantenimiento', error);
      return { success: false, error: error.message };
    }
  }

  isMaintenanceMode() {
    return this.maintenanceMode;
  }

  async createBackup() {
    try {
      const backup = await managerService.exportData();
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `backup_${timestamp}.json`;
      
      // In production, save to file
      // For now, return data
      logger.info('[AdminService] Backup creado', { filename });
      
      return { 
        success: true, 
        backup, 
        filename,
        size: JSON.stringify(backup).length 
      };
    } catch (error) {
      logger.error('[AdminService] Error creando backup', error);
      return { success: false, error: error.message };
    }
  }

  // ============================================================================
  // 🔒 PRIVATE HELPERS
  // ============================================================================

  #formatUptime(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    const parts = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);

    return parts.join(' ');
  }

  #formatBytes(bytes) {
    if (!bytes || isNaN(bytes) || bytes <= 0) return '0 B';
    const k = 1024;
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    const unit = units[i] || 'TB';
    const value = (bytes / Math.pow(k, i)).toFixed(2);
    return `${value} ${unit}`;
  }

  async #checkWireGuardStatus() {
    try {
      const { exec } = require('child_process');
      const util = require('util');
      const execPromise = util.promisify(exec);
      
      await execPromise('wg show');
      return true;
    } catch (error) {
      return false;
    }
  }

  async #checkOutlineStatus() {
    try {
      const OutlineService = require('../../vpn/providers/outline.service');
      await OutlineService.getServerInfo();
      return true;
    } catch (error) {
      return false;
    }
  }
}

module.exports = new AdminService();
