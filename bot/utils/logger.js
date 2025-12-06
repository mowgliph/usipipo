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
 * - Sanitización robusta de datos sensibles
 * - 7 niveles de logging con métodos contextuales
 */
class Logger {
  #sensitivePatterns;
  #logger;

  constructor() {
    this.#sensitivePatterns = this.#getSensitivePatterns();
    this.#logger = winston.createLogger(this.#getLoggerConfig());
    this.#setupConsoleTransport();
  }

  /**
   * Patrones regex robustos para sanitización (IPv4 + claves)
   */
  #getSensitivePatterns() {
    return [
      /telegram_token[:s]*[^,s}]+/gi,
      /admin_id[:s]*[^,s}]+/gi,
      // IPs públicas con CIDR
      /\b(?:(?:25[0-5]|2[0-4]d|1d{2}|[1-9]?d).){3}(?:25[0-5]|2[0-4]d|1d{2}|[1-9]?d)(?:/d{1,2})?\b/g,
      // IPs privadas
      /\b10(?:.d{1,3}){3}\b/g,
      /\b172.(1[6-9]|2d|3[01])(?:.d{1,3}){2}\b/g,
      /\b192.168(?:.d{1,3}){2}\b/g,
      // Claves Wireguard/Outline
      /(wireguard_|outline_)(private_)?key[:s]*[^,s}]+/gi
    ];
  }

  #getLoggerConfig() {
    const logLevel = process.env.LOG_LEVEL || 'info';

    return {
      level: logLevel,
      format: this.#getLogFormat(),
      defaultMeta: {
        service: 'uSipipoVPNBot',
        env: process.env.NODE_ENV || 'development',
        version: '2.0.1', // Actualizado
        pid: process.pid
      },
      transports: [
        new DailyRotateFile({
          filename: path.join('logs', 'app-%DATE%.log'),
          datePattern: 'YYYY-MM-DD',
          zippedArchive: true,
          maxSize: '20m',
          maxFiles: '30d',
          level: logLevel
        }),
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

  #getLogFormat() {
    return winston.format.combine(
      winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
      this.#sanitizeSensitiveData(),
      winston.format.errors({ stack: true }),
      winston.format.json()
    );
  }

  #sanitizeSensitiveData() {
    return winston.format((info) => {
      const message = this.#sanitizeString(info.message);
      info.message = message;
      
      // Sanitiza también otros campos del objeto
      if (typeof info === 'object') {
        Object.keys(info).forEach(key => {
          if (typeof info[key] === 'string') {
            info[key] = this.#sanitizeString(info[key]);
          }
        });
      }
      
      return info;
    })();
  }

  #sanitizeString(str) {
    if (typeof str !== 'string') return str;
    
    let sanitized = str;
    this.#sensitivePatterns.forEach(pattern => {
      sanitized = sanitized.replace(pattern, '[SANITIZED]');
    });
    return sanitized;
  }

  #setupConsoleTransport() {
    if (process.env.NODE_ENV !== 'production') {
      this.#logger.add(
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
    this.#logger.info('Admin action', {
      adminId: adminId?.toString(),
      method,
      ...data
    });
  }

  success(adminId, action, target, data = {}) {
    this.#logger.info('Admin success', {
      adminId: adminId?.toString(),
      action,
      target: target?.toString(),
      ...data
    });
  }

  error(method, error, context = {}) {
    this.#logger.error('Error occurred', {
      method,
      error: error?.message || String(error),
      stack: error?.stack,
      ...context
    });
  }

  warn(message, context = {}) {
    this.#logger.warn(message, context);
  }

  http(method, url, statusCode, duration, context = {}) {
    this.#logger.http('HTTP request', {
      method,
      url: this.#sanitizeString(url),
      statusCode,
      duration,
      ...context
    });
  }

  verbose(message, context = {}) {
    this.#logger.verbose(message, context);
  }

  debug(message, context = {}) {
    this.#logger.debug(message, context);
  }

  silly(message, context = {}) {
    this.#logger.silly(message, context);
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