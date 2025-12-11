'use strict';

const { Markup } = require('telegraf');

/**
 * ============================================================================
 * ⌨️ HELP KEYBOARDS - Teclados para navegación de ayuda
 * ============================================================================
 * Teclados inline organizados por categorías para fácil navegación.
 * Diseño intuitivo y responsive para Telegram.
 * ============================================================================
 */

class HelpKeyboards {
  // ==========================================================================
  // 🎯 TECLADO PRINCIPAL
  // ==========================================================================
  
  static mainHelpKeyboard() {
    return Markup.inlineKeyboard([
      [
        Markup.button.callback('🔐 VPN General', 'help_vpn_general'),
        Markup.button.callback('🛡️ WireGuard', 'help_vpn_wireguard')
      ],
      [
        Markup.button.callback('🌐 Outline', 'help_vpn_outline'),
        Markup.button.callback('👤 Perfil Usuario', 'help_user_profile')
      ],
      [
        Markup.button.callback('📊 Cuotas', 'help_user_quota'),
        Markup.button.callback('🔧 Problemas', 'help_troubleshooting')
      ],
      [
        Markup.button.callback('🛡️ Seguridad', 'help_security'),
        Markup.button.callback('📞 Contacto', 'help_contact')
      ],
      [
        Markup.button.callback('👮 Admin', 'help_admin'),
        Markup.button.callback('❌ Cerrar', 'help_close')
      ]
    ]);
  }

  // ==========================================================================
  // 🔐 TECLADOS VPN
  // ==========================================================================
  
  static vpnCategoryKeyboard() {
    return Markup.inlineKeyboard([
      [
        Markup.button.callback('🔐 General', 'help_vpn_general'),
        Markup.button.callback('🛡️ WireGuard', 'help_vpn_wireguard')
      ],
      [
        Markup.button.callback('🌐 Outline', 'help_vpn_outline'),
        Markup.button.callback('↩️ Volver', 'help_back_main')
      ]
    ]);
  }

  // ==========================================================================
  // 👤 TECLADOS USUARIO
  // ==========================================================================
  
  static userCategoryKeyboard() {
    return Markup.inlineKeyboard([
      [
        Markup.button.callback('👤 Perfil', 'help_user_profile'),
        Markup.button.callback('📊 Cuotas', 'help_user_quota')
      ],
      [
        Markup.button.callback('↩️ Volver', 'help_back_main')
      ]
    ]);
  }

  // ==========================================================================
  // 🛠️ TECLADOS TÉCNICOS
  // ==========================================================================
  
  static technicalCategoryKeyboard() {
    return Markup.inlineKeyboard([
      [
        Markup.button.callback('🔧 Problemas', 'help_troubleshooting'),
        Markup.button.callback('🛡️ Seguridad', 'help_security')
      ],
      [
        Markup.button.callback('↩️ Volver', 'help_back_main')
      ]
    ]);
  }

  // ==========================================================================
  // 📞 TECLADOS CONTACTO
  // ==========================================================================
  
  static contactCategoryKeyboard() {
    return Markup.inlineKeyboard([
      [
        Markup.button.callback('📞 Contacto', 'help_contact'),
        Markup.button.callback('👮 Admin', 'help_admin')
      ],
      [
        Markup.button.callback('↩️ Volver', 'help_back_main')
      ]
    ]);
  }

  // ==========================================================================
  // 👮 TECLADO ADMIN
  // ==========================================================================
  
  static adminCategoryKeyboard() {
    return Markup.inlineKeyboard([
      [
        Markup.button.callback('👮 Comandos Admin', 'help_admin')
      ],
      [
        Markup.button.callback('↩️ Volver', 'help_back_main')
      ]
    ]);
  }

  // ==========================================================================
  // 🔙 TECLADO DE REGRESO (Genérico)
  // ==========================================================================
  
  static backToMainKeyboard() {
    return Markup.inlineKeyboard([
      [Markup.button.callback('↩️ Volver al Menú Principal', 'help_back_main')]
    ]);
  }

  // ==========================================================================
  // 🎯 TECLADO DE CIERRE
  // ==========================================================================
  
  static closeHelpKeyboard() {
    return Markup.inlineKeyboard([
      [Markup.button.callback('❌ Cerrar Centro de Ayuda', 'help_close')]
    ]);
  }

  // ==========================================================================
  // 🔧 MÉTODOS UTILITARIOS
  // ==========================================================================
  
  static getKeyboardForSection(section) {
    const keyboardMap = {
      'vpn_general': this.vpnCategoryKeyboard(),
      'vpn_wireguard': this.vpnCategoryKeyboard(),
      'vpn_outline': this.vpnCategoryKeyboard(),
      'user_profile': this.userCategoryKeyboard(),
      'user_quota': this.userCategoryKeyboard(),
      'troubleshooting': this.technicalCategoryKeyboard(),
      'security': this.technicalCategoryKeyboard(),
      'contact': this.contactCategoryKeyboard(),
      'admin': this.adminCategoryKeyboard()
    };

    return keyboardMap[section] || this.backToMainKeyboard();
  }
}

module.exports = HelpKeyboards;
