'use strict';

const { Markup } = require('telegraf');

module.exports = {

  /**
   * Teclado principal para Administradores
   */
  getAdminKeyboard: () => {
    return Markup.keyboard([
      ['🔐 Gestionar VPN', '👥 Usuarios'],
      ['📊 Estadísticas', '⚙️ Sistema'],
      ['🆘 Ayuda', '🆔 Mi Info']
    ]).resize();
  },

  /**
   * Teclado principal para Usuarios Autorizados
   */
  getUserKeyboard: () => {
    return Markup.keyboard([
      ['🔐 Mis Conexiones', '🆘 Ayuda'],
      ['🆔 Mi Info']
    ]).resize();
  },

  /**
   * Teclado (Inline) para usuarios NO autorizados
   * (Solo acciones básicas permitidas)
   */
  getGuestKeyboard: () => {
    return Markup.inlineKeyboard([
      [Markup.button.callback('🔄 Verificar Estado', 'check_status')]
    ]);
  }
};
