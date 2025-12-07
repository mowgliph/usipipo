'use strict';

const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');
const path = require('path');

/**
 * Logger empresarial para uSipipo VPN Bot
 * - Sanitización avanzada (tokens, IPs reales, claves)
 * - JSON estructurado
 * - Rotación diaria
 * - Context-aware logging
 */
class Logger {
  #patterns;
  #logger;

  constructor() {
    this.#patterns = this.#compileSensitivePatterns();
    this.#logger = winston.createLogger(this.#getLoggerConfig());
    this.#attachConsoleTransportIfNeeded();
  }

  // ===========================================================
  // 🔒 REGEX SANITIZACIÓN — V.2 (Optimizado y más seguro)
  // ===========================================================
  #compileSensitivePatterns() {
    return {
      tokens: [
        /telegram_token\s*[:=]\s*["']?[\w\-:\/\.]+/gi,
        /bot[_-]?token\s*[:=]\s*["']?[\w\-:\/\.]+/gi,
      ],
      keys: [
        /(private_key|public_key|outline.*key|wireguard.*key)\s*[:=]\s*["']?[\w\+=\/]+/gi
      ],
      ips: [
        // IP pública o privada completa
        /\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\b/g
      ]
    };
  }

  #sanitizeString(value) {
    if (typeof value !== 'string') return value;

    let sanitized = value;

    // Sanitización fuerte por categoría
    Object.values(this.#patterns).forEach(patternList => {
      patternList.forEach(pattern => {
        sanitized = sanitized.replace(pattern, '[SANITIZED]');
      });
    });

    return sanitized;
  }

  #sanitizeObject(data) {
    if (!data || typeof data !== 'object') return data;

    const clean = {};
    for (const key of Object.keys(data)) {
      const value = data[key];

      if (typeof value === 'string') clean[key] = this.#sanitizeString(value);
      else if (typeof value === 'object') clean[key] = this.#sanitizeObject(value);
      else clean[key] = value;
    }

    return clean;
  }

  #sanitizeFormat() {
    return winston.format(info => {
      info.message = this.#sanitizeString(info.message);
      const extra = { ...info };
      delete extra.message;
      delete extra.level;
      delete extra.timestamp;

      Object.assign(info, this.#sanitizeObject(extra));
      return info;
    })();
  }

  // ===========================================================
  // ⚙️ CONFIG WINSTON
  // ===========================================================
  #getLoggerConfig() {
    const logLevel = process.env.LOG_LEVEL || 'info';

    return {
      level: logLevel,
      format: winston.format.combine(
        winston.format.timestamp(),
        this.#sanitizeFormat(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      ),
      defaultMeta: {
        service: 'uSipipoVPNBot',
        env: process.env.NODE_ENV || 'development',
        pid: process.pid
      },
      transports: [
        new DailyRotateFile({
          filename: path.join('logs', 'app-%DATE%.log'),
          datePattern: 'YYYY-MM-DD',
          zippedArchive: true,
          maxSize: '20m',
          maxFiles: '30d'
        }),
        new DailyRotateFile({
          filename: path.join('logs', 'error-%DATE%.log'),
          level: 'error',
          datePattern: 'YYYY-MM-DD',
          zippedArchive: true,
          maxSize: '20m',
          maxFiles: '30d'
        })
      ]
    };
  }

  #attachConsoleTransportIfNeeded() {
    if (process.env.NODE_ENV !== 'production') {
      this.#logger.add(
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.printf(
              ({ level, message, timestamp }) =>
                `${timestamp} ${level}: ${message}`
            )
          )
        })
      );
    }
  }

  // ===========================================================
  // 🟦 PUBLIC LOGGING API (con contexto automático)
  // ===========================================================

  info(method, meta = {}) {
    this.#logger.info(method, meta);
  }

  warn(method, meta = {}) {
    this.#logger.warn(method, meta);
  }

  error(method, error, meta = {}) {
    this.#logger.error(method, {
      error: error?.message || String(error),
      stack: error?.stack,
      ...meta
    });
  }

  success(method, meta = {}) {
    this.#logger.info(`SUCCESS: ${method}`, meta);
  }

  debug(method, meta = {}) {
    this.#logger.debug(method, meta);
  }

  verbose(method, meta = {}) {
    this.#logger.verbose(method, meta);
  }

  http(method, url, status, ms, meta = {}) {
    this.#logger.http('HTTP', {
      method,
      url: this.#sanitizeString(url),
      status,
      duration: ms,
      ...meta
    });
  }
}

module.exports = new Logger();