// utils/keyboards.js
const { Markup } = require('telegraf');

/**
 * Colección de menús inline para el bot.
 * Todos los teclados están pensados para usarse con ctx.reply(...) o ctx.editMessageText(...).
 * @module keyboards
 * @exports {Object}
 */
const keyboards = {
  /**
   * Menú principal para usuarios autorizados.
   * @returns {Object} Teclado inline
   */
  mainMenuAuthorized: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('🔐 Crear WireGuard', 'create_wg')],
      [Markup.button.callback('🌐 Crear Outline', 'create_outline')],
      [Markup.button.callback('📊 Ver clientes activos', 'list_clients')],
      [Markup.button.callback('ℹ️ Estado del servidor', 'server_status')],
      [Markup.button.callback('❓ Ayuda', 'help')]
    ]),

  /**
   * Menú principal para usuarios no autorizados.
   * @returns {Object} Teclado inline
   */
  mainMenuUnauthorized: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('👤 Ver mis datos', 'show_my_info')],
      [Markup.button.callback('📧 Solicitar acceso', 'request_access')],
      [Markup.button.callback('🔍 Comprobar estado', 'check_status')]
    ]),

  /**
   * Menú genérico de confirmación/cancelación.
   * @param {string} actionId - ID de la acción a confirmar
   * @returns {Object} Teclado inline
   */
  confirmationMenu: (actionId) =>
    Markup.inlineKeyboard([
      [
        Markup.button.callback('✅ Confirmar', `confirm_${actionId}`),
        Markup.button.callback('❌ Cancelar', 'cancel')
      ]
    ]),

  /**
   * Menú rápido de selección de VPN.
   * @returns {Object} Teclado inline
   */
  vpnSelectionMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('🔐 WireGuard', 'create_wg')],
      [Markup.button.callback('🌐 Outline', 'create_outline')]
    ]),

  /**
   * Menú de administración.
   * @returns {Object} Teclado inline
   */
  adminMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('👥 Ver usuarios', 'admin_list_users')],
      [Markup.button.callback('📊 Estadísticas', 'admin_stats')],
      [Markup.button.callback('🔙 Volver', 'back_to_main')]
    ])
};

module.exports = keyboards;