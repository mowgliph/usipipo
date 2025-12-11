'use strict';

/**
 * ============================================================================
 * ⌨️ AUTH KEYBOARDS - uSipipo VPN Bot
 * ============================================================================
 * Teclados específicos para el módulo de autenticación.
 * ============================================================================
 */

const { Markup } = require('telegraf');

// ============================================================================
// 🔘 TECLADOS INLINE
// ============================================================================

/**
 * Teclado para acciones de autorización rápida (admin)
 */
function getQuickAuthActionsKeyboard(userId) {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('✅ Autorizar', `auth_approve_${userId}`),
      Markup.button.callback('❌ Rechazar', `auth_reject_${userId}`)
    ],
    [
      Markup.button.callback('ℹ️ Ver Info', `auth_info_${userId}`)
    ]
  ]);
}

/**
 * Teclado para gestión de usuario autorizado
 */
function getUserManagementKeyboard(userId) {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('👁️ Ver Perfil', `user_profile_${userId}`),
      Markup.button.callback('🔐 VPN', `user_vpn_${userId}`)
    ],
    [
      Markup.button.callback('✏️ Editar Rol', `user_role_${userId}`),
      Markup.button.callback('🗑️ Eliminar', `user_delete_${userId}`)
    ],
    [
      Markup.button.callback('🔙 Volver', 'admin_users')
    ]
  ]);
}

/**
 * Teclado para confirmación de autorización
 */
function getAuthConfirmationKeyboard(userId) {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('✅ Confirmar Autorización', `auth_confirm_${userId}`),
      Markup.button.callback('❌ Cancelar', 'auth_cancel')
    ]
  ]);
}

/**
 * Teclado para selección de rol al autorizar
 */
function getRoleSelectionKeyboard(userId) {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('👤 Usuario', `auth_role_user_${userId}`),
      Markup.button.callback('👑 Admin', `auth_role_admin_${userId}`)
    ],
    [
      Markup.button.callback('🔙 Cancelar', 'auth_cancel')
    ]
  ]);
}

/**
 * Teclado para lista de usuarios autorizados
 */
function getAuthorizedUsersListKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('➕ Agregar Usuario', 'auth_add_user'),
      Markup.button.callback('🔄 Actualizar', 'auth_refresh_list')
    ],
    [
      Markup.button.callback('📊 Estadísticas', 'auth_stats'),
      Markup.button.callback('🏠 Menú Admin', 'admin_menu')
    ]
  ]);
}

/**
 * Teclado para navegación en listado con paginación
 */
function getPaginatedUsersKeyboard(currentPage, totalPages) {
  const buttons = [];

  // Botones de navegación
  const navRow = [];
  if (currentPage > 1) {
    navRow.push(Markup.button.callback('⬅️ Anterior', `auth_page_${currentPage - 1}`));
  }
  
  navRow.push(Markup.button.callback(`📄 ${currentPage}/${totalPages}`, 'auth_page_current'));
  
  if (currentPage < totalPages) {
    navRow.push(Markup.button.callback('Siguiente ➡️', `auth_page_${currentPage + 1}`));
  }

  if (navRow.length > 0) {
    buttons.push(navRow);
  }

  // Botones de acción
  buttons.push([
    Markup.button.callback('🔄 Actualizar', 'auth_refresh_list'),
    Markup.button.callback('🏠 Menú', 'admin_menu')
  ]);

  return Markup.inlineKeyboard(buttons);
}

/**
 * Teclado de acciones post-autorización
 */
function getPostAuthActionsKeyboard(userId) {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔐 Configurar VPN', `vpn_setup_${userId}`),
      Markup.button.callback('📧 Enviar Mensaje', `user_message_${userId}`)
    ],
    [
      Markup.button.callback('👁️ Ver Usuario', `user_view_${userId}`),
      Markup.button.callback('🏠 Menú Admin', 'admin_menu')
    ]
  ]);
}

/**
 * Teclado de ayuda para usuarios no autorizados
 */
function getUnauthorizedHelpKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('ℹ️ Más Información', 'auth_help'),
      Markup.button.callback('🔄 Verificar Estado', 'auth_check_status')
    ]
  ]);
}

// ============================================================================
// 🏠 TECLADOS REPLY
// ============================================================================

/**
 * Teclado de espera para usuarios no autorizados
 */
function getUnauthorizedReplyKeyboard() {
  return Markup.keyboard([
    ['🔄 Verificar Estado', 'ℹ️ Información'],
    ['🆘 Ayuda']
  ])
  .resize()
  .persistent();
}

/**
 * Teclado simplificado para acciones de autorización (admin)
 */
function getAuthAdminReplyKeyboard() {
  return Markup.keyboard([
    ['➕ Autorizar Usuario', '📋 Lista de Usuarios'],
    ['📊 Estadísticas Auth', '🏠 Menú Admin']
  ])
  .resize();
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // Inline Keyboards
  getQuickAuthActionsKeyboard,
  getUserManagementKeyboard,
  getAuthConfirmationKeyboard,
  getRoleSelectionKeyboard,
  getAuthorizedUsersListKeyboard,
  getPaginatedUsersKeyboard,
  getPostAuthActionsKeyboard,
  getUnauthorizedHelpKeyboard,
  
  // Reply Keyboards
  getUnauthorizedReplyKeyboard,
  getAuthAdminReplyKeyboard
};
