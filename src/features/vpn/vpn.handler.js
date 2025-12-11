'use strict';

/**
 * ============================================================================
 * 🎮 VPN HANDLER - uSipipo VPN Bot
 * ============================================================================
 * Controlador de comandos y callbacks para el módulo VPN.
 * Conecta la UI (Telegram) con la lógica de negocio (service).
 * 
 * 🎯 RESPONSABILIDADES:
 * - Manejar comandos /vpn, /wireguard, /outline
 * - Procesar callbacks de botones inline
 * - Gestionar flujos de conversación
 * - Enviar archivos y QR codes
 * ============================================================================
 */

const vpnService = require('./vpn.service');
const messages = require('./vpn.messages');
const keyboards = require('./vpn.keyboard');
const logger = require('../../core/utils/logger');
const managerService = require('../../shared/services/manager.service');
const { requireAuth } = require('../../core/middleware/auth.middleware');
const fs = require('fs').promises;

class VPNHandler {
  /**
   * Registra todos los handlers VPN
   */
  register(bot) {
    // ========================================================================
    // COMANDOS PRINCIPALES
    // ========================================================================

    bot.command('vpn', requireAuth, async (ctx) => {
      await this.handleVPNMainMenu(ctx);
    });

    bot.command('wireguard', requireAuth, async (ctx) => {
      await this.handleWireGuardMenu(ctx);
    });

    bot.command('wg', requireAuth, async (ctx) => {
      await this.handleWireGuardMenu(ctx);
    });

    bot.command('outline', requireAuth, async (ctx) => {
      await this.handleOutlineMenu(ctx);
    });

    // ========================================================================
    // CALLBACKS - MENÚ PRINCIPAL
    // ========================================================================

    bot.action('vpn_main_menu', requireAuth, async (ctx) => {
      await this.handleVPNMainMenu(ctx, true);
    });

    bot.action('vpn_status_summary', requireAuth, async (ctx) => {
      await this.handleStatusSummary(ctx);
    });

    bot.action('vpn_compare', requireAuth, async (ctx) => {
      await this.handleCompareProtocols(ctx);
    });

    bot.action('vpn_help', requireAuth, async (ctx) => {
      await this.handleVPNHelp(ctx);
    });

    // ========================================================================
    // CALLBACKS - WIREGUARD
    // ========================================================================

    bot.action('vpn_wireguard_menu', requireAuth, async (ctx) => {
      await this.handleWireGuardMenu(ctx, true);
    });

    bot.action('vpn_wg_menu', requireAuth, async (ctx) => {
      await this.handleWireGuardMenu(ctx, true);
    });

    bot.action('vpn_wg_create', requireAuth, async (ctx) => {
      await this.handleWireGuardCreate(ctx);
    });

    bot.action('vpn_create_wireguard', requireAuth, async (ctx) => {
      await this.handleWireGuardCreate(ctx);
    });

    bot.action('vpn_wg_view', requireAuth, async (ctx) => {
      await this.handleWireGuardView(ctx);
    });

    bot.action('vpn_wg_stats', requireAuth, async (ctx) => {
      await this.handleWireGuardStats(ctx);
    });

    bot.action('vpn_wg_stats_refresh', requireAuth, async (ctx) => {
      await this.handleWireGuardStats(ctx, true);
    });

    bot.action('vpn_wg_qr', requireAuth, async (ctx) => {
      await this.handleWireGuardQR(ctx);
    });

    bot.action('vpn_wg_config_file', requireAuth, async (ctx) => {
      await this.handleWireGuardConfigFile(ctx);
    });

    bot.action('vpn_wg_delete_confirm', requireAuth, async (ctx) => {
      await this.handleWireGuardDeleteConfirm(ctx);
    });

    bot.action('vpn_wg_delete_confirm_yes', requireAuth, async (ctx) => {
      await this.handleWireGuardDelete(ctx);
    });

    bot.action('vpn_wg_renew', requireAuth, async (ctx) => {
      await this.handleWireGuardRenew(ctx);
    });

    // ========================================================================
    // CALLBACKS - OUTLINE
    // ========================================================================

    bot.action('vpn_outline_menu', requireAuth, async (ctx) => {
      await this.handleOutlineMenu(ctx, true);
    });

    bot.action('vpn_outline_create', requireAuth, async (ctx) => {
      await this.handleOutlineCreate(ctx);
    });

    bot.action('vpn_create_outline', requireAuth, async (ctx) => {
      await this.handleOutlineCreate(ctx);
    });

    bot.action('vpn_outline_view', requireAuth, async (ctx) => {
      await this.handleOutlineView(ctx);
    });

    bot.action('vpn_outline_stats', requireAuth, async (ctx) => {
      await this.handleOutlineStats(ctx);
    });

    bot.action('vpn_outline_stats_refresh', requireAuth, async (ctx) => {
      await this.handleOutlineStats(ctx, true);
    });

    bot.action('vpn_outline_delete_confirm', requireAuth, async (ctx) => {
      await this.handleOutlineDeleteConfirm(ctx);
    });

    bot.action('vpn_outline_delete_confirm_yes', requireAuth, async (ctx) => {
      await this.handleOutlineDelete(ctx);
    });

    logger.info('[VPNHandler] Handlers registrados correctamente');
  }

