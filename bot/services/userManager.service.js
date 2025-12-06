// services/userManager.service.js
const fs = require('fs').promises;
const path = require('path');
const config = require('../config/environment');
const logger = require('../utils/logger');

/**
 * Servicio central de gestión de usuarios autorizados.
 * Permite sincronización con .env, persistencia local (JSON)
 * y control de roles (admin / user / suspended).
 */
class UserManager {
  constructor() {
    this.usersFilePath = path.join(__dirname, '../data/authorized_users.json');
    this.users = new Map();
    this.init();
  }

  /**
   * Inicialización base con carga y sincronización de Admin.
   */
  async init() {
    await this.loadUsers();
    await this.syncAdminFromEnv();
  }

  /**
   * Sincroniza el ADMIN_ID del .env, asegurando consistencia en privilegios.
   */
  async syncAdminFromEnv() {
    const envAdminId = config.ADMIN_ID;
    if (!envAdminId) {
      logger.warn('ADMIN_ID no definido en .env — se omite sincronización de Admin');
      return;
    }

    const adminIdStr = envAdminId.toString();
    let needsSave = false;

    // Caso 1: Admin no existe
    if (!this.users.has(adminIdStr)) {
      this.users.set(adminIdStr, {
        id: adminIdStr,
        name: 'Admin Principal',
        addedAt: new Date().toISOString(),
        addedBy: 'system',
        status: 'active',
        role: 'admin'
      });
      logger.info('Admin agregado desde .env', { adminId: adminIdStr });
      needsSave = true;
    }

    // Caso 2: Admin existe pero con rol incorrecto
    const adminUser = this.users.get(adminIdStr);
    if (adminUser.role !== 'admin') {
      adminUser.role = 'admin';
      logger.info('Rol corregido a admin para usuario .env', { adminId: adminIdStr });
      needsSave = true;
    }

    // Caso 3: Revocar rol admin a otros usuarios
    for (const [userId, user] of this.users.entries()) {
      if (user.role === 'admin' && userId !== adminIdStr) {
        user.role = 'user';
        logger.warn('Revocado rol admin a usuario no autorizado', { userId });
        needsSave = true;
      }
    }

    if (needsSave) {
      await this.saveUsers();
      logger.info('Sincronización de roles administrativos completada');
    }
  }

  /**
   * Carga usuarios desde el archivo JSON local, creando estructura si no existe.
   */
  async loadUsers() {
    try {
      await fs.mkdir(path.dirname(this.usersFilePath), { recursive: true });
      const data = await fs.readFile(this.usersFilePath, 'utf8');

      const parsed = JSON.parse(data);
      this.users = new Map(Object.entries(parsed.users));

      logger.info('Usuarios autorizados cargados', { count: this.users.size });
    } catch (error) {
      if (error.code === 'ENOENT') {
        logger.warn('Archivo de usuarios no encontrado, se inicializa desde entorno');
        await this.initializeFromEnv();
      } else {
        logger.error('Error cargando archivo de usuarios', error);
        this.users = new Map();
      }
    }
  }

  /**
   * Crea un archivo inicial de usuarios desde AUTHORIZED_USERS + ADMIN_ID del entorno.
   */
  async initializeFromEnv() {
    const envUsers = config.AUTHORIZED_USERS || [];
    const adminId = config.ADMIN_ID;

    const initialData = {
      users: {},
      metadata: {
        created: new Date().toISOString(),
        lastUpdated: new Date().toISOString()
      }
    };

    if (adminId) {
      initialData.users[adminId] = {
        id: adminId,
        name: 'Admin Principal',
        addedAt: new Date().toISOString(),
        addedBy: 'system',
        status: 'active',
        role: 'admin'
      };
      this.users.set(adminId, initialData.users[adminId]);
    }

    for (const userId of envUsers) {
      if (userId !== adminId && !this.users.has(userId)) {
        const entry = {
          id: userId,
          addedAt: new Date().toISOString(),
          addedBy: 'system',
          status: 'active',
          role: 'user'
        };
        this.users.set(userId, entry);
        initialData.users[userId] = entry;
      }
    }

    await this.saveUsers(initialData);
    logger.info('Archivo de usuarios inicializado', { count: this.users.size });
  }

  /**
   * Guarda usuarios en archivo JSON.
   */
  async saveUsers(data = null) {
    try {
      const payload = data || {
        users: Object.fromEntries(this.users),
        metadata: {
          lastUpdated: new Date().toISOString(),
          totalUsers: this.users.size
        }
      };

      await fs.writeFile(this.usersFilePath, JSON.stringify(payload, null, 2), 'utf8');
      logger.info('Usuarios guardados correctamente', { count: this.users.size });
      return true;
    } catch (error) {
      logger.error('Error guardando usuarios', error);
      return false;
    }
  }

  /** ---------------- Funciones de validación ---------------- */

  /**
   * Comprueba si un usuario está autorizado y activo.
   */
  isAuthorized(userId) {
    const user = this.users.get(userId.toString());
    return !!(user && user.status === 'active');
  }

  /**
   * Comprueba si un usuario es administrador activo.
   */
  isAdmin(userId) {
    const user = this.users.get(userId.toString());
    return !!(user && user.role === 'admin' && user.status === 'active');
  }

  /** ---------------- CRUD de Usuarios ---------------- */

  async addUser(userId, addedByUserId, userName = null) {
    const userIdStr = userId.toString();

    if (this.users.has(userIdStr)) {
      throw new Error('Usuario ya existe en la lista');
    }

    const newUser = {
      id: userIdStr,
      name: userName,
      addedAt: new Date().toISOString(),
      addedBy: addedByUserId.toString(),
      status: 'active',
      role: 'user'
    };

    this.users.set(userIdStr, newUser);
    await this.saveUsers();

    logger.info('Usuario agregado', { userId: userIdStr, addedBy: addedByUserId });
    return newUser;
  }

  async removeUser(userId) {
    const userIdStr = userId.toString();

    if (!this.users.has(userIdStr)) throw new Error('Usuario no encontrado');

    const user = this.users.get(userIdStr);
    if (user.role === 'admin') throw new Error('No se puede eliminar a un administrador');

    this.users.delete(userIdStr);
    await this.saveUsers();

    logger.info('Usuario eliminado', { userId: userIdStr });
    return true;
  }

  async suspendUser(userId) {
    const userIdStr = userId.toString();
    const user = this.users.get(userIdStr);

    if (!user) throw new Error('Usuario no encontrado');

    user.status = 'suspended';
    user.suspendedAt = new Date().toISOString();

    await this.saveUsers();
    logger.warn('Usuario suspendido', { userId: userIdStr });
    return user;
  }

  async reactivateUser(userId) {
    const userIdStr = userId.toString();
    const user = this.users.get(userIdStr);

    if (!user) throw new Error('Usuario no encontrado');

    user.status = 'active';
    delete user.suspendedAt;

    await this.saveUsers();
    logger.info('Usuario reactivado', { userId: userIdStr });
    return user;
  }

  /** ---------------- Consultas agregadas ---------------- */

  getAllUsers() {
    return Array.from(this.users.values());
  }

  getUser(userId) {
    return this.users.get(userId.toString()) || null;
  }

  getUserStats() {
    const stats = {
      total: this.users.size,
      active: 0,
      suspended: 0,
      admins: 0,
      users: 0
    };

    for (const user of this.users.values()) {
      if (user.status === 'active') stats.active++;
      if (user.status === 'suspended') stats.suspended++;
      if (user.role === 'admin') stats.admins++;
      if (user.role === 'user') stats.users++;
    }

    return stats;
  }
}

module.exports = new UserManager();