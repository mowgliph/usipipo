// bot/bot.instance.js
'use strict';

const { Telegraf } = require('telegraf');
const config = require('../config/environment');
const logger = require('../utils/logger');

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

// Inicialización del bot con configuración global HTML
const bot = new Telegraf(config.TELEGRAM_TOKEN, {
  handlerTimeout: 90_000, // 90s timeout para operaciones largas
  telegram: {
    parse_mode: 'HTML' // Default global para todo el proyecto
  }
});

const notificationService = new NotificationService(bot);

const authHandler = new AuthHandler(notificationService);
const vpnHandler = new VPNHandler();
const infoHandler = new InfoHandler();
const adminHandler = new AdminHandler(notificationService);

// Middleware global
bot.use(logUserAction);

// =====================================================
// COMANDOS DE USUARIO
// =====================================================

bot.command('start', (ctx) => authHandler.handleStart(ctx));
bot.command('miinfo', (ctx) => authHandler.handleUserInfo(ctx));
bot.command('status', (ctx) => authHandler.handleCheckStatus(ctx));
bot.command('help', (ctx) => authHandler.handleHelp(ctx));
bot.command('commands', (ctx) => infoHandler.handleCommandList(ctx));

// =====================================================
// COMANDOS DE ADMINISTRACIÓN (Solo Admin)
// =====================================================

bot.command('add', requireAdmin, (ctx) => adminHandler.handleAddUser(ctx));
bot.command('rm', requireAdmin, (ctx) => adminHandler.handleRemoveUser(ctx));
bot.command('sus', requireAdmin, (ctx) => adminHandler.handleSuspendUser(ctx));
bot.command('react', requireAdmin, (ctx) => adminHandler.handleReactivateUser(ctx));
bot.command('users', requireAdmin, (ctx) => adminHandler.handleListUsers(ctx));
bot.command('stats', requireAdmin, (ctx) => adminHandler.handleStats(ctx));
bot.command('broadcast', requireAdmin, (ctx) => adminHandler.handleBroadcast(ctx));
bot.command('sms', requireAdmin, (ctx) => adminHandler.handleDirectMessage(ctx));
bot.command('templates', requireAdmin, (ctx) => adminHandler.handleTemplates(ctx));

// =====================================================
// ACCIONES DE AUTENTICACIÓN
// =====================================================

bot.action('show_my_info', (ctx) => authHandler.handleUserInfo(ctx));
bot.action('request_access', (ctx) => authHandler.handleAccessRequest(ctx));
bot.action('check_status', (ctx) => authHandler.handleCheckStatus(ctx));

// =====================================================
// ACCIONES DE VPN (Requiere autorización)
// =====================================================

bot.action('create_wg', requireAuth, (ctx) => vpnHandler.handleCreateWireGuard(ctx));
bot.action('create_outline', requireAuth, (ctx) => vpnHandler.handleCreateOutline(ctx));
bot.action('list_clients', requireAuth, (ctx) => vpnHandler.handleListClients(ctx));

// =====================================================
// ACCIONES INFORMATIVAS
// =====================================================

bot.action('server_status', requireAuth, (ctx) => infoHandler.handleServerStatus(ctx));
bot.action('help', (ctx) => infoHandler.handleHelp(ctx));

// =====================================================
// ACCIONES DE BROADCAST (Solo Admin)
// =====================================================

bot.action(/^broadcast_all_(.+)$/, requireAdmin, (ctx) => {
  const broadcastId = ctx.match[1];
  return adminHandler.handleBroadcastConfirm(ctx, broadcastId, 'all');
});

bot.action(/^broadcast_users_(.+)$/, requireAdmin, (ctx) => {
  const broadcastId = ctx.match[1];
  return adminHandler.handleBroadcastConfirm(ctx, broadcastId, 'users');
});

bot.action(/^broadcast_admins_(.+)$/, requireAdmin, (ctx) => {
  const broadcastId = ctx.match[1];
  return adminHandler.handleBroadcastConfirm(ctx, broadcastId, 'admins');
});

bot.action(/^broadcast_cancel_(.+)$/, requireAdmin, (ctx) => {
  const broadcastId = ctx.match[1];
  return adminHandler.handleBroadcastCancel(ctx, broadcastId);
});

// =====================================================
// HANDLER DE ERRORES GLOBALES
// =====================================================

bot.catch(async (err, ctx) => {
  const userId = ctx.from?.id;
  const updateType = ctx.updateType;

  logger.error('bot.catch', err, { userId, updateType });

  try {
    await notificationService.notifyAdminError(err.message, { userId, updateType });
  } catch (notifyError) {
    logger.warn('Error notificando al admin', { notifyError: notifyError.message });
  }

  // Se asume que messages.ERROR_GENERIC será actualizado a HTML o texto plano
  await ctx.reply(messages.ERROR_GENERIC).catch(() => {});
});

// =====================================================
// COMANDO DE EMERGENCIA (Solo Admin .env)
// =====================================================

bot.command('forceadmin', async (ctx) => {
  const userId = ctx.from.id.toString();
  const envAdminId = config.ADMIN_ID;

  if (userId !== envAdminId) {
    return ctx.reply('⛔ Solo el Admin configurado en .env puede usar este comando.');
  }

  try {
    const userManager = require('../services/userManager.service');
    await userManager.syncAdminFromEnv();

    await ctx.reply(
      `✅ <b>Sincronización forzada completada</b>

🆔 Admin ID: <code>${envAdminId}</code>
👑 Rol: Administrador

Prueba ahora: /stats o /users`
    );

    logger.success(userId, 'forceadmin', envAdminId);
  } catch (error) {
    logger.error('forceadmin', error, { userId });
    await ctx.reply(`❌ Error: ${error.message}`);
  }
});

// =====================================================
// HANDLER DE TEXTO LIBRE Y COMANDOS NO RECONOCIDOS
// =====================================================

bot.on('text', async (ctx) => {
  const userId = ctx.from?.id;
  const userName = ctx.from?.first_name || 'usuario';
  const messageText = ctx.message.text.trim();

  try {
    if (messageText.startsWith('/')) {
      const adminStatus = isAdmin(userId);
      // Eliminado parse_mode explícito, usa global HTML
      await ctx.reply(messages.UNKNOWN_COMMAND(adminStatus));
      logger.verbose('unknown_command', { userId, text: messageText });
    } else {
      // Eliminado parse_mode explícito, usa global HTML
      await ctx.reply(messages.GENERIC_TEXT_PROMPT(userName), {
        reply_markup: keyboards.vpnSelectionMenu().reply_markup
      });
      logger.verbose('generic_message', { userId, text: messageText });
    }
  } catch (err) {
    logger.error('text_handler', err, { userId });
  }
});

module.exports = bot;
