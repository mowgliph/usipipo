'use strict';

/**
 * ============================================================================
 * 👑 ADMIN HANDLER - uSipipo VPN Bot
 * ============================================================================
 * Controlador de comandos y callbacks administrativos.
 * ============================================================================
 */

const adminService = require('./admin.service');
const adminMessages = require('./admin.messages');
const adminKeyboards = require('./admin.keyboard');
const logger = require('../../../core/utils/logger');
const { requireAdmin } = require('../../../core/middleware/auth.middleware');

class AdminHandler {
  constructor(bot) {
    this.bot = bot;
    this.registerCommands();
    this.registerCallbacks();
  }

  // ============================================================================
  // 📝 COMMAND REGISTRATION
  // ============================================================================

  registerCommands() {
    // Main admin panel
    this.bot.command('admin', requireAdmin, async (ctx) => {
      await this.showAdminPanel(ctx);
    });

    // User management
    this.bot.command('adduser', requireAdmin, async (ctx) => {
      await this.handleAddUser(ctx);
    });

    this.bot.command('removeuser', requireAdmin, async (ctx) => {
      await this.handleRemoveUser(ctx);
    });

    this.bot.command('listusers', requireAdmin, async (ctx) => {
      await this.handleListUsers(ctx);
    });

    this.bot.command('userdetail', requireAdmin, async (ctx) => {
      await this.handleUserDetail(ctx);
    });

    // Statistics
    this.bot.command('stats', requireAdmin, async (ctx) => {
      await this.handleStats(ctx);
    });

    this.bot.command('health', requireAdmin, async (ctx) => {
      await this.handleHealth(ctx);
    });

    // Maintenance
    this.bot.command('cleanup', requireAdmin, async (ctx) => {
      await this.handleCleanup(ctx);
    });

    this.bot.command('maintenance', requireAdmin, async (ctx) => {
      await this.handleMaintenanceMode(ctx);
    });

    this.bot.command('backup', requireAdmin, async (ctx) => {
      await this.handleBackup(ctx);
    });

    // Broadcast
    this.bot.command('broadcast', requireAdmin, async (ctx) => {
      await this.handleBroadcast(ctx);
    });
  }

  // ============================================================================
  // 🔘 CALLBACK REGISTRATION
  // ============================================================================

  registerCallbacks() {
    // Main navigation
    this.bot.action('admin_back', requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      await this.showAdminPanel(ctx);
    });

