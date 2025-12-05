// utils/messages.js
const config = require('../config/environment');
const constants = require('../config/constants');
const { escapeMarkdown, bold, code } = require('./markdown');

module.exports = {
  // Mensajes de bienvenida
  WELCOME_AUTHORIZED: (userName) => 
    `👋 ¡Hola ${escapeMarkdown(userName)}! Bienvenido a ${bold('uSipipo VPN Manager')}\n\n` +
    `✅ Tienes acceso autorizado al sistema.\n\n` +
    `Selecciona una opción del menú:`,

  WELCOME_UNAUTHORIZED: (userName) =>
    `👋 ¡Hola ${escapeMarkdown(userName)}! Bienvenido a ${bold('uSipipo VPN Manager')}\n\n` +
    `⚠️ Actualmente ${bold('no tienes acceso autorizado')} a este servicio.\n\n` +
    `📋 Para solicitar acceso, necesitas enviar tu ${bold('ID de Telegram')} al administrador.\n\n` +
    `🔍 Usa el comando /miinfo para ver tus datos de Telegram.\n` +
    `📧 Envía tu ID al administrador: ${bold(config.ADMIN_EMAIL)}`,

  // Mensajes de usuario
  USER_INFO: (user, isAuthorized) => {
    const firstName = escapeMarkdown(user.first_name || 'No disponible');
    const lastName = escapeMarkdown(user.last_name || 'No disponible');
    const username = user.username ? '@' + escapeMarkdown(user.username) : 'No establecido';
    const languageCode = escapeMarkdown(user.language_code || 'No disponible');
    
    return `👤 ${bold('TUS DATOS DE TELEGRAM')}\n\n` +
      `🆔 ${bold('ID:')} ${code(user.id)}\n` +
      `📝 ${bold('Nombre:')} ${firstName}\n` +
      `📝 ${bold('Apellido:')} ${lastName}\n` +
      `🔗 ${bold('Username:')} ${username}\n` +
      `🌐 ${bold('Idioma:')} ${languageCode}\n\n` +
      `${isAuthorized ? constants.STATUS.AUTHORIZED : constants.STATUS.UNAUTHORIZED}\n\n` +
      `📋 ${bold('Para solicitar acceso:')}\n` +
      `Envía tu ${bold('ID (' + user.id + ')')} al administrador en ${bold(config.ADMIN_EMAIL)}`;
  },

  // Solicitud de acceso
  ACCESS_REQUEST_SENT: (user) => {
    const firstName = escapeMarkdown(user.first_name);
    const username = user.username ? '@' + escapeMarkdown(user.username) : 'No disponible';
    
    return `📧 ${bold('Solicitud registrada')}\n\n` +
      `Tu solicitud de acceso ha sido enviada al administrador.\n\n` +
      `📋 ${bold('Datos a compartir:')}\n` +
      `🆔 ID: ${code(user.id)}\n` +
      `👤 Nombre: ${firstName}\n` +
      `🔗 Username: ${username}\n\n` +
      `📮 Envía estos datos a: ${bold(config.ADMIN_EMAIL)}\n\n` +
      `⏳ El administrador revisará tu solicitud y te agregará a la lista de usuarios permitidos.`;
  },

  ACCESS_REQUEST_ADMIN_NOTIFICATION: (user) => {
    const firstName = escapeMarkdown(user.first_name);
    const lastName = user.last_name ? escapeMarkdown(user.last_name) : '';
    const username = user.username ? '@' + escapeMarkdown(user.username) : 'Sin username';
    const languageCode = escapeMarkdown(user.language_code || 'N/A');
    
    return `🔔 ${bold('NUEVA SOLICITUD DE ACCESO')}\n\n` +
      `👤 Usuario: ${firstName} ${lastName}\n` +
      `🆔 ID: ${code(user.id)}\n` +
      `🔗 Username: ${username}\n` +
      `🌐 Idioma: ${languageCode}\n\n` +
      `📝 Para autorizar, agrega este ID a AUTHORIZED_USERS en tu .env:\n` +
      `${code(user.id)}`;
  },


  // Mensajes de acceso denegado
  ACCESS_DENIED: 
    '⛔ **Acceso denegado**\n\n' +
    'No tienes permisos para usar esta función.\n\n' +
    'Usa /miinfo para ver tu ID y solicitar acceso al administrador.',

  ADMIN_ONLY:
    '⛔ Este comando es solo para administradores.',

  // VPN - WireGuard
  WIREGUARD_CREATING: '⏳ Generando configuración WireGuard, por favor espera...',

  WIREGUARD_SUCCESS: (clientIP) =>
    `✅ ${bold('Configuración WireGuard creada')}\n\n` +
    `📍 IP asignada: ${code(clientIP)}\n` +
    `🔗 Endpoint: ${code(config.SERVER_IPV4 + ':' + config.WIREGUARD_PORT)}\n\n` +
    `📱 Usa el QR code a continuación para configuración rápida en móvil.`,

  WIREGUARD_INSTRUCTIONS:
    '📖 **Instrucciones de conexión:**\n\n' +
    '**En móvil:** Abre WireGuard app → "+" → Escanear QR\n' +
    '**En PC:** Importa el archivo .conf en WireGuard client\n\n' +
    `🔗 Descargas: ${constants.URLS.WIREGUARD_DOWNLOAD}`,

  // VPN - Outline
  OUTLINE_CREATING: '⏳ Generando clave de acceso Outline...',

  OUTLINE_SUCCESS: (accessKey) =>
    `✅ ${bold('Clave Outline creada exitosamente')}\n\n` +
    `🔑 ID: ${code(accessKey.id)}\n` +
    `📱 Copia el siguiente enlace en tu app Outline:\n\n` +
    `${code(accessKey.accessUrl)}\n\n` +
    `🛡️ DNS con bloqueo de anuncios activado\n` +
    `📊 Límite de datos: 10GB/mes` +
    `🔗 Descarga Outline: ${constants.URLS.OUTLINE_DOWNLOAD}`,

  // Estado del servidor
  SERVER_STATUS: (outlineInfo) =>
    `🖥️ ${bold('ESTADO DEL SERVIDOR uSipipo')}\n\n` +
    `📍 IP Pública: ${code(config.SERVER_IPV4)}\n` +
    `🔐 WireGuard Port: ${code(config.WIREGUARD_PORT)}\n` +
    `🌐 Outline Port: ${code(config.OUTLINE_API_PORT)}\n` +
    `🛡️ Pi-hole DNS: ${code(config.PIHOLE_DNS)}\n\n` +
    `✅ Todos los servicios operativos`,


  // Ayuda
  HELP_AUTHORIZED:
    `📚 **GUÍA DE USO - uSipipo VPN**\n\n` +
    `**WireGuard:**\n` +
    `• VPN de alto rendimiento\n` +
    `• Ideal para uso general\n` +
    `• Requiere app específica\n\n` +
    `**Outline:**\n` +
    `• Fácil configuración\n` +
    `• Mejor para móviles\n` +
    `• Un clic para conectar\n\n` +
    `**Pi-hole:**\n` +
    `• Bloqueo automático de ads\n` +
    `• Protección anti-tracking\n` +
    `• Integrado en ambas VPNs\n\n` +
    `💬 ¿Problemas? Contacta: ${config.ADMIN_EMAIL}`,

  HELP_UNAUTHORIZED:
    `📚 **AYUDA - uSipipo VPN**\n\n` +
    `⚠️ No tienes acceso autorizado aún.\n\n` +
    `📋 **Pasos para obtener acceso:**\n` +
    `1. Usa /miinfo para ver tu ID de Telegram\n` +
    `2. Envía tu ID al administrador: ${config.ADMIN_EMAIL}\n` +
    `3. Espera la confirmación de acceso\n\n` +
    `💬 ¿Preguntas? Contacta: ${config.ADMIN_EMAIL}`,

  // Errores
  ERROR_GENERIC: '⚠️ Ocurrió un error inesperado. Por favor intenta nuevamente.',
  ERROR_WIREGUARD: (error) => `❌ Error al crear configuración WireGuard: ${escapeMarkdown(error)}`,
  ERROR_OUTLINE: (error) => `❌ Error al crear clave Outline: ${escapeMarkdown(error)}`,
  ERROR_LIST_CLIENTS: '❌ Error al obtener lista de clientes',
  ERROR_SERVER_STATUS: '⚠️ Algunos servicios podrían no estar respondiendo',
  
  // Mensajes de administración
  USER_APPROVED: (userId, userName) => {
    const safeName = userName ? escapeMarkdown(userName) : 'No especificado';
    
    return `🎉 ${bold('¡Solicitud Aprobada!')}\n\n` +
      `✅ El usuario ha sido autorizado:\n` +
      `🆔 ID: ${code(userId)}\n` +
      `👤 Nombre: ${safeName}\n\n` +
      `El usuario recibirá una notificación automática.`;
  },
  
  // Mensajes de comprobación de estado
  STATUS_NOT_REGISTERED: (user) => {
    const firstName = escapeMarkdown(user.first_name);
  
    return `⛔ ${bold('Estado: NO REGISTRADO')}\n\n` +
      `👤 Usuario: ${firstName}\n` +
      `🆔 ID: ${code(user.id)}\n\n` +
      `📋 ${bold('No se encontró ninguna solicitud de acceso')}\n\n` +
      `💡 ${bold('Para solicitar acceso:')}\n` +
      `1. Presiona el botón "📧 Solicitar acceso"\n` +
      `2. Envía tu ID al administrador: ${bold(config.ADMIN_EMAIL)}\n` +
      `3. Espera la aprobación\n\n` +
      `⏳ Una vez aprobado, podrás usar todos los servicios del bot.`;
  },

  STATUS_ACTIVE: (user, userData) => {
    const firstName = escapeMarkdown(user.first_name);
    const addedDate = new Date(userData.addedAt).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
    const roleIcon = userData.role === 'admin' ? '👑' : '✅';
    const roleText = userData.role === 'admin' ? 'Administrador' : 'Usuario Autorizado';
  
    return `${roleIcon} ${bold('Estado: ACTIVO')}\n\n` +
      `👤 Usuario: ${firstName}\n` +
      `🆔 ID: ${code(user.id)}\n` +
      `🎭 Rol: ${bold(roleText)}\n` +
      `📅 Autorizado desde: ${escapeMarkdown(addedDate)}\n\n` +
      `✅ ${bold('Tienes acceso completo a todos los servicios')}\n\n` +
      `🔐 Puedes crear configuraciones VPN\n` +
      `📊 Ver estadísticas del servidor\n` +
      `🛠️ Gestionar tus clientes activos\n\n` +
      `💡 Usa el menú principal para comenzar.`;
  },

  STATUS_SUSPENDED: (user, userData) => {
    const firstName = escapeMarkdown(user.first_name);
    const suspendedDate = userData.suspendedAt 
      ? new Date(userData.suspendedAt).toLocaleDateString('es-ES', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      : 'No disponible';
  
    return `⏸️ ${bold('Estado: SUSPENDIDO')}\n\n` +
      `👤 Usuario: ${firstName}\n` +
      `🆔 ID: ${code(user.id)}\n` +
      `📅 Suspendido desde: ${escapeMarkdown(suspendedDate)}\n\n` +
      `⚠️ ${bold('Tu acceso ha sido suspendido temporalmente')}\n\n` +
      `📧 Para más información, contacta al administrador:\n` +
      `${bold(config.ADMIN_EMAIL)}\n\n` +
      `💡 Una vez reactivado, recibirás una notificación automática.`;
  },

  STATUS_UNKNOWN: (user) => {
    const firstName = escapeMarkdown(user.first_name);
  
    return `❓ ${bold('Estado: DESCONOCIDO')}\n\n` +
      `👤 Usuario: ${firstName}\n` +
      `🆔 ID: ${code(user.id)}\n\n` +
      `⚠️ ${bold('No se pudo determinar tu estado de acceso')}\n\n` +
      `📧 Por favor contacta al administrador:\n` +
      `${bold(config.ADMIN_EMAIL)}\n\n` +
      `🔧 Proporciona tu ID de usuario para asistencia.`;
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

    return `🚀 ${bold('SISTEMA INICIADO CORRECTAMENTE')}\n` +
      `━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `📅 ${bold('Fecha:')} ${startTime}\n\n` +
      `🖥️ ${bold('Estado del Servidor:')}\n` +
      `• IP: ${code(serverInfo.ip)}\n` +
      `• Puerto WG: ${code(serverInfo.wgPort)}\n` +
      `• Puerto Outline: ${code(serverInfo.outlinePort)}\n\n` +
      `👥 ${bold('Base de Usuarios:')}\n` +
      `• Administradores: ${adminCount}\n` +
      `• Usuarios Totales: ${userCount}\n\n` +
      `✅ ${bold('Bot operativo y escuchando peticiones.')}`;
  },
  
  // Mensajes de Broadcast
  BROADCAST_HELP:
    `📢 ${bold('SISTEMA DE BROADCAST')}\n\n` +
    `${bold('Comandos disponibles:')}\n\n` +
    `• ${code('/broadcast [mensaje]')}\n` +
    `  Envía mensaje a todos los usuarios\n\n` +
    `• ${code('/mensaje [ID] [texto]')}\n` +
    `  Mensaje directo a un usuario\n\n` +
    `• ${code('/plantillas')}\n` +
    `  Muestra plantillas predefinidas\n\n` +
    `${bold('Opciones de envío:')}\n` +
    `• 📤 Todos los usuarios activos\n` +
    `• 👤 Solo usuarios regulares\n` +
    `• 👑 Solo administradores\n\n` +
    `💡 Los mensajes soportan formato Markdown.`,

  BROADCAST_SENT: (successCount, failedCount) =>
    `✅ ${bold('Broadcast enviado')}\n\n` +
    `📊 Resultados:\n` +
    `• Exitosos: ${successCount}\n` +
    `• Fallidos: ${failedCount}`,

  BROADCAST_CANCELLED: 
    '❌ Broadcast cancelado.',
    
  ADMIN_HELP:
    `👑 **COMANDOS DE ADMINISTRADOR**\n\n` +
    `**Gestión de usuarios:**\n` +
    `• \`/agregar [ID] [nombre]\` - Autorizar usuario\n` +
    `• \`/remover [ID]\` - Quitar acceso\n` +
    `• \`/suspender [ID]\` - Suspender temporalmente\n` +
    `• \`/reactivar [ID]\` - Reactivar usuario\n\n` +
    `**Información:**\n` +
    `• \`/usuarios\` - Lista completa\n` +
    `• \`/stats\` - Estadísticas del sistema\n\n` +
    `💡 El ID se obtiene con /miinfo`
};
