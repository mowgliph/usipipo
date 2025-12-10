// ============================================================================
// uSipipo VPN Manager - Environment Loader
// Sistema profesional de carga, validación y normalización de variables ENV
// ============================================================================

require('dotenv').config();

// ============================================================================
// 🔧 UTILIDADES
// ============================================================================

/**
 * Convierte a número seguro.
 */
const toNumber = (value, fallback = null) => {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
};

/**
 * Convierte un string estilo ENV a booleano.
 */
const toBoolean = (value) => {
  if (!value) return false;
  return ['true', '1', 'yes', 'y'].includes(String(value).toLowerCase());
};

/**
 * Parsea una lista separada por comas o espacios.
 */
const parseList = (value) =>
  value
    ? value
        .split(/[\s,]+/)
        .map((v) => v.trim())
        .filter(Boolean)
    : [];

// ============================================================================
// 🔒 LISTA DE VARIABLES OBLIGATORIAS
// ============================================================================
const REQUIRED_VARS = [
  // Telegram
  'TELEGRAM_TOKEN',

  // Servidor
  'SERVER_IPV4',
  'SERVER_IP',

  // WireGuard
  'WG_INTERFACE',
  'WG_SERVER_IPV4',
  'WG_SERVER_PORT',
  'WG_SERVER_PUBKEY',
  'WG_SERVER_PRIVKEY',
  'WG_ALLOWED_IPS',

  // Outline
  'OUTLINE_API_URL',
  'OUTLINE_API_PORT',
  'OUTLINE_KEYS_PORT',
  'OUTLINE_SERVER_IP',

  // Sistema
  'NODE_ENV'
];

const validateEnv = () => {
  const missing = REQUIRED_VARS.filter((key) => !process.env[key]);

  if (missing.length > 0) {
    console.error('❌ ERROR CRÍTICO: Variables de entorno faltantes:\n');
    missing.forEach((key) => console.error(`   - ${key}`));
    console.error('\n⚠️ El sistema no puede iniciar sin estas variables.');
    throw new Error('Environment configuration incomplete');
  }
};

validateEnv();

// ============================================================================
// 📦 CONFIGURACIÓN CENTRAL NORMALIZADA
// ============================================================================
const AUTHORIZED_USERS = parseList(process.env.AUTHORIZED_USERS);
const ADMIN_ID = process.env.ADMIN_ID || AUTHORIZED_USERS[0] || null;

const config = {
  // =====================================================
  // 🌎 Entorno
  // =====================================================
  NODE_ENV: process.env.NODE_ENV || 'production',
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',

  // =====================================================
  // 🤖 Telegram
  // =====================================================
  TELEGRAM_TOKEN: process.env.TELEGRAM_TOKEN,
  AUTHORIZED_USERS,
  ADMIN_ID,

  // =====================================================
  // 🖥 Información del servidor
  // =====================================================
  SERVER_IPV4: process.env.SERVER_IPV4,
  SERVER_IPV6: process.env.SERVER_IPV6 || null,
  SERVER_IP: process.env.SERVER_IP || process.env.SERVER_IPV4,

  // =====================================================
  // 🛑 Pi-hole (opcional)
  // =====================================================
  PIHOLE_WEB_PORT: toNumber(process.env.PIHOLE_WEB_PORT, 80),
  PIHOLE_WEBPASS: process.env.PIHOLE_WEBPASS || '',
  PIHOLE_DNS: process.env.PIHOLE_DNS || '',

  // =====================================================
  // 🔐 WireGuard (instalador oficial)
  // =====================================================
  WG_INTERFACE: process.env.WG_INTERFACE,
  WG_SERVER_IPV4: process.env.WG_SERVER_IPV4,
  WG_SERVER_IPV6: process.env.WG_SERVER_IPV6 || null,
  WG_SERVER_PORT: toNumber(process.env.WG_SERVER_PORT),

  WG_SERVER_PUBKEY: process.env.WG_SERVER_PUBKEY,
  WG_SERVER_PRIVKEY: process.env.WG_SERVER_PRIVKEY,

  WG_ALLOWED_IPS: process.env.WG_ALLOWED_IPS,

  WG_PATH: process.env.WG_PATH || '/etc/wireguard',

  // Endpoint real (auto-formado)
  WG_ENDPOINT:
    process.env.WG_ENDPOINT ||
    `${process.env.SERVER_IP}:${process.env.WG_SERVER_PORT}`,

  // =====================================================
  // 🌐 Outline Shadowbox
  // =====================================================
  OUTLINE_API_URL: process.env.OUTLINE_API_URL,
  OUTLINE_CERT_SHA256: process.env.OUTLINE_CERT_SHA256 || null,

  OUTLINE_API_PORT: toNumber(process.env.OUTLINE_API_PORT),
  OUTLINE_KEYS_PORT: toNumber(process.env.OUTLINE_KEYS_PORT),

  OUTLINE_SERVER_IP: process.env.OUTLINE_SERVER_IP,
  OUTLINE_DASHBOARD_URL:
    process.env.OUTLINE_DASHBOARD_URL ||
    `https://${process.env.OUTLINE_SERVER_IP}:9090`,

  // Preservar certificados de Outline
  PRESERVE_CERTS: toBoolean(process.env.PRESERVE_CERTS)
};

// ============================================================================
// 📣 LOGGING INICIAL (solo si no es test)
// ============================================================================
if (config.NODE_ENV !== 'test') {
  console.log('===============================================');
  console.log('  🔧 Variables de entorno cargadas (uSipipo)');
  console.log('===============================================');
  console.log(`🌎 Entorno:          ${config.NODE_ENV}`);
  console.log(`👑 Admin ID:         ${config.ADMIN_ID || 'No definido'}`);
  console.log(`👥 Autorizados:      ${config.AUTHORIZED_USERS.length}`);
  console.log(`🖥 IPv4 Servidor:    ${config.SERVER_IPV4}`);
  console.log(`🔐 Puerto WG:        ${config.WG_SERVER_PORT}`);
  console.log(`🌐 Outline API:      ${config.OUTLINE_API_URL}`);
  console.log('===============================================');
}

module.exports = config;