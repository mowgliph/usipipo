'use strict';

/**
 * services/wireguard.service.js
 *
 * Servicio que integra WireGuard con el instalador oficial (wg_server.sh)
 * - No usa Docker
 * - Usa `wg`, `wg-quick`, `qrencode` (opcional)
 * - Guarda archivos de cliente en /etc/wireguard/clients/
 * - Enlaza clientes con usuarios en userManager (user.wg = {...})
 * - Restricción: 1 cliente por usuario normal (admins ilimitados)
 * - Cuota por cliente: 10 GB (configurable via DEFAULT_QUOTA_BYTES)
 *
 * REQUISITOS:
 * - El proceso Node debe poder ejecutar `wg` y editar /etc/wireguard/wg0.conf
 * - Tener `qrencode` instalado para generar ASCII QR (opcional)
 */

const { exec, spawn } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

const fs = require('fs').promises;
const path = require('path');

const config = require('../config/environment');
const logger = require('../utils/logger');
const userManager = require('./userManager.service');

const WG_INTERFACE = config.WG_INTERFACE || 'wg0';
const WG_CONF_PATH = path.join(config.WG_PATH || '/etc/wireguard', `${WG_INTERFACE}.conf`);
const CLIENTS_DIR = path.join(config.WG_PATH || '/etc/wireguard', 'clients');
const DEFAULT_QUOTA_BYTES = Number(process.env.WG_DEFAULT_QUOTA_BYTES) || 10 * 1024 * 1024 * 1024; // 10 GB

// Helper para ejecutar comandos con logging
async function runCmd(cmd, opts = {}) {
  try {
    logger.debug('runCmd', { cmd });
    const { stdout, stderr } = await execPromise(cmd, opts);
    return { stdout: stdout ? stdout.trim() : '', stderr: stderr ? stderr.trim() : '' };
  } catch (err) {
    logger.error('runCmd error', { cmd, message: err.message });
    throw err;
  }
}

class WireGuardService {
  constructor() {
    this.interface = WG_INTERFACE;
    this.confPath = WG_CONF_PATH;
    this.clientsDir = CLIENTS_DIR;
    this.defaultQuota = DEFAULT_QUOTA_BYTES;
  }

  // --------------------------------------------------
  // UTIL: comprobar que wg está disponible
  // --------------------------------------------------

  async _ensureTools() {
    // Chequeo simple: wg must be available
    try {
      await runCmd('which wg || true');
    } catch (err) {
      logger.warn('wg not found or check failed', { err: err.message });
    }
    
    // 1. Intentamos crear el directorio. Si el install.sh se ejecutó, esto debería
    //    funcionar sin problemas porque la carpeta ya existe y es propiedad del BOT_USER.
    try {
      await fs.mkdir(this.clientsDir, { recursive: true });
      logger.debug('Clients dir ensured via fs.mkdir.', { dir: this.clientsDir });

    } catch (err) {
      // 2. Si hay un fallo de permisos (EACCES) o cualquier otro, usamos 'sudo mkdir'
      //    para intentar arreglar la situación una última vez (requiere NOPASSWD).
      //    Esto actúa como un "auto-arreglo" si los permisos se corrompen.
      if (err.code === 'EACCES' || err.code === 'EPERM') {
         logger.warn('Permission denied creating clients dir. Attempting system fix...', { dir: this.clientsDir });
         try {
            await runCmd(`sudo mkdir -p ${this.clientsDir}`);
            await runCmd(`sudo chown -R $USER:$USER ${this.clientsDir} || sudo chown -R $LOGNAME:$LOGNAME ${this.clientsDir} || true`);
            logger.info('Clients dir created/fixed successfully via sudo.');
         } catch (fixErr) {
            logger.error('CRITICAL: Failed to create/fix clients dir even with sudo.', { dir: this.clientsDir, err: fixErr.message });
            throw new Error(`Fallo al crear ${this.clientsDir}: ${fixErr.message}. Verifica los permisos del usuario del bot en /etc/wireguard/clients.`);
         }
      } else {
        // Otros errores graves
        logger.error('Unable to create clients dir', { dir: this.clientsDir, err: err.message });
        throw err;
      }
    }
  }


