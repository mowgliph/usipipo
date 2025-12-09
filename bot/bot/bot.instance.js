'use strict';

const { Telegraf } = require('telegraf');
const config = require('../config/environment');
const logger = require('../utils/logger');

// Middlewares
const {
  requireAuth,
  requireAdmin,
  logUserAction,
  isAdmin
} = require('../middleware/auth.middleware');

// Services
const NotificationService = require('../services/notification.service');

// Handlers
const AuthHandler = require('../handlers/auth.handler');
// CAMBIO 1: Importamos la instancia directamente (vpnHandler con minúscula)
const vpnHandler = require('../handlers/vpn.handler'); 
const InfoHandler = require('../handlers/info.handler');
const AdminHandler = require('../handlers/admin.handler');

// Keyboards & UI
const keyboards = require('../utils/keyboards');
const messages = require('../utils/messages');

// =====================================================================================
// 🔵 BOT INSTANCE
// =====================================================================================

const bot = new Telegraf(config.TELEGRAM_TOKEN, {
  handlerTimeout: 90_000,
  telegram: { parse_mode: 'HTML' }
});

const notificationService = new NotificationService(bot);

const authHandler = new AuthHandler(notificationService);
// CAMBIO 2: Eliminamos la línea "const vpnHandler = new VPNHandler();" 
// porque ya importamos la instancia arriba.
const infoHandler = new InfoHandler();
const adminHandler = new AdminHandler(notificationService);

// =====================================================================================
// 🟣 GLOBAL MIDDLEWARE
// =====================================================================================

bot.use(logUserAction);

// =====================================================================================
// 🟢 USER COMMANDS
// =====================================================================================

bot.command('start', (ctx) => authHandler.handleStart(ctx));
bot.command('miinfo', (ctx) => authHandler.handleUserInfo(ctx));
bot.command('status', (ctx) => authHandler.handleCheckStatus(ctx));
bot.command('help', (ctx) => authHandler.handleHelp(ctx));
bot.command('commands', (ctx) => infoHandler.handleCommandList(ctx));

// Comandos VPN específicos (agregados por seguridad si no estaban antes)
bot.command('vpn', (ctx) => vpnHandler.cmdVpn(ctx));

// =====================================================================================
// 🟡 ADMIN COMMANDS
// =====================================================================================

bot.command('add', requireAdmin, (ctx) => adminHandler.handleAddUser(ctx));
bot.command('rm', requireAdmin, (ctx) => adminHandler.handleRemoveUser(ctx));
bot.command('sus', requireAdmin, (ctx) => adminHandler.handleSuspendUser(ctx));
bot.command('react', requireAdmin, (ctx) => adminHandler.handleReactivateUser(ctx));
bot.command('users', requireAdmin, (ctx) => adminHandler.handleListUsers(ctx));
bot.command('stats', requireAdmin, (ctx) => adminHandler.handleStats(ctx));
bot.command('broadcast', requireAdmin, (ctx) => adminHandler.handleBroadcast(ctx));
bot.command('sms', requireAdmin, (ctx) => adminHandler.handleDirectMessage(ctx));
bot.command('templates', requireAdmin, (ctx) => adminHandler.handleTemplates(ctx));

// =====================================================================================
// 🔴 SYSTEM COMMAND (emergency use only)
// =====================================================================================

bot.command('forceadmin', async (ctx) => {
  const userId = ctx.from.id.toString();

  if (userId !== config.ADMIN_ID) {
    return ctx.reply('⛔ Solo el Admin principal definido en .env puede usar este comando.');
  }

  try {
    const userManager = require('../services/userManager.service');
    await userManager.syncAdminFromEnv();

    await ctx.reply(
      `✅ <b>Admin sincronizado correctamente</b>\n\n🆔 <code>${config.ADMIN_ID}</code>`
    );
  } catch (error) {
    await ctx.reply(`❌ Error: ${error.message}`);
  }
});

// =====================================================================================
// 🟦 APP-STYLE NAVIGATION MENUS (UI / Botones)
// =====================================================================================

// ----------- USER MAIN NAVIGATION -----------
bot.action('show_my_info', (ctx) => authHandler.handleUserInfo(ctx));
bot.action('request_access', (ctx) => authHandler.handleAccessRequest(ctx));
bot.action('check_status', (ctx) => authHandler.handleCheckStatus(ctx));

