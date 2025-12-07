// services/wireGuard.service.js
const { exec, spawn } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

const config = require('../config/environment');
const constants = require('../config/constants');
const formatters = require('../utils/formatters');
const logger = require('../utils/logger');

class WireGuardService {

  // --------------------------------------------------
  // HELPERS
  // --------------------------------------------------
  static dockerExec(cmd) {
    return execPromise(`docker exec wireguard ${cmd}`)
      .then(res => res.stdout.trim())
      .catch(err => {
        logger.error('dockerExec', { cmd, error: err.message });
        throw err;
      });
  }

  static _execWithStdin(command, args, input) {
    return new Promise((resolve, reject) => {
      const child = spawn(command, args);
      let stdout = '';
      let stderr = '';

      child.stdin.write(input);
      child.stdin.end();

      child.stdout.on('data', d => stdout += d.toString());
      child.stderr.on('data', d => stderr += d.toString());

      child.on('close', code => {
        // qrencode writes in stderr even when OK
        if (code === 0 || stdout.length > 0) {
          resolve(stdout || stderr);
        } else {
          reject(new Error(`Command failed (exit ${code}): ${stderr}`));
        }
      });

      child.on('error', reject);
    });
  }

  // --------------------------------------------------
  // NEW CLIENT CREATION
  // --------------------------------------------------
  static async createNewClient() {
    try {
      // 1) Private Key
      const privateKey = await this.dockerExec('wg genkey');

      // 2) Public Key
      const publicKey = await this.dockerExec(`sh -c "echo '${privateKey}' | wg pubkey"`);

      // 3) Client IP
      const clientIP = await this.getNextAvailableIP();
      await this.addPeerToServer(publicKey, clientIP);

      // 4) Client config
      const clientConfig = this.generateClientConfig(clientIP, privateKey);

      // 5) QR
      const qr = await this._execWithStdin(
        'docker',
        ['exec', '-i', 'wireguard', 'qrencode', '-t', 'UTF8'],
        clientConfig
      );

      logger.info('createNewClient', {
        clientIP,
        publicKey: `${publicKey.slice(0, 12)}...`
      });

      return { config: clientConfig, qr, clientIP, publicKey };

    } catch (err) {
      logger.error('WireGuardService.createNewClient', err);
      throw new Error(`WireGuard creation failed: ${err.message}`);
    }
  }

  // --------------------------------------------------
  // IP MANAGEMENT
  // --------------------------------------------------
  static async getNextAvailableIP() {
    try {
      const configContent = await this.dockerExec('cat /config/wg_confs/wg0.conf');

      const usedIPs = new Set();
      const base = constants.WIREGUARD_IP_RANGE.replace(/\./g, '\\.');
      const regex = new RegExp(`AllowedIPs\\s*=\\s*${base}\\.(\\d+)\\/32`, 'g');

      let match;
      while ((match = regex.exec(configContent)) !== null) {
        usedIPs.add(Number(match[1]));
      }

      for (let i = constants.WIREGUARD_IP_START; i <= constants.WIREGUARD_IP_END; i++) {
        if (!usedIPs.has(i)) {
          const ip = `${constants.WIREGUARD_IP_RANGE}.${i}`;
          logger.debug('getNextAvailableIP', { ip });
          return ip;
        }
      }

      throw new Error('No available IP addresses');

    } catch (err) {
      logger.error('WireGuardService.getNextAvailableIP', err);
      throw err;
    }
  }

  // --------------------------------------------------
  // PEER ADD
  // --------------------------------------------------
  static async addPeerToServer(publicKey, clientIP) {
    const peerBlock = `[Peer]
PublicKey = ${publicKey}
AllowedIPs = ${clientIP}/32
`;

    try {
      // Append to config file
      await this._execWithStdin(
        'docker',
        ['exec', '-i', 'wireguard', 'tee', '-a', '/config/wg_confs/wg0.conf'],
        peerBlock
      );

      // Apply live
      await this.dockerExec(`wg set wg0 peer ${publicKey} allowed-ips ${clientIP}/32`);

      logger.verbose('addPeerToServer', {
        clientIP,
        publicKey: publicKey.slice(0, 14) + '...'
      });

    } catch (err) {
      logger.error('WireGuardService.addPeerToServer', err, { publicKey, clientIP });
      throw new Error(`Error adding peer: ${err.message}`);
    }
  }

  // --------------------------------------------------
  // CLIENT CONFIG
  // --------------------------------------------------
  static generateClientConfig(clientIP, privateKey) {
    const { SERVER_IPV4, WIREGUARD_PORT, WIREGUARD_PUBLIC_KEY } = config;

    if (!SERVER_IPV4 || !WIREGUARD_PORT || !WIREGUARD_PUBLIC_KEY) {
      throw new Error('WireGuard environment variables missing');
    }

    const endpoint = `${SERVER_IPV4}:${WIREGUARD_PORT}`;

    // DNS recomendado
    const dns = '1.1.1.1, 1.0.0.1';

    return `[Interface]
PrivateKey = ${privateKey}
Address = ${clientIP}/24
DNS = ${dns}

[Peer]
PublicKey = ${WIREGUARD_PUBLIC_KEY}
Endpoint = ${endpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25`;
  }

  // --------------------------------------------------
  // LIST CLIENTS
  // --------------------------------------------------
  static async listClients() {
    try {
      const raw = await this.dockerExec('wg show wg0 dump');
      const rows = raw.split('\n').slice(1); // skip header

      const clients = rows
        .map(line => {
          if (!line.trim()) return null;

          const [publicKey, , , allowedIPs, lastSeen, rx, tx] = line.split('\t');
          if (!publicKey || !allowedIPs) return null;

          return {
            publicKey: `${publicKey.slice(0, 10)}...`,
            ip: allowedIPs.replace('/32', ''),
            lastSeen: formatters.formatTimestamp(Number(lastSeen)),
            dataReceived: formatters.formatBytes(Number(rx)),
            dataSent: formatters.formatBytes(Number(tx)),
          };
        })
        .filter(Boolean);

      logger.info('listClients', { count: clients.length });
      return clients;

    } catch (err) {
      logger.error('WireGuardService.listClients', err);
      throw new Error('Error getting WireGuard client list');
    }
  }
}

module.exports = WireGuardService;