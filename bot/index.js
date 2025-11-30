// index.js
require('dotenv').config();
const { Telegraf, Markup } = require('telegraf');
const WireGuardService = require('./services/wireguard');
const OutlineService = require('./services/outline');

// Validación de variables de entorno
const requiredEnvVars = [
  'TELEGRAM_TOKEN',
  'AUTHORIZED_USERS',
  'SERVER_IPV4',
  'WIREGUARD_PORT',
  'OUTLINE_API_PORT',
  'WIREGUARD_SERVER_PUBLIC_KEY'
];

for (const varName of requiredEnvVars) {
  if (!process.env[varName]) {
    console.error(`❌ Missing required environment variable: ${varName}`);
    process.exit(1);
  }
}

const bot = new Telegraf(process.env.TELEGRAM_TOKEN);
const authorizedUsers = process.env.AUTHORIZED_USERS.split(',').map(id => id.trim());

// Middleware de autorización
bot.use((ctx, next) => {
  const userId = ctx.from?.id.toString();
  if (!authorizedUsers.includes(userId)) {
    ctx.reply('⛔ Acceso denegado. Contacta al administrador de uSipipo.');
    console.warn(`❌ Unauthorized access attempt from user ${userId}`);
    return;
  }
  return next();
});

// Comando /start con menú principal
bot.start((ctx) => {
  const userName = ctx.from.first_name || 'Usuario';
  ctx.reply(
    `👋 ¡Hola ${userName}! Bienvenido a **uSipipo VPN Manager**\n\n` +
    `Selecciona una opción del menú:`,
    {
      parse_mode: 'Markdown',
      ...Markup.inlineKeyboard([
        [Markup.button.callback('🔐 Crear WireGuard', 'create_wg')],
        [Markup.button.callback('🌐 Crear Outline', 'create_outline')],
        [Markup.button.callback('📊 Ver Clientes Activos', 'list_clients')],
        [Markup.button.callback('ℹ️ Estado del Servidor', 'server_status')],
        [Markup.button.callback('❓ Ayuda', 'help')]
      ])
    }
  );
});

// Crear cliente WireGuard
bot.action('create_wg', async (ctx) => {
  await ctx.answerCbQuery();
  await ctx.reply('⏳ Generando configuración WireGuard, por favor espera...');
  
  try {
    const { config, qr, clientIP } = await WireGuardService.createNewClient();
    
    // Enviar archivo de configuración
    await ctx.replyWithDocument(
      { 
        source: Buffer.from(config), 
        filename: `wireguard-${clientIP.replace(/\./g, '-')}.conf` 
      },
      { 
        caption: `✅ **Configuración WireGuard creada**\n\n` +
                 `📍 IP asignada: \`${clientIP}\`\n` +
                 `🔗 Endpoint: \`${process.env.SERVER_IPV4}:${process.env.WIREGUARD_PORT}\`\n\n` +
                 `📱 Usa el QR code a continuación para configuración rápida en móvil.`,
        parse_mode: 'Markdown'
      }
    );
    
    // Enviar QR code
    await ctx.reply(`\`\`\`\n${qr}\n\`\`\``, { parse_mode: 'Markdown' });
    
    await ctx.reply(
      '📖 **Instrucciones de conexión:**\n\n' +
      '**En móvil:** Abre WireGuard app → "+" → Escanear QR\n' +
      '**En PC:** Importa el archivo .conf en WireGuard client\n\n' +
      '🔗 Descargas: https://wireguard.com/install',
      { parse_mode: 'Markdown' }
    );
    
  } catch (error) {
    console.error('WireGuard creation error:', error);
    ctx.reply(`❌ Error al crear configuración WireGuard: ${error.message}`);
  }
});

// Crear clave Outline
bot.action('create_outline', async (ctx) => {
  await ctx.answerCbQuery();
  await ctx.reply('⏳ Generando clave de acceso Outline...');
  
  try {
    const userName = ctx.from.username || ctx.from.first_name;
    const accessKey = await OutlineService.createAccessKey(`TG-${userName}`);
    
    await ctx.reply(
      `✅ **Clave Outline creada exitosamente**\n\n` +
      `🔑 ID: \`${accessKey.id}\`\n` +
      `📱 Copia el siguiente enlace en tu app Outline:\n\n` +
      `\`\`\`\n${accessKey.accessUrl}\n\`\`\`\n\n` +
      `🛡️ DNS con bloqueo de anuncios activado\n` +
      `📊 Límite de datos: 10GB/mes\n\n` +
      `🔗 Descarga Outline: https://getoutline.org/get-started`,
      { parse_mode: 'Markdown' }
    );
    
  } catch (error) {
    console.error('Outline creation error:', error);
    ctx.reply(`❌ Error al crear clave Outline: ${error.message}`);
  }
});

