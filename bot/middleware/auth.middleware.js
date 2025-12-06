// middleware/auth.middleware.js
const userManager = require('../services/userManager.service');
const messages = require('../utils/messages');
const logger = require('../utils/logger');

/**
 * Verifica si un usuario está autorizado.
 * @param {number|string} userId - ID del usuario.
 * @returns {boolean}
 */
function isAuthorized(userId) {
  return userManager.isAuthorized(userId);
}

/**
 * Verifica si un usuario es administrador.
 * @param {number|string} userId - ID del usuario.
 * @returns {boolean}
 */
function isAdmin(userId) {
  return userManager.isAdmin(userId);
}

/**
 * Middleware: Requiere autorización de usuario.
 * Si el usuario no está autorizado, detiene el flujo y responde con ACCESS_DENIED.
 * @param {import('telegraf').Context} ctx
 * @param {Function} next
 */
async function requireAuth(ctx, next) {
  const userId = ctx.from?.id;
  const userName = ctx.from?.username || ctx.from?.first_name || `User${userId}`;

  try {
    if (!isAuthorized(userId)) {
      logger.warn('Access denied', { userId, userName });
      await ctx.reply(messages.ACCESS_DENIED, { parse_mode: 'MarkdownV2' });
      return;
    }

    logger.debug('Authorized access', { userId, userName });
    return next();
  } catch (error) {
    logger.error('requireAuth', error, { userId, userName });
    await ctx.reply('⚠️ Error de autorización interna.');
  }
}

/**
 * Middleware: Requiere permisos de administrador.
 * Si el usuario no es admin, detiene el flujo y responde con ADMIN_ONLY.
 * @param {import('telegraf').Context} ctx
 * @param {Function} next
 */
async function requireAdmin(ctx, next) {
  const userId = ctx.from?.id;
  const userName = ctx.from?.username || ctx.from?.first_name || `User${userId}`;

  try {
    if (!isAdmin(userId)) {
      logger.warn('Admin access denied', { userId, userName });
      await ctx.reply(messages.ADMIN_ONLY, { parse_mode: 'MarkdownV2' });
      return;
    }

    logger.debug('Admin access granted', { userId, userName });
    return next();
  } catch (error) {
    logger.error('requireAdmin', error, { userId, userName });
    await ctx.reply('⚠️ Error al verificar permisos de administrador.');
  }
}

/**
 * Middleware global de logging contextualizado.
 * Registra ID, nombre, rol y tipo de acción (ctx.type).
 * @param {import('telegraf').Context} ctx
 * @param {Function} next
 */
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