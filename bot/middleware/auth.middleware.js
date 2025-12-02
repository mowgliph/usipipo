// middleware/auth.middleware.js
const userManager = require('../services/userManager.service');
const messages = require('../utils/messages');

/**
 * Verifica si un usuario está autorizado
 */
function isAuthorized(userId) {
  return userManager.isAuthorized(userId);
}

/**
 * Verifica si un usuario es administrador
 */
function isAdmin(userId) {
  return userManager.isAdmin(userId);
}

/**
 * Middleware para verificar autorización
 */
function requireAuth(ctx, next) {
  const userId = ctx.from?.id;
  
  if (!isAuthorized(userId)) {
    return ctx.reply(messages.ACCESS_DENIED, { parse_mode: 'Markdown' });
  }
  
  return next();
}

/**
 * Middleware para verificar permisos de administrador
 */
function requireAdmin(ctx, next) {
  const userId = ctx.from?.id;
  
  if (!isAdmin(userId)) {
    return ctx.reply(messages.ADMIN_ONLY, { parse_mode: 'Markdown' });
  }
  
  return next();
}

/**
 * Middleware de logging con contexto mejorado
 */
function logUserAction(ctx, next) {
  const userId = ctx.from?.id;
  const username = ctx.from?.username || ctx.from?.first_name;
  const action = ctx.updateType;
  const isAuth = isAuthorized(userId);
  const isAdminUser = isAdmin(userId);
  
  const role = isAdminUser ? '👑' : isAuth ? '✅' : '❌';
  console.log(`${role} [${new Date().toISOString()}] ${userId} (${username}) - ${action}`);
  
  return next();
}

module.exports = {
  isAuthorized,
  isAdmin,
  requireAuth,
  requireAdmin,
  logUserAction
};
