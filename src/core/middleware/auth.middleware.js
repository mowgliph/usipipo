'use strict';

/**
 * ============================================================================
 * 🔐 AUTH MIDDLEWARE - uSipipo VPN Bot
 * ============================================================================
 * Middleware de autenticación y autorización basado en environment.js
 * 
 * ✅ Usa las listas de AUTHORIZED_USERS y ADMIN_ID desde environment.js
 * ✅ No requiere base de datos ni userManager externo
 * ✅ Logging integrado con el logger central
 * ============================================================================
 */

const logger = require('../utils/logger');
const markdown = require('../utils/markdown');
const config = require('../../config/environment');
const constants = require('../../config/constants');

// ============================================================================
// 🔎 USER METADATA HELPER
// ============================================================================

/**
 * Extrae metadatos del usuario desde el contexto de Telegram
 */
function getUserMeta(ctx) {
  const userId = ctx.from?.id;
  const username = ctx.from?.username ? `@${ctx.from.username}` : null;
  const firstName = ctx.from?.first_name || '';
  const lastName = ctx.from?.last_name || '';
  
  const fullName = [firstName, lastName].filter(Boolean).join(' ') || 
                   username || 
                   `User#${userId}`;

  // Convertir userId a string para comparaciones (config usa strings)
  const userIdStr = userId ? String(userId) : null;
  
  return {
    userId: userIdStr,
    username,
    fullName,
    firstName,
    lastName,
    isAuthorized: userIdStr ? config.AUTHORIZED_USERS.includes(userIdStr) : false,
    isAdmin: userIdStr ? userIdStr === String(config.ADMIN_ID) : false
  };
}

// ============================================================================
// 🔐 MIDDLEWARE DE AUTENTICACIÓN
// ============================================================================

/**
 * Middleware que exige que el usuario esté autorizado
 */
async function requireAuth(ctx, next) {
  const meta = getUserMeta(ctx);

  // Si no hay userId (mensaje anónimo o sin from), denegar
  if (!meta.userId) {
    logger.warn('ACCESS DENIED — Anonymous request', { 
      updateType: ctx.updateType,
      chatId: ctx.chat?.id 
    });
    
    await ctx.reply(
      `${constants.EMOJI.ERROR} *Acceso denegado*\n\n` +
      `No se pudo identificar tu usuario. Asegúrate de estar registrado en Telegram.`,
      { parse_mode: 'Markdown' }
    );
    return;
  }

  // Verificar autorización
  if (!meta.isAuthorized) {
    logger.warn('ACCESS DENIED — User not authorized', meta);

    const message = 
      `${constants.EMOJI.ERROR} *Acceso denegado*\n\n` +
      `Lo siento, *${markdown.escapeMarkdown(meta.fullName)}*, no estás autorizado para usar este bot.\n\n` +
      `*Tu ID:* \`${meta.userId}\`\n` +
      `Contacta al administrador para solicitar acceso.`;

    await ctx.reply(message, { parse_mode: 'Markdown' });
    return;
  }

  logger.debug('ACCESS GRANTED — Authorized user', meta);
  return next();
}

/**
 * Middleware que exige permisos de administrador
 */
async function requireAdmin(ctx, next) {
  const meta = getUserMeta(ctx);

  // Primero verificar autorización básica
  if (!meta.userId || !meta.isAuthorized) {
    logger.warn('ACCESS DENIED — Admin check failed: Not authorized', meta);
    
    await ctx.reply(
      `${constants.EMOJI.ERROR} *Acceso denegado*\n\n` +
      `No tienes permisos para acceder a esta función.`,
      { parse_mode: 'Markdown' }
    );
    return;
  }

  // Verificar permisos de administrador
  if (!meta.isAdmin) {
    logger.warn('ACCESS DENIED — Admin only', meta);

    const message = 
      `${constants.EMOJI.ERROR} *Acceso restringido*\n\n` +
      `Esta función es exclusiva para administradores.\n\n` +
      `*Tu ID:* \`${meta.userId}\`\n` +
      `*Tu rol:* Usuario autorizado`;

    await ctx.reply(message, { parse_mode: 'Markdown' });
    return;
  }

  logger.debug('ACCESS GRANTED — Admin user', meta);
  return next();
}

// ============================================================================
// 📊 LOGGING DE ACCIONES DE USUARIO
// ============================================================================

/**
 * Middleware para log de todas las acciones de usuario
 */
async function logUserAction(ctx, next) {
  const meta = getUserMeta(ctx);
  
  const actionType = ctx.updateType || 'unknown';
  const messagePayload = 
    ctx.message?.text || 
    ctx.callbackQuery?.data || 
    ctx.inlineQuery?.query || 
    null;

  // Log estructurado
  logger.http('USER_ACTION', {
    ...meta,
    actionType,
    message: messagePayload ? messagePayload.substring(0, 200) : null,
    chatId: ctx.chat?.id,
    chatType: ctx.chat?.type,
    timestamp: new Date().toISOString()
  });

  return next();
}

// ============================================================================
// 🛡️ FUNCIONES DE VERIFICACIÓN DIRECTAS
// ============================================================================

/**
 * Verifica si un usuario está autorizado (sin contexto)
 */
function isAuthorized(userId) {
  if (!userId) return false;
  return config.AUTHORIZED_USERS.includes(String(userId));
}

/**
 * Verifica si un usuario es administrador (sin contexto)
 */
function isAdmin(userId) {
  if (!userId) return false;
  return String(userId) === String(config.ADMIN_ID);
}

// ============================================================================
// 📦 EXPORTS
// ============================================================================

module.exports = {
  // Middlewares principales
  requireAuth,
  requireAdmin,
  logUserAction,
  
  // Funciones de verificación
  isAuthorized,
  isAdmin,
  
  // Helper para debugging
  getUserMeta
};