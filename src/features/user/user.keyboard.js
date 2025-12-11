'use strict';

/**
 * ============================================================================
 * ⌨️ USER KEYBOARDS - uSipipo VPN Bot
 * ============================================================================
 * Teclados específicos para el módulo de usuario.
 * ============================================================================
 */

const { Markup } = require('telegraf');

// ============================================================================
// 👤 PERFIL DE USUARIO
// ============================================================================

function getProfileKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('📊 Estadísticas', 'profile_stats'),
      Markup.button.callback('⚙️ Preferencias', 'profile_preferences')
    ],
    [
      Markup.button.callback('✏️ Editar Perfil', 'profile_edit'),
      Markup.button.callback('🔄 Actualizar', 'profile_refresh')
    ],
    [
      Markup.button.callback('📋 Informe Mensual', 'profile_report'),
      Markup.button.callback('🏠 Menú', 'back_to_menu')
    ]
  ]);
}

function getProfileEditKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('👤 Nombre', 'edit_name'),
      Markup.button.callback('🌐 Idioma', 'edit_language')
    ],
    [
      Markup.button.callback('🔔 Notificaciones', 'edit_notifications'),
      Markup.button.callback('🔐 VPN Pref', 'edit_vpn_pref')
    ],
    [
      Markup.button.callback('❌ Cancelar', 'profile_cancel'),
      Markup.button.callback('✅ Guardar', 'profile_save')
    ]
  ]);
}

// ============================================================================
// ⚙️ PREFERENCIAS
// ============================================================================

function getPreferencesMainKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔐 VPN', 'pref_vpn'),
      Markup.button.callback('🔔 Notificaciones', 'pref_notifications')
    ],
    [
      Markup.button.callback('🎨 Interfaz', 'pref_interface'),
      Markup.button.callback('🛡️ Seguridad', 'pref_security')
    ],
    [
      Markup.button.callback('💾 Guardar Todo', 'pref_save_all'),
      Markup.button.callback('↩️ Volver', 'back_to_profile')
    ]
  ]);
}

function getVPNPreferencesKeyboard(currentType = 'wireguard') {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback(
        currentType === 'wireguard' ? '✅ WireGuard' : '🔘 WireGuard', 
        'pref_vpn_wireguard'
      ),
      Markup.button.callback(
        currentType === 'outline' ? '✅ Outline' : '🔘 Outline', 
        'pref_vpn_outline'
      )
    ],
    [
      Markup.button.callback(
        currentType === 'ask' ? '✅ Preguntar' : '🔘 Preguntar', 
        'pref_vpn_ask'
      )
    ],
    [
      Markup.button.callback('✅ Auto-conectar', 'pref_vpn_autoconnect'),
      Markup.button.callback('⚙️ Avanzado', 'pref_vpn_advanced')
    ],
    [
      Markup.button.callback('💾 Guardar', 'pref_vpn_save'),
      Markup.button.callback('↩️ Atrás', 'pref_back')
    ]
  ]);
}

function getNotificationPreferencesKeyboard(notifications) {
  const buttons = [
    [
      Markup.button.callback(
        notifications.connectionStatus ? '✅ Estado conexión' : '🔘 Estado conexión',
        'pref_notif_connection'
      ),
      Markup.button.callback(
        notifications.quotaWarnings ? '✅ Advertencias cuota' : '🔘 Advertencias cuota',
        'pref_notif_quota'
      )
    ],
    [
      Markup.button.callback(
        notifications.systemUpdates ? '✅ Actualizaciones' : '🔘 Actualizaciones',
        'pref_notif_updates'
      ),
      Markup.button.callback(
        notifications.promotional ? '✅ Promocionales' : '🔘 Promocionales',
        'pref_notif_promotional'
      )
    ],
    [
      Markup.button.callback('💾 Guardar', 'pref_notif_save'),
      Markup.button.callback('↩️ Atrás', 'pref_back')
    ]
  ];

  return Markup.inlineKeyboard(buttons);
}

function getInterfacePreferencesKeyboard(interfacePrefs) {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🇪🇸 Español', 'pref_lang_es'),
      Markup.button.callback('🇺🇸 English', 'pref_lang_en')
    ],
    [
      Markup.button.callback(
        interfacePrefs.compactMode ? '✅ Modo compacto' : '🔘 Modo compacto',
        'pref_compact_mode'
      ),
      Markup.button.callback(
        interfacePrefs.showEmojis ? '✅ Mostrar emojis' : '🔘 Mostrar emojis',
        'pref_show_emojis'
      )
    ],
    [
      Markup.button.callback('🌍 Zona horaria', 'pref_timezone'),
      Markup.button.callback('🎨 Tema', 'pref_theme')
    ],
    [
      Markup.button.callback('💾 Guardar', 'pref_interface_save'),
      Markup.button.callback('↩️ Atrás', 'pref_back')
    ]
  ]);
}

// ============================================================================
// 📊 ESTADÍSTICAS
// ============================================================================

function getStatisticsKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('📅 Última semana', 'stats_week'),
      Markup.button.callback('📅 Último mes', 'stats_month')
    ],
    [
      Markup.button.callback('📅 Últimos 3 meses', 'stats_quarter'),
      Markup.button.callback('📅 Todo el historial', 'stats_all')
    ],
    [
      Markup.button.callback('📊 VPN Comparación', 'stats_vpn_comparison'),
      Markup.button.callback('📈 Gráfico uso', 'stats_usage_chart')
    ],
    [
      Markup.button.callback('📥 Exportar', 'stats_export'),
      Markup.button.callback('↩️ Volver', 'back_to_profile')
    ]
  ]);
}

// ============================================================================
// 🔧 UTILIDADES
// ============================================================================

function getConfirmationKeyboard(action) {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('✅ Confirmar', `confirm_${action}`),
      Markup.button.callback('❌ Cancelar', `cancel_${action}`)
    ]
  ]);
}

function getBackToProfileKeyboard() {
  return Markup.inlineKeyboard([
    Markup.button.callback('👤 Volver a Perfil', 'back_to_profile')
  ]);
}

function getLanguageSelectionKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🇪🇸 Español', 'lang_es'),
      Markup.button.callback('🇺🇸 English', 'lang_en')
    ],
    [
      Markup.button.callback('🇫🇷 Français', 'lang_fr'),
      Markup.button.callback('🇩🇪 Deutsch', 'lang_de')
    ],
    [
      Markup.button.callback('🇮🇹 Italiano', 'lang_it'),
      Markup.button.callback('🇵🇹 Português', 'lang_pt')
    ],
    [
      Markup.button.callback('❌ Cancelar', 'lang_cancel')
    ]
  ]);
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // Profile Keyboards
  getProfileKeyboard,
  getProfileEditKeyboard,
  
  // Preferences Keyboards
  getPreferencesMainKeyboard,
  getVPNPreferencesKeyboard,
  getNotificationPreferencesKeyboard,
  getInterfacePreferencesKeyboard,
  
  // Statistics Keyboards
  getStatisticsKeyboard,
  
  // Utility Keyboards
  getConfirmationKeyboard,
  getBackToProfileKeyboard,
  getLanguageSelectionKeyboard
};