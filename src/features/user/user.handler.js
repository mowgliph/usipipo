'use strict';

/**
 * ============================================================================
 * 🎮 USER HANDLER - uSipipo VPN Bot
 * ============================================================================
 * Handler principal del módulo de usuario.
 * Maneja comandos y acciones relacionadas con el perfil del usuario.
 * ============================================================================
 */

const { Markup } = require('telegraf');
const logger = require('../../core/utils/logger');
const userService = require('./user.service');
const userMessages = require('./user.messages');
const userKeyboard = require('./user.keyboard');
const commonMessages = require('../../shared/messages/common.messages');
const commonKeyboard = require('../../shared/keyboard/common.keyboard');
const { withErrorHandling } = require('../../core/middleware/error.middleware');

// ============================================================================
// 📋 COMANDOS PRINCIPALES
// ============================================================================

async function handleProfileCommand(ctx) {
  try {
    const userId = String(ctx.from.id);
    const userName = ctx.from.first_name || ctx.from.username || 'Usuario';
    
    // Verificar si el usuario tiene perfil
    const profile = userService.getProfileForDisplay(userId);
    
    if (!profile) {
      // Crear perfil automáticamente si no existe
      await userService.createOrUpdateProfile(ctx.from);
      const newProfile = userService.getProfileForDisplay(userId);
      
      const message = userMessages.getProfileHeader(userName) + '\n' +
                     userMessages.getProfileInfo(newProfile) + '\n' +
                     commonMessages.getOperationSuccessMessage('Perfil creado');
      
      await ctx.reply(message, {
        parse_mode: 'Markdown',
        reply_markup: userKeyboard.getProfileKeyboard().reply_markup
      });
      return;
    }

    const stats = userService.getUsageStatistics(userId);
    
    let message = userMessages.getProfileHeader(userName) + '\n';
    message += userMessages.getProfileInfo(profile) + '\n';
    
    if (stats && stats.general.totalConnections > 0) {
      message += userMessages.getProfileStats(stats);
    }
    
    await ctx.reply(message, {
      parse_mode: 'Markdown',
      reply_markup: userKeyboard.getProfileKeyboard().reply_markup
    });
    
    logger.info('[UserHandler] Perfil mostrado', { userId });
    
  } catch (error) {
    logger.error('[UserHandler] Error en handleProfileCommand', error, { userId: ctx.from?.id });
    await ctx.reply(commonMessages.getGenericErrorMessage(), {
      parse_mode: 'Markdown',
      reply_markup: commonKeyboard.getBackToMenuKeyboard().reply_markup
    });
  }
}

async function handlePreferencesCommand(ctx) {
  try {
    const userId = String(ctx.from.id);
    const profile = userService.getProfile(userId);
    
    if (!profile) {
      await ctx.reply(userMessages.getProfileNotFoundError(), {
        parse_mode: 'Markdown',
        reply_markup: commonKeyboard.getBackToMenuKeyboard().reply_markup
      });
      return;
    }
    
    const prefs = profile.preferences || userService.getDefaultPreferences();
    
    let message = userMessages.getPreferencesHeader() + '\n\n';
    message += userMessages.getVPNPreferences(prefs.vpn) + '\n\n';
    message += userMessages.getNotificationPreferences(prefs.notifications) + '\n\n';
    message += userMessages.getInterfacePreferences(prefs.interface) + '\n\n';
    message += userMessages.getSecurityPreferences(prefs.security);
    
    await ctx.reply(message, {
      parse_mode: 'Markdown',
      reply_markup: userKeyboard.getPreferencesMainKeyboard().reply_markup
    });
    
  } catch (error) {
    logger.error('[UserHandler] Error en handlePreferencesCommand', error);
    await ctx.reply(commonMessages.getGenericErrorMessage(), {
      parse_mode: 'Markdown'
    });
  }
}

// ============================================================================
// 🎯 ACCIONES DE PERFIL (CALLBACKS)
// ============================================================================

async function handleProfileStats(ctx) {
  try {
    await ctx.answerCbQuery();
    const userId = String(ctx.from.id);
    const stats = userService.getUsageStatistics(userId);
    
    if (!stats || stats.general.totalConnections === 0) {
      await ctx.reply(userMessages.getProfileStats({ general: { totalConnections: 0 } }), {
        parse_mode: 'Markdown',
        reply_markup: userKeyboard.getStatisticsKeyboard().reply_markup
      });
      return;
    }
    
    await ctx.reply(userMessages.getProfileStats(stats), {
      parse_mode: 'Markdown',
      reply_markup: userKeyboard.getStatisticsKeyboard().reply_markup
    });
    
  } catch (error) {
    logger.error('[UserHandler] Error en handleProfileStats', error);
    await ctx.answerCbQuery('❌ Error al cargar estadísticas');
  }
}

