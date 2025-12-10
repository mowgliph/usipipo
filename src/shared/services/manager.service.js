'use strict';

const fs = require('fs').promises;
const path = require('path');
const config = require('../../config/environment');
const logger = require('../../core/utils/logger');
const markdown = require('../../core/utils/markdown');
const constants = require('../../config/constants');

/**
 * ============================================================================
 * 🧠 MANAGER SERVICE - uSipipo VPN Bot
 * ============================================================================
 * Servicio centralizado para gestión de usuarios y datos VPN.
 * Combina: datos de autenticación + datos de VPN + utilidades del sistema.
 * 
 * 🎯 OBJETIVO: Ser la fuente única de datos de usuarios para:
 *   - systemJobs.service.js
 *   - notification.service.js
 *   - Cualquier módulo que necesite datos completos de usuario
 * ============================================================================
 */

class ManagerService {
  constructor() {
    // Archivos de persistencia
    this.authFilePath = path.join(__dirname, '../../data/authorized_users.json');
    this.vpnFilePath = path.join(__dirname, '../../data/vpn_users.json');
    this.dataDir = path.join(__dirname, '../../data');
    
    // Almacenamiento en memoria
    this.authUsers = new Map();     // {userId: {id, name, role, status, ...}}
    this.vpnUsers = new Map();      // {userId: {wg: {...}, outline: {...}}}
    
    // Control de escritura secuencial
    this._saveLock = Promise.resolve();
    
    // Inicialización
    this.init();
  }

  // ============================================================================
  // 🔄 INITIALIZATION
  // ============================================================================

  async init() {
    try {
      await fs.mkdir(this.dataDir, { recursive: true });
      await this.loadAuthUsers();
      await this.loadVpnUsers();
      await this.syncWithEnv();
      
      logger.success('[ManagerService] Inicializado correctamente', {
        authUsers: this.authUsers.size,
        vpnUsers: this.vpnUsers.size
      });
    } catch (error) {
      logger.error('[ManagerService] Error en inicialización', error);
      throw error;
    }
  }

  // ============================================================================
  // 📂 LOAD / SAVE OPERATIONS
  // ============================================================================

  async loadAuthUsers() {
    try {
      const raw = await fs.readFile(this.authFilePath, 'utf8').catch(() => '{"users":{}}');
      const data = JSON.parse(raw);
      this.authUsers = new Map(Object.entries(data.users || {}));
    } catch (error) {
      logger.error('[ManagerService] Error cargando usuarios auth', error);
      this.authUsers = new Map();
    }
  }

  async loadVpnUsers() {
    try {
      const raw = await fs.readFile(this.vpnFilePath, 'utf8').catch(() => '{"users":{}}');
      const data = JSON.parse(raw);
      this.vpnUsers = new Map(Object.entries(data.users || {}));
    } catch (error) {
      logger.error('[ManagerService] Error cargando usuarios VPN', error);
      this.vpnUsers = new Map();
    }
  }

  async saveAuthUsers() {
    return this._saveOperation('auth', this.authFilePath, this.authUsers);
  }

  async saveVpnUsers() {
    return this._saveOperation('vpn', this.vpnFilePath, this.vpnUsers);
  }

  async _saveOperation(type, filePath, dataMap) {
    this._saveLock = this._saveLock.then(async () => {
      try {
        const tempPath = `${filePath}.tmp`;
        const payload = {
          users: Object.fromEntries(dataMap),
          metadata: {
            lastUpdated: new Date().toISOString(),
            totalUsers: dataMap.size,
            type
          }
        };

        await fs.writeFile(tempPath, JSON.stringify(payload, null, 2), 'utf8');
        await fs.rename(tempPath, filePath);
        
        logger.debug(`[ManagerService] ${type.toUpperCase()} users saved`, { count: dataMap.size });
        return true;
      } catch (error) {
        logger.error(`[ManagerService] Error guardando ${type} users`, error);
        return false;
      }
    });
    
    return this._saveLock;
  }

  // ============================================================================
  // 🔄 SYNC WITH ENVIRONMENT
  // ============================================================================

