// utils/markdown.js

/**
 * Escapa caracteres especiales de Markdown V2 en Telegram.
 * Úsalo solo cuando el texto vaya a ser renderizado con parse_mode: 'MarkdownV2'.
 * @param {string} text - Texto a escapar
 * @returns {string} Texto escapado
 * @throws {TypeError} Si el input no es string
 */
function escapeMarkdown(text) {
  if (typeof text !== 'string') {
    throw new TypeError('Input must be a string');
  }

  // Caracteres que Telegram exige escapar en MarkdownV2 (excluyendo . para preservar URLs/emails)
  const specials = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '!'];

  let escaped = text;
  specials.forEach((ch) => {
    escaped = escaped.replace(new RegExp(`\\${ch}`, 'g'), `\\${ch}`);
  });

  return escaped;
}

/**
 * Escapa texto para bloques de código (incluyendo backticks y backslash).
 * @param {string} text - Texto a escapar
 * @returns {string} Texto escapado para código
 * @throws {TypeError} Si el input no es string
 */
function escapeCode(text) {
  if (typeof text !== 'string') {
    throw new TypeError('Input must be a string');
  }
  return text.replace(/\\/g, '\\\\').replace(/`/g, '\\`');
}

/**
 * Formatea texto en negrita (MarkdownV2: **texto**).
 * @param {string} text - Texto a formatear
 * @returns {string} Texto en negrita escapado
 * @throws {TypeError} Si el input no es string
 */
function bold(text) {
  return `**${escapeMarkdown(text)}**`;
}

/**
 * Formatea texto en cursiva (MarkdownV2: __texto__).
 * @param {string} text - Texto a formatear
 * @returns {string} Texto en cursiva escapado
 * @throws {TypeError} Si el input no es string
 */
function italic(text) {
  return `__${escapeMarkdown(text)}__`;
}

/**
 * Formatea texto como código inline (MarkdownV2: `texto`).
 * @param {string} text - Texto a formatear
 * @returns {string} Texto como código inline escapado
 * @throws {TypeError} Si el input no es string
 */
function code(text) {
  return ``${escapeCode(text)}``;
}

/**
 * Crea un enlace seguro (MarkdownV2: [texto](url)).
 * @param {string} text - Texto visible
 * @param {string} url - URL destino (no escapada, debe ser válida)
 * @returns {string} Enlace formateado
 * @throws {TypeError} Si text o url no son strings
 */
function link(text, url) {
  if (typeof text !== 'string' || typeof url !== 'string') {
    throw new TypeError('Both text and url must be strings');
  }
  return `[${escapeMarkdown(text)}](${url})`;
}

/**
 * Formatea texto tachado (MarkdownV2: ~~texto~~).
 * @param {string} text - Texto a formatear
 * @returns {string} Texto tachado escapado
 * @throws {TypeError} Si el input no es string
 */
function strikethrough(text) {
  return `~~${escapeMarkdown(text)}~~`;
}

/**
 * Formatea texto como spoiler (MarkdownV2: ||texto||).
 * @param {string} text - Texto a formatear
 * @returns {string} Texto spoiler escapado
 * @throws {TypeError} Si el input no es string
 */
function spoiler(text) {
  return `||${escapeMarkdown(text)}||`;
}

/**
 * Formatea texto subrayado (MarkdownV2: <u>texto</u> para compatibilidad limitada).
 * Nota: Telegram V2 prefiere entidades via API, pero para string: <u>texto</u>.
 * @param {string} text - Texto a formatear
 * @returns {string} Texto subrayado escapado
 * @throws {TypeError} Si el input no es string
 */
function underline(text) {
  return `<u>${escapeMarkdown(text)}</u>`;
}

module.exports = {
  escapeMarkdown,
  escapeCode,
  bold,
  italic,
  code,
  link,
  strikethrough,
  spoiler,
  underline
};