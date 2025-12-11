'use strict';

/**
 * ============================================================================
 * 🔐 AUTH SERVICE - uSipipo VPN Bot
 * ============================================================================
 * Lógica de negocio para autenticación y autorización.
 * Integración con managerService para persistencia.
 * ============================================================================
 */

const managerService = require('../../../shared/services/manager.service');
const logger = require('../../../core/utils/logger');
const config = require('../../../config/environment');

class AuthService {
  
  // ============================================================================
  // 🔍 VERIFICACIÓN DE AUTORIZACIÓN
  // ============================================================================

  /**
   * Verifica si un usuario está autorizado
   */
  isUserAuthorized(userId) {
    return managerService.isUserAuthorized(userId);
  }

  /**
   * Verifica si un usuario es administrador
   */
  isUserAdmin(userId) {
    return managerService.isUserAdmin(userId);
  }

  /**
   * Obtiene información completa de autorización de un usuario
   */
  getUserAuthInfo(userId) {
    const user = managerService.getCompleteUser(userId);
    
    if (!user) {
      return {
        authorized: false,
        isAdmin: false,
        exists: false
      };
    }

    return {
      authorized: user.status === 'active',
      isAdmin: user.role === 'admin',
      exists: true,
      role: user.role,
      status: user.status,
      addedAt: user.addedAt,
      addedBy: user.addedBy
    };
  }

  // ============================================================================
  // ➕ AUTORIZACIÓN DE USUARIOS
  // ============================================================================

  /**
   * Autoriza un nuevo usuario
   */
  async authorizeUser(userId, authorizedBy, userData = {}) {
    try {
      const id = String(userId);
      const adminId = String(authorizedBy);

      // Verificar si ya está autorizado
      if (this.isUserAuthorized(id)) {
        throw new Error('Usuario ya está autorizado');
      }

      // Verificar que quien autoriza sea admin
      if (!this.isUserAdmin(adminId)) {
        throw new Error('Solo administradores pueden autorizar usuarios');
      }

      // Crear usuario autorizado
      const user = await managerService.addAuthUser(
        id,
        adminId,
        userData.name || null
      );

      logger.success('[AuthService] Usuario autorizado', {
        userId: id,
        authorizedBy: adminId,
        name: userData.name
      });

      return {
        success: true,
        user
      };

    } catch (error) {
      logger.error('[AuthService] Error al autorizar usuario', error, { userId, authorizedBy });
      throw error;
    }
  }

  /**
   * Cambia el rol de un usuario existente
   */
  async changeUserRole(userId, newRole, changedBy) {
    try {
      const id = String(userId);
      const adminId = String(changedBy);

      // Verificar permisos
      if (!this.isUserAdmin(adminId)) {
        throw new Error('Solo administradores pueden cambiar roles');
      }

      // Validar rol
      const validRoles = ['admin', 'user'];
      if (!validRoles.includes(newRole)) {
        throw new Error(`Rol inválido. Válidos: ${validRoles.join(', ')}`);
      }

      // No permitir cambiar el rol del admin principal
      if (id === String(config.ADMIN_ID) && newRole !== 'admin') {
        throw new Error('No se puede cambiar el rol del administrador principal');
      }

      const user = await managerService.updateUserRole(id, newRole);

      logger.success('[AuthService] Rol de usuario actualizado', {
        userId: id,
        newRole,
        changedBy: adminId
      });

      return {
        success: true,
        user
      };

    } catch (error) {
      logger.error('[AuthService] Error al cambiar rol', error, { userId, newRole });
      throw error;
    }
  }

  // ============================================================================
  // 📋 LISTADO Y ESTADÍSTICAS
  // ============================================================================

  /**
   * Obtiene lista de todos los usuarios autorizados
   */
  getAllAuthorizedUsers() {
    return managerService.getAllAuthUsers();
  }

  /**
   * Obtiene usuarios autorizados con paginación
   */
  getAuthorizedUsersPaginated(page = 1, pageSize = 10) {
    const allUsers = this.getAllAuthorizedUsers();
    const totalUsers = allUsers.length;
    const totalPages = Math.ceil(totalUsers / pageSize);
    
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    
    const users = allUsers.slice(startIndex, endIndex);

    return {
      users,
      pagination: {
        currentPage: page,
        totalPages,
        totalUsers,
        pageSize,
        hasNext: page < totalPages,
        hasPrev: page > 1
      }
    };
  }

