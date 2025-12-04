// services/outline.service.js
const axios = require('axios');
const https = require('https');
const config = require('../config/environment');
const constants = require('../config/constants');

class OutlineService {
  static getApiConfig() {
    // La URL ya contiene el secreto embebido
    const apiUrl = config.OUTLINE_API_URL;
    const httpsAgent = new https.Agent({ 
      rejectUnauthorized: false // Certificado autofirmado
    });
    
    return { apiUrl, httpsAgent };
  }

  static async createAccessKey(name = null) {
    const { apiUrl, httpsAgent } = this.getApiConfig();

    try {
      // POST a /access-keys (sin /api/access-keys, Outline no usa /api)
      const response = await axios.post(
        `${apiUrl}/access-keys`,
        {},
        { httpsAgent, timeout: 10000 }
      );

      const accessKey = response.data;
      
      // Asignar nombre si se proporciona
      if (name) {
        await axios.put(
          `${apiUrl}/access-keys/${accessKey.id}/name`,
          { name },
          { httpsAgent }
        );
        accessKey.name = name;
      }

      // Configurar límite de datos
      await this.setDataLimit(accessKey.id, constants.OUTLINE_DEFAULT_DATA_LIMIT, httpsAgent, apiUrl);

      console.log(`✅ Outline key created: ${accessKey.id}`);
      return accessKey;
      
    } catch (error) {
      console.error('Outline API Error:', error.response?.data || error.message);
      throw new Error(`Failed to create Outline access key: ${error.message}`);
    }
  }

  static async setDataLimit(keyId, bytes, httpsAgent, apiUrl) {
    try {
      await axios.put(
        `${apiUrl}/access-keys/${keyId}/data-limit`,
        { limit: { bytes } },
        { httpsAgent }
      );
      
      console.log(`✅ Data limit set for key ${keyId}: ${bytes} bytes`);
    } catch (error) {
      console.warn(`⚠️ Could not set data limit for key ${keyId}:`, error.message);
    }
  }

  static async listAccessKeys() {
    const { apiUrl, httpsAgent } = this.getApiConfig();

    try {
      const response = await axios.get(
        `${apiUrl}/access-keys`,
        { httpsAgent }
      );
      
      return response.data.accessKeys || [];
    } catch (error) {
      console.error('Error fetching access keys:', error.message);
      return [];
    }
  }

  static async deleteAccessKey(keyId) {
    const { apiUrl, httpsAgent } = this.getApiConfig();

    try {
      await axios.delete(
        `${apiUrl}/access-keys/${keyId}`,
        { httpsAgent }
      );
      
      console.log(`🗑️ Deleted access key ${keyId}`);
      return true;
    } catch (error) {
      console.error(`Error deleting key ${keyId}:`, error.message);
      return false;
    }
  }

  static async getServerInfo() {
    const { apiUrl, httpsAgent } = this.getApiConfig();

    try {
      const response = await axios.get(
        `${apiUrl}/server`,
        { httpsAgent }
      );
      
      return response.data;
    } catch (error) {
      console.error('Error fetching server info:', error.message);
      return null;
    }
  }

  static async renameAccessKey(keyId, newName) {
    const { apiUrl, httpsAgent } = this.getApiConfig();

    try {
      await axios.put(
        `${apiUrl}/access-keys/${keyId}/name`,
        { name: newName },
        { httpsAgent }
      );
      
      console.log(`✏️ Renamed key ${keyId} to: ${newName}`);
      return true;
    } catch (error) {
      console.error(`Error renaming key ${keyId}:`, error.message);
      return false;
    }
  }
}

module.exports = OutlineService;