  // --------------------------------------------------
  // UTIL: generar nombre de cliente a partir de telegram id
  // --------------------------------------------------
  _clientNameForUser(userId) {
    return `tg_${String(userId).replace(/\D/g, '')}`;
  }

  // --------------------------------------------------
  // UTIL: leer wg0.conf
  // --------------------------------------------------
  async _readWgConf() {
    try {
      const content = await fs.readFile(this.confPath, 'utf8');
      return content;
    } catch (err) {
      logger.error('readWgConf', err);
      throw new Error(`No se pudo leer ${this.confPath}: ${err.message}`);
    }
  }

  // --------------------------------------------------
  // UTIL: escribir wg0.conf temporal y reemplazar
  // --------------------------------------------------
  async _writeWgConfAtomic(content) {
    const tmp = `${this.confPath}.tmp`;
    await fs.writeFile(tmp, content, 'utf8');
    await fs.rename(tmp, this.confPath);
  }

  // --------------------------------------------------
  // GET NEXT AVAILABLE IP
  // --------------------------------------------------
  async getNextAvailableIP() {
    // base IP derivation: try config.WG_SERVER_IPV4 base like "10.13.13"
    const baseFromEnv = (config.WG_SERVER_IPV4 || '').trim();
    let base;
    if (baseFromEnv) {
      // can be "10.13.13.1/24" or "10.13.13.0/24"
      const m = baseFromEnv.match(/^(\d+\.\d+\.\d+)/);
      base = m ? m[1] : null;
    }

    if (!base) {
      // fallback: try to read from conf Address in Interface
      try {
        const conf = await this._readWgConf();
        const m = conf.match(/Address\s*=\s*([\d.]+)\/\d+/);
        if (m) {
          const parts = m[1].split('.');
          parts.pop();
          base = parts.join('.');
        }
      } catch (_) {
        base = null;
      }
    }

    if (!base) {
      throw new Error('No se pudo determinar la red base para asignar IP (WG_SERVER_IPV4 absent)');
    }

    // parse used ips from AllowedIPs entries
    const conf = await this._readWgConf();
    const regex = new RegExp(`AllowedIPs\\s*=\\s*${base.replace(/\./g,'\\.')}\\.(\\d+)\\/32`, 'g');
    const used = new Set();
    let match;
    while ((match = regex.exec(conf)) !== null) {
      used.add(Number(match[1]));
    }

    // search from 2..254
    for (let i = 2; i < 255; i++) {
      if (!used.has(i)) {
        return `${base}.${i}`;
      }
    }

    throw new Error('No hay IPs disponibles en el rango');
  }

  // --------------------------------------------------
  // GENERAR CONFIG CLIENT
  // --------------------------------------------------
  _buildClientConfig({ privateKey, clientIP, publicServerKey, presharedKey }) {
    const dns = config.SERVER_IPV4 || '8.8.8.8';
    const endpoint = `${config.SERVER_IPV4}:${config.WG_SERVER_PORT || '51820'}`;

    const clientConf =
`[Interface]
PrivateKey = ${privateKey}
Address = ${clientIP}/24
DNS = ${dns}

[Peer]
PublicKey = ${publicServerKey}
PresharedKey = ${presharedKey}
Endpoint = ${endpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
`;
    return clientConf;
  }

