'use strict';

/**
 * ============================================================================
 * 🔧 VPN SERVICE - uSipipo VPN Bot
 * ============================================================================
 * Servicio de lógica de negocio para VPN.
 * Orquesta las operaciones entre WireGuard y Outline providers.
 * 
 * 🎯 RESPONSABILIDADES:
 * - Validación de operaciones VPN
 * - Orquestación de providers
 * - Gestión de cuotas y límites
 * - Generación de reportes
 * ============================================================================
 */

const WireGuardService = require('./providers/wireguard.service');
const OutlineService = require('./providers/outline.service');
const managerService = require('../../shared/services/manager.service');
const logger = require('../../core/utils/logger');
const { formatBytes } = require('../../core/utils/formatters');
const config = require('../../config/environment');

class VPNService {
  constructor() {
    this.wgService = new WireGuardService();
    this.outlineService = new OutlineService();
    
    // Límites por defecto (pueden ser sobrescritos por ENV)
    this.limits = {
      wireguard: parseInt(process.env.WG_DATA_LIMIT_BYTES) || (10 * 1024 * 1024 * 1024),
      outline: parseInt(process.env.OUTLINE_DATA_LIMIT_BYTES) || (10 * 1024 * 1024 * 1024),
      maxConnectionsPerUser: parseInt(process.env.MAX_VPN_CONNECTIONS_PER_USER) || 2
    };
  }

  // ============================================================================
  // 🔍 MÉTODOS DE VALIDACIÓN
  // ============================================================================

  /**
   * Valida la salud de los servicios VPN
   */
  async validateServices() {
    const results = {
      wireguard: { healthy: false, error: null },
      outline: { healthy: false, error: null },
      timestamp: new Date().toISOString()
    };

    // Validar WireGuard
    try {
      await this.wgService.validateEnvironment();
      results.wireguard.healthy = true;
    } catch (error) {
      results.wireguard.error = error.message;
      logger.warn('[VPNService] WireGuard no disponible', { error: error.message });
    }

    // Validar Outline
    try {
      const outlineHealth = await this.outlineService.validateEnvironment();
      results.outline.healthy = outlineHealth.healthy;
    } catch (error) {
      results.outline.error = error.message;
      logger.warn('[VPNService] Outline no disponible', { error: error.message });
    }

    const allHealthy = results.wireguard.healthy && results.outline.healthy;
    
    if (!allHealthy) {
      logger.warn('[VPNService] Algunos servicios VPN no están disponibles', results);
    }

    return results;
  }

  /**
   * Verifica si un usuario puede crear una conexión VPN
   */
  async canUserCreateVPN(userId, vpnType) {
    const user = managerService.getCompleteUser(userId);
    
    if (!user) {
      return { 
        allowed: false, 
        reason: 'Usuario no encontrado en el sistema' 
      };
    }

    if (!user.status || user.status !== 'active') {
      return { 
        allowed: false, 
        reason: 'Usuario no está activo' 
      };
    }

    // Verificar si ya tiene conexión del tipo solicitado
    if (vpnType === 'wireguard' && user.wg && user.wg.clientName && !user.wg.suspended) {
      return { 
        allowed: false, 
        reason: 'Ya tienes una configuración WireGuard activa' 
      };
    }

    if (vpnType === 'outline' && user.outline && user.outline.keyId && !user.outline.suspended) {
      return { 
        allowed: false, 
        reason: 'Ya tienes una clave Outline activa' 
      };
    }

    // Verificar límite de conexiones totales
    const activeConnections = this._countActiveConnections(user);
    if (activeConnections >= this.limits.maxConnectionsPerUser) {
      return { 
        allowed: false, 
        reason: `Máximo de ${this.limits.maxConnectionsPerUser} conexiones simultáneas alcanzado` 
      };
    }

    return { allowed: true };
  }

  /**
   * Cuenta conexiones activas de un usuario
   */
  _countActiveConnections(user) {
    let count = 0;
    
    if (user.wg && user.wg.clientName && !user.wg.suspended) count++;
    if (user.outline && user.outline.keyId && !user.outline.suspended) count++;
    
    return count;
  }

  // ============================================================================
  // 📊 MÉTODOS DE CONSULTA Y REPORTES
  // ============================================================================

