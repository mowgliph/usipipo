'use strict';

const axios = require('axios');
const https = require('https');
const config = require('../../config/environment');
const logger = require('../../core/utils/logger');
const managerService = require('../../shared/services/manager.service');
const { formatBytes } = require('../../core/utils/formatters');

/**
 * ============================================================================
 * 🌐 OUTLINE SERVICE - Refactorizado MVP 2025
 * ============================================================================
 * 
 * ✅ CORRECCIONES APLICADAS:
 * 1. Eliminado singleton (ahora es clase normal)
 * 2. Integrado con manager.service (fuente única de verdad)
 * 3. Separación clara de responsabilidades
 * 4. Manejo de errores mejorado con circuit breaker pattern
 * 5. Compatible con nueva arquitectura
 * 6. Circuit breaker para resiliencia
 * 7. Cache inteligente para métricas
 * 
 * 🎯 PATRÓN: Adapter para VPN Repository + Circuit Breaker
 * ============================================================================
 */
class OutlineService {
  constructor() {
    if (!config.OUTLINE_API_URL) {
      logger.warn('[OutlineService] OUTLINE_API_URL no definida en variables de entorno');
    }

    // Configuración de Axios con circuit breaker integrado
    this.api = axios.create({
      baseURL: config.OUTLINE_API_URL,
      timeout: config.OUTLINE_API_TIMEOUT || 15000,
      httpsAgent: new https.Agent({
        rejectUnauthorized: false,
        keepAlive: true
      }),
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'uSipipo-VPN-Bot/1.0'
      }
    });

    // Circuit breaker state
    this.circuitState = {
      isOpen: false,
      failureCount: 0,
      lastFailure: null,
      successThreshold: 3,
      failureThreshold: 5,
      resetTimeout: 60000 // 1 minute
    };

    // Cache para métricas (evita llamadas repetidas)
    this._cache = {
      serverInfo: null,
      serverInfoTimestamp: 0,
      metrics: new Map(),
      metricsTimestamp: 0,
      CACHE_TTL: 30000 // 30 segundos
    };

