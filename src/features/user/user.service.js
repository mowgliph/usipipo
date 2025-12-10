'use strict';

const fs = require('fs').promises;
const path = require('path');
const config = require('../../config/environment');
const logger = require('../../core/utils/logger');
const markdown = require('../../core/utils/markdown');
const constants = require('../../config/constants');

/**
 * ============================================================================
 * 👤 USER SERVICE - uSipipo VPN Bot
 * ============================================================================
 * Servicio específico para gestión de perfil de usuario del bot de Telegram.
 *
 * 🎯 RESPONSABILIDADES:
 *   - Datos de perfil (nombre, username, preferencias)
 *   - Configuración personal del usuario
 *   - Preferencias de VPN (tipo favorito, notificaciones)
 *   - Interacción específica con Telegram
 *
 * 📌 NOTA: Para datos de autenticación/roles usar auth.middleware.js
 *          Para datos completos de VPN usar manager.service.js
 * ============================================================================
 */

class UserService {
  constructor() {
    // Archivo de perfiles de usuario
    this.profilesFilePath = path.join(__dirname, '../../data/user_profiles.json');
    this.dataDir = path.join(__dirname, '../../data');

    // Almacenamiento en memoria
    this.userProfiles = new Map(); // {userId: {profileData}}

    // Control de escritura
    this._saveLock = Promise.resolve();

    // Inicialización
    this.init();
  }

  // ============================================================================
  // 🔄 INITIALIZATION
  // ============================================================================

  async init() {
    try {
      await fs.mkdir(this.dataDir, { recursive: true });
      await this.loadProfiles();

      logger.info('[UserService] Inicializado correctamente', {
        totalProfiles: this.userProfiles.size
      });
    } catch (error) {
      logger.error('[UserService] Error en inicialización', error);
      throw error;
    }
  }

  // ============================================================================
  // 📂 DATA PERSISTENCE
  // ============================================================================

  async loadProfiles() {
    try {
      const raw = await fs.readFile(this.profilesFilePath, 'utf8').catch(() => '{"profiles":{}}');
      const data = JSON.parse(raw);
      this.userProfiles = new Map(Object.entries(data.profiles || {}));
    } catch (error) {
      logger.error('[UserService] Error cargando perfiles', error);
      this.userProfiles = new Map();
    }
  }

  async saveProfiles() {
    this._saveLock = this._saveLock.then(async () => {
      try {
        const tempPath = `${this.profilesFilePath}.tmp`;
        const payload = {
          profiles: Object.fromEntries(this.userProfiles),
          metadata: {
            lastUpdated: new Date().toISOString(),
            totalProfiles: this.userProfiles.size
          }
        };

        await fs.writeFile(tempPath, JSON.stringify(payload, null, 2), 'utf8');
        await fs.rename(tempPath, this.profilesFilePath);

        logger.debug('[UserService] Perfiles guardados', { count: this.userProfiles.size });
        return true;
      } catch (error) {
        logger.error('[UserService] Error guardando perfiles', error);
        return false;
      }
    });

    return this._saveLock;
  }

  // ============================================================================
  // 👤 PROFILE MANAGEMENT (Telegram-focused)
  // ============================================================================

  /**
   * Crea o actualiza perfil desde datos de Telegram
   */
  async createOrUpdateProfile(telegramUser) {
    const userId = String(telegramUser.id);
    const now = new Date().toISOString();

    let profile = this.userProfiles.get(userId) || {
      id: userId,
      createdAt: now,
      updatedAt: now,
      telegramData: {},
      preferences: this.getDefaultPreferences(),
      usageStats: this.getDefaultUsageStats()
    };

    // Actualizar datos de Telegram
    profile.telegramData = {
      username: telegramUser.username || null,
      firstName: telegramUser.first_name || '',
      lastName: telegramUser.last_name || '',
      languageCode: telegramUser.language_code || 'es',
      isPremium: telegramUser.is_premium || false,
      lastSeen: now
    };

    profile.updatedAt = now;

    // Si es nuevo perfil, añadir metadata
    if (!this.userProfiles.has(userId)) {
      profile.firstInteraction = now;
      logger.info('[UserService] Nuevo perfil creado', { userId });
    }

    this.userProfiles.set(userId, profile);
    await this.saveProfiles();

    return profile;
  }

