const axios = require('axios');
const https = require('https');

class OutlineService {
  static async createAccessKey() {
    const outlineApiUrl = `http://${process.env.SERVER_IPV4}:${process.env.OUTLINE_API_PORT}`;

    const agent = new https.Agent({
      rejectUnauthorized: false, // Para certificados autofirmados
      checkServerIdentity: () => {
        return null; // Ignorar verificación de hostname
      }
    });

    try {
      const response = await axios.post(
        `${outlineApiUrl}/access-keys`,
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
