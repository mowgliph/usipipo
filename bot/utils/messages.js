'use strict';

const config = require('../config/environment');
const constants = require('../config/constants');

// ============================================================================
// 🧩 HTML UTILITIES
// ============================================================================
const escapeHtml = (text) =>
  text
    ? String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
    : '';

const bold = (txt) => `<b>${escapeHtml(txt)}</b>`;
const italic = (txt) => `<i>${escapeHtml(txt)}</i>`;
const code = (txt) => `<code>${escapeHtml(txt)}</code>`;

// ============================================================================
// 📋 COMMAND LIST
// ============================================================================
const USER_COMMANDS = [
  '/start - Menú principal',
  '/miinfo - Ver tus datos',
  '/status - Ver estado de acceso',
  '/commands - Comandos disponibles',
  '/help - Ayuda'
];

const ADMIN_COMMANDS = [
  '/add [ID] [nombre] - Autorizar usuario',
  '/rm [ID] - Remover usuario',
  '/sus [ID] - Suspender usuario',
  '/react [ID] - Reactivar usuario',
  '/users - Listar usuarios',
  '/stats - Estadísticas',
  '/broadcast [msg] - Mensaje masivo',
  '/sms [ID] [txt] - Mensaje directo',
  '/templates - Plantillas rápidas'
];

