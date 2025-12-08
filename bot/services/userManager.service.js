'use strict';

const fs = require('fs').promises;
const path = require('path');
const config = require('../config/environment');
const logger = require('../utils/logger');

/**
 * Servicio centralizado para la gestión de usuarios (ACL).
 * - Persistencia en JSON transaccional
 * - Sincronización automática con .env
 * - Sistema seguro con control de roles
 * - API consistente para handlers y middlewares
 */

class UserManager {
  constructor() {
    this.usersFilePath = path.join(__dirname, '../data/authorized_users.json');

    // Mapa interno — mayor performance que objeto plano
    this.users = new Map();

    // Control de guardado secuencial
    this._savePromise = Promise.resolve();

    // Inicialización
    this.init();
  }

  // ============================================================================
  // 🔵 INIT
  // ============================================================================

  async init() {
    try {
      await this.loadUsers();
      await this.syncAdminFromEnv();
      logger.info('UserManager iniciado correctamente', { total: this.users.size });
    } catch (err) {
      logger.error('Fallo al inicializar UserManager', err);
    }
  }

  // ============================================================================
  // 🔧 HELPERS
  // ============================================================================

  toStr(id) {
    return String(id).trim();
  }

  getUser(id) {
    return this.users.get(this.toStr(id)) || null;
  }

  ensureExists(id) {
    const user = this.getUser(id);
    if (!user) throw new Error('Usuario no encontrado');
    return user;
  }

  ensureNotAdmin(user) {
    if (user.role === 'admin') {
      throw new Error('No se puede modificar ni eliminar a un administrador');
    }
  }

  // ============================================================================
  // 📂 LOAD / SAVE
  // ============================================================================

  async loadUsers() {
    try {
      await fs.mkdir(path.dirname(this.usersFilePath), { recursive: true });

      const raw = await fs.readFile(this.usersFilePath, 'utf8');
      const parsed = JSON.parse(raw);

      this.users = new Map(Object.entries(parsed.users));

      logger.info('Usuarios cargados desde archivo', { count: this.users.size });

    } catch (err) {
      if (err.code === 'ENOENT') {
        logger.warn('No existe archivo de usuarios. Inicializando desde entorno...');
        await this.initializeFromEnv();
      } else {
        logger.error('Error leyendo archivo de usuarios', err);
        this.users = new Map();
      }
    }
  }

  async initializeFromEnv() {
    const data = {};
    const adminId = this.toStr(config.ADMIN_ID);
    const extraUsers = config.AUTHORIZED_USERS || [];

    // Admin principal
    if (adminId) {
      const admin = {
        id: adminId,
        name: 'Admin Principal',
        addedAt: new Date().toISOString(),
        addedBy: 'system',
        status: 'active',
        role: 'admin'
      };

      this.users.set(adminId, admin);
      data[adminId] = admin;
    }

    // Usuarios extra del .env
    for (const u of extraUsers) {
      const id = this.toStr(u);
      if (id !== adminId && !this.users.has(id)) {
        const entry = {
          id,
          name: null,
          addedAt: new Date().toISOString(),
          addedBy: 'system',
          status: 'active',
          role: 'user'
        };
        this.users.set(id, entry);
        data[id] = entry;
      }
    }

    await this.saveUsers({ users: data });
    logger.info('Usuarios inicializados desde ENV', { count: this.users.size });
  }

  async saveUsers(data = null) {
    this._savePromise = this._savePromise.then(async () => {
      try {
        const payload = data || {
          users: Object.fromEntries(this.users),
          metadata: {
            lastUpdated: new Date().toISOString(),
            totalUsers: this.users.size
          }
        };

        const tmp = `${this.usersFilePath}.tmp`;

        await fs.writeFile(tmp, JSON.stringify(payload, null, 2), 'utf8');
        await fs.rename(tmp, this.usersFilePath);

        logger.debug('Estado de usuarios persistido', { count: this.users.size });

        return true;

      } catch (err) {
        logger.error('Error guardando usuarios', err);
        return false;
      }
    });

    return this._savePromise;
  }

  // ============================================================================
  // 👑 ADMIN SYNC
  // ============================================================================

  async syncAdminFromEnv() {
    const envAdminId = this.toStr(config.ADMIN_ID);
    if (!envAdminId) return;

    let changed = false;

    // Crear admin si no existe
    if (!this.users.has(envAdminId)) {
      this.users.set(envAdminId, {
        id: envAdminId,
        name: 'Admin Principal',
        addedAt: new Date().toISOString(),
        addedBy: 'system',
        status: 'active',
        role: 'admin'
      });

      logger.info('Admin creado automáticamente desde ENV');
      changed = true;
    }

    // Forzar rol admin
    const admin = this.users.get(envAdminId);
    if (admin.role !== 'admin') {
      admin.role = 'admin';
      changed = true;
      logger.warn('Corregido rol admin para ADMIN_ID');
    }

    // Revocar admins no autorizados
    for (const [id, user] of this.users.entries()) {
      if (id !== envAdminId && user.role === 'admin') {
        user.role = 'user';
        changed = true;
        logger.warn('Revocado rol admin no autorizado', { id });
      }
    }

    if (changed) await this.saveUsers();
  }

  // ============================================================================
  // 🔐 AUTH
  // ============================================================================

  isAuthorized(id) {
    const u = this.getUser(id);
    return !!(u && u.status === 'active');
  }

  isAdmin(id) {
    const u = this.getUser(id);
    return !!(u && u.role === 'admin' && u.status === 'active');
  }

  // ============================================================================
  // ✏️ CRUD
  // ============================================================================

  async addUser(userId, addedBy, name = null) {
    const id = this.toStr(userId);

    if (this.users.has(id)) {
      throw new Error('Usuario ya registrado');
    }

    const entry = {
      id,
      name,
      addedAt: new Date().toISOString(),
      addedBy: this.toStr(addedBy),
      status: 'active',
      role: 'user'
    };

    this.users.set(id, entry);
    await this.saveUsers();

    logger.info('Usuario agregado correctamente', { id, addedBy });
    return entry;
  }

  async removeUser(userId) {
    const user = this.ensureExists(userId);
    this.ensureNotAdmin(user);

    this.users.delete(this.toStr(userId));
    await this.saveUsers();

    logger.warn('Usuario eliminado', { userId });
    return true;
  }

  async suspendUser(userId) {
    const user = this.ensureExists(userId);

    user.status = 'suspended';
    user.suspendedAt = new Date().toISOString();

    await this.saveUsers();

    logger.warn('Usuario suspendido', { userId });
    return user;
  }

  async reactivateUser(userId) {
    const user = this.ensureExists(userId);

    user.status = 'active';
    delete user.suspendedAt;

    await this.saveUsers();

    logger.info('Usuario reactivado', { userId });
    return user;
  }

  // ============================================================================
  // 📊 STATS
  // ============================================================================

  getAllUsers() {
    return Array.from(this.users.values());
  }

  getUserStats() {
    const stats = {
      total: this.users.size,
      active: 0,
      suspended: 0,
      admins: 0,
      users: 0
    };

    for (const u of this.users.values()) {
      if (u.status === 'active') stats.active++;
      if (u.status === 'suspended') stats.suspended++;
      if (u.role === 'admin') stats.admins++;
      if (u.role === 'user') stats.users++;
    }

    return stats;
  }
}

module.exports = new UserManager();