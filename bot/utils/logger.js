// utils/logger.js
'use strict';

const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');
const path = require('path');
const config = require('../config/environment');

/**
 * Logger profesional con Winston para uSipipo VPN Bot
 * - Rotación diaria de logs (30 días)
 * - Formato JSON estructurado
 * - 7 niveles: error, warn, info, http, verbose, debug, silly
 * - Sanitización de datos sensibles (tokens, IPs privadas, etc.)
 * - Integración directa con AdminHandler existente
 */
class Logger {
  constructor() {
    this.logger = winston.createLogger(this.#getLoggerConfig());
    this.#setupConsoleTransport();
  }

  /**
   * Configuración principal del logger
   */
  #getLoggerConfig() {
    const logLevel = process.env.LOG_LEVEL || 'info';

    return {
      level: logLevel,
      format: this.#getLogFormat(),
      defaultMeta: {
        service: 'uSipipoVPNBot',
        env: process.env.NODE_ENV || 'development',
        version: '2.0.0'
      },
      transports: [
        // Archivo principal (todos los niveles)
        new DailyRotateFile({
          filename: path.join('logs', 'app-%DATE%.log'),
          datePattern: 'YYYY-MM-DD',
          zippedArchive: true,
          maxSize: '20m',
          maxFiles: '30d',
          level: logLevel
        }),
        // Errores críticos en archivo separado
        new DailyRotateFile({
          filename: path.join('logs', 'errors-%DATE%.log'),
          datePattern: 'YYYY-MM-DD',
          zippedArchive: true,
          maxSize: '20m',
          maxFiles: '30d',
          level: 'error'
        })
      ]
    };
  }

  /**
   * Formato estructurado JSON con timestamp y sanitización
   */
  #getLogFormat() {
    return winston.format.combine(
      winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
      this.#sanitizeSensitiveData(),
      winston.format.errors({ stack: true }),
      winston.format.json()
    );
  }

  /**
   * Sanitiza datos sensibles antes de loggear
   */
  #sanitizeSensitiveData() {
    const sensitivePatterns = [
      /telegram_token[:s]*[^,s}]+/gi,
      /admin_id[:s]*[^,s}]+/gi,
      /\b(d{1,3}.){3}d{1,3}(/d{1,2})?\b/g,        // IPs públicas o con máscara
      /\b10.d{1,3}.d{1,3}.d{1,3}\b/g,             // IPs privadas 10.x.x.x
      /\b172.(1[6-9]|2d|3[01]).d{1,3}.d{1,3}\b/g, // IPs privadas 172.16–31
      /\b192.168.d{1,3}.d{1,3}\b/g,                // IPs privadas 192.168.x.x
      /(wireguard_|outline_)(private_)?key[:s]*[^,s}]+/gi // Claves privadas
    ];

    return winston.format((info) => {
      let message = info.message;

      if (typeof message === 'object') {
        message = JSON.stringify(message);
      }

      sensitivePatterns.forEach((pattern) => {
        message = message.replace(pattern, '[SANITIZED]');
      });

      info.message = message;
      return info;
    })();
  }

  /**
   * Transport de consola con colores para desarrollo
   */
  #setupConsoleTransport() {
    if (process.env.NODE_ENV !== 'production') {
      this.logger.add(
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.simple()
          )
        })
      );
    }
  }

  // ======================
  // MÉTODOS PÚBLICOS
  // ======================

  info(adminId, method, data = {}) {
    this.logger.info('Admin action', {
      adminId: adminId?.toString(),
      method,
      ...data
    });
  }

  success(adminId, action, target, data = {}) {
    this.logger.info('Admin success', {
      adminId: adminId?.toString(),
      action,
      target: target?.toString(),
      ...data
    });
  }

  error(method, error, context = {}) {
    this.logger.error('Error occurred', {
      method,
      error: error?.message || error,
      stack: error?.stack,
      ...context
    });
  }

  warn(message, context = {}) {
    this.logger.warn(message, context);
  }

  http(method, url, statusCode, duration, context = {}) {
    this.logger.http('HTTP request', {
      method,
      url,
      statusCode,
      duration,
      ...context
    });
  }

  verbose(message, context = {}) {
    this.logger.verbose(message, context);
  }

  debug(message, context = {}) {
    this.logger.debug(message, context);
  }

  silly(message, context = {}) {
    this.logger.silly(message, context);
  }

  // Alias de compatibilidad
  logInfo(adminId, method, data) {
    this.info(adminId, method, data);
  }

  logSuccess(adminId, action, target) {
    this.success(adminId, action, target);
  }

  logError(method, error, context) {
    this.error(method, error, context);
  }
}

// Singleton global
const logger = new Logger();
module.exports = logger;