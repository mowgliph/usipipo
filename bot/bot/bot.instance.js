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
const VPNHandler = require('../handlers/vpn.handler');
const InfoHandler = require('../handlers/info.handler');
const AdminHandler = require('../handlers/admin.handler');

// Utils
const messages = require('../utils/messages');
const keyboards = require('../utils/keyboards');

// ---------------------------------------------------------------------------
// 🟦 BOT INSTANCE
// ---------------------------------------------------------------------------

const bot = new Telegraf(config.TELEGRAM_TOKEN, {
  handlerTimeout: 90_000,
  telegram: { parse_mode: 'HTML' } // Forzar HTML global
});

// Centralizamos NotificationService para que toda la app use una sola instancia
const notificationService = new NotificationService(bot);

// Handlers instanciados
const authHandler = new AuthHandler(notificationService);
const vpnHandler = new VPNHandler();
const infoHandler = new InfoHandler();
const adminHandler = new AdminHandler(notificationService);

// ---------------------------------------------------------------------------
// 🟪 GLOBAL MIDDLEWARE
// ---------------------------------------------------------------------------

bot.use(logUserAction);

// ---------------------------------------------------------------------------
// 🟩 COMMAND HANDLERS
// ---------------------------------------------------------------------------

// User Commands
bot.command('start', (ctx) => authHandler.handleStart(ctx));
bot.command('miinfo', (ctx) => authHandler.handleUserInfo(ctx));
bot.command('status', (ctx) => authHandler.handleCheckStatus(ctx));
bot.command('help', (ctx) => authHandler.handleHelp(ctx));
bot.command('commands', (ctx) => infoHandler.handleCommandList(ctx));

// Admin Commands
bot.command('add', requireAdmin, (ctx) => adminHandler.handleAddUser(ctx));
bot.command('rm', requireAdmin, (ctx) => adminHandler.handleRemoveUser(ctx));
bot.command('sus', requireAdmin, (ctx) => adminHandler.handleSuspendUser(ctx));
bot.command('react', requireAdmin, (ctx) => adminHandler.handleReactivateUser(ctx));
bot.command('users', requireAdmin, (ctx) => adminHandler.handleListUsers(ctx));
bot.command('stats', requireAdmin, (ctx) => adminHandler.handleStats(ctx));
bot.command('broadcast', requireAdmin, (ctx) => adminHandler.handleBroadcast(ctx));
bot.command('sms', requireAdmin, (ctx) => adminHandler.handleDirectMessage(ctx));
bot.command('templates', requireAdmin, (ctx) => adminHandler.handleTemplates(ctx));

// System-only emergency command
bot.command('forceadmin', async (ctx) => {
  const userId = ctx.from.id.toString();

  if (userId !== config.ADMIN_ID) {
    return ctx.reply('⛔ Solo el Admin configurado en <b>.env</b> puede usar este comando.');
  }

  try {
    const userManager = require('../services/userManager.service');

    await userManager.syncAdminFromEnv();

    await ctx.reply(
      `✅ <b>Sincronización completada</b>\n
🆔 Admin: <code>${config.ADMIN_ID}</code>\n👑 Rol: Administrador\n
Ahora puedes usar <b>/stats</b> o <b>/users</b>.`
    );

    logger.success(userId, 'forceadmin', config.ADMIN_ID);
  } catch (error) {
    logger.error('forceadmin', error, { userId });
    await ctx.reply(`❌ Error: ${error.message}`);
  }
});

// ---------------------------------------------------------------------------
// 🟧 ACTION HANDLERS (Botones Inline)
// ---------------------------------------------------------------------------

// User actions
bot.action('show_my_info', (ctx) => authHandler.handleUserInfo(ctx));
bot.action('request_access', (ctx) => authHandler.handleAccessRequest(ctx));
bot.action('check_status', (ctx) => authHandler.handleCheckStatus(ctx));

bot.action('create_wg', requireAuth, (ctx) => vpnHandler.handleCreateWireGuard(ctx));
bot.action('create_outline', requireAuth, (ctx) => vpnHandler.handleCreateOutline(ctx));
bot.action('list_clients', requireAuth, (ctx) => vpnHandler.handleListClients(ctx));

bot.action('server_status', requireAuth, (ctx) => infoHandler.handleServerStatus(ctx));
bot.action('help', (ctx) => infoHandler.handleHelp(ctx));

// Broadcast dynamic actions
bot.action(/^broadcast_(all|users|admins)_(.+)$/, requireAdmin, (ctx) => {
  const [_, scope, id] = ctx.match;
  return adminHandler.handleBroadcastConfirm(ctx, id, scope);
});

bot.action(/^broadcast_cancel_(.+)$/, requireAdmin, (ctx) => {
  const broadcastId = ctx.match[1];
  return adminHandler.handleBroadcastCancel(ctx, broadcastId);
});

// ---------------------------------------------------------------------------
// 🟥 CATCH-ALL ERROR HANDLER
// ---------------------------------------------------------------------------

bot.catch(async (err, ctx) => {
  const userId = ctx.from?.id;
  const updateType = ctx.updateType;

  logger.error('bot.catch', err, { userId, updateType });

  try {
    await notificationService.notifyAdminError(err.message, { userId, updateType });
  } catch (notifyError) {
    logger.warn('Error notificando al admin', { notifyError: notifyError.message });
  }

  await ctx.reply(messages.ERROR_GENERIC).catch(() => {});
});

// ---------------------------------------------------------------------------
// 🟨 GENERIC MESSAGE HANDLER
// ---------------------------------------------------------------------------

bot.on('text', async (ctx) => {
  const userId = ctx.from?.id;
  const userName = ctx.from?.first_name || 'usuario';
  const text = ctx.message.text.trim();

  try {
    // Unknown command
    if (text.startsWith('/')) {
      const adminStatus = isAdmin(userId);
      await ctx.reply(messages.UNKNOWN_COMMAND(adminStatus));
      logger.verbose('unknown_command', { userId, text });
      return;
    }

    // Generic text => show menu
    await ctx.reply(messages.GENERIC_TEXT_PROMPT(userName), {
      reply_markup: keyboards.vpnSelectionMenu().reply_markup
    });

    logger.verbose('generic_message', { userId, text });

  } catch (err) {
    logger.error('text_handler', err, { userId });
  }
});

// ---------------------------------------------------------------------------
// EXPORTS
// ---------------------------------------------------------------------------

module.exports = { bot, notificationService };