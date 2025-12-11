'use strict';

const path = require('path');

module.exports = {
  apps: [
    {
      name: 'usipipo',
      script: path.join(__dirname, 'src/index.js'),

      // === INSTANCIAS ===
      instances: 1,               // Telegraf no permite modo cluster
      exec_mode: 'fork',          // Evitar errores por instancias paralelas

      // === ERRORES Y ESTABILIDAD ===
      autorestart: true,
      max_restarts: 10,           // Evita bucles infinitos si el bot arranca mal
      restart_delay: 2000,        // Pausa entre intentos de reinicio
      max_memory_restart: '500M', // RAM máxima antes de reiniciar

      // === WATCH (desactivado en producción) ===
      watch: false,

      // === LOGS ===
      error_file: path.join(__dirname, 'logs', 'pm2-error.log'),
      out_file: path.join(__dirname, 'logs', 'pm2-out.log'),
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      time: true,                 // Timestamp en los logs

      // === VARIABLES DE ENTORNO ===
      env: {
        NODE_ENV: 'production',

        // Control de Webhook vs Polling
        BOT_WEBHOOK_ENABLED: process.env.BOT_WEBHOOK_ENABLED || false,
        BOT_WEBHOOK_URL: process.env.BOT_WEBHOOK_URL || '',
        BOT_WEBHOOK_PORT: process.env.BOT_WEBHOOK_PORT || 3001,

        TELEGRAM_TOKEN: process.env.TELEGRAM_TOKEN,

        // Configuración general del bot
        ADMIN_ID: process.env.ADMIN_ID,
        SERVER_IP: process.env.SERVER_IP,
        AUTHORIZED_USERS: process.env.AUTHORIZED_USERS || '',
      },

      // === HEALTHCHECK PM2 ===
      // Esto permite verificar si el bot está vivo
      pm2 trigger usipipo health
      listen_timeout: 8000,
      kill_timeout: 8000,
    }
  ]
};