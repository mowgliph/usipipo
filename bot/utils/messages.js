const config = require('../config/environment');
const constants = require('../config/constants');

// ========== HTML UTILS ==========
const escapeHtml = (text) =>
  text ? String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') : '';

const bold = (txt) => `<b>${txt}</b>`;
const italic = (txt) => `<i>${txt}</i>`;
const code = (txt) => `<code>${txt}</code>`;

// ========== COMANDOS ==========
const USER_COMMANDS = [
  '/start - Menú principal',
  '/miinfo - Ver tus datos',
  '/status - Ver tu estado'
];

const ADMIN_COMMANDS = [
  '/ad [ID] [nombre] - Autorizar usuario',
  '/rm [ID] - Quitar acceso',
  '/sus [ID] - Suspender usuario',
  '/react [ID] - Reactivar usuario',
  '/users - Listar usuarios',
  '/stats - Estadísticas',
  '/broadcast [msg] - Enviar mensaje masivo',
  '/sms [ID] [txt] - Mensaje directo',
  '/templates - Plantillas'
];

// ========== MENSAJES ==========
const messages = {
  // ——— Bienvenida ———
  WELCOME_AUTHORIZED: (name) =>
    `👋 Hola ${escapeHtml(name)}

${bold('Acceso autorizado')}
Selecciona una opción del menú.`,

  WELCOME_UNAUTHORIZED: (name) =>
    `👋 Hola ${escapeHtml(name)}

${bold('No tienes acceso autorizado.')}

Usa /miinfo y envía tu ID al admin:
${bold(escapeHtml(config.ADMIN_EMAIL || 'admin@example.com'))}`,

  // ——— Info de usuario ———
  USER_INFO: (user, isAuth) => {
    const username = user.username ? '@' + escapeHtml(user.username) : 'No disponible';

    return `👤 ${bold('Datos de Telegram')}

ID: ${code(user.id)}
Nombre: ${escapeHtml(user.first_name || '')}
Username: ${username}

${isAuth ? constants.STATUS.AUTHORIZED : constants.STATUS.UNAUTHORIZED}`;
  },

  // ——— Solicitud de acceso ———
  ACCESS_REQUEST_SENT: (user) =>
    `📧 ${bold('Solicitud enviada')}

ID: ${code(user.id)}
Nombre: ${escapeHtml(user.first_name || '')}

Envía estos datos al admin:
${bold(escapeHtml(config.ADMIN_EMAIL || 'admin@example.com'))}`,

  ACCESS_REQUEST_ADMIN_NOTIFICATION: (user) => {
    const name = escapeHtml(user.first_name || '');
    const username = user.username ? '@' + escapeHtml(user.username) : 'Sin username';

    return `🔔 ${bold('Nueva solicitud')}

Usuario: ${name}
ID: ${code(user.id)}
Username: ${username}

Para autorizar usa:
${code('/ad ' + user.id)}`;
  },

  ACCESS_DENIED: `⛔ ${bold('Acceso denegado')}
No tienes permisos para esta acción.`,

  ADMIN_ONLY: `⛔ ${bold('Solo administradores')}`,

  // ——— WireGuard ———
  WIREGUARD_CREATING: '⏳ Generando configuración WireGuard...',

  WIREGUARD_SUCCESS: (ip) =>
    `✅ ${bold('WireGuard creado')}

IP: ${code(ip)}
Endpoint: ${code(`${config.SERVER_IPV4}:${config.WIREGUARD_PORT}`)}

Escanea el QR para conectarte.`,

  WIREGUARD_INSTRUCTIONS: `${bold('Instrucciones:')}
• Móvil: Abrir app → "+" → Escanear QR
• PC: Importar archivo .conf

Descarga: ${constants.URLS.WIREGUARD_DOWNLOAD}`,

  // ——— Outline ———
  OUTLINE_CREATING: '⏳ Generando clave Outline...',

  OUTLINE_SUCCESS: (key) =>
    `✅ ${bold('Outline creado')}

ID: ${code(key.id)}
Enlace:
${code(key.accessUrl)}

DNS con bloqueo activo
Descarga Outline: ${constants.URLS.OUTLINE_DOWNLOAD}`,

  // ——— Estado del servidor ———
  SERVER_STATUS: () =>
    `🖥️ ${bold('Estado del servidor')}

IP: ${code(config.SERVER_IPV4)}
WG: ${code(config.WIREGUARD_PORT)}
Outline: ${code(config.OUTLINE_API_PORT)}
DNS: ${code(config.PIHOLE_DNS)}

Servicios operativos.`,

  // ——— Ayuda ———
  HELP_AUTHORIZED: `📚 ${bold('Guía rápida')}

${bold('WireGuard:')} rápido y estable
${bold('Outline:')} fácil para móviles
${bold('Pi-hole:')} bloqueo de ads

Soporte: ${escapeHtml(config.ADMIN_EMAIL || 'admin@example.com')}`,

  HELP_UNAUTHORIZED: `📚 ${bold('Ayuda')}

1) Usa /miinfo
2) Envía tu ID al admin
3) Espera confirmación

Contacto: ${escapeHtml(config.ADMIN_EMAIL)}`,

  // ——— Errores ———
  ERROR_GENERIC: '⚠️ Ocurrió un error. Intenta de nuevo.',
  ERROR_WIREGUARD: (e) => `❌ Error WG: ${escapeHtml(String(e))}`,
  ERROR_OUTLINE: (e) => `❌ Error Outline: ${escapeHtml(String(e))}`,
  ERROR_LIST_CLIENTS: '❌ No se pudo obtener la lista.',
  ERROR_SERVER_STATUS: '⚠️ Algunos servicios no responden.',

  // ——— Admin (nuevas plantillas centralizadas) ———

  // Respuesta cuando un admin agrega un usuario
  ADMIN_USER_ADDED: (userId, userName, addedAt) =>
    `✅ ${bold('Usuario autorizado')}

ID: ${code(userId)}
Nombre: ${escapeHtml(userName || 'No especificado')}
Desde: ${escapeHtml(addedAt)}`,

  // Usuario removido
  ADMIN_USER_REMOVED: (userId) =>
    `🗑️ ${bold('Usuario removido')}

ID: ${code(userId)}
El acceso ha sido revocado.`,

  // Usuario suspendido
  ADMIN_USER_SUSPENDED: (userId) =>
    `⏸️ ${bold('Usuario suspendido')}

ID: ${code(userId)}
Para reactivar: ${code(`/react ${userId}`)}`,

  // Usuario reactivado
  ADMIN_USER_REACTIVATED: (userId) =>
    `▶️ ${bold('Usuario reactivado')}

ID: ${code(userId)}
Ya puede usar el bot.`,

  // Lista compacta de usuarios (se recibe arreglo y stats)
  ADMIN_USER_LIST: (users, stats) => {
    const header = `👥 ${bold('USUARIOS')} • Total: ${stats.total} • Activos: ${stats.active}\n\n`;
    const rows = users.map((u, i) => {
      const status = u.status === 'active' ? '✅' : '⏸️';
      const role = u.role === 'admin' ? '👑' : '👤';
      const name = escapeHtml(u.name || 'Sin nombre');
      return `${i + 1}. ${status} ${role} ${code(u.id)} • ${name}`;
    }).join('\n');
    return header + (rows || '<i>No hay usuarios</i>');
  },

  // Estadísticas compactas
  ADMIN_STATS: (stats, recentCount) =>
    `📊 ${bold('ESTADÍSTICAS')}

Total: ${stats.total}
Activos: ${stats.active}
Suspendidos: ${stats.suspended}
Admins: ${stats.admins}

Nuevos (24h): ${recentCount}`,

  // Broadcast - vista previa antes de confirmar
  BROADCAST_PREVIEW: (broadcastId, safeMessage, userCount, adminCount, total) =>
    `📢 ${bold('CONFIRMAR BROADCAST')}

Mensaje:
${safeMessage}

Destinatarios:
• Usuarios: ${userCount}
• Admins: ${adminCount}
• Total: ${total}

ID: ${broadcastId}`,

  // Resultado del broadcast
  BROADCAST_RESULT: (success, failed) =>
    `📢 ${bold('BROADCAST COMPLETADO')}

✅ Enviados: ${success}
❌ Fallidos: ${failed}`,

  // Ayuda de broadcast (compacta)
  BROADCAST_HELP: `📢 ${bold('Broadcast')}

Uso: ${code('/broadcast [mensaje]')}
Opciones: /sms, /templates`,

  // Mensaje directo enviado (confirmación)
  ADMIN_DIRECT_MSG_SENT: (targetId, targetName) =>
    `✅ ${bold('Mensaje enviado')}

ID: ${code(targetId)}
Para: ${escapeHtml(targetName || 'Sin nombre')}`,

  // Plantillas compactas
  ADMIN_TEMPLATES: () =>
    `📋 ${bold('PLANTILLAS')}
1) ${code('/broadcast 🎉 Bienvenida')}
2) ${code('/broadcast ⚠️ Mantenimiento [FECHA]')}
3) ${code('/broadcast 🎁 PROMO: ...')}`,

  // Notificaciones push simples (para sendDirectMessage / notify)
  NOTIFY_USER_APPROVED: (userName) =>
    `🎉 ${bold('¡Acceso aprobado!')}

Ahora puedes usar /start. Bienvenido${userName ? ` ${escapeHtml(userName)}` : ''}.`,

  NOTIFY_USER_REMOVED: () =>
    `⚠️ ${bold('Acceso revocado')}
Tu acceso ha sido removido. Contacta al admin si es un error.`,

  NOTIFY_USER_REACTIVATED: () =>
    `✅ ${bold('Acceso reactivado')}
Tu acceso ha sido restaurado. Usa /start para continuar.`,

  // ——— Comandos y utilidades ———
  UNKNOWN_COMMAND: (isAdmin) => {
    let msg = `⚠️ ${bold('Comando no válido')}\n\n${bold('Usuario:')}\n`;
    msg += USER_COMMANDS.map((cmd) => {
      const [c, d] = cmd.split(' - ');
      return `${code(c)} - ${escapeHtml(d)}\n`;
    }).join('');
    if (isAdmin) {
      msg += `\n👑 ${bold('Admin:')}\n`;
      msg += ADMIN_COMMANDS.map((cmd) => {
        const [c, d] = cmd.split(' - ');
        return `${code(c)} - ${escapeHtml(d)}\n`;
      }).join('');
    }
    return msg + `\nUsa ${code('/start')}`;
  },

  COMMANDS_LIST: (isAdmin) => {
    let msg = `📋 ${bold('Comandos disponibles')}\n\n`;
    msg += `👤 ${bold('Usuario:')}\n`;
    msg += USER_COMMANDS.map((cmd) => {
      const [c, d] = cmd.split(' - ');
      return `• ${code(c)}: ${escapeHtml(d)}\n`;
    }).join('');
    if (isAdmin) {
      msg += `\n👑 ${bold('Admin:')}\n`;
      msg += ADMIN_COMMANDS.map((cmd) => {
        const [c, d] = cmd.split(' - ');
        return `• ${code(c)}: ${escapeHtml(d)}\n`;
      }).join('');
    }
    return msg;
  },

  GENERIC_TEXT_PROMPT: (name) =>
    `👋 Hola ${escapeHtml(name)}

Crea tu VPN:
• WireGuard
• Outline`,

  // Export helper utilities if alguien las necesita (opcional)
  _helpers: {
    escapeHtml,
    bold,
    code,
    italic
  }
};

module.exports = messages;