'use strict';

const userManager = require('../services/userManager.service');
const messages = require('../utils/messages');
const logger = require('../utils/logger');
const { escapeHtml } = require('../utils/format');

// ============================================================================
// 🔎 User Metadata Helper
// ============================================================================

/**
 * Obtiene toda la metadata relevante del usuario que realiza una acción.
 * Se usa en logs, validaciones y auditorías.
 */
function getUserMeta(ctx) {
  const userId = ctx.from?.id;
  const username = ctx.from?.username ? `@${ctx.from.username}` : null;

  const firstName = escapeHtml(ctx.from?.first_name || '');
  const lastName = escapeHtml(ctx.from?.last_name || '');
  const fullName =
    (firstName + ' ' + lastName).trim() ||
    username ||
    `User${userId}`;

  return {
    userId,
    username,
    fullName,
    isAuthorized: userManager.isAuthorized(userId),
    isAdmin: userManager.isAdmin(userId)
  };
}

// ============================================================================
// 🔐 Middlewares de Seguridad
// ============================================================================

/**
 * Exige que el usuario esté autorizado en el sistema.
 */
async function requireAuth(ctx, next) {
  const meta = getUserMeta(ctx);

  try {
    if (!meta.isAuthorized) {
      logger.warn('ACCESS DENIED — User not authorized', meta);

      await ctx.reply(messages.ACCESS_DENIED, { parse_mode: 'HTML' });
      return;
    }

    logger.debug('ACCESS GRANTED — Authorized user', meta);
    return next();
  } catch (error) {
    logger.error('requireAuth', error, meta);

    await ctx.reply(
      '⚠️ Ocurrió un error durante la verificación de permisos.',
      { parse_mode: 'HTML' }
    );
  }
}

/**
 * Exige que el usuario sea administrador.
 */
async function requireAdmin(ctx, next) {
  const meta = getUserMeta(ctx);

  try {
    if (!meta.isAdmin) {
      logger.warn('ACCESS DENIED — Admin only', meta);

      await ctx.reply(messages.ADMIN_ONLY, { parse_mode: 'HTML' });
      return;
    }

    logger.debug('ACCESS GRANTED — Admin user', meta);
    return next();
  } catch (error) {
    logger.error('requireAdmin', error, meta);

    await ctx.reply(
      '⚠️ Error interno al validar los permisos de administrador.',
      { parse_mode: 'HTML' }
    );
  }
}

// ============================================================================
// 📝 Logger Universal de Actividad
// ============================================================================

/**
 * Log de TODA acción del usuario:
 * - comandos
 * - mensajes
 * - callbacks
 * - botones
 * - eventos desconocidos
 *
 * Nivel: http (auditoría)
 */
async function logUserAction(ctx, next) {
  const meta = getUserMeta(ctx);

  const actionType = ctx.updateType || 'unknown';
  const messagePayload =
    ctx.message?.text ||
    ctx.callbackQuery?.data ||
    null;

  logger.http('UserAction', actionType, 200, 0, {
    ...meta,
    actionType,
    message: messagePayload
  });

  return next();
}

// ============================================================================
// 📦 Exports
// ============================================================================

module.exports = {
  isAuthorized: (id) => userManager.isAuthorized(id),
  isAdmin: (id) => userManager.isAdmin(id),
  requireAuth,
  requireAdmin,
  logUserAction
};