'use strict';

/**
 * ============================================================================
 * 📝 MARKDOWN V1 UTILITIES (Legacy Mode)
 * ============================================================================
 * Manejo seguro de cadenas para Telegram Markdown (V1).
 * NOTA: En V1 NO se deben escapar puntos (.), guiones (-) ni paréntesis.
 * ============================================================================
 */

/**
 * Escapa SOLO los caracteres reservados de Markdown V1.
 * @param {string} text - Texto a escapar.
 * @returns {string} Texto seguro para enviar.
 */
const escapeMarkdown = (text) => {
  if (text === null || text === undefined) return '';
  // En V1 solo escapamos: [  _  *  `
  return String(text).replace(/[[_*`]/g, '\\$&');
};

/**
 * Crea texto en negrita.
 * Ejemplo: *Texto*
 */
const bold = (text) => {
  if (!text) return '';
  return `*${escapeMarkdown(text)}*`;
};

/**
 * Crea texto en cursiva.
 * Ejemplo: _Texto_
 */
const italic = (text) => {
  if (!text) return '';
  return `_${escapeMarkdown(text)}_`;
};

/**
 * Crea texto monoespaciado (ideal para IPs, IDs, comandos).
 * Ejemplo: `Texto`
 */
const code = (text) => {
  if (!text) return '';
  // En bloques de código inline, V1 no requiere escapar mucho, 
  // pero escapamos las tildes inversas para evitar romper el bloque.
  return `\`${String(text).replace(/`/g, '\\`')}\``;
};

/**
 * Crea un bloque de código multilinea.
 * Ideal para logs o configuraciones.
 */
const pre = (text, language = '') => {
  if (!text) return '';
  // En V1 el lenguaje no siempre se renderiza bien en todos los clientes, 
  // pero lo incluimos por si acaso.
  return `\`\`\`${language}\n${String(text).replace(/`/g, '\\`')}\n\`\`\``;
};

/**
 * Crea un enlace con texto personalizado.
 * Ejemplo: [Google](https://google.com)
 */
const link = (text, url) => {
  if (!text || !url) return '';
  return `[${escapeMarkdown(text)}](${url})`;
};

/**
 * Crea una mención a un usuario (sin usar username).
 * Útil cuando el usuario no tiene @alias.
 */
const userMention = (name, id) => {
  return `[${escapeMarkdown(name)}](tg://user?id=${id})`;
};

module.exports = {
  escapeMarkdown,
  bold,
  italic,
  code,
  pre,
  link,
  userMention
};