async function handleProfilePreferences(ctx) {
  try {
    await ctx.answerCbQuery();
    await handlePreferencesCommand(ctx);
  } catch (error) {
    logger.error('[UserHandler] Error en handleProfilePreferences', error);
    await ctx.answerCbQuery('❌ Error al cargar preferencias');
  }
}

async function handleProfileEdit(ctx) {
  try {
    await ctx.answerCbQuery();
    
    const message = userMessages.getEditProfilePrompt();
    
    await ctx.reply(message, {
      parse_mode: 'Markdown',
      reply_markup: userKeyboard.getProfileEditKeyboard().reply_markup
    });
    
  } catch (error) {
    logger.error('[UserHandler] Error en handleProfileEdit', error);
    await ctx.answerCbQuery('❌ Error al editar perfil');
  }
}

async function handleProfileRefresh(ctx) {
  try {
    await ctx.answerCbQuery('🔄 Actualizando...');
    
    // Actualizar perfil con datos de Telegram
    await userService.createOrUpdateProfile(ctx.from);
    
    // Mostrar perfil actualizado
    await handleProfileCommand(ctx);
    
    await ctx.answerCbQuery('✅ Perfil actualizado');
    
  } catch (error) {
    logger.error('[UserHandler] Error en handleProfileRefresh', error);
    await ctx.answerCbQuery('❌ Error al actualizar');
  }
}

// ============================================================================
// ⚙️ GESTIÓN DE PREFERENCIAS (CALLBACKS)
// ============================================================================

async function handlePrefVPN(ctx) {
  try {
    await ctx.answerCbQuery();
    const userId = String(ctx.from.id);
    const profile = userService.getProfile(userId);
    const vpnPref = profile?.preferences?.vpn || { defaultType: 'wireguard' };
    
    await ctx.reply(userMessages.getVPNPreferences(vpnPref), {
      parse_mode: 'Markdown',
      reply_markup: userKeyboard.getVPNPreferencesKeyboard(vpnPref.defaultType).reply_markup
    });
    
  } catch (error) {
    logger.error('[UserHandler] Error en handlePrefVPN', error);
    await ctx.answerCbQuery('❌ Error al cargar preferencias VPN');
  }
}

async function handlePrefNotifications(ctx) {
  try {
    await ctx.answerCbQuery();
    const userId = String(ctx.from.id);
    const profile = userService.getProfile(userId);
    const notifications = profile?.preferences?.notifications || 
      userService.getDefaultPreferences().notifications;
    
    await ctx.reply(userMessages.getNotificationPreferences(notifications), {
      parse_mode: 'Markdown',
      reply_markup: userKeyboard.getNotificationPreferencesKeyboard(notifications).reply_markup
    });
    
  } catch (error) {
    logger.error('[UserHandler] Error en handlePrefNotifications', error);
    await ctx.answerCbQuery('❌ Error al cargar notificaciones');
  }
}

async function toggleNotificationSetting(ctx, setting) {
  try {
    const userId = String(ctx.from.id);
    const currentValue = await userService.getPreference(userId, 'notifications', setting);
    const newValue = !currentValue;
    
    await userService.updatePreference(userId, 'notifications', setting, newValue);
    
    await ctx.answerCbQuery(`✅ ${setting} ${newValue ? 'activado' : 'desactivado'}`);
    
    // Actualizar mensaje
    const profile = userService.getProfile(userId);
    const notifications = profile?.preferences?.notifications;
    
    await ctx.editMessageText(userMessages.getNotificationPreferences(notifications), {
      parse_mode: 'Markdown',
      reply_markup: userKeyboard.getNotificationPreferencesKeyboard(notifications).reply_markup
    });
    
  } catch (error) {
    logger.error('[UserHandler] Error en toggleNotificationSetting', error);
    await ctx.answerCbQuery('❌ Error al cambiar configuración');
  }
}

async function handlePrefInterface(ctx) {
  try {
    await ctx.answerCbQuery();
    const userId = String(ctx.from.id);
    const profile = userService.getProfile(userId);
    const interfacePrefs = profile?.preferences?.interface || 
      userService.getDefaultPreferences().interface;
    
    await ctx.reply(userMessages.getInterfacePreferences(interfacePrefs), {
      parse_mode: 'Markdown',
      reply_markup: userKeyboard.getInterfacePreferencesKeyboard(interfacePrefs).reply_markup
    });
    
  } catch (error) {
    logger.error('[UserHandler] Error en handlePrefInterface', error);
    await ctx.answerCbQuery('❌ Error al cargar interfaz');
  }
}

