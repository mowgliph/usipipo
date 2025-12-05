// index.js
require('dotenv').config();
const bot = require('./bot/bot.instance');
const config = require('./config/environment');

// Iniciar bot
bot.launch().then(() => {
  console.log('🚀 uSipipo VPN Bot iniciado exitosamente');
  console.log(`📡 Admin ID: ${config.ADMIN_ID}`);
  console.log(`👥 Usuarios autorizados: ${config.AUTHORIZED_USERS.length}`);
  console.log(`🌍 Servidor: ${config.SERVER_IPV4}`);
  
  // Esperar 2 segundos para asegurar que la conexión a Telegram esté estable
  setTimeout(() => {
    notificationService.notifyAdminsSystemStartup();
  }, 2000);
  
}).catch((error) => {
  console.error('❌ Error al iniciar el bot:', error);
  process.exit(1);
});

// Graceful shutdown
const shutdownHandler = (signal) => {
  console.log(`\n📴 Recibida señal ${signal}. Cerrando bot...`);
  bot.stop(signal);
  process.exit(0);
};

process.once('SIGINT', () => shutdownHandler('SIGINT'));
process.once('SIGTERM', () => shutdownHandler('SIGTERM'));

// Manejo de errores no capturados
process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection:', reason);
});

process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
  process.exit(1);
});