    // User management
    this.bot.action('admin_user_add', requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      await ctx.reply(
        'Para agregar un usuario, usa el comando:\n\n`/adduser <userId> [nombre]`',
        { parse_mode: 'Markdown' }
      );
    });

    this.bot.action('admin_user_list', requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      await this.handleListUsers(ctx, 1);
    });

    this.bot.action(/^admin_users_page_(\d+)$/, requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      const page = parseInt(ctx.match[1]);
      await this.handleListUsers(ctx, page);
    });

    this.bot.action(/^admin_user_detail_(\d+)$/, requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      const userId = ctx.match[1];
      await this.handleUserDetail(ctx, userId);
    });

    this.bot.action(/^admin_user_role_(\d+)$/, requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      const userId = ctx.match[1];
      await this.showRoleSelection(ctx, userId);
    });

    this.bot.action(/^admin_setrole_(\d+)_(admin|user)$/, requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      const userId = ctx.match[1];
      const newRole = ctx.match[2];
      await this.handleChangeRole(ctx, userId, newRole);
    });

    this.bot.action(/^admin_user_delete_(\d+)$/, requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      const userId = ctx.match[1];
      await this.handleRemoveUserCallback(ctx, userId);
    });

    // Statistics
    this.bot.action('admin_stats_users', requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      await this.handleStats(ctx);
    });

    this.bot.action('admin_stats_refresh', requireAdmin, async (ctx) => {
      await ctx.answerCbQuery('🔄 Actualizando...');
      await this.handleStats(ctx);
    });

    this.bot.action('admin_stats_system', requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      await this.handleHealth(ctx);
    });

    this.bot.action('admin_stats_detailed', requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      await this.handleDetailedStats(ctx);
    });

    // Maintenance
    this.bot.action('admin_maint_cleanup', requireAdmin, async (ctx) => {
      await ctx.answerCbQuery('🧹 Limpiando...');
      await this.handleCleanup(ctx);
    });

    this.bot.action('admin_maint_storage', requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      await this.handleStorageStats(ctx);
    });

    this.bot.action('admin_maint_orphans', requireAdmin, async (ctx) => {
      await ctx.answerCbQuery('🗑️ Limpiando datos huérfanos...');
      await this.handleCleanup(ctx);
    });

    this.bot.action('admin_maint_mode', requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      await this.showMaintenanceMode(ctx);
    });

    this.bot.action(/^admin_maint_mode_(enable|disable)$/, requireAdmin, async (ctx) => {
      await ctx.answerCbQuery();
      const enable = ctx.match[1] === 'enable';
      await this.toggleMaintenanceMode(ctx, enable);
    });

    this.bot.action('admin_maint_backup', requireAdmin, async (ctx) => {
      await ctx.answerCbQuery('💾 Creando backup...');
      await this.handleBackup(ctx);
    });
  }

  // ============================================================================
  // 🏠 ADMIN PANEL
  // ============================================================================

  async showAdminPanel(ctx) {
    try {
      const user = ctx.from;
      const userName = user.first_name || 'Admin';
      
      const message = adminMessages.getAdminWelcomeMessage(userName);
      const keyboard = adminKeyboards.getAdminMainKeyboard();

      if (ctx.callbackQuery) {
        await ctx.editMessageText(message, {
          parse_mode: 'Markdown',
          ...keyboard
        });
      } else {
        await ctx.reply(message, {
          parse_mode: 'Markdown',
          ...keyboard
        });
      }
    } catch (error) {
      logger.error('[AdminHandler] Error mostrando panel admin', error);
      await ctx.reply('❌ Error mostrando panel de administración.');
    }
  }

  // ============================================================================
  // 👥 USER MANAGEMENT HANDLERS
  // ============================================================================

  async handleAddUser(ctx) {
    try {
      const args = ctx.message.text.split(' ').slice(1);
      
      if (args.length === 0) {
        await ctx.reply(adminMessages.getInvalidUserIdMessage(), {
          parse_mode: 'Markdown'
        });
        return;
      }

      const userId = args[0];
      const userName = args.slice(1).join(' ') || null;
      const addedBy = ctx.from.id;

      const result = await adminService.addUser(userId, addedBy, userName);

      if (result.success) {
        await ctx.reply(adminMessages.getUserAddedMessage(userId, userName || 'Usuario'), {
          parse_mode: 'Markdown'
        });
      } else {
        if (result.error.includes('ya existe')) {
          await ctx.reply(adminMessages.getUserAlreadyExistsMessage(userId), {
            parse_mode: 'Markdown'
          });
        } else {
          await ctx.reply(`❌ Error: ${result.error}`, {
            parse_mode: 'Markdown'
          });
        }
      }
    } catch (error) {
      logger.error('[AdminHandler] Error en handleAddUser', error);
      await ctx.reply('❌ Error agregando usuario.');
    }
  }

  async handleRemoveUser(ctx) {
    try {
      const args = ctx.message.text.split(' ').slice(1);
      
      if (args.length === 0) {
        await ctx.reply(adminMessages.getInvalidUserIdMessage(), {
          parse_mode: 'Markdown'
        });
        return;
      }

      const userId = args[0];
      const removedBy = ctx.from.id;

      const result = await adminService.removeUser(userId, removedBy);

      if (result.success) {
        await ctx.reply(adminMessages.getUserRemovedMessage(userId), {
          parse_mode: 'Markdown'
        });
      } else {
        if (result.error.includes('eliminarte a ti mismo')) {
          await ctx.reply(adminMessages.getCannotRemoveSelfMessage(), {
            parse_mode: 'Markdown'
          });
        } else if (result.error.includes('administrador principal')) {
          await ctx.reply(adminMessages.getCannotRemoveMainAdminMessage(), {
            parse_mode: 'Markdown'
          });
        } else if (result.error.includes('no encontrado')) {
          await ctx.reply(adminMessages.getUserNotFoundMessage(userId), {
            parse_mode: 'Markdown'
          });
        } else {
          await ctx.reply(`❌ Error: ${result.error}`, {
            parse_mode: 'Markdown'
          });
        }
      }
    } catch (error) {
      logger.error('[AdminHandler] Error en handleRemoveUser', error);
      await ctx.reply('❌ Error eliminando usuario.');
    }
  }

  async handleRemoveUserCallback(ctx, userId) {
    try {
      const removedBy = ctx.from.id;
      const result = await adminService.removeUser(userId, removedBy);

      if (result.success) {
        await ctx.editMessageText(adminMessages.getUserRemovedMessage(userId), {
          parse_mode: 'Markdown',
          ...adminKeyboards.getBackToAdminKeyboard()
        });
      } else {
        await ctx.reply(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      logger.error('[AdminHandler] Error en handleRemoveUserCallback', error);
      await ctx.reply('❌ Error eliminando usuario.');
    }
  }

  async handleListUsers(ctx, page = 1) {
    try {
      const result = await adminService.listUsers(page, 10);

      if (result.success) {
        const message = adminMessages.getUserListMessage(result.users, page, 10);
        const keyboard = adminKeyboards.getUserListPaginationKeyboard(page, result.totalPages);

        if (ctx.callbackQuery) {
          await ctx.editMessageText(message, {
            parse_mode: 'Markdown',
            ...keyboard
          });
        } else {
          await ctx.reply(message, {
            parse_mode: 'Markdown',
            ...keyboard
          });
        }
      } else {
        await ctx.reply(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      logger.error('[AdminHandler] Error en handleListUsers', error);
      await ctx.reply('❌ Error listando usuarios.');
    }
  }

  async handleUserDetail(ctx, userId = null) {
    try {
      // If no userId provided, try to get from command args
      if (!userId) {
        const args = ctx.message.text.split(' ').slice(1);
        if (args.length === 0) {
          await ctx.reply(adminMessages.getInvalidUserIdMessage(), {
            parse_mode: 'Markdown'
          });
          return;
        }
        userId = args[0];
      }

      const result = await adminService.getUserDetail(userId);

      if (result.success) {
        const message = adminMessages.getUserDetailMessage(result.user);
        const keyboard = adminKeyboards.getUserDetailKeyboard(userId);

        if (ctx.callbackQuery) {
          await ctx.editMessageText(message, {
            parse_mode: 'Markdown',
            ...keyboard
          });
        } else {
          await ctx.reply(message, {
            parse_mode: 'Markdown',
            ...keyboard
          });
        }
      } else {
        await ctx.reply(adminMessages.getUserNotFoundMessage(userId), {
          parse_mode: 'Markdown'
        });
      }
    } catch (error) {
      logger.error('[AdminHandler] Error en handleUserDetail', error);
      await ctx.reply('❌ Error obteniendo detalle de usuario.');
    }
  }

  async showRoleSelection(ctx, userId) {
    try {
      const message = `Selecciona el nuevo rol para el usuario ${userId}:`;
      const keyboard = adminKeyboards.getRoleSelectionKeyboard(userId);

      await ctx.editMessageText(message, {
        parse_mode: 'Markdown',
        ...keyboard
      });
    } catch (error) {
      logger.error('[AdminHandler] Error en showRoleSelection', error);
      await ctx.reply('❌ Error mostrando selección de rol.');
    }
  }

  async handleChangeRole(ctx, userId, newRole) {
    try {
      const changedBy = ctx.from.id;
      const result = await adminService.changeUserRole(userId, newRole, changedBy);

      if (result.success) {
        await ctx.editMessageText(adminMessages.getUserRoleChangedMessage(userId, newRole), {
          parse_mode: 'Markdown',
          ...adminKeyboards.getUserDetailKeyboard(userId)
        });
      } else {
        await ctx.reply(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      logger.error('[AdminHandler] Error en handleChangeRole', error);
      await ctx.reply('❌ Error cambiando rol de usuario.');
    }
  }

  // ============================================================================
  // 📊 STATISTICS HANDLERS
  // ============================================================================

  async handleStats(ctx) {
    try {
      const result = await adminService.getSystemStats();

      if (result.success) {
        const message = adminMessages.getSystemStatsMessage(result.stats);
        const keyboard = adminKeyboards.getStatsKeyboard();

        if (ctx.callbackQuery) {
          await ctx.editMessageText(message, {
            parse_mode: 'Markdown',
            ...keyboard
          });
        } else {
          await ctx.reply(message, {
            parse_mode: 'Markdown',
            ...keyboard
          });
        }
      } else {
        await ctx.reply(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      logger.error('[AdminHandler] Error en handleStats', error);
      await ctx.reply('❌ Error obteniendo estadísticas.');
    }
  }

  async handleHealth(ctx) {
    try {
      const result = await adminService.getSystemHealth();

      if (result.success) {
        const message = adminMessages.getSystemHealthMessage(result.health);
        const keyboard = adminKeyboards.getBackToAdminKeyboard();

        if (ctx.callbackQuery) {
          await ctx.editMessageText(message, {
            parse_mode: 'Markdown',
            ...keyboard
          });
        } else {
          await ctx.reply(message, {
            parse_mode: 'Markdown',
            ...keyboard
          });
        }
      } else {
        await ctx.reply(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      logger.error('[AdminHandler] Error en handleHealth', error);
      await ctx.reply('❌ Error obteniendo salud del sistema.');
    }
  }

  async handleDetailedStats(ctx) {
    try {
      const result = await adminService.getDetailedStats();

      if (result.success) {
        const stats = result.stats;
        
        let message = `📊 *Estadísticas Detalladas*\n\n`;
        message += `*Usuarios:* ${stats.total}\n`;
        message += `*Con WireGuard:* ${stats.withWireGuard}\n`;
        message += `*Con Outline:* ${stats.withOutline}\n\n`;
        message += `*Uso VPN:*\n`;
        message += `WG: ${stats.vpnUsage.wireguard}\n`;
        message += `OL: ${stats.vpnUsage.outline}\n`;
        message += `Total: ${stats.vpnUsage.total}\n\n`;
        message += `*Sistema:*\n`;
        message += `Platform: ${stats.system.platform}\n`;
        message += `Node: ${stats.system.nodeVersion}\n`;
        message += `Memoria: ${stats.system.totalMemory}\n`;

        await ctx.editMessageText(message, {
          parse_mode: 'Markdown',
          ...adminKeyboards.getBackToAdminKeyboard()
        });
      } else {
        await ctx.reply(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      logger.error('[AdminHandler] Error en handleDetailedStats', error);
      await ctx.reply('❌ Error obteniendo estadísticas detalladas.');
    }
  }

  // ============================================================================
  // 🔧 MAINTENANCE HANDLERS
  // ============================================================================

  async handleCleanup(ctx) {
    try {
      const result = await adminService.cleanupOrphanedData();

      if (result.success) {
        const message = adminMessages.getCleanupCompletedMessage({
          wg: result.count,
          outline: 0
        });

        if (ctx.callbackQuery) {
          await ctx.editMessageText(message, {
            parse_mode: 'Markdown',
            ...adminKeyboards.getBackToAdminKeyboard()
          });
        } else {
          await ctx.reply(message, {
            parse_mode: 'Markdown'
          });
        }
      } else {
        await ctx.reply(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      logger.error('[AdminHandler] Error en handleCleanup', error);
      await ctx.reply('❌ Error ejecutando limpieza.');
    }
  }

  async handleStorageStats(ctx) {
    try {
      const result = await adminService.getStorageStats();

      if (result.success) {
        const stats = result.stats;
        
        let message = `💾 *Estadísticas de Storage*\n\n`;
        message += `*Usuarios:*\n`;
        message += `Auth: ${stats.users.auth}\n`;
        message += `VPN: ${stats.users.vpn}\n\n`;
        
        if (stats.jobs) {
          message += `*Jobs Store:*\n`;
          message += `WG: ${stats.jobs.wg.entries} entradas\n`;
          message += `Outline: ${stats.jobs.outline.entries} entradas\n`;
          message += `Total: ${stats.jobs.total.entries} entradas\n`;
        }

        await ctx.editMessageText(message, {
          parse_mode: 'Markdown',
          ...adminKeyboards.getBackToAdminKeyboard()
        });
      } else {
        await ctx.reply(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      logger.error('[AdminHandler] Error en handleStorageStats', error);
      await ctx.reply('❌ Error obteniendo stats de storage.');
    }
  }

  async showMaintenanceMode(ctx) {
    try {
      const isEnabled = adminService.isMaintenanceMode();
      const message = adminMessages.getMaintenanceModeMessage(isEnabled);
      const keyboard = adminKeyboards.getMaintenanceModeKeyboard(isEnabled);

      await ctx.editMessageText(message, {
        parse_mode: 'Markdown',
        ...keyboard
      });
    } catch (error) {
      logger.error('[AdminHandler] Error en showMaintenanceMode', error);
      await ctx.reply('❌ Error mostrando modo mantenimiento.');
    }
  }

  async toggleMaintenanceMode(ctx, enable) {
    try {
      const result = await adminService.setMaintenanceMode(enable);

      if (result.success) {
        const message = adminMessages.getMaintenanceModeMessage(enable);
        await ctx.editMessageText(message, {
          parse_mode: 'Markdown',
          ...adminKeyboards.getBackToAdminKeyboard()
        });
      } else {
        await ctx.reply(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      logger.error('[AdminHandler] Error en toggleMaintenanceMode', error);
      await ctx.reply('❌ Error cambiando modo mantenimiento.');
    }
  }

  async handleBackup(ctx) {
    try {
      const result = await adminService.createBackup();

      if (result.success) {
        let message = `${constants.EMOJI.SUCCESS} *Backup creado*\n\n`;
        message += `Archivo: \`${result.filename}\`\n`;
        message += `Tamaño: ${(result.size / 1024).toFixed(2)} KB\n`;
        message += `Timestamp: ${new Date().toLocaleString('es-ES')}`;

        if (ctx.callbackQuery) {
          await ctx.editMessageText(message, {
            parse_mode: 'Markdown',
            ...adminKeyboards.getBackToAdminKeyboard()
          });
        } else {
          await ctx.reply(message, {
            parse_mode: 'Markdown'
          });
        }

        // Optionally send backup file
        // await ctx.replyWithDocument({ source: Buffer.from(JSON.stringify(result.backup)), filename: result.filename });
      } else {
        await ctx.reply(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      logger.error('[AdminHandler] Error en handleBackup', error);
      await ctx.reply('❌ Error creando backup.');
    }
  }

  // ============================================================================
  // 📢 BROADCAST HANDLER
  // ============================================================================

  async handleBroadcast(ctx) {
    try {
      // This would typically enter a conversation flow
      // For simplicity, showing basic implementation
      
      const args = ctx.message.text.split(' ').slice(1);
      
      if (args.length === 0) {
        await ctx.reply(
          'Uso: `/broadcast <mensaje>`\n\n' +
          'Ejemplo: `/broadcast Mantenimiento programado mañana a las 10:00`',
          { parse_mode: 'Markdown' }
        );
        return;
      }

      const message = args.join(' ');
      
      // Get notification service from global or import
      const notificationService = global.notificationService;
      
      if (!notificationService) {
        await ctx.reply('❌ Servicio de notificaciones no disponible.');
        return;
      }

      const managerService = require('../../../shared/services/manager.service');
      const users = managerService.getUsersByStatus('active');
      
      const results = await notificationService.sendBroadcast(message, users);
      
      await ctx.reply(adminMessages.getBroadcastSentMessage(results), {
        parse_mode: 'Markdown'
      });
    } catch (error) {
      logger.error('[AdminHandler] Error en handleBroadcast', error);
      await ctx.reply('❌ Error enviando broadcast.');
    }
  }
}

module.exports = AdminHandler;
