'use strict';

const managerService = require('../../core/data/manager.service');
const logger = require('../../core/utils/logger');

class StartService {
  
  /**
   * Procesa la entrada de un usuario en /start
   * Determina su rol y estado actual.
   * @param {Object} telegramUser - Objeto user de Telegram (ctx.from)
   * @returns {Promise<Object>} Resultado con tipo de usuario y datos
   */
  async processUserEntry(telegramUser) {
    const userId = String(telegramUser.id);
    
    // 1. Sincronización proactiva con ENV (por si se añadió manualmente al .env y reinició)
    // Esto asegura que si está en el .env, el manager lo sepa antes de responder.
    await managerService.syncWithEnv();

    // 2. Obtener datos completos
    const user = managerService.getAuthUser(userId);
    const isAdmin = managerService.isUserAdmin(userId);

    // 3. Determinar estado
    if (isAdmin) {
      return { type: 'ADMIN', user };
    }

    if (user && user.status === 'active') {
      return { type: 'AUTHORIZED', user };
    }

    if (user && user.status === 'suspended') {
      return { type: 'SUSPENDED', user };
    }

    // 4. Si no existe, es un invitado (Guest)
    return { type: 'GUEST', user: telegramUser };
  }
}

module.exports = new StartService();