async function handlePrefSecurity(ctx) {
  try {
    await ctx.answerCbQuery();
    const userId = String(ctx.from.id);
    const profile = userService.getProfile(userId);
    const security = profile?.preferences?.security || 
      userService.getDefaultPreferences().security;
    
    await ctx.reply(userMessages.getSecurityPreferences(security), {
      parse_mode: 'Markdown'
    });
    
  } catch (error) {
    logger.error('[UserHandler] Error en handlePrefSecurity', error);
    await ctx.answerCbQuery('❌ Error al cargar seguridad');
  }
}

// ============================================================================
// 🔄 CAMBIOS DE CONFIGURACIÓN
// ============================================================================

async function handleSetVPNType(ctx, vpnType) {
  try {
    const userId = String(ctx.from.id);
    const validTypes = ['wireguard', 'outline', 'ask'];
    
    if (!validTypes.includes(vpnType)) {
      await ctx.answerCbQuery(userMessages.getInvalidPreferenceValueError('Tipo VPN', validTypes));
      return;
    }
    
    await userService.updatePreference(userId, 'vpn', 'defaultType', vpnType);
    
    await ctx.answerCbQuery(`✅ VPN predeterminada: ${vpnType}`);
    
    // Actualizar teclado
    await ctx.editMessageReplyMarkup(
      userKeyboard.getVPNPreferencesKeyboard(vpnType).reply_markup
    );
    
  } catch (error) {
    logger.error('[UserHandler] Error en handleSetVPNType', error);
    await ctx.answerCbQuery('❌ Error al cambiar tipo VPN');
  }
}

async function handleSetLanguage(ctx, language) {
  try {
    const userId = String(ctx.from.id);
    const validLanguages = ['es', 'en', 'fr', 'de', 'it', 'pt'];
    
    if (!validLanguages.includes(language)) {
      await ctx.answerCbQuery('❌ Idioma no soportado');
      return;
    }
    
    await userService.updatePreference(userId, 'interface', 'language', language);
    
    await ctx.answerCbQuery(`✅ Idioma cambiado a: ${language}`);
    
    // Si el mensaje actual tiene teclado de idiomas, editarlo
    if (ctx.callbackQuery.message.text.includes('Idioma:')) {
      const profile = userService.getProfile(userId);
      const interfacePrefs = profile?.preferences?.interface;
      
      await ctx.editMessageText(userMessages.getInterfacePreferences(interfacePrefs), {
        parse_mode: 'Markdown',
        reply_markup: userKeyboard.getInterfacePreferencesKeyboard(interfacePrefs).reply_markup
      });
    }
    
  } catch (error) {
    logger.error('[UserHandler] Error en handleSetLanguage', error);
    await ctx.answerCbQuery('❌ Error al cambiar idioma');
  }
}

// ============================================================================
// 📊 ESTADÍSTICAS DETALLADAS
// ============================================================================

async function handleStatsTimeRange(ctx, range) {
  try {
    await ctx.answerCbQuery(`📊 Cargando estadísticas ${range}...`);
    
    // En una implementación real, aquí se obtendrían estadísticas filtradas por tiempo
    const userId = String(ctx.from.id);
    const stats = userService.getUsageStatistics(userId);
    
    let rangeText = '';
    switch (range) {
      case 'week': rangeText = 'de la última semana'; break;
      case 'month': rangeText = 'del último mes'; break;
      case 'quarter': rangeText = 'de los últimos 3 meses'; break;
      case 'all': rangeText = 'totales'; break;
    }
    
    let message = `${commonMessages.EMOJI.CHART} *ESTADÍSTICAS ${rangeText.toUpperCase()}*\n\n`;
    
    if (stats && stats.general.totalConnections > 0) {
      message += `🔸 *Conexiones:* ${stats.general.totalConnections}\n`;
      message += `🔸 *Datos:* ${stats.general.totalBytesTransferred}\n`;
      message += `🔸 *VPN favorita:* ${stats.general.favoriteVPN}\n`;
    } else {
      message += `No hay datos ${rangeText}.\n`;
      message += `Usa el bot más frecuentemente para generar estadísticas.`;
    }
    
    await ctx.reply(message, {
      parse_mode: 'Markdown',
      reply_markup: userKeyboard.getStatisticsKeyboard().reply_markup
    });
    
  } catch (error) {
    logger.error('[UserHandler] Error en handleStatsTimeRange', error);
    await ctx.answerCbQuery('❌ Error al cargar estadísticas');
  }
}

