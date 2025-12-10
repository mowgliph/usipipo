'use strict';

const { exec } = require('child_process');
const util = require('util');
const fs = require('fs').promises;
const path = require('path');

const execPromise = util.promisify(exec);

// ✅ NUEVAS IMPORTACIONES - Arquitectura refactorizada
const config = require('../../config/environment');
const logger = require('../../core/utils/logger');
const managerService = require('../../shared/services/manager.service');
const { formatBytes, escapeMarkdown } = require('../../core/utils/formatters');

/**
 * ============================================================================
 * 🛡️ WIREGUARD SERVICE - Refactorizado MVP 2025
 * ============================================================================
 *
 * ✅ CORRECCIONES APLICADAS:
 * 1. Eliminado singleton (ahora es clase normal)
 * 2. Integrado con manager.service (fuente única de verdad)
 * 3. Separación clara de responsabilidades
 * 4. Manejo de errores mejorado
 * 5. Compatible con nueva arquitectura
 *
 * 🎯 PATRÓN: Adapter para VPN Repository
 * ============================================================================
 */

class WireGuardService {
  constructor() {
    this.interface = config.WG_INTERFACE || 'wg0';
    this.confPath = config.WG_CONF_PATH || `/etc/wireguard/${this.interface}.conf`;
    this.clientsDir = config.WG_CLIENTS_DIR || `/etc/wireguard/clients`;
    this.defaultQuota = parseInt(process.env.WG_DEFAULT_QUOTA_BYTES) || (10 * 1024 * 1024 * 1024); // 10GB

    // Cache para performance
    this._cache = {
      serverPublicKey: null,
      serverConfig: null,
      lastUpdate: null
    };
  }

  // ============================================================================
  // 🔧 MÉTODOS DE CONFIGURACIÓN Y VALIDACIÓN
  // ============================================================================

  async validateEnvironment() {
    const checks = [
      { cmd: 'which wg', name: 'WireGuard CLI' },
      { cmd: 'which wg-quick', name: 'WG-Quick' },
      { cmd: `test -f ${this.confPath} && echo "exists"`, name: 'Config File' }
    ];

    const results = [];

    for (const check of checks) {
      try {
        await execPromise(check.cmd);
        results.push({ [check.name]: 'OK' });
      } catch (error) {
        results.push({ [check.name]: 'FAILED', error: error.message });
      }
    }

    const allOk = results.every(r => Object.values(r)[0] === 'OK');

    if (!allOk) {
      logger.error('[WireGuard] Validación de entorno fallida', { results });
      throw new Error('WireGuard no está correctamente instalado o configurado');
    }

    logger.info('[WireGuard] Entorno validado correctamente');
    return true;
  }

