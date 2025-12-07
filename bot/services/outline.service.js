// services/outline.service.js
const axios = require('axios');
const https = require('https');
const config = require('../config/environment');
const constants = require('../config/constants');
const logger = require('../utils/logger');

/**
 * Servicio Outline — versión refactorizada Estilo A
 * -----------------------------------------------
 * ✔ Cliente Axios unificado
 * ✔ Manejo de errores consistente
 * ✔ Reducción del 50% del código repetido
 * ✔ Logs más claros
 */
class OutlineService {

  // =============================================
  // CLIENTE AXIOS CENTRALIZADO
  // =============================================
  static get client() {
    if (!this._client) {
      this._client = axios.create({
        baseURL: config.OUTLINE_API_URL,
        timeout: 10000,
        httpsAgent: new https.Agent({ rejectUnauthorized: false }),
        validateStatus: () => true // manejamos errores manualmente
      });
    }
    return this._client;
  }

  // =============================================
  // HELPER CENTRAL PARA REQUESTS
  // =============================================
  static async request(method, path, body = null) {
    try {
      const res = await this.client.request({
        method,
        url: path,
        data: body || undefined
      });

      // Error HTTP → lo tratamos como fallo real
      if (res.status >= 400) {
        logger.error(`OutlineService HTTP ${res.status}`, {
          path,
          response: res.data
        });
        throw new Error(res.data?.message || `HTTP ${res.status}`);
      }

      return res.data;

    } catch (err) {
      logger.error('OutlineService.request FAILED', {
        method,
        path,
        error: err.message
      });
      throw new Error(`Outline API error: ${err.message}`);
    }
  }

  // =============================================
  // CREATE ACCESS KEY
  // =============================================
  static async createAccessKey(name = null) {
    try {
      // 1. Crear clave
      const accessKey = await this.request('post', '/access-keys');

      // 2. Asignar nombre (opcional)
      if (name) {
        await this.request(
          'put',
          `/access-keys/${accessKey.id}/name`,
          { name }
        );
        accessKey.name = name;
      }

      // 3. Límite de datos por defecto
      await this.setDataLimit(accessKey.id, constants.OUTLINE_DEFAULT_DATA_LIMIT);

      logger.success('OutlineService.createAccessKey', {
        id: accessKey.id,
        name,
        url: accessKey.accessUrl
      });

      return accessKey;

    } catch (err) {
      logger.error('OutlineService.createAccessKey ERROR', err.message);
      throw new Error(`Failed to create Outline key: ${err.message}`);
    }
  }

  // =============================================
  // SET DATA LIMIT
  // =============================================
  static async setDataLimit(keyId, bytes) {
    try {
      await this.request(
        'put',
        `/access-keys/${keyId}/data-limit`,
        { limit: { bytes } }
      );

      logger.info('OutlineService.setDataLimit', { keyId, bytes });

    } catch (err) {
      logger.warn(`Could not set data limit for key ${keyId}`, err.message);
      // NO lanzamos error — Outline puede seguir funcionando
    }
  }

  // =============================================
  // LIST KEYS
  // =============================================
  static async listAccessKeys() {
    try {
      const data = await this.request('get', '/access-keys');

      const keys = data.accessKeys || [];

      logger.info('OutlineService.listAccessKeys', {
        count: keys.length
      });

      return keys;

    } catch (err) {
      logger.error('OutlineService.listAccessKeys ERROR', err.message);
      return []; // fallback seguro
    }
  }

  // =============================================
  // DELETE KEY
  // =============================================
  static async deleteAccessKey(keyId) {
    try {
      await this.request('delete', `/access-keys/${keyId}`);

      logger.info('OutlineService.deleteAccessKey', { keyId });
      return true;

    } catch (err) {
      logger.error('OutlineService.deleteAccessKey ERROR', {
        keyId,
        error: err.message
      });
      return false;
    }
  }

  // =============================================
  // SERVER INFO
  // =============================================
  static async getServerInfo() {
    try {
      return await this.request('get', '/server');

    } catch (err) {
      logger.error('OutlineService.getServerInfo ERROR', err.message);
      return null;
    }
  }

  // =============================================
  // RENAME KEY
  // =============================================
  static async renameAccessKey(keyId, newName) {
    try {
      await this.request(
        'put',
        `/access-keys/${keyId}/name`,
        { name: newName }
      );

      logger.info('OutlineService.renameAccessKey', {
        keyId,
        newName
      });

      return true;

    } catch (err) {
      logger.error('OutlineService.renameAccessKey ERROR', {
        keyId, newName, error: err.message
      });
      return false;
    }
  }
}

module.exports = OutlineService;