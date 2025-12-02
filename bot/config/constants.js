// config/constants.js
module.exports = {
  // Límites
  OUTLINE_DEFAULT_DATA_LIMIT: 10737418240, // 10GB en bytes
  WIREGUARD_IP_RANGE: '10.13.13',
  WIREGUARD_IP_START: 2,
  WIREGUARD_IP_END: 254,
  
  // URLs de descarga
  URLS: {
    WIREGUARD_DOWNLOAD: 'https://wireguard.com/install',
    OUTLINE_DOWNLOAD: 'https://getoutline.org/get-started'
  },
  
  // Mensajes de estado
  STATUS: {
    AUTHORIZED: '✅ Autorizado',
    UNAUTHORIZED: '⛔ Sin autorización',
    PENDING: '⏳ Pendiente'
  },
  
  // Emojis
  EMOJI: {
    SUCCESS: '✅',
    ERROR: '❌',
    WARNING: '⚠️',
    INFO: 'ℹ️',
    LOADING: '⏳',
    VPN: '🔐',
    SERVER: '🖥️',
    USER: '👤',
    ADMIN: '👑'
  }
};