  /**
   * Obtiene perfil completo del usuario
   */
  getProfile(userId) {
    const id = String(userId);
    return this.userProfiles.get(id) || null;
  }

  /**
   * Obtiene datos básicos para mostrar en UI
   */
  getProfileForDisplay(userId) {
    const profile = this.getProfile(userId);
    if (!profile) return null;

    const telegram = profile.telegramData || {};
    return {
      id: profile.id,
      username: telegram.username ? `@${telegram.username}` : 'Sin username',
      fullName: `${telegram.firstName || ''} ${telegram.lastName || ''}`.trim() || 'Usuario',
      language: telegram.languageCode || 'es',
      isPremium: telegram.isPremium || false,
      createdAt: profile.createdAt,
      lastSeen: telegram.lastSeen || profile.updatedAt,
      preferences: profile.preferences || {}
    };
  }

  // ============================================================================
  // ⚙️ PREFERENCES MANAGEMENT
  // ============================================================================

  getDefaultPreferences() {
    return {
      vpn: {
        defaultType: 'wireguard', // 'wireguard' | 'outline' | 'ask'
        autoConnect: false,
        showAdvancedOptions: false
      },
      notifications: {
        connectionStatus: true,
        quotaWarnings: true,
        systemUpdates: true,
        promotional: false
      },
      interface: {
        language: 'es',
        compactMode: false,
        showEmojis: true,
        timezone: 'UTC'
      },
      security: {
        requireConfirmation: true,
        logOutOtherSessions: false,
        twoFactorAuth: false
      }
    };
  }

  getDefaultUsageStats() {
    return {
      totalConnections: 0,
      totalBytesTransferred: 0,
      favoriteVPN: null,
      lastConnected: null,
      averageSessionTime: 0,
      commandsUsed: {}
    };
  }

  async updatePreference(userId, category, key, value) {
    const profile = this.getProfile(userId);
    if (!profile) {
      throw new Error('Perfil no encontrado');
    }

    if (!profile.preferences[category]) {
      profile.preferences[category] = {};
    }

    profile.preferences[category][key] = value;
    profile.updatedAt = new Date().toISOString();

    this.userProfiles.set(String(userId), profile);
    await this.saveProfiles();

    logger.debug('[UserService] Preferencia actualizada', { userId, category, key });
    return profile.preferences;
  }

  async getPreference(userId, category, key) {
    const profile = this.getProfile(userId);
    if (!profile || !profile.preferences[category]) {
      return null;
    }
    return profile.preferences[category][key];
  }

  // ============================================================================
  // 📊 USAGE STATISTICS & ANALYTICS
  // ============================================================================

  async recordCommandUsage(userId, command) {
    const profile = this.getProfile(userId);
    if (!profile) return;

    if (!profile.usageStats.commandsUsed) {
      profile.usageStats.commandsUsed = {};
    }

    profile.usageStats.commandsUsed[command] = (profile.usageStats.commandsUsed[command] || 0) + 1;
    profile.usageStats.lastCommand = {
      command,
      timestamp: new Date().toISOString()
    };

    this.userProfiles.set(String(userId), profile);
    await this.saveProfiles();
  }

