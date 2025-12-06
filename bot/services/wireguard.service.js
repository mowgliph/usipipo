// services/wireguard.service.js
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

const config = require('../config/environment');
const constants = require('../config/constants');
const formatters = require('../utils/formatters');
const logger = require('../utils/logger');

/**
 * Servicio para gestionar clientes y configuración del servidor WireGuard.
 * Interactúa con el contenedor Docker que aloja WireGuard.
 */
class WireGuardService {
  /**
   * Crea un nuevo cliente WireGuard en el servidor.
   * Genera claves, IP, actualiza wg0.conf y produce archivo + QR.
   */
  static async createNewClient() {
    try {
      const { stdout: privateKeyStdout } = await execPromise('docker exec wireguard wg genkey');
      const privateKey = privateKeyStdout.trim();

      const { stdout: publicKeyStdout } = await execPromise(
        `docker exec wireguard sh -c "echo '${privateKey}' | wg pubkey"`
      );
      const publicKey = publicKeyStdout.trim();

      const clientIP = await this.getNextAvailableIP();
      await this.addPeerToServer(publicKey, clientIP);

      const clientConfig = this.generateClientConfig(clientIP, privateKey);

      const { stdout: qrCode } = await execPromise(
        `echo '${clientConfig}' | docker exec -i wireguard qrencode -t UTF8`
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

  /**
   * Determina la próxima IP disponible dentro del rango configurado.
   */
  static async getNextAvailableIP() {
    try {
      const { stdout: configContent } = await execPromise(
        'docker exec wireguard cat /config/wg_confs/wg0.conf'
      );

      const usedIPs = new Set();
      const ipRegex = new RegExp(
        `AllowedIPs\\s*=\\s*${constants.WIREGUARD_IP_RANGE}\\.(\\d+)\\/32`,
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

  /**
   * Añade un Peer (cliente) nuevo a la configuración wg0.conf y lo aplica.
   */
  static async addPeerToServer(publicKey, clientIP) {
    const peerConfig = `[Peer]
PublicKey = ${publicKey}
AllowedIPs = ${clientIP}/32
`;
    try {
      // Escapar comillas simples correctamente para shell seguro
      const safePeerConfig = peerConfig.replace(/'/g, `'\\''`);

      // 1️⃣ Añadir entrada en wg0.conf dentro del contenedor
      await execPromise(
        `docker exec wireguard sh -c "echo '${safePeerConfig}' >> /config/wg_confs/wg0.conf"`
      );

      // 2️⃣ Aplicar cambios en caliente
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

  /**
   * Genera la configuración del cliente (.conf).
   */
  static generateClientConfig(clientIP, privateKey) {
    if (!config.SERVER_IPV4 || !config.WIREGUARD_PORT) {
      throw new Error('SERVER_IPV4 o WIREGUARD_PORT no están definidos en la configuración');
    }
    if (!config.WIREGUARD_PUBLIC_KEY) {
      throw new Error('WIREGUARD_PUBLIC_KEY no está definida en la configuración');
    }

    const serverEndpoint = `${config.SERVER_IPV4}:${config.WIREGUARD_PORT}`;
    const dnsServer = config.SERVER_IPV4;

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

  /**
   * Devuelve la lista de clientes activos del servidor.
   */
  static async listClients() {
    try {
      const { stdout } = await execPromise('docker exec wireguard wg show wg0 dump');
      const lines = stdout.trim().split('
').slice(1);

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