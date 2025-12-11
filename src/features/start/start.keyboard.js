'use strict';

/**
 * ============================================================================
 * 🚀 START KEYBOARDS - uSipipo VPN Bot
 * ============================================================================
 * Teclados específicos para el módulo de inicio (/start)
 * Incluye bienvenidas, reintentos y acciones de error
 *
 * 📌 FUNCIONES PRINCIPALES:
 * - Teclados de bienvenida para diferentes tipos de usuario
 * - Teclado de reintento para errores
 * - Teclados de acción para callbacks
 * ============================================================================
 */

const { Markup } = require('telegraf');

// ============================================================================
// 🏠 TECLADOS REPLY (MENÚS DE BIENVENIDA)
// ============================================================================

/**
 * Teclado para usuarios no autorizados (esperando aprobación)
 */
function getUnauthorizedKeyboard() {
  return Markup.keyboard([
    ['🆘 Ayuda', 'ℹ️ Información']
  ])
  .resize()
  .oneTime();
}

/**
 * Teclado para usuarios autorizados (menú principal)
 */
function getAuthorizedKeyboard() {
  return Markup.keyboard([
    ['🔐 Conectar VPN', '📊 Mis Conexiones'],
    ['👤 Mi Perfil', '🆘 Ayuda'],
    ['⚙️ Configuración', 'ℹ️ Información']
  ])
  .resize()
  .oneTime();
}

/**
 * Teclado para administradores (menú principal con opciones admin)
 */
function getAdminKeyboard() {
  return Markup.keyboard([
    ['🔐 Conectar VPN', '📊 Mis Conexiones'],
    ['👤 Mi Perfil', '👑 Panel Admin'],
    ['⚙️ Configuración', 'ℹ️ Información'],
    ['🆘 Ayuda', '📈 Estadísticas']
  ])
  .resize()
  .oneTime();
}

// ============================================================================
// 🔄 TECLADO DE REINTENTO (PARA ERRORES)
// ============================================================================

/**
 * Teclado para reintentar operaciones fallidas
 */
function getRetryKeyboard() {
  return Markup.keyboard([
    ['🔄 Reintentar Inicio', '🆘 Ayuda'],
    ['ℹ️ Información', '📞 Contactar Admin']
  ])
  .resize()
  .oneTime();
}

// ============================================================================
// ❗ TECLADO DE ERROR
// ============================================================================

/**
 * Teclado para manejar errores de registro/inicio
 */
function getErrorKeyboard() {
  return Markup.keyboard([
    ['🔄 Reintentar', '🆘 Ayuda'],
    ['ℹ️ Información del Sistema']
  ])
  .resize()
  .oneTime();
}

// ============================================================================
// 🔘 TECLADOS INLINE (ACCIONES)
// ============================================================================

/**
 * Teclado inline para acciones de inicio
 */
function getStartActionKeyboard() {
  return Markup.inlineKeyboard([
    Markup.button.callback('🏠 Ir al Inicio', 'start_home'),
    Markup.button.callback('🆘 Ayuda', 'start_help'),
    Markup.button.callback('ℹ️ Información', 'start_info')
  ]);
}

/**
 * Teclado inline para confirmación de reintento
 */
function getRetryConfirmationKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('✅ Sí, reintentar', 'retry_confirm'),
      Markup.button.callback('❌ No, cancelar', 'retry_cancel')
    ],
    [Markup.button.callback('🆘 Ayuda', 'retry_help')]
  ]);
}

/**
 * Teclado inline para opciones de error
 */
function getErrorActionKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔄 Reintentar', 'error_retry'),
      Markup.button.callback('🆘 Ayuda', 'error_help')
    ],
    [
      Markup.button.callback('📞 Contactar Admin', 'error_contact'),
      Markup.button.callback('🏠 Volver al Inicio', 'error_home')
    ]
  ]);
}

// ============================================================================
// 🛠️ FUNCIONES UTILITARIAS
// ============================================================================

/**
 * Determina el teclado de bienvenida basado en el tipo de usuario
 * @param {boolean} isAdmin - Si el usuario es administrador
 * @param {boolean} isAuthorized - Si el usuario está autorizado
 * @returns {Object} Teclado de Markup
 */
function getWelcomeKeyboard(isAdmin = false, isAuthorized = true) {
  if (!isAuthorized) {
    return getUnauthorizedKeyboard();
  }

  if (isAdmin) {
    return getAdminKeyboard();
  }

  return getAuthorizedKeyboard();
}

/**
 * Elimina el teclado actual (para respuestas sin botones)
 */
function removeKeyboard() {
  return Markup.removeKeyboard();
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // Reply Keyboards
  getUnauthorizedKeyboard,
  getAuthorizedKeyboard,
  getAdminKeyboard,
  getRetryKeyboard,
  getErrorKeyboard,

  // Inline Keyboards
  getStartActionKeyboard,
  getRetryConfirmationKeyboard,
  getErrorActionKeyboard,

  // Utility Functions
  getWelcomeKeyboard,
  removeKeyboard
};