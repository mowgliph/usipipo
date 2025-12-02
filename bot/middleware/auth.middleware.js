// middleware/auth.middleware.js
const config = require('../config/environment');
const messages = require('../utils/messages');

/**
 * Verifica si un usuario está autorizado
 */
function isAuthorized(userId) {
  return config.AUTHORIZED_USERS.includes(userId.toString());
}

/**
 * Verifica si un usuario es administrador
 */
function isAdmin(userId) {
  return userId.toString() === config.ADMIN_ID;
}

/**
 * Middleware para verificar autorización
 */
function requireAuth(ctx, next) {
  const userId = ctx.from?.id.toString();
  
  if (!isAuthorized(userId)) {
    return ctx.reply(messages.ACCESS_DENIED, { parse_mode: 'Markdown' });
  }
  
  return next();
}

/**
 * Middleware para verificar permisos de administrador
 */
function requireAdmin(ctx, next) {
  const userId = ctx.from?.id.toString();
  
  if (!isAdmin(userId)) {
    return ctx.reply(messages.ADMIN_ONLY, { parse_mode: 'Markdown' });
  }
  
  return next();
}

/**
 * Middleware de logging
 */
function logUserAction(ctx, next) {
  const userId = ctx.from?.id;
  const username = ctx.from?.username || ctx.from?.first_name;
  const action = ctx.updateType;
  
  console.log(`📝 [${new Date().toISOString()}] User ${userId} (${username}) - ${action}`);
  
  return next();
}

module.exports = {
  isAuthorized,
  isAdmin,
  requireAuth,
  requireAdmin,
  logUserAction
};
