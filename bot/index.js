// index.js

require('dotenv').config();

const { bot, notificationService } = require('./bot/bot.instance');
const config = require('./config/environment');

// ===============================================================
// 🟢 STARTUP FUNCTIONS
// ===============================================================

// Construcción de comandos
const buildCommands = () => {
  const userCommands = [
    { command: 'start', description: '🏠 Menú Principal' },
    { command: 'miinfo', description: '👤 Ver mis datos e ID' },
    { command: 'status', description: '✅ Comprobar estado de acceso' },
    { command: 'commands', description: '📋 Lista de comandos' },
    { command: 'help', description: '❓ Ayuda y soporte' }
  ];

  const adminCommands = [
    ...userCommands,
    { command: 'users', description: '👥 Listar usuarios' },
    { command: 'add', description: '➕ Autorizar usuario (uso: /add ID Nombre)' },
    { command: 'rm', description: '➖ Remover usuario (uso: /rm ID)' },
    { command: 'sus', description: '⏸️ Suspender usuario' },
    { command: 'react', description: '▶️ Reactivar usuario' },
    { command: 'stats', description: '📊 Estadísticas del servidor' },
    { command: 'broadcast', description: '📢 Enviar mensaje a todos' }
  ];

  return { userCommands, adminCommands };
};

// Establecer comandos en Telegram
const configureTelegramCommands = async () => {
  const { userCommands, adminCommands } = buildCommands();

  await bot.telegram.setMyCommands(userCommands);

  // Comandos exclusivos para Admin en su chat privado
  if (config.ADMIN_ID) {
    await bot.telegram.setMyCommands(adminCommands, {
      scope: { type: 'chat', chat_id: config.ADMIN_ID }
    });
  }

  console.log('✅ Comandos de Telegram configurados');
};

// Notificación de arranque
const notifyStartup = async () => {
  try {
    await notificationService.notifyAdminsSystemStartup();
    console.log('📨 Notificación de arranque enviada al Admin');
  } catch (err) {
    console.error('⚠️ No se pudo enviar la notificación de arranque:', err.message);
  }
};

// Mostrar información de entorno
const logStartupInfo = () => {
  console.log('🚀 uSipipo VPN Bot iniciado');
  console.log(`📡 Admin ID: ${config.ADMIN_ID || 'no definido'}`);
  console.log(`👥 Usuarios autorizados: ${(config.AUTHORIZED_USERS || []).length}`);
  console.log(`🌍 Servidor IPv4: ${config.SERVER_IPV4}`);
};

// ===============================================================
// 🔵 LAUNCH BOT
// ===============================================================

(async () => {
  try {
    await bot.launch();

    logStartupInfo();
    await configureTelegramCommands();

    // Delay para evitar "Too Many Requests" al iniciar
    setTimeout(notifyStartup, 2000);

  } catch (error) {
    console.error('❌ Error al iniciar el bot:', error);
    process.exit(1);
  }
})();

// ===============================================================
// 🔴 SHUTDOWN & FATAL ERRORS
// ===============================================================

const shutdownHandler = (signal) => {
  console.log(`\n📴 Señal recibida (${signal}). Cerrando bot...`);
  bot.stop(signal);
  process.exit(0);
};

process.once('SIGINT', () => shutdownHandler('SIGINT'));
process.once('SIGTERM', () => shutdownHandler('SIGTERM'));

process.on('unhandledRejection', (reason) => {
  console.error('❌ Unhandled Rejection:', reason);
});

process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
  process.exit(1);
});