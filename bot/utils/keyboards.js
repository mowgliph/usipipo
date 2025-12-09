'use strict';

const { Markup } = require('telegraf');

/**
 * ============================================================================
 * 🎛️ Teclados Inline — uSipipo VPN Manager
 * UI estilo App: navegación limpia, profesional y coherente.
 * Refactorizado para incluir menús faltantes y prevenir crash.
 * ============================================================================
 */

const keyboards = {
  // ========================================================================
  // 🟢 MENÚ PRINCIPAL — Usuario Autorizado
  // ========================================================================
  homeAuthorized: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('🔐 VPN (WireGuard/Outline)', 'vpn_menu')],
      [
        Markup.button.callback('👤 Mi Info', 'show_my_info'),
        Markup.button.callback('📊 Estado Servidor', 'server_status')
      ],
      [Markup.button.callback('❓ Ayuda', 'help')]
    ]),

  // ========================================================================
  // 🔴 MENÚ PRINCIPAL — Usuario NO autorizado
  // ========================================================================
  homeUnauthorized: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('🔓 Solicitar Acceso', 'request_access')],
      [
        Markup.button.callback('🔄 Verificar Estado', 'check_status'),
        Markup.button.callback('❓ Ayuda', 'help')
      ]
    ]),

  // ========================================================================
  // 👤 MENÚ DE INFORMACIÓN DE USUARIO (Fix: Añadido para AuthHandler)
  // ========================================================================
  userInfoMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('🔄 Actualizar', 'show_my_info')],
      [Markup.button.callback('⬅️ Volver al Inicio', 'start')]
    ]),

  // ========================================================================
  // ❓ MENÚ DE AYUDA (Fix: Añadido para AuthHandler)
  // ========================================================================
  helpMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.url('🆘 Soporte Oficial', 'https://t.me/TuUsuarioDeSoporte')], // Cambia esto si tienes un canal/usuario real
      [Markup.button.callback('⬅️ Volver al Inicio', 'start')]
    ]),

  // ========================================================================
  // 📡 MENU GENERAL DE VPN
  // ========================================================================
  vpnMenu: () =>
    Markup.inlineKeyboard([
      [
        Markup.button.callback('🔐 WireGuard', 'wg_menu'),
        Markup.button.callback('🌐 Outline', 'outline_menu')
      ],
      [Markup.button.callback('📋 Listar Mis Clientes', 'list_clients')],
      [Markup.button.callback('⬅️ Volver al Inicio', 'start')]
    ]),

  // ========================================================================
  // 🔐 SUBMENÚ — WireGuard
  // ========================================================================
  wgMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('➕ Crear Nuevo', 'create_wg')],
      [
        Markup.button.callback('📥 Descargar .conf', 'wg_download'),
        Markup.button.callback('📱 Ver QR', 'wg_qr')
      ],
      [
        Markup.button.callback('👁️ Ver Config', 'wg_show'),
        Markup.button.callback('📉 Ver Consumo', 'wg_usage')
      ],
      [Markup.button.callback('🗑️ Eliminar Config', 'wg_delete')],
      [Markup.button.callback('⬅️ Volver', 'vpn_menu')]
    ]),

  // ========================================================================
  // 🌐 SUBMENÚ — Outline
  // ========================================================================
  outlineMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('➕ Crear Nueva Clave', 'create_outline')],
      [
        Markup.button.callback('🔗 Ver Enlace', 'outline_show'),
        Markup.button.callback('📉 Ver Consumo', 'outline_usage')
      ],
      [Markup.button.callback('🗑️ Eliminar Clave', 'outline_delete')],
      [Markup.button.callback('⬅️ Volver', 'vpn_menu')]
    ]),

  // ========================================================================
  // ⚠️ CONFIRMACIÓN Y NAVEGACIÓN
  // ========================================================================
  backButton: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('⬅️ Volver', 'vpn_menu')]
    ]),

  cancelButton: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('❌ Cancelar', 'cancel_action')]
    ]),

  // ========================================================================
  // ⌨️ MENÚ DE TEXTO (Fallback)
  // ========================================================================
  vpnSelectionMenu: () => {
    return Markup.keyboard([
      ['/start', '/help'],
      ['/miinfo', '/status']
    ]).resize().oneTime();
  }
};

module.exports = keyboards;
