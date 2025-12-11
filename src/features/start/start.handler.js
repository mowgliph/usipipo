'use strict';

/**
 * ============================================================================
 * 🚀 START HANDLER - uSipipo VPN Bot
 * ============================================================================
 * Manejador del comando /start
 * Coordina mensajes, servicio y respuesta al usuario
 * ============================================================================
 */

const { Composer } = require('telegraf');
const StartService = require('./start.service');
const startMessages = require('./start.messages');
const startKeyboard = require('./start.keyboard');
const commonMessages = require('../../shared/messages/common.messages');
const commonKeyboard = require('../../shared/keyboard/common.keyboard');
const logger = require('../../core/utils/logger');

// Middleware de autenticación (opcional para /start)
// El comando /start debe estar disponible para todos
const startHandler = new Composer();

/**
 * Comando /start - Punto de entrada principal
 */
startHandler.start(async (ctx) => {
  const startTime = Date.now();
  const userId = String(ctx.from.id);
  const userName = ctx.from.first_name || 'Usuario';
  
  logger.info('[StartHandler] Comando /start recibido', {
    userId,
    userName,
    username: ctx.from.username
  });

  try {
    // Inicializar servicios
    const startService = new StartService();
    
    // Procesar comando /start
    const result = await startService.processStartCommand(ctx.from, ctx.telegram);
    
    // Determinar mensaje basado en el resultado
    let message;
    let keyboard;

    switch (result.type) {
      case 'welcome_back':
      case 'welcome_authorized':
        if (result.isAdmin) {
          message = startMessages.WELCOME_ADMIN({
            userName: ctx.from.first_name || result.userData.name,
            userId
          });
          keyboard = commonKeyboard.getAdminMainMenuKeyboard();
        } else {
          message = startMessages.WELCOME_AUTHORIZED({
            userName: ctx.from.first_name || result.userData.name,
            userId,
            isAdmin: result.isAdmin
          });
          keyboard = commonKeyboard.getMainMenuKeyboard();
        }
        break;

      case 'request_sent':
        message = startMessages.WELCOME_UNAUTHORIZED({
          userName,
          userId
        });
        // Cambiar teclado para usuarios no autorizados
        keyboard = startKeyboard.getUnauthorizedKeyboard();
        break;

      case 'registration_error':
        message = startMessages.REGISTRATION_ERROR({
          error: result.data?.error || 'Error desconocido'
        });
        keyboard = startKeyboard.getErrorKeyboard();
        break;

      default:
        message = commonMessages.UNKNOWN_ERROR();
        keyboard = startKeyboard.getErrorKeyboard();
        break;
    }
    
    // Agregar footer común
    message += startMessages.START_FOOTER();
    
    // Enviar respuesta
    await ctx.replyWithMarkdown(message, {
      reply_markup: keyboard,
      disable_web_page_preview: true
    });
    
    // Si fue una solicitud enviada, mostrar mensaje adicional
    if (result.type === 'request_sent') {
      await ctx.replyWithMarkdown(
        startMessages.REQUEST_SENT_TO_ADMIN(),
        { disable_web_page_preview: true }
      );
    }
    
    const duration = Date.now() - startTime;
    logger.success('[StartHandler] Comando /start procesado exitosamente', {
      userId,
      duration: `${duration}ms`,
      resultType: result.type
    });
    
  } catch (error) {
    logger.error('[StartHandler] Error procesando comando /start', {
      userId,
      error: error.message,
      stack: error.stack
    });
    
    // Enviar mensaje de error al usuario
    await ctx.replyWithMarkdown(
      startMessages.REGISTRATION_ERROR({ error: error.message }),
      {
        reply_markup: startKeyboard.getErrorKeyboard(),
        disable_web_page_preview: true
      }
    );
  }
});

/**
 * Comando /retry - Para reintentar el inicio
 */
startHandler.command('retry', async (ctx) => {
  const userId = String(ctx.from.id);
  
  logger.info('[StartHandler] Comando /retry recibido', { userId });
  
  try {
    await ctx.replyWithMarkdown(
      startMessages.RETRY_MESSAGE(),
      {
        reply_markup: commonKeyboard.getMainMenuKeyboard(),
        disable_web_page_preview: true
      }
    );
    
  } catch (error) {
    logger.error('[StartHandler] Error procesando /retry', {
      userId,
      error: error.message
    });
    
    await ctx.replyWithMarkdown(
      commonMessages.UNKNOWN_ERROR(),
      { disable_web_page_preview: true }
    );
  }
});

