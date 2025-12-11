'use strict';

/**
 * ============================================================================
 * ⌨️ INFO KEYBOARDS - uSipipo VPN Bot
 * ============================================================================
 * Teclados específicos para el módulo de información
 * ============================================================================
 */

const { Markup } = require('telegraf');

// ============================================================================
// 📊 MENÚ PRINCIPAL DE INFORMACIÓN
// ============================================================================

function getInfoMainKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🖥️ Sistema', 'info_system'),
      Markup.button.callback('🌐 Servidor', 'info_server')
    ],
    [
      Markup.button.callback('🔐 WireGuard', 'info_wireguard'),
      Markup.button.callback('🌐 Outline', 'info_outline')
    ],
    [
      Markup.button.callback('⚖️ Comparación', 'info_comparison'),
      Markup.button.callback('📡 Red', 'info_network')
    ],
    [
      Markup.button.callback('🛡️ Seguridad', 'info_security'),
      Markup.button.callback('📋 Política', 'info_policy')
    ],
    [
      Markup.button.callback('❓ FAQ', 'info_faq'),
      Markup.button.callback('🔧 Problemas', 'info_troubleshoot')
    ],
    [
      Markup.button.callback('📞 Contacto', 'info_contact'),
      Markup.button.callback('ℹ️ Acerca de', 'info_about')
    ],
    [Markup.button.callback('🏠 Menú Principal', 'back_to_menu')]
  ]);
}

// ============================================================================
// 🔐 SUBMENU: INFORMACIÓN VPN
// ============================================================================

function getVPNInfoKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔐 WireGuard', 'info_wireguard'),
      Markup.button.callback('🌐 Outline', 'info_outline')
    ],
    [
      Markup.button.callback('⚖️ Comparación', 'info_comparison')
    ],
    [
      Markup.button.callback('📱 Descargar Apps', 'info_download'),
      Markup.button.callback('🔧 Configurar', 'info_setup')
    ],
    [Markup.button.callback('◀️ Volver', 'info_main')]
  ]);
}

// ============================================================================
// 🛡️ SUBMENU: SEGURIDAD Y PRIVACIDAD
// ============================================================================

function getSecurityInfoKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔒 Cifrado', 'info_encryption'),
      Markup.button.callback('🚫 No-Logs', 'info_nologs')
    ],
    [
      Markup.button.callback('📋 Política Datos', 'info_policy'),
      Markup.button.callback('🛡️ Protección', 'info_protection')
    ],
    [Markup.button.callback('◀️ Volver', 'info_main')]
  ]);
}

// ============================================================================
// ❓ SUBMENU: AYUDA Y SOPORTE
// ============================================================================

function getHelpInfoKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('❓ FAQ', 'info_faq'),
      Markup.button.callback('🔧 Problemas', 'info_troubleshoot')
    ],
    [
      Markup.button.callback('📞 Contacto', 'info_contact'),
      Markup.button.callback('📚 Guías', 'info_guides')
    ],
    [Markup.button.callback('◀️ Volver', 'info_main')]
  ]);
}

// ============================================================================
// 📱 SUBMENU: DESCARGAS Y APPS
// ============================================================================

function getDownloadKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.url('📱 WireGuard iOS', 'https://apps.apple.com/app/wireguard/id1441195209'),
      Markup.button.url('🤖 WireGuard Android', 'https://play.google.com/store/apps/details?id=com.wireguard.android')
    ],
    [
      Markup.button.url('💻 WireGuard Windows', 'https://www.wireguard.com/install/'),
      Markup.button.url('🍎 WireGuard macOS', 'https://apps.apple.com/app/wireguard/id1451685025')
    ],
    [
      Markup.button.url('📱 Outline iOS', 'https://apps.apple.com/app/outline-app/id1356177741'),
      Markup.button.url('🤖 Outline Android', 'https://play.google.com/store/apps/details?id=org.outline.android.client')
    ],
    [
      Markup.button.url('💻 Outline Windows', 'https://s3.amazonaws.com/outline-releases/client/windows/stable/Outline-Client.exe'),
      Markup.button.url('🍎 Outline macOS', 'https://s3.amazonaws.com/outline-releases/client/macos/stable/Outline-Client.dmg')
    ],
    [Markup.button.callback('◀️ Volver', 'info_main')]
  ]);
}

// ============================================================================
// 📖 TECLADO CON BOTÓN DE VOLVER
// ============================================================================

function getBackToInfoKeyboard() {
  return Markup.inlineKeyboard([
    Markup.button.callback('◀️ Volver a Información', 'info_main')
  ]);
}

// ============================================================================
// 🔄 TECLADO DE NAVEGACIÓN RÁPIDA
// ============================================================================

function getQuickNavigationKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔐 VPN', 'info_vpn_menu'),
      Markup.button.callback('🛡️ Seguridad', 'info_security_menu')
    ],
    [
      Markup.button.callback('❓ Ayuda', 'info_help_menu'),
      Markup.button.callback('📱 Apps', 'info_download')
    ],
    [Markup.button.callback('🏠 Menú Principal', 'back_to_menu')]
  ]);
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // Main Keyboards
  getInfoMainKeyboard,
  getVPNInfoKeyboard,
  getSecurityInfoKeyboard,
  getHelpInfoKeyboard,
  getDownloadKeyboard,
  
  // Utility Keyboards
  getBackToInfoKeyboard,
  getQuickNavigationKeyboard
};
