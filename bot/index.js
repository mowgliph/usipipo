// ============================================================================
// 🛡️ uSipipo VPN Manager - Bot Bootstrap
// Punto de entrada principal del sistema
// ============================================================================

require('dotenv').config();

const { bot, notificationService } = require('./bot/bot.instance');
const config = require('./config/environment');

// System Jobs
const SystemJobsService = require('./services/systemJobs.service');

// ============================================================================
// 🟢 STARTUP HELPERS
// ============================================================================

/**
 * Construye la lista de comandos disponibles para usuarios y admins.
 */
const buildCommands = () => {
  const userCommands = [
    { command: 'start', description: '🏠 Menú Principal' },
    { command: 'miinfo', description: '👤 Ver mis datos e ID' },
    { command: 'status', description: '✅ Estado de acceso' },
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
    { command: 'broadcast', description: '📢 Enviar mensaje global' }
  ];

  return { userCommands, adminCommands };
};

/**
 * Establece comandos personalizados en Telegram.
 */
const configureTelegramCommands = async () => {
  const { userCommands, adminCommands } = buildCommands();

  await bot.telegram.setMyCommands(userCommands);

  if (config.ADMIN_ID) {
    await bot.telegram.setMyCommands(adminCommands, {
      scope: { type: 'chat', chat_id: config.ADMIN_ID }
    });
  }

  console.log('✅ Comandos de Telegram configurados correctamente');
};

/**
 * Envía notificación de arranque del sistema.
 */
const notifyStartup = async () => {
  try {
    await notificationService.notifyAdminsSystemStartup();
    console.log('📨 Notificación de arranque enviada al Admin');
  } catch (err) {
    console.error('⚠️ No se pudo enviar la notificación de arranque:', err.message);
  }
};

/**
 * Log profesional al iniciar.
 */
const logStartupInfo = () => {
  console.log('\n===================================================');
  console.log('🚀 uSipipo VPN Bot iniciado correctamente');
  console.log('===================================================');
  console.log(`👑 Admin ID:             ${config.ADMIN_ID || 'No definido'}`);
  console.log(`👥 Usuarios autorizados: ${config.AUTHORIZED_USERS.length}`);
  console.log(`🌍 Servidor IPv4:        ${config.SERVER_IPV4}`);
  console.log('===================================================\n');
};

// ============================================================================
// 🔵 LAUNCH BOT
// ============================================================================

(async () => {
  try {
    await bot.launch();

    logStartupInfo();
    await configureTelegramCommands();

    // Delay para evitar "Too Many Requests"
    setTimeout(notifyStartup, 1500);

    // ============================================================================
    // 🔄 Inicio de System Jobs (Quota Monitor + Enforcement)
    // ============================================================================
    const systemJobs = new SystemJobsService(notificationService);

    try {
      await systemJobs.initialize();
      console.log('🔁 SystemJobs inicializado (monitoreo de cuotas activo)');
    } catch (err) {
      console.error('❌ Error inicializando SystemJobs:', err.message);
      await notificationService.notifyAdminError(
        'Fallo inicializando SystemJobs',
        { error: err.message }
      );
    }

  } catch (error) {
    console.error('❌ Error crítico al iniciar el bot:', error);
    process.exit(1);
  }
})();

// ============================================================================
// 🔴 SHUTDOWN & FATAL ERROR HANDLERS
// ============================================================================

/**
 * Manejo elegante de apagado.
 */
const shutdownHandler = (signal) => {
  console.log(`\n📴 Señal recibida (${signal}). Cerrando bot de forma segura...`);
  try {
    bot.stop(signal);
  } catch (e) {
    console.error('⚠️ Error al detener el bot:', e);
  }
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