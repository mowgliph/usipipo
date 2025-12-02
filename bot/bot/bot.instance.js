// bot/bot.instance.js
const { Telegraf } = require('telegraf');
const config = require('../config/environment');
const { requireAuth, logUserAction } = require('../middleware/auth.middleware');

// Services
const NotificationService = require('../services/notification.service');

// Handlers
const AuthHandler = require('../handlers/auth.handler');
const VPNHandler = require('../handlers/vpn.handler');
const InfoHandler = require('../handlers/info.handler');

// Crear instancia del bot
const bot = new Telegraf(config.TELEGRAM_TOKEN);

// Inicializar servicios
const notificationService = new NotificationService(bot);

// Inicializar handlers
const authHandler = new AuthHandler(notificationService);
const vpnHandler = new VPNHandler();
const infoHandler = new InfoHandler();

// Aplicar middleware global de logging
bot.use(logUserAction);

// ========== COMANDOS ==========
bot.start((ctx) => authHandler.handleStart(ctx));
bot.command('miinfo', (ctx) => authHandler.handleUserInfo(ctx));
bot.command('usuarios', (ctx) => authHandler.handleListUsers(ctx));

// ========== ACCIONES DE AUTENTICACIÓN ==========
bot.action('show_my_info', (ctx) => authHandler.handleUserInfo(ctx));
bot.action('request_access', (ctx) => authHandler.handleAccessRequest(ctx));

// ========== ACCIONES DE VPN (Requieren autorización) ==========
bot.action('create_wg', requireAuth, (ctx) => vpnHandler.handleCreateWireGuard(ctx));
bot.action('create_outline', requireAuth, (ctx) => vpnHandler.handleCreateOutline(ctx));
bot.action('list_clients', requireAuth, (ctx) => vpnHandler.handleListClients(ctx));

// ========== ACCIONES INFORMATIVAS ==========
bot.action('server_status', requireAuth, (ctx) => infoHandler.handleServerStatus(ctx));
bot.action('help', (ctx) => infoHandler.handleHelp(ctx));

// ========== MANEJO DE ERRORES ==========
bot.catch(async (err, ctx) => {
  console.error(`❌ Bot error for user ${ctx.from?.id}:`, err);
  
  // Notificar al admin sobre errores críticos
  await notificationService.notifyAdminError(err.message, {
    userId: ctx.from?.id,
    updateType: ctx.updateType
  });
  
  // Responder al usuario
  ctx.reply(messages.ERROR_GENERIC).catch(() => {});
});

module.exports = bot;
