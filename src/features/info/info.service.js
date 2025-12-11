'use strict';

/**
 * ============================================================================
 * 📊 INFO SERVICE - uSipipo VPN Bot
 * ============================================================================
 * Lógica de negocio para información del sistema, estadísticas y documentación
 * ============================================================================
 */

const os = require('os');
const config = require('../../config/environment');
const managerService = require('../../shared/services/manager.service');
const logger = require('../../core/utils/logger');
const { formatBytes, formatTimestamp } = require('../../core/utils/formatters');

class InfoService {
  // ============================================================================
  // 📊 ESTADÍSTICAS DEL SISTEMA
  // ============================================================================

  /**
   * Obtiene estadísticas completas del sistema
   */
  getSystemStats() {
    try {
      const userStats = managerService.getUserStats();
      const systemInfo = this.getSystemInfo();

      return {
        users: userStats,
        system: systemInfo,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      logger.error('[InfoService] Error obteniendo estadísticas', error);
      throw error;
    }
  }

  /**
   * Información del sistema operativo y recursos
   */
  getSystemInfo() {
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;
    const memUsagePercent = ((usedMem / totalMem) * 100).toFixed(2);

    const uptime = process.uptime();
    const days = Math.floor(uptime / 86400);
    const hours = Math.floor((uptime % 86400) / 3600);
    const minutes = Math.floor((uptime % 3600) / 60);

    return {
      platform: os.platform(),
      arch: os.arch(),
      nodeVersion: process.version,
      cpuCount: os.cpus().length,
      cpuModel: os.cpus()[0]?.model || 'Unknown',
      totalMemory: formatBytes(totalMem),
      freeMemory: formatBytes(freeMem),
      usedMemory: formatBytes(usedMem),
      memoryUsagePercent: memUsagePercent,
      uptime: {
        days,
        hours,
        minutes,
        formatted: `${days}d ${hours}h ${minutes}m`
      },
      hostname: os.hostname(),
      processId: process.pid
    };
  }

  // ============================================================================
  // 🌐 INFORMACIÓN DEL SERVIDOR VPN
  // ============================================================================

  /**
   * Información completa del servidor VPN
   */
  getServerInfo() {
    return {
      general: {
        ipv4: config.SERVER_IPV4,
        ipv6: config.SERVER_IPV6 || null,
        hostname: config.SERVER_IP
      },
      wireguard: {
        interface: config.WG_INTERFACE,
        serverIpv4: config.WG_SERVER_IPV4,
        serverIpv6: config.WG_SERVER_IPV6 || null,
        port: config.WG_SERVER_PORT,
        endpoint: config.WG_ENDPOINT,
        allowedIps: config.WG_ALLOWED_IPS,
        publicKey: config.WG_SERVER_PUBKEY
      },
      outline: {
        apiUrl: config.OUTLINE_API_URL,
        apiPort: config.OUTLINE_API_PORT,
        keysPort: config.OUTLINE_KEYS_PORT,
        serverIp: config.OUTLINE_SERVER_IP,
        dashboardUrl: config.OUTLINE_DASHBOARD_URL
      },
      pihole: config.PIHOLE_DNS ? {
        dns: config.PIHOLE_DNS,
        webPort: config.PIHOLE_WEB_PORT
      } : null
    };
  }

  /**
   * Obtiene la configuración de red actual
   */
  getNetworkConfig() {
    const interfaces = os.networkInterfaces();
    const activeInterfaces = {};

    for (const [name, addresses] of Object.entries(interfaces)) {
      const ipv4 = addresses.find(addr => addr.family === 'IPv4' && !addr.internal);
      const ipv6 = addresses.find(addr => addr.family === 'IPv6' && !addr.internal);

      if (ipv4 || ipv6) {
        activeInterfaces[name] = {
          ipv4: ipv4?.address || null,
          ipv6: ipv6?.address || null,
          mac: ipv4?.mac || ipv6?.mac || null
        };
      }
    }

    return {
      interfaces: activeInterfaces,
      hostname: os.hostname()
    };
  }

  // ============================================================================
  // 📈 ESTADÍSTICAS DE USO
  // ============================================================================

  /**
   * Estadísticas de uso de VPN por usuarios
   */
  getVPNUsageStats() {
    const users = managerService.getAllUsers();

    const stats = {
      totalUsers: users.length,
      activeWireGuard: 0,
      activeOutline: 0,
      suspendedWireGuard: 0,
      suspendedOutline: 0,
      totalDataWG: 0,
      totalDataOutline: 0,
      averageDataWG: 0,
      averageDataOutline: 0
    };

    users.forEach(user => {
      if (user.wg) {
        if (user.wg.suspended) {
          stats.suspendedWireGuard++;
        } else {
          stats.activeWireGuard++;
        }
        const dataReceived = parseInt(user.wg.dataReceived) || 0;
        const dataSent = parseInt(user.wg.dataSent) || 0;
        stats.totalDataWG += dataReceived + dataSent;
      }

      if (user.outline) {
        if (user.outline.suspended) {
          stats.suspendedOutline++;
        } else {
          stats.activeOutline++;
        }
        stats.totalDataOutline += parseInt(user.outline.usedBytes) || 0;
      }
    });

    // Calcular promedios
    if (stats.activeWireGuard > 0) {
      stats.averageDataWG = stats.totalDataWG / stats.activeWireGuard;
    }
    if (stats.activeOutline > 0) {
      stats.averageDataOutline = stats.totalDataOutline / stats.activeOutline;
    }

    return stats;
  }

  // ============================================================================
  // 📋 INFORMACIÓN FORMATEADA PARA USUARIO
  // ============================================================================

  /**
   * Formatea estadísticas del sistema para mostrar al usuario
   */
  formatSystemStatsForUser() {
    const stats = this.getSystemStats();
    const vpnStats = this.getVPNUsageStats();

    return {
      users: {
        total: stats.users.total,
        active: stats.users.active,
        suspended: stats.users.suspended,
        admins: stats.users.admins
      },
      vpn: {
        wireguard: {
          active: vpnStats.activeWireGuard,
          suspended: vpnStats.suspendedWireGuard,
          totalData: formatBytes(vpnStats.totalDataWG),
          averageData: formatBytes(vpnStats.averageDataWG)
        },
        outline: {
          active: vpnStats.activeOutline,
          suspended: vpnStats.suspendedOutline,
          totalData: formatBytes(vpnStats.totalDataOutline),
          averageData: formatBytes(vpnStats.averageDataOutline)
        }
      },
      system: {
        uptime: stats.system.uptime.formatted,
        cpuCount: stats.system.cpuCount,
        memoryUsage: `${stats.system.memoryUsagePercent}%`,
        freeMemory: stats.system.freeMemory
      }
    };
  }

  /**
   * Información técnica detallada (solo para admins)
   */
  getDetailedSystemInfo() {
    return {
      system: this.getSystemInfo(),
      server: this.getServerInfo(),
      network: this.getNetworkConfig(),
      stats: this.getSystemStats(),
      vpnUsage: this.getVPNUsageStats()
    };
  }

  // ============================================================================
  // 🔍 VERIFICACIONES DE SALUD DEL SISTEMA
  // ============================================================================

  /**
   * Verifica el estado de salud del sistema
   */
  async checkSystemHealth() {
    const health = {
      status: 'healthy',
      checks: {
        memory: true,
        disk: true,
        services: true
      },
      warnings: [],
      errors: []
    };

    try {
      // Verificar memoria
      const freeMem = os.freemem();
      const totalMem = os.totalmem();
      const memUsagePercent = ((totalMem - freeMem) / totalMem) * 100;

      if (memUsagePercent > 90) {
        health.checks.memory = false;
        health.errors.push('Uso de memoria crítico (>90%)');
        health.status = 'critical';
      } else if (memUsagePercent > 80) {
        health.warnings.push('Uso de memoria alto (>80%)');
        health.status = 'warning';
      }

      // Verificar servicios (datos de usuario)
      const userCount = managerService.getUserStats().total;
      if (userCount === 0) {
        health.warnings.push('No hay usuarios registrados');
      }

      logger.info('[InfoService] Health check completado', health);
      return health;

    } catch (error) {
      logger.error('[InfoService] Error en health check', error);
      health.status = 'error';
      health.checks.services = false;
      health.errors.push('Error al verificar servicios');
      return health;
    }
  }

  // ============================================================================
  // 📅 INFORMACIÓN DE VERSIÓN Y ACTUALIZACIONES
  // ============================================================================

  /**
   * Información de la versión actual del bot
   */
  getVersionInfo() {
    return {
      version: '2.0.0',
      releaseDate: '2025-12-11',
      environment: config.NODE_ENV,
      nodeVersion: process.version,
      features: [
        'Gestión de WireGuard',
        'Gestión de Outline',
        'Control de cuotas automático',
        'Sistema de notificaciones',
        'Panel de administración',
        'Logging estructurado',
        'Persistencia de datos'
      ]
    };
  }
}

// Exportar instancia singleton
module.exports = new InfoService();
