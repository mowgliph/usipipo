// bot/config/environment.js
require('dotenv').config();

// =====================================================
// 🔧 UTILIDADES
// =====================================================

/**
 * Convierte variable tipo número, con fallback seguro.
 */
const toNumber = (value, fallback = null) => {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
};

/**
 * Convierte booleanos estilo ENV: "true", "1", "yes"
 */
const toBoolean = (value) => {
  if (!value) return false;
  return ['true', '1', 'yes', 'y'].includes(String(value).toLowerCase());
};

/**
 * Parsea listas separadas por comas o espacios.
 */
const parseList = (value) =>
  value
    ? value
        .split(/[\s,]+/)
        .map((v) => v.trim())
      .filter(Boolean)
    : [];

// =====================================================
// 🔒 VALIDACIÓN DE VARIABLES REQUERIDAS
// =====================================================

const REQUIRED_VARS = [
  'TELEGRAM_TOKEN',
  'SERVER_IPV4',
  'WIREGUARD_PORT',
  'WIREGUARD_PUBLIC_KEY',
  'OUTLINE_API_URL',
  'OUTLINE_API_PORT',
  'OUTLINE_API_SECRET',
  'NODE_ENV'
];

const validateEnv = () => {
  const missing = REQUIRED_VARS.filter((key) => !process.env[key]);

  if (missing.length > 0) {
    console.error('❌ Faltan variables críticas de entorno:\n');
    for (const key of missing) console.error(`   - ${key}`);
    console.error('\n⚠️ El sistema no puede iniciar sin estas variables.');
    throw new Error('Environment configuration incomplete');
  }
};

validateEnv();

// =====================================================
// 📦 CONFIGURACIÓN CENTRAL
// =====================================================

const AUTHORIZED_USERS = parseList(process.env.AUTHORIZED_USERS);
const ADMIN_ID = process.env.ADMIN_ID || AUTHORIZED_USERS[0] || null;

const config = {
  // 🌎 Entorno
  NODE_ENV: process.env.NODE_ENV || 'production',

  // 🤖 Telegram
  TELEGRAM_TOKEN: process.env.TELEGRAM_TOKEN,
  AUTHORIZED_USERS,
  ADMIN_ID,

  // 🖥 Servidor
  SERVER_IPV4: process.env.SERVER_IPV4,
  SERVER_IPV6: process.env.SERVER_IPV6 || null,
  SERVER_IP: process.env.SERVER_IP || process.env.SERVER_IPV4,

  // 🛑 Pi-hole
  PIHOLE_WEB_PORT: toNumber(process.env.PIHOLE_WEB_PORT, 80),
  PIHOLE_WEBPASS: process.env.PIHOLE_WEBPASS || '',
  PIHOLE_DNS: process.env.PIHOLE_DNS || '',

  // 🔐 WireGuard
  WIREGUARD_PORT: toNumber(process.env.WIREGUARD_PORT),
  WIREGUARD_PUBLIC_KEY: process.env.WIREGUARD_PUBLIC_KEY,
  WIREGUARD_ENDPOINT: process.env.WIREGUARD_ENDPOINT || null,
  WIREGUARD_PATH: process.env.WIREGUARD_PATH || '/config',

  // 🌐 Outline
  OUTLINE_API_URL: process.env.OUTLINE_API_URL,
  OUTLINE_API_SECRET: process.env.OUTLINE_API_SECRET,
  OUTLINE_API_PORT: toNumber(process.env.OUTLINE_API_PORT),
  OUTLINE_KEYS_PORT: toNumber(process.env.OUTLINE_KEYS_PORT),
  OUTLINE_CERT_SHA256: process.env.OUTLINE_CERT_SHA256 || null,
  PRESERVE_CERTS: toBoolean(process.env.PRESERVE_CERTS)
};

// =====================================================
// 📣 LOGGING (solo si NO es entorno de test)
// =====================================================
if (config.NODE_ENV !== 'test') {
  console.log('✅ Variables de entorno cargadas correctamente');
  console.log(`🌎 Entorno         : ${config.NODE_ENV}`);
  console.log(`👑 Admin ID        : ${config.ADMIN_ID || 'No definido'}`);
  console.log(`👥 Autorizados     : ${config.AUTHORIZED_USERS.length}`);
  console.log(`🖥 IPv4 Servidor   : ${config.SERVER_IPV4}`);
  console.log(`🔐 Puerto WG       : ${config.WIREGUARD_PORT}`);
  console.log(`🌐 Outline API     : ${config.OUTLINE_API_URL}`);
}

module.exports = config;