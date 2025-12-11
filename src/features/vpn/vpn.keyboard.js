'use strict';

/**
 * ============================================================================
 * ⌨️ VPN KEYBOARDS - uSipipo VPN Bot
 * ============================================================================
 * Teclados inline específicos para el módulo VPN.
 * Sigue el patrón de common.keyboard pero especializado en VPN.
 * ============================================================================
 */

const { Markup } = require('telegraf');

// ============================================================================
// 🏠 TECLADO PRINCIPAL VPN
// ============================================================================

/**
 * Menú principal de gestión VPN
 */
function getVPNMainMenuKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔐 WireGuard', 'vpn_wireguard_menu'),
      Markup.button.callback('🌐 Outline', 'vpn_outline_menu')
    ],
    [
      Markup.button.callback('📊 Mi Estado VPN', 'vpn_status_summary')
    ],
    [
      Markup.button.callback('ℹ️ Comparar Protocolos', 'vpn_compare'),
      Markup.button.callback('🆘 Ayuda VPN', 'vpn_help')
    ],
    [
      Markup.button.callback('🏠 Menú Principal', 'back_to_menu')
    ]
  ]);
}

/**
 * Selector de tipo de VPN (cuando se crea nueva conexión)
 */
function getVPNTypeSelectionKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔐 WireGuard', 'vpn_create_wireguard'),
      Markup.button.callback('🌐 Outline', 'vpn_create_outline')
    ],
    [
      Markup.button.callback('ℹ️ ¿Cuál elegir?', 'vpn_compare')
    ],
    [
      Markup.button.callback('« Volver', 'vpn_main_menu')
    ]
  ]);
}

// ============================================================================
// 🔐 TECLADOS WIREGUARD
// ============================================================================

/**
 * Menú principal de WireGuard
 */
function getWireGuardMenuKeyboard(hasConfig = false) {
  if (!hasConfig) {
    // Usuario sin configuración
    return Markup.inlineKeyboard([
      [Markup.button.callback('➕ Crear Configuración', 'vpn_wg_create')],
      [Markup.button.callback('ℹ️ ¿Qué es WireGuard?', 'vpn_wg_info')],
      [Markup.button.callback('« Volver al Menú VPN', 'vpn_main_menu')]
    ]);
  }
  
  // Usuario con configuración existente
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('👁️ Ver Config', 'vpn_wg_view'),
      Markup.button.callback('📊 Estadísticas', 'vpn_wg_stats')
    ],
    [
      Markup.button.callback('📄 Archivo .conf', 'vpn_wg_config_file'),
      Markup.button.callback('📱 Código QR', 'vpn_wg_qr')
    ],
    [
      Markup.button.callback('🔄 Renovar Config', 'vpn_wg_renew'),
      Markup.button.callback('🗑️ Eliminar', 'vpn_wg_delete_confirm')
    ],
    [
      Markup.button.callback('« Volver al Menú VPN', 'vpn_main_menu')
    ]
  ]);
}

/**
 * Confirmación de eliminación WireGuard
 */
function getWireGuardDeleteConfirmKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('✅ Sí, eliminar', 'vpn_wg_delete_confirm_yes'),
      Markup.button.callback('❌ Cancelar', 'vpn_wg_menu')
    ]
  ]);
}

/**
 * Acciones post-creación WireGuard
 */
function getWireGuardPostCreationKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('📱 Ver código QR', 'vpn_wg_qr'),
      Markup.button.callback('📄 Descargar .conf', 'vpn_wg_config_file')
    ],
    [
      Markup.button.callback('📖 Instrucciones', 'vpn_wg_instructions')
    ],
    [
      Markup.button.callback('✅ Entendido', 'vpn_wg_menu')
    ]
  ]);
}

// ============================================================================
// 🌐 TECLADOS OUTLINE
// ============================================================================

/**
 * Menú principal de Outline
 */