  /**
   * Obtiene el estado completo de VPN de un usuario
   */
  async getUserVPNStatus(userId) {
    const user = managerService.getCompleteUser(userId);
    
    if (!user) {
      throw new Error('Usuario no encontrado');
    }

    const status = {
      userId,
      hasWireGuard: false,
      hasOutline: false,
      wireguard: null,
      outline: null,
      totalConnections: 0,
      totalDataUsed: 0,
      timestamp: new Date().toISOString()
    };

    // Obtener estado de WireGuard
    if (user.wg && user.wg.clientName) {
      try {
        const wgData = await this.wgService.getClient(userId);
        status.hasWireGuard = true;
        status.wireguard = wgData;
        
        if (wgData.stats) {
          status.totalDataUsed += wgData.stats.total || 0;
        }
        
        status.totalConnections++;
      } catch (error) {
        logger.error('[VPNService] Error obteniendo estado WireGuard', {
          userId,
          error: error.message
        });
        status.wireguard = { error: error.message, suspended: user.wg.suspended };
      }
    }

    // Obtener estado de Outline
    if (user.outline && user.outline.keyId) {
      try {
        const outlineData = await this.outlineService.getKey(userId);
        status.hasOutline = true;
        status.outline = outlineData;
        
        if (outlineData.metrics) {
          status.totalDataUsed += outlineData.metrics.bytesUsed || 0;
        }
        
        status.totalConnections++;
      } catch (error) {
        logger.error('[VPNService] Error obteniendo estado Outline', {
          userId,
          error: error.message
        });
        status.outline = { error: error.message, suspended: user.outline.suspended };
      }
    }

    status.totalDataUsedHuman = formatBytes(status.totalDataUsed);

    return status;
  }

  /**
   * Genera un reporte consolidado de todas las conexiones VPN
   */
  async getVPNReport() {
    try {
      const [wgStats, outlineStats, serviceHealth] = await Promise.all([
        this.wgService.getAllClientsStats().catch(() => ({})),
        this.outlineService.getAllKeysStats().catch(() => ({})),
        this.validateServices()
      ]);

      const users = managerService.getAllUsers();

      const report = {
        timestamp: new Date().toISOString(),
        services: serviceHealth,
        summary: {
          totalUsers: users.length,
          activeWireGuardClients: Object.keys(wgStats).length,
          activeOutlineKeys: Object.keys(outlineStats).length,
          totalConnections: Object.keys(wgStats).length + Object.keys(outlineStats).length
        },
        quotaStatus: {
          wireguard: await this.wgService.checkAllQuotas().catch(() => ({ 
            totalClients: 0, 
            quotaExceeded: 0 
          })),
          outline: await this.outlineService.checkAllQuotas().catch(() => ({ 
            totalKeys: 0, 
            quotaExceeded: 0 
          }))
        },
        users: []
      };

      // Compilar datos por usuario
      for (const user of users) {
        const userReport = {
          userId: user.id,
          name: user.name || 'Sin nombre',
          wireguard: wgStats[user.id] || null,
          outline: outlineStats[user.id] || null
        };

        // Calcular uso total
        let totalUsage = 0;
        if (userReport.wireguard) {
          totalUsage += userReport.wireguard.total || 0;
        }
        if (userReport.outline) {
          totalUsage += userReport.outline.bytesUsed || 0;
        }

        userReport.totalDataUsage = totalUsage;
        userReport.totalDataUsageHuman = formatBytes(totalUsage);

        report.users.push(userReport);
      }

      logger.info('[VPNService] Reporte VPN generado', {
        totalUsers: report.summary.totalUsers,
        totalConnections: report.summary.totalConnections
      });

      return report;
    } catch (error) {
      logger.error('[VPNService] Error generando reporte VPN', error);
      throw new Error(`Error generando reporte: ${error.message}`);
    }
  }

  /**
   * Obtiene estadísticas agregadas del sistema VPN
   */
  async getSystemStats() {
    try {
      const report = await this.getVPNReport();

      const stats = {
        services: report.services,
        connections: {
          total: report.summary.totalConnections,
          wireguard: report.summary.activeWireGuardClients,
          outline: report.summary.activeOutlineKeys
        },
        quotas: {
          wireguard: {
            limit: this.limits.wireguard,
            limitHuman: formatBytes(this.limits.wireguard),
            exceeded: report.quotaStatus.wireguard.quotaExceeded || 0
          },
          outline: {
            limit: this.limits.outline,
            limitHuman: formatBytes(this.limits.outline),
            exceeded: report.quotaStatus.outline.quotaExceeded || 0
          }
        },
        usage: {
          totalData: report.users.reduce((sum, u) => sum + u.totalDataUsage, 0),
          averagePerUser: report.users.length > 0 
            ? report.users.reduce((sum, u) => sum + u.totalDataUsage, 0) / report.users.length 
            : 0
        },
        timestamp: new Date().toISOString()
      };

      stats.usage.totalDataHuman = formatBytes(stats.usage.totalData);
      stats.usage.averagePerUserHuman = formatBytes(stats.usage.averagePerUser);

      return stats;
    } catch (error) {
      logger.error('[VPNService] Error obteniendo estadísticas del sistema', error);
      throw error;
    }
  }

  // ============================================================================
  // 🔧 MÉTODOS DE GESTIÓN (ORCHESTRATION)
  // ============================================================================