  // --------------------------------------------------
  // CREAR CLIENTE PARA UN USUARIO
  // --------------------------------------------------
  /**
   * createClientForUser(userId)
   * - verifica límites
   * - genera claves
   * - asigna IP
   * - añade Peer a wg0.conf y aplica live via wg set
   * - guarda .conf en clientsDir
   * - registra en userManager (user.wg = {...})
   *
   * Retorna: {
   *   clientName, ip, clientConfig, clientFilePath, qr (ascii|null), publicKey, presharedKey
   * }
   */
  async createClientForUser(userId) {
    await this._ensureTools();

    const uid = String(userId);
    const user = userManager.getUser(uid) || null;
    const isAdmin = userManager.isAdmin(uid);

    // Restricción: 1 cliente por usuario (si no admin)
    const existing = this.getUserClient(uid);
    if (existing && !isAdmin) {
      throw new Error('Ya existe una configuración WireGuard para este usuario. Elimina la actual para crear otra.');
    }

    // generar claves
    let privateKey, publicKey, presharedKey;
    try {
      const { stdout: priv } = await execPromise('wg genkey');
      privateKey = priv.trim();
      const pubProc = await execPromise(`echo "${privateKey}" | wg pubkey`);
      publicKey = pubProc.stdout.trim();

      try {
        const { stdout: pskOut } = await execPromise('wg genpsk');
        presharedKey = pskOut.trim();
      } catch (err) {
        // psk optional
        presharedKey = '';
        logger.debug('psk generation failed (optional)', { err: err.message });
      }
    } catch (err) {
      logger.error('Key generation failed', err);
      throw new Error('Error generando claves WireGuard: ' + err.message);
    }

    // asignar IP
    const clientIP = await this.getNextAvailableIP();

    // añadir peer block al conf
    // bloque con marcador para facilitar eliminación:
    // ### CLIENT tg_<id>
    // [Peer]...
    const peerBlock =
`\n### CLIENT ${this._clientNameForUser(uid)}\n[Peer]\nPublicKey = ${publicKey}\n` +
`PresharedKey = ${presharedKey || ''}\nAllowedIPs = ${clientIP}/32\n`;

    try {
      // append safe: read, append, write atomic
      const conf = await this._readWgConf();
      const newConf = conf + '\n' + peerBlock;
      await this._writeWgConfAtomic(newConf);

      // apply live via 'wg set <iface> peer <pubkey> allowed-ips <clientIP>/32'
      await runCmd(`wg set ${this.interface} peer ${publicKey} allowed-ips ${clientIP}/32`);
    } catch (err) {
      logger.error('addPeer failed', err);
      throw new Error('Error agregando peer al servidor WireGuard: ' + err.message);
    }

    // generar cliente .conf
    const clientConf = this._buildClientConfig({
      privateKey,
      clientIP,
      publicServerKey: config.WG_SERVER_PUBKEY || '',
      presharedKey
    });

    const clientName = `${this._clientNameForUser(uid)}`;
    const fileName = `${this.interface}-${clientName}.conf`;
    const filePath = path.join(this.clientsDir, fileName);

    try {
      await fs.writeFile(filePath, clientConf, { mode: 0o600 });
    } catch (err) {
      logger.error('write client file failed', err);
      throw new Error('No se pudo escribir el archivo de configuración del cliente: ' + err.message);
    }

    // intentar generar QR ASCII con qrencode si está disponible
    let qrAscii = null;
    try {
      // qrencode -t UTF8 -o - "clientConf"
      // usamos spawn para manejar stdin
      const qr = spawn('qrencode', ['-t', 'UTF8', '-o', '-'], { stdio: ['pipe', 'pipe', 'ignore'] });
      qr.stdin.write(clientConf);
      qr.stdin.end();

      // leer stdout (ASCII)
      const chunks = [];
      for await (const chunk of qr.stdout) chunks.push(chunk);
      const out = Buffer.concat(chunks).toString('utf8');
      qrAscii = out.trim();
    } catch (err) {
      // qrencode no disponible o fallo -> no crítico
      logger.debug('qrencode not available or failed', { message: err.message });
      qrAscii = null;
    }

    // Guardar mapping en userManager
    try {
      const u = userManager.getUser(uid) || { id: uid, addedAt: new Date().toISOString(), role: 'user', status: 'active' };
      u.wg = {
        clientName,
        ip: clientIP,
        clientFilePath: filePath,
        clientConfig: clientConf,
        publicKey,
        createdAt: new Date().toISOString()
      };
      // Ensure exists in map
      userManager.users = userManager.users || new Map(Object.entries({})); // defensive, if exported directly
      // userManager is a module with internal map; we have set/get functions; use addUser if not existing
      if (!userManager.getUser(uid)) {
        // add a minimal user record
        await userManager.addUser(uid, 'system', `TG ${uid}`);
      }
      // merge wg into existing user stored in userManager
      const stored = userManager.getUser(uid);
      stored.wg = u.wg;
      await userManager.saveUsers();

    } catch (err) {
      logger.error('userManager mapping failed', err);
      // no detener la creación: el peer ya está en el servidor, pero avisamos
    }

    logger.info('createClientForUser success', { userId: uid, clientName, ip: clientIP });

    return {
      clientName,
      ip: clientIP,
      clientConfig,
      clientFilePath: filePath,
      qr: qrAscii,
      publicKey,
      presharedKey
    };
  }

