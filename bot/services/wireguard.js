const { execSync } = require('child_process');
const ConfigManager = require('../utils/configManager');

class WireGuardService {
  static async createNewClient() {
    // Generar claves
    const privateKey = execSync('wg genkey').toString().trim();
    const publicKey = execSync(`echo ${privateKey} | wg pubkey`).toString().trim();
    
    // Asignar IP
    const clientIP = ConfigManager.getNextIP();
    
    // Actualizar configuración del servidor
    ConfigManager.addPeerToServer(publicKey, clientIP);
    
    // Generar configuración para cliente
    const clientConfig = ConfigManager.generateWGConfig(clientIP, privateKey, publicKey);
    
    return {
      config: clientConfig,
      qr: execSync(`qrencode -t UTF8 '${clientConfig}'`).toString()
    };
  }
}

module.exports = WireGuardService;
