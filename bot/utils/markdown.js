// utils/markdown.js

/**
 * Escapa caracteres especiales de Markdown V2 en Telegram
 * @param {string} text - Texto a escapar
 * @returns {string} - Texto con caracteres especiales escapados
 */
function escapeMarkdown(text) {
  if (!text) return '';
  
  // Caracteres que deben ser escapados en Markdown V2
  const specialChars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'];
  
  let escaped = text.toString();
  specialChars.forEach(char => {
    escaped = escaped.replace(new RegExp('\\' + char, 'g'), '\\' + char);
  });
  
  return escaped;
}

/**
 * Escapa solo para contexto de código inline
 */
function escapeCode(text) {
  if (!text) return '';
  return text.toString().replace(/`/g, '\\`').replace(/\\/g, '\\\\');
}

/**
 * Formatea texto en negrita de forma segura
 */
function bold(text) {
  return `**${escapeMarkdown(text)}**`;
}

/**
 * Formatea texto en cursiva de forma segura
 */
function italic(text) {
  return `_${escapeMarkdown(text)}_`;
}

/**
 * Formatea texto como código de forma segura
 */
function code(text) {
  return `\`${escapeCode(text)}\``;
}

/**
 * Crea un enlace de forma segura
 */
function link(text, url) {
  return `[${escapeMarkdown(text)}](${url})`;
}

module.exports = {
  escapeMarkdown,
  escapeCode,
  bold,
  italic,
  code,
  link
};
