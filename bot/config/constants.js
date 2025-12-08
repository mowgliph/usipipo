/**
 * Constantes globales del sistema uSipipo VPN Bot.
 * Diseñado para ser totalmente inmutable, modular y consistente.
 */

const constants = Object.freeze({

  // =====================================================
  // 📦 Límites, rangos y configuración interna
  // =====================================================
  LIMITS: Object.freeze({
    // Límite de datos por defecto para Outline (10GB)
    OUTLINE_DEFAULT_DATA_LIMIT: 10 * 1024 * 1024 * 1024
  }),

  // =====================================================
  // 🌐 Redes internas asignadas para clientes WireGuard
  // (generación incremental de direcciones)
  // =====================================================
  NETWORK: Object.freeze({
    // Prefijo por defecto si no existe ENV
    WG_DEFAULT_PREFIX: '10.13.13.',

    // Rangos válidos de clientes
    WG_IP_START: 2,
    WG_IP_END: 254
  }),

  // =====================================================
  // 🔗 URLs externas oficiales
  // =====================================================
  URLS: Object.freeze({
    WIREGUARD_DOWNLOAD: 'https://www.wireguard.com/install/',
    OUTLINE_DOWNLOAD: 'https://getoutline.org/get-started'
  }),

  // =====================================================
  // 🧩 Estados del sistema y permisos
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