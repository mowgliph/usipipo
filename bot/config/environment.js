// config/environment.js
const requiredEnvVars = [
  'TELEGRAM_TOKEN',
  'AUTHORIZED_USERS',
  'SERVER_IPV4',
  'WIREGUARD_PORT',
  'OUTLINE_API_PORT',
  'WIREGUARD_SERVER_PUBLIC_KEY'
];

// Validar variables de entorno requeridas
function validateEnvironment() {
  const missing = requiredEnvVars.filter(varName => !process.env[varName]);
  
  if (missing.length > 0) {
    console.error(`❌ Variables de entorno faltantes: ${missing.join(', ')}`);
    process.exit(1);
  }
}

validateEnvironment();

// Exportar configuración
const authorizedUsers = process.env.AUTHORIZED_USERS.split(',').map(id => id.trim());

module.exports = {
  TELEGRAM_TOKEN: process.env.TELEGRAM_TOKEN,
  AUTHORIZED_USERS: authorizedUsers,
  ADMIN_ID: authorizedUsers[0],
  
  // Configuración del servidor
  SERVER_IPV4: process.env.SERVER_IPV4,
  SERVER_IPV6: process.env.SERVER_IPV6,
  SERVER_IP: process.env.SERVER_IP,
  
  // WireGuard
  WIREGUARD_PORT: process.env.WIREGUARD_PORT,
  WIREGUARD_SERVER_PUBLIC_KEY: process.env.WIREGUARD_SERVER_PUBLIC_KEY,
  WIREGUARD_PATH: process.env.WIREGUARD_PATH,
  
  // Outline
  OUTLINE_API_URL: process.env.OUTLINE_API_URL,
  OUTLINE_API_SECRET: process.env.OUTLINE_API_SECRET,
  OUTLINE_API_PORT: process.env.OUTLINE_API_PORT,
  
  // Pi-hole
  PIHOLE_WEB_PORT: process.env.PIHOLE_WEB_PORT,
  PIHOLE_WEBPASS: process.env.PIHOLE_WEBPASS,
  PIHOLE_DNS: process.env.PIHOLE_DNS,
  
  // Admin contact
  ADMIN_EMAIL: 'usipipo@etlgr.com'
};
