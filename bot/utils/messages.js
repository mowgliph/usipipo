// utils/messages.js
const config = require('../config/environment');
const constants = require('../config/constants');

module.exports = {
  // Mensajes de bienvenida
  WELCOME_AUTHORIZED: (userName) => 
    `👋 ¡Hola ${userName}! Bienvenido a **uSipipo VPN Manager**\n\n` +
    `✅ Tienes acceso autorizado al sistema.\n\n` +
    `Selecciona una opción del menú:`,

  WELCOME_UNAUTHORIZED: (userName) =>
    `👋 ¡Hola ${userName}! Bienvenido a **uSipipo VPN Manager**\n\n` +
    `⚠️ Actualmente **no tienes acceso autorizado** a este servicio.\n\n` +
    `📋 Para solicitar acceso, necesitas enviar tu **ID de Telegram** al administrador.\n\n` +
    `🔍 Usa el comando /miinfo para ver tus datos de Telegram.\n` +
    `📧 Envía tu ID al administrador: **${config.ADMIN_EMAIL}**`,

  // Mensajes de usuario
  USER_INFO: (user, isAuthorized) => 
    `👤 **TUS DATOS DE TELEGRAM**\n\n` +
    `🆔 **ID:** \`${user.id}\`\n` +
    `📝 **Nombre:** ${user.first_name || 'No disponible'}\n` +
    `📝 **Apellido:** ${user.last_name || 'No disponible'}\n` +
    `🔗 **Username:** ${user.username ? '@' + user.username : 'No establecido'}\n` +
    `🌐 **Idioma:** ${user.language_code || 'No disponible'}\n\n` +
    `${isAuthorized ? constants.STATUS.AUTHORIZED : constants.STATUS.UNAUTHORIZED}\n\n` +
    `📋 **Para solicitar acceso:**\n` +
    `Envía tu **ID (${user.id})** al administrador en **${config.ADMIN_EMAIL}**`,

  // Solicitud de acceso
  ACCESS_REQUEST_SENT: (user) =>
    `📧 **Solicitud registrada**\n\n` +
    `Tu solicitud de acceso ha sido enviada al administrador.\n\n` +
    `📋 **Datos a compartir:**\n` +
    `🆔 ID: \`${user.id}\`\n` +
    `👤 Nombre: ${user.first_name}\n` +
    `🔗 Username: ${user.username ? '@' + user.username : 'No disponible'}\n\n` +
    `📮 Envía estos datos a: **${config.ADMIN_EMAIL}**\n\n` +
    `⏳ El administrador revisará tu solicitud y te agregará a la lista de usuarios permitidos.`,

  ACCESS_REQUEST_ADMIN_NOTIFICATION: (user) =>
    `🔔 **NUEVA SOLICITUD DE ACCESO**\n\n` +
    `👤 Usuario: ${user.first_name} ${user.last_name || ''}\n` +
    `🆔 ID: \`${user.id}\`\n` +
    `🔗 Username: ${user.username ? '@' + user.username : 'Sin username'}\n` +
    `🌐 Idioma: ${user.language_code || 'N/A'}\n\n` +
    `📝 Para autorizar, agrega este ID a AUTHORIZED_USERS en tu .env:\n` +
    `\`${user.id}\``,

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
    `✅ **Configuración WireGuard creada**\n\n` +
    `📍 IP asignada: \`${clientIP}\`\n` +
    `🔗 Endpoint: \`${config.SERVER_IPV4}:${config.WIREGUARD_PORT}\`\n\n` +
    `📱 Usa el QR code a continuación para configuración rápida en móvil.`,

  WIREGUARD_INSTRUCTIONS:
    '📖 **Instrucciones de conexión:**\n\n' +
    '**En móvil:** Abre WireGuard app → "+" → Escanear QR\n' +
    '**En PC:** Importa el archivo .conf en WireGuard client\n\n' +
    `🔗 Descargas: ${constants.URLS.WIREGUARD_DOWNLOAD}`,

  // VPN - Outline
  OUTLINE_CREATING: '⏳ Generando clave de acceso Outline...',

  OUTLINE_SUCCESS: (accessKey) =>
    `✅ **Clave Outline creada exitosamente**\n\n` +
    `🔑 ID: \`${accessKey.id}\`\n` +
    `📱 Copia el siguiente enlace en tu app Outline:\n\n` +
    `\`\`\`\n${accessKey.accessUrl}\n\`\`\`\n\n` +
    `🛡️ DNS con bloqueo de anuncios activado\n` +
    `📊 Límite de datos: 10GB/mes\n\n` +
    `🔗 Descarga Outline: ${constants.URLS.OUTLINE_DOWNLOAD}`,

  // Estado del servidor
  SERVER_STATUS: (outlineInfo) =>
    `🖥️ **ESTADO DEL SERVIDOR uSipipo**\n\n` +
    `📍 IP Pública: \`${config.SERVER_IPV4}\`\n` +
    `🔐 WireGuard Port: \`${config.WIREGUARD_PORT}\`\n` +
    `🌐 Outline Port: \`${config.OUTLINE_API_PORT}\`\n` +
    `🛡️ Pi-hole DNS: \`${config.PIHOLE_DNS}\`\n\n` +
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
  ERROR_WIREGUARD: (error) => `❌ Error al crear configuración WireGuard: ${error}`,
  ERROR_OUTLINE: (error) => `❌ Error al crear clave Outline: ${error}`,
  ERROR_LIST_CLIENTS: '❌ Error al obtener lista de clientes',
  ERROR_SERVER_STATUS: '⚠️ Algunos servicios podrían no estar respondiendo',
  
  // Mensajes de administración
  USER_APPROVED: (userId, userName) =>
    `🎉 **¡Solicitud Aprobada!**\n\n` +
    `✅ El usuario ha sido autorizado:\n` +
    `🆔 ID: \`${userId}\`\n` +
    `👤 Nombre: ${userName || 'No especificado'}\n\n` +
    `El usuario recibirá una notificación automática.`,
    
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
