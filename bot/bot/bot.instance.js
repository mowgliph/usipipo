// bot/bot.instance.js
const { Telegraf } = require('telegraf');
const config = require('../config/environment');
const { requireAuth, requireAdmin, logUserAction, isAdmin } = require('../middleware/auth.middleware'); 

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
bot.command('status', (ctx) => authHandler.handleCheckStatus(ctx));
bot.command('help', (ctx) => authHandler.handleHelp(ctx))
bot.command('commands', (ctx) => infoHandler.handleCommandList(ctx)); 

// ========== COMANDOS DE ADMINISTRACIÓN (Solo Admin) ==========
bot.command('add', requireAdmin, (ctx) => adminHandler.handleAddUser(ctx));
bot.command('rm', requireAdmin, (ctx) => adminHandler.handleRemoveUser(ctx));
bot.command('sus', requireAdmin, (ctx) => adminHandler.handleSuspendUser(ctx));
bot.command('react', requireAdmin, (ctx) => adminHandler.handleReactivateUser(ctx));
bot.command('users', requireAdmin, (ctx) => adminHandler.handleListUsers(ctx));
bot.command('stats', requireAdmin, (ctx) => adminHandler.handleStats(ctx));

// ========== NUEVOS COMANDOS DE BROADCAST (Solo Admin) ==========
bot.command('broadcast', requireAdmin, (ctx) => adminHandler.handleBroadcast(ctx));
bot.command('sms', requireAdmin, (ctx) => adminHandler.handleDirectMessage(ctx));
bot.command('templates', requireAdmin, (ctx) => adminHandler.handleTemplates(ctx));

// ========== ACCIONES DE AUTENTICACIÓN ==========
bot.action('show_my_info', (ctx) => authHandler.handleUserInfo(ctx));
bot.action('request_access', (ctx) => authHandler.handleAccessRequest(ctx));
bot.action('check_status', (ctx) => authHandler.handleCheckStatus(ctx));

// ========== ACCIONES DE VPN (Requieren autorización) ==========
bot.action('create_wg', requireAuth, (ctx) => vpnHandler.handleCreateWireGuard(ctx));
bot.action('create_outline', requireAuth, (ctx) => vpnHandler.handleCreateOutline(ctx));
bot.action('list_clients', requireAuth, (ctx) => vpnHandler.handleListClients(ctx));

// ========== ACCIONES INFORMATIVAS ==========
bot.action('server_status', requireAuth, (ctx) => infoHandler.handleServerStatus(ctx));
bot.action('help', (ctx) => infoHandler.handleHelp(ctx));

// ========== ACCIONES DE BROADCAST (Solo Admin) ==========
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

// Handler genérico para mensajes de texto (comandos no reconocidos o texto libre)
bot.on('text', async (ctx) => {
    const userId = ctx.from?.id;
    const userName = ctx.from?.first_name || 'usuario';
    const messageText = ctx.message.text.trim();
    
    // Si el mensaje comienza con '/', se asume que es un comando no reconocido
    // ya que los comandos conocidos fueron manejados por bot.command()
    if (messageText.startsWith('/')) {
        // 1. Manejo de COMANDOS NO RECONOCIDOS
        
        // Comprobar si es administrador
        const isUserAdmin = isAdmin(userId); 
        
        await ctx.reply(messages.UNKNOWN_COMMAND(isUserAdmin), {
            parse_mode: 'Markdown'
        }).catch(err => {
            console.error(`Error al enviar mensaje de comando desconocido: ${err.message}`);
        });

    } else {
        // 2. Manejo de TEXTO GENÉRICO (no es un comando)
        
        // Saludo profesional y menú de selección de VPN
        await ctx.reply(messages.GENERIC_TEXT_PROMPT(userName), {
            parse_mode: 'Markdown',
            reply_markup: keyboards.vpnSelectionMenu().reply_markup // Usar el nuevo menú
        }).catch(err => {
            console.error(`Error al enviar mensaje de texto genérico: ${err.message}`);
        });
    }
});

module.exports = bot;