/**
 * Acción para botón "Inicio"
 */
startHandler.action('start', async (ctx) => {
  const userId = String(ctx.from.id);
  
  logger.debug('[StartHandler] Acción start recibida', { userId });
  
  try {
    // Editar mensaje existente o enviar nuevo
    if (ctx.callbackQuery?.message?.message_id) {
      await ctx.editMessageText(
        startMessages.WELCOME_AUTHORIZED({
          userName: ctx.from.first_name || 'Usuario',
          userId,
          isAdmin: false // Esto debería verificarse en una implementación real
        }) + startMessages.START_FOOTER(),
        {
          parse_mode: 'Markdown',
          reply_markup: commonKeyboard.getMainMenuKeyboard(),
          disable_web_page_preview: true
        }
      );
    } else {
      await ctx.replyWithMarkdown(
        startMessages.WELCOME_AUTHORIZED({
          userName: ctx.from.first_name || 'Usuario',
          userId,
          isAdmin: false
        }) + startMessages.START_FOOTER(),
        {
          reply_markup: commonKeyboard.getMainMenuKeyboard(),
          disable_web_page_preview: true
        }
      );
    }
    
    await ctx.answerCbQuery();
    
  } catch (error) {
    logger.error('[StartHandler] Error en acción start', {
      userId,
      error: error.message
    });
    
    await ctx.answerCbQuery('❌ Error cargando inicio');
  }
});

/**
 * Middleware para manejar mensajes de texto que podrían ser intentos de /start
 */
startHandler.on('text', async (ctx, next) => {
  const messageText = ctx.message.text || '';
  
  // Detectar variantes de /start
  if (messageText.match(/^(start|inicio|comenzar|empezar)$/i)) {
    const userId = String(ctx.from.id);
    
    logger.debug('[StartHandler] Variante de start detectada en texto', {
      userId,
      text: messageText
    });
    
    // Responder con instrucciones
    await ctx.replyWithMarkdown(
      `⚠️ *Comando detectado*\n\n` +
      `Parece que intentaste usar el comando "${messageText}".\n\n` +
      `Por favor, usa ${startMessages.START_BUTTON} en el menú o escribe ${commonMessages.CODE('/start')} directamente.`,
      {
        reply_markup: commonKeyboard.getMainMenuKeyboard(false),
        disable_web_page_preview: true
      }
    );
    
    return;
  }
  
  // Pasar al siguiente middleware si no es un comando start
  return next();
});

/**
 * Middleware para logging de nuevos usuarios
 */
startHandler.use(async (ctx, next) => {
  // Solo aplicar a mensajes de chat privado
  if (ctx.chat?.type === 'private') {
    const userId = String(ctx.from.id);
    
    // Registrar información del usuario (solo una vez por sesión)
    if (!ctx.session?.userLogged) {
      logger.info('[StartHandler] Nuevo usuario detectado', {
        userId,
        userName: ctx.from.first_name,
        username: ctx.from.username,
        chatId: ctx.chat.id
      });
      
      if (!ctx.session) ctx.session = {};
      ctx.session.userLogged = true;
    }
  }
  
  return next();
});

/**
 * Helper para verificar estado de usuario
 */
startHandler.help(async (ctx) => {
  const userId = String(ctx.from.id);
  const user = await managerService.getAuthUser(userId);
  
  let statusMessage;
  if (user) {
    statusMessage = `✅ *Estás registrado*\n\n` +
                   `Nombre: ${user.name || 'No especificado'}\n` +
                   `Rol: ${user.role === 'admin' ? '👑 Administrador' : '👤 Usuario'}\n` +
                   `Estado: ${user.status === 'active' ? '✅ Activo' : '⏳ Pendiente'}`;
  } else {
    statusMessage = `❌ *No estás registrado*\n\n` +
                   `Usa el comando ${commonMessages.CODE('/start')} para registrarte.`;
  }
  
  await ctx.replyWithMarkdown(statusMessage);
});

module.exports = startHandler;
