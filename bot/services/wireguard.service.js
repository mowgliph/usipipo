// services/wireguard.service.js
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);
const config = require('../config/environment');
const constants = require('../config/constants');
const formatters = require('../utils/formatters');

class WireGuardService {
  static async createNewClient() {
    try {
      // Generar claves
      const { stdout: privateKey } = await execPromise(
        'docker exec wireguard wg genkey'
      );
      const cleanPrivateKey = privateKey.trim();
      
      const { stdout: publicKey } = await execPromise(
        `docker exec wireguard sh -c "echo '${cleanPrivateKey}' | wg pubkey"`
      );
      const cleanPublicKey = publicKey.trim();
      
      // Obtener siguiente IP
      const clientIP = await this.getNextAvailableIP();
      
      // Agregar peer
      await this.addPeerToServer(cleanPublicKey, clientIP);
      
      // Generar configuración
      const clientConfig = this.generateClientConfig(clientIP, cleanPrivateKey);
      
      // Generar QR
      const { stdout: qrCode } = await execPromise(
        `echo '${clientConfig}' | docker exec -i wireguard qrencode -t UTF8`
      );
      
      return {
        config: clientConfig,
        qr: qrCode,
        clientIP: clientIP,
        publicKey: cleanPublicKey
      };
    } catch (error) {
      console.error('Error creating WireGuard client:', error);
      throw new Error(`WireGuard creation failed: ${error.message}`);
    }
  }

  static async getNextAvailableIP() {
    const { stdout: configContent } = await execPromise(
      'docker exec wireguard cat /config/wg_confs/wg0.conf'
    );
    
    const usedIPs = new Set();
    const ipRegex = new RegExp(`AllowedIPs\\s*=\\s*${constants.WIREGUARD_IP_RANGE}\\.(\\d+)\\/32`, 'g');
    let match;
    
    while ((match = ipRegex.exec(configContent)) !== null) {
      usedIPs.add(parseInt(match[1]));
    }
    
    for (let i = constants.WIREGUARD_IP_START; i <= constants.WIREGUARD_IP_END; i++) {
      if (!usedIPs.has(i)) {
        return `${constants.WIREGUARD_IP_RANGE}.${i}`;
      }
    }
    
    throw new Error('No available IP addresses in range');
  }

  static async addPeerToServer(publicKey, clientIP) {
    const peerConfig = `\n[Peer]\nPublicKey = ${publicKey}\nAllowedIPs = ${clientIP}/32\n`;
    
    await execPromise(
      `docker exec wireguard sh -c "echo '${peerConfig}' >> /config/wg_confs/wg0.conf"`
    );
    
    await execPromise(
      `docker exec wireguard wg set wg0 peer ${publicKey} allowed-ips ${clientIP}/32`
    );
    
    console.log(`✅ Peer added: ${clientIP}`);
  }

  static generateClientConfig(clientIP, privateKey) {
    const serverEndpoint = `${config.SERVER_IPV4}:${config.WIREGUARD_PORT}`;

    return `[Interface]
PrivateKey = ${privateKey}
Address = ${clientIP}/24
DNS = ${config.SERVER_IPV4}

[Peer]
PublicKey = ${config.WIREGUARD_SERVER_PUBLIC_KEY}
Endpoint = ${serverEndpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25`;
  }

  static async listClients() {
    const { stdout } = await execPromise('docker exec wireguard wg show wg0 dump');
    const lines = stdout.trim().split('\n').slice(1);
    
    return lines.map(line => {
      const [publicKey, , , allowedIPs, latestHandshake, rxBytes, txBytes] = line.split('\t');
      return {
        publicKey: publicKey.substring(0, 10) + '...',
        ip: allowedIPs.replace('/32', ''),
        lastSeen: formatters.formatTimestamp(latestHandshake),
        dataReceived: formatters.formatBytes(parseInt(rxBytes)),
        dataSent: formatters.formatBytes(parseInt(txBytes))
      };
    });
  }
}

module.exports = WireGuardService;
