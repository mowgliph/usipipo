'use strict';

const config = require('../config/environment');
const constants = require('../config/constants');
// 👇 Asegúrate de que este archivo sea el formatters.js del paso anterior
//    o que exporte correctamente escapeMarkdown, bold, code.
const { escapeMarkdown, bold, code, italic } = require('../utils/formatters');

// ============================================================================
// 📋 LISTA DE COMANDOS (Visualización limpia)
// ============================================================================
const USER_COMMANDS = [
  '/start    - 🏠 Menú Principal',
  '/miinfo   - 👤 Mi Cuenta y Estado',
  '/status   - 📡 Estado del Servidor',
  '/help     - 🆘 Soporte y Ayuda'
];

const ADMIN_COMMANDS = [
  '/users    - 👥 Gestión de Usuarios',
  '/stats    - 📊 Métricas del Sistema',
  '/broadcast - 📢 Mensaje Global',
  '/add [ID] - ✅ Autorizar Usuario',
  '/rm [ID]  - 🗑 Revocar Acceso'
];

// ============================================================================
// 💬 MESSAGES — Tono Profesional & MarkdownV2 Seguro
// ============================================================================

const messages = {

  // ------------------------------------------------------------------------
  // 🟢 BIENVENIDA & AUTENTICACIÓN
  // ------------------------------------------------------------------------
  
  WELCOME_AUTHORIZED: (name) =>
    `👋 Hola, ${bold(name)}\n\n` +
    `Bienvenido al ecosistema ${bold('uSipipo VPN')}\\.\n` +
    `Su conexión segura está lista para ser configurada\\.\n\n` +
    `👇 *Seleccione una opción del menú:*`,

  WELCOME_UNAUTHORIZED: (name) =>
    `🔒 ${bold('Acceso Restringido')}\n\n` +
    `Estimado ${escapeMarkdown(name)}, su cuenta aún no tiene permisos para utilizar este servicio VPN\\.\n\n` +
    `📂 *Para solicitar acceso:*\n` +
    `1️⃣ Copie su ID de usuario\\.\n` +
    `2️⃣ Envíelo al administrador del sistema\\.\n\n` +
    `👤 Admin: ${code(config.ADMIN_ID || 'No definido')}`,

  // ------------------------------------------------------------------------
  // 👤 PERFIL DE USUARIO
  // ------------------------------------------------------------------------
  
  USER_INFO: (user, isAuth) => {
    const statusIcon = isAuth ? '🟢' : '🔴';
    const statusText = isAuth ? 'Activo' : 'Pendiente';
    const username = user.username ? `@${escapeMarkdown(user.username)}` : italic('No configurado');

    return (
      `👤 ${bold('Perfil de Usuario')}\n` +
      `━━━━━━━━━━━━━━━━━━\n` +
      `🆔 ID: ${code(user.id)}\n` +
      `👤 Nombre: ${escapeMarkdown(user.first_name || 'Sin nombre')}\n` +
      `💬 Alias: ${username}\n` +
      `🛡 Estado: ${statusIcon} ${bold(statusText)}\n` +
      `━━━━━━━━━━━━━━━━━━`
    );
  },

  // ------------------------------------------------------------------------
  // 📨 SOLICITUDES
  // ------------------------------------------------------------------------

  ACCESS_REQUEST_SENT: (user) =>
    `📤 ${bold('Solicitud Registrada')}\n\n` +
    `Hemos notificado al administrador sobre su petición de acceso\\.\n\n` +
    `🆔 Su ID: ${code(user.id)}\n` +
    `⏳ Por favor, espere la confirmación\\...`,

  ACCESS_REQUEST_ADMIN_NOTIFICATION: (user) => {
    const name = escapeMarkdown(user.first_name || 'Anónimo');
    const username = user.username ? `@${escapeMarkdown(user.username)}` : 'N/A';

    return (
      `🔔 ${bold('Nueva Solicitud de Acceso')}\n` +
      `━━━━━━━━━━━━━━━━━━\n` +
      `👤 Usuario: ${name}\n` +
      `🔗 Alias: ${username}\n` +
      `🆔 ID: ${code(user.id)}\n\n` +
      `👇 *Acción requerida:*`
    );
  },

  ACCESS_DENIED: `⛔ ${bold('Acceso Denegado')}\nNo tiene permisos para ejecutar esta acción\\.`,
  ADMIN_ONLY: `🛡 ${bold('Seguridad')}\nEste comando es exclusivo para administradores\\.`,

  // ------------------------------------------------------------------------
  // 🔐 SERVICIOS VPN (WireGuard & Outline)
  // ------------------------------------------------------------------------

  WIREGUARD_CREATING: `⚙️ ${italic('Provisionando túnel WireGuard, por favor espere...')}`,

  WIREGUARD_SUCCESS: (ip) =>
    `🔐 ${bold('WireGuard Configurado')}\n\n` +
    `Su túnel cifrado ha sido generado exitosamente\\.\n` +
    `━━━━━━━━━━━━━━━━━━\n` +
    `💻 IP Interna: ${code(ip)}\n` +
    `🌐 Endpoint: ${code(`${config.SERVER_IP}:${config.WG_SERVER_PORT}`)}\n` +
    `━━━━━━━━━━━━━━━━━━\n\n` +
    `📲 *Instrucciones:*\n` +
    `Descargue el archivo adjunto o escanee el código QR desde la App oficial\\.`,

  ERROR_WIREGUARD: (e) => 
    `❌ ${bold('Error de Provisionamiento')}\n` +
    `No se pudo generar la configuración WireGuard\\.\n` +
    `Error: ${code(truncate(String(e), 100))}`,

  OUTLINE_CREATING: `⚙️ ${italic('Generando llave de acceso Outline...')}`,

  OUTLINE_SUCCESS: (key) =>
    `🌐 ${bold('Outline Access Key')}\n\n` +
    `Copie la siguiente clave de acceso para iniciar su conexión segura:\n\n` +
    `${code(key.accessUrl)}\n\n` +
    `ℹ️ _Toque la clave para copiarla automáticamente_\\.`,

  ERROR_OUTLINE: (e) => 
    `❌ ${bold('Error de Outline')}\n` +
    `El servidor Shadowbox no respondió correctamente\\.\n` +
    `Detalle: ${code(truncate(String(e), 100))}`,

  // ------------------------------------------------------------------------
  // 🖥 ESTADO DEL SISTEMA
  // ------------------------------------------------------------------------

  SERVER_STATUS: (info) => {
    // Asumimos que 'info' viene del OutlineService.getServerInfo refactorizado
    return (
      `🖥 ${bold('Estado del Sistema')}\n` +
      `━━━━━━━━━━━━━━━━━━\n` +
      `📍 IP Pública: ${code(config.SERVER_IPV4)}\n` +
      `🛡 Versión: ${escapeMarkdown(info.version || 'v1.0')}\n` +
      `👥 Usuarios VPN: ${code(info.totalKeys || 0)}\n` +
      `🔌 Puertos: ${code(config.WG_SERVER_PORT)} (WG) / ${code(config.OUTLINE_API_PORT)} (API)\n` +
      `━━━━━━━━━━━━━━━━━━\n` +
      `✅ Todos los servicios operativos\\.`
    );
  },

  ERROR_SERVER_STATUS: `⚠️ ${bold('Conexión Fallida')}\nNo se pudo establecer conexión con el servidor de gestión\\.`,

  // ------------------------------------------------------------------------
  // 📚 AYUDA Y SOPORTE
  // ------------------------------------------------------------------------

  HELP_AUTHORIZED:
    `📚 ${bold('Centro de Ayuda')}\n\n` +
    `🟢 ${bold('WireGuard')}: Protocolo recomendado para máxima velocidad y estabilidad (Streaming, Gaming)\\.\n\n` +
    `🔵 ${bold('Outline')}: Protocolo recomendado para alta censura o redes restrictivas (Oficinas, Universidades)\\.\n\n` +
    `🆘 *¿Problemas de conexión?*\n` +
    `Contacte a soporte técnico: ${code('@' + (config.ADMIN_USERNAME || 'Admin'))}`,

  HELP_UNAUTHORIZED:
    `❓ ${bold('¿Cómo obtengo acceso?')}\n\n` +
    `Este es un servicio privado\\. Para utilizarlo, debe solicitar una invitación al administrador del sistema\\.\n\n` +
    `Use el comando /miinfo para obtener sus credenciales de registro\\.`,

  // ------------------------------------------------------------------------
  // 👑 PANEL DE ADMINISTRADOR
  // ------------------------------------------------------------------------

  ADMIN_USER_ADDED: (id, name) =>
    `✅ ${bold('Usuario Autorizado')}\n` +
    `El usuario ${escapeMarkdown(name)} (${code(id)}) ha sido añadido a la lista blanca\\.`,

  ADMIN_USER_REMOVED: (id) => 
    `🗑 ${bold('Usuario Revocado')}\n` +
    `Se han eliminado los accesos para el ID ${code(id)}\\.`,

  ADMIN_STATS: (stats) =>
    `📊 ${bold('Métricas en Tiempo Real')}\n` +
    `━━━━━━━━━━━━━━━━━━\n` +
    `👥 Totales: ${code(stats.total)}\n` +
    `🟢 Activos: ${code(stats.active)}\n` +
    `⛔ Suspendidos: ${code(stats.suspended)}\n` +
    `👑 Admins: ${code(stats.admins)}\n` +
    `━━━━━━━━━━━━━━━━━━`,

  BROADCAST_PREVIEW: (msg, count) =>
    `📢 ${bold('Confirmación de Difusión')}\n\n` +
    `📜 *Mensaje:*\n${italic(msg)}\n\n` +
    `👥 *Destinatarios:* ${count} usuarios\n\n` +
    `¿Desea proceder con el envío?`,

  BROADCAST_RESULT: (success, failed) =>
    `📬 ${bold('Difusión Finalizada')}\n` +
    `✅ Entregados: ${success}\n` +
    `❌ Fallidos: ${failed}`,

  // ------------------------------------------------------------------------
  // ⚠️ ERRORES GENÉRICOS
  // ------------------------------------------------------------------------

  UNKNOWN_COMMAND: (isAdmin) => {
    let msg = `🤔 ${bold('Comando no reconocido')}\n\n`;
    msg += `Use el menú interactivo o pruebe uno de los siguientes:\n\n`;
    msg += USER_COMMANDS.map(c => `• ${escapeMarkdown(c)}`).join('\n');
    
    if (isAdmin) {
        msg += `\n\n🛠 ${bold('Admin Panel:')}\n`;
        msg += ADMIN_COMMANDS.map(c => `• ${escapeMarkdown(c)}`).join('\n');
    }
    return msg;
  },
  
  // Helpers internos para compatibilidad
  _helpers: { escapeMarkdown, bold, code, italic }
};

/**
 * Helper simple para recortar strings largos en mensajes de error
 */
function truncate(str, n){
  return (str.length > n) ? str.substr(0, n-1) + '...' : str;
}

module.exports = messages;
