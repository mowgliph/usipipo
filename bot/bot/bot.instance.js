/**
 * @fileoverview bot.instance.js — Instancia principal del bot uSipipo VPN (v1.1.0)
 * @version 1.1.0
 * @author Team uSipipo
 * @description Bot Telegraf con handlers modulares, StartHandler premium y UI limpia.
 */

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

// 🆕 Handlers
const StartHandler = require('../handlers/start.handler');
const AuthHandler = require('../handlers/auth.handler');
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
  telegram: { parse_mode: 'Markdown' }
});

const notificationService = new NotificationService(bot);

// 🆕 Instancias de handlers
const startHandler = new StartHandler();
const authHandler = new AuthHandler(notificationService);
const infoHandler = new InfoHandler();
const adminHandler = new AdminHandler(notificationService);

// =====================================================================================
// 🟣 GLOBAL MIDDLEWARE
// =====================================================================================

bot.use(logUserAction);

// =====================================================================================
// 🟢 USER COMMANDS — MIGRANTES A START HANDLER
// =====================================================================================

// ⭐ /start → StartHandler (nuevo estándar premium)
bot.command('start', (ctx) => startHandler.handleStart(ctx));

bot.command('miinfo', (ctx) => authHandler.handleUserInfo(ctx));
bot.command('status', (ctx) => authHandler.handleCheckStatus(ctx));
bot.command('help', (ctx) => infoHandler.handleHelp(ctx));
bot.command('commands', (ctx) => infoHandler.handleCommandList(ctx));

// Comandos VPN específicos
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

    // ✅ FIX: Markdown V1 correcto con 


    await ctx.reply(
      `✅ *Admin sincronizado correctamente*

🆔 `${config.ADMIN_ID}``
    );
  } catch (error) {
    await ctx.reply(`❌ Error: ${error.message}`);
  }
});

// =====================================================================================
// 🟦 APP-STYLE NAVIGATION MENUS (UI / Botones)
// =====================================================================================

// ⭐ BOTÓN "Volver al Inicio" → StartHandler
bot.action('start', (ctx) => startHandler.handleStart(ctx));

// ----------- USER MAIN NAVIGATION -----------
bot.action('show_my_info', (ctx) => authHandler.handleUserInfo(ctx));
bot.action('request_access', (ctx) => authHandler.handleAccessRequest(ctx));
bot.action('check_status', (ctx) => authHandler.handleCheckStatus(ctx));

// ----------- VPN ACTIONS -----------
bot.action('vpn_menu', requireAuth, (ctx) => vpnHandler.actionVpnMenu(ctx));
bot.action('wg_menu', requireAuth, (ctx) => vpnHandler.actionWgMenu(ctx));
bot.action('outline_menu', requireAuth, (ctx) => vpnHandler.actionOutlineMenu(ctx));
bot.action('create_wg', requireAuth, (ctx) => vpnHandler.handleCreateWireGuard(ctx));
bot.action('wg_show', requireAuth, (ctx) => vpnHandler.actionWgShowConfig(ctx));
bot.action('wg_download', requireAuth, (ctx) => vpnHandler.actionWgDownload(ctx));
bot.action('wg_qr', requireAuth, (ctx) => vpnHandler.actionWgQr(ctx));
bot.action('wg_usage', requireAuth, (ctx) => vpnHandler.actionWgUsage(ctx));
bot.action('wg_delete', requireAuth, (ctx) => vpnHandler.actionWgDelete(ctx));
bot.action('create_outline', requireAuth, (ctx) => vpnHandler.handleCreateOutline(ctx));
bot.action('outline_show', requireAuth, (ctx) => vpnHandler.actionOutlineShow(ctx));
bot.action('outline_usage', requireAuth, (ctx) => vpnHandler.actionOutlineUsage(ctx));
bot.action('outline_delete', requireAuth, (ctx) => vpnHandler.actionOutlineDelete(ctx));
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
// 🟨 TEXT HANDLER → fallback al menú principal
// =====================================================================================

bot.on('text', async (ctx) => {
  const userId = ctx.from?.id;
  const text = ctx.message?.text?.trim() || '';

  try {
    if (text.startsWith('/')) {
      const admin = isAdmin(userId);
      return ctx.reply(messages.UNKNOWN_COMMAND(admin));
    }
    
    // ⭐ FALLBACK → StartHandler (menú principal)
    return startHandler.handleStart(ctx);
    
  } catch (err) {
    logger.error('text_handler', err, { userId });
  }
});

// =====================================================================================
// EXPORT
// =====================================================================================

module.exports = { bot, notificationService };