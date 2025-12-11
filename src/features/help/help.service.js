'use strict';

/**
 * ============================================================================
 * 🛎️ HELP SERVICE - uSipipo VPN Bot
 * ============================================================================
 * Lógica de negocio para el sistema de ayuda.
 * Gestiona contexto, navegación y contenido dinámico.
 * ============================================================================
 */

const logger = require('../../../core/utils/logger');
const messages = require('./help.messages');
const keyboards = require('./help.keyboard');
const { isAdmin } = require('../../../core/middleware/auth.middleware');

class HelpService {
  constructor() {
    // Caché de sesiones de ayuda (evita regenerar contenido)
    this.helpSessions = new Map();
    
    // Estadísticas de uso
    this.stats = {
      totalRequests: 0,
      byCategory: {
        main: 0,
        vpn: 0,
        profile: 0,
        system: 0,
        admin: 0,
        troubleshooting: 0,
        commands: 0
      }
    };
  }

  // ============================================================================
  // 📊 GESTIÓN DE ESTADÍSTICAS
  // ============================================================================

  incrementStats(category) {
    this.stats.totalRequests++;
    if (this.stats.byCategory[category] !== undefined) {
      this.stats.byCategory[category]++;
    }
    
    logger.debug('[HelpService] Stats updated', {
      category,
      total: this.stats.totalRequests
    });
  }

  getStats() {
    return { ...this.stats };
  }

  // ============================================================================
  // 🔍 OBTENER CONTENIDO DE AYUDA
  // ============================================================================

  getHelpContent(category, userId) {
    const userIsAdmin = isAdmin(userId);
    let content = {};

    this.incrementStats(category);

    switch (category) {
      case 'main':
        content = {
          message: messages.getMainHelpMessage(userIsAdmin),
          keyboard: keyboards.getMainHelpKeyboard(userIsAdmin)
        };
        break;

      case 'vpn':
        content = {
          message: messages.getVPNHelpMessage(),
          keyboard: keyboards.getVPNHelpKeyboard()
        };
        break;

      case 'profile':
        content = {
          message: messages.getProfileHelpMessage(),
          keyboard: keyboards.getProfileHelpKeyboard()
        };
        break;

      case 'system':
        content = {
          message: messages.getSystemInfoHelpMessage(),
          keyboard: keyboards.getSystemHelpKeyboard()
        };
        break;

      case 'admin':
        if (!userIsAdmin) {
          content = {
            message: '❌ *Acceso denegado*\n\nEsta sección es exclusiva para administradores.',
            keyboard: keyboards.getBackToHelpKeyboard()
          };
        } else {
          content = {
            message: messages.getAdminHelpMessage(),
            keyboard: keyboards.getAdminHelpKeyboard()
          };
        }
        break;

      case 'troubleshooting':
        content = {
          message: messages.getTroubleshootingHelpMessage(),
          keyboard: keyboards.getTroubleshootingKeyboard()
        };
        break;

      case 'commands':
        content = {
          message: messages.getCommandsListMessage(userIsAdmin),
          keyboard: keyboards.getCommandsListKeyboard()
        };
        break;

      default:
        content = {
          message: messages.getMainHelpMessage(userIsAdmin),
          keyboard: keyboards.getMainHelpKeyboard(userIsAdmin)
        };
    }

    // Guardar en sesión
    this.helpSessions.set(userId, {
      category,
      timestamp: Date.now(),
      isAdmin: userIsAdmin
    });

    logger.info('[HelpService] Content requested', {
      userId,
      category,
      isAdmin: userIsAdmin
    });

    return content;
  }

  // ============================================================================
  // 🗂️ GESTIÓN DE SESIONES
  // ============================================================================

  getSession(userId) {
    return this.helpSessions.get(userId) || null;
  }

  clearSession(userId) {
    this.helpSessions.delete(userId);
    logger.debug('[HelpService] Session cleared', { userId });
  }

  clearOldSessions(maxAgeMinutes = 30) {
    const now = Date.now();
    const maxAge = maxAgeMinutes * 60 * 1000;
    let cleared = 0;

    for (const [userId, session] of this.helpSessions.entries()) {
      if (now - session.timestamp > maxAge) {
        this.helpSessions.delete(userId);
        cleared++;
      }
    }

    if (cleared > 0) {
      logger.info('[HelpService] Old sessions cleared', { count: cleared });
    }

    return cleared;
  }

  // ============================================================================
  // 🔗 GENERACIÓN DE ENLACES ÚTILES
  // ============================================================================

  getDownloadLinks() {
    const constants = require('../../../config/constants');
    return {
      wireguard: constants.URLS.WIREGUARD_DOWNLOAD,
      outline: constants.URLS.OUTLINE_DOWNLOAD
    };
  }

  // ============================================================================
  // 📝 BÚSQUEDA DE AYUDA (FUTURA IMPLEMENTACIÓN)
  // ============================================================================

  searchHelp(query) {
    // Placeholder para búsqueda futura
    logger.debug('[HelpService] Search requested', { query });
    return {
      results: [],
      message: 'Función de búsqueda en desarrollo. Por favor, usa las categorías del menú.'
    };
  }

  // ============================================================================
  // 🔧 REPORTE DE PROBLEMA
  // ============================================================================

  formatProblemReport(userId, problemType, description) {
    const timestamp = new Date().toISOString();
    
    const report = {
      userId,
      problemType,
      description,
      timestamp,
      status: 'pending'
    };

    logger.info('[HelpService] Problem report created', report);

    return {
      success: true,
      report,
      message: '✅ Reporte enviado correctamente.\n\nEl administrador lo revisará pronto.'
    };
  }
}

// Exportar instancia singleton
module.exports = new HelpService();