  // --------------------------------------------------
  // OBTENER CLIENTE VINCULADO A USUARIO
  // --------------------------------------------------
  getUserClient(userId) {
    const u = userManager.getUser(String(userId));
    if (!u) return null;
    return u.wg || null;
  }

  // --------------------------------------------------
  // LISTAR CLIENTES (parse wg show dump)
  // --------------------------------------------------
  async listClients() {
    try {
      // wg show wg0 dump
      const { stdout } = await execPromise(`wg show ${this.interface} dump`);
      const rows = stdout.split('\n').slice(1).filter(Boolean);
      const clients = rows.map(line => {
        const cols = line.split('\t');
        // Format: publickey\tprivatekey?...\t... allowedips\tlastHandshake?\trx\ttx
        // Defensive parsing based on typical `wg show <iface> dump`:
        const publicKey = cols[0] || '';
        const allowed = cols[3] || '';
        const lastSeen = cols[4] || '0';
        const rx = Number(cols[5] || 0);
        const tx = Number(cols[6] || 0);

        return {
          publicKey: publicKey.slice(0, 10) + '...',
          ip: allowed.replace('/32', ''),
          lastSeen,
          dataReceived: rx,
          dataSent: tx
        };
      });

      logger.info('listClients', { count: clients.length });
      return clients;
    } catch (err) {
      logger.error('listClients error', err);
      throw new Error('No se pudo listar clientes WireGuard: ' + err.message);
    }
  }

  // --------------------------------------------------
  // OBTENER USO POR NOMBRE DE CLIENTE (usa wg show dump)
  // --------------------------------------------------
  async getClientUsageByName(clientName) {
    try {
      // find user mapping with wg.clientName = clientName
      // We will search userManager for matching clientName
      const all = userManager.getAllUsers();
      let pubkey = null;
      for (const u of all) {
        if (u.wg && u.wg.clientName === clientName) {
          pubkey = u.wg.publicKey;
          break;
        }
      }

      if (!pubkey) {
        // fallback: parse wg show dump and find by AllowedIPs or by marker in conf
        const conf = await this._readWgConf();
        const match = conf.match(new RegExp(`### CLIENT ${clientName}[\\s\\S]*?PublicKey\\s*=\\s*([A-Za-z0-9+/=]+)`));
        if (match) pubkey = match[1];
      }

      if (!pubkey) {
        throw new Error('No se encontró la clave pública del cliente');
      }

      return await this.getClientUsageByPublicKey(pubkey);
    } catch (err) {
      logger.error('getClientUsageByName', err);
      throw err;
    }
  }

  async getClientUsageByPublicKey(publicKey) {
    try {
      const { stdout } = await execPromise(`wg show ${this.interface} dump`);
      const rows = stdout.split('\n').slice(1);
      for (const line of rows) {
        if (!line.trim()) continue;
        const cols = line.split('\t');
        const pk = cols[0];
        if (pk === publicKey) {
          const rx = Number(cols[5] || 0);
          const tx = Number(cols[6] || 0);
          return { rx, tx, total: rx + tx };
        }
      }
      return { rx: 0, tx: 0, total: 0 };
    } catch (err) {
      logger.error('getClientUsageByPublicKey', err);
      throw new Error('No se pudo obtener el uso del cliente: ' + err.message);
    }
  }

