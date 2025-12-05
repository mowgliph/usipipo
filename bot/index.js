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
  
  // 1. Definir comandos para USUARIOS NORMALES
  const userCommands = [
    { command: 'start', description: '🏠 Menú Principal' },
    { command: 'miinfo', description: '👤 Ver mis datos e ID' },
    { command: 'status', description: '✅ Comprobar estado de acceso' },
    { command: 'commands', description: '📋 Lista de comandos' },
    { command: 'help', description: '❓ Ayuda y soporte' }
  ];

  // 2. Definir comandos para ADMINISTRADOR (Incluye los de usuario + gestión)
  const adminCommands = [
    ...userCommands, // Hereda los comandos de usuario
    { command: 'users', description: '👥 Listar usuarios' },
    { command: 'add', description: '➕ Autorizar usuario (uso: /add ID Nombre)' },
    { command: 'rm', description: '➖ Remover usuario (uso: /rm ID)' },
    { command: 'sus', description: '⏸️ Suspender usuario' },
    { command: 'react', description: '▶️ Reactivar usuario' },
    { command: 'stats', description: '📊 Estadísticas del servidor' },
    { command: 'broadcast', description: '📢 Enviar mensaje a todos' }
  ];

  try {
    // A. Establecer comandos por defecto (para todos)
    await bot.telegram.setMyCommands(userCommands);

    // B. Establecer comandos específicos SOLO para el Admin
    // Esto hace que en tu chat privado veas las opciones extra
    await bot.telegram.setMyCommands(adminCommands, { 
      scope: { type: 'chat', chat_id: config.ADMIN_ID } 
    });
    
    console.log('✅ Menú de comandos actualizado en Telegram');
  } catch (error) {
    console.error('⚠️ Error al actualizar el menú de comandos:', error);
  }
  
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