  /**
   * Crea una conexión VPN (WireGuard o Outline)
   */
  async createVPN(userId, vpnType, options = {}) {
    // Validar permiso
    const validation = await this.canUserCreateVPN(userId, vpnType);
    if (!validation.allowed) {
      throw new Error(validation.reason);
    }

    try {
      if (vpnType === 'wireguard') {
        logger.info('[VPNService] Creando cliente WireGuard', { userId });
        return await this.wgService.createClient(userId, options);
      } else if (vpnType === 'outline') {
        logger.info('[VPNService] Creando clave Outline', { userId });
        return await this.outlineService.createKey(userId, options);
      } else {
        throw new Error(`Tipo de VPN no válido: ${vpnType}`);
      }
    } catch (error) {
      logger.error('[VPNService] Error creando VPN', {
        userId,
        vpnType,
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Elimina una conexión VPN
   */
  async deleteVPN(userId, vpnType) {
    try {
      if (vpnType === 'wireguard') {
        logger.info('[VPNService] Eliminando cliente WireGuard', { userId });
        return await this.wgService.deleteClient(userId);
      } else if (vpnType === 'outline') {
        logger.info('[VPNService] Eliminando clave Outline', { userId });
        return await this.outlineService.deleteKey(userId);
      } else {
        throw new Error(`Tipo de VPN no válido: ${vpnType}`);
      }
    } catch (error) {
      logger.error('[VPNService] Error eliminando VPN', {
        userId,
        vpnType,
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Suspende una conexión VPN
   */
  async suspendVPN(userId, vpnType, reason = 'Suspensión manual') {
    try {
      if (vpnType === 'wireguard') {
        logger.warn('[VPNService] Suspendiendo cliente WireGuard', { userId, reason });
        return await this.wgService.suspendClient(userId, reason);
      } else if (vpnType === 'outline') {
        logger.warn('[VPNService] Suspendiendo clave Outline', { userId, reason });
        return await this.outlineService.suspendKey(userId, reason);
      } else {
        throw new Error(`Tipo de VPN no válido: ${vpnType}`);
      }
    } catch (error) {
      logger.error('[VPNService] Error suspendiendo VPN', {
        userId,
        vpnType,
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Reanuda una conexión VPN suspendida
   */
  async resumeVPN(userId, vpnType) {
    try {
      if (vpnType === 'wireguard') {
        logger.info('[VPNService] Reanudando cliente WireGuard', { userId });
        return await this.wgService.resumeClient(userId);
      } else if (vpnType === 'outline') {
        logger.info('[VPNService] Reanudando clave Outline', { userId });
        return await this.outlineService.resumeKey(userId);
      } else {
        throw new Error(`Tipo de VPN no válido: ${vpnType}`);
      }
    } catch (error) {
      logger.error('[VPNService] Error reanudando VPN', {
        userId,
        vpnType,
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Limpia conexiones huérfanas (sin usuario asociado)
   */
  async cleanupOrphanedConnections() {
    const results = {
      wireguard: { cleaned: 0, errors: 0 },
      outline: { cleaned: 0, errors: 0 },
      timestamp: new Date().toISOString()
    };

    // Limpiar claves Outline huérfanas
    try {
      const outlineCleanup = await this.outlineService.cleanupOrphanedKeys();
      results.outline.cleaned = outlineCleanup.deleted || 0;
      results.outline.errors = outlineCleanup.errors || 0;
    } catch (error) {
      logger.error('[VPNService] Error limpiando claves Outline huérfanas', error);
      results.outline.errors++;
    }

    // TODO: Implementar limpieza de clientes WireGuard huérfanos si es necesario
    // (WireGuard no tiene API para listar, hay que parsear el dump)

    logger.info('[VPNService] Limpieza de conexiones huérfanas completada', results);
    return results;
  }

  // ============================================================================
  // 🛠️ MÉTODOS DE UTILIDAD
  // ============================================================================

  /**
   * Obtiene información del servidor VPN
   */
  async getServerInfo() {
    return {
      wireguard: await this.wgService.getServerInfo().catch(err => ({ error: err.message })),
      outline: await this.outlineService.getServerInfo().catch(err => ({ error: err.message })),
      limits: {
        wireguard: {
          dataLimit: this.limits.wireguard,
          dataLimitHuman: formatBytes(this.limits.wireguard)
        },
        outline: {
          dataLimit: this.limits.outline,
          dataLimitHuman: formatBytes(this.limits.outline)
        },
        maxConnectionsPerUser: this.limits.maxConnectionsPerUser
      },
      config: {
        serverIp: config.SERVER_IP,
        wireguardPort: config.WG_SERVER_PORT,
        outlinePort: config.OUTLINE_KEYS_PORT
      }
    };
  }
}

// Exportar instancia singleton
module.exports = new VPNService();
