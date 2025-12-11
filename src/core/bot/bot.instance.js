'use strict';

/**
 * src/core/bot/bot.instance.js
 *
 * Inicializa el bot de Telegram, registra middlewares, servicios y handlers
 * Detecta automáticamente todos los archivos *.handler.js dentro de src/features
 * e intenta instanciarlos y registrar sus handlers si exportan una clase u objeto
 * con método `registerHandlers`.
 *
 * Compatibilidad con el estilo CommonJS del proyecto.
 */

const { Telegraf } = require('telegraf');
const fs = require('fs');
const path = require('path');

const env = require('../../config/environment');
const logger = require('../utils/logger');

// Middlewares
const {
  loggingMiddleware,
  commandLoggingMiddleware,
  callbackLoggingMiddleware
} = require('../middleware/logging.middleware');

const { errorMiddleware, withErrorHandling } = require('../middleware/error.middleware');
const authMiddleware = require('../middleware/auth.middleware');

// Services (algunos services esperan la instancia del bot)
const NotificationService = require('../../shared/services/notification.service');
const managerService = require('../../shared/services/manager.service');
const SystemJobsService = require('../../shared/services/systemJobs.service');

// ---------- CREAR INSTANCIA DEL BOT ----------
const bot = new Telegraf(env.TELEGRAM_TOKEN || env.TELEGRAM_TOKEN);

// Exponer logger en context por conveniencia
bot.context.logger = logger;

// Contenedor para services accesible desde handlers: ctx.services.*
bot.context.services = {};

// ---------- REGISTRO DE MIDDLEWARES ----------
function registerCoreMiddlewares(instance) {
  // Logging general
  instance.use(async (ctx, next) => loggingMiddleware(ctx, next));

  // Command / Callback specific logging
  instance.use(commandLoggingMiddleware);
  instance.use(callbackLoggingMiddleware);

  // Attach helper middlewares (non-blocking)
  // logUserAction logs every request with user metadata
  if (authMiddleware && typeof authMiddleware.logUserAction === 'function') {
    instance.use(authMiddleware.logUserAction);
  }

  // Global error catcher for telegraf (will forward to our errorMiddleware)
  instance.catch(async (err, ctx) => {
    try {
      // errorMiddleware expects (error, ctx, next)
      await errorMiddleware(err, ctx, () => Promise.resolve());
    } catch (e) {
      // fallback: log
      logger.error('[Bot] Error dentro de errorMiddleware', e, { original: err?.message });
    }
  });

  logger.info('[Bot] Middlewares core registrados');
}

// ---------- INICIALIZAR SERVICIOS ----------
async function initServices(instance) {
  // NotificationService necesita la instancia del bot
  const notificationService = new NotificationService(instance);
  instance.context.services.notificationService = notificationService;

  // Manager service (ya viene como singleton o clase exportada)
  instance.context.services.managerService = managerService;

  // SystemJobs: pasar notificationService si el módulo lo requiere
  try {
    const sysJobs = new SystemJobsService(notificationService);
    instance.context.services.systemJobs = sysJobs;

    // Intentar inicializar system jobs, sin bloquear el arranque si falla.
    if (typeof sysJobs.initialize === 'function') {
      sysJobs.initialize().catch((err) => {
        logger.warn('[Bot] systemJobs.initialize falló (continuando)', { err: err?.message });
      });
    }
  } catch (err) {
    logger.warn('[Bot] No se pudo inicializar SystemJobsService', { err: err?.message });
  }

  logger.info('[Bot] Services inicializados');
}

// ---------- CARGA DINÁMICA DE HANDLERS (features) ----------
/**
 * Busca recursivamente archivos *.handler.js en src/features y los registra.
 */
