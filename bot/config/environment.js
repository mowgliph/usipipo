// bot/config/environment.js
require('dotenv').config();

const REQUIRED_VARS = [
  'TELEGRAM_TOKEN',
  'AUTHORIZED_USERS',
  'SERVER_IPV4',
  'SERVER_IP',
  'WIREGUARD_PORT',
  'WIREGUARD_PUBLIC_KEY',
  'WIREGUARD_ENDPOINT',
  'WIREGUARD_PATH',
  'OUTLINE_API_SECRET',
  'OUTLINE_API_PORT',
  'OUTLINE_KEYS_PORT',
  'OUTLINE_API_URL',
  'OUTLINE_CERT_SHA256',
  'NODE_ENV'
];

/**
 * Valida que las variables críticas estén presentes.
 * Lanza error en caso contrario para fallar rápido al arrancar.
 * @throws {Error} Si faltan variables requeridas
 */
const validateEnv = () => {
  const missing = REQUIRED_VARS.filter((key) => !process.env[key]);

  if (missing.length > 0) {
    console.error('Faltan variables de entorno requeridas:');
    missing.forEach((key) => console.error(`   - ${key}`));
    throw new Error('Configuración de entorno incompleta. Revisa tu archivo .env');
  }
};

validateEnv();

/**
 * Parsea lista de IDs de usuarios (separados por comas o espacios).
 * @param {string} value - Cadena de IDs a parsear
 * @returns {Array<string>} Lista de IDs limpios
 */
const parseUserList = (value) => {
  if (!value) return [];
  return value
    .split(/[\s,]+/)
    .map((v) => v.trim())
    .filter((v) => v.length > 0);
};

const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN;
const AUTHORIZED_USERS = parseUserList(process.env.AUTHORIZED_USERS);

// Por ahora tomamos el primer autorizado como ADMIN_ID por compatibilidad
const ADMIN_ID = process.env.ADMIN_ID || AUTHORIZED_USERS[0] || null;

const config = {
  // Entorno
  NODE_ENV: process.env.NODE_ENV || 'production',

  // Telegram
  TELEGRAM_TOKEN,
  AUTHORIZED_USERS,
  ADMIN_ID,

  // Servidor
  SERVER_IPV4: process.env.SERVER_IPV4,
  SERVER_IPV6: process.env.SERVER_IPV6 || null,
  SERVER_IP: process.env.SERVER_IP || process.env.SERVER_IPV4,

  // Pi-hole
  PIHOLE_WEB_PORT: Number(process.env.PIHOLE_WEB_PORT) || 80,
  PIHOLE_WEBPASS: process.env.PIHOLE_WEBPASS || '',
  PIHOLE_DNS: process.env.PIHOLE_DNS || '',

  // WireGuard
  WIREGUARD_PORT: Number(process.env.WIREGUARD_PORT),
  WIREGUARD_PUBLIC_KEY: process.env.WIREGUARD_PUBLIC_KEY,
  WIREGUARD_ENDPOINT: process.env.WIREGUARD_ENDPOINT,
  WIREGUARD_PATH: process.env.WIREGUARD_PATH || '/config',

  // Outline
  OUTLINE_API_SECRET: process.env.OUTLINE_API_SECRET,
  OUTLINE_API_PORT: Number(process.env.OUTLINE_API_PORT),
  OUTLINE_KEYS_PORT: Number(process.env.OUTLINE_KEYS_PORT),
  OUTLINE_API_URL: process.env.OUTLINE_API_URL,
  OUTLINE_CERT_SHA256: process.env.OUTLINE_CERT_SHA256,
  PRESERVE_CERTS: String(process.env.PRESERVE_CERTS).toLowerCase() === 'true'
};

// Logging condicional (omitir en test)
if (config.NODE_ENV !== 'test') {
  console.log('Configuración de entorno cargada correctamente');
  console.log(`Entorno: ${config.NODE_ENV}`);
  console.log(`Admin ID: ${config.ADMIN_ID || 'no definido'}`);
  console.log(`Usuarios autorizados: ${config.AUTHORIZED_USERS.length}`);
  console.log(`Servidor IPv4: ${config.SERVER_IPV4}`);
}

module.exports = config;