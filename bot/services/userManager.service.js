// services/userManager.service.js
const fs = require('fs').promises;
const path = require('path');
const config = require('../config/environment');

class UserManager {
  constructor() {
    this.usersFilePath = path.join(__dirname, '../data/authorized_users.json');
    this.users = new Map();
    this.init();
  }

  /**
   * Inicialización con sincronización de Admin
   */
  async init() {
    await this.loadUsers();
    await this.syncAdminFromEnv(); // ← NUEVO
  }

  /**
   * Sincroniza el Admin ID desde .env (siempre tiene prioridad)
   */
  async syncAdminFromEnv() {
    const envAdminId = config.ADMIN_ID;
    
    if (!envAdminId) {
      console.warn('⚠️ ADMIN_ID no definido en .env');
      return;
    }

    const adminIdStr = envAdminId.toString();
    let needsSave = false;

    // Caso 1: El admin del .env no está en la lista
    if (!this.users.has(adminIdStr)) {
      console.log(`📌 Agregando Admin desde .env: ${adminIdStr}`);
      this.users.set(adminIdStr, {
        id: adminIdStr,
        name: 'Admin Principal',
        addedAt: new Date().toISOString(),
        addedBy: 'system',
        status: 'active',
        role: 'admin'
      });
      needsSave = true;
    }

    // Caso 2: El admin existe pero no tiene rol admin
    const adminUser = this.users.get(adminIdStr);
    if (adminUser.role !== 'admin') {
      console.log(`🔧 Promoviendo usuario ${adminIdStr} a Admin`);
      adminUser.role = 'admin';
      needsSave = true;
    }

    // Caso 3: Revocar admin a usuarios que ya no están en ADMIN_ID
    for (const [userId, user] of this.users.entries()) {
      if (user.role === 'admin' && userId !== adminIdStr) {
        console.log(`⬇️ Removiendo rol admin de ${userId}`);
        user.role = 'user';
        needsSave = true;
      }
    }

    if (needsSave) {
      await this.saveUsers();
      console.log('✅ Roles de administrador sincronizados con .env');
    }
  }

  async loadUsers() {
    try {
      await fs.mkdir(path.dirname(this.usersFilePath), { recursive: true });
      
      const data = await fs.readFile(this.usersFilePath, 'utf8');
      const parsed = JSON.parse(data);
      
      this.users = new Map(Object.entries(parsed.users));
      console.log(`✅ Cargados ${this.users.size} usuarios autorizados`);
      
    } catch (error) {
      if (error.code === 'ENOENT') {
        await this.initializeFromEnv();
      } else {
        console.error('❌ Error cargando usuarios:', error);
        this.users = new Map();
      }
    }
  }

  async initializeFromEnv() {
    const envUsers = process.env.AUTHORIZED_USERS?.split(',').map(id => id.trim()) || [];
    const adminId = config.ADMIN_ID;
    
    const initialData = {
      users: {},
      metadata: {
        created: new Date().toISOString(),
        lastUpdated: new Date().toISOString()
      }
    };

    // Agregar admin primero
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

    // Agregar resto de usuarios
    envUsers.forEach(userId => {
      if (userId !== adminId && !this.users.has(userId)) {
        initialData.users[userId] = {
          id: userId,
          addedAt: new Date().toISOString(),
          addedBy: 'system',
          status: 'active',
          role: 'user'
        };
        this.users.set(userId, initialData.users[userId]);
      }
    });

    await this.saveUsers(initialData);
    console.log(`✅ Archivo de usuarios inicializado con ${this.users.size} usuarios`);
  }

  async saveUsers(data = null) {
    try {
      const toSave = data || {
        users: Object.fromEntries(this.users),
        metadata: {
          lastUpdated: new Date().toISOString(),
          totalUsers: this.users.size
        }
      };

      await fs.writeFile(
        this.usersFilePath, 
        JSON.stringify(toSave, null, 2),
        'utf8'
      );
      
      console.log('💾 Usuarios guardados exitosamente');
      return true;
      
    } catch (error) {
      console.error('❌ Error guardando usuarios:', error);
      return false;
    }
  }

  isAuthorized(userId) {
    const user = this.users.get(userId.toString());
    return user && user.status === 'active';
  }

  isAdmin(userId) {
    const user = this.users.get(userId.toString());
    return user && user.role === 'admin' && user.status === 'active';
  }

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
    
    console.log(`✅ Usuario ${userIdStr} agregado por ${addedByUserId}`);
    return newUser;
  }

  async removeUser(userId) {
    const userIdStr = userId.toString();
    
    if (!this.users.has(userIdStr)) {
      throw new Error('Usuario no encontrado');
    }

    const user = this.users.get(userIdStr);
    if (user.role === 'admin') {
      throw new Error('No se puede remover a un administrador');
    }

    this.users.delete(userIdStr);
    await this.saveUsers();
    
    console.log(`🗑️ Usuario ${userIdStr} removido`);
    return true;
  }

  async suspendUser(userId) {
    const userIdStr = userId.toString();
    const user = this.users.get(userIdStr);
    
    if (!user) {
      throw new Error('Usuario no encontrado');
    }

    user.status = 'suspended';
    user.suspendedAt = new Date().toISOString();
    
    await this.saveUsers();
    console.log(`⏸️ Usuario ${userIdStr} suspendido`);
    return user;
  }

  async reactivateUser(userId) {
    const userIdStr = userId.toString();
    const user = this.users.get(userIdStr);
    
    if (!user) {
      throw new Error('Usuario no encontrado');
    }

    user.status = 'active';
    delete user.suspendedAt;
    
    await this.saveUsers();
    console.log(`▶️ Usuario ${userIdStr} reactivado`);
    return user;
  }

  getAllUsers() {
    return Array.from(this.users.values());
  }

  getUser(userId) {
    return this.users.get(userId.toString());
  }

  getUserStats() {
    const stats = {
      total: this.users.size,
      active: 0,
      suspended: 0,
      admins: 0,
      users: 0
    };

    this.users.forEach(user => {
      if (user.status === 'active') stats.active++;
      if (user.status === 'suspended') stats.suspended++;
      if (user.role === 'admin') stats.admins++;
      if (user.role === 'user') stats.users++;
    });

    return stats;
  }
}

// Exportar instancia única (Singleton)
module.exports = new UserManager();
