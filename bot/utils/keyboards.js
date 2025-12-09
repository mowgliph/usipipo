'use strict';

const { Markup } = require('telegraf');

const keyboards = {
  // ... (Tus menús homeAuthorized y homeUnauthorized se quedan igual) ...
  homeAuthorized: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('🔐 VPN (WireGuard/Outline)', 'vpn_menu')],
      [
        Markup.button.callback('👤 Mi Info', 'show_my_info'),
        Markup.button.callback('📊 Estado Servidor', 'server_status')
      ],
      [Markup.button.callback('❓ Ayuda', 'help')]
    ]),

  homeUnauthorized: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('🔓 Solicitar Acceso', 'request_access')],
      [
        Markup.button.callback('🔄 Verificar Estado', 'check_status'),
        Markup.button.callback('❓ Ayuda', 'help')
      ]
    ]),

  userInfoMenu: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('🔄 Actualizar', 'show_my_info')],
      [Markup.button.callback('⬅️ Volver al Inicio', 'start')]
    ]),

  helpMenu: () =>
    Markup.inlineKeyboard([
      // Cambia la URL por tu contacto real
      [Markup.button.url('🆘 Soporte Oficial', 'https://t.me/TuUsuarioDeSoporte')],
      [Markup.button.callback('⬅️ Volver al Inicio', 'start')]
    ]),

  vpnMenu: () =>
    Markup.inlineKeyboard([
      [
        Markup.button.callback('🔐 WireGuard', 'wg_menu'),
        Markup.button.callback('🌐 Outline', 'outline_menu')
      ],
      [Markup.button.callback('📋 Listar Mis Clientes', 'list_clients')],
      [Markup.button.callback('⬅️ Volver al Inicio', 'start')]
    ]),

  // ... (wgMenu y outlineMenu se quedan igual) ...
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

  // === BOTONES DE NAVEGACIÓN ===

  // Úsalo dentro de menús profundos de VPN
  backButton: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('⬅️ Volver', 'vpn_menu')]
    ]),

  // NUEVO: Úsalo para Info, Ayuda o Estado del Servidor
  backToMain: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('⬅️ Volver al Inicio', 'start')]
    ]),

  cancelButton: () =>
    Markup.inlineKeyboard([
      [Markup.button.callback('❌ Cancelar', 'cancel_action')]
    ]),

  vpnSelectionMenu: () => {
    return Markup.keyboard([
      ['/start', '/help'],
      ['/miinfo', '/status']
    ]).resize().oneTime();
  }
};

module.exports = keyboards;