// ============================================================================
// 🏠 NAVEGACIÓN
// ============================================================================

async function handleBackToProfile(ctx) {
  try {
    await ctx.answerCbQuery();
    await handleProfileCommand(ctx);
  } catch (error) {
    logger.error('[UserHandler] Error en handleBackToProfile', error);
    await ctx.answerCbQuery('❌ Error al volver');
  }
}

async function handleBackToPreferences(ctx) {
  try {
    await ctx.answerCbQuery();
    await handlePreferencesCommand(ctx);
  } catch (error) {
    logger.error('[UserHandler] Error en handleBackToPreferences', error);
    await ctx.answerCbQuery('❌ Error al volver');
  }
}

// ============================================================================
// 🎮 REGISTRO DE HANDLERS
// ============================================================================

function registerUserHandlers(bot) {
  logger.info('[UserHandler] Registrando handlers de usuario');
  
  // Comandos principales
  bot.command('profile', withErrorHandling(handleProfileCommand));
  bot.command('preferences', withErrorHandling(handlePreferencesCommand));
  bot.command('settings', withErrorHandling(handlePreferencesCommand));
  bot.command('stats', withErrorHandling(handleProfileCommand));
  
  // Acciones de perfil
  bot.action('profile_stats', withErrorHandling(handleProfileStats));
  bot.action('profile_preferences', withErrorHandling(handleProfilePreferences));
  bot.action('profile_edit', withErrorHandling(handleProfileEdit));
  bot.action('profile_refresh', withErrorHandling(handleProfileRefresh));
  
  // Preferencias
  bot.action('pref_vpn', withErrorHandling(handlePrefVPN));
  bot.action('pref_notifications', withErrorHandling(handlePrefNotifications));
  bot.action('pref_interface', withErrorHandling(handlePrefInterface));
  bot.action('pref_security', withErrorHandling(handlePrefSecurity));
  
  // Tipos de VPN
  bot.action('pref_vpn_wireguard', (ctx) => handleSetVPNType(ctx, 'wireguard'));
  bot.action('pref_vpn_outline', (ctx) => handleSetVPNType(ctx, 'outline'));
  bot.action('pref_vpn_ask', (ctx) => handleSetVPNType(ctx, 'ask'));
  
  // Notificaciones (toggle)
  bot.action('pref_notif_connection', (ctx) => toggleNotificationSetting(ctx, 'connectionStatus'));
  bot.action('pref_notif_quota', (ctx) => toggleNotificationSetting(ctx, 'quotaWarnings'));
  bot.action('pref_notif_updates', (ctx) => toggleNotificationSetting(ctx, 'systemUpdates'));
  bot.action('pref_notif_promotional', (ctx) => toggleNotificationSetting(ctx, 'promotional'));
  
  // Idiomas
  bot.action('pref_lang_es', (ctx) => handleSetLanguage(ctx, 'es'));
  bot.action('pref_lang_en', (ctx) => handleSetLanguage(ctx, 'en'));
  bot.action('lang_es', (ctx) => handleSetLanguage(ctx, 'es'));
  bot.action('lang_en', (ctx) => handleSetLanguage(ctx, 'en'));
  bot.action('lang_fr', (ctx) => handleSetLanguage(ctx, 'fr'));
  bot.action('lang_de', (ctx) => handleSetLanguage(ctx, 'de'));
  bot.action('lang_it', (ctx) => handleSetLanguage(ctx, 'it'));
  bot.action('lang_pt', (ctx) => handleSetLanguage(ctx, 'pt'));
  
  // Estadísticas por rango de tiempo
  bot.action('stats_week', (ctx) => handleStatsTimeRange(ctx, 'week'));
  bot.action('stats_month', (ctx) => handleStatsTimeRange(ctx, 'month'));
  bot.action('stats_quarter', (ctx) => handleStatsTimeRange(ctx, 'quarter'));
  bot.action('stats_all', (ctx) => handleStatsTimeRange(ctx, 'all'));
  
  // Navegación
  bot.action('back_to_profile', withErrorHandling(handleBackToProfile));
  bot.action('pref_back', withErrorHandling(handleBackToPreferences));
  bot.action('profile_cancel', withErrorHandling(handleBackToProfile));
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  registerUserHandlers,
  handleProfileCommand,
  handlePreferencesCommand
};