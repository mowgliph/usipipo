'use strict';

/**
 * ============================================================================
 * 📝 MARKDOWN UTILITIES (Telegram Markdown V1)
 * Centraliza el escape y formateo de texto para evitar redundancia.
 * ============================================================================
 */

/**
 * Escapa caracteres reservados de Markdown V1.
 * Caracteres: _ * ` [
 */
const escapeMarkdown = (text) =>
  text
    ? String(text)
        .replace(/_/g, '\\_')
        .replace(/\*/g, '\\*')
        .replace(/`/g, '\\`')
        .replace(/\[/g, '\\[')
    : '';

const bold = (text) => `*${escapeMarkdown(text)}*`;
const italic = (text) => `_${escapeMarkdown(text)}_`;
const code = (text) => `\`${escapeMarkdown(text)}\``;
const pre = (text) => `\`\`\`\n${escapeMarkdown(text)}\n\`\`\``;

module.exports = {
  escapeMarkdown,
  bold,
  italic,
  code,
  pre
};