// Listar clientes activos
bot.action('list_clients', async (ctx) => {
  await ctx.answerCbQuery();
  await ctx.reply('🔍 Consultando clientes activos...');
  
  try {
    const [wgClients, outlineKeys] = await Promise.all([
      WireGuardService.listClients(),
      OutlineService.listAccessKeys()
    ]);
    
    let message = '📊 **CLIENTES ACTIVOS**\n\n';
    
    message += `🔐 **WireGuard** (${wgClients.length} clientes)\n`;
    message += '━━━━━━━━━━━━━━━━━\n';
    wgClients.forEach((client, index) => {
      message += `${index + 1}. IP: \`${client.ip}\`\n`;
      message += `   📡 Última conexión: ${client.lastSeen}\n`;
      message += `   📥 Recibido: ${client.dataReceived}\n`;
      message += `   📤 Enviado: ${client.dataSent}\n\n`;
    });
    
    message += `\n🌐 **Outline** (${outlineKeys.length} claves)\n`;
    message += '━━━━━━━━━━━━━━━━━\n';
    outlineKeys.forEach((key, index) => {
      message += `${index + 1}. ID: \`${key.id}\` - ${key.name || 'Sin nombre'}\n`;
    });
    
    await ctx.reply(message, { parse_mode: 'Markdown' });
    
  } catch (error) {
    console.error('List clients error:', error);
    ctx.reply('❌ Error al obtener lista de clientes');
  }
});

// Estado del servidor
bot.action('server_status', async (ctx) => {
  await ctx.answerCbQuery();
  
  try {
    const outlineInfo = await OutlineService.getServerInfo();
    
    const message = 
      `🖥️ **ESTADO DEL SERVIDOR uSipipo**\n\n` +
      `📍 IP Pública: \`${process.env.SERVER_IPV4}\`\n` +
      `🔐 WireGuard Port: \`${process.env.WIREGUARD_PORT}\`\n` +
      `🌐 Outline Port: \`${process.env.OUTLINE_API_PORT}\`\n` +
      `🛡️ Pi-hole DNS: \`${process.env.PIHOLE_DNS || '10.2.0.100'}\`\n\n` +
      `✅ Todos los servicios operativos`;
    
    await ctx.reply(message, { parse_mode: 'Markdown' });
    
  } catch (error) {
    ctx.reply('⚠️ Algunos servicios podrían no estar respondiendo');
  }
});

// Ayuda
bot.action('help', (ctx) => {
  ctx.answerCbQuery();
  ctx.reply(
    `📚 **GUÍA DE USO - uSipipo VPN**\n\n` +
    `**WireGuard:**\n` +
    `• VPN de alto rendimiento\n` +
    `• Ideal para uso general\n` +
    `• Requiere app específica\n\n` +
    `**Outline:**\n` +
    `• Fácil configuración\n` +
    `• Mejor para móviles\n` +
    `• Un clic para conectar\n\n` +
    `**Pi-hole:**\n` +
    `• Bloqueo automático de ads\n` +
    `• Protección anti-tracking\n` +
    `• Integrado en ambas VPNs\n\n` +
    `💬 ¿Problemas? Contacta: usipipo@etlgr.com`,
    { parse_mode: 'Markdown' }
  );
});

// Manejo de errores
bot.catch((err, ctx) => {
  console.error(`❌ Bot error for user ${ctx.from?.id}:`, err);
  ctx.reply('⚠️ Ocurrió un error inesperado. Por favor intenta nuevamente.');
});

// Iniciar bot
bot.launch().then(() => {
  console.log('🚀 uSipipo VPN Bot started successfully');
  console.log(`📡 Authorized users: ${authorizedUsers.join(', ')}`);
});

// Graceful shutdown
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