// ============================================================================
// 💬 MESSAGES — Estilo premium tipo App
// ============================================================================
const messages = {
  // ------------------------------------------------------------------------
  // 🟢 Bienvenida
  // ------------------------------------------------------------------------
  WELCOME_AUTHORIZED: (name) =>
    `👋 Hola ${escapeHtml(name)}\n\n` +
    `${bold('Bienvenido nuevamente')}\n` +
    `Accede a las opciones desde el menú.`,

  WELCOME_UNAUTHORIZED: (name) =>
    `👋 Hola ${escapeHtml(name)}\n\n` +
    `${bold('Tu acceso aún no está autorizado.')}\n\n` +
    `Usa /miinfo para obtener tus datos y envíalos al administrador:\n` +
    `${code(config.ADMIN_ID || 'No definido')}`,

  // ------------------------------------------------------------------------
  // 👤 Información del usuario
  // ------------------------------------------------------------------------
  USER_INFO: (user, isAuth) => {
    const username = user.username ? '@' + escapeHtml(user.username) : 'No disponible';

    return (
      `👤 ${bold('Datos de tu cuenta')}\n\n` +
      `ID: ${code(user.id)}\n` +
      `Nombre: ${escapeHtml(user.first_name || '')}\n` +
      `Username: ${username}\n\n` +
      (isAuth ? constants.STATUS.AUTHORIZED : constants.STATUS.UNAUTHORIZED)
    );
  },

  // ------------------------------------------------------------------------
  // 📨 Solicitud de acceso
  // ------------------------------------------------------------------------
  ACCESS_REQUEST_SENT: (user) =>
    `📨 ${bold('Solicitud enviada correctamente')}\n\n` +
    `ID: ${code(user.id)}\n` +
    `Nombre: ${escapeHtml(user.first_name || '')}\n\n` +
    `Envía este ID al administrador para continuar.`,

  ACCESS_REQUEST_ADMIN_NOTIFICATION: (user) => {
    const name = escapeHtml(user.first_name || '');
    const username = user.username ? '@' + escapeHtml(user.username) : 'Sin username';

    return (
      `🔔 ${bold('Nueva solicitud de acceso')}\n\n` +
      `👤 Usuario: ${name}\n` +
      `🆔 ID: ${code(user.id)}\n` +
      `💬 Username: ${username}\n\n` +
      `Para autorizar:\n${code('/add ' + user.id)}`
    );
  },

  ACCESS_DENIED: `⛔ ${bold('Acceso denegado')}`,
  ADMIN_ONLY: `⛔ ${bold('Solo administradores')}`,

  // ------------------------------------------------------------------------
  // 🔐 WireGuard
  // ------------------------------------------------------------------------
  WIREGUARD_CREATING: '⏳ Generando tu perfil WireGuard...',

  WIREGUARD_SUCCESS: (ip) =>
    `✅ ${bold('WireGuard creado correctamente')}\n\n` +
    `🖥 IP asignada: ${code(ip)}\n` +
    `🌐 Endpoint: ${code(`${config.SERVER_IP}:${config.WG_SERVER_PORT}`)}\n\n` +
    `Descarga el archivo o escanea el código QR.`,

  WIREGUARD_INSTRUCTIONS:
    `${bold('Instrucciones de uso')}\n\n` +
    `📱 *Móvil*: Abrir app → "+" → Escanear QR\n` +
    `💻 *PC*: Importar archivo .conf\n\n` +
    `Descargar WireGuard:\n${constants.URLS.WIREGUARD_DOWNLOAD}`,

  ERROR_WIREGUARD: (e) => `❌ Error en WireGuard:\n${escapeHtml(String(e))}`,

  // ------------------------------------------------------------------------
  // 🌐 Outline
  // ------------------------------------------------------------------------
  OUTLINE_CREATING: '⏳ Generando acceso Outline...',

  OUTLINE_SUCCESS: (key) =>
    `✅ ${bold('Acceso Outline generado')}\n\n` +
    `ID: ${code(key.id)}\n` +
    `Enlace:\n${code(key.accessUrl)}\n\n` +
    `Descargar Outline:\n${constants.URLS.OUTLINE_DOWNLOAD}`,

  ERROR_OUTLINE: (e) => `❌ Error en Outline:\n${escapeHtml(String(e))}`,

  // ------------------------------------------------------------------------
  // 🖥 Estado del servidor
  // ------------------------------------------------------------------------
  SERVER_STATUS: () =>
    `🖥️ ${bold('Estado del servidor')}\n\n` +
    `IPv4: ${code(config.SERVER_IPV4)}\n` +
    `Puerto WireGuard: ${code(config.WG_SERVER_PORT)}\n` +
    `Outline API: ${code(config.OUTLINE_API_PORT)}\n` +
    `DNS (Pi-hole): ${code(config.PIHOLE_DNS || 'N/A')}\n\n` +
    `Todos los servicios están operativos.`,

  ERROR_SERVER_STATUS: '⚠️ No se pudo consultar el estado del servidor.',

  // ------------------------------------------------------------------------
  // 📚 Ayuda
  // ------------------------------------------------------------------------
  HELP_AUTHORIZED:
    `📚 ${bold('Guía rápida')}\n\n` +
    `🔐 ${bold('WireGuard')}: rápido y estable\n` +
    `🌐 ${bold('Outline')}: ideal para móviles\n` +
    `🛑 ${bold('Pi-hole')}: bloqueo de anuncios activo\n\n` +
    `Soporte: ${code(config.ADMIN_ID || 'No definido')}`,

  HELP_UNAUTHORIZED:
    `📚 ${bold('Ayuda')}\n\n` +
    `1️⃣ Usa /miinfo para obtener tu ID\n` +
    `2️⃣ Envíalo al administrador\n` +
    `3️⃣ Espera aprobación\n\n` +
    `Contacto: ${code(config.ADMIN_ID)}`,

  ERROR_LIST_CLIENTS: '❌ No se pudo obtener la lista de clientes.',

  // ------------------------------------------------------------------------
  // 👑 Administrador
  // ------------------------------------------------------------------------
  ADMIN_USER_ADDED: (id, name, addedAt) =>
    `✅ ${bold('Usuario autorizado')}\n\n` +
    `ID: ${code(id)}\n` +
    `Nombre: ${escapeHtml(name)}\n` +
    `Fecha: ${escapeHtml(addedAt)}`,

  ADMIN_USER_REMOVED: (id) => `🗑️ ${bold('Usuario eliminado')}\nID: ${code(id)}`,

  ADMIN_USER_SUSPENDED: (id) =>
    `⏸️ ${bold('Usuario suspendido')}\nID: ${code(id)}\n` +
    `Para reactivarlo usa: ${code(`/react ${id}`)}`,

  ADMIN_USER_REACTIVATED: (id) =>
    `▶️ ${bold('Usuario reactivado')}\nID: ${code(id)}`,

  ADMIN_USER_LIST: (users, stats) => {
    const header =
      `👥 ${bold('Usuarios registrados')}\n` +
      `Total: ${stats.total} • Activos: ${stats.active}\n\n`;

    const rows = users
      .map((u, i) => {
        const status = u.status === 'active' ? '🟢' : '⛔';
        const role = u.role === 'admin' ? '👑' : '👤';
        return `${i + 1}. ${status} ${role} ${code(u.id)} — ${escapeHtml(u.name)}`;
      })
      .join('\n');

    return header + (rows || italic('No hay usuarios registrados.'));
  },

  ADMIN_STATS: (stats, new24h) =>
    `📊 ${bold('Estadísticas del sistema')}\n\n` +
    `Usuarios totales: ${stats.total}\n` +
    `Activos: ${stats.active}\n` +
    `Suspendidos: ${stats.suspended}\n` +
    `Administradores: ${stats.admins}\n\n` +
    `Nuevos en 24h: ${new24h}`,

  BROADCAST_PREVIEW: (id, msg, u, a, t) =>
    `📢 ${bold('Confirmar envío')}\n\n` +
    `${msg}\n\n` +
    `Destinatarios:\n` +
    `• Usuarios: ${u}\n` +
    `• Admins: ${a}\n` +
    `• Total: ${t}\n\n` +
    `ID: ${code(id)}`,

  BROADCAST_RESULT: (ok, fail) =>
    `📢 ${bold('Envío completado')}\n\n` +
    `✅ Enviados: ${ok}\n` +
    `❌ Fallidos: ${fail}`,

  ADMIN_DIRECT_MSG_SENT: (id, name) =>
    `📨 ${bold('Mensaje enviado')}\nID: ${code(id)}\nUsuario: ${escapeHtml(name)}`,

  ADMIN_TEMPLATES: () =>
    `📋 ${bold('Plantillas disponibles')}\n\n` +
    `1) ${code('/broadcast 🎉 Bienvenido a uSipipo VPN')}\n` +
    `2) ${code('/broadcast ⚠️ Mantenimiento programado [FECHA]')}\n` +
    `3) ${code('/broadcast 🎁 Promoción activa: ...')}`,

  // ------------------------------------------------------------------------
  // ❌ Comandos desconocidos
  // ------------------------------------------------------------------------
  UNKNOWN_COMMAND: (isAdmin) => {
    let msg =
      `⚠️ ${bold('Comando no reconocido')}\n\n` +
      `${bold('Comandos de usuario:')}\n`;

    msg += USER_COMMANDS.map((c) => `• ${escapeHtml(c)}\n`).join('');

    if (isAdmin) {
      msg += `\n${bold('Comandos de administrador:')}\n`;
      msg += ADMIN_COMMANDS.map((c) => `• ${escapeHtml(c)}\n`).join('');
    }

    return msg + `\n\nUsa ${code('/start')} para volver al menú.`;
  },

  COMMANDS_LIST: (isAdmin) => {
    let msg =
      `📋 ${bold('Lista de comandos')}\n\n` +
      `👤 ${bold('Usuario:')}\n`;

    msg += USER_COMMANDS.map((c) => `• ${escapeHtml(c)}\n`).join('');

    if (isAdmin) {
      msg += `\n👑 ${bold('Administrador:')}\n`;
      msg += ADMIN_COMMANDS.map((c) => `• ${escapeHtml(c)}\n`).join('');
    }

    return msg;
  },

  GENERIC_TEXT_PROMPT: (name) =>
    `👋 Hola ${escapeHtml(name)}\n\nSelecciona el tipo de VPN:\n• WireGuard\n• Outline`,

  // ------------------------------------------------------------------------
  // Helpers exportados
  // ------------------------------------------------------------------------
  _helpers: { escapeHtml, bold, code, italic }
};

module.exports = messages;