function loadFeatureHandlers(instance) {
  const featuresDir = path.join(__dirname, '..', '..', 'features');

  function walkAndCollectHandlers(dir) {
    let results = [];
    const list = fs.readdirSync(dir);
    list.forEach((fileOrDir) => {
      const fullPath = path.join(dir, fileOrDir);
      const stat = fs.statSync(fullPath);
      if (stat && stat.isDirectory()) {
        results = results.concat(walkAndCollectHandlers(fullPath));
      } else if (stat && stat.isFile() && fileOrDir.endsWith('.handler.js')) {
        results.push(fullPath);
      }
    });
    return results;
  }

  let handlerFiles = [];
  try {
    handlerFiles = walkAndCollectHandlers(featuresDir);
  } catch (err) {
    logger.warn('[Bot] No se pudo leer directorio de features o no existe', { err: err?.message });
    return;
  }

  handlerFiles.forEach((hf) => {
    try {
      // require el handler
      const mod = require(hf);

      let instanceHandler = null;

      // Si exporta una clase/constructor -> new Class(bot)
      if (typeof mod === 'function') {
        try {
          instanceHandler = new mod(instance);
        } catch (e) {
          // Si falla al construir, quizás exporta una factory o es función util.
          // comprobamos si tiene export default
          if (mod.default && typeof mod.default === 'function') {
            instanceHandler = new mod.default(instance);
          }
        }
      } else if (mod && typeof mod.default === 'function') {
        instanceHandler = new mod.default(instance);
      } else if (mod && typeof mod.create === 'function') {
        instanceHandler = mod.create(instance);
      } else if (mod && typeof mod.registerHandlers === 'function') {
        // Si el módulo ya es un objeto con registerHandlers, lo usamos (algunos handlers no necesitan instancia)
        instanceHandler = mod;
      }

      if (instanceHandler && typeof instanceHandler.registerHandlers === 'function') {
        // envolver métodos expuestos con control de errores si no lo hacen internamente
        try {
          instanceHandler.registerHandlers();
          logger.success(`[Bot] Handler registrado -> ${path.relative(process.cwd(), hf)}`);
        } catch (err) {
          // si el handler define internamente try/catch, se usará; si no, registramos el error
          logger.error('[Bot] Error registrando handler', err, { handler: hf });
        }
      } else {
        logger.debug('[Bot] Archivo handler ignorado (no tiene registerHandlers export)', { file: hf });
      }
    } catch (err) {
      logger.error('[Bot] Error cargando handler', err, { file: hf });
    }
  });
}

// ---------- UTILIDADES (wrap handlers con manejo de errores) ----------
/**
 * Helper para aplicar withErrorHandling a funciones concretas cuando las registres manualmente.
 * Ej:
 *   bot.command('start', wrap(async (ctx) => { ... }))
 */
function wrap(fn) {
  if (!fn) return fn;
  try {
    return withErrorHandling(fn);
  } catch (e) {
    // fallback: devolver la función original
    return fn;
  }
}

// ---------- FUNCIÓN DE INICIALIZACIÓN PRINCIPAL ----------
/**
 * Inicializa todo y devuelve la instancia del bot lista para lanzar (launch).
 */
async function initBot() {
  try {
    // Middlewares core
    registerCoreMiddlewares(bot);

    // Inicializar servicios (notification, manager, systemJobs, etc)
    await initServices(bot);

    // Cargar handlers dinámicamente
    loadFeatureHandlers(bot);

    // Comandos básicos en bot.telegram (opcional)
    try {
      bot.telegram.setMyCommands([
        { command: 'start', description: 'Iniciar el bot' },
        { command: 'help', description: 'Ayuda' },
        { command: 'menu', description: 'Mostrar menú' }
      ]);
    } catch (e) {
      logger.debug('[Bot] setMyCommands falló (posible modo de test)', { err: e?.message });
    }

    logger.info('[Bot] Inicialización completa');
    return bot;
  } catch (err) {
    logger.error('[Bot] Error inicializando bot', err);
    throw err;
  }
}

// Exportamos la instancia y la función initBot
module.exports = {
  bot,
  initBot,
  wrap
};