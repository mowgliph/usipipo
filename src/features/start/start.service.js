'use strict';

/**
 * ============================================================================
 * 🚀 START SERVICE - uSipipo VPN Bot
 * ============================================================================
 * Lógica de negocio para el comando /start
 * Maneja registro, autorización y flujo de inicio
 * ============================================================================
 */

const managerService = require('../../shared/services/manager.service');
const notificationService = require('../../shared/services/notification.service');
const logger = require('../../core/utils/logger');

class StartService {
  constructor() {
    this.logger = logger;
  }

  /**
   * Procesa el comando /start para un usuario
   * @param {Object} user - Datos del usuario de Telegram
   * @param {Object} bot - Instancia del bot para notificaciones
   * @returns {Object} Resultado del procesamiento
   */
  async processStartCommand(user, bot) {
    const userId = String(user.id);
    const userName = user.first_name || 'Usuario';
    const username = user.username || null;

    try {
      // Verificar si el usuario ya existe en el sistema
      const existingUser = managerService.getAuthUser(userId);
      
      if (existingUser) {
        // Usuario ya registrado
        return await this.handleExistingUser(existingUser, user, bot);
      } else {
        // Nuevo usuario - proceso de registro
        return await this.handleNewUser(user, bot);
      }
    } catch (error) {
      logger.error('[StartService] Error procesando comando /start', {
        userId,
        userName,
        error: error.message,
        stack: error.stack
      });
      
      return {
        success: false,
        type: 'error',
        message: 'registration_error',
        data: { error: error.message }
      };
    }
  }

  /**
   * Maneja un usuario existente
   */
  async handleExistingUser(existingUser, telegramUser, bot) {
    const userId = String(telegramUser.id);
    const userName = telegramUser.first_name || existingUser.name || 'Usuario';
    const isAdmin = managerService.isUserAdmin(userId);
    
    // Actualizar nombre si ha cambiado
    if (userName !== existingUser.name) {
      await this.updateUserName(userId, userName);
    }

    // Crear instancia de notificación si no existe
    const notification = new notificationService(bot);

    // Enviar notificación de reinicio si está configurado
    if (process.env.NOTIFY_START === 'true') {
      await this.notifyUserRestart(userId, userName, isAdmin, notification);
    }

    return {
      success: true,
      type: existingUser.status === 'active' ? 'welcome_back' : 'pending',
      isAdmin,
      userData: {
        id: userId,
        name: userName,
        role: existingUser.role,
        status: existingUser.status,
        isFromEnv: existingUser.isFromEnv || false
      }
    };
  }

  /**
   * Maneja un nuevo usuario
   */
  async handleNewUser(telegramUser, bot) {
    const userId = String(telegramUser.id);
    const userName = telegramUser.first_name || 'Usuario';
    const username = telegramUser.username || null;

    // Verificar si el usuario está en la lista de autorizados por ENV
    const isPreAuthorized = await this.checkPreAuthorization(userId);
    
    if (isPreAuthorized) {
      // Usuario pre-autorizado por ENV
      return await this.registerPreAuthorizedUser(telegramUser, bot);
    } else {
      // Usuario no autorizado - enviar solicitud
      return await this.registerNewUserWithRequest(telegramUser, bot);
    }
  }

  /**
   * Verifica si el usuario está pre-autorizado por variables ENV
   */
  async checkPreAuthorization(userId) {
    try {
      // Obtener lista de usuarios autorizados desde ENV
      const authorizedIds = process.env.AUTHORIZED_USERS 
        ? process.env.AUTHORIZED_USERS.split(',').map(id => id.trim())
        : [];

      // Verificar si el usuario está en la lista
      return authorizedIds.includes(userId) || userId === process.env.ADMIN_ID;
    } catch (error) {
      logger.warn('[StartService] Error verificando pre-autorización', {
        userId,
        error: error.message
      });
      return false;
    }
  }

  /**
   * Registra un usuario pre-autorizado (desde ENV)
   */
  async registerPreAuthorizedUser(telegramUser, bot) {
    const userId = String(telegramUser.id);
    const userName = telegramUser.first_name || 'Usuario';
    const isAdmin = userId === process.env.ADMIN_ID;

    try {
      // Registrar usuario en el sistema
      await managerService.addAuthUser(userId, 'system', userName);
      
      // Si es admin, asegurar rol
      if (isAdmin) {
        await managerService.updateUserRole(userId, 'admin');
      }

      // Crear instancia de notificación
      const notification = new notificationService(bot);

      // Notificar al admin sobre nuevo usuario pre-autorizado
      if (!isAdmin && process.env.ADMIN_ID) {
        await notification.notifyAdminAlert('Nuevo usuario pre-autorizado', {
          userId,
          userName,
          source: 'ENV_VARIABLE',
          timestamp: new Date().toISOString()
        });
      }

      // Enviar mensaje de bienvenida al usuario
      await notification.sendWelcomeMessage(userId);

      logger.info('[StartService] Usuario pre-autorizado registrado', {
        userId,
        userName,
        isAdmin
      });

      return {
        success: true,
        type: 'welcome_authorized',
        isAdmin,
        userData: {
          id: userId,
          name: userName,
          role: isAdmin ? 'admin' : 'user',
          status: 'active',
          isFromEnv: true
        }
      };

    } catch (error) {
      logger.error('[StartService] Error registrando usuario pre-autorizado', {
        userId,
        error: error.message
      });
      
      throw error;
    }
  }

