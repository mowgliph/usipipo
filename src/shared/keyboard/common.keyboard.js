'use strict';

/**
 * ============================================================================
 * ⌨️ COMMON KEYBOARDS - uSipipo VPN Bot
 * ============================================================================
 * Teclados inline y reply reutilizables para todo el sistema.
 * 
 * 📌 PRINCIPIOS DE DISEÑO:
 * 1. Consistencia visual en todos los módulos
 * 2. Máximo 8 botones por fila (límite de Telegram)
 * 3. Iconos estándar para acciones comunes
 * 4. Teclados específicos por contexto
 * ============================================================================
 */

const { Markup } = require('telegraf');

// ============================================================================
// 🏠 TECLADOS REPLY (MENÚS PRINCIPALES)
// ============================================================================

/**
 * Menú principal para usuarios autorizados
 */
function getMainMenuKeyboard() {
  return Markup.keyboard([
    ['🔐 Conectar VPN', '📊 Mis Conexiones'],
    ['👤 Mi Perfil', '🆘 Ayuda'],
    ['⚙️ Configuración', 'ℹ️ Información']
  ])
  .resize()
  .oneTime();
}

/**
 * Menú principal para administradores (incluye opciones admin)
 */
function getAdminMainMenuKeyboard() {
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
// 🔘 TECLADOS INLINE (BOTONES BAJO MENSAJES)
// ============================================================================

/**
 * Teclado de confirmación (Sí/No)
 */
function getConfirmationKeyboard() {
  return Markup.inlineKeyboard([
    Markup.button.callback('✅ Sí', 'confirm_yes'),
    Markup.button.callback('❌ No', 'confirm_no')
  ]);
}

/**
 * Teclado para volver al menú principal
 */
function getBackToMenuKeyboard() {
  return Markup.inlineKeyboard([
    Markup.button.callback('🏠 Volver al Menú', 'back_to_menu')
  ]);
}

/**
 * Teclado para seleccionar tipo de VPN
 */
function getVPNTypeKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔐 WireGuard', 'vpn_wireguard'),
      Markup.button.callback('🌐 Outline', 'vpn_outline')
    ],
    [Markup.button.callback('🔄 Ambos', 'vpn_both')]
  ]);
}

/**
 * Teclado para selección de servidores (si hay múltiples)
 */
function getServerSelectionKeyboard(servers = []) {
  const buttons = servers.map((server, index) => {
    return Markup.button.callback(`🖥️ ${server.name}`, `server_${server.id}`);
  });

  // Agrupar en filas de 2
  const rows = [];
  for (let i = 0; i < buttons.length; i += 2) {
    rows.push(buttons.slice(i, i + 2));
  }

  // Añadir botón de cancelar
  rows.push([Markup.button.callback('❌ Cancelar', 'server_cancel')]);

  return Markup.inlineKeyboard(rows);
}

/**
 * Teclado para acciones de usuario (ver, editar, eliminar)
 */
function getUserActionsKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('👁️ Ver', 'user_view'),
      Markup.button.callback('✏️ Editar', 'user_edit')
    ],
    [
      Markup.button.callback('🗑️ Eliminar', 'user_delete'),
      Markup.button.callback('📋 Listar', 'user_list')
    ],
    [Markup.button.callback('🏠 Menú', 'back_to_menu')]
  ]);
}

/**
 * Teclado para acciones de conexión VPN
 */
function getVPNConnectionKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('➕ Nueva', 'vpn_new'),
      Markup.button.callback('📋 Listar', 'vpn_list')
    ],
    [
      Markup.button.callback('🔄 Renovar', 'vpn_renew'),
      Markup.button.callback('🚫 Eliminar', 'vpn_delete')
    ],
    [
      Markup.button.callback('📊 Estadísticas', 'vpn_stats'),
      Markup.button.callback('🔧 Configurar', 'vpn_configure')
    ]
  ]);
}

// ============================================================================
// 🛠️ FUNCIONES UTILITARIAS
// ============================================================================

/**
 * Elimina el teclado actual (para respuestas sin botones)
 */
function removeKeyboard() {
  return Markup.removeKeyboard();
}

/**
 * Teclado para cancelar acciones
 */
function getCancelKeyboard() {
  return Markup.inlineKeyboard([
    Markup.button.callback('❌ Cancelar', 'action_cancel')
  ]);
}

/**
 * Teclado para paginación (anterior/siguiente)
 */
function getPaginationKeyboard(currentPage, totalPages, prefix = 'page') {
  const buttons = [];

  if (currentPage > 1) {
    buttons.push(Markup.button.callback('⬅️ Anterior', `${prefix}_${currentPage - 1}`));
  }

  buttons.push(Markup.button.callback(`📄 ${currentPage}/${totalPages}`, 'page_current'));

  if (currentPage < totalPages) {
    buttons.push(Markup.button.callback('Siguiente ➡️', `${prefix}_${currentPage + 1}`));
  }

  return Markup.inlineKeyboard([buttons]);
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // Reply Keyboards
  getMainMenuKeyboard,
  getAdminMainMenuKeyboard,
  
  // Inline Keyboards
  getConfirmationKeyboard,
  getBackToMenuKeyboard,
  getVPNTypeKeyboard,
  getServerSelectionKeyboard,
  getUserActionsKeyboard,
  getVPNConnectionKeyboard,
  getCancelKeyboard,
  getPaginationKeyboard,
  
  // Utility Functions
  removeKeyboard
};