  async recordVPNConnection(userId, vpnType, duration, bytesTransferred) {
    const profile = this.getProfile(userId);
    if (!profile) return;

    profile.usageStats.totalConnections = (profile.usageStats.totalConnections || 0) + 1;
    profile.usageStats.totalBytesTransferred = (profile.usageStats.totalBytesTransferred || 0) + bytesTransferred;

    // Actualizar VPN favorito
    if (!profile.usageStats.vpnUsage) {
      profile.usageStats.vpnUsage = {};
    }
    profile.usageStats.vpnUsage[vpnType] = (profile.usageStats.vpnUsage[vpnType] || 0) + 1;

    // Calcular VPN favorita
    let favoriteVPN = null;
    let maxUsage = 0;
    for (const [vpn, count] of Object.entries(profile.usageStats.vpnUsage)) {
      if (count > maxUsage) {
        maxUsage = count;
        favoriteVPN = vpn;
      }
    }
    profile.usageStats.favoriteVPN = favoriteVPN;

    profile.usageStats.lastConnected = {
      vpnType,
      timestamp: new Date().toISOString(),
      duration,
      bytesTransferred
    };

    // Calcular tiempo promedio de sesión
    if (profile.usageStats.averageSessionTime === 0) {
      profile.usageStats.averageSessionTime = duration;
    } else {
      profile.usageStats.averageSessionTime =
        (profile.usageStats.averageSessionTime + duration) / 2;
    }

    this.userProfiles.set(String(userId), profile);
    await this.saveProfiles();
  }

  getUsageStatistics(userId) {
    const profile = this.getProfile(userId);
    if (!profile) return null;

    return {
      general: {
        totalConnections: profile.usageStats.totalConnections || 0,
        totalBytesTransferred: this.formatBytes(profile.usageStats.totalBytesTransferred || 0),
        favoriteVPN: profile.usageStats.favoriteVPN,
        averageSessionTime: this.formatDuration(profile.usageStats.averageSessionTime || 0)
      },
      vpnUsage: profile.usageStats.vpnUsage || {},
      commandUsage: profile.usageStats.commandsUsed || {},
      lastConnection: profile.usageStats.lastConnected
    };
  }

  // ============================================================================
  // 💬 MESSAGE FORMATTING (For Telegram UI)
  // ============================================================================

  formatProfileMessage(userId) {
    const profile = this.getProfileForDisplay(userId);
    if (!profile) {
      return `${constants.EMOJI.USER} *Perfil no encontrado*\n\nNo tienes un perfil registrado.`;
    }

    const preferences = this.getProfile(userId)?.preferences || {};

    let message = `${constants.EMOJI.USER} *TU PERFIL*\n\n`;

    message += `👤 *Nombre:* ${markdown.escapeMarkdown(profile.fullName)}\n`;
    message += `🔖 *Username:* ${profile.username}\n`;
    message += `🆔 *ID:* ${markdown.code(profile.id)}\n`;
    message += `🌐 *Idioma:* ${profile.language.toUpperCase()}\n`;
    message += `⭐ *Premium:* ${profile.isPremium ? 'Sí ✅' : 'No'}\n\n`;

    message += `📅 *Registrado:* ${this.formatDate(profile.createdAt)}\n`;
    message += `👀 *Última vez:* ${this.formatDate(profile.lastSeen)}\n\n`;

    // Preferencias de VPN
    const vpnPref = preferences.vpn || {};
    message += `🔐 *VPN Preferida:* ${markdown.bold(vpnPref.defaultType || 'No definida')}\n`;
    message += `🔔 *Auto-conectar:* ${vpnPref.autoConnect ? 'Sí ✅' : 'No'}\n\n`;

    // Estadísticas si existen
    const stats = this.getUsageStatistics(userId);
    if (stats && stats.general.totalConnections > 0) {
      message += `📊 *Estadísticas de Uso*\n`;
      message += `• Conexiones totales: ${stats.general.totalConnections}\n`;
      message += `• Datos transferidos: ${stats.general.totalBytesTransferred}\n`;
      message += `• VPN favorita: ${markdown.bold(stats.general.favoriteVPN || 'Ninguna')}\n`;
    }

    return message;
  }

