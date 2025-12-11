'use strict';

/**
 * ============================================================================
 * 🚀 MAIN ENTRY POINT — uSipipo VPN Bot
 * ============================================================================
 * Este archivo inicia toda la aplicación.
 * Se encarga de:
 *   - Cargar variables de entorno
 *   - Inicializar el bot mediante initBot()
 *   - Ejecutar modo Polling o Webhook según configuración
 *   - Manejar señales de apagado del sistema
 * ============================================================================
 */

require('dotenv').config();

const env = require('./config/environment');
const logger = require('./core/utils/logger');
const { bot, initBot } = require('./core/bot/bot.instance');

async function start() {
  try {
    // Inicializar bot (middlewares, servicios, handlers)
    await initBot();

    // Modo webhook activado
    if (env.BOT_WEBHOOK_ENABLED === true || env.BOT_WEBHOOK_ENABLED === 'true') {
      logger.info('⚡ Iniciando bot en modo Webhook...');

      await bot.launch({
        webhook: {
          domain: env.BOT_WEBHOOK_URL,
          port: env.BOT_WEBHOOK_PORT || 3001
        }
      });

      logger.success(`🚀 Webhook activo en: ${env.BOT_WEBHOOK_URL}`);

    } else {
      // Modo polling
      logger.info('⚡ Iniciando bot en modo Long Polling...');

      await bot.launch();
      logger.success('🤖 Bot iniciado correctamente en modo Polling');
    }

    // Manejo elegante de apagado
    process.once('SIGINT', () => {
      logger.warn('⛔ Cierre recibido (SIGINT). Deteniendo bot...');
      bot.stop('SIGINT');
    });

    process.once('SIGTERM', () => {
      logger.warn('⛔ Cierre recibido (SIGTERM). Deteniendo bot...');
      bot.stop('SIGTERM');
    });

  } catch (error) {
    logger.error('❌ ERROR FATAL al iniciar la aplicación', error);
    process.exit(1);
  }
}

start();