  // --------------------------------------------------
  // ELIMINAR CLIENTE POR NOMBRE (revoca peer y quita bloque del conf)
  // --------------------------------------------------
  async deleteClientByName(clientName) {
    try {
      const conf = await this._readWgConf();

      // buscar bloque del cliente por marcador
      const regex = new RegExp(`\\n### CLIENT ${clientName}[\\s\\S]*?\\n(?=(### CLIENT|$))`, 'g');
      const match = conf.match(new RegExp(`### CLIENT ${clientName}[\\s\\S]*?PublicKey\\s*=\\s*([A-Za-z0-9+/=]+)`));
      const pubkey = match ? match[1] : null;

      // eliminar bloque (si existe)
      const newConf = conf.replace(regex, '\n');

      if (newConf === conf) {
        // no encontrado por bloque, intentar buscar por client file mapping
        const all = userManager.getAllUsers();
        let clientUserId = null;
        for (const u of all) {
          if (u.wg && u.wg.clientName === clientName) {
            clientUserId = u.id;
            break;
          }
        }
        if (!pubkey && clientUserId) {
          pubkey = userManager.getUser(clientUserId).wg?.publicKey || null;
        }
      }

      // escribir conf sin el bloque
      await this._writeWgConfAtomic(newConf);

      // aplicar live: remove peer if pubkey known
      if (pubkey) {
        try {
          await runCmd(`wg set ${this.interface} peer ${pubkey} remove`);
        } catch (err) {
          logger.warn('wg remove peer failed', { pubkey, err: err.message });
        }
      }

      // borrar archivo cliente si existe
      const fileName = `${this.interface}-${clientName}.conf`;
      const filePath = path.join(this.clientsDir, fileName);
      try {
        await fs.unlink(filePath);
      } catch (_) {
        // no crítico
      }

      // eliminar mapping en userManager
      const allUsers = userManager.getAllUsers();
      for (const u of allUsers) {
        if (u.wg && u.wg.clientName === clientName) {
          delete u.wg;
        }
      }
      await userManager.saveUsers();

      logger.warn('deleteClientByName success', { clientName });
      return true;
    } catch (err) {
      logger.error('deleteClientByName error', err);
      throw new Error('No se pudo eliminar el cliente: ' + err.message);
    }
  }

  // --------------------------------------------------
  // hasQuotaExceededForUser
  // --------------------------------------------------
  async hasQuotaExceededForUser(userId) {
    try {
      const client = this.getUserClient(userId);
      if (!client) return false; // no client => no quota

      const usage = await this.getClientUsageByName(client.clientName);
      return (usage.total || 0) >= this.defaultQuota;
    } catch (err) {
      logger.error('hasQuotaExceededForUser', err);
      // en caso de error, no forzar quota
      return false;
    }
  }

  // --------------------------------------------------
  // enforceQuotaForUser -> revoca cliente y suspende usuario si excede y no admin
  // --------------------------------------------------
  async enforceQuotaForUser(userId) {
    try {
      const uid = String(userId);
      const user = userManager.getUser(uid);
      if (!user) return { enforced: false, reason: 'no_user' };

      if (user.role === 'admin') return { enforced: false, reason: 'is_admin' };

      const exceeded = await this.hasQuotaExceededForUser(uid);
      if (!exceeded) return { enforced: false, reason: 'within_quota' };

      const client = this.getUserClient(uid);
      if (client && client.clientName) {
        await this.deleteClientByName(client.clientName);
      }

      // suspend user
      await userManager.suspendUser(uid);

      logger.warn('Quota enforced: user suspended', { userId: uid });
      return { enforced: true };
    } catch (err) {
      logger.error('enforceQuotaForUser', err);
      return { enforced: false, error: err.message };
    }
  }

  // --------------------------------------------------
  // Método utilitario: check and enforce for all users (puede usarse por cron)
  // --------------------------------------------------
  async enforceQuotaForAllUsers() {
    const users = userManager.getAllUsers();
    const results = [];
    for (const u of users) {
      try {
        const res = await this.enforceQuotaForUser(u.id);
        results.push({ id: u.id, result: res });
      } catch (err) {
        results.push({ id: u.id, error: err.message });
      }
    }
    return results;
  }
}

module.exports = new WireGuardService();