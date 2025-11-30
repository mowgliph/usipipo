// services/wireguard.js
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

class WireGuardService {
  static async createNewClient() {
    try {
      // Generar claves dentro del contenedor de WireGuard
      const { stdout: privateKey } = await execPromise(
        'docker exec wireguard wg genkey'
      );
      const cleanPrivateKey = privateKey.trim();
      
      const { stdout: publicKey } = await execPromise(
        `docker exec wireguard sh -c "echo '${cleanPrivateKey}' | wg pubkey"`
      );
      const cleanPublicKey = publicKey.trim();
      
      // Obtener siguiente IP disponible
      const clientIP = await this.getNextAvailableIP();
      
      // Agregar peer al servidor
      await this.addPeerToServer(cleanPublicKey, clientIP);
      
      // Generar configuración del cliente
      const clientConfig = this.generateClientConfig(clientIP, cleanPrivateKey);
      
      // Generar QR code
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
      'docker exec wireguard cat /config/wg0.conf'
    );
    
    const usedIPs = new Set();
    const ipRegex = /AllowedIPs\s*=\s*10\.13\.13\.(\d+)\/32/g;
    let match;
    
    while ((match = ipRegex.exec(configContent)) !== null) {
      usedIPs.add(parseInt(match[1]));
    }
    
    // Buscar primera IP disponible (2-254)
    for (let i = 2; i < 255; i++) {
      if (!usedIPs.has(i)) {
        return `10.13.13.${i}`;
      }
    }
    
    throw new Error('No available IP addresses in range');
  }

  static async addPeerToServer(publicKey, clientIP) {
    const peerConfig = `\n[Peer]\nPublicKey = ${publicKey}\nAllowedIPs = ${clientIP}/32\n`;
    
    await execPromise(
      `docker exec wireguard sh -c "echo '${peerConfig}' >> /config/wg0.conf"`
    );
    
    // Aplicar cambios en tiempo real
    await execPromise(
      `docker exec wireguard wg set wg0 peer ${publicKey} allowed-ips ${clientIP}/32`
    );
    
    console.log(`✅ Peer added: ${clientIP} with key ${publicKey.substring(0, 10)}...`);
  }

  static generateClientConfig(clientIP, privateKey) {
    const serverPublicKey = process.env.WIREGUARD_SERVER_PUBLIC_KEY;
    const serverEndpoint = `${process.env.SERVER_IPV4}:${process.env.WIREGUARD_PORT}`;
    const dnsServer = process.env.PIHOLE_DNS || '10.2.0.100';

    return `[Interface]
PrivateKey = ${privateKey}
Address = ${clientIP}/24
DNS = ${dnsServer}

[Peer]
PublicKey = ${serverPublicKey}
Endpoint = ${serverEndpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25`;
  }

  static async listClients() {
    const { stdout } = await execPromise('docker exec wireguard wg show wg0 dump');
    const lines = stdout.trim().split('\n').slice(1); // Saltar header
    
    return lines.map(line => {
      const [publicKey, , , allowedIPs, latestHandshake, rxBytes, txBytes] = line.split('\t');
      return {
        publicKey: publicKey.substring(0, 10) + '...',
        ip: allowedIPs.replace('/32', ''),
        lastSeen: latestHandshake === '0' ? 'Never' : new Date(parseInt(latestHandshake) * 1000).toLocaleString(),
        dataReceived: this.formatBytes(parseInt(rxBytes)),
        dataSent: this.formatBytes(parseInt(txBytes))
      };
    });
  }

  static formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}

module.exports = WireGuardService;