  async syncWithEnv() {
    const adminId = String(config.ADMIN_ID || '');
    const authorizedIds = config.AUTHORIZED_USERS || [];
    
    // Crear/actualizar admin desde ENV
    if (adminId) {
      if (!this.authUsers.has(adminId)) {
        this.authUsers.set(adminId, {
          id: adminId,
          name: 'Administrador Principal',
          addedAt: new Date().toISOString(),
          addedBy: 'system',
          status: 'active',
          role: 'admin',
          isFromEnv: true
        });
        logger.info('[ManagerService] Admin creado desde ENV', { adminId });
      }
    }

    // Sincronizar usuarios autorizados desde ENV
    for (const userId of authorizedIds) {
      const id = String(userId);
      if (!this.authUsers.has(id)) {
        this.authUsers.set(id, {
          id: id,
          name: null,
          addedAt: new Date().toISOString(),
          addedBy: 'system',
          status: 'active',
          role: 'user',
          isFromEnv: true
        });
      }
    }

    await this.saveAuthUsers();
  }

  // ============================================================================
  // 👥 USER AUTHENTICATION DATA (CRUD)
  // ============================================================================

  getAuthUser(userId) {
    const id = String(userId);
    return this.authUsers.get(id) || null;
  }

  getAllAuthUsers() {
    return Array.from(this.authUsers.values());
  }

  isUserAuthorized(userId) {
    const user = this.getAuthUser(userId);
    return !!(user && user.status === 'active');
  }

  isUserAdmin(userId) {
    const user = this.getAuthUser(userId);
    return !!(user && user.role === 'admin' && user.status === 'active');
  }

  async addAuthUser(userId, addedBy, name = null) {
    const id = String(userId);
    
    if (this.authUsers.has(id)) {
      throw new Error('Usuario ya existe');
    }

    const userData = {
      id,
      name,
      addedAt: new Date().toISOString(),
      addedBy: String(addedBy),
      status: 'active',
      role: 'user',
      isFromEnv: false
    };

    this.authUsers.set(id, userData);
    await this.saveAuthUsers();
    
    logger.info('[ManagerService] Usuario auth agregado', { userId: id, addedBy });
    return userData;
  }

  async updateUserRole(userId, role) {
    const user = this.getAuthUser(userId);
    if (!user) throw new Error('Usuario no encontrado');
    
    const validRoles = ['admin', 'user'];
    if (!validRoles.includes(role)) {
      throw new Error(`Rol inválido. Válidos: ${validRoles.join(', ')}`);
    }

    user.role = role;
    user.updatedAt = new Date().toISOString();
    
    await this.saveAuthUsers();
    logger.info('[ManagerService] Rol de usuario actualizado', { userId, role });
    return user;
  }

  // ============================================================================
  // 🔐 VPN DATA MANAGEMENT
  // ============================================================================

  getVpnUser(userId) {
    const id = String(userId);
    return this.vpnUsers.get(id) || { wg: null, outline: null };
  }

  getCompleteUser(userId) {
    const authData = this.getAuthUser(userId);
    if (!authData) return null;
    
    const vpnData = this.getVpnUser(userId);
    return {
      ...authData,
      ...vpnData
    };
  }

  async setWireGuardData(userId, wgData) {
    const id = String(userId);
    const user = this.getCompleteUser(id);
    if (!user) throw new Error('Usuario no encontrado');

    const currentVpn = this.vpnUsers.get(id) || {};
    
    this.vpnUsers.set(id, {
      ...currentVpn,
      wg: {
        clientName: wgData.clientName,
        ip: wgData.ip,
        lastSeen: wgData.lastSeen || new Date().toISOString(),
        dataReceived: wgData.dataReceived || 0,
        dataSent: wgData.dataSent || 0,
        suspended: wgData.suspended || false,
        suspendedAt: wgData.suspendedAt || null,
        updatedAt: new Date().toISOString()
      }
    });

    await this.saveVpnUsers();
    logger.debug('[ManagerService] Datos WireGuard actualizados', { userId: id });
    return this.getCompleteUser(id);
  }

  async setOutlineData(userId, outlineData) {
    const id = String(userId);
    const user = this.getCompleteUser(id);
    if (!user) throw new Error('Usuario no encontrado');

    const currentVpn = this.vpnUsers.get(id) || {};
    
    this.vpnUsers.set(id, {
      ...currentVpn,
      outline: {
        keyId: outlineData.keyId,
        name: outlineData.name || 'Sin nombre',
        accessUrl: outlineData.accessUrl,
        usedBytes: outlineData.usedBytes || 0,
        suspended: outlineData.suspended || false,
        suspendedAt: outlineData.suspendedAt || null,
        updatedAt: new Date().toISOString()
      }
    });

    await this.saveVpnUsers();
    logger.debug('[ManagerService] Datos Outline actualizados', { userId: id });
    return this.getCompleteUser(id);
  }

