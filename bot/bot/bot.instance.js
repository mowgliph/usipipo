// bot/bot.instance.js
const { Telegraf } = require('telegraf');
const config = require('../config/environment');
const { requireAuth, requireAdmin, logUserAction } = require('../middleware/auth.middleware');

// Services
const NotificationService = require('../services/notification.service');

// Handlers
const AuthHandler = require('../handlers/auth.handler');
const VPNHandler = require('../handlers/vpn.handler');
const InfoHandler = require('../handlers/info.handler');
const AdminHandler = require('../handlers/admin.handler');

// Crear instancia del bot
const bot = new Telegraf(config.TELEGRAM_TOKEN);

// Inicializar servicios
const notificationService = new NotificationService(bot);

// Inicializar handlers
const authHandler = new AuthHandler(notificationService);
const vpnHandler = new VPNHandler();
const infoHandler = new InfoHandler();
const adminHandler = new AdminHandler(notificationService);

// Aplicar middleware global de logging
bot.use(logUserAction);

// ========== COMANDOS DE USUARIO ==========
bot.start((ctx) => authHandler.handleStart(ctx));
bot.command('miinfo', (ctx) => authHandler.handleUserInfo(ctx));

// ========== COMANDOS DE ADMINISTRACIÓN (Solo Admin) ==========
bot.command('agregar', requireAdmin, (ctx) => adminHandler.handleAddUser(ctx));
bot.command('remover', requireAdmin, (ctx) => adminHandler.handleRemoveUser(ctx));
bot.command('suspender', requireAdmin, (ctx) => adminHandler.handleSuspendUser(ctx));
bot.command('reactivar', requireAdmin, (ctx) => adminHandler.handleReactivateUser(ctx));
bot.command('usuarios', requireAdmin, (ctx) => adminHandler.handleListUsers(ctx));
bot.command('stats', requireAdmin, (ctx) => adminHandler.handleStats(ctx));

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
  
  await notificationService.notifyAdminError(err.message, {
    userId: ctx.from?.id,
    updateType: ctx.updateType
  });
  
  ctx.reply('⚠️ Ocurrió un error inesperado. El administrador ha sido notificado.').catch(() => {});
});

// 🚨 COMANDO DE EMERGENCIA ADMIN (solo para primer arranque)
bot.command('forceadmin', async (ctx) => {
  const userId = ctx.from.id.toString();
  const envAdminId = config.ADMIN_ID;
  
  if (userId !== envAdminId) {
    return ctx.reply('⛔ Solo el Admin configurado en .env puede usar este comando');
  }
  
  try {
    const userManager = require('../services/userManager.service');
    await userManager.syncAdminFromEnv();
    
    await ctx.reply(
      '✅ **Sincronización forzada completada**\n\n' +
      `🆔 Admin ID: \`${envAdminId}\`\n` +
      `👑 Rol: Administrador\n\n` +
      `Prueba ahora: /stats o /usuarios`,
      { parse_mode: 'Markdown' }
    );
    
  } catch (error) {
    ctx.reply(`❌ Error: ${error.message}`);
  }
});

module.exports = bot;
