const userManager = require('../services/userManager.service');
const messages = require('../utils/messages');
const logger = require('../utils/logger');

// ======================================================
// Helpers internos
// ======================================================

function getUserMeta(ctx) {
  const userId = ctx.from?.id;
  const username = ctx.from?.username ? `@${ctx.from.username}` : null;
  const firstName = ctx.from?.first_name || '';
  const lastName = ctx.from?.last_name || '';
  const fullName = (firstName + ' ' + lastName).trim() || username || `User${userId}`;

  return {
    userId,
    username,
    fullName,
    isAuthorized: userManager.isAuthorized(userId),
    isAdmin: userManager.isAdmin(userId)
  };
}

// ======================================================
// Middlewares principales
// ======================================================

async function requireAuth(ctx, next) {
  const meta = getUserMeta(ctx);

  try {
    if (!meta.isAuthorized) {
      logger.warn('Access denied (User is NOT authorized)', meta);
      await ctx.reply(messages.ACCESS_DENIED, { parse_mode: 'HTML' });
      return;
    }

    logger.debug('Authorized access', meta);
    return next();
  } catch (error) {
    logger.error('requireAuth', error, meta);
    await ctx.reply('⚠️ Error interno durante la verificación de acceso.');
  }
}

async function requireAdmin(ctx, next) {
  const meta = getUserMeta(ctx);

  try {
    if (!meta.isAdmin) {
      logger.warn('Admin access denied', meta);
      await ctx.reply(messages.ADMIN_ONLY, { parse_mode: 'HTML' });
      return;
    }

    logger.debug('Admin access granted', meta);
    return next();
  } catch (error) {
    logger.error('requireAdmin', error, meta);
    await ctx.reply('⚠️ Error interno al validar permisos de administrador.');
  }
}

/**
 * Logger universal de acciones del usuario.
 * Registra TODO: comandos, botones, textos, eventos...
 */
async function logUserAction(ctx, next) {
  const meta = getUserMeta(ctx);
  const actionType = ctx.updateType || 'unknown';
  const messageType = ctx.message?.text || ctx.callbackQuery?.data || null;

  logger.http(
    'UserAction',
    actionType,
    200,
    0,
    {
      ...meta,
      actionType,
      message: messageType
    }
  );

  return next();
}

// ======================================================
// Exports
// ======================================================

module.exports = {
  isAuthorized: (id) => userManager.isAuthorized(id),
  isAdmin: (id) => userManager.isAdmin(id),
  requireAuth,
  requireAdmin,
  logUserAction
};