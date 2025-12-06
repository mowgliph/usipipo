// services/outline.service.js
const axios = require('axios');
const https = require('https');
const config = require('../config/environment');
const constants = require('../config/constants');
const logger = require('../utils/logger');

/**
 * Servicio para interactuar con la API de Outline (Access Server).
 * Soporta creación, administración y consulta de claves de acceso VPN.
 */
class OutlineService {
  /**
   * Retorna la configuración base para peticiones Outline.
   * Incluye el agente HTTPS que permite certificados autofirmados.
   * @returns {{ apiUrl: string, httpsAgent: https.Agent }}
   */
  static getApiConfig() {
    const apiUrl = config.OUTLINE_API_URL;
    const httpsAgent = new https.Agent({
      rejectUnauthorized: false // Permite certificados autofirmados
    });
    return { apiUrl, httpsAgent };
  }

  /**
   * Crea una nueva clave de acceso Outline opcionalmente nombrada.
   * @param {string|null} name - Nombre descriptivo de la clave
   * @returns {Promise<Object>} Objeto de clave Outline con accessUrl, id y name.
   */
  static async createAccessKey(name = null) {
    const { apiUrl, httpsAgent } = this.getApiConfig();

    try {
      const response = await axios.post(
        `${apiUrl}/access-keys`,
        {},
        { httpsAgent, timeout: 10000 }
      );
      const accessKey = response.data;

      // Agregar nombre descriptivo
      if (name) {
        await axios.put(
          `${apiUrl}/access-keys/${accessKey.id}/name`,
          { name },
          { httpsAgent }
        );
        accessKey.name = name;
      }

      // Establecer límite de datos por defecto
      await OutlineService.setDataLimit(
        accessKey.id,
        constants.OUTLINE_DEFAULT_DATA_LIMIT,
        httpsAgent,
        apiUrl
      );

      logger.success('OutlineService', 'createAccessKey', accessKey.id, {
        name,
        url: accessKey.accessUrl
      });

      return accessKey;
    } catch (error) {
      logger.error('OutlineService.createAccessKey', error, {
        endpoint: `${apiUrl}/access-keys`,
        cause: error.response?.data || error.message
      });
      throw new Error(`Failed to create Outline access key: ${error.message}`);
    }
  }

  /**
   * Asigna un límite de uso (en bytes) a una clave de acceso existente.
   * @param {string} keyId - ID de la clave
   * @param {number} bytes - Límite de datos
   * @param {https.Agent} httpsAgent
   * @param {string} apiUrl
   */
  static async setDataLimit(keyId, bytes, httpsAgent, apiUrl) {
    try {
      await axios.put(
        `${apiUrl}/access-keys/${keyId}/data-limit`,
        { limit: { bytes } },
        { httpsAgent }
      );

      logger.info('OutlineService.setDataLimit', 'Data limit set', {
        keyId,
        bytes
      });
    } catch (error) {
      logger.warn(`Could not set data limit for key ${keyId}`, {
        error: error.message
      });
    }
  }

  /**
   * Obtiene la lista actual de claves de acceso activas.
   * @returns {Promise<Array>} Lista de claves
   */
  static async listAccessKeys() {
    const { apiUrl, httpsAgent } = this.getApiConfig();

    try {
      const response = await axios.get(`${apiUrl}/access-keys`, { httpsAgent });
      const keys = response.data.accessKeys || [];

      logger.info('OutlineService.listAccessKeys', 'Fetched Outline keys', {
        count: keys.length
      });

      return keys;
    } catch (error) {
      logger.error('OutlineService.listAccessKeys', error, { apiUrl });
      return [];
    }
  }

  /**
   * Elimina una clave de acceso por ID.
   * @param {string} keyId
   * @returns {Promise<boolean>} true si se eliminó correctamente
   */
  static async deleteAccessKey(keyId) {
    const { apiUrl, httpsAgent } = this.getApiConfig();

    try {
      await axios.delete(`${apiUrl}/access-keys/${keyId}`, { httpsAgent });
      logger.info('OutlineService.deleteAccessKey', 'Deleted access key', { keyId });
      return true;
    } catch (error) {
      logger.error('OutlineService.deleteAccessKey', error, { keyId });
      return false;
    }
  }

  /**
   * Obtiene información general del servidor Outline.
   * @returns {Promise<Object|null>} Datos del servidor o null si falla
   */
  static async getServerInfo() {
    const { apiUrl, httpsAgent } = this.getApiConfig();

    try {
      const response = await axios.get(`${apiUrl}/server`, { httpsAgent });
      logger.info('OutlineService.getServerInfo', 'Fetched server status', {
        apiUrl
      });
      return response.data;
    } catch (error) {
      logger.error('OutlineService.getServerInfo', error, { apiUrl });
      return null;
    }
  }

  /**
   * Renombra una clave existente.
   * @param {string} keyId
   * @param {string} newName
   * @returns {Promise<boolean>} true si el cambio fue exitoso
   */
  static async renameAccessKey(keyId, newName) {
    const { apiUrl, httpsAgent } = this.getApiConfig();

    try {
      await axios.put(
        `${apiUrl}/access-keys/${keyId}/name`,
        { name: newName },
        { httpsAgent }
      );

      logger.info('OutlineService.renameAccessKey', 'Renamed key', {
        keyId,
        newName
      });
      return true;
    } catch (error) {
      logger.error('OutlineService.renameAccessKey', error, { keyId, newName });
      return false;
    }
  }
}

module.exports = OutlineService;