// services/outline.js
const axios = require('axios');
const https = require('https');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

class OutlineService {
  static async createAccessKey(name = null) {
    const apiUrl = `https://${process.env.SERVER_IPV4}:${process.env.OUTLINE_API_PORT}`;
    
    // Crear agente HTTPS que ignore certificados autofirmados
    const httpsAgent = new https.Agent({
      rejectUnauthorized: false
    });

    try {
      // Crear nueva clave de acceso
      const response = await axios.post(
        `${apiUrl}/access-keys`,
        {},
        { 
          httpsAgent,
          timeout: 10000
        }
      );

      const accessKey = response.data;
      
      // Opcional: asignar nombre descriptivo
      if (name) {
        await axios.put(
          `${apiUrl}/access-keys/${accessKey.id}/name`,
          { name },
          { httpsAgent }
        );
        accessKey.name = name;
      }

      // Configurar DNS de Pi-hole para esta clave
      await this.configureDNS(accessKey.id, httpsAgent, apiUrl);

      return accessKey;
    } catch (error) {
      if (error.response) {
        console.error('Outline API Error:', error.response.status, error.response.data);
      } else if (error.request) {
        console.error('No response from Outline server. Is it running?');
      } else {
        console.error('Error:', error.message);
      }
      throw new Error('Failed to create Outline access key');
    }
  }

  static async configureDNS(keyId, httpsAgent, apiUrl) {
    const piholeIP = process.env.PIHOLE_DNS || '10.2.0.100';
    
    try {
      await axios.put(
        `${apiUrl}/access-keys/${keyId}`,
        { 
          "metricsEnabled": false,
          "name": `User-${keyId}`,
          "dataLimit": {
            "bytes": 10737418240 // 10GB default limit
          }
        },
        { httpsAgent }
      );
      
      console.log(`✅ DNS configured for key ${keyId} -> ${piholeIP}`);
    } catch (error) {
      console.warn(`⚠️ Could not configure DNS for key ${keyId}`);
    }
  }

  static async listAccessKeys() {
    const apiUrl = `https://${process.env.SERVER_IPV4}:${process.env.OUTLINE_API_PORT}`;
    const httpsAgent = new https.Agent({ rejectUnauthorized: false });

    try {
      const response = await axios.get(`${apiUrl}/access-keys`, { httpsAgent });
      return response.data.accessKeys || [];
    } catch (error) {
      console.error('Error fetching access keys:', error.message);
      return [];
    }
  }

  static async deleteAccessKey(keyId) {
    const apiUrl = `https://${process.env.SERVER_IPV4}:${process.env.OUTLINE_API_PORT}`;
    const httpsAgent = new https.Agent({ rejectUnauthorized: false });

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
    const apiUrl = `https://${process.env.SERVER_IPV4}:${process.env.OUTLINE_API_PORT}`;
    const httpsAgent = new https.Agent({ rejectUnauthorized: false });

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
