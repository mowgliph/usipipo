const { Markup } = require('telegraf');

/**
 * Colección de menús inline del bot.
 * Botones optimizados para estilo compacto y profesional.
 */

const keyboards = {
  /**
   * Menú principal (usuario autorizado)
   */
  mainMenuAuthorized: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('🔐 WireGuard', 'create_wg')],
      [Markup.button.callback('🌐 Outline', 'create_outline')],
      [Markup.button.callback('📊 Clientes', 'list_clients')],
      [Markup.button.callback('ℹ️ Servidor', 'server_status')],
      [Markup.button.callback('❓ Ayuda', 'help')]
    ]),

  /**
   * Menú principal (usuario no autorizado)
   */
  mainMenuUnauthorized: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('👤 Mis datos', 'show_my_info')],
      [Markup.button.callback('📧 Solicitar acceso', 'request_access')],
      [Markup.button.callback('🔍 Ver estado', 'check_status')]
    ]),

  /**
   * Menú de confirmación genérico
   */
  confirmationMenu: (actionId) =>
    Markup.inlineKeyboard([
      [
        Markup.button.callback('✅ Confirmar', `confirm_${actionId}`),
        Markup.button.callback('❌ Cancelar', 'cancel')
      ]
    ]),

  /**
   * Menú rápido de selección de VPN
   */
  vpnSelectionMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('🔐 WireGuard', 'create_wg')],
      [Markup.button.callback('🌐 Outline', 'create_outline')]
    ]),

  /**
   * Menú para administradores
   */
  adminMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('👥 Usuarios', 'admin_list_users')],
      [Markup.button.callback('📊 Estadísticas', 'admin_stats')],
      [Markup.button.callback('🔙 Volver', 'back_to_main')]
    ])
};

module.exports = keyboards;