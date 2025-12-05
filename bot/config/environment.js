// config/environment.js
const requiredEnvVars = [
  'TELEGRAM_TOKEN',
  'SERVER_IPV4',
  'WIREGUARD_PORT',
  'OUTLINE_API_PORT',
  'WIREGUARD_PUBLIC_KEY'
];

function validateEnvironment() {
  const missing = requiredEnvVars.filter(varName => !process.env[varName]);
  
  if (missing.length > 0) {
    console.error(`❌ Variables de entorno faltantes: ${missing.join(', ')}`);
    process.exit(1);
  }
}

validateEnvironment();

// Procesar usuarios autorizados
const authorizedUsersArray = process.env.AUTHORIZED_USERS?.split(',').map(id => id.trim()) || [];

// El ADMIN_ID es el primero de AUTHORIZED_USERS
const adminId = authorizedUsersArray.length > 0 ? authorizedUsersArray[0] : null;

module.exports = {
  TELEGRAM_TOKEN: process.env.TELEGRAM_TOKEN,
  
  // Configuración del servidor
  SERVER_IPV4: process.env.SERVER_IPV4,
  SERVER_IPV6: process.env.SERVER_IPV6,
  SERVER_IP: process.env.SERVER_IP,
  
  // WireGuard
  WIREGUARD_PORT: process.env.WIREGUARD_PORT,
  WIREGUARD_PUBLIC_KEY: process.env.WIREGUARD_PUBLIC_KEY,
  WIREGUARD_PATH: process.env.WIREGUARD_PATH,
  WIREGUARD_ENDPOINT: process.env.WIREGUARD_ENDPOINT,
  
  // Outline
  OUTLINE_API_URL: process.env.OUTLINE_API_URL,
  OUTLINE_API_SECRET: process.env.OUTLINE_API_SECRET,
  OUTLINE_API_PORT: process.env.OUTLINE_API_PORT,
  
  // Pi-hole
  PIHOLE_WEB_PORT: process.env.PIHOLE_WEB_PORT,
  PIHOLE_WEBPASS: process.env.PIHOLE_WEBPASS,
  PIHOLE_DNS: process.env.PIHOLE_DNS,
  
  // Admin y usuarios
  ADMIN_EMAIL: 'usipipo@etlgr.com',
  ADMIN_ID: adminId, // ← ID del primer usuario autorizado
  AUTHORIZED_USERS: authorizedUsersArray,
  LEGACY_AUTHORIZED_USERS: authorizedUsersArray
};
