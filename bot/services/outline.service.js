// services/outline.service.js
const axios = require('axios');
const https = require('https');
const config = require('../config/environment');
const constants = require('../config/constants');

class OutlineService {
  static getApiConfig() {
    const apiUrl = `https://${config.SERVER_IPV4}:${config.OUTLINE_API_PORT}`;
    const httpsAgent = new https.Agent({ rejectUnauthorized: false });
    
    return { apiUrl, httpsAgent };
  }

  static async createAccessKey(name = null) {
    const { apiUrl, httpsAgent } = this.getApiConfig();

    try {
      const response = await axios.post(
        `${apiUrl}/access-keys`,
        {},
        { httpsAgent, timeout: 10000 }
      );

      const accessKey = response.data;
      
      if (name) {
        await axios.put(
          `${apiUrl}/access-keys/${accessKey.id}/name`,
          { name },
          { httpsAgent }
        );
        accessKey.name = name;
      }

      await this.configureDNS(accessKey.id, httpsAgent, apiUrl);

      return accessKey;
    } catch (error) {
      console.error('Outline API Error:', error.message);
      throw new Error('Failed to create Outline access key');
    }
  }

  static async configureDNS(keyId, httpsAgent, apiUrl) {
    try {
      await axios.put(
        `${apiUrl}/access-keys/${keyId}`,
        { 
          "metricsEnabled": false,
          "name": `User-${keyId}`,
          "dataLimit": {
            "bytes": constants.OUTLINE_DEFAULT_DATA_LIMIT
          }
        },
        { httpsAgent }
      );
      
      console.log(`✅ DNS configured for key ${keyId}`);
    } catch (error) {
      console.warn(`⚠️ Could not configure DNS for key ${keyId}`);
    }
  }

  static async listAccessKeys() {
    const { apiUrl, httpsAgent } = this.getApiConfig();

    try {
      const response = await axios.get(`${apiUrl}/access-keys`, { httpsAgent });
      return response.data.accessKeys || [];
    } catch (error) {
      console.error('Error fetching access keys:', error.message);
      return [];
    }
  }

  static async deleteAccessKey(keyId) {
    const { apiUrl, httpsAgent } = this.getApiConfig();

    try {
      await axios.delete(`${apiUrl}/access-keys/${keyId}`, { httpsAgent });
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
      const response = await axios.get(`${apiUrl}/server`, { httpsAgent });
      return response.data;
    } catch (error) {
      console.error('Error fetching server info:', error.message);
      return null;
    }
  }
}

module.exports = OutlineService;
