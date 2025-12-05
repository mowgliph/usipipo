// utils/keyboards.js
const { Markup } = require('telegraf');

module.exports = {
  // Menú principal para usuarios autorizados
  mainMenuAuthorized: () => 
    Markup.inlineKeyboard([
      [Markup.button.callback('🔐 Crear WireGuard', 'create_wg')],
      [Markup.button.callback('🌐 Crear Outline', 'create_outline')],
      [Markup.button.callback('📊 Ver Clientes Activos', 'list_clients')],
      [Markup.button.callback('ℹ️ Estado del Servidor', 'server_status')],
      [Markup.button.callback('❓ Ayuda', 'help')]
    ]),

  // Menú para usuarios no autorizados
  mainMenuUnauthorized: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('👤 Ver mis datos', 'show_my_info')],
      [Markup.button.callback('📧 Solicitar acceso', 'request_access')],
      [Markup.button.callback('🔍 Comprobar Estado', 'check_status')]
    ]),

  // Menú de confirmación
  confirmationMenu: (actionId) =>
    Markup.inlineKeyboard([
      [
        Markup.button.callback('✅ Confirmar', `confirm_${actionId}`),
        Markup.button.callback('❌ Cancelar', 'cancel')
      ]
    ]),

  // Menú de administración
  adminMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('👥 Ver Usuarios', 'admin_list_users')],
      [Markup.button.callback('📊 Estadísticas', 'admin_stats')],
      [Markup.button.callback('🔙 Volver', 'back_to_main')]
    ])
};
