const axios = require('axios');
const https = require('https');

class OutlineService {
  static async createAccessKey() {
    const agent = new https.Agent({
      rejectUnauthorized: false, // Para certificados autofirmados
      checkServerIdentity: () => { 
        return null; // Ignorar verificación de hostname
      }
    });

    try {
      const response = await axios.post(
        `${process.env.OUTLINE_API_URL}/access-keys`,
        {},
        { httpsAgent: agent }
      );
      
      return response.data;
    } catch (error) {
      console.error('Error Outline API:', error.response?.data || error.message);
      throw new Error('Error al crear clave de acceso Outline');
    }
  }
}

module.exports = OutlineService;
