// config/constants.js

/**
 * Constantes globales del sistema uSipipo VPN Bot.
 * Diseñado para ser inmutable y modular.
 */

const constants = Object.freeze({

  // =====================================================
  // 📦 Límites, rangos y configuración interna
  // =====================================================
  LIMITS: Object.freeze({
    OUTLINE_DEFAULT_DATA_LIMIT: 10 * 1024 * 1024 * 1024 // 10 GB
  }),

  NETWORK: Object.freeze({
    WIREGUARD_IP_RANGE: '10.13.13',
    WIREGUARD_IP_START: 2,
    WIREGUARD_IP_END: 254
  }),

  // =====================================================
  // 🔗 URLs externas (descargas y recursos)
  // =====================================================
  URLS: Object.freeze({
    WIREGUARD_DOWNLOAD: 'https://wireguard.com/install',
    OUTLINE_DOWNLOAD: 'https://getoutline.org/get-started'
  }),

  // =====================================================
  // 🧩 Estados y mensajes de estado del usuario
  // =====================================================
  STATUS: Object.freeze({
    AUTHORIZED: '✅ Autorizado',
    UNAUTHORIZED: '⛔ Sin autorización',
    PENDING: '⏳ Pendiente'
  }),

  // =====================================================
  // 🎨 Emojis globales para consistencia visual
  // =====================================================
  EMOJI: Object.freeze({
    SUCCESS: '✅',
    ERROR: '❌',
    WARNING: '⚠️',
    INFO: 'ℹ️',
    LOADING: '⏳',
    VPN: '🔐',
    SERVER: '🖥️',
    USER: '👤',
    ADMIN: '👑'
  })
});

module.exports = constants;