'use strict';

const { Markup } = require('telegraf');

/**
 * ============================================================================
 * 🎛️ Teclados Inline — uSipipo VPN Manager
 * UI estilo App: navegación limpia, profesional y coherente.
 * TODOS los handlers y comandos ya están adaptados a estas acciones.
 * ============================================================================
 */

const keyboards = {
  // ========================================================================
  // 🟢 MENÚ PRINCIPAL — Usuario Autorizado
  // ========================================================================
  mainMenuAuthorized: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('🔐 Crear VPN WireGuard', 'wg_create')],
      [Markup.button.callback('🌐 Crear VPN Outline', 'outline_create')],
      [Markup.button.callback('📁 Mis VPNs', 'vpn_menu')],
      [Markup.button.callback('🖥 Estado del Servidor', 'server_status')],
      [Markup.button.callback('❓ Ayuda', 'help')]
    ]),

  // ========================================================================
  // 🔴 MENÚ PRINCIPAL — Usuario NO autorizado
  // ========================================================================
  mainMenuUnauthorized: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('👤 Mis Datos', 'show_my_info')],
      [Markup.button.callback('📧 Solicitar Acceso', 'request_access')],
      [Markup.button.callback('🔍 Ver Estado', 'check_status')]
    ]),

  // ========================================================================
  // ⚠️ CONFIRMACIÓN DE ACCIONES DESTRUCTIVAS
  // ========================================================================
  confirmationMenu: (actionId) =>
    Markup.inlineKeyboard([
      [
        Markup.button.callback('✅ Confirmar', `confirm_${actionId}`),
        Markup.button.callback('❌ Cancelar', `cancel_${actionId}`)
      ]
    ]),

  // ========================================================================
  // 📡 MENU GENERAL DE VPN
  // ========================================================================
  vpnMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('🔐 WireGuard', 'wg_menu')],
      [Markup.button.callback('🌐 Outline', 'outline_menu')],
      [Markup.button.callback('📊 Mi consumo total', 'vpn_usage_total')],
      [Markup.button.callback('🔙 Volver al inicio', 'back_to_main')]
    ]),

  // ========================================================================
  // 🔐 SUBMENÚ — WireGuard
  // ========================================================================
  wgMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('⚡ Crear nueva configuración', 'wg_create')],
      [Markup.button.callback('📄 Ver configuración', 'wg_show')],
      [Markup.button.callback('📥 Descargar .conf', 'wg_download')],
      [Markup.button.callback('🔍 Ver código QR', 'wg_qr')],
      [Markup.button.callback('📈 Mi consumo', 'wg_usage')],
      [Markup.button.callback('🗑️ Eliminar mi configuración', 'wg_delete_confirm')],
      [Markup.button.callback('⬅️ Volver', 'vpn_menu')]
    ]),

  // ========================================================================
  // 🌐 SUBMENÚ — Outline
  // ========================================================================
  outlineMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('⚡ Crear nueva clave', 'outline_create')],
      [Markup.button.callback('🔗 Ver enlace', 'outline_show')],
      [Markup.button.callback('📈 Mi consumo', 'outline_usage')],
      [Markup.button.callback('🗑️ Eliminar clave', 'outline_delete_confirm')],
      [Markup.button.callback('⬅️ Volver', 'vpn_menu')]
    ]),

  // ========================================================================
  // 👑 MENU ADMINISTRADOR
  // ========================================================================
  adminMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('👥 Gestión de Usuarios', 'admin_users')],
      [Markup.button.callback('📊 Estadísticas del Servidor', 'admin_stats')],
      [Markup.button.callback('📢 Broadcast', 'admin_broadcast')],
      [Markup.button.callback('📨 Mensaje Directo', 'admin_sms')],
      [Markup.button.callback('📋 Plantillas', 'admin_templates')],
      [Markup.button.callback('🔙 Volver al inicio', 'back_to_main')]
    ]),

  // ========================================================================
  // Botón simple de volver
  // ========================================================================
  backButton: () =>
    Markup.inlineKeyboard([[Markup.button.callback('🔙 Volver', 'back_to_main')]])
};

module.exports = keyboards;