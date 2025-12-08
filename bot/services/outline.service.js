'use strict';

const axios = require('axios');
const config = require('../config/environment');
const logger = require('../utils/logger');
const { bold, code, escapeHtml } = require('../utils/messages')._helpers;

/**
 * Servicio oficial para gestionar Outline (Shadowbox)
 * Compatible 100% con el API REST del servidor oficial "shadowbox"
 *
 * Requisitos:
 *  - OUTLINE_API_URL        → https://IP:PORT/<secret>/
 *  - OUTLINE_CERT_SHA256    → sha256 del certificado de Shadowbox
 *  - OUTLINE_SERVER_IP
 *  - OUTLINE_API_PORT
 */
class OutlineService {

  constructor() {
    if (!config.OUTLINE_API_URL) {
      logger.warn('OutlineService inicializado SIN OUTLINE_API_URL en .env');
    }

    this.api = axios.create({
      baseURL: config.OUTLINE_API_URL,
      timeout: 10000,
      httpsAgent: new (require('https').Agent)({
        rejectUnauthorized: false
      })
    });
  }

  // ---------------------------------------------------------------------
  // 🔒 UTILIDADES INTERNAS
  // ---------------------------------------------------------------------

  /**
   * Añade el tag a los enlaces Outline como:
   * ss://HASH@server:port#uSipipo%20VPN,%20MIAMI,%20US
   */
  static applyBranding(accessUrl) {
    const brand = config.OUTLINE_BRAND || 'uSipipo VPN';
    const city = config.OUTLINE_LOCATION_NAME || null;
    const country = config.OUTLINE_LOCATION_COUNTRY || null;

    let tagParts = [];

    if (brand) tagParts.push(brand);
    if (city) tagParts.push(city);
    if (country) tagParts.push(country);

    const finalTag = tagParts.join(', ');
    const encoded = encodeURIComponent(finalTag);

    return `${accessUrl}#${encoded}`;
  }

  _safeError(err) {
    if (err.response) {
      return `HTTP ${err.response.status}: ${JSON.stringify(err.response.data)}`;
    }
    return err.message;
  }

  // ---------------------------------------------------------------------
  // 🔑 CREAR NUEVA CLAVE (CLIENTE)
  // ---------------------------------------------------------------------
  async createKey(name = 'Cliente') {
    try {
      const res = await this.api.post('/access-keys', { name });

      const key = res.data;
      if (!key || !key.accessUrl) {
        throw new Error('Respuesta inválida del servidor Outline');
      }

      const branded = OutlineService.applyBranding(key.accessUrl);

      logger.info('Outline key creada', {
        id: key.id,
        name
      });

      return {
        id: key.id,
        name,
        accessUrl: branded
      };

    } catch (err) {
      const safe = this._safeError(err);
      logger.error('createKey', safe);
      throw new Error(`Error creando clave Outline: ${safe}`);
    }
  }

  // ---------------------------------------------------------------------
  // 🗑 ELIMINAR CLAVE
  // ---------------------------------------------------------------------
  async deleteKey(keyId) {
    try {
      await this.api.delete(`/access-keys/${keyId}`);

      logger.warn('Outline key eliminada', { keyId });
      return true;

    } catch (err) {
      const safe = this._safeError(err);
      logger.error('deleteKey', safe, { keyId });
      throw new Error(`No se pudo eliminar la clave: ${safe}`);
    }
  }

  // ---------------------------------------------------------------------
  // 📋 LISTAR CLAVES
  // ---------------------------------------------------------------------
  async listKeys() {
    try {
      const res = await this.api.get('/access-keys');
      const list = res.data || [];

      const final = list.map(k => ({
        id: k.id,
        name: k.name || 'Sin nombre',
        accessUrl: OutlineService.applyBranding(k.accessUrl)
      }));

      logger.info('listKeys', { count: final.length });

      return final;

    } catch (err) {
      const safe = this._safeError(err);
      logger.error('listKeys', safe);
      throw new Error(`No se pudieron obtener las claves: ${safe}`);
    }
  }

  // ---------------------------------------------------------------------
  // 📊 ESTADÍSTICAS DEL SERVIDOR OUTLINE
  // ---------------------------------------------------------------------
  async getServerStats() {
    try {
      const res = await this.api.get('/server');

      return {
        name: res.data.name,
        createdAt: res.data.createdTimestampMs,
        version: res.data.version,
        port: config.OUTLINE_API_PORT,
        keys: res.data.accessKeys?.length ?? 0
      };

    } catch (err) {
      const safe = this._safeError(err);
      logger.error('getServerStats', safe);
      throw new Error(`Error obteniendo estadísticas del servidor: ${safe}`);
    }
  }

  // ---------------------------------------------------------------------
  // 📡 OBTENER USO (DATA USAGE) DE UNA CLAVE
  // ---------------------------------------------------------------------
  async getKeyUsage(keyId) {
    try {
      const res = await this.api.get(`/metrics/transfer`);
      const entries = res.data?.bytesTransferredByUserId || {};

      const usage = entries[keyId] || { bytesUploaded: 0, bytesDownloaded: 0 };

      return {
        uploaded: usage.bytesUploaded,
        downloaded: usage.bytesDownloaded,
        total: usage.bytesUploaded + usage.bytesDownloaded
      };

    } catch (err) {
      const safe = this._safeError(err);
      logger.error('getKeyUsage', safe, { keyId });
      throw new Error(`Error leyendo consumo de clave Outline: ${safe}`);
    }
  }
}

module.exports = new OutlineService();