  /**
   * Obtiene estadísticas de autorización
   */
  getAuthStatistics() {
    const stats = managerService.getUserStats();
    
    return {
      total: stats.total,
      active: stats.active,
      suspended: stats.suspended,
      admins: stats.admins,
      users: stats.users,
      withVPN: stats.withWireGuard + stats.withOutline - stats.withBothVpn,
      withWireGuard: stats.withWireGuard,
      withOutline: stats.withOutline,
      withBothVPN: stats.withBothVpn
    };
  }

  /**
   * Busca usuarios por término
   */
  searchUsers(searchTerm) {
    const allUsers = this.getAllAuthorizedUsers();
    const term = String(searchTerm).toLowerCase();

    return allUsers.filter(user => {
      const userName = (user.name || '').toLowerCase();
      const userId = String(user.id);
      
      return userName.includes(term) || userId.includes(term);
    });
  }

  // ============================================================================
  // 🔒 SUSPENSIÓN Y REACTIVACIÓN
  // ============================================================================

  /**
   * Suspende un usuario (no lo elimina, solo desactiva)
   */
  async suspendUser(userId, suspendedBy, reason = null) {
    try {
      const id = String(userId);
      const adminId = String(suspendedBy);

      if (!this.isUserAdmin(adminId)) {
        throw new Error('Solo administradores pueden suspender usuarios');
      }

      const user = managerService.getAuthUser(id);
      if (!user) {
        throw new Error('Usuario no encontrado');
      }

      // No permitir suspender al admin principal
      if (id === String(config.ADMIN_ID)) {
        throw new Error('No se puede suspender al administrador principal');
      }

      user.status = 'suspended';
      user.suspendedAt = new Date().toISOString();
      user.suspendedBy = adminId;
      user.suspensionReason = reason;

      await managerService.saveAuthUsers();

      logger.warn('[AuthService] Usuario suspendido', {
        userId: id,
        suspendedBy: adminId,
        reason
      });

      return {
        success: true,
        user
      };

    } catch (error) {
      logger.error('[AuthService] Error al suspender usuario', error, { userId });
      throw error;
    }
  }

  /**
   * Reactiva un usuario suspendido
   */
  async reactivateUser(userId, reactivatedBy) {
    try {
      const id = String(userId);
      const adminId = String(reactivatedBy);

      if (!this.isUserAdmin(adminId)) {
        throw new Error('Solo administradores pueden reactivar usuarios');
      }

      const user = managerService.getAuthUser(id);
      if (!user) {
        throw new Error('Usuario no encontrado');
      }

      if (user.status !== 'suspended') {
        throw new Error('El usuario no está suspendido');
      }

      user.status = 'active';
      user.reactivatedAt = new Date().toISOString();
      user.reactivatedBy = adminId;
      delete user.suspendedAt;
      delete user.suspendedBy;
      delete user.suspensionReason;

      await managerService.saveAuthUsers();

      logger.success('[AuthService] Usuario reactivado', {
        userId: id,
        reactivatedBy: adminId
      });

      return {
        success: true,
        user
      };

    } catch (error) {
      logger.error('[AuthService] Error al reactivar usuario', error, { userId });
      throw error;
    }
  }

  // ============================================================================
  // 📊 INFORMACIÓN DETALLADA
  // ============================================================================

  /**
   * Obtiene información completa de un usuario (auth + VPN)
   */
  getUserCompleteInfo(userId) {
    return managerService.getCompleteUser(userId);
  }

  /**
   * Verifica el estado de una solicitud de acceso
   */
  checkAccessRequestStatus(userId) {
    const user = managerService.getAuthUser(userId);
    
    if (!user) {
      return {
        status: 'not_requested',
        message: 'No hay registro de solicitud'
      };
    }

    if (user.status === 'active') {
      return {
        status: 'approved',
        message: 'Acceso aprobado',
        approvedAt: user.addedAt,
        approvedBy: user.addedBy
      };
    }

    if (user.status === 'suspended') {
      return {
        status: 'suspended',
        message: 'Usuario suspendido',
        suspendedAt: user.suspendedAt,
        reason: user.suspensionReason
      };
    }

    return {
      status: 'pending',
      message: 'Solicitud pendiente de revisión'
    };
  }
}

// Exportar instancia singleton
module.exports = new AuthService();
