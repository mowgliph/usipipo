'use strict';

/**
 * ============================================================================
 * ⌨️ HELP KEYBOARDS - uSipipo VPN Bot
 * ============================================================================
 * Teclados inline para navegación en el sistema de ayuda.
 * ============================================================================
 */

const { Markup } = require('telegraf');

// ============================================================================
// 🏠 MENÚ PRINCIPAL DE AYUDA
// ============================================================================

function getMainHelpKeyboard(isAdmin = false) {
  const buttons = [
    [
      Markup.button.callback('🔐 VPN', 'help_vpn'),
      Markup.button.callback('👤 Perfil', 'help_profile')
    ],
    [
      Markup.button.callback('ℹ️ Sistema', 'help_system'),
      Markup.button.callback('🔧 Problemas', 'help_troubleshooting')
    ],
    [
      Markup.button.callback('📋 Comandos', 'help_commands')
    ]
  ];

  if (isAdmin) {
    buttons.splice(2, 0, [
      Markup.button.callback('👑 Admin', 'help_admin')
    ]);
  }

  buttons.push([
    Markup.button.callback('🏠 Menú Principal', 'back_to_menu')
  ]);

  return Markup.inlineKeyboard(buttons);
}

// ============================================================================
// 🔙 BOTÓN DE REGRESO A AYUDA PRINCIPAL
// ============================================================================

function getBackToHelpKeyboard() {
  return Markup.inlineKeyboard([
    [Markup.button.callback('◀️ Volver a Ayuda', 'help_main')],
    [Markup.button.callback('🏠 Menú Principal', 'back_to_menu')]
  ]);
}

// ============================================================================
// 🔐 AYUDA VPN - NAVEGACIÓN
// ============================================================================

function getVPNHelpKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('📱 Descargar WireGuard', 'help_download_wg', true),
      Markup.button.callback('📱 Descargar Outline', 'help_download_outline', true)
    ],
    [
      Markup.button.callback('🎓 Tutorial WG', 'help_tutorial_wg'),
      Markup.button.callback('🎓 Tutorial Outline', 'help_tutorial_outline')
    ],
    [
      Markup.button.callback('❓ FAQ VPN', 'help_vpn_faq')
    ],
    [
      Markup.button.callback('◀️ Volver a Ayuda', 'help_main')
    ]
  ]);
}

// ============================================================================
// 🔧 SOLUCIÓN DE PROBLEMAS - NAVEGACIÓN
// ============================================================================

function getTroubleshootingKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔐 Problema WireGuard', 'help_issue_wg'),
      Markup.button.callback('🌐 Problema Outline', 'help_issue_outline')
    ],
    [
      Markup.button.callback('📊 Alto consumo', 'help_issue_data'),
      Markup.button.callback('🤖 Bot no responde', 'help_issue_bot')
    ],
    [
      Markup.button.callback('📞 Contactar Admin', 'help_contact_admin')
    ],
    [
      Markup.button.callback('◀️ Volver a Ayuda', 'help_main')
    ]
  ]);
}

// ============================================================================
// 👤 PERFIL - NAVEGACIÓN
// ============================================================================

function getProfileHelpKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('👁️ Ver mi perfil', 'profile_view'),
      Markup.button.callback('⚙️ Configuración', 'settings_view')
    ],
    [
      Markup.button.callback('📊 Mis estadísticas', 'stats_view')
    ],
    [
      Markup.button.callback('◀️ Volver a Ayuda', 'help_main')
    ]
  ]);
}

// ============================================================================
// 👑 ADMIN - NAVEGACIÓN (SOLO ADMINISTRADORES)
// ============================================================================

function getAdminHelpKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('👥 Gestión Usuarios', 'admin_users'),
      Markup.button.callback('🔐 Gestión VPN', 'admin_vpn')
    ],
    [
      Markup.button.callback('📋 Ver Logs', 'admin_logs'),
      Markup.button.callback('📢 Broadcast', 'admin_broadcast')
    ],
    [
      Markup.button.callback('💾 Backup', 'admin_backup'),
      Markup.button.callback('🧹 Cleanup', 'admin_cleanup')
    ],
    [
      Markup.button.callback('◀️ Volver a Ayuda', 'help_main')
    ]
  ]);
}

// ============================================================================
// ℹ️ SISTEMA - NAVEGACIÓN
// ============================================================================

function getSystemHelpKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('📊 Estado Sistema', 'system_status'),
      Markup.button.callback('ℹ️ Info Detallada', 'system_info')
    ],
    [
      Markup.button.callback('🏓 Ping', 'system_ping')
    ],
    [
      Markup.button.callback('◀️ Volver a Ayuda', 'help_main')
    ]
  ]);
}

// ============================================================================
// 📋 LISTA DE COMANDOS - NAVEGACIÓN
// ============================================================================

function getCommandsListKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔐 Comandos VPN', 'commands_vpn'),
      Markup.button.callback('👤 Comandos Usuario', 'commands_user')
    ],
    [
      Markup.button.callback('🖥️ Comandos Sistema', 'commands_system'),
      Markup.button.callback('👑 Comandos Admin', 'commands_admin')
    ],
    [
      Markup.button.callback('◀️ Volver a Ayuda', 'help_main')
    ]
  ]);
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  getMainHelpKeyboard,
  getBackToHelpKeyboard,
  getVPNHelpKeyboard,
  getTroubleshootingKeyboard,
  getProfileHelpKeyboard,
  getAdminHelpKeyboard,
  getSystemHelpKeyboard,
  getCommandsListKeyboard
};
