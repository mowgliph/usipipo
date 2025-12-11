'use strict';

/**
 * ============================================================================
 * 🚀 START MESSAGES - uSipipo VPN Bot
 * ============================================================================
 * Mensajes específicos para el comando /start
 * Usa markdown V1 para máxima compatibilidad
 * ============================================================================
 */

const markdown = require('../../core/utils/markdown');
const constants = require('../../config/constants');

module.exports = {
  /**
   * Mensaje de bienvenida para usuarios no autorizados
   */
  WELCOME_UNAUTHORIZED: ({ userName = 'Usuario', userId }) => {
    return `${constants.EMOJI.SHIELD} *¡Hola ${userName}!*\n\n` +
           `Bienvenido al *uSipipo VPN Manager*.\n\n` +
           `${markdown.bold('Tu ID:')} ${markdown.code(userId)}\n\n` +
           `🔒 *Estado:* ${markdown.italic('Esperando autorización')}\n` +
           `📋 *Acción:* Se ha enviado una solicitud de acceso al administrador.\n\n` +
           `⏳ Por favor, espera a que un administrador apruebe tu acceso.\n` +
           `📬 Recibirás una notificación cuando seas autorizado.\n\n` +
           `${markdown.italic('Gracias por tu paciencia.')}`;
  },

  /**
   * Mensaje de bienvenida para usuarios autorizados
   */
  WELCOME_AUTHORIZED: ({ userName = 'Usuario', userId, isAdmin = false }) => {
    const role = isAdmin ? '👑 Administrador' : '👤 Usuario';
    
    return `${constants.EMOJI.ROCKET} *¡Bienvenido de nuevo ${userName}!*\n\n` +
           `*uSipipo VPN Manager* - Panel de control\n\n` +
           `${markdown.bold('Tu ID:')} ${markdown.code(userId)}\n` +
           `${markdown.bold('Rol:')} ${role}\n` +
           `${markdown.bold('Estado:')} ${constants.EMOJI.CHECK} Autorizado\n\n` +
           `📊 *Comandos disponibles:*\n` +
           `${constants.EMOJI.SMALL_BLUE_DIAMOND} ${markdown.code('/help')} - Muestra ayuda\n` +
           `${constants.EMOJI.SMALL_BLUE_DIAMOND} ${markdown.code('/info')} - Información del sistema\n` +
           `${constants.EMOJI.SMALL_BLUE_DIAMOND} ${markdown.code('/user')} - Tu perfil y VPNs\n` +
           `${constants.EMOJI.SMALL_BLUE_DIAMOND} ${markdown.code('/vpn')} - Gestión de VPN\n\n` +
           `${isAdmin ? `${constants.EMOJI.SMALL_BLUE_DIAMOND} ${markdown.code('/admin')} - Panel de administración\n\n` : ''}` +
           `💡 Usa ${markdown.code('/help')} para ver todos los comandos.`;
  },

  /**
   * Mensaje de bienvenida para administradores
   */
  WELCOME_ADMIN: ({ userName = 'Administrador', userId }) => {
    return `${constants.EMOJI.CROWN} *¡Bienvenido ${userName}!*\n\n` +
           `*Panel de Administración - uSipipo VPN Manager*\n\n` +
           `${markdown.bold('ID:')} ${markdown.code(userId)}\n` +
           `${markdown.bold('Rol:')} 👑 Administrador\n` +
           `${markdown.bold('Estado:')} ${constants.EMOJI.CHECK} Activo\n\n` +
           `⚡ *Comandos administrativos:*\n` +
           `${constants.EMOJI.SMALL_ORANGE_DIAMOND} ${markdown.code('/admin')} - Panel principal\n` +
           `${constants.EMOJI.SMALL_ORANGE_DIAMOND} ${markdown.code('/admin users')} - Gestión de usuarios\n` +
           `${constants.EMOJI.SMALL_ORANGE_DIAMOND} ${markdown.code('/admin stats')} - Estadísticas\n` +
           `${constants.EMOJI.SMALL_ORANGE_DIAMOND} ${markdown.code('/admin broadcast')} - Envío masivo\n\n` +
           `📋 *Comandos generales:*\n` +
           `${constants.EMOJI.SMALL_BLUE_DIAMOND} ${markdown.code('/vpn')} - Gestión VPN\n` +
           `${constants.EMOJI.SMALL_BLUE_DIAMOND} ${markdown.code('/info')} - Info del sistema\n` +
           `${constants.EMOJI.SMALL_BLUE_DIAMOND} ${markdown.code('/help')} - Ayuda completa\n\n` +
           `🔧 *Recursos del sistema:*\n` +
           `• Server IP: ${markdown.code(process.env.SERVER_IPV4 || 'N/A')}\n` +
           `• WG Port: ${markdown.code(process.env.WG_SERVER_PORT || 'N/A')}\n` +
           `• Outline Port: ${markdown.code(process.env.OUTLINE_API_PORT || 'N/A')}\n\n` +
           `${constants.EMOJI.INFO} Sistema iniciado correctamente.`;
  },

  /**
   * Mensaje cuando el usuario ya está registrado
   */
  ALREADY_REGISTERED: ({ userName = 'Usuario' }) => {
    return `${constants.EMOJI.INFO} *Ya estás registrado, ${userName}!*\n\n` +
           `Parece que ya tienes acceso al sistema.\n\n` +
           `Usa ${markdown.code('/help')} para ver los comandos disponibles o ` +
           `${markdown.code('/user')} para ver tu perfil.`;
  },

  /**
   * Solicitud enviada al administrador
   */
  REQUEST_SENT_TO_ADMIN: () => {
    return `${constants.EMOJI.ENVELOPE} *Solicitud enviada*\n\n` +
           `Tu solicitud de acceso ha sido enviada al administrador.\n\n` +
           `${constants.EMOJI.CLOCK} *Tiempo estimado:* 1-24 horas\n` +
           `${constants.EMOJI.BELL} *Notificación:* Recibirás un mensaje cuando seas aprobado.\n\n` +
           `${markdown.italic('Gracias por tu paciencia.')}`;
  },

  /**
   * Error en el registro
   */
  REGISTRATION_ERROR: ({ error = 'Error desconocido' }) => {
    return `${constants.EMOJI.ERROR} *Error en el registro*\n\n` +
           `No se pudo procesar tu solicitud:\n` +
           `${markdown.code(error)}\n\n` +
           `${constants.EMOJI.PHONE} Contacta con el administrador si el problema persiste.`;
  },

  /**
   * Botón de inicio (para teclados)
   */
  START_BUTTON: `${constants.EMOJI.HOUSE} Inicio`,

  /**
   * Mensaje de reintento
   */
  RETRY_MESSAGE: () => {
    return `${constants.EMOJI.REFRESH} *¿Problemas con el inicio?*\n\n` +
           `Intenta lo siguiente:\n\n` +
           `1. ${markdown.bold('Cierra y reabre Telegram')}\n` +
           `2. ${markdown.bold('Elimina el chat con el bot y empieza de nuevo')}\n` +
           `3. ${markdown.bold('Contacta al administrador si el problema persiste')}\n\n` +
           `También puedes usar ${markdown.code('/help')} para más información.`;
  },

  /**
   * Footer común para mensajes de inicio
   */
  START_FOOTER: () => {
    return `\n\n${constants.EMOJI.DIVIDER}\n` +
           `${markdown.italic('uSipipo VPN Manager v2.0 • Sistema profesional de VPN')}`;
  }
};