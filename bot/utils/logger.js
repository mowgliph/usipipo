// utils/logger.js
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
      /(d{1,3}.){3}d{1,3}(/d{1,2})?/g, // IPs públicas
      /10.d{1,3}.d{1,3}.d{1,3}/g,     // IPs privadas 10.x
      /172.(1[6-9]|2d|3[01]).d{1,3}.d{1,3}/g, // 172.16-31
      /192.168.d{1,3}.d{1,3}/g,         // 192.168
      /(wireguard_|outline_)(private_)?key[:s]*[^,s}]+/gi
    ];

    return winston.format((info) => {
      let message = info.message;
      
      if (typeof message === 'object') {
        message = JSON.stringify(message);
      }

      sensitivePatterns.forEach(pattern => {
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
      this.logger.add(new winston.transports.Console({
        format: winston.format.combine(
          winston.format.colorize(),
          winston.format.simple()
        )
      }));
    }
  }

  // ========== MÉTODOS PÚBLICOS (compatibles con AdminHandler) ==========

  /**
   * Log INFO estructurado (reemplaza console.log en AdminHandler)
   */
  info(adminId, method, data = {}) {
    this.logger.info(`Admin action`, {
      adminId: adminId.toString(),
      method,
      ...data
    });
  }

  /**
   * Log SUCCESS (alias de info con contexto específico)
   */
  success(adminId, action, target, data = {}) {
    this.logger.info(`Admin success`, {
      adminId: adminId.toString(),
      action,
      target: target?.toString(),
      ...data
    });
  }

  /**
   * Log ERROR con stack trace completo
   */
  error(method, error, context = {}) {
    this.logger.error(`Error occurred`, {
      method,
      error: error.message,
      stack: error.stack,
      ...context
    });
  }

  /**
   * Log WARN para advertencias no críticas
   */
  warn(message, context = {}) {
    this.logger.warn(message, context);
  }

  /**
   * Log HTTP requests/responses
   */
  http(method, url, statusCode, duration, context = {}) {
    this.logger.http(`HTTP request`, {
      method,
      url,
      statusCode,
      duration,
      ...context
    });
  }

  /**
   * Log VERBOSE para información detallada
   */
  verbose(message, context = {}) {
    this.logger.verbose(message, context);
  }

  /**
   * Log DEBUG para desarrollo
   */
  debug(message, context = {}) {
    this.logger.debug(message, context);
  }

  /**
   * Log SILLY para trazas muy detalladas
   */
  silly(message, context = {}) {
    this.logger.silly(message, context);
  }

  /**
   * Alias para compatibilidad con AdminHandler existente
   */
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

// Singleton instance
const logger = new Logger();
module.exports = logger;