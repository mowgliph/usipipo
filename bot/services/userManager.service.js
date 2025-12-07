// services/userManager.service.js
const fs = require('fs').promises;
const path = require('path');
const config = require('../config/environment');
const logger = require('../utils/logger');

class UserManager {
  constructor() {
    this.usersFilePath = path.join(__dirname, '../data/authorized_users.json');
    this.users = new Map();
    this._savePromise = Promise.resolve();

    this.init();
  }

  // ------------------------------------------------------
  // INIT
  // ------------------------------------------------------
  async init() {
    await this.loadUsers();
    await this.syncAdminFromEnv();
  }

  // ------------------------------------------------------
  // HELPERS
  // ------------------------------------------------------
  toStr(id) {
    return String(id);
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
    if (user.role === 'admin') throw new Error('No se puede eliminar/modificar a un administrador');
  }

  // ------------------------------------------------------
  // LOAD / SAVE
  // ------------------------------------------------------
  async loadUsers() {
    try {
      await fs.mkdir(path.dirname(this.usersFilePath), { recursive: true });
      const raw = await fs.readFile(this.usersFilePath, 'utf8');
      const parsed = JSON.parse(raw);

      this.users = new Map(Object.entries(parsed.users));
      logger.info('Usuarios cargados', { count: this.users.size });
    } catch (err) {
      if (err.code === 'ENOENT') {
        logger.warn('Sin archivo de usuarios, inicializando desde entorno');
        await this.initializeFromEnv();
      } else {
        logger.error('Error cargando usuarios', err);
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
      data[adminId] = {
        id: adminId,
        name: 'Admin Principal',
        addedAt: new Date().toISOString(),
        addedBy: 'system',
        status: 'active',
        role: 'admin'
      };
      this.users.set(adminId, data[adminId]);
    }

    // Usuarios adicionales
    for (const u of extraUsers) {
      const id = this.toStr(u);
      if (id !== adminId && !this.users.has(id)) {
        const entry = {
          id,
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
    logger.info('Usuarios inicializados desde entorno', { count: this.users.size });
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

        logger.info('Usuarios guardados', { count: this.users.size });
        return true;
      } catch (err) {
        logger.error('Error guardando usuarios', err);
        return false;
      }
    });

    return this._savePromise;
  }

  // ------------------------------------------------------
  // ADMIN SYNC
  // ------------------------------------------------------
  async syncAdminFromEnv() {
    const envAdminId = this.toStr(config.ADMIN_ID);
    if (!envAdminId) return;

    let changed = false;

    // Garantizar que admin exista
    if (!this.users.has(envAdminId)) {
      this.users.set(envAdminId, {
        id: envAdminId,
        name: 'Admin Principal',
        addedAt: new Date().toISOString(),
        addedBy: 'system',
        status: 'active',
        role: 'admin'
      });
      changed = true;
      logger.info('Admin creado desde ENV');
    }

    // Forzar rol admin en este usuario
    const admin = this.users.get(envAdminId);
    if (admin.role !== 'admin') {
      admin.role = 'admin';
      changed = true;
      logger.info('Rol admin corregido para ADMIN_ID');
    }

    // Revocar roles admin a cualquier otro
    for (const [id, user] of this.users.entries()) {
      if (id !== envAdminId && user.role === 'admin') {
        user.role = 'user';
        changed = true;
        logger.warn('Revocado rol admin no autorizado', { id });
      }
    }

    if (changed) await this.saveUsers();
  }

  // ------------------------------------------------------
  // AUTH
  // ------------------------------------------------------
  isAuthorized(id) {
    const u = this.getUser(id);
    return !!(u && u.status === 'active');
  }

  isAdmin(id) {
    const u = this.getUser(id);
    return !!(u && u.role === 'admin' && u.status === 'active');
  }

  // ------------------------------------------------------
  // CRUD
  // ------------------------------------------------------
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

    logger.info('Usuario agregado', { id, addedBy });
    return entry;
  }

  async removeUser(userId) {
    const user = this.ensureExists(userId);
    this.ensureNotAdmin(user);

    this.users.delete(this.toStr(userId));
    await this.saveUsers();

    logger.info('Usuario eliminado', { userId });
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

  // ------------------------------------------------------
  // STATS
  // ------------------------------------------------------
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