  async removeVpnData(userId, vpnType = 'all') {
    const id = String(userId);
    const currentVpn = this.vpnUsers.get(id);
    
    if (!currentVpn) return;

    if (vpnType === 'all') {
      this.vpnUsers.delete(id);
    } else if (vpnType === 'wg') {
      if (currentVpn.outline) {
        this.vpnUsers.set(id, { outline: currentVpn.outline });
      } else {
        this.vpnUsers.delete(id);
      }
    } else if (vpnType === 'outline') {
      if (currentVpn.wg) {
        this.vpnUsers.set(id, { wg: currentVpn.wg });
      } else {
        this.vpnUsers.delete(id);
      }
    }

    await this.saveVpnUsers();
    logger.info('[ManagerService] Datos VPN eliminados', { userId: id, vpnType });
  }

  // ============================================================================
  // 📊 STATISTICS & QUERIES
  // ============================================================================

  getAllUsers() {
    return Array.from(this.authUsers.values()).map(user => {
      const vpnData = this.vpnUsers.get(user.id) || {};
      return {
        ...user,
        ...vpnData
      };
    });
  }

  getUserStats() {
    const stats = {
      total: this.authUsers.size,
      active: 0,
      suspended: 0,
      admins: 0,
      users: 0,
      withWireGuard: 0,
      withOutline: 0,
      withBothVpn: 0
    };

    for (const [userId, authData] of this.authUsers.entries()) {
      if (authData.status === 'active') stats.active++;
      if (authData.status === 'suspended') stats.suspended++;
      if (authData.role === 'admin') stats.admins++;
      if (authData.role === 'user') stats.users++;
      
      const vpnData = this.vpnUsers.get(userId);
      if (vpnData) {
        if (vpnData.wg) stats.withWireGuard++;
        if (vpnData.outline) stats.withOutline++;
        if (vpnData.wg && vpnData.outline) stats.withBothVpn++;
      }
    }

    return stats;
  }

  getUsersWithWireGuard() {
    return this.getAllUsers().filter(user => user.wg);
  }

  getUsersWithOutline() {
    return this.getAllUsers().filter(user => user.outline);
  }

  // ============================================================================
  // 🛠️ UTILITY METHODS FOR OTHER SERVICES
  // ============================================================================

  formatUserForNotification(user) {
    const vpnData = this.vpnUsers.get(user.id) || {};
    return {
      id: user.id,
      name: user.name || 'Sin nombre',
      role: user.role,
      status: user.status,
      hasWireGuard: !!vpnData.wg,
      hasOutline: !!vpnData.outline,
      wireguard: vpnData.wg ? {
        clientName: vpnData.wg.clientName,
        ip: vpnData.wg.ip,
        suspended: vpnData.wg.suspended
      } : null,
      outline: vpnData.outline ? {
        keyId: vpnData.outline.keyId,
        name: vpnData.outline.name,
        suspended: vpnData.outline.suspended
      } : null
    };
  }

  getUsersByStatus(status = 'active') {
    return this.getAllUsers().filter(user => user.status === status);
  }

  // ============================================================================
  // 🧹 MAINTENANCE OPERATIONS
  // ============================================================================

  async cleanupOrphanedVpnData() {
    const authIds = new Set(this.authUsers.keys());
    const vpnIds = new Set(this.vpnUsers.keys());
    const orphanedIds = [...vpnIds].filter(id => !authIds.has(id));
    
    for (const id of orphanedIds) {
      this.vpnUsers.delete(id);
    }
    
    if (orphanedIds.length > 0) {
      await this.saveVpnUsers();
      logger.warn('[ManagerService] Datos VPN huérfanos eliminados', {
        count: orphanedIds.length,
        ids: orphanedIds
      });
    }
    
    return orphanedIds.length;
  }

  async exportData() {
    return {
      authUsers: Object.fromEntries(this.authUsers),
      vpnUsers: Object.fromEntries(this.vpnUsers),
      metadata: {
        exportedAt: new Date().toISOString(),
        authCount: this.authUsers.size,
        vpnCount: this.vpnUsers.size
      }
    };
  }
}

// Exportar instancia singleton
module.exports = new ManagerService();