  /**
   * Registra un nuevo usuario y envía solicitud
   */
  async registerNewUserWithRequest(telegramUser, bot) {
    const userId = String(telegramUser.id);
    const userName = telegramUser.first_name || 'Usuario';
    const username = telegramUser.username || null;

    try {
      // Crear instancia de notificación
      const notification = new notificationService(bot);

      // 1. Notificar al administrador
      const adminNotified = await notification.notifyAdminAccessRequest(telegramUser);
      
      if (!adminNotified) {
        throw new Error('No se pudo notificar al administrador');
      }

      // 2. Registrar usuario como pendiente (opcional - podríamos no registrarlo hasta ser aprobado)
      // Por ahora, no lo registramos hasta que sea aprobado explícitamente
      // Esto evita acumular usuarios no autorizados en la base de datos

      // 3. Registrar la solicitud en un log separado
      await this.logAccessRequest(telegramUser);

      logger.info('[StartService] Solicitud de acceso enviada', {
        userId,
        userName,
        adminNotified
      });

      return {
        success: true,
        type: 'request_sent',
        adminNotified,
        userData: {
          id: userId,
          name: userName,
          username,
          status: 'pending',
          requestedAt: new Date().toISOString()
        }
      };

    } catch (error) {
      logger.error('[StartService] Error enviando solicitud de acceso', {
        userId,
        error: error.message
      });
      
      throw error;
    }
  }

  /**
   * Actualiza el nombre de usuario
   */
  async updateUserName(userId, newName) {
    try {
      // Nota: managerService no tiene método updateUserName directamente
      // Podríamos necesitar extenderlo o manejar esto de otra forma
      // Por ahora, solo logueamos el cambio
      logger.debug('[StartService] Nombre de usuario cambiado', {
        userId,
        oldName: managerService.getAuthUser(userId)?.name,
        newName
      });
      
      // En una implementación futura, podríamos actualizar en managerService
      return true;
    } catch (error) {
      logger.warn('[StartService] Error actualizando nombre de usuario', {
        userId,
        error: error.message
      });
      return false;
    }
  }

  /**
   * Notifica el reinicio de sesión
   */
  async notifyUserRestart(userId, userName, isAdmin, notification) {
    try {
      // Solo notificar si el usuario está activo
      const user = managerService.getAuthUser(userId);
      if (user && user.status === 'active') {
        const message = `🔄 *Sesión reiniciada*\n\n` +
                       `Hola ${userName}, has reiniciado tu sesión en el bot.\n\n` +
                       `*Rol:* ${isAdmin ? '👑 Administrador' : '👤 Usuario'}\n` +
                       `*Estado:* ${user.status === 'active' ? '✅ Activo' : '⏳ Pendiente'}\n\n` +
                       `Usa /help para ver los comandos disponibles.`;

        await notification.sendDirectMessage(userId, message);
        
        logger.debug('[StartService] Notificación de reinicio enviada', { userId });
      }
    } catch (error) {
      logger.warn('[StartService] Error enviando notificación de reinicio', {
        userId,
        error: error.message
      });
    }
  }

  /**
   * Registra solicitud de acceso en log
   */
  async logAccessRequest(user) {
    try {
      const logEntry = {
        userId: String(user.id),
        userName: user.first_name || 'Sin nombre',
        username: user.username || null,
        timestamp: new Date().toISOString(),
        action: 'access_request'
      };

      // Aquí podríamos guardar en un archivo de log específico
      // o en la base de datos. Por ahora solo logueamos.
      logger.info('[StartService] Solicitud de acceso registrada', logEntry);
      
      return true;
    } catch (error) {
      logger.error('[StartService] Error registrando solicitud de acceso', {
        userId: user?.id,
        error: error.message
      });
      return false;
    }
  }

  /**
   * Obtiene estadísticas de registro
   */
  async getRegistrationStats() {
    try {
      const allUsers = managerService.getAllAuthUsers();
      const stats = {
        total: allUsers.length,
        active: allUsers.filter(u => u.status === 'active').length,
        pending: allUsers.filter(u => u.status === 'pending').length,
        suspended: allUsers.filter(u => u.status === 'suspended').length,
        admins: allUsers.filter(u => u.role === 'admin').length,
        users: allUsers.filter(u => u.role === 'user').length,
        fromEnv: allUsers.filter(u => u.isFromEnv).length
      };

      return {
        success: true,
        stats,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      logger.error('[StartService] Error obteniendo estadísticas de registro', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Limpia solicitudes pendientes antiguas
   */
  async cleanupOldRequests(daysOld = 7) {
    try {
      // Esta funcionalidad dependería de cómo almacenamos las solicitudes pendientes
      // En la implementación actual, no almacenamos solicitudes pendientes en managerService
      // Solo logueamos para futura implementación
      logger.info('[StartService] Limpieza de solicitudes antiguas solicitada', {
        daysOld,
        note: 'Funcionalidad pendiente de implementación'
      });
      
      return {
        success: true,
        message: 'Funcionalidad pendiente de implementación',
        daysOld
      };
    } catch (error) {
      logger.error('[StartService] Error en limpieza de solicitudes', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
}

module.exports = StartService;