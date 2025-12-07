const { exec, spawn } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

const config = require('../config/environment');
const constants = require('../config/constants');
const formatters = require('../utils/formatters');
const logger = require('../utils/logger');

/**
 * Servicio para gestionar clientes WireGuard de forma segura.
 */
class WireGuardService {
  
  /**
   * Helper privado para ejecutar comandos inyectando datos por STDIN.
   */
  static _execWithStdin(command, args, input) {
    return new Promise((resolve, reject) => {
      const child = spawn(command, args);
      let stdout = '';
      let stderr = '';

      child.stdin.write(input);
      child.stdin.end();

      child.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      child.on('close', (code) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          // A veces qrencode escribe en stderr pero sale exit 0, o viceversa.
          // Si hay stdout, resolvemos aunque haya warning.
          if (stdout.length > 0) resolve(stdout);
          else reject(new Error(`Command failed (Code ${code}): ${stderr}`));
        }
      });

      child.on('error', (err) => {
        reject(err);
      });
    });
  }

  static async createNewClient() {
    try {
      // 1. Generar Private Key
      const { stdout: privateKeyStdout } = await execPromise('docker exec wireguard wg genkey');
      const privateKey = privateKeyStdout.trim();

      // 2. Generar Public Key
      const { stdout: publicKeyStdout } = await execPromise(
        `docker exec wireguard sh -c "echo '${privateKey}' | wg pubkey"`
      );
      const publicKey = publicKeyStdout.trim();

      // 3. Obtener IP y añadir Peer
      const clientIP = await this.getNextAvailableIP();
      await this.addPeerToServer(publicKey, clientIP);

      // 4. Generar Configuración del Cliente
      const clientConfig = this.generateClientConfig(clientIP, privateKey);

      // 5. Generar QR
      const qrCode = await this._execWithStdin(
        'docker', 
        ['exec', '-i', 'wireguard', 'qrencode', '-t', 'UTF8'], 
        clientConfig
      );

      logger.info('createNewClient', 'Cliente WireGuard creado', {
        clientIP,
        publicKey: `${publicKey.slice(0, 16)}...`,
      });

      return { config: clientConfig, qr: qrCode, clientIP, publicKey };
    } catch (error) {
      logger.error('WireGuardService.createNewClient', error);
      throw new Error(`WireGuard creation failed: ${error.message}`);
    }
  }

  static async getNextAvailableIP() {
    try {
      const { stdout: configContent } = await execPromise(
        'docker exec wireguard cat /config/wg_confs/wg0.conf'
      );

      const usedIPs = new Set();
      const ipRegex = new RegExp(
        `AllowedIPs\\s*=\\s*${constants.WIREGUARD_IP_RANGE.replace('.', '\\.')}\\.(\\d+)\\/32`,
        'g'
      );
      let match;

      while ((match = ipRegex.exec(configContent)) !== null) {
        usedIPs.add(parseInt(match[1], 10));
      }

      for (let i = constants.WIREGUARD_IP_START; i <= constants.WIREGUARD_IP_END; i++) {
        if (!usedIPs.has(i)) {
          const ip = `${constants.WIREGUARD_IP_RANGE}.${i}`;
          logger.debug('getNextAvailableIP', { nextIP: ip });
          return ip;
        }
      }

      throw new Error('No available IP addresses in configured WireGuard range');
    } catch (error) {
      logger.error('WireGuardService.getNextAvailableIP', error);
      throw error;
    }
  }

  static async addPeerToServer(publicKey, clientIP) {
    const peerConfig = `
[Peer]
PublicKey = ${publicKey}
AllowedIPs = ${clientIP}/32
`;
    try {
      await this._execWithStdin(
        'docker',
        ['exec', '-i', 'wireguard', 'tee', '-a', '/config/wg_confs/wg0.conf'],
        peerConfig
      );

      await execPromise(
        `docker exec wireguard wg set wg0 peer ${publicKey} allowed-ips ${clientIP}/32`
      );

      logger.verbose('addPeerToServer', {
        clientIP,
        publicKey: `${publicKey.slice(0, 16)}...`,
      });
    } catch (error) {
      logger.error('WireGuardService.addPeerToServer', error, { clientIP, publicKey });
      throw new Error(`Error adding peer to server: ${error.message}`);
    }
  }

  static generateClientConfig(clientIP, privateKey) {
    if (!config.SERVER_IPV4 || !config.WIREGUARD_PORT) {
      throw new Error('SERVER_IPV4 o WIREGUARD_PORT no están definidos en la configuración');
    }
    if (!config.WIREGUARD_PUBLIC_KEY) {
      throw new Error('WIREGUARD_PUBLIC_KEY no está definida en la configuración');
    }

    const serverEndpoint = `${config.SERVER_IPV4}:${config.WIREGUARD_PORT}`;
    
    // CORRECCIÓN 2: Usar DNS público (Cloudflare) para evitar problemas de firewall/bind locales.
    // Si usas la IP pública del servidor como DNS y el puerto 53 está cerrado desde fuera, no hay internet.
    const dnsServer = '1.1.1.1, 1.0.0.1'; 

    return `[Interface]
PrivateKey = ${privateKey}
Address = ${clientIP}/24
DNS = ${dnsServer}

[Peer]
PublicKey = ${config.WIREGUARD_PUBLIC_KEY}
Endpoint = ${serverEndpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25`;
  }

  static async listClients() {
    try {
      const { stdout } = await execPromise('docker exec wireguard wg show wg0 dump');
      const lines = stdout.trim().split('\n').slice(1);

      const clients = lines
        .map((line) => {
          const [publicKey, , , allowedIPs, latestHandshake, rxBytes, txBytes] = line.split('\t');
          if (!publicKey || !allowedIPs) return null;

          return {
            publicKey: `${publicKey.substring(0, 10)}...`,
            ip: allowedIPs.replace('/32', ''),
            lastSeen: formatters.formatTimestamp(Number(latestHandshake)),
            dataReceived: formatters.formatBytes(parseInt(rxBytes, 10)),
            dataSent: formatters.formatBytes(parseInt(txBytes, 10)),
          };
        })
        .filter(Boolean);

      logger.info('listClients', 'Clientes WireGuard listados', { count: clients.length });
      return clients;
    } catch (error) {
      logger.error('WireGuardService.listClients', error);
      throw new Error('Error obtaining WireGuard clients list');
    }
  }
}

module.exports = WireGuardService;
