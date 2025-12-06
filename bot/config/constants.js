// config/constants.js

/**
 * Constantes globales para la aplicación uSipipo VPN Bot.
 * Incluye límites, URLs, estados y emojis reutilizables.
 * @module constants
 * @exports {Object} - Objeto con todas las constantes
 */
module.exports = {
  /**
   * Límites de recursos
   */
  OUTLINE_DEFAULT_DATA_LIMIT: 10 * 1024 * 1024 * 1024, // 10 GB en bytes
  WIREGUARD_IP_RANGE: '10.13.13',
  WIREGUARD_IP_START: 2,
  WIREGUARD_IP_END: 254,

  /**
   * URLs de descarga y recursos externos
   */
  URLS: {
    WIREGUARD_DOWNLOAD: 'https://wireguard.com/install',
    OUTLINE_DOWNLOAD: 'https://getoutline.org/get-started'
  },

  /**
   * Mensajes de estado para notificaciones
   */
  STATUS: {
    AUTHORIZED: '✅ Autorizado',
    UNAUTHORIZED: '⛔ Sin autorización',
    PENDING: '⏳ Pendiente'
  },

  /**
   * Emojis reutilizables para consistencia visual
   */
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