// ----------- VPN ACTIONS -----------
bot.action('vpn_menu', requireAuth, (ctx) => vpnHandler.actionVpnMenu(ctx)); // Agregado por seguridad
bot.action('wg_menu', requireAuth, (ctx) => vpnHandler.actionWgMenu(ctx)); // Agregado
bot.action('outline_menu', requireAuth, (ctx) => vpnHandler.actionOutlineMenu(ctx)); // Agregado
bot.action('create_wg', requireAuth, (ctx) => vpnHandler.handleCreateWireGuard(ctx));
bot.action('wg_show', requireAuth, (ctx) => vpnHandler.actionWgShowConfig(ctx)); // Agregado
bot.action('wg_download', requireAuth, (ctx) => vpnHandler.actionWgDownload(ctx)); // Agregado
bot.action('wg_qr', requireAuth, (ctx) => vpnHandler.actionWgShowQr(ctx)); // Agregado
bot.action('wg_usage', requireAuth, (ctx) => vpnHandler.actionWgUsage(ctx)); // Agregado
bot.action('wg_delete', requireAuth, (ctx) => vpnHandler.actionWgDelete(ctx)); // Agregado
bot.action('create_outline', requireAuth, (ctx) => vpnHandler.handleCreateOutline(ctx));
bot.action('outline_show', requireAuth, (ctx) => vpnHandler.actionOutlineShow(ctx)); // Agregado
bot.action('outline_usage', requireAuth, (ctx) => vpnHandler.actionOutlineUsage(ctx)); // Agregado
bot.action('outline_delete', requireAuth, (ctx) => vpnHandler.actionOutlineDelete(ctx)); // Agregado
bot.action('list_clients', requireAuth, (ctx) => vpnHandler.handleListClients(ctx));

// ----------- SYSTEM / HELP -----------
bot.action('server_status', requireAuth, (ctx) => infoHandler.handleServerStatus(ctx));
bot.action('help', (ctx) => infoHandler.handleHelp(ctx));

// =====================================================================================
// 🔥 UNIVERSAL CONFIRMATION SYSTEM
// =====================================================================================

// Cancelar acción
bot.action('cancel_action', async (ctx) => {
  await ctx.answerCbQuery().catch(() => {});
  return ctx.editMessageText('❌ Acción cancelada.');
});

// ----- ADMIN destructive confirmations -----

bot.action(/^confirm_admin_rm_(.+)$/, requireAdmin, (ctx) => {
  const userId = ctx.match[1];
  return adminHandler.confirmRemoveUser(ctx, userId);
});

bot.action(/^confirm_admin_sus_(.+)$/, requireAdmin, (ctx) => {
  const userId = ctx.match[1];
  return adminHandler.confirmSuspendUser(ctx, userId);
});

bot.action(/^confirm_admin_react_(.+)$/, requireAdmin, (ctx) => {
  const userId = ctx.match[1];
  return adminHandler.confirmReactivateUser(ctx, userId);
});

// ----- VPN destructive confirmations -----

bot.action(/^confirm_delete_wg_(.+)$/, requireAuth, (ctx) => {
  const id = ctx.match[1];
  return vpnHandler.confirmDeleteWireGuard(ctx, id);
});

bot.action(/^confirm_delete_outline_(.+)$/, requireAuth, (ctx) => {
  const keyId = ctx.match[1];
  return vpnHandler.confirmDeleteOutlineKey(ctx, keyId);
});

// =====================================================================================
// 📢 BROADCAST dynamic confirm system
// =====================================================================================

bot.action(/^broadcast_(all|users|admins)_(.+)$/, requireAdmin, (ctx) => {
  const [_, scope, id] = ctx.match;
  return adminHandler.handleBroadcastConfirm(ctx, id, scope);
});

bot.action(/^broadcast_cancel_(.+)$/, requireAdmin, (ctx) => {
  const id = ctx.match[1];
  return adminHandler.handleBroadcastCancel(ctx, id);
});

// =====================================================================================
// GLOBAL ERROR HANDLER
// =====================================================================================

bot.catch(async (err, ctx) => {
  const userId = ctx.from?.id;
  logger.error('bot.catch', err, { userId });

  try {
    await notificationService.notifyAdminError(err.message, { userId });
  } catch (_) {}

  await ctx.reply(messages.ERROR_GENERIC).catch(() => {});
});

// =====================================================================================
// 🟨 TEXT HANDLER → fallback al menú VPN
// =====================================================================================

bot.on('text', async (ctx) => {
  const userId = ctx.from?.id;
  const text = ctx.message?.text?.trim() || '';

  try {
    if (text.startsWith('/')) {
      const admin = isAdmin(userId);
      return ctx.reply(messages.UNKNOWN_COMMAND(admin));
    }
    
    // Si tienes un menú de selección VPN en keyboards.js
    if (keyboards.vpnSelectionMenu) {
       return ctx.reply(
          messages.GENERIC_TEXT_PROMPT(ctx.from?.first_name),
          keyboards.vpnSelectionMenu()
       );
    } else {
       // Fallback simple si no existe vpnSelectionMenu
       return ctx.reply('Use /help para ver los comandos.');
    }

  } catch (err) {
    logger.error('text_handler', err, { userId });
  }
});

// =====================================================================================
// EXPORT
// =====================================================================================

module.exports = { bot, notificationService };
