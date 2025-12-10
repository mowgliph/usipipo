'use strict';

const axios = require('axios');
const https = require('https');
const config = require('../config/environment');
const logger = require('../utils/logger');

/**
 * Servicio Outline (Shadowbox)
 * Refactorizado para estabilidad MVP 2025
 */
class OutlineService {

  constructor() {
    if (!config.OUTLINE_API_URL) {
      logger.warn('⚠️ OutlineService: Falta OUTLINE_API_URL en variables de entorno');
    }

    // Configuración de Axios ignorando certificados autofirmados (común en Outline)
    this.api = axios.create({
      baseURL: config.OUTLINE_API_URL,
      timeout: 15000, // Aumentado timeout para evitar falsos negativos
      httpsAgent: new https.Agent({
        rejectUnauthorized: false
      })
    });
  }

  // ---------------------------------------------------------------------
  // 🔒 UTILIDADES INTERNAS
  // ---------------------------------------------------------------------

  /**
   * Formatea el enlace ss:// con branding
   */
  static applyBranding(accessUrl) {
    const brand = config.OUTLINE_BRAND || 'uSipipo VPN';
    // Codificación segura para evitar romper el link
    const tag = encodeURIComponent(brand);
    return `${accessUrl}#${tag}`;
  }

  /**
   * Manejo estandarizado de errores de Axios
   */
  _safeError(err, context = '') {
    const errorMsg = err.response 
      ? `HTTP ${err.response.status} - ${JSON.stringify(err.response.data)}`
      : err.message;
    
    return `${context}: ${errorMsg}`;
  }

  // ---------------------------------------------------------------------
  // 📡 INFORMACIÓN DEL SERVIDOR (Fix para InfoHandler)
  // ---------------------------------------------------------------------
  async getServerInfo() {
    try {
      // Endpoint /server solo devuelve: name, serverId, metricsEnabled, createdTimestampMs, version, etc.
      const serverRes = await this.api.get('/server');
      
      // Para obtener el conteo real de keys, necesitamos consultar /access-keys
      // Hacemos esto en paralelo o secuencial si la carga es baja.
      let keyCount = 0;
      try {
        const keysRes = await this.api.get('/access-keys');
        keyCount = keysRes.data?.accessKeys?.length || 0;
      } catch (e) {
        logger.warn('No se pudo obtener conteo de keys en getServerInfo', e.message);
      }

      const data = serverRes.data;

      return {
        name: data.name || 'Outline Server',
        serverId: data.serverId,
        version: data.version,
        metricsEnabled: data.metricsEnabled,
        createdTimestampMs: data.createdTimestampMs,
        portForNewAccessKeys: data.portForNewAccessKeys || config.OUTLINE_API_PORT,
        totalKeys: keyCount, // Dato corregido
        isHealthy: true
      };

    } catch (err) {
      const safe = this._safeError(err, 'getServerInfo');
      logger.error(safe);
      throw new Error('El servidor VPN no responde o no es accesible.');
    }
  }

  // ---------------------------------------------------------------------
  // 🔑 GESTIÓN DE CLAVES
  // ---------------------------------------------------------------------
  
  async createKey(name = 'Usuario') {
    try {
      const res = await this.api.post('/access-keys', { name });
      const key = res.data; // { id, name, password, port, method, accessUrl }

      if (!key || !key.accessUrl) {
        throw new Error('Respuesta malformada de Shadowbox');
      }

      const brandedUrl = OutlineService.applyBranding(key.accessUrl);

      logger.info(`Key creada: ID ${key.id} (${name})`);

      return {
        id: key.id,
        name: key.name,
        accessUrl: brandedUrl,
        port: key.port,
        method: key.method
      };

    } catch (err) {
      const safe = this._safeError(err, 'createKey');
      logger.error(safe);
      throw new Error('Error al crear la llave de acceso.');
    }
  }

  async deleteKey(keyId) {
    try {
      await this.api.delete(`/access-keys/${keyId}`);
      logger.info(`Key eliminada: ID ${keyId}`);
      return true;
    } catch (err) {
      // Si es 404, técnicamente ya está borrada, no deberíamos lanzar error fatal
      if (err.response && err.response.status === 404) {
        logger.warn(`Intento de borrar key inexistente: ${keyId}`);
        return true;
      }
      const safe = this._safeError(err, `deleteKey(${keyId})`);
      logger.error(safe);
      throw new Error('No se pudo eliminar la llave.');
    }
  }

  async listKeys() {
    try {
      const res = await this.api.get('/access-keys');
      const rawKeys = res.data?.accessKeys || [];

      return rawKeys.map(k => ({
        id: k.id,
        name: k.name || 'Sin Nombre',
        accessUrl: OutlineService.applyBranding(k.accessUrl),
        dataLimit: k.dataLimit || null
      }));

    } catch (err) {
      const safe = this._safeError(err, 'listKeys');
      logger.error(safe);
      throw new Error('Error listando usuarios.');
    }
  }

  // ---------------------------------------------------------------------
  // 📊 MÉTRICAS DE USO
  // ---------------------------------------------------------------------
  async getKeyUsage(keyId) {
    try {
      // Metrics devuelve un objeto: { bytesTransferredByUserId: { "id": bytes, ... } }
      const res = await this.api.get('/metrics/transfer');
      const usageMap = res.data?.bytesTransferredByUserId || {};
      
      const bytes = usageMap[keyId] || 0;

      return {
        keyId,
        bytesUsed: bytes, // Outline API standard actual solo devuelve total, no up/down separado a veces
        bytesUsedHuman: (bytes / (1024 * 1024)).toFixed(2) + ' MB'
      };

    } catch (err) {
      const safe = this._safeError(err, `getKeyUsage(${keyId})`);
      logger.error(safe);
      // Retornamos 0 en lugar de romper el flujo, el usuario quiere ver su menú
      return { keyId, bytesUsed: 0, error: true };
    }
  }
}

module.exports = new OutlineService();