  // ==========================================================================
  // 🏠 HANDLERS DE MENÚ PRINCIPAL
  // ==========================================================================

  async handleVPNMainMenu(ctx, isCallback = false) {
    try {
      const msg = messages.getVPNMainMenuMessage();
      const keyboard = keyboards.getVPNMainMenuKeyboard();

      if (isCallback) {
        await ctx.editMessageText(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
        await ctx.answerCbQuery();
      } else {
        await ctx.reply(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
      }
    } catch (error) {
      logger.error('[VPNHandler] Error en handleVPNMainMenu', error);
      await this._handleError(ctx, error, isCallback);
    }
  }

  async handleStatusSummary(ctx) {
    try {
      const userId = ctx.from.id;
      const status = await vpnService.getUserVPNStatus(userId);
      
      const msg = messages.getVPNStatusSummaryMessage(status);
      const keyboard = keyboards.getVPNSummaryKeyboard();

      await ctx.editMessageText(msg, {
        parse_mode: 'Markdown',
        ...keyboard
      });
      await ctx.answerCbQuery('📊 Estado actualizado');
    } catch (error) {
      logger.error('[VPNHandler] Error en handleStatusSummary', error);
      await this._handleError(ctx, error, true);
    }
  }

  async handleCompareProtocols(ctx) {
    try {
      const msg = messages.getVPNComparisonMessage();
      const keyboard = keyboards.getVPNCompareKeyboard();

      await ctx.editMessageText(msg, {
        parse_mode: 'Markdown',
        ...keyboard
      });
      await ctx.answerCbQuery();
    } catch (error) {
      logger.error('[VPNHandler] Error en handleCompareProtocols', error);
      await this._handleError(ctx, error, true);
    }
  }

  async handleVPNHelp(ctx) {
    try {
      const msg = `ℹ️ *Ayuda VPN*\n\n` +
                  `Aquí encontrarás información sobre cómo usar las conexiones VPN.\n\n` +
                  `Selecciona una opción:`;
      
      const keyboard = keyboards.getVPNHelpKeyboard();

      await ctx.editMessageText(msg, {
        parse_mode: 'Markdown',
        ...keyboard
      });
      await ctx.answerCbQuery();
    } catch (error) {
      logger.error('[VPNHandler] Error en handleVPNHelp', error);
      await this._handleError(ctx, error, true);
    }
  }

  // ==========================================================================
  // 🔐 HANDLERS DE WIREGUARD
  // ==========================================================================

  async handleWireGuardMenu(ctx, isCallback = false) {
    try {
      const userId = ctx.from.id;
      const user = managerService.getCompleteUser(userId);
      
      const hasConfig = !!(user && user.wg && user.wg.clientName);
      
      const msg = messages.getWireGuardWelcomeMessage();
      const keyboard = keyboards.getWireGuardMenuKeyboard(hasConfig);

      if (isCallback) {
        await ctx.editMessageText(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
        await ctx.answerCbQuery();
      } else {
        await ctx.reply(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
      }
    } catch (error) {
      logger.error('[VPNHandler] Error en handleWireGuardMenu', error);
      await this._handleError(ctx, error, isCallback);
    }
  }

  async handleWireGuardCreate(ctx) {
    try {
      await ctx.answerCbQuery('⏳ Creando configuración WireGuard...');
      
      const userId = ctx.from.id;
      
      // Verificar si puede crear
      const validation = await vpnService.canUserCreateVPN(userId, 'wireguard');
      if (!validation.allowed) {
        const msg = messages.getWireGuardAlreadyExistsMessage();
        const keyboard = keyboards.getWireGuardMenuKeyboard(true);
        
        await ctx.editMessageText(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
        return;
      }

      // Mostrar mensaje de progreso
      await ctx.editMessageText(
        '⏳ *Creando tu configuración WireGuard...*\n\n' +
        'Esto puede tardar unos segundos.\n' +
        'Estamos generando tus claves criptográficas.',
        { parse_mode: 'Markdown' }
      );

      // Crear cliente
      const result = await vpnService.createVPN(userId, 'wireguard');

      // Enviar mensaje de éxito
      const successMsg = messages.getWireGuardCreationSuccessMessage(result);
      const keyboard = keyboards.getWireGuardPostCreationKeyboard();

      await ctx.editMessageText(successMsg, {
        parse_mode: 'Markdown',
        ...keyboard
      });

      // Enviar QR automáticamente si existe
      if (result.qrCode) {
        await ctx.replyWithPhoto(
          { source: Buffer.from(result.qrCode) },
          { caption: messages.getWireGuardQRCodeMessage() }
        );
      }

      logger.info('[VPNHandler] WireGuard creado exitosamente', { userId });

    } catch (error) {
      logger.error('[VPNHandler] Error en handleWireGuardCreate', error);
      
      const errorMsg = messages.getVPNCreationErrorMessage('WireGuard', error.message);
      const keyboard = keyboards.getWireGuardMenuKeyboard(false);

      await ctx.editMessageText(errorMsg, {
        parse_mode: 'Markdown',
        ...keyboard
      });
    }
  }

  async handleWireGuardView(ctx) {
    try {
      const userId = ctx.from.id;
      const client = await vpnService.wgService.getClient(userId);

      if (!client) {
        const msg = messages.getWireGuardNotFoundMessage();
        const keyboard = keyboards.getWireGuardMenuKeyboard(false);
        
        await ctx.editMessageText(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
        await ctx.answerCbQuery('❌ Sin configuración');
        return;
      }

      if (client.suspended) {
        const msg = messages.getWireGuardSuspendedMessage(client.suspensionReason || 'Desconocido');
        const keyboard = keyboards.getWireGuardMenuKeyboard(true);
        
        await ctx.editMessageText(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
        await ctx.answerCbQuery('⚠️ Servicio suspendido');
        return;
      }

      // Mostrar configuración
      const configText = client.configContent || 'No disponible';
      const msg = `🔐 *Configuración WireGuard*\n\n` +
                  `\`\`\`\n${configText}\n\`\`\`\n\n` +
                  `Cliente: \`${client.clientName}\`\n` +
                  `IP: \`${client.ipv4}\``;

      const keyboard = keyboards.getWireGuardMenuKeyboard(true);

      await ctx.editMessageText(msg, {
        parse_mode: 'Markdown',
        ...keyboard
      });
      await ctx.answerCbQuery('✅ Configuración cargada');

    } catch (error) {
      logger.error('[VPNHandler] Error en handleWireGuardView', error);
      await this._handleError(ctx, error, true);
    }
  }

  async handleWireGuardStats(ctx, refresh = false) {
    try {
      if (refresh) {
        await ctx.answerCbQuery('🔄 Actualizando estadísticas...');
      } else {
        await ctx.answerCbQuery();
      }

      const userId = ctx.from.id;
      const client = await vpnService.wgService.getClient(userId);

      if (!client) {
        const msg = messages.getWireGuardNotFoundMessage();
        const keyboard = keyboards.getWireGuardMenuKeyboard(false);
        
        await ctx.editMessageText(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
        return;
      }

      const msg = messages.getWireGuardStatsMessage(client);
      const keyboard = keyboards.getStatsKeyboard('wireguard');

      await ctx.editMessageText(msg, {
        parse_mode: 'Markdown',
        ...keyboard
      });

    } catch (error) {
      logger.error('[VPNHandler] Error en handleWireGuardStats', error);
      await this._handleError(ctx, error, true);
    }
  }

  async handleWireGuardQR(ctx) {
    try {
      const userId = ctx.from.id;
      const user = managerService.getCompleteUser(userId);

      if (!user || !user.wg || !user.wg.qrCode) {
        await ctx.answerCbQuery('❌ Código QR no disponible');
        return;
      }

      await ctx.answerCbQuery('📱 Enviando código QR...');

      const caption = messages.getWireGuardQRCodeMessage();
      
      await ctx.replyWithPhoto(
        { source: Buffer.from(user.wg.qrCode) },
        { 
          caption,
          parse_mode: 'Markdown'
        }
      );

      logger.info('[VPNHandler] QR code enviado', { userId });

    } catch (error) {
      logger.error('[VPNHandler] Error en handleWireGuardQR', error);
      await ctx.answerCbQuery('❌ Error enviando QR');
    }
  }

  async handleWireGuardConfigFile(ctx) {
    try {
      const userId = ctx.from.id;
      const user = managerService.getCompleteUser(userId);

      if (!user || !user.wg || !user.wg.configContent) {
        await ctx.answerCbQuery('❌ Archivo no disponible');
        return;
      }

      await ctx.answerCbQuery('📄 Enviando archivo...');

      const fileName = `${user.wg.clientName}.conf`;
      const buffer = Buffer.from(user.wg.configContent, 'utf-8');

      await ctx.replyWithDocument(
        { source: buffer, filename: fileName },
        { 
          caption: messages.getWireGuardConfigFileMessage(user.wg.clientName),
          parse_mode: 'Markdown'
        }
      );

      logger.info('[VPNHandler] Config file enviado', { userId, fileName });

    } catch (error) {
      logger.error('[VPNHandler] Error en handleWireGuardConfigFile', error);
      await ctx.answerCbQuery('❌ Error enviando archivo');
    }
  }

  async handleWireGuardDeleteConfirm(ctx) {
    try {
      const userId = ctx.from.id;
      const user = managerService.getCompleteUser(userId);

      if (!user || !user.wg) {
        await ctx.answerCbQuery('❌ Sin configuración para eliminar');
        return;
      }

      const msg = messages.getWireGuardDeleteConfirmMessage(user.wg.clientName);
      const keyboard = keyboards.getWireGuardDeleteConfirmKeyboard();

      await ctx.editMessageText(msg, {
        parse_mode: 'Markdown',
        ...keyboard
      });
      await ctx.answerCbQuery();

    } catch (error) {
      logger.error('[VPNHandler] Error en handleWireGuardDeleteConfirm', error);
      await this._handleError(ctx, error, true);
    }
  }

  async handleWireGuardDelete(ctx) {
    try {
      await ctx.answerCbQuery('🗑️ Eliminando configuración...');

      const userId = ctx.from.id;
      const user = managerService.getCompleteUser(userId);
      const clientName = user.wg.clientName;

      await vpnService.deleteVPN(userId, 'wireguard');

      const msg = messages.getWireGuardDeletedMessage(clientName);
      const keyboard = keyboards.getWireGuardMenuKeyboard(false);

      await ctx.editMessageText(msg, {
        parse_mode: 'Markdown',
        ...keyboard
      });

      logger.info('[VPNHandler] WireGuard eliminado', { userId, clientName });

    } catch (error) {
      logger.error('[VPNHandler] Error en handleWireGuardDelete', error);
      await this._handleError(ctx, error, true);
    }
  }

  async handleWireGuardRenew(ctx) {
    try {
      await ctx.answerCbQuery('🔄 Renovando configuración...');

      const userId = ctx.from.id;

      // Eliminar configuración actual
      await vpnService.deleteVPN(userId, 'wireguard');

      // Crear nueva
      const result = await vpnService.createVPN(userId, 'wireguard');

      const msg = `✅ *Configuración renovada*\n\n` +
                  messages.getWireGuardCreationSuccessMessage(result);
      
      const keyboard = keyboards.getWireGuardPostCreationKeyboard();

      await ctx.editMessageText(msg, {
        parse_mode: 'Markdown',
        ...keyboard
      });

      logger.info('[VPNHandler] WireGuard renovado', { userId });

    } catch (error) {
      logger.error('[VPNHandler] Error en handleWireGuardRenew', error);
      await this._handleError(ctx, error, true);
    }
  }

  // ==========================================================================
  // 🌐 HANDLERS DE OUTLINE
  // ==========================================================================

  async handleOutlineMenu(ctx, isCallback = false) {
    try {
      const userId = ctx.from.id;
      const user = managerService.getCompleteUser(userId);
      
      const hasKey = !!(user && user.outline && user.outline.keyId);
      
      const msg = messages.getOutlineWelcomeMessage();
      const keyboard = keyboards.getOutlineMenuKeyboard(hasKey);

      if (isCallback) {
        await ctx.editMessageText(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
        await ctx.answerCbQuery();
      } else {
        await ctx.reply(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
      }
    } catch (error) {
      logger.error('[VPNHandler] Error en handleOutlineMenu', error);
      await this._handleError(ctx, error, isCallback);
    }
  }

  async handleOutlineCreate(ctx) {
    try {
      await ctx.answerCbQuery('⏳ Creando clave Outline...');
      
      const userId = ctx.from.id;
      
      // Verificar si puede crear
      const validation = await vpnService.canUserCreateVPN(userId, 'outline');
      if (!validation.allowed) {
        const msg = messages.getOutlineAlreadyExistsMessage();
        const keyboard = keyboards.getOutlineMenuKeyboard(true);
        
        await ctx.editMessageText(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
        return;
      }

      // Mostrar mensaje de progreso
      await ctx.editMessageText(
        '⏳ *Creando tu clave Outline...*\n\n' +
        'Conectando con el servidor...',
        { parse_mode: 'Markdown' }
      );

      // Crear clave
      const result = await vpnService.createVPN(userId, 'outline', {
        name: `Usuario ${userId}`
      });

      // Enviar mensaje de éxito
      const successMsg = messages.getOutlineCreationSuccessMessage(result);
      const keyboard = keyboards.getOutlinePostCreationKeyboard();

      await ctx.editMessageText(successMsg, {
        parse_mode: 'Markdown',
        ...keyboard
      });

      // Enviar enlace de acceso en mensaje separado
      const urlMsg = messages.getOutlineAccessUrlMessage(result.accessUrl, result.name);
      await ctx.reply(urlMsg, { parse_mode: 'Markdown' });

      logger.info('[VPNHandler] Outline creado exitosamente', { userId, keyId: result.keyId });

    } catch (error) {
      logger.error('[VPNHandler] Error en handleOutlineCreate', error);
      
      const errorMsg = messages.getVPNCreationErrorMessage('Outline', error.message);
      const keyboard = keyboards.getOutlineMenuKeyboard(false);

      await ctx.editMessageText(errorMsg, {
        parse_mode: 'Markdown',
        ...keyboard
      });
    }
  }

  async handleOutlineView(ctx) {
    try {
      const userId = ctx.from.id;
      const key = await vpnService.outlineService.getKey(userId);

      if (!key) {
        const msg = messages.getOutlineNotFoundMessage();
        const keyboard = keyboards.getOutlineMenuKeyboard(false);
        
        await ctx.editMessageText(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
        await ctx.answerCbQuery('❌ Sin clave activa');
        return;
      }

      if (key.suspended) {
        const msg = messages.getOutlineSuspendedMessage(key.suspensionReason || 'Desconocido');
        const keyboard = keyboards.getOutlineMenuKeyboard(true);
        
        await ctx.editMessageText(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
        await ctx.answerCbQuery('⚠️ Servicio suspendido');
        return;
      }

      const msg = messages.getOutlineAccessUrlMessage(key.accessUrl, key.name);
      const keyboard = keyboards.getOutlineMenuKeyboard(true);

      await ctx.editMessageText(msg, {
        parse_mode: 'Markdown',
        ...keyboard
      });
      await ctx.answerCbQuery('✅ Enlace cargado');

    } catch (error) {
      logger.error('[VPNHandler] Error en handleOutlineView', error);
      await this._handleError(ctx, error, true);
    }
  }

  async handleOutlineStats(ctx, refresh = false) {
    try {
      if (refresh) {
        await ctx.answerCbQuery('🔄 Actualizando estadísticas...');
      } else {
        await ctx.answerCbQuery();
      }

      const userId = ctx.from.id;
      const key = await vpnService.outlineService.getKey(userId);

      if (!key) {
        const msg = messages.getOutlineNotFoundMessage();
        const keyboard = keyboards.getOutlineMenuKeyboard(false);
        
        await ctx.editMessageText(msg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
        return;
      }

      const msg = messages.getOutlineStatsMessage(key);
      const keyboard = keyboards.getStatsKeyboard('outline');

      await ctx.editMessageText(msg, {
        parse_mode: 'Markdown',
        ...keyboard
      });

    } catch (error) {
      logger.error('[VPNHandler] Error en handleOutlineStats', error);
      await this._handleError(ctx, error, true);
    }
  }

  async handleOutlineDeleteConfirm(ctx) {
    try {
      const userId = ctx.from.id;
      const user = managerService.getCompleteUser(userId);

      if (!user || !user.outline) {
        await ctx.answerCbQuery('❌ Sin clave para eliminar');
        return;
      }

      const msg = messages.getOutlineDeleteConfirmMessage(user.outline.name);
      const keyboard = keyboards.getOutlineDeleteConfirmKeyboard();

      await ctx.editMessageText(msg, {
        parse_mode: 'Markdown',
        ...keyboard
      });
      await ctx.answerCbQuery();

    } catch (error) {
      logger.error('[VPNHandler] Error en handleOutlineDeleteConfirm', error);
      await this._handleError(ctx, error, true);
    }
  }

  async handleOutlineDelete(ctx) {
    try {
      await ctx.answerCbQuery('🗑️ Eliminando clave...');

      const userId = ctx.from.id;
      const user = managerService.getCompleteUser(userId);
      const keyName = user.outline.name;

      await vpnService.deleteVPN(userId, 'outline');

      const msg = messages.getOutlineDeletedMessage(keyName);
      const keyboard = keyboards.getOutlineMenuKeyboard(false);

      await ctx.editMessageText(msg, {
        parse_mode: 'Markdown',
        ...keyboard
      });

      logger.info('[VPNHandler] Outline eliminado', { userId, keyName });

    } catch (error) {
      logger.error('[VPNHandler] Error en handleOutlineDelete', error);
      await this._handleError(ctx, error, true);
    }
  }

  // ==========================================================================
  // 🛠️ UTILIDADES PRIVADAS
  // ==========================================================================

  async _handleError(ctx, error, isCallback = false) {
    const errorMsg = messages.getVPNServerErrorMessage();
    const keyboard = keyboards.getVPNMainMenuKeyboard();

    try {
      if (isCallback) {
        await ctx.editMessageText(errorMsg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
        await ctx.answerCbQuery('❌ Error');
      } else {
        await ctx.reply(errorMsg, {
          parse_mode: 'Markdown',
          ...keyboard
        });
      }
    } catch (replyError) {
      logger.error('[VPNHandler] Error enviando mensaje de error', replyError);
    }
  }
}

module.exports = new VPNHandler();