  formatPreferencesMessage(userId) {
    const profile = this.getProfile(userId);
    if (!profile) {
      return `${constants.EMOJI.WARNING} No tienes un perfil registrado.`;
    }

    const prefs = profile.preferences || this.getDefaultPreferences();

    let message = `${constants.EMOJI.SETTINGS} *TUS PREFERENCIAS*\n\n`;

    message += `🔐 *VPN*\n`;
    message += `• Tipo por defecto: ${markdown.bold(prefs.vpn.defaultType)}\n`;
    message += `• Auto-conectar: ${prefs.vpn.autoConnect ? '✅ Sí' : '❌ No'}\n`;
    message += `• Opciones avanzadas: ${prefs.vpn.showAdvancedOptions ? '✅ Sí' : '❌ No'}\n\n`;

    message += `🔔 *Notificaciones*\n`;
    message += `• Estado conexión: ${prefs.notifications.connectionStatus ? '✅ Sí' : '❌ No'}\n`;
    message += `• Advertencias de cuota: ${prefs.notifications.quotaWarnings ? '✅ Sí' : '❌ No'}\n`;
    message += `• Actualizaciones: ${prefs.notifications.systemUpdates ? '✅ Sí' : '❌ No'}\n`;
    message += `• Promocionales: ${prefs.notifications.promotional ? '✅ Sí' : '❌ No'}\n\n`;

    message += `🎨 *Interfaz*\n`;
    message += `• Idioma: ${markdown.bold(prefs.interface.language)}\n`;
    message += `• Modo compacto: ${prefs.interface.compactMode ? '✅ Sí' : '❌ No'}\n`;
    message += `• Mostrar emojis: ${prefs.interface.showEmojis ? '✅ Sí' : '❌ No'}\n`;
    message += `• Zona horaria: ${prefs.interface.timezone}\n\n`;

    message += `🛡️ *Seguridad*\n`;
    message += `• Confirmar acciones: ${prefs.security.requireConfirmation ? '✅ Sí' : '❌ No'}\n`;
    message += `• Cerrar otras sesiones: ${prefs.security.logOutOtherSessions ? '✅ Sí' : '❌ No'}\n`;
    message += `• Autenticación 2FA: ${prefs.security.twoFactorAuth ? '✅ Sí' : '❌ No'}`;

    return message;
  }

  // ============================================================================
  // 🛠️ UTILITY FUNCTIONS
  // ============================================================================

  formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  formatDuration(seconds) {
    if (seconds < 60) return `${Math.round(seconds)} segundos`;
    if (seconds < 3600) return `${Math.round(seconds / 60)} minutos`;
    return `${(seconds / 3600).toFixed(1)} horas`;
  }

  formatDate(dateString) {
    if (!dateString) return 'Nunca';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Fecha inválida';
    }
  }

  // ============================================================================
  // 📈 ADMIN & REPORTING FUNCTIONS
  // ============================================================================

  getAllProfiles() {
    return Array.from(this.userProfiles.values());
  }

  getActiveUsers(lastDays = 30) {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - lastDays);

    return this.getAllProfiles().filter(profile => {
      const lastSeen = profile.telegramData?.lastSeen || profile.updatedAt;
      return new Date(lastSeen) > cutoff;
    });
  }

  getProfileStats() {
    const profiles = this.getAllProfiles();

    return {
      total: profiles.length,
      withUsername: profiles.filter(p => p.telegramData?.username).length,
      premiumUsers: profiles.filter(p => p.telegramData?.isPremium).length,
      mostCommonLanguage: this.getMostCommonLanguage(profiles),
      averageConnections: this.calculateAverageConnections(profiles),
      last30DaysActive: this.getActiveUsers(30).length
    };
  }

  getMostCommonLanguage(profiles) {
    const languages = {};
    profiles.forEach(p => {
      const lang = p.telegramData?.languageCode || 'unknown';
      languages[lang] = (languages[lang] || 0) + 1;
    });

    let mostCommon = 'unknown';
    let maxCount = 0;
    for (const [lang, count] of Object.entries(languages)) {
      if (count > maxCount) {
        maxCount = count;
        mostCommon = lang;
      }
    }

    return { language: mostCommon, count: maxCount };
  }

  calculateAverageConnections(profiles) {
    const totalConnections = profiles.reduce((sum, p) => {
      return sum + (p.usageStats?.totalConnections || 0);
    }, 0);

    return profiles.length > 0 ? (totalConnections / profiles.length).toFixed(1) : 0;
  }
}

// Exportar instancia singleton
module.exports = new UserService();