require('dotenv').config();
const fs = require('fs');

const { Telegraf, Markup } = require('telegraf');
const WireGuardService = require('./services/wireguard');
const OutlineService = require('./services/outline');

// Check for required environment variables
const requiredEnvVars = [
  'TELEGRAM_TOKEN',
  'AUTHORIZED_USERS',
  'SERVER_IPV4',
  'PIHOLE_WEBPASS',
  'WIREGUARD_PORT',
  'OUTLINE_API_PORT'
];

for (const varName of requiredEnvVars) {
  if (!process.env[varName]) {
    console.error(`❌ Error: Missing required environment variable: ${varName}`);
    console.error('Please ensure all required variables are set in your .env file.');
    process.exit(1);
  }
}

// Inicializar bot
const bot = new Telegraf(process.env.TELEGRAM_TOKEN);

// Middleware de autorización
const authorizedUsers = process.env.AUTHORIZED_USERS.split(',').map(id => id.trim());
bot.use((ctx, next) => {
  if (!authorizedUsers.includes(ctx.from.id.toString())) {
    ctx.reply('⛔ No tienes acceso a este bot. Contacta al administrador.');
    return;
  }
  return next();
});

// Comando /start
bot.start((ctx) => {
  ctx.reply('¡Hola! Selecciona el tipo de VPN que necesitas:', 
    Markup.inlineKeyboard([
      Markup.button.callback('🔐 WireGuard', 'wg'),
      Markup.button.callback('🌐 Outline', 'outline')
    ])
  );
});

// Manejadores de callbacks
bot.action('wg', async (ctx) => {
  try {
    await ctx.answerCbQuery('Generando configuración WireGuard...');
    ctx.reply('⏳ Creando tu conexión WireGuard...');
    
    const { config, qr } = await WireGuardService.createNewClient();
    
    // Enviar archivo de configuración
    await ctx.replyWithDocument(
      { source: Buffer.from(config), filename: 'client.conf' },
      { caption: '✅ ¡Configuración generada! Usa este archivo en tu cliente WireGuard.' }
    );
    
    // Enviar QR para móviles
    await ctx.reply(`📱 QR para conexión rápida:\n\`\`\`\n${qr}\n\`\`\``, {
      parse_mode: 'Markdown',
      reply_markup: { remove_keyboard: true }
    });
    
  } catch (error) {
    console.error('WG Error:', error);
    ctx.reply('❌ Error al generar WireGuard. Contacta al administrador.');
  }
});

bot.action('outline', async (ctx) => {
  try {
    await ctx.answerCbQuery('Generando enlace Outline...');
    ctx.reply('⏳ Creando tu clave de acceso Outline...');
    
    const accessKey = await OutlineService.createAccessKey();
    
    await ctx.reply(
      `✅ ¡Clave de acceso generada!\n\n` +
      `🔗 Copia y pega este enlace en tu cliente Outline:\n\`\`\`\n${accessKey.accessUrl}\n\`\`\`\n\n` +
      `ℹ️ Este enlace incluye configuración DNS para bloquear anuncios.`,
      { parse_mode: 'Markdown' }
    );
  } catch (error) {
    console.error('Outline Error:', error);
    ctx.reply('❌ Error al generar Outline. Contacta al administrador.');
  }
});

// Manejo de errores global
bot.catch((err, ctx) => {
  console.error(`Error en bot para ${ctx.from.id}:`, err);
  ctx.reply('⚠️ Ocurrió un error inesperado. Intenta nuevamente más tarde.');
});

// Iniciar bot
bot.launch();
console.log('🚀 Bot de Telegram iniciado');

// Graceful shutdown
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
