'use strict';

/**
 * ============================================================================
 * ⌨️ ADMIN KEYBOARDS - uSipipo VPN Bot
 * ============================================================================
 * Teclados específicos para el panel de administración.
 * ============================================================================
 */

const { Markup } = require('telegraf');

// ============================================================================
// 🏠 MENÚ PRINCIPAL ADMIN
// ============================================================================

function getAdminMainKeyboard() {
  return Markup.keyboard([
    ['👥 Usuarios', '📊 Estadísticas'],
    ['📢 Notificar', '🔧 Mantenimiento'],
    ['📝 Logs', '⚙️ Configuración'],
    ['🏠 Menú Principal']
  ])
  .resize()
  .oneTime();
}

// ============================================================================
// 👥 GESTIÓN DE USUARIOS
// ============================================================================

function getUserManagementKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('➕ Agregar', 'admin_user_add'),
      Markup.button.callback('📋 Listar', 'admin_user_list')
    ],
    [
      Markup.button.callback('🔍 Buscar', 'admin_user_search'),
      Markup.button.callback('👑 Promover', 'admin_user_promote')
    ],
    [
      Markup.button.callback('🗑️ Eliminar', 'admin_user_remove'),
      Markup.button.callback('⛔ Suspender', 'admin_user_suspend')
    ],
    [Markup.button.callback('🔙 Volver', 'admin_back')]
  ]);
}

function getUserDetailKeyboard(userId) {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('✏️ Editar', `admin_user_edit_${userId}`),
      Markup.button.callback('👑 Rol', `admin_user_role_${userId}`)
    ],
    [
      Markup.button.callback('🔐 WG', `admin_user_wg_${userId}`),
      Markup.button.callback('🌐 OL', `admin_user_ol_${userId}`)
    ],
    [
      Markup.button.callback('🗑️ Eliminar', `admin_user_delete_${userId}`),
      Markup.button.callback('⛔ Suspender', `admin_user_suspend_${userId}`)
    ],
    [Markup.button.callback('🔙 Volver', 'admin_user_list')]
  ]);
}

function getUserListPaginationKeyboard(currentPage, totalPages) {
  const buttons = [];

  if (currentPage > 1) {
    buttons.push(Markup.button.callback('⬅️ Anterior', `admin_users_page_${currentPage - 1}`));
  }

  buttons.push(Markup.button.callback(`📄 ${currentPage}/${totalPages}`, 'admin_users_page_current'));

  if (currentPage < totalPages) {
    buttons.push(Markup.button.callback('Siguiente ➡️', `admin_users_page_${currentPage + 1}`));
  }

  return Markup.inlineKeyboard([
    buttons,
    [Markup.button.callback('🔙 Volver', 'admin_back')]
  ]);
}

function getRoleSelectionKeyboard(userId) {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('👑 Admin', `admin_setrole_${userId}_admin`),
      Markup.button.callback('👤 User', `admin_setrole_${userId}_user`)
    ],
    [Markup.button.callback('❌ Cancelar', `admin_user_detail_${userId}`)]
  ]);
}

// ============================================================================
// 📊 ESTADÍSTICAS
// ============================================================================

function getStatsKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('👥 Usuarios', 'admin_stats_users'),
      Markup.button.callback('🔐 VPN', 'admin_stats_vpn')
    ],
    [
      Markup.button.callback('💾 Storage', 'admin_stats_storage'),
      Markup.button.callback('🖥️ Sistema', 'admin_stats_system')
    ],
    [
      Markup.button.callback('🔄 Actualizar', 'admin_stats_refresh'),
      Markup.button.callback('📊 Detallado', 'admin_stats_detailed')
    ],
    [Markup.button.callback('🔙 Volver', 'admin_back')]
  ]);
}

// ============================================================================
// 📢 NOTIFICACIONES
// ============================================================================

function getNotificationKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('📢 Broadcast', 'admin_notify_broadcast'),
      Markup.button.callback('👤 Individual', 'admin_notify_individual')
    ],
    [
      Markup.button.callback('👑 Admins', 'admin_notify_admins'),
      Markup.button.callback('👥 Usuarios', 'admin_notify_users')
    ],
    [Markup.button.callback('🔙 Volver', 'admin_back')]
  ]);
}

function getBroadcastConfirmKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('✅ Enviar', 'admin_broadcast_confirm'),
      Markup.button.callback('❌ Cancelar', 'admin_broadcast_cancel')
    ]
  ]);
}

// ============================================================================
// 🔧 MANTENIMIENTO
// ============================================================================

function getMaintenanceKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🧹 Limpiar Cache', 'admin_maint_cleanup'),
      Markup.button.callback('🔄 Reiniciar Jobs', 'admin_maint_restart_jobs')
    ],
    [
      Markup.button.callback('📊 Storage Stats', 'admin_maint_storage'),
      Markup.button.callback('🗑️ Datos Huérfanos', 'admin_maint_orphans')
    ],
    [
      Markup.button.callback('⚠️ Modo Mantenimiento', 'admin_maint_mode'),
      Markup.button.callback('🔄 Backup', 'admin_maint_backup')
    ],
    [Markup.button.callback('🔙 Volver', 'admin_back')]
  ]);
}

function getMaintenanceModeKeyboard(isEnabled) {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback(
        isEnabled ? '✅ Desactivar' : '⚠️ Activar',
        isEnabled ? 'admin_maint_mode_disable' : 'admin_maint_mode_enable'
      )
    ],
    [Markup.button.callback('🔙 Volver', 'admin_maint')]
  ]);
}

// ============================================================================
// 📝 LOGS
// ============================================================================

function getLogsKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('📄 Ver últimos', 'admin_logs_recent'),
      Markup.button.callback('🔍 Buscar', 'admin_logs_search')
    ],
    [
      Markup.button.callback('⚠️ Errores', 'admin_logs_errors'),
      Markup.button.callback('📊 Stats', 'admin_logs_stats')
    ],
    [
      Markup.button.callback('🗑️ Limpiar antiguos', 'admin_logs_cleanup'),
      Markup.button.callback('📥 Descargar', 'admin_logs_download')
    ],
    [Markup.button.callback('🔙 Volver', 'admin_back')]
  ]);
}

// ============================================================================
// ⚙️ CONFIGURACIÓN
// ============================================================================

function getConfigKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔐 WireGuard', 'admin_config_wg'),
      Markup.button.callback('🌐 Outline', 'admin_config_outline')
    ],
    [
      Markup.button.callback('🤖 Bot', 'admin_config_bot'),
      Markup.button.callback('📊 Quotas', 'admin_config_quotas')
    ],
    [
      Markup.button.callback('🔄 Reload ENV', 'admin_config_reload'),
      Markup.button.callback('💾 Backup Config', 'admin_config_backup')
    ],
    [Markup.button.callback('🔙 Volver', 'admin_back')]
  ]);
}

// ============================================================================
// 🔙 NAVEGACIÓN
// ============================================================================

function getBackToAdminKeyboard() {
  return Markup.inlineKeyboard([
    [Markup.button.callback('🔙 Volver al Panel Admin', 'admin_back')]
  ]);
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // Main
  getAdminMainKeyboard,
  
  // User Management
  getUserManagementKeyboard,
  getUserDetailKeyboard,
  getUserListPaginationKeyboard,
  getRoleSelectionKeyboard,
  
  // Statistics
  getStatsKeyboard,
  
  // Notifications
  getNotificationKeyboard,
  getBroadcastConfirmKeyboard,
  
  // Maintenance
  getMaintenanceKeyboard,
  getMaintenanceModeKeyboard,
  
  // Logs
  getLogsKeyboard,
  
  // Configuration
  getConfigKeyboard,
  
  // Navigation
  getBackToAdminKeyboard
};