  async getServerInfo() {
    try {
      const [status, dump, configContent] = await Promise.all([
        execPromise(`wg show ${this.interface}`),
        execPromise(`wg show ${this.interface} dump`),
        fs.readFile(this.confPath, 'utf8').catch(() => '')
      ]);

      const lines = dump.stdout.trim().split('\n');
      const peerCount = Math.max(0, lines.length - 1); // Excluye header

      // Parsear IP del servidor
      const serverIpMatch = configContent.match(/Address\s*=\s*([\d\.\/:]+)/);
      const serverIp = serverIpMatch ? serverIpMatch[1] : 'No configurada';

      // Obtener clave pública del servidor
      const pubKeyMatch = configContent.match(/# Server Public Key:?\s*([A-Za-z0-9+/=]+)/);
      let serverPubKey = pubKeyMatch ? pubKeyMatch[1] : null;

      if (!serverPubKey) {
        // Intentar obtener dinámicamente
        try {
          const { stdout } = await execPromise(`wg show ${this.interface} public-key`);
          serverPubKey = stdout.trim();
        } catch (error) {
          serverPubKey = 'No disponible';
        }
      }

      return {
        interface: this.interface,
        serverIp,
        serverPublicKey: serverPubKey ? `${serverPubKey.substring(0, 16)}...` : 'No disponible',
        peerCount,
        status: status.stdout.includes('listening') ? '🟢 Activo' : '🔴 Inactivo',
        lastHandshake: lines.length > 1 ? 'Reciente' : 'Nunca',
        totalPeers: peerCount
      };
    } catch (error) {
      logger.error('[WireGuard] Error obteniendo info del servidor', error);
      return {
        interface: this.interface,
        status: '🔴 Error',
        error: error.message
      };
    }
  }

  // ============================================================================
  // 👤 MÉTODOS DE GESTIÓN DE CLIENTES (INTEGRADO CON MANAGER)
  // ============================================================================

  async createClient(userId, options = {}) {
    const startTime = Date.now();
    const user = managerService.getCompleteUser(userId);

    if (!user) {
      throw new Error(`Usuario ${userId} no encontrado en el sistema`);
    }

    // Validar que no tenga cliente existente
    if (user.wg && user.wg.clientName && !user.wg.suspended) {
      throw new Error('El usuario ya tiene una configuración WireGuard activa');
    }

    try {
      await this.validateEnvironment();

      // 1. Generar claves
      const { privateKey, publicKey, presharedKey } = await this._generateKeys();

      // 2. Obtener IP disponible
      const ipAssignment = await this._getAvailableIP();

      // 3. Obtener clave pública del servidor
      const serverPubKey = await this._getServerPublicKey();

      // 4. Crear configuración del cliente
      const clientConfig = this._buildClientConfig({
        privateKey,
        clientIp: ipAssignment.ipv4,
        clientIpv6: ipAssignment.ipv6,
        serverPublicKey: serverPubKey,
        presharedKey,
        dns: config.WG_CLIENT_DNS || '1.1.1.1, 1.0.0.1',
        endpoint: `${config.SERVER_IP || config.SERVER_IPV4}:${config.WG_SERVER_PORT || 51820}`,
        mtu: config.WG_MTU || 1420
      });

      // 5. Añadir peer al servidor
      await this._addPeerToServer({
        publicKey,
        presharedKey,
        allowedIps: ipAssignment.ipv6
          ? `${ipAssignment.ipv4}/32,${ipAssignment.ipv6}/128`
          : `${ipAssignment.ipv4}/32`
      });

      // 6. Guardar archivo de configuración
      const clientName = `tg_${String(userId).replace(/\D/g, '')}`;
      const filePath = await this._saveClientConfig(clientName, clientConfig);

      // 7. Generar QR si está disponible qrencode
      let qrCode = null;
      try {
        qrCode = await this._generateQRCode(clientConfig);
      } catch (error) {
        logger.debug('[WireGuard] QR code no generado', { error: error.message });
      }

      // 8. Actualizar en manager.service
      const wgData = {
        clientName,
        ipv4: ipAssignment.ipv4,
        ipv6: ipAssignment.ipv6 || null,
        publicKey,
        presharedKey: presharedKey || null,
        configFilePath: filePath,
        configContent: clientConfig,
        qrCode,
        createdAt: new Date().toISOString(),
        suspended: false,
        suspendedAt: null,
        lastSeen: null,
        dataReceived: 0,
        dataSent: 0
      };

      await managerService.setWireGuardData(userId, wgData);

      const duration = Date.now() - startTime;
      logger.info('[WireGuard] Cliente creado exitosamente', {
        userId,
        clientName,
        duration: `${duration}ms`,
        ip: ipAssignment.ipv4
      });

      return {
        success: true,
        clientName,
        ipv4: ipAssignment.ipv4,
        ipv6: ipAssignment.ipv6,
        config: clientConfig,
        qrCode,
        filePath,
        downloadUrl: `/download/wg/${clientName}.conf` // Para API futura
      };

    } catch (error) {
      logger.error('[WireGuard] Error creando cliente', {
        userId,
        error: error.message,
        stack: error.stack
      });

      // Limpiar recursos en caso de error
      await this._cleanupFailedCreation(userId).catch(() => {});

      throw new Error(`Error creando cliente WireGuard: ${error.message}`);
    }
  }

  async getClient(userId) {
    const user = managerService.getCompleteUser(userId);

    if (!user || !user.wg) {
      return null;
    }

    try {
      // Obtener estadísticas actualizadas
      const stats = await this._getClientStats(user.wg.publicKey);

      return {
        ...user.wg,
        stats: {
          dataReceived: stats.rx,
          dataSent: stats.tx,
          total: stats.rx + stats.tx,
          lastHandshake: stats.lastHandshake
        },
        quota: {
          limit: this.defaultQuota,
          used: stats.rx + stats.tx,
          percentage: ((stats.rx + stats.tx) / this.defaultQuota * 100).toFixed(1),
          exceeded: (stats.rx + stats.tx) >= this.defaultQuota
        }
      };
    } catch (error) {
      // Si no podemos obtener stats, devolver datos básicos
      return user.wg;
    }
  }

  async deleteClient(userId) {
    const user = managerService.getCompleteUser(userId);

    if (!user || !user.wg) {
      throw new Error('Usuario no tiene configuración WireGuard');
    }

    const { clientName, publicKey, configFilePath } = user.wg;

    try {
      // 1. Remover peer del servidor
      if (publicKey) {
        await execPromise(`wg set ${this.interface} peer ${publicKey} remove`);
      }

      // 2. Remover del archivo de configuración
      await this._removePeerFromConfig(clientName);

      // 3. Eliminar archivo de configuración
      if (configFilePath) {
        await fs.unlink(configFilePath).catch(() => {});
      }

      // 4. Actualizar manager.service
      await managerService.removeVpnData(userId, 'wg');

      logger.info('[WireGuard] Cliente eliminado', { userId, clientName });

      return {
        success: true,
        message: `Cliente WireGuard ${clientName} eliminado correctamente`
      };

    } catch (error) {
      logger.error('[WireGuard] Error eliminando cliente', {
        userId,
        error: error.message
      });

      throw new Error(`Error eliminando cliente: ${error.message}`);
    }
  }

  async suspendClient(userId, reason = 'Cuota excedida') {
    const user = managerService.getCompleteUser(userId);

    if (!user || !user.wg) {
      throw new Error('Usuario no tiene configuración WireGuard');
    }

    try {
      // 1. Remover peer temporalmente
      await execPromise(`wg set ${this.interface} peer ${user.wg.publicKey} remove`);

      // 2. Actualizar estado en manager
      await managerService.setWireGuardData(userId, {
        ...user.wg,
        suspended: true,
        suspendedAt: new Date().toISOString(),
        suspensionReason: reason
      });

      logger.warn('[WireGuard] Cliente suspendido', {
        userId,
        clientName: user.wg.clientName,
        reason
      });

      return true;
    } catch (error) {
      logger.error('[WireGuard] Error suspendiendo cliente', {
        userId,
        error: error.message
      });

      throw new Error(`Error suspendiendo cliente: ${error.message}`);
    }
  }

  async resumeClient(userId) {
    const user = managerService.getCompleteUser(userId);

    if (!user || !user.wg || !user.wg.suspended) {
      throw new Error('Usuario no tiene configuración WireGuard suspendida');
    }

    try {
      // 1. Re-añadir peer al servidor
      const allowedIps = user.wg.ipv6
        ? `${user.wg.ipv4}/32,${user.wg.ipv6}/128`
        : `${user.wg.ipv4}/32`;

      await execPromise(
        `wg set ${this.interface} peer ${user.wg.publicKey} allowed-ips ${allowedIps}`
      );

      // 2. Actualizar estado en manager
      await managerService.setWireGuardData(userId, {
        ...user.wg,
        suspended: false,
        suspendedAt: null,
        suspensionReason: null
      });

      logger.info('[WireGuard] Cliente reanudado', {
        userId,
        clientName: user.wg.clientName
      });

      return true;
    } catch (error) {
      logger.error('[WireGuard] Error reanudando cliente', {
        userId,
        error: error.message
      });

      throw new Error(`Error reanudando cliente: ${error.message}`);
    }
  }

  // ============================================================================
  // 📊 MÉTODOS DE MONITOREO Y ESTADÍSTICAS
  // ============================================================================

  async getAllClientsStats() {
    try {
      const { stdout } = await execPromise(`wg show ${this.interface} dump`);
      const lines = stdout.trim().split('\n').slice(1); // Saltar encabezado

      const stats = {};
      const users = managerService.getAllUsers();

      for (const line of lines) {
        const [publicKey, , , allowedIps, lastHandshake, rx, tx] = line.split('\t');

        // Buscar usuario por IP
        const ip = allowedIps.split(',')[0].replace('/32', '');
        const user = users.find(u => u.wg && u.wg.ipv4 === ip);

        if (user) {
          stats[user.id] = {
            publicKey: publicKey.substring(0, 16) + '...',
            ip,
            lastHandshake: lastHandshake !== '0'
              ? new Date(parseInt(lastHandshake) * 1000).toLocaleString()
              : 'Nunca',
            dataReceived: parseInt(rx),
            dataSent: parseInt(tx),
            total: parseInt(rx) + parseInt(tx),
            quotaPercentage: ((parseInt(rx) + parseInt(tx)) / this.defaultQuota * 100).toFixed(2)
          };
        }
      }

      return stats;
    } catch (error) {
      logger.error('[WireGuard] Error obteniendo estadísticas', error);
      return {};
    }
  }

  async checkAllQuotas() {
    const clients = await this.getAllClientsStats();
    const exceeded = [];

    for (const [userId, stats] of Object.entries(clients)) {
      if (stats.total >= this.defaultQuota) {
        exceeded.push({
          userId,
          ...stats,
          exceededBy: formatBytes(stats.total - this.defaultQuota)
        });
      }
    }

    return {
      totalClients: Object.keys(clients).length,
      quotaExceeded: exceeded.length,
      exceededClients: exceeded
    };
  }

  // ============================================================================
  // 🔒 MÉTODOS PRIVADOS (IMPLEMENTACIÓN INTERNA)
  // ============================================================================

  async _generateKeys() {
    try {
      const privateKey = (await execPromise('wg genkey')).stdout.trim();
      const publicKey = (await execPromise(`echo "${privateKey}" | wg pubkey`)).stdout.trim();

      let presharedKey = null;
      try {
        presharedKey = (await execPromise('wg genpsk')).stdout.trim();
      } catch (error) {
        logger.debug('[WireGuard] PSK no generado (opcional)', { error: error.message });
      }

      return { privateKey, publicKey, presharedKey };
    } catch (error) {
      logger.error('[WireGuard] Error generando claves', error);
      throw new Error('Error generando claves criptográficas');
    }
  }

  async _getAvailableIP() {
    try {
      const configContent = await fs.readFile(this.confPath, 'utf8');
      const baseIp = config.WG_SERVER_IPV4_NETWORK || '10.13.13.0';
      const baseParts = baseIp.split('.').slice(0, 3).join('.');

      // Buscar IPs usadas
      const usedIps = new Set();
      const regex = new RegExp(`AllowedIPs\\s*=\\s*${baseParts.replace(/\./g, '\\.')}\\.(\\d+)/32`, 'g');
      let match;

      while ((match = regex.exec(configContent)) !== null) {
        usedIps.add(parseInt(match[1]));
      }

      // Encontrar IP libre (2-254)
      for (let i = 2; i < 255; i++) {
        if (!usedIps.has(i)) {
          const result = { ipv4: `${baseParts}.${i}` };

          // Si hay IPv6 configurado
          if (config.WG_SERVER_IPV6_NETWORK) {
            const ipv6Base = config.WG_SERVER_IPV6_NETWORK.split('::')[0];
            result.ipv6 = `${ipv6Base}::${i}`;
          }

          return result;
        }
      }

      throw new Error('No hay direcciones IP disponibles en la red');
    } catch (error) {
      logger.error('[WireGuard] Error obteniendo IP disponible', error);
      throw new Error('Error asignando dirección IP');
    }
  }

  async _getServerPublicKey() {
    if (this._cache.serverPublicKey && this._cache.lastUpdate &&
        (Date.now() - this._cache.lastUpdate < 30000)) { // Cache 30 segundos
      return this._cache.serverPublicKey;
    }

    try {
      // Primero intentar de config
      if (config.WG_SERVER_PUBKEY && config.WG_SERVER_PUBKEY.length === 44) {
        this._cache.serverPublicKey = config.WG_SERVER_PUBKEY;
        this._cache.lastUpdate = Date.now();
        return this._cache.serverPublicKey;
      }

      // Obtener dinámicamente
      const { stdout } = await execPromise(`wg show ${this.interface} public-key`);
      const pubKey = stdout.trim();

      if (pubKey.length !== 44) {
        throw new Error('Clave pública del servidor inválida');
      }

      this._cache.serverPublicKey = pubKey;
      this._cache.lastUpdate = Date.now();

      return pubKey;
    } catch (error) {
      logger.error('[WireGuard] Error obteniendo clave pública del servidor', error);
      throw new Error('No se pudo obtener la clave pública del servidor');
    }
  }

  _buildClientConfig({ privateKey, clientIp, clientIpv6, serverPublicKey, presharedKey, dns, endpoint, mtu }) {
    const addresses = clientIpv6
      ? `${clientIp}/24, ${clientIpv6}/128`
      : `${clientIp}/24`;

    return `[Interface]
PrivateKey = ${privateKey}
Address = ${addresses}
DNS = ${dns}
MTU = ${mtu}

[Peer]
PublicKey = ${serverPublicKey}
${presharedKey ? `PresharedKey = ${presharedKey}` : ''}
Endpoint = ${endpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25`;
  }

  async _addPeerToServer({ publicKey, presharedKey, allowedIps }) {
    try {
      let cmd = `wg set ${this.interface} peer ${publicKey} allowed-ips ${allowedIps}`;

      if (presharedKey) {
        // Usar archivo temporal para PSK
        const tmpFile = `/tmp/wg_psk_${Date.now()}`;
        await fs.writeFile(tmpFile, presharedKey, { mode: 0o600 });
        cmd += ` preshared-key ${tmpFile}`;

        try {
          await execPromise(cmd);
        } finally {
          await fs.unlink(tmpFile).catch(() => {});
        }
      } else {
        await execPromise(cmd);
      }

      // Añadir al archivo de configuración persistente
      await this._appendPeerToConfig(publicKey, presharedKey, allowedIps);

    } catch (error) {
      logger.error('[WireGuard] Error añadiendo peer al servidor', {
        publicKey: publicKey.substring(0, 16) + '...',
        error: error.message
      });
      throw new Error('Error añadiendo cliente al servidor WireGuard');
    }
  }

  async _saveClientConfig(clientName, configContent) {
    const fileName = `${this.interface}-${clientName}.conf`;
    const filePath = path.join(this.clientsDir, fileName);

    try {
      await fs.mkdir(this.clientsDir, { recursive: true });
      await fs.writeFile(filePath, configContent, { mode: 0o600 });
      return filePath;
    } catch (error) {
      logger.error('[WireGuard] Error guardando configuración del cliente', {
        clientName,
        error: error.message
      });
      throw new Error('Error guardando archivo de configuración');
    }
  }

  async _generateQRCode(configContent) {
    try {
      const { stdout } = await execPromise(
        `echo "${configContent.replace(/"/g, '\\"')}" | qrencode -t ANSIUTF8`
      );
      return stdout;
    } catch (error) {
      throw new Error('qrencode no disponible o falló');
    }
  }

  async _getClientStats(publicKey) {
    try {
      const { stdout } = await execPromise(`wg show ${this.interface} dump`);
      const lines = stdout.trim().split('\n');

      for (const line of lines) {
        const cols = line.split('\t');
        if (cols[0] === publicKey) {
          return {
            rx: parseInt(cols[5] || 0),
            tx: parseInt(cols[6] || 0),
            lastHandshake: cols[4] !== '0'
              ? new Date(parseInt(cols[4]) * 1000).toLocaleString()
              : null
          };
        }
      }

      return { rx: 0, tx: 0, lastHandshake: null };
    } catch (error) {
      logger.debug('[WireGuard] Error obteniendo stats del cliente', {
        publicKey: publicKey.substring(0, 16) + '...',
        error: error.message
      });
      return { rx: 0, tx: 0, lastHandshake: null };
    }
  }

  async _appendPeerToConfig(publicKey, presharedKey, allowedIps) {
    try {
      const timestamp = new Date().toISOString();
      const comment = `\n# Peer added by uSipipo VPN Bot at ${timestamp}`;
      const peerBlock = `[Peer]\nPublicKey = ${publicKey}\n`;
      const presharedLine = presharedKey ? `PresharedKey = ${presharedKey}\n` : '';
      const allowedLine = `AllowedIPs = ${allowedIps}\n`;

      const content = comment + '\n' + peerBlock + presharedLine + allowedLine;

      await fs.appendFile(this.confPath, content, 'utf8');

      logger.debug('[WireGuard] Peer añadido al archivo de configuración', {
        publicKey: publicKey.substring(0, 16) + '...'
      });
    } catch (error) {
      logger.warn('[WireGuard] Error escribiendo en archivo de configuración', {
        error: error.message
      });
      // No lanzamos error porque el peer ya está activo en memoria
    }
  }

  async _removePeerFromConfig(clientName) {
    try {
      let content = await fs.readFile(this.confPath, 'utf8');
      // Buscar y remover sección del peer
      const regex = new RegExp(`# Peer.*${clientName}[\\s\\S]*?(?=\\n\\[|$)`, 'g');
      content = content.replace(regex, '');
      await fs.writeFile(this.confPath, content, 'utf8');
    } catch (error) {
      logger.warn('[WireGuard] Error limpiando archivo de configuración', {
        clientName,
        error: error.message
      });
    }
  }

  async _cleanupFailedCreation(userId) {
    try {
      await managerService.removeVpnData(userId, 'wg');
    } catch (error) {
      logger.debug('[WireGuard] Cleanup falló', { userId, error: error.message });
    }
  }
}

// Exportar como clase, no como singleton
module.exports = WireGuardService;