function getOutlineMenuKeyboard(hasKey = false) {
  if (!hasKey) {
    // Usuario sin clave
    return Markup.inlineKeyboard([
      [Markup.button.callback('➕ Crear Clave', 'vpn_outline_create')],
      [Markup.button.callback('ℹ️ ¿Qué es Outline?', 'vpn_outline_info')],
      [Markup.button.callback('« Volver al Menú VPN', 'vpn_main_menu')]
    ]);
  }
  
  // Usuario con clave existente
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔗 Ver Enlace', 'vpn_outline_view'),
      Markup.button.callback('📊 Estadísticas', 'vpn_outline_stats')
    ],
    [
      Markup.button.callback('✏️ Renombrar', 'vpn_outline_rename'),
      Markup.button.callback('🔄 Regenerar Enlace', 'vpn_outline_regenerate')
    ],
    [
      Markup.button.callback('🗑️ Eliminar', 'vpn_outline_delete_confirm')
    ],
    [
      Markup.button.callback('« Volver al Menú VPN', 'vpn_main_menu')
    ]
  ]);
}

/**
 * Confirmación de eliminación Outline
 */
function getOutlineDeleteConfirmKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('✅ Sí, eliminar', 'vpn_outline_delete_confirm_yes'),
      Markup.button.callback('❌ Cancelar', 'vpn_outline_menu')
    ]
  ]);
}

/**
 * Acciones post-creación Outline
 */
function getOutlinePostCreationKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔗 Copiar enlace', 'vpn_outline_view')
    ],
    [
      Markup.button.callback('📖 Instrucciones', 'vpn_outline_instructions')
    ],
    [
      Markup.button.callback('✅ Entendido', 'vpn_outline_menu')
    ]
  ]);
}

// ============================================================================
// 📊 TECLADOS DE ESTADÍSTICAS
// ============================================================================

/**
 * Teclado para vista de estadísticas
 */
function getStatsKeyboard(vpnType) {
  const prefix = vpnType === 'wireguard' ? 'wg' : 'outline';
  
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔄 Actualizar', `vpn_${prefix}_stats_refresh`)
    ],
    [
      Markup.button.callback('📈 Ver histórico', `vpn_${prefix}_stats_history`)
    ],
    [
      Markup.button.callback('« Volver', `vpn_${prefix}_menu`)
    ]
  ]);
}

/**
 * Teclado para resumen de estado VPN
 */
function getVPNSummaryKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔐 Gestionar WireGuard', 'vpn_wireguard_menu'),
      Markup.button.callback('🌐 Gestionar Outline', 'vpn_outline_menu')
    ],
    [
      Markup.button.callback('🔄 Actualizar estado', 'vpn_status_summary')
    ],
    [
      Markup.button.callback('« Volver al Menú VPN', 'vpn_main_menu')
    ]
  ]);
}

// ============================================================================
// 🆘 TECLADOS DE AYUDA E INFORMACIÓN
// ============================================================================

/**
 * Teclado de ayuda VPN
 */
function getVPNHelpKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔐 Ayuda WireGuard', 'vpn_help_wireguard'),
      Markup.button.callback('🌐 Ayuda Outline', 'vpn_help_outline')
    ],
    [
      Markup.button.callback('📱 Instalar apps', 'vpn_help_install')
    ],
    [
      Markup.button.callback('🔧 Solución problemas', 'vpn_help_troubleshoot')
    ],
    [
      Markup.button.callback('« Volver', 'vpn_main_menu')
    ]
  ]);
}

/**
 * Teclado de comparación de protocolos
 */
function getVPNCompareKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔐 Crear WireGuard', 'vpn_create_wireguard'),
      Markup.button.callback('🌐 Crear Outline', 'vpn_create_outline')
    ],
    [
      Markup.button.callback('« Volver', 'vpn_main_menu')
    ]
  ]);
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // Menús principales
  getVPNMainMenuKeyboard,
  getVPNTypeSelectionKeyboard,
  
  // WireGuard
  getWireGuardMenuKeyboard,
  getWireGuardDeleteConfirmKeyboard,
  getWireGuardPostCreationKeyboard,
  
  // Outline
  getOutlineMenuKeyboard,
  getOutlineDeleteConfirmKeyboard,
  getOutlinePostCreationKeyboard,
  
  // Estadísticas y resumen
  getStatsKeyboard,
  getVPNSummaryKeyboard,
  
  // Ayuda
  getVPNHelpKeyboard,
  getVPNCompareKeyboard
};
