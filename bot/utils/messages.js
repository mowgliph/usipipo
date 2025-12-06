// utils/messages.js
const config = require('../config/environment');
const constants = require('../config/constants');
const { escapeMarkdown, bold, italic, code } = require('./markdown');

// Definición de los comandos disponibles (extraídos de bot.instance.js)
const USER_COMMANDS = [
  '/start - Iniciar conversación/Ver menú principal',
  '/miinfo - Ver tus datos de Telegram (ID, etc.)',
  '/status - Comprobar tu estado de acceso y rol'
];

const ADMIN_COMMANDS = [
  '/ad [ID] [nombre] - Autorizar un nuevo usuario',
  '/rm [ID] - Quitar acceso a un usuario',
  '/sus [ID] - Suspender temporalmente el acceso',
  '/react [ID] - Reactivar un usuario suspendido',
  '/users - Listar todos los usuarios en el sistema',
  '/stats - Ver estadísticas de WireGuard y Outline',
  '/broadcast [mensaje] - Enviar un mensaje a todos los usuarios',
  '/sms [ID] [texto] - Enviar un mensaje directo a un usuario',
  '/templates - Mostrar plantillas de mensaje predefinidas'
  // Se omite /forceadmin por ser un comando de emergencia/configuración.
];

const messages = {
  // Mensajes de bienvenida
  WELCOME_AUTHORIZED: (userName) => `👋 ¡Hola \( {escapeMarkdown(userName)}! Bienvenido a \){bold('uSipipo VPN Manager')}

✅ Tienes acceso autorizado al sistema.

Selecciona una opción del menú:`,

  WELCOME_UNAUTHORIZED: (userName) => `👋 ¡Hola \( {escapeMarkdown(userName)}! Bienvenido a \){bold('uSipipo VPN Manager')}

⚠️ Actualmente ${bold('no tienes acceso autorizado')} a este servicio.

📋 Para solicitar acceso, necesitas enviar tu ${bold('ID de Telegram')} al administrador.

🔍 Usa el comando /miinfo para ver tus datos de Telegram.
📧 Envía tu ID al administrador: ${bold(escapeMarkdown(config.ADMIN_EMAIL || 'admin@example.com'))}`,

  // Mensajes de usuario
  USER_INFO: (user, isAuthorized) => {
    const firstName = escapeMarkdown(user.first_name || 'No disponible');
    const lastName = escapeMarkdown(user.last_name || 'No disponible');
    const username = user.username ? `@${escapeMarkdown(user.username)}` : 'No establecido';
    const languageCode = escapeMarkdown(user.language_code || 'No disponible');

    return `👤 ${bold('TUS DATOS DE TELEGRAM')}

🆔 \( {bold('ID:')} \){code(String(user.id))}
📝 \( {bold('Nombre:')} \){firstName}
📝 \( {bold('Apellido:')} \){lastName}
🔗 \( {bold('Username:')} \){username}
🌐 \( {bold('Idioma:')} \){languageCode}

${isAuthorized ? constants.STATUS.AUTHORIZED : constants.STATUS.UNAUTHORIZED}

📋 ${bold('Para solicitar acceso:')}
Envía tu \( {bold(`ID ( \){user.id})`)} al administrador en ${bold(escapeMarkdown(config.ADMIN_EMAIL || 'admin@example.com'))}`;
  },

  // Solicitud de acceso
  ACCESS_REQUEST_SENT: (user) => {
    const firstName = escapeMarkdown(user.first_name || 'No disponible');
    const username = user.username ? `@${escapeMarkdown(user.username)}` : 'No disponible';

    return `📧 ${bold('Solicitud registrada')}

Tu solicitud de acceso ha sido enviada al administrador.

📋 ${bold('Datos a compartir:')}
🆔 ID: ${code(String(user.id))}
👤 Nombre: ${firstName}
🔗 Username: ${username}

📮 Envía estos datos a: ${bold(escapeMarkdown(config.ADMIN_EMAIL || 'admin@example.com'))}

⏳ El administrador revisará tu solicitud y te agregará a la lista de usuarios permitidos.`;
  },

  ACCESS_REQUEST_ADMIN_NOTIFICATION: (user) => {
    const firstName = escapeMarkdown(user.first_name || '');
    const lastName = user.last_name ? escapeMarkdown(user.last_name) : '';
    const username = user.username ? `@${escapeMarkdown(user.username)}` : 'Sin username';
    const languageCode = escapeMarkdown(user.language_code || 'N/A');

    return `🔔 ${bold('NUEVA SOLICITUD DE ACCESO')}

👤 Usuario: \( {firstName} \){lastName}
🆔 ID: ${code(String(user.id))}
🔗 Username: ${username}
🌐 Idioma: ${languageCode}

📝 Para autorizar, agrega este ID a AUTHORIZED_USERS en tu .env:
${code(String(user.id))}`;
  },

  // Mensajes de acceso denegado
  ACCESS_DENIED: `⛔ ${bold('Acceso denegado')}

No tienes permisos para usar esta función.

Usa /miinfo para ver tu ID y solicitar acceso al administrador.`,

  ADMIN_ONLY: '⛔ Este comando es solo para administradores.',

  // VPN - WireGuard
  WIREGUARD_CREATING: '⏳ Generando configuración WireGuard, por favor espera...',

  WIREGUARD_SUCCESS: (clientIP) => `✅ ${bold('Configuración WireGuard creada')}

📍 IP asignada: ${code(clientIP)}
🔗 Endpoint: \( {code(` \){config.SERVER_IPV4}:${config.WIREGUARD_PORT}`)}

📱 Usa el QR code a continuación para configuración rápida en móvil.`,

  WIREGUARD_INSTRUCTIONS: `📖 ${bold('Instrucciones de conexión:')}

${bold('En móvil:')} Abre WireGuard app → "+" → Escanear QR
${bold('En PC:')} Importa el archivo .conf en WireGuard client

🔗 Descargas: ${constants.URLS.WIREGUARD_DOWNLOAD}`,

  // VPN - Outline
  OUTLINE_CREATING: '⏳ Generando clave de acceso Outline...',

  OUTLINE_SUCCESS: (accessKey) => `✅ ${bold('Clave Outline creada exitosamente')}

🔑 ID: ${code(accessKey.id)}
📱 Copia el siguiente enlace en tu app Outline:

${code(accessKey.accessUrl)}

🛡️ DNS con bloqueo de anuncios activado
📊 Límite de datos: 10GB/mes
🔗 Descarga Outline: ${constants.URLS.OUTLINE_DOWNLOAD}`,

  // Estado del servidor
  SERVER_STATUS: (outlineInfo) => `🖥️ ${bold('ESTADO DEL SERVIDOR uSipipo')}

📍 IP Pública: ${code(config.SERVER_IPV4)}
🔐 WireGuard Port: ${code(String(config.WIREGUARD_PORT))}
🌐 Outline Port: ${code(String(config.OUTLINE_API_PORT))}
🛡️ Pi-hole DNS: ${code(config.PIHOLE_DNS)}

✅ Todos los servicios operativos`,

  // Ayuda
  HELP_AUTHORIZED: `📚 ${bold('GUÍA DE USO - uSipipo VPN')}

${bold('WireGuard:')}
• VPN de alto rendimiento
• Ideal para uso general
• Requiere app específica

${bold('Outline:')}
• Fácil configuración
• Mejor para móviles
• Un clic para conectar

${bold('Pi-hole:')}
• Bloqueo automático de ads
• Protección anti-tracking
• Integrado en ambas VPNs

💬 ¿Problemas? Contacta: ${escapeMarkdown(config.ADMIN_EMAIL || 'admin@example.com')}`,

  HELP_UNAUTHORIZED: `📚 ${bold('AYUDA - uSipipo VPN')}

⚠️ No tienes acceso autorizado aún.

📋 ${bold('Pasos para obtener acceso:')}
1. Usa /miinfo para ver tu ID de Telegram
2. Envía tu ID al administrador: ${escapeMarkdown(config.ADMIN_EMAIL || 'admin@example.com')}
3. Espera la confirmación de acceso

💬 ¿Preguntas? Contacta: ${escapeMarkdown(config.ADMIN_EMAIL || 'admin@example.com')}`,

  // Errores
  ERROR_GENERIC: '⚠️ Ocurrió un error inesperado. Por favor intenta nuevamente.',
  ERROR_WIREGUARD: (error) => `❌ Error al crear configuración WireGuard: ${escapeMarkdown(String(error))}`,
  ERROR_OUTLINE: (error) => `❌ Error al crear clave Outline: ${escapeMarkdown(String(error))}`,
  ERROR_LIST_CLIENTS: '❌ Error al obtener lista de clientes',
  ERROR_SERVER_STATUS: '⚠️ Algunos servicios podrían no estar respondiendo',

  // Mensajes de administración
  USER_APPROVED: (userId, userName) => {
    const safeName = userName ? escapeMarkdown(userName) : 'No especificado';

    return `🎉 ${bold('¡Solicitud aprobada!')}

✅ El usuario ha sido autorizado:
🆔 ID: ${code(String(userId))}
👤 Nombre: ${safeName}

El usuario recibirá una notificación automática.`;
  },

  // Mensajes de comprobación de estado
  STATUS_NOT_REGISTERED: (user) => {
    const firstName = escapeMarkdown(user.first_name || 'Usuario');

    return `⛔ ${bold('Estado: NO REGISTRADO')}

👤 Usuario: ${firstName}
🆔 ID: ${code(String(user.id))}

📋 ${bold('No se encontró ninguna solicitud de acceso')}

💡 ${bold('Para solicitar acceso:')}
1. Presiona el botón "📧 Solicitar acceso"
2. Envía tu ID al administrador: ${bold(escapeMarkdown(config.ADMIN_EMAIL || 'admin@example.com'))}
3. Espera la aprobación

⏳ Una vez aprobado, podrás usar todos los servicios del bot.`;
  },

  STATUS_ACTIVE: (user, userData) => {
    const firstName = escapeMarkdown(user.first_name || 'Usuario');
    const addedDate = new Date(userData.addedAt).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
    const roleIcon = userData.role === 'admin' ? '👑' : '✅';
    const roleText = userData.role === 'admin' ? 'Administrador' : 'Usuario autorizado';

    return `\( {roleIcon} \){bold('Estado: ACTIVO')}

👤 Usuario: ${firstName}
🆔 ID: ${code(String(user.id))}
🎭 Rol: ${bold(roleText)}
📅 Autorizado desde: ${escapeMarkdown(addedDate)}

✅ ${bold('Tienes acceso completo a todos los servicios')}

🔐 Puedes crear configuraciones VPN
📊 Ver estadísticas del servidor
🛠️ Gestionar tus clientes activos

💡 Usa el menú principal para comenzar.`;
  },

  STATUS_SUSPENDED: (user, userData) => {
    const firstName = escapeMarkdown(user.first_name || 'Usuario');
    const suspendedDate = userData.suspendedAt
      ? new Date(userData.suspendedAt).toLocaleDateString('es-ES', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      : 'No disponible';

    return `⏸️ ${bold('Estado: SUSPENDIDO')}

👤 Usuario: ${firstName}
🆔 ID: ${code(String(user.id))}
📅 Suspendido desde: ${escapeMarkdown(suspendedDate)}

⚠️ ${bold('Tu acceso ha sido suspendido temporalmente')}

📧 Para más información, contacta al administrador:
${bold(escapeMarkdown(config.ADMIN_EMAIL || 'admin@example.com'))}

💡 Una vez reactivado, recibirás una notificación automática.`;
  },

  STATUS_UNKNOWN: (user) => {
    const firstName = escapeMarkdown(user.first_name || 'Usuario');

    return `❓ ${bold('Estado: DESCONOCIDO')}

👤 Usuario: ${firstName}
🆔 ID: ${code(String(user.id)))}

⚠️ ${bold('No se pudo determinar tu estado de acceso')}

📧 Por favor contacta al administrador:
${bold(escapeMarkdown(config.ADMIN_EMAIL || 'admin@example.com'))}

🔧 Proporciona tu ID de usuario para asistencia.`;
  },

  // Mensaje de Inicio del Sistema
  SYSTEM_STARTUP: (serverInfo, adminCount, userCount) => {
    const startTime = new Date().toLocaleString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });

    return `🚀 ${bold('SISTEMA INICIADO CORRECTAMENTE')}
━━━━━━━━━━━━━━━━━━━━━

📅 \( {bold('Fecha:')} \){escapeMarkdown(startTime)}

🖥️ ${bold('Estado del servidor:')}
• IP: ${code(serverInfo.ip)}
• Puerto WG: ${code(String(serverInfo.wgPort))}
• Puerto Outline: ${code(String(serverInfo.outlinePort))}

👥 ${bold('Base de usuarios:')}
• Administradores: ${adminCount}
• Usuarios totales: ${userCount}

✅ ${bold('Bot operativo y escuchando peticiones.')}`;
  },

  // Mensajes de Broadcast
  BROADCAST_HELP: `📢 ${bold('SISTEMA DE BROADCAST')}

${bold('Comandos disponibles:')}

• ${code('/broadcast [mensaje]')}
  Envía mensaje a todos los usuarios

• ${code('/sms [ID] [texto]')}
  Mensaje directo a un usuario

• ${code('/templates')}
  Muestra plantillas predefinidas

${bold('Opciones de envío:')}
• 📤 Todos los usuarios activos
• 👤 Solo usuarios regulares
• 👑 Solo administradores

💡 Los mensajes soportan formato Markdown.`,

  BROADCAST_SENT: (successCount, failedCount) => `✅ ${bold('Broadcast enviado')}

📊 Resultados:
• Exitosos: ${successCount}
• Fallidos: ${failedCount}`,

  BROADCAST_CANCELLED: '❌ Broadcast cancelado.',

  // Mensaje para comandos no reconocidos
  UNKNOWN_COMMAND: (isUserAdmin) => {
    let message = `⚠️ ${bold('Comando no reconocido')}

El comando que has enviado no se encuentra en la lista de comandos disponibles. Por favor, revisa la sintaxis.

${bold('Comandos de usuario:')}\n`;

    message += USER_COMMANDS.map(cmd => {
      const [command, description] = cmd.split(' - ');
      return `\( {code(command)} - \){escapeMarkdown(description)}\n`;
    }).join('');

    if (isUserAdmin) {
      message += `\n👑 ${bold('Comandos de administrador:')}\n`;
      message += ADMIN_COMMANDS.map(cmd => {
        const [command, description] = cmd.split(' - ');
        return `\( {code(command)} - \){escapeMarkdown(description)}\n`;
      }).join('');
    }

    message += `\n💡 Para más ayuda, usa el comando ${code('/start')}.`;
    return message;
  },

  // Nueva función para listar comandos
  COMMANDS_LIST: (isUserAdmin) => {
    let message = `📋 ${bold('LISTA DE COMANDOS DISPONIBLES')}\n`;

    // Comandos de usuario
    message += `👤 ${bold('Usuario regular:')}\n`;
    message += USER_COMMANDS.map(cmd => {
      const [command, description] = cmd.split(' - ');
      return `• \( {code(command)}: \){escapeMarkdown(description)}\n`;
    }).join('');

    // Comandos de admin (solo si es admin)
    if (isUserAdmin) {
      message += `\n👑 ${bold('Administrador:')}\n`;
      message += ADMIN_COMMANDS.map(cmd => {
        const [command, description] = cmd.split(' - ');
        return `• \( {code(command)}: \){escapeMarkdown(description)}\n`;
      }).join('');
    }

    message += `\n💡 ${italic('Toca cualquier comando para ejecutarlo.')}`;
    return message;
  },

  // Mensaje para texto genérico (no comando)
  GENERIC_TEXT_PROMPT: (userName) => {
    const safeName = escapeMarkdown(userName || 'usuario');

    return `👋 \( {bold('¡Hola')} \){safeName},

Soy ${bold('uSipipo VPN Bot')}, tu asistente de autogestión VPN.

¿Aún no tienes una configuración VPN?
Selecciona el tipo de servicio que deseas crear a continuación (WireGuard o Outline).`;
  },

  // Mensaje de ayuda para admin (unificado con ADMIN_COMMANDS)
  ADMIN_HELP: `👑 ${bold('COMANDOS DE ADMINISTRADOR')}

${bold('Gestión de usuarios:')}
• ${code('/ad [ID] [nombre]')} - Autorizar usuario
• ${code('/rm [ID]')} - Quitar acceso
• ${code('/sus [ID]')} - Suspender temporalmente
• ${code('/react [ID]')} - Reactivar usuario

${bold('Información:')}
• ${code('/users')} - Lista completa
• ${code('/stats')} - Estadísticas del sistema

💡 El ID se obtiene con /miinfo`
};

module.exports = messages;