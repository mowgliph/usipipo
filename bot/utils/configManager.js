const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

class ConfigManager {
  static getNextIP() {
    const usedIPs = new Set();
    const config = fs.readFileSync('/etc/wireguard/wg0.conf', 'utf8');
    
    // Extraer IPs existentes
    const peerRegex = /AllowedIPs\s*=\s*(\d+\.\d+\.\d+\.\d+)\/32/g;
    let match;
    while ((match = peerRegex.exec(config)) !== null) {
      usedIPs.add(match[1]);
    }

    // Encontrar próxima IP disponible (rango 10.10.10.2 - 10.10.10.254)
    for (let i = 2; i < 255; i++) {
      const ip = `10.10.10.${i}`;
      if (!usedIPs.has(ip)) return ip;
    }
    throw new Error('No IPs disponibles');
  }

  static generateWGConfig(clientIP, privateKey, publicKey) {
    const serverPublicKey = this.getServerPublicKey();
    const wgDns = process.env.SERVER_IPV4;
    const wgServerEndpoint = `${process.env.SERVER_IPV4}:${process.env.WIREGUARD_PORT}`;

    return `[Interface]
PrivateKey = ${privateKey}
Address = ${clientIP}/24
DNS = ${wgDns}

[Peer]
PublicKey = ${serverPublicKey}
Endpoint = ${wgServerEndpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25`;
  }

  static getServerPublicKey() {
    const config = fs.readFileSync('/etc/wireguard/wg0.conf', 'utf8');
    const lines = config.split('\n');
    let inInterface = false;
    for (const line of lines) {
      if (line.trim() === '[Interface]') {
        inInterface = true;
      } else if (line.trim() === '[Peer]') {
        inInterface = false;
      } else if (inInterface && line.startsWith('PublicKey')) {
        return line.split('=')[1].trim();
      }
    }
    throw new Error('Server public key not found in WireGuard config');
  }

  static addPeerToServer(publicKey, clientIP) {
    const config = fs.readFileSync('/etc/wireguard/wg0.conf', 'utf8');

    // Añadir nuevo peer al final
    const newPeer = `\n[Peer]
PublicKey = ${publicKey}
AllowedIPs = ${clientIP}/32
# ID: ${uuidv4()}\n`;

    fs.writeFileSync('/etc/wireguard/wg0.conf', config + newPeer);

    // Aplicar cambios sin reiniciar
    require('child_process').execSync(
      `wg set wg0 peer ${publicKey} allowed-ips ${clientIP}/32`,
      { stdio: 'inherit' }
    );
  }
}

module.exports = ConfigManager;