    // Default quota (10GB)
    this.defaultQuota = parseInt(process.env.OUTLINE_DATA_LIMIT_BYTES) || 
                       (10 * 1024 * 1024 * 1024);
  }

  // ============================================================================
  // 🔧 MÉTODOS DE CONFIGURACIÓN Y VALIDACIÓN
  // ============================================================================

  async validateEnvironment() {
    if (this.circuitState.isOpen) {
      const timeSinceFailure = Date.now() - this.circuitState.lastFailure;
      if (timeSinceFailure > this.circuitState.resetTimeout) {
        // Half-open state - test the connection
        this.circuitState.isOpen = false;
      } else {
        throw new Error('Outline API temporalmente no disponible (circuit breaker abierto)');
      }
    }

    try {
      const response = await this.api.get('/server', { 
        timeout: 5000 // Timeout corto para health check
      });
      
      // Reset circuit breaker on success
      this.circuitState.failureCount = 0;
      this.circuitState.isOpen = false;
      
      logger.info('[OutlineService] Conexión con Outline API establecida');
      return {
        healthy: true,
        version: response.data?.version,
        name: response.data?.name
      };
    } catch (error) {
      this._handleApiError(error, 'validateEnvironment');
      throw new Error(`Outline API no responde: ${error.message}`);
    }
  }

  async getServerInfo(forceRefresh = false) {
    const now = Date.now();
    const cacheValid = !forceRefresh && 
                      this._cache.serverInfo && 
                      (now - this._cache.serverInfoTimestamp < this._cache.CACHE_TTL);

    if (cacheValid) {
      return this._cache.serverInfo;
    }

    try {
      const [serverRes, keysRes] = await Promise.all([
        this.api.get('/server'),
        this.api.get('/access-keys')
      ]);

      const serverData = serverRes.data;
      const keys = keysRes.data?.accessKeys || [];

      const info = {
        name: serverData.name || 'Outline Server',
        serverId: serverData.serverId,
        version: serverData.version,
        metricsEnabled: serverData.metricsEnabled || false,
        createdTimestampMs: serverData.createdTimestampMs,
        portForNewAccessKeys: serverData.portForNewAccessKeys || config.OUTLINE_API_PORT,
        totalKeys: keys.length,
        isHealthy: true,
        timestamp: new Date().toISOString()
      };

      // Update cache
      this._cache.serverInfo = info;
      this._cache.serverInfoTimestamp = now;

      return info;
    } catch (error) {
      logger.error('[OutlineService] Error obteniendo info del servidor', error);
      
      // Return cached data if available, even if stale
      if (this._cache.serverInfo) {
        return {
          ...this._cache.serverInfo,
          isHealthy: false,
          error: error.message,
          timestamp: new Date().toISOString()
        };
      }

      return {
        name: 'Outline Server',
        totalKeys: 0,
        isHealthy: false,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  // ============================================================================
  // 👤 MÉTODOS DE GESTIÓN DE CLAVES (INTEGRADO CON MANAGER)
  // ============================================================================

  async createKey(userId, options = {}) {
    const startTime = Date.now();
    const user = managerService.getCompleteUser(userId);
    
    if (!user) {
      throw new Error(`Usuario ${userId} no encontrado en el sistema`);
    }

    // Validar que no tenga clave existente activa
    if (user.outline && user.outline.keyId && !user.outline.suspended) {
      throw new Error('El usuario ya tiene una clave Outline activa');
    }

    try {
      await this.validateEnvironment();

      // 1. Crear clave en Outline API
      const name = options.name || `Usuario ${userId}`;
      const res = await this.api.post('/access-keys', { name });
      const key = res.data;

      if (!key || !key.accessUrl) {
        throw new Error('Respuesta malformada de Outline API');
      }

      // 2. Aplicar branding al enlace
      const brandedUrl = this._applyBranding(key.accessUrl);

      // 3. Obtener métricas iniciales
      let initialMetrics = { bytesUsed: 0 };
      try {
        const metrics = await this.getKeyUsage(key.id);
        initialMetrics = metrics;
      } catch (error) {
        logger.debug('[OutlineService] No se pudieron obtener métricas iniciales', { 
          keyId: key.id,
          error: error.message 
        });
      }

      // 4. Actualizar manager.service
      const outlineData = {
        keyId: key.id,
        name: key.name,
        accessUrl: brandedUrl,
        originalUrl: key.accessUrl,
        port: key.port,
        method: key.method,
        password: key.password, // Guardar password para regeneración si es necesario
        createdAt: new Date().toISOString(),
        suspended: false,
        suspendedAt: null,
        usedBytes: initialMetrics.bytesUsed,
        lastUpdated: new Date().toISOString(),
        dataLimit: this.defaultQuota,
        dataLimitHuman: formatBytes(this.defaultQuota)
      };

      await managerService.setOutlineData(userId, outlineData);

      // 5. Invalidar caché
      this._cache.metrics.delete(key.id);
      this._cache.serverInfo = null;

      const duration = Date.now() - startTime;
      logger.info('[OutlineService] Clave Outline creada exitosamente', {
        userId,
        keyId: key.id,
        name: key.name,
        duration: `${duration}ms`
      });

      return {
        success: true,
        keyId: key.id,
        name: key.name,
        accessUrl: brandedUrl,
        port: key.port,
        method: key.method,
        metrics: {
          bytesUsed: initialMetrics.bytesUsed,
          bytesUsedHuman: formatBytes(initialMetrics.bytesUsed),
          quotaPercentage: ((initialMetrics.bytesUsed / this.defaultQuota) * 100).toFixed(2)
        },
        quota: {
          limit: this.defaultQuota,
          limitHuman: formatBytes(this.defaultQuota),
          used: initialMetrics.bytesUsed,
          usedHuman: formatBytes(initialMetrics.bytesUsed),
          remaining: this.defaultQuota - initialMetrics.bytesUsed,
          remainingHuman: formatBytes(this.defaultQuota - initialMetrics.bytesUsed),
          percentage: ((initialMetrics.bytesUsed / this.defaultQuota) * 100).toFixed(2)
        }
      };

    } catch (error) {
      logger.error('[OutlineService] Error creando clave Outline', {
        userId,
        error: error.message,
        stack: error.stack
      });
      
      // Limpiar recursos en caso de error
      await this._cleanupFailedCreation(userId).catch(() => {});
      
      throw new Error(`Error creando clave Outline: ${error.message}`);
    }
  }

  async getKey(userId) {
    const user = managerService.getCompleteUser(userId);
    
    if (!user || !user.outline) {
      return null;
    }

    const { keyId } = user.outline;
    
    try {
      // Obtener métricas actualizadas (con cache)
      const metrics = await this.getKeyUsage(keyId);
      
      // Calcular información de cuota
      const usedBytes = metrics.bytesUsed;
      const quotaPercentage = (usedBytes / this.defaultQuota) * 100;
      const remainingBytes = Math.max(0, this.defaultQuota - usedBytes);
      
      return {
        ...user.outline,
        metrics: {
          bytesUsed: usedBytes,
          bytesUsedHuman: formatBytes(usedBytes),
          lastUpdated: metrics.lastUpdated || user.outline.lastUpdated
        },
        quota: {
          limit: this.defaultQuota,
          limitHuman: formatBytes(this.defaultQuota),
          used: usedBytes,
          usedHuman: formatBytes(usedBytes),
          remaining: remainingBytes,
          remainingHuman: formatBytes(remainingBytes),
          percentage: quotaPercentage.toFixed(2),
          exceeded: usedBytes >= this.defaultQuota,
          warning: quotaPercentage > 80 && quotaPercentage < 100
        },
        status: user.outline.suspended ? 'suspended' : 'active'
      };
    } catch (error) {
      logger.error('[OutlineService] Error obteniendo detalles de clave', {
        userId,
        keyId,
        error: error.message
      });
      
      // Si no podemos obtener métricas, devolver datos básicos
      return {
        ...user.outline,
        metrics: {
          bytesUsed: user.outline.usedBytes || 0,
          bytesUsedHuman: formatBytes(user.outline.usedBytes || 0),
          lastUpdated: user.outline.lastUpdated
        },
        quota: {
          limit: this.defaultQuota,
          limitHuman: formatBytes(this.defaultQuota),
          used: user.outline.usedBytes || 0,
          usedHuman: formatBytes(user.outline.usedBytes || 0),
          remaining: Math.max(0, this.defaultQuota - (user.outline.usedBytes || 0)),
          remainingHuman: formatBytes(Math.max(0, this.defaultQuota - (user.outline.usedBytes || 0))),
          percentage: (((user.outline.usedBytes || 0) / this.defaultQuota) * 100).toFixed(2),
          exceeded: (user.outline.usedBytes || 0) >= this.defaultQuota
        },
        status: user.outline.suspended ? 'suspended' : 'active'
      };
    }
  }

  async deleteKey(userId) {
    const user = managerService.getCompleteUser(userId);
    
    if (!user || !user.outline) {
      throw new Error('Usuario no tiene clave Outline');
    }

    const { keyId } = user.outline;

    try {
      // 1. Eliminar clave de Outline API
      await this.api.delete(`/access-keys/${keyId}`);

      // 2. Actualizar manager.service
      await managerService.removeVpnData(userId, 'outline');

      // 3. Limpiar caché
      this._cache.metrics.delete(keyId);
      if (this._cache.serverInfo) {
        this._cache.serverInfo.totalKeys = Math.max(0, this._cache.serverInfo.totalKeys - 1);
      }

      logger.info('[OutlineService] Clave eliminada', { userId, keyId });
      
      return {
        success: true,
        message: `Clave Outline ${keyId} eliminada correctamente`,
        keyId
      };

    } catch (error) {
      // Si es 404, la clave ya no existe, igual la eliminamos del manager
      if (error.response && error.response.status === 404) {
        logger.warn('[OutlineService] Clave no encontrada al eliminar, limpiando localmente', { keyId });
        await managerService.removeVpnData(userId, 'outline');
        this._cache.metrics.delete(keyId);
        return {
          success: true,
          message: 'Clave ya eliminada en el servidor, limpiada localmente',
          keyId
        };
      }

      logger.error('[OutlineService] Error eliminando clave', {
        userId,
        keyId,
        error: error.message
      });
      
      throw new Error(`Error eliminando clave Outline: ${error.message}`);
    }
  }

  async suspendKey(userId, reason = 'Cuota excedida') {
    const user = managerService.getCompleteUser(userId);
    
    if (!user || !user.outline) {
      throw new Error('Usuario no tiene clave Outline');
    }

    try {
      // En Outline no hay suspensión nativa a nivel de API,
      // pero podemos marcar como suspendida en nuestro sistema
      // y opcionalmente establecer un límite de datos de 0 bytes
      
      // Opción 1: Establecer límite de datos a 0 (si la API lo soporta)
      try {
        await this.api.put(`/access-keys/${user.outline.keyId}/data-limit`, {
          limit: { bytes: 0 }
        });
        logger.debug('[OutlineService] Límite de datos establecido a 0 para suspensión', {
          keyId: user.outline.keyId
        });
      } catch (limitError) {
        // Si la API no soporta límites de datos, continuamos
        logger.debug('[OutlineService] API no soporta límites de datos, solo marcando como suspendida');
      }

      // Actualizar estado en manager
      await managerService.setOutlineData(userId, {
        ...user.outline,
        suspended: true,
        suspendedAt: new Date().toISOString(),
        suspensionReason: reason,
        lastUpdated: new Date().toISOString()
      });

      logger.warn('[OutlineService] Clave suspendida', {
        userId,
        keyId: user.outline.keyId,
        reason
      });

      return {
        success: true,
        keyId: user.outline.keyId,
        suspendedAt: new Date().toISOString(),
        reason
      };

    } catch (error) {
      logger.error('[OutlineService] Error suspendiendo clave', {
        userId,
        keyId: user.outline.keyId,
        error: error.message
      });
      
      throw new Error(`Error suspendiendo clave Outline: ${error.message}`);
    }
  }

  async resumeKey(userId) {
    const user = managerService.getCompleteUser(userId);
    
    if (!user || !user.outline || !user.outline.suspended) {
      throw new Error('Usuario no tiene clave Outline suspendida');
    }

    try {
      // Restaurar límite de datos original (si se había establecido a 0)
      try {
        await this.api.delete(`/access-keys/${user.outline.keyId}/data-limit`);
        logger.debug('[OutlineService] Límite de datos restaurado', {
          keyId: user.outline.keyId
        });
      } catch (limitError) {
        // Si la API no soporta eliminación de límites, continuamos
        logger.debug('[OutlineService] API no soporta eliminación de límites de datos');
      }

      // Actualizar estado en manager
      await managerService.setOutlineData(userId, {
        ...user.outline,
        suspended: false,
        suspendedAt: null,
        suspensionReason: null,
        lastUpdated: new Date().toISOString()
      });

      logger.info('[OutlineService] Clave reanudada', {
        userId,
        keyId: user.outline.keyId
      });

      return {
        success: true,
        keyId: user.outline.keyId,
        resumedAt: new Date().toISOString()
      };

    } catch (error) {
      logger.error('[OutlineService] Error reanudando clave', {
        userId,
        keyId: user.outline.keyId,
        error: error.message
      });
      
      throw new Error(`Error reanudando clave Outline: ${error.message}`);
    }
  }

  async renameKey(userId, newName) {
    const user = managerService.getCompleteUser(userId);
    
    if (!user || !user.outline) {
      throw new Error('Usuario no tiene clave Outline');
    }

    try {
      await this.api.put(`/access-keys/${user.outline.keyId}/name`, {
        name: newName
      });

      // Actualizar en manager
      await managerService.setOutlineData(userId, {
        ...user.outline,
        name: newName,
        lastUpdated: new Date().toISOString()
      });

      logger.info('[OutlineService] Clave renombrada', {
        userId,
        keyId: user.outline.keyId,
        oldName: user.outline.name,
        newName
      });

      return {
        success: true,
        keyId: user.outline.keyId,
        oldName: user.outline.name,
        newName
      };

    } catch (error) {
      logger.error('[OutlineService] Error renombrando clave', {
        userId,
        keyId: user.outline.keyId,
        error: error.message
      });
      
      throw new Error(`Error renombrando clave Outline: ${error.message}`);
    }
  }

  // ============================================================================
  // 📊 MÉTODOS DE MONITOREO Y ESTADÍSTICAS
  // ============================================================================

  async getKeyUsage(keyId, forceRefresh = false) {
    const now = Date.now();
    const cached = this._cache.metrics.get(keyId);
    
    // Verificar cache
    if (!forceRefresh && cached && (now - cached.timestamp < this._cache.CACHE_TTL)) {
      return cached.data;
    }

    try {
      const res = await this.api.get('/metrics/transfer');
      const usageMap = res.data?.bytesTransferredByUserId || {};
      
      const bytes = usageMap[keyId] || 0;
      const result = {
        keyId,
        bytesUsed: bytes,
        bytesUsedHuman: formatBytes(bytes),
        lastUpdated: new Date().toISOString()
      };

      // Actualizar cache
      this._cache.metrics.set(keyId, {
        data: result,
        timestamp: now
      });

      // Actualizar también en manager si el usuario existe
      const users = managerService.getAllUsers();
      const user = this._findUserIdByKeyId(keyId, users);
      if (user) {
        await managerService.setOutlineData(user, {
          ...user.outline,
          usedBytes: bytes,
          lastUpdated: new Date().toISOString()
        });
      }

      return result;
    } catch (error) {
      logger.error('[OutlineService] Error obteniendo uso de clave', {
        keyId,
        error: error.message
      });
      
      // Si hay datos cacheados, devolverlos aunque estén desactualizados
      if (cached) {
        logger.warn('[OutlineService] Usando datos cacheados para métricas', { keyId });
        return cached.data;
      }
      
      // Si no hay cache, devolver valores por defecto
      return { 
        keyId, 
        bytesUsed: 0, 
        bytesUsedHuman: '0 B',
        lastUpdated: new Date().toISOString(),
        error: true 
      };
    }
  }

  async getAllKeysStats() {
    try {
      const [keysRes, metricsRes] = await Promise.all([
        this.api.get('/access-keys'),
        this.api.get('/metrics/transfer')
      ]);

      const keys = keysRes.data?.accessKeys || [];
      const usageMap = metricsRes.data?.bytesTransferredByUserId || {};

      const stats = {};
      const users = managerService.getAllUsers();

      for (const key of keys) {
        const userId = this._findUserIdByKeyId(key.id, users);
        const bytesUsed = usageMap[key.id] || 0;
        const quotaPercentage = (bytesUsed / this.defaultQuota) * 100;

        if (userId) {
          stats[userId] = {
            keyId: key.id,
            name: key.name,
            bytesUsed,
            bytesUsedHuman: formatBytes(bytesUsed),
            accessUrl: this._applyBranding(key.accessUrl),
            quotaPercentage: quotaPercentage.toFixed(2),
            quotaExceeded: bytesUsed >= this.defaultQuota,
            quotaWarning: quotaPercentage > 80 && quotaPercentage < 100,
            lastUpdated: new Date().toISOString()
          };
        } else {
          // Key sin usuario asociado (huérfana)
          stats[key.id] = {
            keyId: key.id,
            name: key.name,
            bytesUsed,
            bytesUsedHuman: formatBytes(bytesUsed),
            orphaned: true,
            quotaPercentage: quotaPercentage.toFixed(2),
            quotaExceeded: bytesUsed >= this.defaultQuota
          };
        }
      }

      // Actualizar cache
      const now = Date.now();
      for (const [keyId, data] of Object.entries(stats)) {
        if (data.keyId) {
          this._cache.metrics.set(data.keyId, {
            data: {
              keyId: data.keyId,
              bytesUsed: data.bytesUsed,
              bytesUsedHuman: data.bytesUsedHuman,
              lastUpdated: data.lastUpdated
            },
            timestamp: now
          });
        }
      }

      return stats;
    } catch (error) {
      logger.error('[OutlineService] Error obteniendo estadísticas de todas las claves', error);
      return {};
    }
  }

  async checkAllQuotas() {
    const stats = await this.getAllKeysStats();
    const exceeded = [];
    const warnings = [];
    
    for (const [userId, keyStats] of Object.entries(stats)) {
      if (keyStats.quotaExceeded) {
        exceeded.push({
          userId: userId.startsWith('tg_') ? userId : userId, // userId o keyId
          ...keyStats,
          exceededBy: formatBytes(keyStats.bytesUsed - this.defaultQuota)
        });
      } else if (keyStats.quotaWarning) {
        warnings.push({
          userId: userId.startsWith('tg_') ? userId : userId,
          ...keyStats,
          remaining: formatBytes(this.defaultQuota - keyStats.bytesUsed)
        });
      }
    }
    
    return {
      totalKeys: Object.keys(stats).length,
      quotaExceeded: exceeded.length,
      quotaWarnings: warnings.length,
      exceededKeys: exceeded,
      warningKeys: warnings
    };
  }

  async cleanupOrphanedKeys() {
    try {
      const [keysRes, users] = await Promise.all([
        this.api.get('/access-keys'),
        managerService.getAllUsers()
      ]);

      const keys = keysRes.data?.accessKeys || [];
      const userKeyIds = new Set(
        users
          .filter(u => u.outline && u.outline.keyId)
          .map(u => u.outline.keyId)
      );

      const orphanedKeys = keys.filter(key => !userKeyIds.has(key.id));
      const results = [];

      for (const key of orphanedKeys) {
        try {
          await this.api.delete(`/access-keys/${key.id}`);
          results.push({
            keyId: key.id,
            name: key.name,
            status: 'deleted',
            reason: 'huérfana'
          });
          logger.warn('[OutlineService] Clave huérfana eliminada', { keyId: key.id });
        } catch (error) {
          results.push({
            keyId: key.id,
            name: key.name,
            status: 'error',
            error: error.message
          });
        }
      }

      return {
        totalOrphaned: orphanedKeys.length,
        deleted: results.filter(r => r.status === 'deleted').length,
        errors: results.filter(r => r.status === 'error').length,
        details: results
      };
    } catch (error) {
      logger.error('[OutlineService] Error limpiando claves huérfanas', error);
      throw new Error(`Error limpiando claves huérfanas: ${error.message}`);
    }
  }

  // ============================================================================
  // 🔒 MÉTODOS PRIVADOS (IMPLEMENTACIÓN INTERNA)
  // ============================================================================

  _applyBranding(accessUrl) {
    const brand = config.OUTLINE_BRAND || 'uSipipo VPN';
    const tag = encodeURIComponent(brand);
    return `${accessUrl}#${tag}`;
  }

  _findUserIdByKeyId(keyId, users) {
    for (const user of users) {
      if (user.outline && user.outline.keyId === keyId) {
        return user.id;
      }
    }
    return null;
  }

  _handleApiError(error, context = '') {
    this.circuitState.failureCount++;
    this.circuitState.lastFailure = Date.now();

    if (this.circuitState.failureCount >= this.circuitState.failureThreshold) {
      this.circuitState.isOpen = true;
      logger.error('[OutlineService] Circuit breaker abierto - Outline API no disponible', {
        context,
        failureCount: this.circuitState.failureCount,
        lastFailure: new Date(this.circuitState.lastFailure).toISOString()
      });
    }

    // Log detallado del error
    if (error.response) {
      logger.error(`[OutlineService] Error en ${context}`, {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers
      });
    } else if (error.request) {
      logger.error(`[OutlineService] Error de red en ${context}`, {
        message: error.message,
        code: error.code
      });
    } else {
      logger.error(`[OutlineService] Error en ${context}`, {
        message: error.message,
        stack: error.stack
      });
    }
  }

  async _cleanupFailedCreation(userId) {
    try {
      await managerService.removeVpnData(userId, 'outline');
    } catch (error) {
      logger.debug('[OutlineService] Cleanup falló', { userId, error: error.message });
    }
  }

  // ============================================================================
  // 🛠️ MÉTODOS DE UTILIDAD PARA SISTEMA
  // ============================================================================

  getCircuitBreakerStatus() {
    return {
      isOpen: this.circuitState.isOpen,
      failureCount: this.circuitState.failureCount,
      lastFailure: this.circuitState.lastFailure 
        ? new Date(this.circuitState.lastFailure).toISOString() 
        : null,
      timeSinceLastFailure: this.circuitState.lastFailure 
        ? Date.now() - this.circuitState.lastFailure 
        : null,
      resetTimeout: this.circuitState.resetTimeout
    };
  }

  resetCircuitBreaker() {
    const oldState = { ...this.circuitState };
    this.circuitState = {
      isOpen: false,
      failureCount: 0,
      lastFailure: null,
      successThreshold: 3,
      failureThreshold: 5,
      resetTimeout: 60000
    };
   
    logger.info('[OutlineService] Circuit breaker reseteado', { oldState });
    return { success: true, oldState };
  }

  clearCache() {
    const cacheStats = {
      serverInfo: this._cache.serverInfo ? 'cleared' : 'empty',
      metricsCount: this._cache.metrics.size,
      metricsCleared: true
    };

    this._cache = {
      serverInfo: null,
      serverInfoTimestamp: 0,
      metrics: new Map(),
      metricsTimestamp: 0,
      CACHE_TTL: 30000
    };

    logger.debug('[OutlineService] Cache limpiado', cacheStats);
    return { success: true, ...cacheStats };
  }
}

// Exportar como clase, no como singleton
module.exports = OutlineService;
