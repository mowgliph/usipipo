// services/userManager.service.js
const fs = require('fs').promises;
const path = require('path');

class UserManager {
  constructor() {
    this.usersFilePath = path.join(__dirname, '../data/authorized_users.json');
    this.users = new Map();
    this.loadUsers();
  }

  /**
   * Carga usuarios desde el archivo JSON
   */
  async loadUsers() {
    try {
      await fs.mkdir(path.dirname(this.usersFilePath), { recursive: true });
      
      const data = await fs.readFile(this.usersFilePath, 'utf8');
      const parsed = JSON.parse(data);
      
      this.users = new Map(Object.entries(parsed.users));
      console.log(`✅ Cargados ${this.users.size} usuarios autorizados`);
      
    } catch (error) {
      if (error.code === 'ENOENT') {
        // Archivo no existe, crear estructura inicial desde .env
        await this.initializeFromEnv();
      } else {
        console.error('❌ Error cargando usuarios:', error);
        this.users = new Map();
      }
    }
  }

  /**
   * Inicializa desde variables de entorno (primera vez)
   */
  async initializeFromEnv() {
    const envUsers = process.env.AUTHORIZED_USERS?.split(',').map(id => id.trim()) || [];
    
    const initialData = {
      users: {},
      metadata: {
        created: new Date().toISOString(),
        lastUpdated: new Date().toISOString()
      }
    };

    envUsers.forEach(userId => {
      initialData.users[userId] = {
        id: userId,
        addedAt: new Date().toISOString(),
        addedBy: 'system',
        status: 'active',
        role: userId === envUsers[0] ? 'admin' : 'user'
      };
      this.users.set(userId, initialData.users[userId]);
    });

    await this.saveUsers(initialData);
    console.log(`✅ Archivo de usuarios inicializado con ${envUsers.length} usuarios`);
  }

  /**
   * Guarda usuarios en el archivo JSON
   */
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

  /**
   * Verifica si un usuario está autorizado
   */
  isAuthorized(userId) {
    const user = this.users.get(userId.toString());
    return user && user.status === 'active';
  }

  /**
   * Verifica si un usuario es administrador
   */
  isAdmin(userId) {
    const user = this.users.get(userId.toString());
    return user && user.role === 'admin' && user.status === 'active';
  }

  /**
   * Agrega un nuevo usuario
   */
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

  /**
   * Remueve un usuario
   */
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

  /**
   * Suspende temporalmente un usuario
   */
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

  /**
   * Reactiva un usuario suspendido
   */
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

  /**
   * Lista todos los usuarios
   */
  getAllUsers() {
    return Array.from(this.users.values());
  }

  /**
   * Obtiene información de un usuario específico
   */
  getUser(userId) {
    return this.users.get(userId.toString());
  }

  /**
   * Cuenta usuarios por rol
   */
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
