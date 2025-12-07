const userManager = require('../services/userManager.service');
const messages = require('../utils/messages');
const logger = require('../utils/logger');

function isAuthorized(userId) {
  return userManager.isAuthorized(userId);
}

function isAdmin(userId) {
  return userManager.isAdmin(userId);
}

async function requireAuth(ctx, next) {
  const userId = ctx.from?.id;
  const userName = ctx.from?.username || ctx.from?.first_name || `User${userId}`;

  try {
    if (!isAuthorized(userId)) {
      logger.warn('Access denied', { userId, userName });
      // CORREGIDO: HTML
      await ctx.reply(messages.ACCESS_DENIED, { parse_mode: 'HTML' });
      return;
    }

    logger.debug('Authorized access', { userId, userName });
    return next();
  } catch (error) {
    logger.error('requireAuth', error, { userId, userName });
    await ctx.reply('⚠️ Error de autorización interna.');
  }
}

async function requireAdmin(ctx, next) {
  const userId = ctx.from?.id;
  const userName = ctx.from?.username || ctx.from?.first_name || `User${userId}`;

  try {
    if (!isAdmin(userId)) {
      logger.warn('Admin access denied', { userId, userName });
      // CORREGIDO: HTML
      await ctx.reply(messages.ADMIN_ONLY, { parse_mode: 'HTML' });
      return;
    }

    logger.debug('Admin access granted', { userId, userName });
    return next();
  } catch (error) {
    logger.error('requireAdmin', error, { userId, userName });
    await ctx.reply('⚠️ Error al verificar permisos de administrador.');
  }
}

async function logUserAction(ctx, next) {
  const userId = ctx.from?.id;
  const firstName = ctx.from?.first_name || 'Unknown';
  const lastName = ctx.from?.last_name || '';
  const username = ctx.from?.username ? `@${ctx.from.username}` : '';
  const fullName = `${firstName} ${lastName}`.trim() || username || 'Unknown';
  const action = ctx.updateType || 'unknown';

  const isAuth = isAuthorized(userId);
  const isAdminUser = isAdmin(userId);
  const role = isAdminUser ? 'ADMIN' : isAuth ? 'USER' : 'UNAUTHORIZED';

  logger.http('User action', action, 200, 0, {
    userId,
    fullName,
    role,
    username
  });

  return next();
}

module.exports = {
  isAuthorized,
  isAdmin,
  requireAuth,
  requireAdmin,
  logUserAction
};
