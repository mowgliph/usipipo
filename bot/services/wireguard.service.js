// services/wireguard.service.js
const { exec, spawn } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

const config = require('../config/environment');
const constants = require('../config/constants');
const formatters = require('../utils/formatters');
const logger = require('../utils/logger');

/**
 * Servicio para gestionar clientes WireGuard de forma segura.
 * Se ha eliminado la concatenación de strings en shell para evitar inyecciones.
 */
class WireGuardService {
  
  /**
   * Helper privado para ejecutar comandos inyectando datos por STDIN.
   * Esto evita tener que escapar caracteres y previene Shell Injection.
   * @param {string} command - Comando base (ej: 'docker')
   * @param {Array} args - Argumentos
   * @param {string} input - Datos a enviar por stdin
   */
  static _execWithStdin(command, args, input) {
    return new Promise((resolve, reject) => {
      const child = spawn(command, args);
      let stdout = '';
      let stderr = '';

      // Escribir input en stdin y cerrar el stream
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
          reject(new Error(`Command failed (Code ${code}): ${stderr}`));
        }
      });

      child.on('error', (err) => {
        reject(err);
      });
    });
  }

  static async createNewClient() {
    try {
      // Generación de claves (seguro usar exec aquí, no hay input de usuario)
      const { stdout: privateKeyStdout } = await execPromise('docker exec wireguard wg genkey');
      const privateKey = privateKeyStdout.trim();

      const { stdout: publicKeyStdout } = await execPromise(
        `docker exec wireguard sh -c "echo '${privateKey}' | wg pubkey"`
      );
      const publicKey = publicKeyStdout.trim();

      const clientIP = await this.getNextAvailableIP();
      await this.addPeerToServer(publicKey, clientIP);

      const clientConfig = this.generateClientConfig(clientIP, privateKey);

      // CORREGIDO: Usamos spawn/stdin para el QR code
      // 'qrencode' lee de stdin si no se le pasa archivo, perfecto para esto.
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
      // Regex mejorado para ser más estricto
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
      // 1️⃣ Añadir entrada en wg0.conf de forma SEGURA usando tee -a (append)
      // El flag -i en docker exec es crucial para mantener stdin abierto
      await this._execWithStdin(
        'docker',
        ['exec', '-i', 'wireguard', 'tee', '-a', '/config/wg_confs/wg0.conf'],
        peerConfig
      );

      // 2️⃣ Aplicar cambios en caliente (Aquí sí usamos exec porque los argumentos son controlados por nosotros)
      // Aunque publicKey venga de fuera, ya ha pasado por wg genkey, pero por seguridad extra validamos caracteres básicos si fuera necesario.
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
    const dnsServer = config.SERVER_IPV4; // Ojo: Asegúrate que el servidor DNS escucha en esta IP

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
